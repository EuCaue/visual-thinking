import subprocess, tempfile


def test_context_menu():
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        out_path = f.name
    res = subprocess.run(
        [
            "python3",
            "scripts/build-scene.py",
            "examples/05-fluxo-autenticacao.json",
            out_path,
        ],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, res.stderr
    with open(out_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "vt-menu" in content
    assert "contextmenu" in content
    assert "Isolar vizinhança" in content
    assert "Ajustar à tela" in content


if __name__ == "__main__":
    test_context_menu()
    print("PASS")
