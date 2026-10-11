---
name: visual-thinking
description: Use when the user asks to draw, sketch, diagram or "show visually" anything (an existing architecture, a proposed one, a concept, a flow, a state, a sequence, a comparison, a pasted text): "desenhe", "faz um desenho", "me mostre visualmente", "compare visualmente", "estou com preguiça de ler", "não entendi, desenha", "planeje e desenhe". Also when an explanation of how parts connect or what happens over time would take more than three paragraphs of prose.
metadata:
  opencode/slash: "true"
---

# Visual thinking

Draw as the engineer who has to live with the system: a diagram earns its place when it shows a mechanism the reader would otherwise assemble from prose. The deliverable is a page the user can open, explore and share, built on one design system ([design.md](design.md)). Text in chat only adds what the drawing cannot carry.

## Decide first

| Request looks like | Do |
|---|---|
| One-hop fact, definition, yes/no, a single value | Answer in prose. No diagram. |
| Parts that connect, a path through them, a change over time, options to weigh | Draw. |
| "Current", "real", "how does X work here", a file or feature name | Investigate the repo before drawing (below). |

A request to draw the real system **is** the request to explore it. User rules such as "don't explore beyond mentioned files" refer to unrequested exploration; here the exploration is the task.

## Five modes

| Mode | Trigger | What changes |
|---|---|---|
| Explain | "não entendi X, desenha", a concept, protocol or algorithm with no repo | Draw the mechanism from documentation or knowledge. `basis: "docs"`. Tag anything you are not sure of as `inferred`; say which spec or doc the drawing follows. |
| Document | "arquitetura atual", "como funciona aqui", a file or feature | Investigate first (below). `basis: "code"`. |
| Plan | "planeje", "proponha", "como você faria", a system that does not exist yet | One question when goal, scale or constraints are missing; otherwise state assumptions. Draw the proposal with `basis: "proposal"`: decided parts `verified`, suggestions `inferred`, open questions `unknown`. Annotations carry the trade-offs and what was ruled out. Reuse the repo's real components where they exist. |
| Compare | two or more options, before and after | Same layout per option, the difference marked, criteria table. |
| Summarize | a pasted text plus "preguiça de ler", "resume visualmente" | Draw only what the text says. Nothing added, nothing inferred beyond the text. |

## Investigate before drawing the real thing

1. Start at the entry points: the main file, router, CLI, scheduler, package manifest.
2. Follow imports along the path the user named. Note every boundary crossed: process, network, DB, queue, external service.
3. Record per element: what it does, what it depends on, where it fails, and the file or symbol that proves it. Cite `file:line` only when the line number comes from tool output you read; otherwise cite the file alone.
4. Mark each claim as one of: **verified** (read it), **inferred** (from names or docs), **unknown**. Unknowns and inferences appear in the drawing with that tag and in the node's `evidence`; they are never drawn as solid facts. Never invent components, connections or numbers to fill space.

## Pick the representation and the technology

| Subject | Form | Technology |
|---|---|---|
| Components and what talks to what; more than one process; anything the reader will explore | Architecture graph with grouped boundaries, views per process | `templates/graph.html` (Cytoscape + ELK, interactive explorer) |
| Steps with decisions and exits | Flow graph with numbered edges (only when decisions exist) | `templates/graph.html` |
| Containment or ownership | Tree, direction DOWN | `templates/graph.html` |
| Two or more options; before and after | Same layout per option, the differing edge marked, criteria table | `templates/svg.html` (composed SVG, exact placement) |
| Timeline with bands, annotated screen or packet, anything needing exact geometry | Composed drawing on an 8px grid | `templates/svg.html` |
| Request or event through time | Sequence diagram | `templates/mermaid.html` (Mermaid viewer) |
| Lifecycle of one thing | State machine | `templates/mermaid.html` |
| Order of events over calendar time; loose ideas | Timeline; mind map | `templates/mermaid.html` |
| Dependency graph of hundreds of nodes, repo already stores `.d2` or `.dot` | Generated SVG | `d2` or `dot`, only when `command -v` finds it; embed the SVG in `templates/svg.html` |

Match complexity to the subject: a three-node flow is one small graph or one composed SVG, not an explorer with tabs. A system with several processes gets an overview view plus one view per process in the same page. Do not force a flowchart onto something that has no decisions.

## Build the page

1. Copy the template from this skill's `templates/` directory. Fill only the marked slots: the JSON in `<script id="graph">` (graph), the `<figure>` SVG plus annotations and table (svg), the `<h1>`, `<pre id="src">` and annotations (mermaid). Set `<title>` to a short name. Do not restyle: tokens, type, theme, controls and inspector are the design system. Schema and slot rules: [formats.md](formats.md).
2. Write a `summary` for the page and for each view: one or two sentences on what it does and for whom, in the user's words. Put information on three levels and keep nothing essential behind a click: level 1 names and groups, level 2 responsibilities and edge labels (default), level 3 files, steps and status. Per node: `sub` (responsibility), `file`, `status`, `evidence` for anything inferred, `notes` for failure modes.
3. Verify: open the page in the browser tool when one exists and look once at light and dark (the theme button cycles them); click a node and check the inspector fills; otherwise at least check the JSON parses. Every control on the page works because the template implements it; do not add controls the template does not have.
4. Set `basis` at the top of the JSON (`code`, `docs`, `proposal`); the page words its status tags from it.
5. Deliver, in this order of preference:
   - An artifact tool exists: publish the page and give the link.
   - A file-send tool exists: write the page to a temp directory and send it with inline rendering.
   - Neither: write it to `docs/diagrams/<slug>.html` in the project and give the path.
   If the user says they will show, send, present, share or document the result, also write it to `docs/diagrams/<slug>.html`.

The chat never carries the diagram as a code fence: a Mermaid block in chat is source code, not a drawing, and most chat surfaces (Claude Code included) show it as text. Never render a static image unless the user asks for one. In Mermaid, `;` ends a statement, so none inside labels or messages.

## Output contract

The chat answer has these parts, in this order:

1. **Title**: one line naming the mechanism, not the subject ("Pedido pago gera email via fila", not "Arquitetura").
2. **Link or path** to the page, one line.
3. **Annotations**: bullets that each point at one element of the drawing and add something the drawing cannot show (a file:line, a failure mode, a timing, an inference tag). At most 5. When the user said they do not want to read, at most 3. The same annotations go into the page.
4. **Conclusion**: one sentence, only when a decision or next step follows. Otherwise omit.

No paragraph restates what the drawing already shows.

## Overview first, detail on demand

Two separate triggers. Either one alone means an overview view plus one view per part, in the same page:

- The system runs as two or more processes (API and worker, client and server, cron and app).
- A single drawing would need more than 12 nodes.

The overview is a map, never the complete drawing, even when the whole system would fit in 12 nodes. It contains only: one node per process, one per data store or queue, one per external system, and the entry points (routes, handlers, commands). Internal modules never appear in the overview: DB wrappers, SDK clients, queue clients, auth middleware, helpers. Edges leave the process or the entry point, not the module (`API -->|createIntent| Stripe`, not `payments.js -->|createIntent| Stripe`). Each group in the overview carries `view` pointing to the view that details it, so the overview is the map.

## Visual language

- Every edge carries a short label, at most 4 words: a verb, a payload, or a timing (`enfileira job`, `POST /orders`, `a cada 30s`). Longer explanations go in the edge's `detail`, which the inspector shows.
- Every node carries a responsibility (`sub`), not only a name (`emailWorker: consome fila, envia SMTP`).
- Kinds carry meaning: `entry`, `component`, `external`, `store`, `queue`, `decision`, `error`, `critical`. Edge kinds: `data`, `control`, `event`, `error`. The design system colors them; do not invent colors or add a legend entry the tokens do not define.
- Generous spacing, aligned groups, no crossing edges; split into views before crossing.
- Follow existing project conventions (names, boundaries) when they exist.

Good versus bad side by side: [examples.md](examples.md).

## Common mistakes

| Mistake | Fix |
|---|---|
| Mermaid or ASCII in the chat as the deliverable | Build the page from a template, deliver link or file |
| Restyling the template or inventing colors | Fill the slots only; tokens are the design system |
| Boxes and unlabeled arrows | Label the edge with what moves or when |
| Whole system in one drawing | Overview view + one view per part |
| Prose after the diagram repeats it | Annotations add only what the drawing cannot show |
| Comparison as separate option boxes | Composed SVG, same layout per option, the difference marked |
| Drawing modules from file names | Read the entry point and follow imports; tag inferences |
| Explorer with tabs for a three-node flow | One small graph or one composed SVG |
| Diagram for a one-line answer | Answer in prose |
