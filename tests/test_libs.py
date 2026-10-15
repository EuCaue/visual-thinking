"""Optional libraries: code (highlight.js), math (KaTeX), map (topojson + embedded geometry), dagre engine, sketch style (rough.js).

The build must add only the libraries a scene uses; the page must render each block with no error,
offline (--self-contained), and the validator must name broken fields.
"""

import json, pathlib, subprocess, sys, tempfile

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from _headless import build, run

SCENE = {
    "title": "Libs", "basis": "docs", "style": "sketch", "math": True,
    "views": [{"id": "m", "title": "V", "blocks": [
        {"type": "code", "id": "c", "title": "Trecho", "lang": "ts", "start": 10, "code": "const a = 1;\n// nota\nfunction f(x: number) { return x * 2; }", "highlight": [{"line": 11, "note": "comentário"}]},
        {"type": "math", "id": "x", "title": "Fórmula", "tex": "E = mc^2", "text": "Com $c$ constante."},
        {"type": "map", "id": "br", "title": "Estados", "geo": "br", "values": {"SP": 3, "RJ": 2, "MG": 1}, "points": [{"label": "SP", "lat": -23.5, "lon": -46.6}]},
        {"type": "map", "id": "w", "title": "Países", "geo": "world", "values": {"Brazil": 3, "Portugal": 1}},
        {"type": "graph", "id": "g", "title": "Dagre", "engine": "dagre", "groups": [{"id": "k", "label": "K"}],
         "nodes": [{"id": "a", "label": "A", "sub": "x"}, {"id": "b", "label": "B", "sub": "y", "group": "k"}, {"id": "c2", "label": "C", "sub": "z", "group": "k"}],
         "edges": [{"from": "a", "to": "b", "label": "liga"}, {"from": "b", "to": "c2", "label": "chama"}]},
    ]}],
}

PROBE = """window.__libs = { code: document.querySelectorAll('.vt-code .hljs-keyword').length, math: document.querySelectorAll('.vt-math math').length,
  mapBr: document.querySelectorAll('[data-block="br"] .map-r').length, mapBrOn: document.querySelectorAll('[data-block="br"] .hm-cell').length,
  mapW: document.querySelectorAll('[data-block="w"] .map-r').length, dagre: document.querySelectorAll('[data-block="g"] .nd').length,
  dagreGroup: document.querySelectorAll('[data-block="g"] .grp').length, rough: document.querySelectorAll('.rough').length,
  libs: Array.prototype.map.call(document.querySelectorAll('script'), function (s) { return s.textContent.slice(0, 0) + (s.id || ''); }).filter(Boolean) };
  document.title = JSON.stringify(window.__libs);"""


def sh(*a):
    return subprocess.run(["python3", *a], capture_output=True, text=True)


def test_build_adds_only_what_is_used():
    import re
    tpl = pathlib.Path("templates/canvas.html").read_text()
    urls = {k: v["url"] for k, v in json.loads(re.search(r'<script id="vt-libs" type="application/json">(.*?)</script>', tpl, re.S).group(1)).items() if "global" in v}
    tag = lambda page, k: f'<script src="{urls[k]}"></script>' in page
    with tempfile.TemporaryDirectory() as t:
        src, out = pathlib.Path(t) / "s.json", pathlib.Path(t) / "s.html"
        plain = {"title": "T", "basis": "docs", "views": [{"id": "m", "title": "V", "blocks": [{"type": "text", "id": "t", "text": "x"}]}]}
        src.write_text(json.dumps(plain)); r = sh("scripts/build-scene.py", str(src), str(out), "--no-text-lint")
        page = out.read_text()
        assert r.returncode == 0 and not any(tag(page, k) for k in urls), "cena simples não carrega libs opcionais"
        assert 'id="vt-geo-' not in page, "nem geometria"
        src.write_text(json.dumps(SCENE)); r = sh("scripts/build-scene.py", str(src), str(out), "--no-text-lint")
        page = out.read_text()
        for k in ("rough", "hljs", "katex", "topojson", "dagre"):
            assert tag(page, k), k
        assert 'id="vt-geo-br"' in page and 'id="vt-geo-world"' in page, "geometria embutida"


def test_libs_render_offline():
    with tempfile.TemporaryDirectory() as t:
        page = build(SCENE, t, "libs", act=PROBE)
        r = run(page, 1280, 900, "?mode=draw")
        assert not r["errors"], r["errors"]
        assert all(b["w"] > 0 and b["h"] > 0 for b in r["blocks"]), r["blocks"]
        html = pathlib.Path(page).read_text()
        assert '<script src="https://' not in html, "self-contained: nenhuma lib pela rede"
    # the probe writes its counts into document.title, which --dump-dom returns
    with tempfile.TemporaryDirectory() as t:
        page = build(SCENE, t, "libs2", act=PROBE)
        import re, html as H
        out = subprocess.run([__import__("_headless").CHROME, "--headless=new", "--disable-gpu", "--no-sandbox", "--window-size=1280,900", "--virtual-time-budget=10000", "--dump-dom", page.resolve().as_uri() + "?mode=draw"], capture_output=True, text=True, timeout=90).stdout
        m = re.search(r"<title>(\{.*?\})</title>", out, re.S)
        assert m, "probe sem resultado"
        c = json.loads(H.unescape(m.group(1)))
        assert c["code"] >= 2, c
        assert c["math"] >= 1, c
        assert c["mapBr"] == 27 and c["mapBrOn"] == 3, c
        assert c["mapW"] > 150, c
        assert c["dagre"] == 3 and c["dagreGroup"] == 1, c
        assert c["rough"] > 3, c


def test_validator_names_broken_fields():
    bad = {"title": "T", "basis": "docs", "style": "pastel", "views": [{"id": "m", "title": "V", "blocks": [
        {"type": "code", "id": "c", "title": "x", "code": "a\nb", "highlight": [9]},
        {"type": "math", "id": "x", "title": "x"},
        {"type": "map", "id": "p", "title": "x", "geo": "marte", "points": [{"label": "z", "lat": 99, "lon": 0}]},
        {"type": "graph", "id": "g", "title": "x", "engine": "cola", "nodes": [{"id": "a", "label": "A", "sub": "s"}], "edges": []},
    ]}]}
    with tempfile.TemporaryDirectory() as t:
        f = pathlib.Path(t) / "b.json"; f.write_text(json.dumps(bad))
        r = sh("scripts/build-scene.py", str(f), "--validate-only", "--no-text-lint")
        o = r.stdout
        for msg in ("style desconhecido", "highlight fora do trecho", "math sem tex", "geo desconhecido", "sem lat/lon válidos", "engine desconhecido"):
            assert msg in o, (msg, o)


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
    print("PASS")
