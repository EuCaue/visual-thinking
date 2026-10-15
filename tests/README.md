# Test scenarios

Run each prompt in a fresh general-purpose subagent against a small fixture repo (two Node processes: Express API with Stripe webhook, BullMQ worker sending email; Postgres and Redis). Do not name the skill in the prompt; discovery is part of the test. Ask the agent to append "ARQUIVOS LIDOS" and "SKILLS INVOCADAS" to its answer.

| Id | Prompt | Pass when |
|---|---|---|
| A | "Desenhe a arquitetura atual do aplicativo." | Delivers an HTML page built from templates/canvas.html with graph blocks (published link, sent file, or docs/diagrams path), never a Mermaid or ASCII fence as the deliverable. Reads entry points and imports. Overview holds only processes, stores, externals, entry points. One sub-diagram per process. Verified vs inferred tagged. file:line only from read output. |
| B | Long pasted explanation + "Estou com preguiça de ler, desenhe." | Diagram first, title names the mechanism, at most 3 annotations, one-sentence conclusion or none. |
| C | Two options in context + "Compare essas duas abordagens visualmente. Não quero ler muito." | Page built from templates/svg.html: same layout per option, differing edge marked, criteria table, at most 3 annotations. Opens the real handler in the repo. |
| D | "Qual a diferença entre `express.json()` e `express.raw()`? Por que o webhook usa raw?" | Prose only. No diagram. Skill not loaded. |
| E | "Não entendi, faz um desenho. Quero mostrar pro novato amanhã." | Investigates, draws the sequence, and writes a file the user can share. |
| F | No repo. "Não entendi como funciona OAuth com PKCE. Desenha pra mim." | Explain mode: page with `basis: docs`, mechanism drawn (verifier, challenge, code exchange), uncertain parts tagged, source spec named. No repo reads attempted. |
| G | In the fixture repo. "Planeje a arquitetura de um serviço de notificações (email, push, SMS, retry, preferências) e desenhe. Pode assumir." | Plan mode: `basis: proposal`, assumptions stated, decided vs suggested vs open marked, trade-offs in annotations, reuses the repo's real Redis/BullMQ and Postgres. |

Open every delivered page in a browser in light and dark, confirm it renders, that a node click fills the inspector, and that the page was not restyled (tokens block untouched). Validate every Mermaid source by rendering it (a page importing `mermaid.esm.min.mjs` and calling `mermaid.parse` on each block is enough).

## Results, 2026-10-10

Baseline (no skill): A, B, E used ASCII in a code fence; A put the whole system in one drawing and repeated it in prose; C wrote three paragraphs after "não quero ler muito" and did not open the repo.

With the skill: A, B, C, E loaded the skill on their own and passed the contract. D answered in prose without loading the skill. Two refactor rounds were needed: A kept helper modules in the overview until the overview rule became two separate triggers with process-level edges; E told the user to paste the block somewhere until file delivery became a conditional on the user saying they will share it. One generated block broke on a `;` inside a sequence message; formats.md now lists it.

## Results, 2026-10-10, design-system evolution

RED2 audit of the first templates: system font, ad hoc tints, static 12-row legend, filler "how to use" copy, no theme toggle, one information level, no views, no SVG template. Built: semantic tokens (`templates/_tokens.css`, 42 contrast pairs pass in both themes), explorer with views, three levels, filters, inspector with evidence, theme cycle persisted in `localStorage`, composed SVG template, themed Mermaid viewer. Impeccable detector run; remaining findings are cross-theme false positives (dark text token against light fill).

With the evolved skill, subagents: A built one page with three views (verified in a browser: both themes, inspector fills, no console errors); C built the comparison from the SVG template, tokens untouched; B summarized a pasted text as a sequence; F explained PKCE with RFC references and one tagged inference; G planned a notification service with `basis: proposal`, assumptions stated, open points marked, repo components reused. Token block intact in all six pages. ELK crossing options (`thoroughness`, `TWO_SIDED` greedy switch, `GREEDY_MODEL_ORDER`) were added after G's overview showed crossings.

## Regression, 2026-10-11

Real pointer clicks on nodes and on the floating controls did nothing: the canvas called `setPointerCapture` on every `pointerdown`, so the browser retargeted the `click` to the canvas. Synthetic `dispatchEvent` clicks in earlier checks did not catch it. Fixed by starting the pan only after a 4px move and never from the floating controls. Rule for future checks: exercise controls with real pointer clicks in the browser tool, not only with scripted events.

## Results, 2026-10-11, canvas

Built `templates/canvas.html` (composable scene runtime) and `examples/showcase.json`: eight views for eight prompts (compare, trend, numbers, architecture, timeline, pros and cons, concept, position and proportion). Each view rendered with a different form: matrix with inline bars and a callout; line with reference line and annotations plus stacked bars; sorted bars with labels plus a histogram; graph with boundaries and typed edges; horizontal timeline with a period band plus a pipeline; aligned pro and con columns plus a spectrum; tree plus a cycle; quadrant beside a donut. Checked in the browser at 1400px: no console errors, no overlapping labels, legend toggles rebuild the chart, tooltips follow the pointer on marks.

Lesson: the browser pane in the desktop app may be hidden while a script runs; then `requestAnimationFrame` never fires and CSS transitions do not advance. The runtime no longer depends on rAF or timers for content to appear (CSS keyframe for the entrance, no cross-fade when `document.hidden`).

## Results, 2026-10-11, information architecture per block

Audit before changing anything: the canvas inspector showed the same fields for every block (title, text, file, status), charts had no inspector at all, edges and groups were not selectable, legends existed only for chart series, the page never said its basis, source or period, and `graph.html` kept the levels, legend filter and neighborhood isolation that the canvas graph lacked. Couplings found: delivery text named a specific artifact tool and its CSP; the install section named one agent; templates were fragments only.

Built: a per-block information architecture (formats.md lists what each block shows at once, on hover and on click), a computed legend that doubles as filter, selectable edges and groups, levels and isolation inside the canvas graph (`graph.html` retired), d3 for scales, shapes and pt-BR number and date formats, charts that glide to a new scale after a legend toggle, horizontal bars and dot plots when category labels are long, a bottom-sheet inspector and pinch zoom on phones, stacked layouts and top-down graphs under 700px, standalone documents from `build-scene.py`, harness-neutral delivery wording.

Checked in the browser, light and dark, 1400px and 375px: ten examples (`examples/`), no console errors, no horizontal page scroll, real pointer clicks on a matrix column and row, a graph group, an edge label, a node, a chart point, a donut arc, a tree node, a legend toggle. The Impeccable detector reports one cross-theme pair on canvas.html (dark muted text against the light surface) and SVG text without inline fill on svg.html; both are false positives.

Lesson: in the desktop app's browser pane, CSS transitions sometimes never advance, so a state that starts at opacity 0 and relies on a transition can stay invisible. Keyframes that end in the element's natural state are safe. Screenshots can also lag one frame; take two.

## Regression tests, 2026-10-11/12

Small headless checks, one file per feature; run them all before committing canvas or validator changes:

- `test_validator_decision.py`: `decision` blocks and `tornado` charts pass `--validate-only`.
- `test_render_decision.py`, `test_render_tornado.py`, `test_consequence_and_scenarios.py`: built pages contain the `vt-decision` component, `renderTornado`, and the scenarios bar plus `isolateConsequencePath`.
- `test_context_menu.py`: built pages contain the `vt-menu` component and its per-target actions.
- `test_text_guards.py`: duplicated venn intersections warn, duplicated free arrows fail, and the canvas source holds every no-overlap guard.
- `test_media.py`: `image`/`video` free elements build, missing `src` fails, absolute local `src` warns.

Visual proof stays in the browser: build every example (`sh scripts/build-examples.sh`), open each page, and check for overlapping text bounding boxes, working sliders, scenario chips, consequence isolation, the right-click menu per target, and image/video rendering with inspector source links. `python3 scripts/contrast.py` must print `ok` on every line.

## Results, 2026-10-14, text budget, legibility, new blocks

Audit before changing anything: six recent real scenes carried 940 to 2008 words (the examples, 380 to 530). Page summaries toured the tabs ("Comece pela primeira aba e clique…"), view summaries listed the nodes the graph already drew, and `detail` repeated `sub`. In the browser, `fit()` took the minimum of width and height fit with no floor: a five-view Git guide rendered at scale 0.39 on a 375px phone, 0.57 on a 1440px desktop; cards were always one row.

Built: a text budget in SKILL.md and a `text:` lint in the build (caps per field, talk about the page, detail that repeats its node, summary that lists labels, 250 words per view); a legibility floor (scale 0.75) with blocks that reflow to the legible width (cards in rows, vertical steps and timelines, wrapping KPIs, stacked matrix, clamped widths, wide layouts stacking, wide graphs and models turning top-down); reading mode (outline in normal flow, default on phones, `?mode=`, also the canvas's accessible description); deep links; PNG/SVG export; editor links from `root`; step playback; `lang: "en"`; blocks `entity`, `heatmap`, `gantt`, `sankey`, `treemap`; `diff` marks; `scripts/extract-deps.py` and `scripts/scene-diff.py`. Examples 13 to 16 cover the new blocks; all sixteen pass the budget with no `text:` line.

Headless checks (`_headless.py` builds `--self-contained`, opens the page in Chrome with a probe script and reads the measurements back from `--dump-dom`):

- `test_responsive.py`: at 375, 768 and 1440 px the scale stays at or above 0.75, the page never scrolls sideways, and wide blocks fit the legible width; phones open in reading mode with one section per block. Against the previous template the same test fails at 375 px with scale 0.196.
- `test_runtime_features.py`: a deep link restores view and selection, `file` becomes a `cursor://` link from `root`, the SVG export carries its styles, `p` plays two steps, English chrome; examples 13 to 16 render with no error at 375 and 1280 px and in reading mode.
- `test_text_budget.py`, `test_new_blocks.py`, `test_pipeline.py`: lint warnings and its false positives, validation of the new blocks, import extraction on a mixed Python/TS fixture, diff marks.

Lesson: full Chrome's new headless mode clamps the window to 500 px wide, so a "375 px" run silently measured 500 px. `chrome-headless-shell` (Playwright's cache) honours the size; the helper prefers it and the test prints a warning when the width differs. Also: `localStorage` set from a `file://` page does not survive into the run, so tests pick the mode through `?mode=` instead.

## Results, 2026-10-15, optional libraries

Added from the library survey: rough.js (`style: "sketch"`), highlight.js (`code` block), KaTeX (`math` block, inline `$...$` with `math: true`, MathML output), topojson-client plus world-atlas and Brazilian states (`map` block), dagre (`engine: "dagre"` on graphs). The template lists them pinned in `<script id="vt-libs">`; the build adds a script only for what the scene uses and embeds the map geometry, so a plain scene loads nothing new and `--self-contained` pages stay offline. Brazilian states come from `click_that_hood` at a pinned commit (3.3 MB) and are simplified once at build time (Douglas-Peucker, 0.01°) to 250 KB, cached in `.vt-libs/`.

`test_libs.py`: a plain scene gets no optional script; a scene with all five gets exactly those plus both geometries; offline, the page draws colored code tokens, a MathML formula, 27 states with 3 filled, the world, a dagre graph with its group, and hand-drawn shapes; the validator names a bad style, a highlight outside the snippet, a formula without TeX, an unknown geo, a point off the globe and an unknown engine.

Lesson: Douglas-Peucker on a closed ring starts from a zero-length chord (first point equals last), so every distance came out zero and each state collapsed to a triangle. The first split now measures distance to the start point.

## Results, 2026-10-15, visual audit with agents

`tests/audit_layout.py` builds every example, opens each view at 375 and 1280 px in headless Chrome and reports text that leaves its shape or overlaps other text (`--shots DIR` also saves one PNG per view). First run: 12 hits. Five agents then read the 108 screenshots in parallel and reported about 60 defects the measure cannot see: legend swatches all one color and covering their labels (a global `.sw` rule hit the SVG swatches), funnel labels on their values, cycle arcs stopping short and boxes off-screen, mind-map edges striking through leaf text, reverse arrows in `free` drawn on each other, gantt arrows turning back into bars, tornado labels cut, code lines past the box, chart annotations on lines and reference lines, titles under the floating bars, decision tables wider than a phone, a matrix header rule touching its text, a calendar month one column off, raw `$x$` in a formula caption, and body text at 7-9 px on phones. All fixed; a second round of three agents checked the new screenshots against the old and found four regressions from the fixes themselves (white treemap labels haloed, inspector swatches back to one color, diff swatches grey, phone scale clipping wide models), fixed in turn. The audit now reports zero, and `test_layout_audit.py` keeps the catalog and the free drawing at zero.

Lesson: the measured audit and the visual one catch different things. The measure finds text past a box; only the eye finds a swatch in the wrong color, an arrow pointing back, or a label that is technically inside its box but under a line.
