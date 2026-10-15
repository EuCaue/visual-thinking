"""Text budget lint: long strings, talk about the page, details that repeat the label."""

import json, subprocess, tempfile


def lint(scene, *flags):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(scene, f, ensure_ascii=False)
    r = subprocess.run(["python3", "scripts/build-scene.py", f.name, "--validate-only", *flags], capture_output=True, text=True)
    return r.returncode, [l.split("note: text: ", 1)[1] for l in r.stdout.splitlines() if "note: text: " in l]


def scene(**kw):
    s = {
        "title": "Fila separa o checkout do envio de email",
        "basis": "code",
        "summary": "O checkout responde antes do email sair.",
        "views": [{"id": "m", "title": "V", "blocks": [{
            "type": "graph", "id": "g", "title": "Dois processos e uma fila",
            "nodes": [
                {"id": "api", "label": "API", "sub": "recebe o pedido"},
                {"id": "q", "label": "Fila", "sub": "guarda jobs", "kind": "queue"},
            ],
            "edges": [{"from": "api", "to": "q", "label": "enfileira"}],
        }]}],
    }
    s.update(kw)
    return s


def test_clean_scene_has_no_text_warning():
    code, w = lint(scene())
    assert code == 0 and w == [], w


def test_caps_and_meta():
    s = scene(title="Esta página mostra, em cinco abas, como o checkout separa o envio de email do pedido e da fila",
              summary="Clique em qualquer caixa para ver mais detalhes no painel da direita.")
    g = s["views"][0]["blocks"][0]
    g["nodes"][0]["sub"] = "recebe o pedido do cliente e valida tudo antes"
    g["nodes"][0]["detail"] = "Recebe o pedido."
    _, w = lint(s)
    joined = "\n".join(w)
    assert "scene title has" in joined, joined
    assert "describes the page" in joined, joined
    assert "'API' sub has 9 words" in joined, joined
    assert "repeats the label/sub" in joined, joined


def test_subject_matter_is_not_meta():
    s = scene()
    s["views"][0]["blocks"][0]["nodes"][0]["label"] = "Usuário clica em entrar"
    _, w = lint(s)
    assert not any("navigation" in x for x in w), w


def test_summary_that_lists_the_drawing():
    s = scene()
    s["views"][0]["summary"] = "API, Fila e o resto: a API manda para a Fila."
    s["views"][0]["blocks"][0]["nodes"].append({"id": "w", "label": "Worker", "sub": "envia"})
    s["views"][0]["summary"] = "Mostra API, Fila e Worker."
    _, w = lint(s)
    assert any("repeats 3 labels" in x for x in w), w


def test_view_word_total():
    s = scene()
    s["views"][0]["blocks"].append({"type": "cards", "id": "c", "title": "Muito texto", "items": [{"title": f"C{i}", "text": "palavra " * 14} for i in range(20)]})
    _, w = lint(s)
    assert any("turned into prose" in x for x in w), w


def test_flag_turns_lint_off():
    _, w = lint(scene(title="um título longo demais para o orçamento de doze palavras do lint de texto"), "--no-text-lint")
    assert w == [], w


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
    print("PASS")
