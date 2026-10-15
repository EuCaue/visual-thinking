"""custom block: the agent's own SVG, HTML or draw code, with pinned external libraries; validator guards the contract."""

import json, pathlib, re, subprocess, sys, tempfile, html as H

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from _headless import build, CHROME

EX = json.loads(pathlib.Path("examples/21-custom-drawing.json").read_text())
PROBE = """<script>setTimeout(function () { var q = function (s) { return document.querySelectorAll(s).length; };
var views = ['svg', 'draw', 'lib'], out = {}, i = 0;
(function next() { if (i >= views.length) { document.title = JSON.stringify(out); return; } var v = views[i++]; document.querySelector('#views [data-view="' + v + '"]').click();
 setTimeout(function () { out[v] = { paths: q('#world path'), clickable: q('#world [data-title]'), failed: /falhou/.test(document.getElementById('world').textContent) }; next(); }, 700); })(); }, 1500);</script>"""


def validate(scene):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(scene, f, ensure_ascii=False)
    return subprocess.run(["python3", "scripts/build-scene.py", f.name, "--validate-only", "--no-text-lint"], capture_output=True, text=True).stdout


def test_custom_renders_offline():
    with tempfile.TemporaryDirectory() as t:
        page = build(EX, t, "custom")
        page.write_text(page.read_text().replace("</body>", PROBE + "</body>"))
        assert '<script src="https://' not in page.read_text(), "lib externa inlined"
        out = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox", "--window-size=1280,860", "--virtual-time-budget=15000", "--dump-dom", page.resolve().as_uri() + "?mode=draw"], capture_output=True, text=True, timeout=90).stdout
        m = re.search(r"<title>(\{.*?\})</title>", out, re.S)
        assert m, "probe sem resultado"
        r = json.loads(H.unescape(m.group(1)))
        assert r["svg"]["clickable"] == 1 and not r["svg"]["failed"], r
        assert r["draw"]["paths"] >= 10 and r["draw"]["clickable"] == 4 and not r["draw"]["failed"], r
        assert r["lib"]["paths"] > 30 and not r["lib"]["failed"], r


def test_validator():
    base = {"title": "T", "basis": "docs", "libs": [{"name": "x", "url": "http://example.com/x.js"}], "views": [{"id": "m", "title": "V", "blocks": [
        {"type": "custom", "id": "a", "title": "a", "svg": "<g/>", "draw": "return"},
        {"type": "custom", "id": "b", "title": "b", "svg": "<rect fill='#ff0000'/>"},
        {"type": "custom", "id": "c", "title": "c", "draw": "return", "libs": ["nope"]},
    ]}]}
    o = validate(base)
    for msg in ("exactly one of svg, html and draw", "needs width and height", "literal color", "unknown lib 'nope'", "pinned version", "custom has no alt"):
        assert msg in o, (msg, o)
    assert "note" not in validate(EX).replace("note: view", ""), validate(EX)


if __name__ == "__main__":
    test_validator()
    test_custom_renders_offline()
    print("PASS")
