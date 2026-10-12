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

Reference pages for each: `examples/`. `02-comparacao-tecnologias.json` compares three databases, `05-fluxo-autenticacao.json` draws OAuth PKCE with evidence tags, `11-decisao-arquitetural.json` picks a message broker with a weighted matrix and a tornado, `12-analise-cenarios.json` runs a migration under three scenarios.

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
```

On success the first output line is the absolute path of the page. `--validate-only` checks without writing; `--fragment` skips the document tags for publish tools that add their own skeleton.

## Project layout

- `SKILL.md`, `strategy.md`: when to draw, the intent-to-block lookup, the deep strategies and anti-choices.
- `formats.md`: scene schema, every block's fields and what it shows at each information level, delivery per tool.
- `design.md`: the design system the templates enforce.
- `templates/canvas.html`, `svg.html`, `mermaid.html`: the three renderers. `canvas.html` is the default.
- `scripts/`: build, token sync, contrast check.
- `examples/`: twelve scenes, rebuilt by `sh scripts/build-examples.sh`.
- `tests/`: regression tests for the validator and every canvas feature.

## Limits

- Charts, trees and graphs load d3 and elkjs from CDNs; offline they show a one-line message instead. Everything else renders offline. A build with `--self-contained` inlines both libraries into the file, so it works fully offline.
- A graph view stays under 12 nodes plus groups; more than that belongs in an overview view plus one view per part.
- The agent never invents data: with no real numbers in reach, it draws the underlying structure and marks values unknown, or asks for them.
- The repo is private for now; the skill itself has no telemetry and no network calls beyond the two CDNs (none with `--self-contained`).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The short version: every scene change ships with a build, a test run and a contrast check.

## Docs

[SKILL.md](SKILL.md) · [strategy.md](strategy.md) · [formats.md](formats.md) · [design.md](design.md) · [examples.md](examples.md)
