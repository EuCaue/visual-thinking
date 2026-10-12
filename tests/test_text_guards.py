import json, subprocess, tempfile

SCENE = {
    "title": "T",
    "basis": "docs",
    "summary": "S",
    "views": [
        {
            "id": "m",
            "title": "V",
            "summary": "V",
            "blocks": [
                {
                    "type": "venn",
                    "id": "v",
                    "title": "V",
                    "sets": [{"label": "A"}, {"label": "B"}],
                    "overlaps": [
                        {"sets": [0, 1], "label": "x"},
                        {"sets": [1, 0], "label": "y"},
                    ],
                },
                {
                    "type": "free",
                    "id": "f",
                    "title": "F",
                    "elements": [
                        {"type": "rect", "id": "a", "x": 0, "y": 0, "w": 60, "h": 40},
                        {"type": "rect", "id": "c", "x": 200, "y": 0, "w": 60, "h": 40},
                        {"type": "arrow", "from": "a", "to": "c", "label": "um"},
                        {"type": "arrow", "from": "a", "to": "c", "label": "dois"},
                    ],
                },
            ],
        }
    ],
}


def test_collision_guards():
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(SCENE, f)
        path = f.name
    res = subprocess.run(
        ["python3", "scripts/build-scene.py", path, "--validate-only"],
        capture_output=True,
        text=True,
    )
    out = res.stdout + res.stderr
    assert "duplicada" in out, "venn com interseção duplicada devia avisar"
    assert "mesmas pontas" in out, "setas duplicadas deviam falhar"


def test_runtime_guards_present():
    src = open("templates/canvas.html", encoding="utf-8").read()
    for needle in ["clearTop", "clashH", "clash", "var rev =", "y0: ev.length"]:
        assert needle in src, "guarda ausente: " + needle


if __name__ == "__main__":
    test_collision_guards()
    test_runtime_guards_present()
    print("PASS")
