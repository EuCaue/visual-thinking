import json, subprocess, tempfile


def build(motion):
    scene = {
        "title": "M",
        "basis": "docs",
        "summary": "S",
        "views": [
            {
                "id": "m",
                "title": "V",
                "summary": "V",
                "blocks": [
                    {
                        "type": "graph",
                        "id": "g",
                        "title": "G",
                        "motion": motion,
                        "nodes": [
                            {"id": "a", "label": "A", "sub": "s"},
                            {"id": "b", "label": "B", "sub": "s"},
                            {"id": "c", "label": "C", "sub": "s"},
                        ],
                        "edges": [
                            {"from": "a", "to": "b", "label": "dados", "kind": "data"},
                            {"from": "a", "to": "c", "label": "fluxo", "kind": "event"},
                        ],
                    }
                ],
            }
        ],
    }
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(scene, f)
        sc = f.name
    out = "/tmp/motion-" + ("on" if motion else "off") + ".html"
    res = subprocess.run(
        ["python3", "scripts/build-scene.py", sc, out], capture_output=True, text=True
    )
    assert res.returncode == 0, res.stderr
    return out


def build_kinds(kinds):
    scene = {
        "title": "M",
        "basis": "docs",
        "summary": "S",
        "views": [
            {
                "id": "m",
                "title": "V",
                "summary": "V",
                "blocks": [
                    {
                        "type": "graph",
                        "id": "g",
                        "title": "G",
                        "motion": True,
                        "nodes": [
                            {"id": "a", "label": "A", "sub": "s"},
                            {"id": "b", "label": "B", "sub": "s"},
                        ],
                        "edges": [
                            {"from": "a", "to": "b", "label": "e", "kind": k}
                            for k in kinds
                        ],
                    }
                ],
            }
        ],
    }
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(scene, f)
        sc = f.name
    out = "/tmp/motion-kinds.html"
    res = subprocess.run(
        ["python3", "scripts/build-scene.py", sc, out], capture_output=True, text=True
    )
    assert res.returncode == 0, res.stderr
    return out


if __name__ == "__main__":
    off = build(False)
    on = build(True)
    kinds = build_kinds(["data", "event", "control", "error"])
    import agent_check

    agent_check.motion(off, on, kinds)
    print("PASS")
