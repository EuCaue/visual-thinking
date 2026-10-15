"""entity, heatmap, gantt, sankey, treemap: examples validate; broken scenes fail with a line that names the problem."""

import copy, json, pathlib, subprocess, tempfile

EX = ["13-data-model", "14-schedule", "15-budget-flow", "16-heatmap"]


def validate(scene):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(scene, f, ensure_ascii=False)
    r = subprocess.run(["python3", "scripts/build-scene.py", f.name, "--validate-only", "--no-text-lint"], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def one(block):
    return {"title": "T", "basis": "docs", "views": [{"id": "m", "title": "V", "blocks": [block]}]}


def ex(name):
    return json.loads(pathlib.Path(f"examples/{name}.json").read_text())


def test_examples_validate():
    for n in EX:
        code, out = validate(ex(n))
        assert code == 0, n + "\n" + out


def test_entity_dangling_relation():
    b = copy.deepcopy(ex("13-data-model")["views"][0]["blocks"][0])
    b["relations"].append({"from": "colaborador", "to": "fantasma"})
    code, out = validate(one(b))
    assert code == 1 and "relation has no valid 'to'" in out, out


def test_entity_duplicate_field():
    b = {"type": "entity", "id": "e", "title": "x", "entities": [{"id": "t", "fields": [{"name": "id"}, {"name": "id"}]}]}
    code, out = validate(one(b))
    assert code == 1 and "duplicate fields" in out, out


def test_gantt_missing_dep_and_reverse_dates():
    b = {"type": "gantt", "id": "g", "title": "x", "tasks": [{"id": "a", "label": "A", "start": "2026-02-01", "end": "2026-01-01", "deps": ["z"]}]}
    code, out = validate(one(b))
    assert code == 1 and "ends before it starts" in out and "missing id" in out, out


def test_sankey_cycle():
    b = {"type": "sankey", "id": "s", "title": "x", "nodes": [{"id": "a", "label": "A"}, {"id": "b", "label": "B"}], "links": [{"from": "a", "to": "b", "value": 1}, {"from": "b", "to": "a", "value": 1}]}
    code, out = validate(one(b))
    assert code == 1 and "cycle" in out, out


def test_heatmap_shape():
    b = {"type": "heatmap", "id": "h", "title": "x", "x": ["a", "b"], "y": ["l1"], "values": [[1, 2, 3]]}
    code, out = validate(one(b))
    assert code == 1 and "3 values for 2 columns" in out, out


def test_treemap_leaf_without_value():
    b = {"type": "treemap", "id": "t", "title": "x", "root": {"label": "r", "children": [{"label": "a"}]}}
    code, out = validate(one(b))
    assert code == 1 and "has no numeric value" in out, out


def test_runtime_has_renderers_and_sankey_lib():
    c = pathlib.Path("templates/canvas.html").read_text()
    for fn in ("drawEntity", "drawHeatmap", "drawGantt", "drawSankey", "drawTreemap", "d3-sankey@0.12.3"):
        assert fn in c, fn


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
    print("PASS")
