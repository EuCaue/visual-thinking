import json, subprocess, tempfile


def test_consequences_and_scenarios():
    scene = {
        "title": "Cenários e Consequências",
        "basis": "decision",
        "summary": "Teste",
        "views": [
            {
                "id": "main",
                "title": "Principal",
                "summary": "Visão com cenários",
                "scenarios": {
                    "controls": [
                        {
                            "id": "vol",
                            "label": "Volume",
                            "options": ["Baixo", "Alto"],
                            "default": "Baixo",
                        }
                    ]
                },
                "blocks": [
                    {
                        "type": "graph",
                        "id": "g1",
                        "title": "Caminhos de Decisão",
                        "nodes": [
                            {
                                "id": "d1",
                                "label": "Decisão",
                                "sub": "Escolha de protocolo",
                                "kind": "decision",
                            },
                            {
                                "id": "c1",
                                "label": "REST",
                                "sub": "Simples",
                                "kind": "component",
                                "consequence": {"order": 1, "polarity": "ok"},
                            },
                            {
                                "id": "c2",
                                "label": "gRPC",
                                "sub": "Performático",
                                "kind": "component",
                                "consequence": {"order": 1, "polarity": "ok"},
                            },
                        ],
                        "edges": [
                            {"from": "d1", "to": "c1", "label": "opção 1", "prob": 0.5},
                            {"from": "d1", "to": "c2", "label": "opção 2", "prob": 0.5},
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
    assert "vt-scenarios-bar" in content
    assert "isolateConsequencePath" in content


if __name__ == "__main__":
    test_consequences_and_scenarios()
    print("PASS")
