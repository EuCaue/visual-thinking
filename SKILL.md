---
name: visual-thinking
description: Use when the user asks to draw, sketch, diagram, chart or "show visually" anything (an architecture, a concept, a comparison, a trend, numbers, a timeline, a process, ideas to organize, a pasted text): "desenhe", "faz um desenho", "me mostre visualmente", "compare visualmente", "mostre a evolução", "organize essas ideias", "estou com preguiça de ler", "não entendi, desenha", "planeje e desenhe". Also when an explanation of how parts connect, how values compare or what happens over time would take more than three paragraphs of prose.
metadata:
  opencode/slash: "true"
---

# Visual thinking

Draw as the engineer who has to live with the system: a picture earns its place when it shows something the reader would otherwise assemble from prose. The representation comes from the information, never from a favorite template. The deliverable is a page the user can open, explore and share, built on one design system ([design.md](design.md)). Text in chat only adds what the drawing cannot carry.

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
| Explain | "não entendi X", a concept, protocol or algorithm, no repo | Draw the mechanism from documentation or knowledge. `basis: "docs"`. Tag what you are not sure of as `inferred`; name the spec or doc. |
| Document | "arquitetura atual", "como funciona aqui", a file or feature | Investigate first. `basis: "code"`. |
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
| `templates/canvas.html` | The default. A scene of composable blocks: chart (line, area, bar, stacked bar, scatter, dot, histogram, donut), kpi, matrix, cards, timeline, steps, tree, mindmap, quadrant, spectrum, cycle, funnel, venn, callout, text, free canvas, graph. Views as tabs. |
| `templates/graph.html` | A system explorer when the whole deliverable is one architecture with several process views and a deep inspector. |
| `templates/svg.html` | Hand-composed drawings with exact placement: two architectures side by side, annotated screens, packet layouts. |
| `templates/mermaid.html` | Sequence diagrams, state machines, Gantt-like timelines. |

Schemas, slots and rules: [formats.md](formats.md). Design rules the templates enforce: [design.md](design.md). Reference renders: `examples/showcase.json` (eight prompts, eight pictures; build with `python3 scripts/build-scene.py`).

## Build the page

1. Copy the template. Fill only the marked slots (the scene JSON, the figure, or the Mermaid source) and the `<title>`. Do not restyle: tokens, type, theme, controls and inspector are the design system.
2. Write a `summary` for the page and for each view: one or two sentences on what it shows and for whom. Every block has a `title` that says what the reader will learn, not the chart type. Edge labels at most 4 words; longer explanations go in `detail`. Groups hold at least one node.
3. Keep nothing essential behind a click: the default view answers the question. Interaction adds depth (inspector, tooltips, filters, levels), never the core.
4. Verify: open the page in the browser tool when one exists and look once at light and dark; click one element and check the inspector; check that the JSON parses. Then the visual check: do the blocks look different from each other and right for the data, with no overlap, no clipped text, no crossing edges?
5. Deliver, in this order: an artifact tool (publish, give the link); a file-send tool (write to a temp directory, send with inline rendering); otherwise `docs/diagrams/<slug>.html` in the project and the path. If the user says they will show, send, present or document the result, also write it to `docs/diagrams/`.

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
| Restyling the template or inventing colors | Fill the slots only |
| Unlabeled edges, nodes without responsibility | Label what moves; give every node a `sub` |
| Whole system in one drawing | Overview view plus one view per part |
| Prose after the drawing repeats it | Annotations add only what the drawing cannot show |
| Data invented to fill a chart | Ask for the numbers or leave the block out |
| Asking before trying | Draw with a stated assumption unless two readings differ materially |
| Drawing for a one-line answer | Answer in prose |
