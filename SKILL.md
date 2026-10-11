---
name: visual-thinking
description: Use when the user asks to draw, sketch, diagram, chart or "show visually" anything (an architecture, a concept, a comparison, a trend, numbers, a timeline, a process, ideas to organize, a pasted text): "desenhe", "faz um desenho", "me mostre visualmente", "compare visualmente", "mostre a evolução", "organize essas ideias", "estou com preguiça de ler", "não entendi, desenha", "planeje e desenhe". Also when an explanation of how parts connect, how values compare or what happens over time would take more than three paragraphs of prose.
metadata:
  opencode/slash: "true"
---

# Visual thinking

Draw as the engineer who has to live with the system: a picture earns its place when it shows something the reader would otherwise assemble from prose. The representation comes from the information, never from a favorite template. The deliverable is a standalone HTML page the user can open, explore and share, built on one design system ([design.md](design.md)). Text in chat only adds what the drawing cannot carry.

The skill is a contract between any agent and a renderer: agent reads intent, writes a scene (JSON), the template renders it. Nothing here depends on a particular agent, harness or publishing tool.

## Decide first

| Request looks like | Do |
|---|---|
| One-hop fact, definition, yes/no, two numbers | Answer in prose. No drawing. |
| Options to weigh, values that change, parts that connect, steps in order, ideas to organize | Draw. |
| "Current", "real", "how does X work here", a file or feature name | Investigate the repo before drawing (below). |

A request to draw the real system **is** the request to explore it. User rules such as "don't explore beyond mentioned files" refer to unrequested exploration; here the exploration is the task.

## Choose the representation: intent, structure, strategy

Run [strategy.md](strategy.md) before touching a template:

1. **Intent**: what the user needs to see. Compare, trend, proportion, magnitude, distribution, relationship, sequence, hierarchy, position, cause and effect, lifecycle, spatial exploration, change.
2. **Information structure**: what the data is. Entities with attributes, ordered observations, part-to-whole, samples, pairs of measures, nodes and edges, steps, tree, states, events, options with arguments, loose concepts.
3. **Visual strategy**: the row in strategy.md that matches intent and structure. It names the blocks, the marks and the composition. Several blocks can compose one page when the question has more than one part; the answer goes in the first block.

Five prompts with five intents must produce five different pictures. If the result is boxes and arrows for a comparison, or a matrix for a trend, the strategy step was skipped.

**Ask only when it changes the drawing.** Draw first when one strategy is clearly right; state the assumption in the subtitle. Ask one sentence when two readings lead to materially different pictures and the context does not settle it (compare on what? which numbers? which components?). Never invent data, components or metrics to fill a block.

## Five modes

| Mode | Trigger | What changes |
|---|---|---|
| Explain | "não entendi X", a concept, protocol or algorithm, no repo | Draw the mechanism from documentation or knowledge. `basis: "docs"`. Tag what you are not sure of as `inferred`; name the spec or doc in `source`. |
| Document | "arquitetura atual", "como funciona aqui", a file or feature | Investigate first. `basis: "code"`, `source` names the directories read, `date` the day. |
| Plan | "planeje", "proponha", "como você faria" | One question when goal, scale or constraints are missing; otherwise state assumptions. `basis: "proposal"`: decided `verified`, suggestions `inferred`, open questions `unknown`. Trade-offs in annotations. Reuse real components where they exist. |
| Compare | two or more options, before and after | Comparison strategies in strategy.md: matrix, aligned cards, side by side with the difference marked, bars for metrics. Never a wall of cards, never boxes and arrows. |
| Summarize | a pasted text plus "preguiça de ler", "resume visualmente" | Draw only what the text says. Nothing added, nothing inferred beyond the text. |

## Investigate before drawing the real thing

1. Start at the entry points: the main file, router, CLI, scheduler, package manifest.
2. Follow imports along the path the user named. Note every boundary crossed: process, network, DB, queue, external service.
3. Record per element: what it does, what it depends on, where it fails, and the file or symbol that proves it. Cite `file:line` only when the line number comes from tool output you read; otherwise cite the file alone.
4. Mark each claim **verified** (read it), **inferred** (from names or docs) or **unknown**. Unknowns and inferences carry that tag and an `evidence` line; they are never drawn as solid facts.

## Templates

| Template | Use for |
|---|---|
| `templates/canvas.html` | The default, for everything. A scene of composable blocks: chart (line, area, bar, stacked bar, scatter, dot, histogram, donut), kpi, matrix, cards, timeline, steps, tree, mindmap, quadrant, spectrum, cycle, funnel, venn, callout, text, free canvas, graph (architecture with groups, typed edges, three information levels, legend as filter). Views as tabs; one inspector per block. |
| `templates/svg.html` | Hand-composed drawings with exact placement: two architectures side by side, annotated screens, packet layouts, an SVG from `d2` or `dot`. |
| `templates/mermaid.html` | Sequence diagrams and state machines. |

Schemas, slots and what each block shows at each level: [formats.md](formats.md). Design rules the templates enforce: [design.md](design.md). Reference pages: `examples/*.json`, ten prompts, ten different pictures (`sh scripts/build-examples.sh`).

## Build the page

1. Write the scene JSON. Fill only the schema: `title` (the finding), `subtitle`, `basis`, `source`, `date`, `summary`, views, blocks. Do not restyle: tokens, type, theme, controls and inspector are the design system.
2. Fill the three levels. Level 1 is the drawing: every block has a `title` that says what the reader learns, axes carry a label or `unit`, edges carry a label of at most 4 words, nodes carry `sub`. Level 2 and 3 are the fields the inspector reads: `note`, `detail`, `evidence`, `notes`, `text`, `source`. Write a `summary` for the page and for each view: one or two sentences on what it shows and for whom. Groups hold at least one node.
3. Keep nothing essential behind a click: the default view answers the question. Interaction adds depth, never the core.
4. Build: `python3 scripts/build-scene.py scene.json out.html "Title"` (standalone document). Without Python, copy the template and replace the JSON in `<script id="scene">` and the `<title>`.
5. Verify when a browser tool exists: open the page, look once at light and dark, click one element and read the inspector, check the legend names every color and line style on screen, and that no console error appears. Then the reading test: would someone who never saw the prompt understand what is compared, measured or connected, and in what unit?
6. Deliver with whatever the harness offers, in this order: a publish tool (use `--fragment` when the tool wraps pages in its own document; give the link); a file-send tool with inline rendering; otherwise `docs/diagrams/<slug>.html` in the project and the path. If the user says they will show, send, present or document the result, also write it to `docs/diagrams/`.

The chat never carries a diagram as a code fence. Never render a static image unless asked. In Mermaid, `;` ends a statement.

## Output contract

The chat answer has, in this order: a **title** naming the finding ("Svelte troca runtime por build", not "Comparação"); the **link or path**; up to five **annotations** that add what the drawing cannot show (a file:line, a failure mode, a source, an inference tag), at most three when the user said they do not want to read; one sentence of **conclusion** only when a decision follows. No paragraph restates the drawing.

## Overview first, detail on demand

Two separate triggers; either one means an overview view plus one view per part, in the same page: the system runs as two or more processes, or a single drawing would need more than 12 nodes. The overview holds only processes, stores, externals and entry points; internal modules live in their process view; edges leave the process or the entry point. Each group carries `view` pointing to its detail.

## Common mistakes

| Mistake | Fix |
|---|---|
| Every request becomes nodes and edges | Run strategy.md; a comparison is a matrix or aligned cards, a trend is a line, a magnitude is bars |
| Chart chosen by habit (pie for everything, radar for comparisons) | Anti-choices in strategy.md |
| Restyling the template or inventing colors | Fill the schema only |
| Unlabeled edges, nodes without responsibility, axes without unit | Label what moves; give every node a `sub`; give `y.unit` or a label |
| Whole system in one drawing | Overview view plus one view per part |
| Prose after the drawing repeats it | Annotations add only what the drawing cannot show |
| Data invented to fill a chart | Ask for the numbers or leave the block out |
| Asking before trying | Draw with a stated assumption unless two readings differ materially |
| Drawing for a one-line answer | Answer in prose |
