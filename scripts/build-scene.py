#!/usr/bin/env python3
"""Inject a scene JSON into templates/canvas.html.

Usage: build-scene.py scene.json out.html [title] [--fragment] [--validate-only]

The scene is validated first; an invalid scene is not built. Exit 0 prints the
output path; exit 1 prints the problems, one per line, prefixed by the scene file.
"""

import json, pathlib, re, sys

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
}
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
    if len(nodes) + len(groups) > 12:
        w(
            c
            + f"{len(nodes)} nós + {len(groups)} grupos numa vista; máximo 12, divida em vistas"
        )


def check_free(b, p, c):
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
        check_free(b, p, c)
    elif t == "decision":
        check_decision(b, p, w, c)
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


def check_scene(scene, p, w):
    if not scene.get("title"):
        p("scene sem title")
    if not (scene.get("summary") or "").strip():
        w("scene sem summary")
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
        if not (v.get("summary") or "").strip():
            w(f"vista '{vid}' sem summary")
        if "scenarios" in v and v["scenarios"] is not None:
            check_scenarios(v["scenarios"], p, f"vista '{vid}': ")
        for b in v.get("blocks") or []:
            b["_view_ids"] = view_ids
            check_block(b, p, w, f"vista '{vid}' · block '{b.get('id')}': ")


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
    except Exception as e:
        problems.append(f"validação interrompida: {e}")
    for b in [b for v in scene.get("views", []) for b in (v.get("blocks") or [])]:
        b.pop("_view_ids", None)
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
