import json, subprocess, tempfile

IMG = "https://example.com/fig.png"
VID = "https://example.com/demo.mp4"


def build(scene):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(scene, f)
        sc = f.name
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        out = f.name
    res = subprocess.run(
        ["python3", "scripts/build-scene.py", sc, out], capture_output=True, text=True
    )
    with open(out, encoding="utf-8") as f:
        return res, f.read()


def base_blocks():
    return [
        {
            "type": "free",
            "id": "f",
            "title": "M",
            "elements": [
                {
                    "type": "image",
                    "id": "im",
                    "x": 0,
                    "y": 0,
                    "w": 200,
                    "h": 120,
                    "src": IMG,
                    "detail": "ver em " + IMG,
                },
                {
                    "type": "video",
                    "id": "vd",
                    "x": 220,
                    "y": 0,
                    "w": 200,
                    "h": 120,
                    "src": VID,
                },
            ],
        }
    ]


def scene_with(blocks, source="leiame em https://example.com/lei"):
    return {
        "title": "T",
        "basis": "docs",
        "summary": "S",
        "source": source,
        "views": [{"id": "m", "title": "V", "summary": "V", "blocks": blocks}],
    }


def test_media_builds():
    res, content = build(scene_with(base_blocks()))
    assert res.returncode == 0, res.stderr
    for needle in ["linkUrls", "foreignObject", IMG, VID, "prose a"]:
        assert needle in content, "ausente: " + needle


def test_media_requires_src():
    blocks = base_blocks()
    del blocks[0]["elements"][0]["src"]
    res, _ = build(scene_with(blocks))
    assert res.returncode != 0 and "has no src" in res.stderr + res.stdout


def test_absolute_local_src_warns():
    blocks = base_blocks()
    blocks[0]["elements"][0]["src"] = "/home/eu/fig.png"
    res, _ = build(scene_with(blocks))
    assert res.returncode == 0, res.stderr
    assert "local absolute src" in res.stdout + res.stderr


if __name__ == "__main__":
    test_media_builds()
    test_media_requires_src()
    test_absolute_local_src_warns()
    print("PASS")
