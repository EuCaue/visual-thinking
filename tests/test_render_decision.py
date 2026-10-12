import json, subprocess, tempfile

def test_decision_html_build():
    scene = {
        "title": "Decisão de Teste",
        "basis": "decision",
        "summary": "Resumo de teste",
        "views": [{
            "id": "main",
            "title": "Principal",
            "summary": "Visão principal",
            "blocks": [{
                "type": "decision",
                "id": "dec_test",
                "title": "Opção A lidera",
                "options": [
                    {"id": "opt_a", "label": "Opção A"},
                    {"id": "opt_b", "label": "Opção B"}
                ],
                "criteria": [
                    {"id": "c1", "label": "Custo", "weight": 60, "scores": {"opt_a": {"score": 9}, "opt_b": {"score": 3}}},
                    {"id": "c2", "label": "Prazo", "weight": 40, "scores": {"opt_a": {"score": 5}, "opt_b": {"score": 8}}}
                ]
            }]
        }]
    }
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(scene, f)
        sc_path = f.name
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        out_path = f.name
    
    res = subprocess.run(["python3", "scripts/build-scene.py", sc_path, out_path], capture_output=True, text=True)
    assert res.returncode == 0
    with open(out_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "vt-decision" in content, "Faltando componente vt-decision no canvas runtime"

if __name__ == "__main__":
    test_decision_html_build()
    print("PASS")
