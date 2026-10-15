"""extract-deps drafts a valid scene from real imports; scene-diff marks added, removed and changed."""

import json, pathlib, subprocess, tempfile

FIXTURE = {
    "api/server.ts": "import { charge } from '../billing/charge';\nimport express from 'express';\n",
    "api/routes.ts": "import { charge } from '../billing/charge.js';\nconst db = require('../db/pool');\n",
    "billing/charge.ts": "import Stripe from 'stripe';\nimport { pool } from '../db/pool';\n",
    "db/pool.ts": "import { Pool } from 'pg';\n",
    "worker/main.py": "from worker import mailer\nimport redis\n",
    "worker/mailer.py": "import smtplib\nfrom tools.fmt import money\n",
    "tools/fmt.py": "def money(x):\n    return x\n",
    "tools/__init__.py": "",
    "worker/__init__.py": "",
    "api/server.test.ts": "import { charge } from '../billing/charge';\n",
}


def sh(*a):
    return subprocess.run(["python3", *a], capture_output=True, text=True)


def test_extract_deps():
    with tempfile.TemporaryDirectory() as t:
        root = pathlib.Path(t) / "repo"
        for p, c in FIXTURE.items():
            (root / p).parent.mkdir(parents=True, exist_ok=True)
            (root / p).write_text(c)
        out = pathlib.Path(t) / "deps.json"
        r = sh("scripts/extract-deps.py", str(root), str(out))
        assert r.returncode == 0, r.stderr
        s = json.loads(out.read_text())
        g = s["views"][0]["blocks"][0]
        ids = {n["id"] for n in g["nodes"]}
        pairs = {(e["from"], e["to"]) for e in g["edges"]}
        assert {"api", "billing", "db", "worker", "tools"} <= ids, ids
        assert ("api", "billing") in pairs and ("billing", "db") in pairs and ("api", "db") in pairs and ("worker", "tools") in pairs, pairs
        assert ("db", "api") not in pairs
        assert any(n["kind"] == "external" and n["label"] in ("stripe", "pg", "express", "redis") for n in g["nodes"]), g["nodes"]
        assert not any(n["label"] in ("smtplib",) for n in g["nodes"]), "stdlib fica de fora"
        assert next(n for n in g["nodes"] if n["id"] == "worker")["kind"] == "entry", "main.py marca ponto de entrada"
        v = sh("scripts/build-scene.py", str(out), "--validate-only", "--no-text-lint")
        assert v.returncode == 0, v.stdout


def test_scene_diff():
    before = {"title": "A", "basis": "code", "views": [{"id": "m", "title": "V", "blocks": [{"type": "graph", "id": "g", "title": "G",
              "nodes": [{"id": "a", "label": "A", "sub": "x"}, {"id": "b", "label": "B", "sub": "x"}, {"id": "c", "label": "C", "sub": "x"}],
              "edges": [{"from": "a", "to": "b", "label": "chama"}, {"from": "b", "to": "c", "label": "chama"}]}]}]}
    after = json.loads(json.dumps(before))
    g = after["views"][0]["blocks"][0]
    g["nodes"] = [n for n in g["nodes"] if n["id"] != "c"] + [{"id": "d", "label": "D", "sub": "y"}]
    g["nodes"][0]["sub"] = "mudou"
    g["edges"] = [{"from": "a", "to": "b", "label": "chama"}, {"from": "b", "to": "d", "label": "publica"}]
    with tempfile.TemporaryDirectory() as t:
        pb, pa, po = (pathlib.Path(t) / n for n in ("b.json", "a.json", "o.json"))
        pb.write_text(json.dumps(before)); pa.write_text(json.dumps(after))
        r = sh("scripts/scene-diff.py", str(pb), str(pa), str(po))
        assert r.returncode == 0, r.stderr
        o = json.loads(po.read_text())["views"][0]["blocks"][0]
        mark = {n["id"]: n.get("diff") for n in o["nodes"]}
        assert mark == {"a": "changed", "b": None, "d": "added", "c": "removed"}, mark
        emark = {(e["from"], e["to"]): e.get("diff") for e in o["edges"]}
        assert emark[("b", "d")] == "added" and emark[("b", "c")] == "removed" and emark[("a", "b")] is None, emark
        v = sh("scripts/build-scene.py", str(po), "--validate-only", "--no-text-lint")
        assert v.returncode == 0, v.stdout


if __name__ == "__main__":
    test_extract_deps()
    test_scene_diff()
    print("PASS")
