---
name: visual-thinking
description: >-
  Use when the user asks to draw, sketch, diagram, chart or show visually
  anything (an architecture, a concept, a comparison, a trend, numbers, a
  timeline, a process, ideas to organize, a pasted text). Also when an
  explanation of how parts connect, how values compare or what happens over
  time would take more than three paragraphs of prose.
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

## Choose the representation: intent, blocks

Fast lookup, then draw. The default template is `canvas.html`.

| The reader needs to | Block |
|---|---|
| compare options on shared attributes | `matrix` (pros and cons per option → `cards`) |
| weigh options with scores and weights | `decision` (weighted matrix with sliders, vetoes, sensitivity note) |
| see what flips the answer | `chart` kind `tornado` (sensitivity, sorted by swing) |
| see consequences of a choice | `graph` with `kind: "decision"` nodes, `consequence` order/polarity, `prob` on edges (click isolates the path) |
| compare futures under different hypotheses | view-level `scenarios` controls (chips swap override data without reload) |
| see change over time | `chart` line or area |
| see parts of a whole | `chart` donut up to 5 parts, else sorted bars |
| see which is bigger, a ranking | sorted bars |
| see how things connect: architecture, flow with decisions, dependencies | `graph` |
| follow a sequence without branches | `steps` |
| follow a protocol message by message | `mermaid.html`, sequence diagram |
| see hierarchy or containment | `tree` |
| organize loose ideas | `tree` with `layout: "mindmap"` |
| see before and after | `row` of two cards or two `graph` blocks, difference marked |
| see states of one thing | `mermaid.html`, state diagram |
| situate on two criteria | `quadrant` |
| situate on one spectrum | `spectrum` |
| see events in time | `timeline` |
| see conversion through stages | `funnel` |
| see the numbers at a glance | `kpi` |
| show a photo, screenshot, diagram image or video | `free` with `image`/`video` elements (`src` a link or page-relative path) |
| none of them fit | `free` |

Borderline choices, compositions of several blocks, the anti-choices and the "when to ask" list: [strategy.md](strategy.md). Different prompts with different intents must produce different pictures; boxes and arrows for a comparison or a matrix for a trend means the lookup was skipped.

**Assumption beats question.** Draw what the context settles, and carry every guess openly: state it in the subtitle or tag it `inferred` / `unknown` in the scene. Ask one short sentence only in two cases: two readings lead to materially different pictures, or a data-driven chart has no real numbers in reach (never invent an axis, a series or a metric; draw the underlying structure instead — matrix, steps, graph — with the values marked `unknown`, or ask for the numbers).

## Seven modes

| Mode | Trigger | What changes |
|---|---|---|
| Sketch | casual, quick ask: "faz um esquema", "desenha aí", an idea to lay out | The whole flow shrinks: SKILL.md alone, the fast lookup, strategy.md only if the choice is borderline. One view, 1–2 blocks, the first one answers. Assumptions go in the subtitle, nothing asked back. One build; the browser pass is a single look if a tool exists. Chat: title, absolute path, one line. |
| Explain | "não entendi X", a concept, protocol or algorithm, no repo | Draw the mechanism from documentation or knowledge. `basis: "docs"`. Tag what you are not sure of as `inferred`; name the spec or doc in `source`. |
| Document | "arquitetura atual", "como funciona aqui", a file or feature | Investigate first. `basis: "code"`, `source` names the directories read, `date` the day. |
| Plan | "planeje", "proponha", "como você faria" | One question when goal, scale or constraints are missing; otherwise state assumptions. `basis: "proposal"`: decided `verified`, suggestions `inferred`, open questions `unknown`. Trade-offs in annotations. Reuse real components where they exist. |
| Compare | two or more options, before and after | Comparison strategies in strategy.md: matrix, aligned cards, side by side with the difference marked, bars for metrics. Never a wall of cards, never boxes and arrows. |
| Summarize | a pasted text plus "preguiça de ler", "resume visualmente" | Draw only what the text says. Nothing added, nothing inferred beyond the text. |
| Decide | "qual escolher", "vale a pena", trade-off, buy vs build, risk, scenarios | `basis: "decision"`. `decision` block with weights and a stated `weightBasis` (never equal weights by default), `tornado` for what flips the answer, `graph` with consequence paths, `scenarios` for alternative futures. The title names the recommendation; the reader must trace it to criteria. |

## Investigate before drawing the real thing

1. Start at the entry points: the main file, router, CLI, scheduler, package manifest.
2. Follow imports along the path the user named. Note every boundary crossed: process, network, DB, queue, external service.
3. Record per element: what it does, what it depends on, where it fails, and the file or symbol that proves it. Cite `file:line` only when the line number comes from tool output you read; otherwise cite the file alone.
4. Mark each claim **verified** (read it), **inferred** (from names or docs) or **unknown**. Unknowns and inferences carry that tag and an `evidence` line; they are never drawn as solid facts.

## Templates

| Template | Use for |
|---|---|
| `templates/canvas.html` | The default, for everything. A scene of composable blocks: chart (line, area, bar, stacked bar, scatter, dot, histogram, donut, tornado), kpi, matrix, decision, cards, timeline, steps, tree, mindmap, quadrant, spectrum, cycle, funnel, venn, callout, text, free canvas (with image and video elements), graph (architecture with groups, typed edges, three information levels, legend as filter; decision nodes with consequence paths). Views as tabs, with optional `scenarios` controls; one inspector per block; right-click menu with per-target actions. |
| `templates/svg.html` | Hand-composed drawings with exact placement: two architectures side by side, annotated screens, packet layouts, an SVG from `d2` or `dot`. |
| `templates/mermaid.html` | Sequence diagrams and state machines. |

Schemas, slots and what each block shows at each level: [formats.md](formats.md). Design rules the templates enforce: [design.md](design.md). Reference pages: `examples/*.json`, ten prompts, ten different pictures (`sh scripts/build-examples.sh`).

## Build the page

1. Write the scene JSON. Fill only the schema: `title` (the finding), `subtitle`, `basis`, `source`, `date`, `summary`, views, blocks. Do not restyle: tokens, type, theme, controls and inspector are the design system.
2. Fill the three levels. Level 1 is the drawing: every block has a `title` that says what the reader learns, axes carry a label or `unit`, edges carry a label of at most 4 words, nodes carry `sub`. Level 2 and 3 are the fields the inspector reads: `note`, `detail`, `evidence`, `notes`, `text`, `source`. Write a `summary` for the page and for each view: one or two sentences on what it shows and for whom. Groups hold at least one node. In sketch mode this shrinks to the minimum: page `title`, block titles and content; `summary`, `source`, `date` and level-3 fields stay out — the build warns about them, it does not block.
3. Keep nothing essential behind a click: the default view answers the question. Interaction adds depth, never the core.
4. Build: `python3 scripts/build-scene.py scene.json out.html "Title"` (standalone document). The build validates the scene first: dangling ids, unlabeled edges, unknown kinds, empty groups, out-of-range values; exit 1 lists each problem with the block it belongs to, and nothing is built until they are fixed. On success the first output line is the absolute path of the page. `--self-contained` inlines the two libraries so the page works fully offline (build fetches them once; without network it keeps the CDN tags and warns). Without Python, copy the template and replace the JSON in `<script id="scene">` and the `<title>`.
5. Verify when a browser tool exists: open the page, look once at light and dark, click one element and read the inspector, check the legend names every color and line style on screen, and that no console error appears. Then two readings: the reader test (would someone who never saw the prompt understand what is compared, measured or connected, and in what unit?) and the sense test — walk the scene element by element and fix or delete anything you cannot state the reason for: an element nobody asked about, a series without a source, an edge whose meaning you cannot name. A drawing with dead elements is as broken as one that does not render.
6. Deliver with whatever the harness offers, in this order: a publish tool (use `--fragment` when the tool wraps pages in its own document; give the link); a file-send tool with inline rendering; otherwise `docs/diagrams/<slug>.html` in the project. Always give the **full absolute path** (`/home/.../docs/diagrams/<slug>.html`), never a relative or shortened one; the build already prints it. If the user says they will show, send, present or document the result, also write it to `docs/diagrams/`.

The chat never carries a diagram as a code fence. Never render a static image unless asked. In Mermaid, `;` ends a statement.

## Move elements without breaking anything

The scene is data; the page is computed from it. Elements have no fixed coordinates except inside `free`, so moving, reordering and regrouping are safe as long as ids stay consistent.

Safe to do freely, no rebuild concern beyond rerunning the build:

- Reorder blocks inside a view, reorder views, change `layout` (`stack`/`row`/`grid`, `gap`, `columns`), move a block to another view.
- Edit any text: titles, `sub`, edge labels, `note`, `detail`, `caption`, annotations.
- Add or remove anything nothing references: a block, a series, a tree leaf, a `free` rect or text, a callout.
- Regroup: move a graph node to another group, or a `free` element to new `x`/`y` on the 8px grid; arrows follow by id.

Load-bearing ids; change each only together with every reference, in the same edit:

| Id | Referenced by |
|---|---|
| graph node `id` | `edges.from` / `edges.to` in the same view |
| graph group `id` | `node.group` |
| view `id` | `group.view`, `node.view` |
| `free` element `id` | `arrow.from`/`to`, `line.from`/`to` |

Delete a graph node only after deleting its edges; empty a group before deleting it. Never edit tokens, CSS, the runtime or the built HTML: edit the scene and rebuild. The build validates and points at dangling references; a page that renders with a missing node, an unlabeled line or a silent dropped group means someone bypassed it.

## Output contract

The chat answer has, in this order: a **title** naming the finding ("Svelte troca runtime por build", not "Comparação"); the **link or the full absolute path** of the page (absolute, so it opens from any interface; never a relative or abbreviated path); **annotations** that add what the drawing cannot show (a file:line, a failure mode, a source, an inference tag) — **one by default**; take two or three when the material demands it and up to five in Document mode; one sentence of **conclusion** only when a decision follows. No paragraph restates the drawing.

## Overview first, detail on demand

Two separate triggers; either one means an overview view plus one view per part, in the same page: the system runs as two or more processes, or a single drawing would need more than 12 nodes. The overview holds only processes, stores, externals and entry points; internal modules live in their process view; edges leave the process or the entry point. Each group carries `view` pointing to its detail.

## Decision test

For any Decide page, before delivering: can the reader trace the recommendation to the criteria (which weights, which scores, which veto)? Is every weight stated in `weightBasis`, every veto drawn as a veto, the leader highlighted at rest, and the one criterion that could flip the answer named? If not, the page is a verdict without a trial — fix it.

## Common mistakes

| Mistake | Fix |
|---|---|
| Every request becomes nodes and edges | Run strategy.md; a comparison is a matrix or aligned cards, a trend is a line, a magnitude is bars |
| Chart chosen by habit (pie for everything, radar for comparisons) | Anti-choices in strategy.md |
| Restyling the template or inventing colors | Fill the schema only |
| Unlabeled edges, nodes without responsibility, axes without unit | Label what moves; give every node a `sub`; give `y.unit` or a label |
| Whole system in one drawing | Overview view plus one view per part |
| Prose after the drawing repeats it | Annotations add only what the drawing cannot show |
| Data invented to fill a chart | The numbers must be real; with none in reach, draw the underlying structure with values marked `unknown` or ask for the numbers |
| Asking before trying | Draw with a stated assumption unless two readings differ materially |
| Drawing for a one-line answer | Answer in prose |
| Hand-edited scene renders broken | Run the build; fix every dangling id it points at, rebuild |
| Element the reader cannot make sense of | Fix or delete it before delivering; the sense test in "Build the page" |
| Decision matrix with equal or missing weights | State every weight in `weightBasis`; infer from context when the user did not give them, never default to equal |
| Pros/cons that hide the trade-off | Write paired trade-offs ("buys X at the cost of Y"), not isolated lists |
| Mandatory requirement drawn as one more criterion | Model eliminatory constraints as `vetoBelow`; a vetoed option is disqualified, not outscored |
| Recommendation the reader cannot trace | Decision test above: weights, scores, vetoes and the flip criterion all visible |
