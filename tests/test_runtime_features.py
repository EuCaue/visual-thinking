"""Deep links, editor links, export, step playback, English chrome, and the new blocks rendering in a real browser."""

import json, pathlib, sys, tempfile

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from _headless import build, run

SCENE = {
    "title": "Login goes through the API",
    "basis": "code",
    "lang": "en",
    "root": "/srv/app",
    "editor": "cursor",
    "views": [
        {"id": "a", "title": "First", "summary": "x", "blocks": [{"type": "text", "id": "t", "text": "first view"}]},
        {"id": "flow", "title": "Flow", "summary": "y", "blocks": [{
            "type": "graph", "id": "g", "title": "Three hops",
            "nodes": [
                {"id": "web", "label": "Web", "sub": "form", "file": "web/login.tsx:12"},
                {"id": "api", "label": "API", "sub": "checks", "file": "api/auth.py"},
                {"id": "db", "label": "DB", "sub": "users", "kind": "store"},
            ],
            "edges": [
                {"from": "web", "to": "api", "label": "POST", "step": 1},
                {"from": "api", "to": "db", "label": "select", "step": 2, "kind": "data"},
            ],
        }]},
    ],
}


def test_deep_link_editor_link_export_and_english():
    with tempfile.TemporaryDirectory() as t:
        r = run(build(SCENE, t, "rt"), 1280, 860, "?mode=draw#v=flow&b=g&k=web")
        assert not r["errors"], r["errors"]
        assert r["sel"] and r["sel"].get("id") == "web", r["sel"]
        assert r["detail"] == "Web", r["detail"]
        assert r["fileHref"] == "cursor://file/srv/app/web/login.tsx:12", r["fileHref"]
        assert r["svgLen"] > 2000 and r["svgHasStyle"], (r["svgLen"], r["svgHasStyle"])
        assert r["lang"] == "en" and r["btnRead"] == "Text" and r["level1"] == "Map", (r["lang"], r["btnRead"], r["level1"])


def test_step_playback():
    with tempfile.TemporaryDirectory() as t:
        act = "document.dispatchEvent(new KeyboardEvent('keydown', { key: 'p' }));"
        r = run(build(SCENE, t, "play", act=act), 1280, 860, "?mode=draw#v=flow")
        assert r["count"].startswith("Step 1 of 2"), r["count"]
        assert r["playDim"] > 0, "outros elementos esmaecem"


def test_new_blocks_render():
    with tempfile.TemporaryDirectory() as t:
        for name in ("13-modelo-de-dados", "14-cronograma", "15-fluxo-orcamento", "16-mapa-de-calor"):
            scene = json.loads(pathlib.Path(f"examples/{name}.json").read_text())
            for w in (375, 1280):
                r = run(build(scene, t, name), w, 860, "?mode=draw")
                assert not r["errors"], (name, r["errors"])
                assert r["blocks"] and all(b["w"] > 0 and b["h"] > 0 for b in r["blocks"]), (name, w, r["blocks"])
                assert r["scale"] >= 0.74, (name, w, r["scale"])
            rr = run(build(scene, t, name), 375, 860, "?mode=read")
            assert rr["reading"] and rr["readerSections"] >= 1, name


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
    print("PASS")
