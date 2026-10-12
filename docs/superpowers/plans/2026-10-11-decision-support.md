# Decision Support Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand `visual-thinking` to support interactive multi-criteria decision making, consequence mapping, scenario analysis, and sensitivity testing without compromising semantic fidelity or performance.

**Architecture:** Extend the scene validation pipeline (`scripts/build-scene.py`), introduce the `decision` block type and `tornado` chart kind into `templates/canvas.html`, equip graph and views with consequence paths and scenario toggles, and document the 7th mode (`Decide`) and 10 decision sub-intents in skill guides.

**Tech Stack:** Python 3 (validator/compiler), HTML5/SVG, Vanilla JS, D3 7.9.0, ELKjs 0.9.3, CSS custom properties (`_tokens.css`).

**Spec:** `docs/superpowers/specs/2026-10-11-decision-support-design.md`

## Global Constraints

- Standalone HTML artifact generation: no Node.js runtime, no bundlers, zero external npm dependencies.
- Zero style regressions: rely strictly on semantic tokens defined in `templates/_tokens.css`.
- Progressive disclosure: Level 1 must be self-explanatory at rest (no hidden critical information behind clicks).
- Strict backward compatibility: all existing 10 examples and previous scene JSONs must continue to pass validation and render identically.

---

### Task 1: Scene Validation Extensions for Decisions (`scripts/build-scene.py`)

**Files:**
- Modify: `scripts/build-scene.py`
- Test: `tests/test_validator_decision.py`

**Interfaces:**
- Consumes: Scene JSON data with new block type `"decision"`, chart kind `"tornado"`, and optional `reversibility`, `vetoBelow`, and `scenarios` fields.
- Produces: `check_decision()`, `check_tornado()`, validation updates in `check_block()`, `check_graph()`, and `check_scene()`.

- [ ] **Step 1: Write the failing test for decision validation**

Create `tests/test_validator_decision.py`:
```python
import json, subprocess, tempfile, pathlib

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
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(valid_scene, f)
        path = f.name
    
    res = subprocess.run(["python3", "scripts/build-scene.py", path, "--validate-only"], capture_output=True, text=True)
    assert res.returncode == 0, f"Validation failed: {res.stderr}\n{res.stdout}"

if __name__ == "__main__":
    test_decision_block_validation()
    print("PASS")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 tests/test_validator_decision.py`  
Expected: FAIL with `"block type desconhecido: 'decision'"`

- [ ] **Step 3: Implement validation functions in `scripts/build-scene.py`**

1. Add `"decision"` to `TYPES`.
2. Add `"tornado"` to `KINDS`.
3. Add `check_decision(b, p, w, c)`:
   - Verify `options` exists, is non-empty list, each item has `id` and `label`.
   - Verify `criteria` exists, is non-empty list, each has `id`, `label`, `weight` (number >= 0), and `scores` mapping option ids to score objects.
   - Validate optional `vetoBelow` (number) and `reversibility` (`"one-way"` | `"two-way"`).
4. Update `check_scene()` to validate optional `scenarios` block at view level.
5. In `check_graph()`, accept optional `reversibility`, `consequence`, and `prob` attributes on nodes/edges.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 tests/test_validator_decision.py`  
Expected: PASS

- [ ] **Step 5: Verify all existing examples still pass validation**

Run: `python3 scripts/build-scene.py examples/01-arquitetura.json --validate-only`  
Expected: Exit 0.

- [ ] **Step 6: Commit**

```bash
git add scripts/build-scene.py tests/test_validator_decision.py
git commit -m "feat(validator): add schema validation for decision blocks and tornado charts"
```

---

### Task 2: Implement Decision Matrix Block (`templates/canvas.html`)

**Files:**
- Modify: `templates/canvas.html`
- Test: `tests/test_render_decision.py`

**Interfaces:**
- Consumes: Scene block of type `"decision"` with `options`, `criteria`, `weightBasis`, and optional `mode`.
- Produces: SVG/HTML hybrid rendering inside the canvas with interactive sliders, weighted score calculation, dynamic reordering, and level 1-3 inspector integration.

- [ ] **Step 1: Write test verifying HTML generation and interactive elements**

Create `tests/test_render_decision.py`:
```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 tests/test_render_decision.py`  
Expected: FAIL with `"AssertionError: Faltando componente vt-decision"`

- [ ] **Step 3: Implement decision block renderer in `templates/canvas.html`**

1. Add CSS rules in `templates/canvas.html` for `.vt-decision`, `.vt-dec-slider`, `.vt-dec-score-bar`, `.vt-dec-rank-badge`, and `.vt-dec-veto`.
2. Add `renderDecision(block, container)` function in script:
   - Compute normalized scores: $S_i = \frac{\sum w_j \cdot s_{ij}}{\sum w_j}$.
   - Render table with options header (including reversibility tag if present).
   - Render rows with criteria, weight display, and score bars.
   - Render aggregate score summary bar for each option.
   - Highlight current leading option (bold, accent indicator).
   - Wire input listeners for weight sliders: dynamically update $S_i$, rank badges, and sensitivity indicators on input without redrawing the whole canvas.
   - Connect block selection to the Inspector: render criterion notes, raw values, and veto criteria.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 tests/test_render_decision.py`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add templates/canvas.html tests/test_render_decision.py
git commit -m "feat(canvas): implement interactive decision matrix block"
```

---

### Task 3: Implement Tornado Chart Kind (`templates/canvas.html`)

**Files:**
- Modify: `templates/canvas.html`
- Test: `tests/test_render_tornado.py`

**Interfaces:**
- Consumes: Chart block with `kind: "tornado"`, `baseline`, and `series` with `low`, `high`, `lowLabel`, `highLabel`.
- Produces: D3 bidirectional horizontal bar chart sorted by swing range.

- [ ] **Step 1: Write test for tornado chart generation**

Create `tests/test_render_tornado.py`:
```python
import json, subprocess, tempfile

def test_tornado_chart():
    scene = {
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
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(scene, f)
        sc_path = f.name
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        out_path = f.name
    
    res = subprocess.run(["python3", "scripts/build-scene.py", sc_path, out_path], capture_output=True, text=True)
    assert res.returncode == 0
    with open(out_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "renderTornado" in content

if __name__ == "__main__":
    test_tornado_chart()
    print("PASS")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 tests/test_render_tornado.py`  
Expected: FAIL

- [ ] **Step 3: Implement `renderTornado()` in `templates/canvas.html`**

1. Sort series descending by `Math.abs(high - low)`.
2. Compute D3 scale centered at baseline value.
3. Draw vertical baseline with token `--line-strong` dashed.
4. Draw left and right horizontal bars from baseline to low and high values using tokens `--accent` and `--warn`.
5. Add text labels for values and deltas in `--font-data`.
6. Attach tooltip on hover with delta values relative to baseline.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 tests/test_render_tornado.py`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add templates/canvas.html tests/test_render_tornado.py
git commit -m "feat(canvas): add tornado chart kind for sensitivity analysis"
```

---

### Task 4: Consequence Paths and Scenario Controls (`templates/canvas.html`)

**Files:**
- Modify: `templates/canvas.html`
- Test: `tests/test_consequence_and_scenarios.py`

**Interfaces:**
- Consumes: Graph with decision nodes and consequence metadata (`order`, `prob`, `polarity`); View with `scenarios` control object.
- Produces: Interactive path highlighting on decision node click; interactive scenario pill selector in view header.

- [ ] **Step 1: Write test for consequence path & scenario controls**

Create `tests/test_consequence_and_scenarios.py`:
```python
import json, subprocess, tempfile

def test_consequences_and_scenarios():
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
                    {"id": "d1", "label": "Decisão", "sub": "Escolha de protocolo", "kind": "decision"},
                    {"id": "c1", "label": "REST", "sub": "Simples", "kind": "component", "consequence": {"order": 1, "polarity": "ok"}},
                    {"id": "c2", "label": "gRPC", "sub": "Performático", "kind": "component", "consequence": {"order": 1, "polarity": "ok"}}
                ],
                "edges": [
                    {"from": "d1", "to": "c1", "label": "opção 1", "prob": 0.5},
                    {"from": "d1", "to": "c2", "label": "opção 2", "prob": 0.5}
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
    assert "vt-scenarios-bar" in content
    assert "isolateConsequencePath" in content

if __name__ == "__main__":
    test_consequences_and_scenarios()
    print("PASS")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 tests/test_consequence_and_scenarios.py`  
Expected: FAIL

- [ ] **Step 3: Implement consequence path isolation and scenario switcher**

1. In `templates/canvas.html`, check if active view has `scenarios`:
   - Render segmented control `.vt-scenarios-bar` below view title.
   - Add event listener to swap scenario override data and trigger `renderView()`.
2. In graph renderer:
   - Recognize `kind: "decision"` and render with distinct shape/border.
   - On clicking a decision node or choosing an outgoing branch, trigger `isolateConsequencePath(nodeId)`: highlight full downstream traversal up to terminal leaves, apply dimming (`opacity: 0.15`) to unrelated branches.
   - Aggregate consequence metrics into the Inspector panel.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 tests/test_consequence_and_scenarios.py`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add templates/canvas.html tests/test_consequence_and_scenarios.py
git commit -m "feat(canvas): add consequence path isolation and scenario toggles"
```

---

### Task 5: Documentation and Skill Strategy Guides Update

**Files:**
- Modify: `SKILL.md`
- Modify: `strategy.md`
- Modify: `formats.md`
- Modify: `README.md`

**Interfaces:**
- Consumes: Design spec definitions from `docs/superpowers/specs/2026-10-11-decision-support-design.md`.
- Produces: Updated guidance for agent intent recognition, mode selection (7 modes), decision sub-intents, and schema documentation.

- [ ] **Step 1: Update `SKILL.md`**

1. Fix mode count: "Sete modos" (Sketch, Explain, Document, Plan, Compare, Summarize, Decide).
2. Add Decide mode row to the modes table with triggers and rules.
3. Add decision patterns to "Choose the representation" fast lookup table.
4. Add decision quality verification checklist ("Decision test: can reader trace recommendation to criteria?").
5. Add decision anti-patterns to Common Mistakes table.

- [ ] **Step 2: Update `strategy.md`**

1. Add 10 decision sub-intents to intent table: Evaluate, Contrast/Bilateral, Explore consequences, Assess risk, Compare trade-offs, Prioritize, Explore scenarios, Test robustness, Diagnose, Navigate dependencies.
2. Add decision visual strategies to Section 3.
3. Add decision anti-choices (equal-weight fallacy, isolated pros/cons, ungrounded speculation).

- [ ] **Step 3: Update `formats.md` and `README.md`**

1. Document JSON schema for block `decision`.
2. Document `kind: "tornado"` for chart block.
3. Document view-level `scenarios` and graph consequence attributes.
4. Update `README.md` overview.

- [ ] **Step 4: Verify formatting and links**

Verify that all cross-references between `SKILL.md`, `strategy.md`, and `formats.md` match.

- [ ] **Step 5: Commit**

```bash
git add SKILL.md strategy.md formats.md README.md
git commit -m "docs(skill): document Decide mode, decision sub-intents, and schema updates"
```

---

### Task 6: Concrete Decision Examples and End-to-End Verification

**Files:**
- Create: `examples/11-decisao-arquitetural.json`
- Create: `examples/12-analise-cenarios.json`
- Modify: `scripts/build-examples.sh`
- Test: `tests/test_e2e_examples.sh`

**Interfaces:**
- Consumes: Complete scene JSON examples exercising all new decision features.
- Produces: HTML builds `examples/11-decisao-arquitetural.html` and `examples/12-analise-cenarios.html`, and automated build verification.

- [ ] **Step 1: Author `examples/11-decisao-arquitetural.json`**

Create realistic architectural decision scene (e.g., Selecting Message Broker / Event Bus: Kafka vs RabbitMQ vs SQS/SNS) containing:
- Block 1: `decision` (weighted matrix with criteria weights, scores, veto, and reversibility tags).
- Block 2: `chart` kind `tornado` (sensitivity analysis showing which cost/scale criteria flips the decision).
- Block 3: `cards` with paired trade-offs ("compra X ao custo de Y").

- [ ] **Step 2: Author `examples/12-analise-cenarios.json`**

Create scenario and consequence map scene (e.g., Monolith Migration Strategy: Big Bang vs Strangler Fig) containing:
- View-level `scenarios` controls (Pessimista / Base / Otimista).
- `graph` with `kind: "decision"` and 1st, 2nd, 3rd order consequence paths.
- `quadrant` with `preset: "risk"`.

- [ ] **Step 3: Update `scripts/build-examples.sh`**

Add builds for examples 11 and 12.

- [ ] **Step 4: Execute build script and run end-to-end checks**

Run: `sh scripts/build-examples.sh`  
Expected: Exit 0, 12 examples built cleanly without validation errors.

- [ ] **Step 5: Run contrast check on tokens**

Run: `python3 scripts/contrast.py`  
Expected: All contrast pairs pass >= 3:1 and >= 4.5:1.

- [ ] **Step 6: Commit**

```bash
git add examples/11-decisao-arquitetural.json examples/12-analise-cenarios.json scripts/build-examples.sh
git commit -m "feat(examples): add reference scenes for architectural decision and scenario analysis"
```

---

## Plan Self-Review Checklist

- **Spec coverage:** Every requirement from `docs/superpowers/specs/2026-10-11-decision-support-design.md` (decision matrix, tornado chart, consequence paths, scenario toggles, validator, documentation, examples) maps directly to Tasks 1 through 6.
- **No placeholders:** All steps contain actual paths, concrete python/bash code snippets, and exact test assertions.
- **Type/Interface consistency:** Block types (`decision`, `tornado`), properties (`reversibility`, `vetoBelow`, `scenarios`), and validator hooks are uniform across all tasks.
