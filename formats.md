# Formats and templates

The deliverable is a page built from `templates/`. All four templates share one design system (`templates/_tokens.css`, explained in [design.md](design.md)): IBM Plex Sans and Mono, semantic color tokens, light and dark themes with a persisted toggle, one radius scale, focus states, reduced motion. Fill the slots; never restyle.

## Delivery

| Tool present | Do |
|---|---|
| Artifact or similar publish tool | Publish the page (title: short name; icon: `diagram`). Give the link. |
| File-send tool that renders HTML inline | Write the page to a temp directory, send it with inline rendering. |
| Browser tool | Open the page once; check light and dark with the theme button; click a node. |
| None of the above | Write to `docs/diagrams/<slug>.html` in the project and give the path. |

The templates are HTML fragments (no `doctype`, `html`, `head`, `body` tags) so the artifact skeleton can wrap them; browsers open them directly as files too. Scripts and fonts load from cdnjs, jsdelivr and Google Fonts with pinned versions, which the artifact CSP allows.

## templates/canvas.html: composable canvas (default)

A scene is one or more views; a view is a layout of blocks. The runtime measures text, lays out, draws in SVG, animates, and gives every page the same controls: views as a segmented control, search, zoom and fit, theme toggle, inspector with the view summary and the selected element, tooltips on data marks, scrub on line charts, legend that toggles series, level of detail on zoom, keyboard (`f`, `+`, `-`, `/`, arrows, `Esc`).

```json
{
  "title": "Svelte troca runtime por build", "subtitle": "Comparação · fontes nos rodapés", "basis": "docs",
  "summary": "Uma ou duas frases sobre o que a página mostra e para quem.",
  "views": [
    { "id": "main", "title": "Comparar", "summary": "O que esta vista responde.",
      "layout": { "type": "stack", "gap": 40 },
      "blocks": [ { "type": "matrix", "id": "m", "title": "React, Vue e Svelte", "columns": [], "rows": [] } ],
      "annotations": [ "Texto que o desenho não carrega." ] }
  ]
}
```

`layout.type`: `stack` (one below the other, narrative order), `row` (side by side, for things to compare), `grid` with `columns`. Every block has `type`, `id`, `title` (what the reader learns), optional `caption` (source, scope) and `width`.

| Block | Fields | Notes |
|---|---|---|
| `chart` | `kind`: `line`, `area`, `bar`, `stackedBar`, `scatter`, `dot`, `histogram`, `donut`; `series: [{name, data: [[x, y], ...]}]` (`values: [...]` for histogram; `data: [[label, value]]` for donut; `[[x, y, label]]` for scatter); `x: {type: category|number|time, label}`; `y: {label, min, max}`; `marks`: subset of `line`, `point`, `area`, `bar`, `label`; `refLines: [{y or x, label}]`; `annotations: [{x, y, text, side}]`; `height`; `legend` | Bars start at zero. Up to 6 series. Legend toggles series. Line and area get a scrub tooltip. |
| `kpi` | `items: [{label, value, unit, delta, deltaKind: ok|danger|neutral, spark: [..]}]` | Numbers first, no tiles. |
| `matrix` | `columns: [{label, sub}]`, `rows: [{label, cells: [...], best: max|min, unit, bars}]`; a cell is a string, number, boolean or `{value, note, unit}` | Numbers get an inline bar scaled to the row max; `best` marks the winner; `note` shows on hover. |
| `cards` | `items: [{title, meta, points: [{kind: pro|con|neutral, text}]}]`, `cardWidth` | Pros and cons, before and after. Same criteria order in every card. |
| `timeline` | `events: [{date, title, text, kind: milestone}]`, `periods: [{from, to, label}]`, `orientation` | Horizontal up to 7 events, vertical beyond. |
| `steps` | `items: [{title, text, kind}]`, `stepWidth` | Linear pipeline. Decisions belong in `graph`. |
| `tree` | `root: {label, text, kind, children: [...]}`, `direction: DOWN|RIGHT`, `layout: tree|mindmap` | `mindmap` is radial with the topic in the center. |
| `quadrant` | `x: {label, low, high}`, `y: {label, low, high}`, `quadrants: [4 labels]`, `items: [{label, x, y}]` with x and y in 0..1 | Position on two criteria. |
| `spectrum` | `min`, `max` (labels), `items: [{label, value 0..1}]` | Position on one criterion. |
| `cycle` | `items: [{label, text}]` | Repeating stages. |
| `funnel` | `items: [{label, value}]`, `shape: funnel|pyramid`, `unit` | Shows the conversion per stage. |
| `venn` | `sets: [{label, items}]` (2 or 3), `overlaps: [{sets: [0, 1], label, items}]` | |
| `callout` | `kind: note|warn|danger|ok`, `label`, `text` | The one sentence the reader must not miss. |
| `text` | `text`, `width` | A paragraph when the drawing needs it. |
| `free` | `width`, `height`, `elements: [...]` with `rect`, `ellipse`, `text`, `badge`, `group`, `line`, `arrow` (`from`/`to` by id or `x1, y1, x2, y2`, `route: straight|orthogonal|curve`, `label`, `dashed`), `path` | Coordinates on an 8px grid. For what no block expresses. |
| `graph` | `direction`, `groups`, `nodes` (`id, label, sub, kind, group, file, status, notes, evidence`), `edges` (`from, to, label, kind, detail`) | Same vocabulary as graph.html; labels placed by ELK. |

Rules: one block answers the question first; others add context. Charts never invent data. Donut only up to 5 parts. Bars and lines never exceed 6 series. A block the data does not support is left out, not filled.

## templates/graph.html: interactive explorer

ELK layered layout rendered as SVG by the page itself: ELK sizes the layout from measured text, routes edges orthogonally and places edge labels as part of the layout, so labels never sit on top of nodes or other edges. Views as a segmented control, three information levels, legend that doubles as kind filter, search with a no-result state, zoom and direction controls, theme toggle (pure CSS, so the drawing follows instantly), inspector with summary, responsibility, file, status, evidence, notes and clickable neighbors, neighborhood isolation, empty and loading states, keyboard (`f` fit, `+`/`-` zoom, `d` direction, arrows pan, `/` search, `Esc` clear). Layout changes glide nodes to their new place. Nodes are not draggable; the layout is the layout.

Fill only `<title>` and the JSON inside `<script id="graph" type="application/json">`:

```json
{
  "title": "Pedido pago gera email via fila, em dois processos",
  "subtitle": "shop-api · lido em src/ e docs/ · 2026-10-10",
  "basis": "code",
  "summary": "Loja Node em dois processos: a API recebe pedidos e o webhook do Stripe; um worker separado envia o recibo por email a partir de uma fila no Redis.",
  "views": [
    {
      "id": "overview", "title": "Visão geral", "direction": "RIGHT",
      "summary": "Caminho de um pedido: cliente cria, Stripe cobra e avisa por webhook, API marca pago e enfileira, worker envia o email.",
      "groups": [ { "id": "api", "label": "Processo API", "file": "src/api/server.js", "view": "api" } ],
      "nodes": [
        { "id": "hooks", "label": "POST /webhooks/stripe", "sub": "marca pago, enfileira recibo",
          "kind": "critical", "group": "api", "file": "src/api/webhooks.js", "status": "verified",
          "evidence": "webhooks.js:12-16 não consulta event.id antes de enfileirar (inferido).",
          "notes": ["Evento duplicado gera dois emails."] },
        { "id": "redis", "label": "Redis", "sub": "fila BullMQ email", "kind": "queue", "status": "verified" }
      ],
      "edges": [ { "from": "hooks", "to": "redis", "label": "job send", "kind": "event", "step": 6, "detail": "BullMQ, 5 tentativas, backoff 2s" } ],
      "annotations": [ "API responde 200 ao Stripe antes do email sair." ]
    },
    { "id": "api", "title": "Processo API", "direction": "DOWN", "nodes": [], "edges": [] }
  ]
}
```

A single-view page may put `direction`, `groups`, `nodes`, `edges`, `annotations` at the top level instead of `views`.

Rules:

- `basis`: `code` (read in the repo), `docs` (per documentation or spec), `proposal` (designed, not built). It changes how status tags read: verified becomes "Verificado no código", "Conforme documentação" or "Decidido"; unknown becomes "Desconhecido", "Não documentado" or "Em aberto".
- `summary` (top level and per view): one or two sentences saying what the system or the view does and for whom. Shown in the inspector before any node is selected. Required.
- `direction`: `RIGHT` for flows, `DOWN` for layers and trees.
- `groups`: one per process, service or host, and every group holds at least one node (an empty group is dropped with a console warning). `label` names the boundary; `file` its entry point; `view` links to the view that details it (double-click or the inspector button opens it).
- `nodes.kind`: `entry`, `component`, `external`, `store`, `queue`, `decision`, `error`, `critical`. `status`: `verified`, `inferred`, `unknown`. `sub` is required. `file` is the path the reader opens. `evidence` says what proves the claim or why it is inferred. `notes` hold failure modes.
- `edges.kind`: `data`, `control`, `event`, `error`. `label` is required and short: at most 4 words or 28 characters (`job send`, `POST /orders`, `a cada 30s`). Anything longer goes in `detail`, shown in the inspector. `step` numbers edges for flows and shows at level 3.
- One view under 12 nodes plus groups. Split into views before crossing edges.
- Ids: letters, digits, `_`. Node ids are per view. Strings may hold any Unicode; escape quotes.

## templates/svg.html: composed drawing

Hand-placed SVG on an 8px grid with the design system's classes, a hover tooltip and click-to-inspect for any element with `data-name`, an optional criteria table, annotations, theme toggle. Use it for comparisons (same layout per option, the differing edge gets class `diff`), timelines with bands, annotated screens, or to embed an SVG produced by `d2` or `dot`.

Fill `<title>`, `<h1>`, the `<figure>` (SVG, `viewBox` sized to content, `figcaption` stating the one claim), the table and the annotation list.

Classes: `.node.entry|component|external|store|critical` (add `.inferred` for dashed), `.edge.data|control|event|error` (add `.diff` to thicken the edge that differs), `.panel` and `.panel-lbl` for option boxes, `.band` for a time band, `.lbl`, `.lbl-muted`, `.lbl-mono`, `.elbl` for edge labels with a background halo. Arrowheads: `marker-end` is set by the edge class. Interactivity: `data-name`, `data-sub`, `data-file`, `data-note` on a `<g>`.

Geometry: nodes 56px tall, widths in multiples of 8, 24px between a node and its label, 80px or more between columns. Text 12px for names, 11px for secondary labels. Nothing crosses; move a node before crossing an edge.

## templates/mermaid.html: viewer

Renders one Mermaid source with pan, zoom, copy-source and theme toggle; Mermaid theme variables come from the tokens, so both themes match the other templates. Fill `<title>`, `<h1>`, `<pre id="src">` and the annotation `<ul>`.

Source conventions:

- `sequenceDiagram` for time order; `Note over X: ...` for failure exits; `-->>` for replies; `alt`/`else` for branches; `participant W as webhooks.js<br/>POST /webhooks/stripe` to carry the file.
- `stateDiagram-v2` for lifecycles with guards on transitions (`pending --> paid : webhook ok`).
- `timeline` for calendar order; `mindmap` for loose ideas.
- `;` ends a statement anywhere, including inside a message or label. Use `,` instead.
- Quote labels that contain `:`, `(`, `)` or `/`. `%%` comments on their own line.
- Under about 12 participants or states; split otherwise.

## Mermaid in Markdown docs

Only when the user asks for a `.md` the repo will render (GitHub, docs site). Write the same diagram as a fenced `mermaid` block in that file, in addition to the page, never instead of it. Use `subgraph` for boundaries, `[(...)]` for stores, `{...}` for decisions, `<br/>` for line breaks, `LR` for flows and `TB` for layers.

## D2 and Graphviz

`d2 in.d2 out.svg` and `dot -Tsvg in.dot -o out.svg` need a binary on PATH (`command -v d2`, `command -v dot`). Use them for large dependency graphs or when the repo already keeps diagrams in that format. Paste the resulting `<svg>` into `templates/svg.html` and add `data-name` to the nodes that matter, so the page keeps the inspector and the theme.

## Maintenance

`python3 scripts/sync-tokens.py` copies `_tokens.css` into the templates; `--check` reports drift. `python3 scripts/contrast.py` checks the token pairs in both themes. ASCII diagrams are not a deliverable.
