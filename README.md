# visual-thinking

An agent skill that turns explanations, architectures, decisions and data into standalone, explorable HTML pages. The agent reads what you need to see, writes a JSON scene, and the template renders it as a page you can open, click through and share. No build step, no framework, no account.

## Why

Architecture, trade-offs and trends live badly in prose. You read three paragraphs to reconstruct one picture, and the writer has to keep every reader's mental image in sync. ASCII art in chat makes it worse: it doesn't survive a phone, and nobody can click it.

This skill draws the picture instead, and draws it in a form that carries the load: labeled edges, units on axes, evidence tags on claims that came from reading, a right panel that answers "where did this number come from?" on click. When there is nothing worth drawing ("what's the difference between these two numbers?"), the skill answers in prose and skips the page.

## How it works

1. The agent classifies what the reader needs (compare, weigh a decision, follow a flow, see a trend) and picks a block for it.
2. It writes a scene: a JSON file with a title, a summary, one or more views, and blocks. Nothing is styled by hand; colors, type and layout come from the design system.
3. `scripts/build-scene.py` validates the scene (dangling ids, unlabeled edges, out-of-range values) and emits one standalone HTML file.

The full contract the agent follows lives in [SKILL.md](SKILL.md).

## What it can draw

| The reader needs to | Block |
|---|---|
| compare options on shared attributes | `matrix` |
| weigh options with weights, vetoes and sensitivity | `decision` |
| see what flips a decision | `chart` kind `tornado` |
| see consequences of a choice | `graph` with decision nodes and consequence paths |
| test alternative futures | view-level `scenarios` controls |
| see change over time | `chart` line or area |
| follow an architecture, flow or dependency | `graph` |
| follow steps or a protocol | `steps`, or `mermaid.html` for sequence and state |
| see hierarchy or organize ideas | `tree`, or `tree` with `layout: "mindmap"` |
| situate items on criteria | `quadrant`, `spectrum` |
| see events, conversion, proportions, numbers | `timeline`, `funnel`, `donut` and other `chart` kinds, `kpi` |
| show an image or video | `free` with `image`/`video` elements |
| read a data model (tables, fields, keys) | `entity` |
| follow amounts between stages, or parts that nest | `sankey`, `treemap` |
| see a value per day or per pair of categories | `heatmap` |
| plan tasks with dates and dependencies | `gantt` |
| see what changed between two versions | `scripts/scene-diff.py`, marks on `graph` and `entity` |
| see values on a map (countries, Brazilian states) | `map` |
| read code or a formula | `code`, `math` |

Reference pages for each: `examples/`. `02-comparacao-tecnologias.json` compares three databases, `05-fluxo-autenticacao.json` draws OAuth PKCE with evidence tags, `11-decisao-arquitetural.json` picks a message broker with a weighted matrix and a tornado, `12-analise-cenarios.json` runs a migration under three scenarios, `13-modelo-de-dados.json` draws an HR data model, `14-cronograma.json` a migration plan, `15-fluxo-orcamento.json` a budget as sankey and treemap, `16-mapa-de-calor.json` support load by hour and by day.

Every page reads on a phone: the canvas never shrinks text below a legible scale and blocks reflow to fit, phones open in a reading mode that lays the same scene out as text (also the screen-reader description), and `?mode=draw` or `?mode=read` picks one in a link. Selecting an element puts it in the address (`#v=…&b=…&k=…`), so a link opens on it. The right-click menu exports PNG or SVG and copies element links; `p` plays a sequence step by step; `file` fields open in the editor when the scene sets `root`; `"lang": "en"` switches the interface to English; `"style": "sketch"` draws it by hand. Optional libraries (rough.js, highlight.js, KaTeX, topojson, dagre) are added only to pages that use them.

## Install

```bash
npx skills add EuCaue/visual-thinking
```

Or point the agent's skills directory at this folder:

```bash
ln -sfn "$PWD" ~/.agents/skills/visual-thinking
```

## Use

Write a scene JSON (start from an `examples/*.json` file), build it, open the page:

```bash
python3 scripts/build-scene.py my-scene.json my-page.html
python3 scripts/build-scene.py my-scene.json my-page.html --self-contained   # inlina d3 e elkjs: a página funciona offline
```

On success the first output line is the absolute path of the page. `--validate-only` checks without writing; `--fragment` skips the document tags for publish tools that add their own skeleton. The build also warns when the scene carries more text than the drawing needs (`texto:` lines; `--no-text-lint` silences them).

Two helpers write scenes for you:

```bash
python3 scripts/extract-deps.py ~/code/my-repo draft.json        # graph draft from real imports (Python, JS/TS, Go)
python3 scripts/scene-diff.py before.json after.json diff.json   # one scene with added, changed and removed marked
```

## Project layout

- `SKILL.md`, `strategy.md`: when to draw, the intent-to-block lookup, the deep strategies and anti-choices.
- `formats.md`: scene schema, every block's fields and what it shows at each information level, delivery per tool.
- `design.md`: the design system the templates enforce.
- `templates/canvas.html`, `svg.html`, `mermaid.html`: the three renderers. `canvas.html` is the default.
- `scripts/`: build, import extractor, scene diff, token sync, contrast check.
- `examples/`: twenty scenes (`18-catalogo` has one of every block, `19` the sketch style in English, `20` a diff), rebuilt by `sh scripts/build-examples.sh`.
- `tests/`: regression tests for the validator and every canvas feature; the `test_responsive` and `test_runtime_features` files measure pages in headless Chrome (prefers Playwright's `chrome-headless-shell`, since full Chrome's headless mode will not go below 500px wide; `VT_CHROME` overrides).

## Limits

- Charts, trees, graphs and flows load d3, elkjs and d3-sankey from CDNs, plus the optional libraries a page uses; offline they show a one-line message instead. Everything else renders offline. A build with `--self-contained` inlines the libraries into the file, so it works fully offline.
- A graph view stays under 12 nodes plus groups; more than that belongs in an overview view plus one view per part.
- The agent never invents data: with no real numbers in reach, it draws the underlying structure and marks values unknown, or asks for them.
- The repo is private for now; the skill itself has no telemetry and no network calls beyond the CDNs (none with `--self-contained`).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The short version: every scene change ships with a build, a test run and a contrast check.

## Docs

[SKILL.md](SKILL.md) · [strategy.md](strategy.md) · [formats.md](formats.md) · [design.md](design.md) · [examples.md](examples.md)
