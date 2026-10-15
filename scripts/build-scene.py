#!/usr/bin/env python3
"""Inject a scene JSON into templates/canvas.html.

Usage: build-scene.py scene.json out.html [title] [--cdn] [--fragment] [--validate-only] [--no-text-lint]

The page works offline by default: the libraries it uses are inlined (fetched once
into .vt-libs/). --cdn keeps <script src> tags instead, for a lighter file that needs
the network. Layout libraries a scene does not use (ELK, d3-sankey) are left out.

The scene is validated first; an invalid scene is not built. Exit 0 prints the
output path; exit 1 prints the problems, one per line, prefixed by the scene file.
"""

import difflib, json, pathlib, re, sys

ID_RE = re.compile(r"^[A-Za-z0-9_]+$")
KINDS = {
    "line",
    "area",
    "bar",
    "stackedBar",
    "scatter",
    "dot",
    "histogram",
    "donut",
    "tornado",
}
TYPES = {
    "chart",
    "kpi",
    "matrix",
    "cards",
    "timeline",
    "steps",
    "tree",
    "mindmap",
    "quadrant",
    "spectrum",
    "cycle",
    "funnel",
    "venn",
    "callout",
    "text",
    "free",
    "graph",
    "decision",
    "entity",
    "heatmap",
    "gantt",
    "sankey",
    "treemap",
    "code",
    "math",
    "map",
    "custom",
}
LIB_HOSTS = ("https://cdn.jsdelivr.net/npm/", "https://cdn.jsdelivr.net/gh/", "https://cdnjs.cloudflare.com/ajax/libs/", "https://unpkg.com/")
COLOR_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b|\brgba?\(")
DIFFS = {"added", "removed", "changed"}
GRAPH_KINDS = {
    "entry",
    "component",
    "external",
    "store",
    "queue",
    "decision",
    "error",
    "critical",
}
EDGE_KINDS = {"data", "control", "event", "error"}


def check_tornado(b, p, c):
    base = b.get("baseline")
    if base is not None:
        if isinstance(base, dict):
            if "value" in base and not isinstance(base["value"], (int, float)):
                p(c + f"tornado baseline value inválido: {base['value']!r}")
        elif not isinstance(base, (int, float)):
            p(c + f"tornado baseline inválido: {base!r}")
    series = b.get("series")
    if not series or not isinstance(series, list):
        p(c + "tornado sem series")
        return
    for se in series:
        if not isinstance(se, dict):
            p(c + "série tornado deve ser objeto")
            continue
        if not se.get("name"):
            p(c + f"série tornado sem name: {json.dumps(se, ensure_ascii=False)[:80]}")
        if "low" not in se or not isinstance(se["low"], (int, float)):
            p(c + f"série '{se.get('name', '?')}' sem valor numérico 'low'")
        if "high" not in se or not isinstance(se["high"], (int, float)):
            p(c + f"série '{se.get('name', '?')}' sem valor numérico 'high'")


def check_chart(b, p, c):
    if b.get("kind") and b["kind"] not in KINDS:
        p(c + f"kind desconhecido: {b['kind']!r}")
    if b.get("kind") == "tornado":
        check_tornado(b, p, c)
        return
    s = b.get("series") or []
    if b.get("kind") == "donut":
        if s and len(s) > 5:
            p(c + f"donut com {len(s)} partes; máximo 5")
        return
    if len(s) > 6:
        p(c + f"{len(s)} séries; máximo 6")
    for se in s:
        if not se.get("name"):
            p(c + f"série sem name: {json.dumps(se, ensure_ascii=False)[:80]}")
        if not (se.get("data") or se.get("values")):
            p(c + f"série '{se.get('name')}' sem data")


def check_graph(b, p, w, c):
    nodes, groups = b.get("nodes") or [], b.get("groups") or []
    ids = [n.get("id", "") for n in nodes]
    for n in nodes:
        nid = n.get("id")
        if not nid:
            p(c + "nó sem id")
            continue
        if not ID_RE.match(str(nid)):
            p(c + f"id inválido {nid!r}: use letras, dígitos e _")
        if not n.get("sub"):
            p(c + f"nó '{nid}' sem sub (responsabilidade)")
        if n.get("kind") and n["kind"] not in GRAPH_KINDS:
            p(c + f"nó '{nid}' kind desconhecido: {n['kind']!r}")
        if n.get("status") and n["status"] not in ("verified", "inferred", "unknown"):
            p(c + f"nó '{nid}' status desconhecido: {n['status']!r}")
        if n.get("reversibility") and n["reversibility"] not in ("one-way", "two-way"):
            p(c + f"nó '{nid}' reversibility desconhecido: {n['reversibility']!r}")
        if n.get("consequence") is not None:
            cons = n["consequence"]
            if not isinstance(cons, dict):
                p(c + f"nó '{nid}' consequence deve ser objeto")
            else:
                if "order" in cons and not isinstance(cons["order"], int):
                    p(c + f"nó '{nid}' consequence.order deve ser inteiro")
                if cons.get("polarity") and cons["polarity"] not in (
                    "ok",
                    "danger",
                    "neutral",
                    "warn",
                ):
                    p(
                        c
                        + f"nó '{nid}' consequence.polarity desconhecido: {cons['polarity']!r}"
                    )
        if "prob" in n and (
            not isinstance(n["prob"], (int, float)) or not (0 <= n["prob"] <= 1)
        ):
            p(c + f"nó '{nid}' prob deve ser número entre 0 e 1: {n['prob']!r}")
        check_diff(n, p, c, f"nó '{nid}'")
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        p(c + f"ids de nó duplicados: {sorted(dup)}")
    gids = {g.get("id") for g in groups}
    for g in groups:
        if not g.get("id"):
            p(c + "grupo sem id")
        used = any(n.get("group") == g.get("id") for n in nodes)
        if not used:
            p(c + f"grupo '{g.get('id')}' sem nenhum nó (runtime apaga em silêncio)")
        if g.get("view") and g["view"] not in (b.get("_view_ids") or ()):
            p(c + f"grupo '{g['id']}' aponta para vista inexistente: {g['view']!r}")
    for n in nodes:
        if n.get("group") and n["group"] not in gids:
            p(c + f"nó '{n['id']}' em grupo inexistente: {n['group']!r}")
        if n.get("view") and n["view"] not in (b.get("_view_ids") or ()):
            p(c + f"nó '{n['id']}' aponta para vista inexistente: {n['view']!r}")
    for e in b.get("edges") or []:
        for end in ("from", "to"):
            if e.get(end) not in ids:
                p(
                    c
                    + f"edge sem '{end}' válido: {json.dumps(e, ensure_ascii=False)[:80]}"
                )
        lbl = e.get("label")
        if not lbl:
            p(c + f"edge {e.get('from')}→{e.get('to')} sem label")
        elif len(lbl) > 28:
            p(
                c
                + f"edge '{lbl}' com {len(lbl)} caracteres; máximo 28, o resto vai em detail"
            )
        if e.get("kind") and e["kind"] not in EDGE_KINDS:
            p(c + f"edge kind desconhecido: {e['kind']!r}")
        if e.get("reversibility") and e["reversibility"] not in ("one-way", "two-way"):
            p(c + f"edge reversibility desconhecido: {e['reversibility']!r}")
        if e.get("consequence") is not None:
            cons = e["consequence"]
            if not isinstance(cons, dict):
                p(c + f"edge {e.get('from')}→{e.get('to')} consequence deve ser objeto")
            else:
                if "order" in cons and not isinstance(cons["order"], int):
                    p(
                        c
                        + f"edge {e.get('from')}→{e.get('to')} consequence.order deve ser inteiro"
                    )
                if cons.get("polarity") and cons["polarity"] not in (
                    "ok",
                    "danger",
                    "neutral",
                    "warn",
                ):
                    p(
                        c
                        + f"edge {e.get('from')}→{e.get('to')} consequence.polarity desconhecido: {cons['polarity']!r}"
                    )
        if "prob" in e and (
            not isinstance(e["prob"], (int, float)) or not (0 <= e["prob"] <= 1)
        ):
            p(
                c
                + f"edge {e.get('from')}→{e.get('to')} prob deve ser número entre 0 e 1: {e['prob']!r}"
            )
    if b.get("engine") and b["engine"] not in ("elk", "dagre"):
        p(c + f"engine desconhecido: {b['engine']!r} (elk ou dagre)")
    if len(nodes) + len(groups) > 12:
        w(
            c
            + f"{len(nodes)} nós + {len(groups)} grupos numa vista; máximo 12, divida em vistas"
        )


def check_free(b, p, w, c):
    by_id = {e.get("id") for e in (b.get("elements") or []) if e.get("id")}
    for e in b.get("elements") or []:
        t = e.get("type")
        if t == "text":
            continue
        if t in ("rect", "ellipse"):
            for f in ("x", "y", "w", "h"):
                if e.get(f) is None:
                    p(c + f"{t} '{e.get('id', e.get('text', '?'))}' sem {f}")
            continue
        if t in ("image", "video"):
            for f in ("x", "y", "w", "h", "src"):
                if e.get(f) is None:
                    p(c + f"{t} '{e.get('id', '?')}' sem {f}")
            src = e.get("src") or ""
            if src.startswith("/") and "://" not in src:
                w(
                    c
                    + f"{t} '{e.get('id', '?')}' com src absoluto local; quebra ao enviar, use relativo ou http(s)"
                )
            continue
        if t in ("line", "arrow"):
            if not (e.get("from") or "x1" in e):
                p(c + f"{t} sem from nem x1/y1")
            if not (e.get("to") or "x2" in e):
                p(c + f"{t} sem to nem x2/y2")
            if e.get("from") and e["from"] not in by_id:
                p(c + f"{t} aponta para elemento inexistente: {e['from']!r}")
            if e.get("to") and e["to"] not in by_id:
                p(c + f"{t} aponta para elemento inexistente: {e['to']!r}")
    pairs = [
        (e.get("from"), e.get("to"))
        for e in (b.get("elements") or [])
        if e.get("type") in ("line", "arrow") and e.get("from") and e.get("to")
    ]
    if len(set(pairs)) != len(pairs):
        p(c + "duas setas com as mesmas pontas; rótulos colidem, some ou inverta uma")


def check_decision(b, p, w, c):
    opts = b.get("options")
    if not opts or not isinstance(opts, list):
        p(c + "decision sem options")
    else:
        for opt in opts:
            if not isinstance(opt, dict):
                p(c + "opção deve ser objeto")
                continue
            oid = opt.get("id")
            if not oid:
                p(c + "opção sem id")
            if not opt.get("label"):
                p(c + f"opção '{oid or '?'}' sem label")
            if "reversibility" in opt and opt["reversibility"] not in (
                "one-way",
                "two-way",
            ):
                p(
                    c
                    + f"opção '{oid or '?'}' reversibility desconhecido: {opt['reversibility']!r}"
                )
            if (
                "vetoBelow" in opt
                and opt["vetoBelow"] is not None
                and not isinstance(opt["vetoBelow"], (int, float))
            ):
                p(c + f"opção '{oid or '?'}' vetoBelow inválido: {opt['vetoBelow']!r}")

    crits = b.get("criteria")
    if not crits or not isinstance(crits, list):
        p(c + "decision sem criteria")
    else:
        for cr in crits:
            if not isinstance(cr, dict):
                p(c + "critério deve ser objeto")
                continue
            cid = cr.get("id")
            if not cid:
                p(c + "critério sem id")
            if not cr.get("label"):
                p(c + f"critério '{cid or '?'}' sem label")
            w_val = cr.get("weight")
            if w_val is None or not isinstance(w_val, (int, float)) or w_val < 0:
                p(
                    c
                    + f"critério '{cid or '?'}' weight inválido (esperado número >= 0): {w_val!r}"
                )
            if (
                "vetoBelow" in cr
                and cr["vetoBelow"] is not None
                and not isinstance(cr["vetoBelow"], (int, float))
            ):
                p(
                    c
                    + f"critério '{cid or '?'}' vetoBelow inválido (esperado número): {cr['vetoBelow']!r}"
                )
            if "reversibility" in cr and cr["reversibility"] not in (
                "one-way",
                "two-way",
            ):
                p(
                    c
                    + f"critério '{cid or '?'}' reversibility desconhecido: {cr['reversibility']!r}"
                )
            scores = cr.get("scores")
            if scores is None or not isinstance(scores, dict):
                p(c + f"critério '{cid or '?'}' sem scores")
            else:
                for opt_id, sc in scores.items():
                    if not isinstance(sc, dict):
                        p(
                            c
                            + f"critério '{cid or '?'}' score para '{opt_id}' deve ser objeto"
                        )

    if "reversibility" in b and b["reversibility"] not in ("one-way", "two-way"):
        p(c + f"decision reversibility desconhecido: {b['reversibility']!r}")
    if (
        "vetoBelow" in b
        and b["vetoBelow"] is not None
        and not isinstance(b["vetoBelow"], (int, float))
    ):
        p(c + f"decision vetoBelow inválido: {b['vetoBelow']!r}")
    if not b.get("weightBasis"):
        w(c + "decision sem weightBasis (declare de onde vêm os pesos)")


def check_diff(o, p, c, what):
    if o.get("diff") and o["diff"] not in DIFFS:
        p(c + f"{what} diff desconhecido: {o['diff']!r} (use added, removed, changed)")


def check_entity(b, p, w, c):
    ents = b.get("entities") or []
    if not ents:
        p(c + "entity sem entities")
    ids = [e.get("id") for e in ents]
    for e in ents:
        eid = e.get("id")
        if not eid:
            p(c + "entidade sem id")
            continue
        if not ID_RE.match(str(eid)):
            p(c + f"id inválido {eid!r}: use letras, dígitos e _")
        if not e.get("fields"):
            w(c + f"entidade '{eid}' sem fields")
        names = [f if isinstance(f, str) else f.get("name") for f in e.get("fields") or []]
        if any(not n for n in names):
            p(c + f"entidade '{eid}' tem campo sem name")
        dup = {n for n in names if n and names.count(n) > 1}
        if dup:
            p(c + f"entidade '{eid}' com campos duplicados: {sorted(dup)}")
        check_diff(e, p, c, f"entidade '{eid}'")
    dup = {i for i in ids if i and ids.count(i) > 1}
    if dup:
        p(c + f"ids de entidade duplicados: {sorted(dup)}")
    for r in b.get("relations") or []:
        for end in ("from", "to"):
            if r.get(end) not in ids:
                p(c + f"relação sem '{end}' válido: {json.dumps(r, ensure_ascii=False)[:80]}")
        check_diff(r, p, c, "relação")
    if len(ents) > 12:
        w(c + f"{len(ents)} entidades numa vista; máximo 12, divida por domínio")


def check_heatmap(b, p, c):
    if b.get("calendar"):
        for d in b.get("data") or []:
            if not (isinstance(d, list) and len(d) == 2 and isinstance(d[1], (int, float))):
                p(c + f"heatmap calendar: cada item é [data, número]: {d!r}")
                break
        if not b.get("data"):
            p(c + "heatmap calendar sem data")
        return
    xs, ys, vals = b.get("x") or [], b.get("y") or [], b.get("values") or []
    if not xs or not ys:
        p(c + "heatmap sem x/y (rótulos das colunas e linhas)")
    if len(vals) != len(ys):
        p(c + f"heatmap com {len(vals)} linhas em values para {len(ys)} rótulos em y")
    for i, row in enumerate(vals):
        if len(row) != len(xs):
            p(c + f"heatmap linha {i} com {len(row)} valores para {len(xs)} colunas")
            break
        if any(v is not None and not isinstance(v, (int, float)) for v in row):
            p(c + f"heatmap linha {i} com valor não numérico (use null para vazio)")
            break


def check_gantt(b, p, c):
    tasks = b.get("tasks") or []
    if not tasks:
        p(c + "gantt sem tasks")
    ids = {t.get("id") for t in tasks if t.get("id")}
    date = re.compile(r"^\d{4}-\d{2}-\d{2}")
    for t in tasks:
        lbl = t.get("label") or t.get("id") or "?"
        if not t.get("label"):
            p(c + f"tarefa '{lbl}' sem label")
        if not (t.get("start") and date.match(str(t["start"]))):
            p(c + f"tarefa '{lbl}' sem start AAAA-MM-DD")
        if t.get("end") and not date.match(str(t["end"])):
            p(c + f"tarefa '{lbl}' com end inválido: {t['end']!r}")
        if t.get("end") and t.get("start") and str(t["end"]) < str(t["start"]):
            p(c + f"tarefa '{lbl}' termina antes de começar")
        for d in t.get("deps") or []:
            if d not in ids:
                p(c + f"tarefa '{lbl}' depende de id inexistente: {d!r}")
        if t.get("progress") is not None and not (0 <= t["progress"] <= 1):
            p(c + f"tarefa '{lbl}' progress fora de 0..1")


def check_sankey(b, p, c):
    ids = [n.get("id") for n in b.get("nodes") or []]
    if not ids:
        p(c + "sankey sem nodes")
    for n in b.get("nodes") or []:
        if not n.get("label"):
            p(c + f"nó '{n.get('id')}' sem label")
    links = b.get("links") or []
    if not links:
        p(c + "sankey sem links")
    for l in links:
        for end in ("from", "to"):
            if l.get(end) not in ids:
                p(c + f"link sem '{end}' válido: {json.dumps(l, ensure_ascii=False)[:80]}")
        if not isinstance(l.get("value"), (int, float)) or l["value"] <= 0:
            p(c + f"link {l.get('from')}→{l.get('to')} sem value positivo")
    # cycles break the layout
    adj = {}
    for l in links:
        adj.setdefault(l.get("from"), []).append(l.get("to"))
    seen, stack = set(), set()

    def cyc(n):
        if n in stack:
            return True
        if n in seen:
            return False
        seen.add(n)
        stack.add(n)
        r = any(cyc(m) for m in adj.get(n, []))
        stack.discard(n)
        return r

    if any(cyc(n) for n in list(adj)):
        p(c + "sankey com ciclo; fluxo deve seguir em uma direção (use graph para ciclos)")


def check_treemap(b, p, c):
    root = b.get("root")
    if not isinstance(root, dict) or not root.get("children"):
        p(c + "treemap sem root.children")
        return

    def walk(n, path):
        kids = n.get("children") or []
        if not n.get("label"):
            p(c + f"treemap: nó sem label em {' › '.join(path) or 'raiz'}")
        if not kids:
            v = n.get("value")
            if not isinstance(v, (int, float)) or v < 0:
                p(c + f"treemap: folha '{n.get('label', '?')}' sem value numérico >= 0")
        for k in kids:
            walk(k, path + [str(n.get("label", ""))])

    walk(root, [])


def check_code(b, p, w, c):
    code = b.get("code")
    if not isinstance(code, str) or not code.strip():
        p(c + "code sem code")
        return
    n = code.count("\n") + 1
    if n > 60:
        w(c + f"code com {n} linhas; mostre só o trecho que importa (até 60)")
    start = b.get("start", 1)
    for h in b.get("highlight") or []:
        ln = h if isinstance(h, int) else h.get("line") if isinstance(h, dict) else None
        if not isinstance(ln, int) or not (start <= ln < start + n):
            p(c + f"highlight fora do trecho: {h!r} (linhas {start} a {start + n - 1})")


def check_map(b, p, w, c):
    geo = b.get("geo", "world")
    if geo not in ("world", "br") and not str(geo).startswith(("http://", "https://")):
        p(c + f"map geo desconhecido: {geo!r} (world, br ou URL de GeoJSON/TopoJSON)")
    vals = b.get("values") or {}
    items = vals.items() if isinstance(vals, dict) else [((v or {}).get("key") or (v or {}).get("id") or (v or {}).get("name"), (v or {}).get("value")) for v in vals]
    for k, v in items:
        if not k:
            p(c + "map: valor sem key")
        if not isinstance(v, (int, float)):
            p(c + f"map: valor de {k!r} não numérico: {v!r}")
    for pt in b.get("points") or []:
        lat, lon = pt.get("lat"), pt.get("lon")
        if not (isinstance(lat, (int, float)) and -90 <= lat <= 90 and isinstance(lon, (int, float)) and -180 <= lon <= 180):
            p(c + f"map: ponto '{pt.get('label', '?')}' sem lat/lon válidos")
    if not vals and not b.get("points"):
        p(c + "map sem values nem points")


def check_custom(b, p, w, c, lib_names):
    kinds = [k for k in ("svg", "html", "draw") if b.get(k)]
    if len(kinds) != 1:
        p(c + "custom precisa de exatamente um entre svg, html e draw")
        return
    if not (b.get("alt") or "").strip():
        w(c + "custom sem alt: uma frase com o que o desenho mostra (modo leitura e leitor de tela)")
    if kinds[0] in ("svg", "html") and not (isinstance(b.get("width"), (int, float)) and isinstance(b.get("height"), (int, float))):
        p(c + f"custom {kinds[0]} precisa de width e height")
    if COLOR_RE.search(b[kinds[0]]):
        w(c + "custom com cor literal; use var(--s1)... para dados, var(--fg) e var(--fg-muted) para texto, para valer nos dois temas")
    used = set(re.findall(r"var\(--([a-z0-9-]+)", b[kinds[0]]))
    for name in sorted(used - TOKENS):
        near = difflib.get_close_matches(name, sorted(TOKENS), n=2)
        w(c + f"custom usa var(--{name}), que não existe" + (f"; quis dizer {' ou '.join('--' + x for x in near)}?" if near else "; veja os tokens em formats.md"))
    if "accent" in used:
        w(c + "custom usa var(--accent) num desenho; --accent é seleção e foco, dado usa var(--s1) a var(--s6)")
    for n in b.get("libs") or []:
        if n not in lib_names:
            p(c + f"custom usa lib desconhecida {n!r}; declare em scene.libs ou use uma das embutidas")


def check_block(b, p, w, c):
    t = b.get("type")
    if t not in TYPES:
        p(c + f"block type desconhecido: {t!r}")
        return
    if not b.get("id"):
        p(c + f"block '{t}' sem id")
    if not b.get("title"):
        w(c + f"block '{b.get('id')}' sem title (o título deve dizer o que se aprende)")
    if t == "chart":
        check_chart(b, p, c)
    elif t == "graph":
        check_graph(b, p, w, c)
    elif t == "free":
        check_free(b, p, w, c)
    elif t == "decision":
        check_decision(b, p, w, c)
    elif t == "entity":
        check_entity(b, p, w, c)
    elif t == "heatmap":
        check_heatmap(b, p, c)
    elif t == "gantt":
        check_gantt(b, p, c)
    elif t == "sankey":
        check_sankey(b, p, c)
    elif t == "treemap":
        check_treemap(b, p, c)
    elif t == "code":
        check_code(b, p, w, c)
    elif t == "math":
        if not (b.get("tex") or "").strip():
            p(c + "math sem tex")
    elif t == "map":
        check_map(b, p, w, c)
    elif t == "custom":
        check_custom(b, p, w, c, b.get("_lib_names") or ())
    elif t in ("matrix",):
        if not (b.get("columns") or b.get("rows")):
            p(c + "matrix sem columns/rows")
    elif t in ("cards", "steps", "cycle", "funnel"):
        if not b.get("items"):
            p(c + f"{t} sem items")
    elif t == "timeline":
        for ev in b.get("events") or []:
            if not ev.get("date"):
                p(c + f"evento '{ev.get('title', '?')}' sem date")
    elif t in ("quadrant", "spectrum"):
        for it in b.get("items") or []:
            for f in ("x", "y") if t == "quadrant" else ("value",):
                v = it.get(f)
                if v is None or not (0 <= v <= 1):
                    p(c + f"{t} '{it.get('label', '?')}': {f}={v} fora de 0..1")
    elif t == "venn":
        n = len(b.get("sets") or [])
        if n not in (2, 3):
            p(c + f"venn com {n} conjuntos; use 2 ou 3")
        seen = set()
        for o in b.get("overlaps") or []:
            key = tuple(sorted((o.get("sets") or [])))
            if key in seen:
                w(
                    c
                    + f"venn com interseção duplicada {list(key)}; rótulos colidem, una as duas"
                )
            seen.add(key)
    elif t == "kpi":
        if not b.get("items"):
            p(c + "kpi sem items")


def check_scenarios(sc, p, c):
    if not isinstance(sc, dict):
        p(c + "scenarios deve ser objeto")
        return
    ctrls = sc.get("controls")
    if ctrls is not None:
        if not isinstance(ctrls, list):
            p(c + "scenarios controls deve ser lista")
        else:
            for ctrl in ctrls:
                if not isinstance(ctrl, dict):
                    p(c + "controle de cenário deve ser objeto")
                    continue
                if not ctrl.get("id"):
                    p(c + "controle de cenário sem id")
                if not ctrl.get("label"):
                    p(c + f"controle de cenário '{ctrl.get('id', '?')}' sem label")
                if "options" in ctrl and not isinstance(ctrl["options"], list):
                    p(
                        c
                        + f"controle de cenário '{ctrl.get('id', '?')}' options deve ser lista"
                    )
    if "overrides" in sc and not isinstance(sc["overrides"], dict):
        p(c + "scenarios overrides deve ser objeto")


# ---------- text budget: the drawing carries the meaning; text only labels it.
# Warnings, never errors: a long string still builds, the author sees where it bloats.
CAP_SCENE = {"title": 12, "subtitle": 12, "summary": 25}
CAP_FIELD = {"sub": 6, "meta": 6, "text": 15, "detail": 25, "note": 25, "summary": 25}
CAP_BLOCK_TITLE = 8
CAP_VIEW_WORDS = 250
PARAGRAPH_TYPES = {"text", "callout"}  # their own `text` is prose by design
SKIP_TEXT_TYPES = {"free"}  # labels on a hand-placed canvas
# page level (title, subtitle, summaries): any talk about the page, its tabs or its audience
META_RE = re.compile(
    r"\b(clique|clicar|aba|abas|comece (?:pela|por|pelo)|esta página|essa página|nesta página|"
    r"painel da direita|painel lateral|para quem|click|this page|this tab)\b",
    re.I,
)
# item level: only instructions to the viewer; "o usuário clica" is subject matter
META_ITEM_RE = re.compile(
    r"\b(clique|ver aba|na aba|veja a aba|esta página|nesta página|painel da direita|painel lateral|click here|this page)\b",
    re.I,
)
# token names the page defines; a var(--x) outside this set renders as nothing
TOKENS = set(re.findall(r"--([a-z0-9-]+)\s*:", (pathlib.Path(__file__).resolve().parent.parent / "templates" / "_tokens.css").read_text()))
URL_RE = re.compile(r"https?://")
STOP = set(
    "a o os as de da do das dos e é em no na nos nas um uma uns umas que se por para com sem ao à "
    "the of and to in is it for on with".split()
)


def words(s):
    return len(str(s).split())


def toks(s):
    return {t for t in re.findall(r"\w+", str(s).lower()) if len(t) > 2 and t not in STOP}


def overlap(a, b):
    ta, tb = toks(a), toks(b)
    return len(ta & tb) / len(ta) if ta else 0.0


def check_text(scene, w):
    for k, cap in CAP_SCENE.items():
        if words(scene.get(k) or "") > cap:
            w(f"texto: scene {k} com {words(scene[k])} palavras; máximo {cap}")
    for k in ("summary", "subtitle", "title"):
        if META_RE.search(scene.get(k) or ""):
            w(f"texto: scene {k} descreve a página ou a navegação; diga o achado")
    for v in scene.get("views") or []:
        vid = v.get("id")
        total = words(v.get("summary") or "")
        if words(v.get("summary") or "") > CAP_FIELD["summary"]:
            w(f"texto: vista '{vid}' summary com {words(v['summary'])} palavras; máximo 25")
        if META_RE.search(v.get("summary") or ""):
            w(f"texto: vista '{vid}' summary descreve a navegação; diga o achado da vista")
        for a in v.get("annotations") or []:
            total += words(a)
            if words(a) > 25:
                w(f"texto: vista '{vid}' anotação com {words(a)} palavras; máximo 25")
        labels = []
        for b in v.get("blocks") or []:
            c = f"texto: vista '{vid}' · block '{b.get('id')}': "
            t = b.get("type")
            if words(b.get("title") or "") > CAP_BLOCK_TITLE:
                w(c + f"title com {words(b['title'])} palavras; máximo {CAP_BLOCK_TITLE}")
            if t in SKIP_TEXT_TYPES:
                continue
            if t == "callout" and b.get("label") and b.get("label") == b.get("title"):
                w(c + "callout label repete o title; tire o label")
            if t in PARAGRAPH_TYPES and URL_RE.search(b.get("text") or ""):
                w(c + "URL no texto; links vão em source, que o painel já lista")
            if t in PARAGRAPH_TYPES:
                total += words(b.get("text") or "")
                if words(b.get("text") or "") > 40:
                    w(c + f"{t} com {words(b['text'])} palavras; máximo 40")
                continue
            total += _walk_text(b, c, w, labels, top=True)
        s = v.get("summary") or ""
        hits = sorted({l for l in labels if len(l) > 2 and l.lower() in s.lower()})
        if len(hits) >= 3:
            w(f"texto: vista '{vid}' summary repete {len(hits)} rótulos do desenho ({', '.join(hits[:4])}); diga o que eles significam juntos")
        if total > CAP_VIEW_WORDS:
            w(f"texto: vista '{vid}' com {total} palavras; acima de {CAP_VIEW_WORDS} a página virou texto, corte detail/text sem fato novo")


def _walk_text(o, c, w, labels, top=False):
    """Count words, cap per field, flag detail that only rephrases the label or sub."""
    n = 0
    if isinstance(o, list):
        return sum(_walk_text(x, c, w, labels) for x in o)
    if not isinstance(o, dict):
        return 0
    name = o.get("label") or o.get("title") or o.get("name") or o.get("id") or "?"
    if not top and (o.get("label") or o.get("title")):
        labels.append(str(o.get("label") or o.get("title")))
    for k, v in o.items():
        if k.startswith("_"):
            continue
        if isinstance(v, str):
            if k in ("id", "from", "to", "kind", "type", "group", "status", "view", "file", "src", "date", "unit"):
                continue
            n += words(v)
            if k in CAP_FIELD and not (top and k == "text") and words(v) > CAP_FIELD[k]:
                w(c + f"'{name}' {k} com {words(v)} palavras; máximo {CAP_FIELD[k]}")
            if META_ITEM_RE.search(v):
                w(c + f"'{name}' {k} fala da navegação ou da página: {v[:50]!r}")
        elif isinstance(v, (list, dict)) and k not in ("data", "values", "spark", "cells", "scores"):
            n += _walk_text(v, c, w, labels)
    for k in ("detail", "note"):
        d = o.get(k)
        if isinstance(d, str):
            ref = " ".join(str(o.get(x) or "") for x in ("label", "title", "sub", "text", "meta"))
            if ref.strip() and overlap(d, ref) >= 0.6:
                w(c + f"'{name}' {k} repete o rótulo/sub sem fato novo; apague ou troque por evidência")
    return n


def check_scene(scene, p, w):
    if not scene.get("title"):
        p("scene sem title")
    if scene.get("style") not in (None, "clean", "sketch"):
        p(f"scene style desconhecido: {scene['style']!r} (clean ou sketch)")
    if scene.get("lang") not in (None, "pt", "en"):
        p(f"scene lang desconhecido: {scene['lang']!r} (pt ou en)")
    if not (scene.get("summary") or "").strip():
        w("scene sem summary")
    lib_names = {"rough", "hljs", "katex", "topojson", "dagre"}
    for l in scene.get("libs") or []:
        if not (isinstance(l, dict) and l.get("name") and l.get("url")):
            p(f"scene libs: cada item é {{name, url, global}}: {l!r}")
            continue
        if not str(l["url"]).startswith(LIB_HOSTS) or "@" not in str(l["url"]):
            p(f"scene lib '{l['name']}': URL precisa vir de jsDelivr, cdnjs ou unpkg com versão fixa (nome@1.2.3)")
        lib_names.add(l["name"])
    views = scene.get("views")
    if not views or not isinstance(views, list):
        p("scene sem views")
        return
    view_ids = {v.get("id") for v in views if v.get("id")}
    for v in views:
        vid = v.get("id")
        if not vid:
            p("vista sem id")
            continue
        if not v.get("title"):
            w(f"vista '{vid}' sem title")
        if len(views) > 1 and not (v.get("summary") or "").strip():
            w(f"vista '{vid}' sem summary (uma frase com o achado da vista)")
        if "scenarios" in v and v["scenarios"] is not None:
            check_scenarios(v["scenarios"], p, f"vista '{vid}': ")
        for b in v.get("blocks") or []:
            b["_view_ids"] = view_ids
            b["_lib_names"] = lib_names
            check_block(b, p, w, f"vista '{vid}' · block '{b.get('id')}': ")


def needs(scene):
    """Optional libraries and map geometry this scene uses."""
    blocks = [b for v in scene.get("views", []) for b in (v.get("blocks") or [])]
    libs, geos = [], []
    if scene.get("style") == "sketch":
        libs.append("rough")
    if any(b.get("type") == "code" for b in blocks):
        libs.append("hljs")
    if scene.get("math") or any(b.get("type") == "math" for b in blocks):
        libs.append("katex")
    if any(b.get("type") == "graph" and b.get("engine") == "dagre" for b in blocks):
        libs.append("dagre")
    for b in blocks:
        if b.get("type") == "custom":
            libs += list(b.get("libs") or [])
    for b in blocks:
        if b.get("type") == "map":
            g = b.get("geo", "world")
            if g in ("world", "br") and g not in geos:
                geos.append(g)
            if g == "world" or "topo" in str(g).lower():
                libs.append("topojson")
    return list(dict.fromkeys(libs)), geos


def simplify(coords, tol):
    """Douglas-Peucker on one ring, then 3-decimal rounding (about 100 m)."""
    pts = [c[:2] for c in coords]
    if len(pts) < 5:
        return [[round(x, 3), round(y, 3)] for x, y in pts]
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True

    def dist(i, a, z):
        (x1, y1), (x2, y2), (x, y) = pts[a], pts[z], pts[i]
        dx, dy = x2 - x1, y2 - y1
        n = (dx * dx + dy * dy) ** 0.5
        if n < 1e-12:  # closed ring: the chord is a point
            return ((x - x1) ** 2 + (y - y1) ** 2) ** 0.5
        return abs(dy * x - dx * y + x2 * y1 - y2 * x1) / n

    stack = [(0, len(pts) - 1)]
    while stack:
        a, z = stack.pop()
        best, bi = 0.0, -1
        for i in range(a + 1, z):
            d = dist(i, a, z)
            if d > best:
                best, bi = d, i
        if bi > 0 and (best > tol or (a == 0 and z == len(pts) - 1)):
            keep[bi] = True
            stack += [(a, bi), (bi, z)]
    out = [[round(x, 3), round(y, 3)] for (x, y), k in zip(pts, keep) if k]
    return out if len(out) >= 4 else [[round(x, 3), round(y, 3)] for x, y in pts]


def geo_data(key, w):
    """World TopoJSON as published; Brazilian states simplified once and cached."""
    import urllib.request

    root = pathlib.Path(__file__).resolve().parent.parent
    tpl = (root / "templates" / "canvas.html").read_text()
    libs = json.loads(re.search(r'<script id="vt-libs" type="application/json">(.*?)</script>', tpl, re.S).group(1))
    cache = root / ".vt-libs"
    f = cache / ("geo-" + key + ".json")
    if f.exists():
        return f.read_text()
    url = libs["worldAtlas" if key == "world" else "brStates"]["url"]
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            data = json.loads(r.read())
    except Exception as e:
        w(f"mapa '{key}' sem rede ({e}); a página baixa a geometria ao abrir")
        return None
    if key == "br":
        for ft in data["features"]:
            g = ft["geometry"]
            polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
            polys = [[simplify(ring, 0.01) for ring in poly] for poly in polys]
            g["coordinates"] = polys if g["type"] == "MultiPolygon" else polys[0]
            ft["properties"] = {k: ft["properties"][k] for k in ("name", "sigla", "codigo_ibg") if k in ft["properties"]}
    text = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
    cache.mkdir(exist_ok=True)
    f.write_text(text)
    return text


def inline_libs(page, w):
    """Replace CDN <script src> tags with the file contents, cached in .vt-libs/.

    Build needs network once; opening the page never does. A failed download
    keeps the CDN tags and warns instead of failing the build, so an offline
    author still gets a page.
    """
    import urllib.request

    root = pathlib.Path(__file__).resolve().parent.parent
    cache = root / ".vt-libs"
    for url in re.findall(r'<script src="(https://[^"]+)"></script>', page):
        name = url.rsplit("/", 1)[-1].split("?")[0]
        if name.startswith("index"):  # generic file names would collide in the cache
            name = re.sub(r"[^A-Za-z0-9.@-]+", "_", url.split("://", 1)[-1])
        lib = cache / name
        if not lib.exists():
            cache.mkdir(exist_ok=True)
            try:
                with urllib.request.urlopen(url, timeout=30) as r:
                    lib.write_bytes(r.read())
            except Exception as e:
                w(f"self-contained sem rede para {url}: mantendo a tag CDN ({e})")
                continue
        page = page.replace(
            f'<script src="{url}"></script>',
            "<script>\n" + lib.read_text().replace("</script", "<\\/script") + "\n</script>",
        )
    return page


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) < 2 and "--validate-only" not in sys.argv:
        sys.exit(__doc__.strip())
    src = pathlib.Path(args[0])
    try:
        scene = json.loads(src.read_text())
    except Exception as e:
        sys.exit(f"{src}: JSON inválido: {e}")
    problems = []
    warns = []
    p = problems.append
    w = warns.append
    try:
        check_scene(scene, p, w)
        if "--no-text-lint" not in sys.argv:
            check_text(scene, w)
    except Exception as e:
        problems.append(f"validação interrompida: {e}")
    for b in [b for v in scene.get("views", []) for b in (v.get("blocks") or [])]:
        b.pop("_view_ids", None)
        b.pop("_lib_names", None)
    for q in warns:
        print(f"{src}: nota: {q}")
    for q in problems:
        print(f"{src}: {q}")
    if "--validate-only" in sys.argv:
        sys.exit(1 if problems else 0)
    if problems:
        sys.exit(
            f"{src}: {len(problems)} problema(s); cena não construída. Corrija ou remova o que não faz sentido."
        )
    title = args[2] if len(args) > 2 else scene.get("title", "Canvas")
    tpl = (
        pathlib.Path(__file__).resolve().parent.parent / "templates" / "canvas.html"
    ).read_text()
    page = re.sub(
        r'<script id="scene" type="application/json">.*?</script>',
        lambda m: (
            '<script id="scene" type="application/json">\n'
            + json.dumps(scene, ensure_ascii=False, indent=2)
            + "\n</script>"
        ),
        tpl,
        flags=re.S,
    )
    page = re.sub(
        r"<title>.*?</title>",
        "<title>" + title.replace("<", "&lt;") + "</title>",
        page,
        count=1,
    )
    libs, geos = needs(scene)
    lib_urls = json.loads(re.search(r'<script id="vt-libs" type="application/json">(.*?)</script>', tpl, re.S).group(1))
    lib_urls.update({l["name"]: {"url": l["url"], "global": l.get("global", l["name"])} for l in scene.get("libs") or []})
    tags = "".join(f'<script src="{lib_urls[n]["url"]}"></script>\n' for n in libs)
    for g in geos:
        data = geo_data(g, lambda q: print(f"{src}: nota: {q}"))
        if data:
            tags += f'<script id="vt-geo-{g}" type="application/json">{data}</script>\n'
    page = page.replace("<!-- VT:LIBS -->", tags.rstrip("\n") or "<!-- VT:LIBS -->", 1)
    # drop the always-on layout libraries this scene never calls (ELK alone is 1.6 MB)
    blocks = [b for v in scene.get("views", []) for b in (v.get("blocks") or [])]
    if not any(b.get("type") in ("graph", "tree", "mindmap", "entity") for b in blocks):
        page = re.sub(r'<script src="https://[^"]*elkjs[^"]*"></script>\n?', "", page)
    if not any(b.get("type") == "sankey" for b in blocks):
        page = re.sub(r'<script src="https://[^"]*d3-sankey[^"]*"></script>\n?', "", page)
    if "--cdn" not in sys.argv:
        page = inline_libs(page, p)

    out = pathlib.Path(args[1]).resolve()
    if "--fragment" not in sys.argv:
        head, body = page.split("</style>", 1)
        page = (
            '<!doctype html>\n<html lang="pt-BR">\n<head>\n'
            + head
            + "</style>\n</head>\n<body>"
            + body
            + "\n</body>\n</html>\n"
        )
    out.write_text(page)
    print(out)
    print(
        "views:",
        [v["id"] for v in scene.get("views", [scene])],
        "(fragment)" if "--fragment" in sys.argv else "(standalone)",
    )


if __name__ == "__main__":
    main()
