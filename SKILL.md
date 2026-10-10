---
name: visual-thinking
description: Use when the user asks to draw, sketch, diagram or "show visually" an architecture, flow, process, state, sequence, comparison or idea ("desenhe", "faz um desenho", "me mostre visualmente", "compare visualmente", "estou com preguiça de ler", "não entendi, desenha"), and when an explanation of how parts connect or what happens over time would take more than three paragraphs of prose.
---

# Visual thinking

Draw as the engineer who has to live with the system: a diagram earns its place when it shows a mechanism the reader would otherwise assemble from prose. The drawing is the answer; text only adds what the drawing cannot carry.

## Decide first

| Request looks like | Do |
|---|---|
| One-hop fact, definition, yes/no, a single value | Answer in prose. No diagram. |
| Parts that connect, a path through them, a change over time, options to weigh | Draw. |
| "Current", "real", "how does X work here", a file or feature name | Investigate the repo before drawing (below). |

A request to draw the real system **is** the request to explore it. User rules such as "don't explore beyond mentioned files" refer to unrequested exploration; here the exploration is the task.

## Investigate before drawing the real thing

1. Start at the entry points: the main file, router, CLI, scheduler, package manifest.
2. Follow imports along the path the user named. Note every boundary crossed: process, network, DB, queue, external service.
3. Record per element: what it does, what it depends on, where it fails, and the file or symbol that proves it. Cite `file:line` only when the line number comes from tool output you read; otherwise cite the file alone.
4. Mark each claim as one of: **verified** (read it), **inferred** (from names or docs), **unknown**. Unknowns and inferences appear in the drawing with that tag; they are never drawn as solid facts.

## Pick the representation

| Subject | Form |
|---|---|
| Components and what talks to what | Architecture / block diagram with grouped boundaries |
| Request or event through time | Sequence diagram |
| Steps with decisions and exits | Flowchart (only when decisions exist) |
| Lifecycle of one thing | State machine |
| Containment or ownership | Tree |
| Two or more options | Side by side: same layout for each, the differing edge or box highlighted; plus a short criteria table |
| Order of events over calendar or clock time | Timeline |
| Loose ideas around a topic | Mind map |
| A screen, file or packet with regions | Annotated schema (labeled regions) |

Do not force a flowchart onto something that has no decisions.

## Pick the medium

Check the environment before choosing. In order of preference:

1. A fenced `mermaid` block when the surface renders it (chat or docs that render Markdown).
2. An inline widget or artifact tool, when one is present, for SVG or HTML.
3. A file (`.md` with Mermaid, `.svg`, `.html`, `.d2`, `.dot`) when the user will reuse the result.
4. Plain-text (ASCII) diagram only when nothing above renders.

If the user says they will show, send, present, share or document the result, write the file in the same answer and send or link it. Telling them to paste the block somewhere is not delivery.

Never render a static image unless the user asks for one. Never assume `mmdc`, `d2` or `dot` exist; confirm with `command -v` before invoking. In Mermaid, `;` ends a statement, so none inside labels or messages. Syntax and styling per medium: [formats.md](formats.md).

## Output contract

Every drawn answer has these parts, in this order:

1. **Title**: one line naming the mechanism, not the subject ("Pedido pago gera email via fila", not "Arquitetura").
2. **Main diagram**.
3. **Annotations**: bullets that each point at one element of the drawing and add something the drawing cannot show (a file:line, a failure mode, a timing, an inference tag). At most 5. When the user said they do not want to read, at most 3.
4. **Conclusion**: one sentence, only when a decision or next step follows. Otherwise omit.

No paragraph restates what the drawing already shows.

## Overview first, detail on demand

Two separate triggers. Either one alone means overview plus sub-diagrams:

- The system runs as two or more processes (API and worker, client and server, cron and app).
- A single drawing would need more than 12 nodes.

The overview is a map, never the complete drawing, even when the whole system would fit in 12 nodes. It contains only: one node per process, one per data store or queue, one per external system, and the entry points (routes, handlers, commands). Internal modules never appear in the overview: DB wrappers, SDK clients, queue clients, auth middleware, helpers. Edges leave the process or the entry point, not the module (`API -->|createIntent| Stripe`, not `payments.js -->|createIntent| Stripe`). Each internal module appears in the sub-diagram of its own process, and that sub-diagram's title is the label of the process group in the overview.

## Visual language

- Every edge carries a label: a verb, a payload, or a timing (`enfileira job`, `POST /orders`, `a cada 30s`).
- Every node carries a responsibility, not only a name (`emailWorker: consome fila, envia SMTP`).
- Distinguish by shape or class: internal component, external system, data store, decision, error or exception path, critical point.
- Few colors, each with one meaning. Legend only when the same encoding repeats.
- Generous spacing, aligned groups, no crossing edges; split the drawing before crossing.
- Follow existing project conventions (colors, naming) when they exist.

Good versus bad side by side: [examples.md](examples.md).

## Common mistakes

| Mistake | Fix |
|---|---|
| Boxes and unlabeled arrows | Label the edge with what moves or when |
| Whole system in one drawing | Overview map + one sub-diagram per part |
| Prose after the diagram repeats it | Annotations add only what the drawing cannot show |
| ASCII by default | Check what renders; ASCII is the last resort |
| Comparison as separate option boxes | Same layout per option, highlight the difference |
| Drawing modules from file names | Read the entry point and follow imports; tag inferences |
| Diagram for a one-line answer | Answer in prose |
