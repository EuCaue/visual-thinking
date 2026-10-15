#!/usr/bin/env python3
"""Draft a graph scene from the imports of a repository (Python, JS/TS, Go).

Usage: extract-deps.py <dir> [out.json] [--externals N] [--depth N]

Reads import statements only; nothing is executed. Files are grouped into
modules by directory: the overview uses the shallowest depth that yields at
most 12 modules, and every module with two or more submodules gets a detail
view one level down. Edges are "A imports B", counted per file.

The output is a draft: every node is `verified` (the import was read), the
title and summaries are placeholders the author must replace with the finding.
"""

import ast, collections, datetime, json, os, pathlib, re, sys

SKIP = {"node_modules", ".git", "dist", "build", "out", "coverage", "venv", ".venv", "__pycache__", ".next", ".nuxt", "target", "vendor", ".tox", ".mypy_cache", ".pytest_cache", ".vt-libs", "site-packages"}
JS_EXT = (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".mts", ".cts", ".vue", ".svelte")
ENTRY = re.compile(r"(^|/)(main|index|app|server|cli|__main__|manage|cmd)\.(py|ts|tsx|js|mjs|go)$|(^|/)cmd/")
JS_IMPORT = re.compile(r"""(?:import\s[^'"]*?from\s*|import\s*\(\s*|require\s*\(\s*|export\s[^'"]*?from\s*|import\s+)['"]([^'"]+)['"]""")
GO_IMPORT_BLOCK = re.compile(r"import\s*\((.*?)\)", re.S)
GO_IMPORT_ONE = re.compile(r'import\s+(?:\w+\s+)?"([^"]+)"')
MAX = 12


def files(root):
    for d, dirs, fs in os.walk(root):
        dirs[:] = [x for x in dirs if x not in SKIP and not x.startswith(".")]
        for f in fs:
            p = pathlib.Path(d) / f
            if p.suffix in (".py", ".go") or p.suffix in JS_EXT:
                if not re.search(r"(\.test|\.spec|_test)\.\w+$|(^|/)tests?/", str(p.relative_to(root))):
                    yield p


def py_imports(p, root, mods):
    try:
        tree = ast.parse(p.read_text(errors="ignore"))
    except SyntaxError:
        return [], []
    rel = p.relative_to(root)
    pkg = list(rel.parent.parts)
    inside, outside = [], []

    def resolve(nm):
        parts = [x for x in nm.split(".") if x]
        for k in range(len(parts), 0, -1):
            hit = mods.get("/".join(parts[:k]))
            if hit:
                return hit
        return None

    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            groups = [(a.name, [a.name]) for a in n.names]
            relative = False
        elif isinstance(n, ast.ImportFrom):
            base = pkg[: len(pkg) - n.level + 1] if n.level else []
            mod = ".".join(base + ([n.module] if n.module else []))
            groups = [(mod, [mod + "." + a.name for a in n.names] + [mod])]
            relative = bool(n.level)
        else:
            continue
        for top, cands in groups:
            hits = [h for h in (resolve(c) for c in cands) if h]
            if hits:
                inside.extend(h for h in hits[:1] if h != rel)
            elif not relative and top:
                outside.append(top.split(".")[0])
    return inside, outside


def js_resolve(p, spec, root, known):
    if not spec.startswith("."):
        return None
    base = (p.parent / spec).resolve()
    cands = [base] + [base.with_suffix(e) for e in JS_EXT] + [base / ("index" + e) for e in JS_EXT]
    if base.suffix == ".js":
        cands += [base.with_suffix(e) for e in (".ts", ".tsx")]
    for c in cands:
        try:
            r = c.relative_to(root)
        except ValueError:
            return None
        if r in known:
            return r
    return None


def js_imports(p, root, known):
    src = p.read_text(errors="ignore")
    inside, outside = [], []
    for spec in JS_IMPORT.findall(src):
        r = js_resolve(p, spec, root, known)
        if r and r != p.relative_to(root):
            inside.append(r)
        elif not spec.startswith(".") and not spec.startswith("/"):
            outside.append("/".join(spec.split("/")[:2]) if spec.startswith("@") else spec.split("/")[0])
    return inside, outside


def go_imports(p, root, gomod, dirs):
    src = p.read_text(errors="ignore")
    specs = []
    for blk in GO_IMPORT_BLOCK.findall(src):
        specs += re.findall(r'"([^"]+)"', blk)
    specs += GO_IMPORT_ONE.findall(src)
    inside, outside = [], []
    for s in specs:
        if gomod and s.startswith(gomod):
            d = s[len(gomod):].lstrip("/")
            if d in dirs:
                inside.append(dirs[d])
        elif "." in s.split("/")[0]:
            outside.append("/".join(s.split("/")[:3]))
    return inside, outside


def unit(rel, depth):
    parts = rel.parts[:-1]
    if not parts:
        return "(raiz)"
    return "/".join(parts[:depth])


def sid(s):
    return re.sub(r"\W+", "_", s).strip("_") or "raiz"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__.strip())
    root = pathlib.Path(args[0]).resolve()
    out = pathlib.Path(args[1]) if len(args) > 1 else None
    opt = lambda k, d: int(sys.argv[sys.argv.index(k) + 1]) if k in sys.argv else d
    n_ext = opt("--externals", 5)
    all_files = list(files(root))
    known = {f.relative_to(root) for f in all_files}
    mods = {}
    for r in known:
        if r.suffix == ".py":
            key = "/".join(r.with_suffix("").parts)
            mods[key] = r
            if r.name == "__init__.py":
                mods["/".join(r.parent.parts)] = r
    gomod = None
    gm = root / "go.mod"
    if gm.exists():
        m = re.search(r"^module\s+(\S+)", gm.read_text(), re.M)
        gomod = m.group(1) if m else None
    godirs = {}
    for r in known:
        if r.suffix == ".go":
            godirs.setdefault("/".join(r.parent.parts), r)

    deps = collections.defaultdict(set)
    ext_of = {}
    ext = collections.Counter()
    langs = collections.defaultdict(collections.Counter)
    for f in all_files:
        r = f.relative_to(root)
        if r.suffix == ".py":
            i, o = py_imports(f, root, mods)
            lang = "Python"
        elif r.suffix == ".go":
            i, o = go_imports(f, root, gomod, godirs)
            lang = "Go"
        else:
            i, o = js_imports(f, root, known)
            lang = "TS" if r.suffix in (".ts", ".tsx", ".mts", ".cts") else "JS"
        deps[r] |= set(i)
        ext_of[r] = set(o)
        ext.update(set(o))
        langs[r] = lang
    std = set(getattr(sys, "stdlib_module_names", ()))
    for k in list(ext):
        if k in std or k.startswith("node:") or k in ("fs", "path", "os", "http", "https", "url", "crypto", "util", "events", "child_process", "stream"):
            del ext[k]

    depth = opt("--depth", 0)
    if not depth:
        depth = 1
        while depth < 6 and len({unit(r, depth) for r in known}) <= MAX and len({unit(r, depth + 1) for r in known}) <= MAX and {unit(r, depth + 1) for r in known} != {unit(r, depth) for r in known}:
            depth += 1

    def view(level_files, d, vid, title, prefix):
        units = collections.defaultdict(list)
        for r in level_files:
            units[unit(r, d)].append(r)
        names = sorted(units, key=lambda u: -len(units[u]))
        if len(names) > MAX:
            keep, rest = names[: MAX - 1], names[MAX - 1:]
            units["(outros)"] = [r for u in rest for r in units.pop(u)]
            names = keep + ["(outros)"]
        of = {r: u for u in names for r in units[u]}
        edges = collections.Counter()
        for r in level_files:
            for t in deps[r]:
                if t in of and of[t] != of[r]:
                    edges[(of[r], of[t])] += 1
        nodes = []
        for u in names:
            fs = units[u]
            lc = collections.Counter(langs[r] for r in fs).most_common(1)[0][0]
            nodes.append({
                "id": sid(prefix + u), "label": (u[len(prefix):] if u.startswith(prefix) else u) or u,
                "sub": f"{len(fs)} arquivo{'s' if len(fs) > 1 else ''} {lc}",
                "kind": "entry" if any(ENTRY.search(str(r)) for r in fs) else "component",
                "status": "verified", "file": u if u not in ("(raiz)", "(outros)") else "",
            })
        es = [{"from": sid(prefix + a), "to": sid(prefix + b), "label": "importa", "kind": "control", "detail": f"{c} import{'s' if c > 1 else ''} de arquivo"} for (a, b), c in edges.most_common()]
        return {"id": vid, "title": title, "summary": "", "blocks": [{"type": "graph", "id": "g_" + vid, "title": "Quem importa quem", "direction": "RIGHT", "nodes": nodes, "edges": es}]}, units

    ov, units = view(list(known), depth, "overview", "Visão geral", "")
    g = ov["blocks"][0]
    if n_ext:
        top = ext.most_common(n_ext)
        for name, c in top:
            g["nodes"].append({"id": sid("ext_" + name), "label": name, "sub": "dependência externa", "kind": "external", "status": "verified"})
        users = collections.defaultdict(collections.Counter)
        of = {r: u for u, fs in units.items() for r in fs}
        for r, names in ext_of.items():
            for name in names:
                if name in dict(top) and r in of:
                    users[name][of[r]] += 1
        for name, _ in top:
            for u, c in users[name].most_common(3):
                g["edges"].append({"from": sid(u), "to": sid("ext_" + name), "label": "usa", "kind": "data", "detail": f"{c} arquivo{'s' if c > 1 else ''}"})
    views = [ov]
    for u, fs in sorted(units.items(), key=lambda kv: -len(kv[1])):
        if u in ("(raiz)", "(outros)"):
            continue
        sub = {unit(r, depth + 1) for r in fs}
        if len(sub) >= 2:
            v, _ = view(fs, depth + 1, sid(u), u, u + "/")
            if len(v["blocks"][0]["nodes"]) >= 2:
                views.append(v)
                for n in g["nodes"]:
                    if n["id"] == sid(u):
                        n["view"] = sid(u)
        if len(views) > 8:
            break
    scene = {
        "title": f"TODO: o achado sobre {root.name}",
        "subtitle": f"{len(known)} arquivos · imports lidos em {datetime.date.today().isoformat()}",
        "basis": "code",
        "source": str(root),
        "root": str(root),
        "date": datetime.date.today().isoformat(),
        "summary": "",
        "views": views,
    }
    text = json.dumps(scene, ensure_ascii=False, indent=2)
    if out:
        out.write_text(text + "\n")
        print(out.resolve())
        print(f"{len(known)} arquivos, {len(views)} vistas, {sum(len(v['blocks'][0]['nodes']) for v in views)} nós; troque o title e escreva os summaries")
    else:
        print(text)


if __name__ == "__main__":
    main()
