import json, subprocess, tempfile


def test_tornado_chart():
    scene = {
        "title": "Análise de Sensibilidade",
        "basis": "decision",
        "summary": "Sensibilidade do projeto",
        "views": [
            {
                "id": "main",
                "title": "Sensibilidade",
                "summary": "Resumo de sensibilidade",
                "blocks": [
                    {
                        "type": "chart",
                        "id": "torn_1",
                        "kind": "tornado",
                        "title": "Custo é o fator determinante",
                        "baseline": {"label": "Caso Base", "value": 100},
                        "series": [
                            {
                                "name": "Custo Infra",
                                "low": 70,
                                "high": 140,
                                "lowLabel": "-30%",
                                "highLabel": "+40%",
                            },
                            {
                                "name": "Equipe",
                                "low": 90,
                                "high": 115,
                                "lowLabel": "-10%",
                                "highLabel": "+15%",
                            },
                        ],
                    }
                ],
            }
        ],
    }
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(scene, f)
        sc_path = f.name
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        out_path = f.name

    res = subprocess.run(
        ["python3", "scripts/build-scene.py", sc_path, out_path],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0
    with open(out_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "renderTornado" in content


if __name__ == "__main__":
    test_tornado_chart()
    print("PASS")
