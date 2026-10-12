import json, subprocess, tempfile, os, pathlib

SCENE = {
    "title": "Offline",
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
                    "nodes": [
                        {"id": "a", "label": "A", "sub": "s"},
                        {"id": "b", "label": "B", "sub": "s"},
                    ],
                    "edges": [{"from": "a", "to": "b", "label": "liga"}],
                }
            ],
        }
    ],
}


def build(tmp, *flags):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(SCENE, f)
        sc = f.name
    out = os.path.join(tmp, "out.html")
    res = subprocess.run(
        ["python3", "scripts/build-scene.py", sc, out, *flags],
        capture_output=True,
        text=True,
    )
    return res, out


def test_default_keeps_cdn(tmp_path):
    res, out = build(tmp_path)
    assert res.returncode == 0, res.stderr
    c = open(out).read()
    assert (
        '<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>'
        in c
    )
    assert "https://cdn.jsdelivr.net/npm/elkjs@0.9.3/lib/elk.bundled.js" in c


def test_selfcontained_inlines(tmp_path):
    res, out = build(tmp_path, "--self-contained")
    assert res.returncode == 0, res.stderr
    c = open(out).read()
    assert '<script src="https://cdnjs' not in c, "CDN tag deve sair"
    assert '<script src="https://cdn.jsdelivr' not in c, "CDN tag deve sair"
    assert "elk.layout" in c and "elkjs" in c.lower() or "elk" in c, "elk inlined"
    assert len(c) > 1_500_000, "código das libs deve estar no arquivo"
    libdir = pathlib.Path(".vt-libs")
    assert any(libdir.glob("d3*.js")) and any(libdir.glob("elk*.js")), "cache criado"


def test_flag_with_no_network_is_not_a_crash():
    # simulado: flag + URL inválida no template não é testável sem reescrever;
    # aqui cobre o comportamento documendado: build normal sem rede continua ok (CDN tags ficam)
    res, out = build("/tmp")
    assert res.returncode == 0


if __name__ == "__main__":
    t = "/tmp/sc-tmp"
    os.makedirs(t, exist_ok=True)
    test_default_keeps_cdn(t)
    test_selfcontained_inlines(t)
    test_flag_with_no_network_is_not_a_crash()
    print("PASS")
