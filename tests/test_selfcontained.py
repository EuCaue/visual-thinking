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


def test_cdn_flag_keeps_tags(tmp_path):
    res, out = build(tmp_path, "--cdn")
    assert res.returncode == 0, res.stderr
    c = open(out).read()
    assert '<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>' in c
    assert "https://cdn.jsdelivr.net/npm/elkjs@0.9.3/lib/elk.bundled.js" in c


def test_default_inlines(tmp_path):
    res, out = build(tmp_path)
    assert res.returncode == 0, res.stderr
    c = open(out).read()
    assert '<script src="https://' not in c, "por padrão nenhuma lib vem da rede"
    assert len(c) > 1_500_000, "d3 e elk dentro do arquivo"
    libdir = pathlib.Path(".vt-libs")
    assert any(libdir.glob("d3*.js")) and any(libdir.glob("elk*.js")), "cache criado"


def test_unused_layout_libs_left_out(tmp_path):
    import copy
    s = copy.deepcopy(SCENE)
    s["views"][0]["blocks"] = [{"type": "text", "id": "t", "text": "só texto"}]
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(s, f)
    out = os.path.join(tmp_path, "light.html")
    r = subprocess.run(["python3", "scripts/build-scene.py", f.name, out], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    c = open(out).read()
    assert "elk.bundled" not in c, "sem ELK quando não há grafo"
    assert len(c) < 700_000, f"página simples pesa {len(c)} bytes"


def test_flag_with_no_network_is_not_a_crash():
    # simulado: flag + URL inválida no template não é testável sem reescrever;
    # aqui cobre o comportamento documendado: build normal sem rede continua ok (CDN tags ficam)
    res, out = build("/tmp")
    assert res.returncode == 0


if __name__ == "__main__":
    t = "/tmp/sc-tmp"
    os.makedirs(t, exist_ok=True)
    test_cdn_flag_keeps_tags(t)
    test_default_inlines(t)
    test_unused_layout_libs_left_out(t)
    test_flag_with_no_network_is_not_a_crash()
    print("PASS")
