import json, subprocess, tempfile, pathlib

def run_validator(scene_dict):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(scene_dict, f)
        path = f.name
    res = subprocess.run(["python3", "scripts/build-scene.py", path, "--validate-only"], capture_output=True, text=True)
    return res

def test_decision_block_validation():
    valid_scene = {
        "title": "Decisão de Banco de Dados",
        "basis": "decision",
        "summary": "Comparação ponderada.",
        "views": [{
            "id": "main",
            "title": "Decisão",
            "summary": "Resumo da decisão",
            "blocks": [{
                "type": "decision",
                "id": "dec_1",
                "title": "Postgres vs Dynamo",
                "options": [
                    {"id": "pg", "label": "PostgreSQL", "reversibility": "two-way"},
                    {"id": "dynamo", "label": "DynamoDB", "reversibility": "one-way"}
                ],
                "criteria": [
                    {
                        "id": "cost",
                        "label": "Custo",
                        "weight": 50,
                        "scores": {"pg": {"score": 8}, "dynamo": {"score": 4}}
                    }
                ]
            }]
        }]
    }
    res = run_validator(valid_scene)
    assert res.returncode == 0, f"Validation failed: {res.stderr}\n{res.stdout}"

def test_decision_block_invalid_cases():
    base_scene = {
        "title": "Decisão Teste",
        "basis": "decision",
        "summary": "Resumo",
        "views": [{
            "id": "main",
            "title": "V",
            "summary": "S",
            "blocks": [{
                "type": "decision",
                "id": "dec",
                "title": "T",
                "options": [{"id": "a", "label": "A"}],
                "criteria": [{"id": "c", "label": "C", "weight": 10, "scores": {"a": {"score": 5}}}]
            }]
        }]
    }
    
    # Empty options
    sc = json.loads(json.dumps(base_scene))
    sc["views"][0]["blocks"][0]["options"] = []
    assert run_validator(sc).returncode == 1

    # Invalid reversibility in option
    sc = json.loads(json.dumps(base_scene))
    sc["views"][0]["blocks"][0]["options"][0]["reversibility"] = "invalid"
    assert run_validator(sc).returncode == 1

    # Negative weight
    sc = json.loads(json.dumps(base_scene))
    sc["views"][0]["blocks"][0]["criteria"][0]["weight"] = -5
    assert run_validator(sc).returncode == 1

    # Invalid vetoBelow
    sc = json.loads(json.dumps(base_scene))
    sc["views"][0]["blocks"][0]["criteria"][0]["vetoBelow"] = "not-a-number"
    assert run_validator(sc).returncode == 1

    # Missing scores
    sc = json.loads(json.dumps(base_scene))
    del sc["views"][0]["blocks"][0]["criteria"][0]["scores"]
    assert run_validator(sc).returncode == 1

def test_tornado_chart_validation():
    valid_tornado = {
        "title": "Análise de Sensibilidade",
        "basis": "decision",
        "summary": "Sensibilidade do projeto",
        "views": [{
            "id": "main",
            "title": "Sensibilidade",
            "summary": "Resumo de sensibilidade",
            "blocks": [{
                "type": "chart",
                "id": "torn_1",
                "kind": "tornado",
                "title": "Custo é o fator determinante",
                "baseline": {"label": "Caso Base", "value": 100},
                "series": [
                    {"name": "Custo Infra", "low": 70, "high": 140, "lowLabel": "-30%", "highLabel": "+40%"},
                    {"name": "Equipe", "low": 90, "high": 115, "lowLabel": "-10%", "highLabel": "+15%"}
                ]
            }]
        }]
    }
    res = run_validator(valid_tornado)
    assert res.returncode == 0, f"Tornado validation failed: {res.stderr}\n{res.stdout}"

    # Missing series
    invalid_tornado = json.loads(json.dumps(valid_tornado))
    invalid_tornado["views"][0]["blocks"][0]["series"] = []
    assert run_validator(invalid_tornado).returncode == 1

    # Missing low
    invalid_tornado = json.loads(json.dumps(valid_tornado))
    del invalid_tornado["views"][0]["blocks"][0]["series"][0]["low"]
    assert run_validator(invalid_tornado).returncode == 1

def test_scenarios_and_graph_attributes():
    scene = {
        "title": "Cenários e Consequências",
        "basis": "decision",
        "summary": "Teste",
        "views": [{
            "id": "main",
            "title": "Principal",
            "summary": "Visão com cenários",
            "scenarios": {
                "controls": [{"id": "vol", "label": "Volume", "options": ["Baixo", "Alto"], "default": "Baixo"}]
            },
            "blocks": [{
                "type": "graph",
                "id": "g1",
                "title": "Caminhos de Decisão",
                "nodes": [
                    {"id": "d1", "label": "Decisão", "sub": "Escolha de protocolo", "kind": "decision", "reversibility": "two-way"},
                    {"id": "c1", "label": "REST", "sub": "Simples", "kind": "component", "consequence": {"order": 1, "polarity": "ok"}},
                    {"id": "c2", "label": "gRPC", "sub": "Performático", "kind": "component", "consequence": {"order": 1, "polarity": "ok"}}
                ],
                "edges": [
                    {"from": "d1", "to": "c1", "label": "opção 1", "prob": 0.5, "reversibility": "two-way"},
                    {"from": "d1", "to": "c2", "label": "opção 2", "prob": 0.5}
                ]
            }]
        }]
    }
    res = run_validator(scene)
    assert res.returncode == 0, f"Graph decision/scenarios validation failed: {res.stderr}\n{res.stdout}"

    # Invalid prob
    invalid_scene = json.loads(json.dumps(scene))
    invalid_scene["views"][0]["blocks"][0]["edges"][0]["prob"] = 1.5
    assert run_validator(invalid_scene).returncode == 1

    # Invalid consequence polarity
    invalid_scene = json.loads(json.dumps(scene))
    invalid_scene["views"][0]["blocks"][0]["nodes"][1]["consequence"]["polarity"] = "unknown_polarity"
    assert run_validator(invalid_scene).returncode == 1

if __name__ == "__main__":
    test_decision_block_validation()
    test_decision_block_invalid_cases()
    test_tornado_chart_validation()
    test_scenarios_and_graph_attributes()
    print("PASS")
