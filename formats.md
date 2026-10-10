# Formats and templates

The deliverable is a page built from `templates/`. All three templates share one design system (`templates/_tokens.css`, explained in [design.md](design.md)): IBM Plex Sans and Mono, semantic color tokens, light and dark themes with a persisted toggle, one radius scale, focus states, reduced motion. Fill the slots; never restyle.

## Delivery

| Tool present | Do |
|---|---|
| Artifact or similar publish tool | Publish the page (title: short name; icon: `diagram`). Give the link. |
| File-send tool that renders HTML inline | Write the page to a temp directory, send it with inline rendering. |
| Browser tool | Open the page once; check light and dark with the theme button; click a node. |
| None of the above | Write to `docs/diagrams/<slug>.html` in the project and give the path. |

The templates are HTML fragments (no `doctype`, `html`, `head`, `body` tags) so the artifact skeleton can wrap them; browsers open them directly as files too. Scripts and fonts load from cdnjs, jsdelivr and Google Fonts with pinned versions, which the artifact CSP allows.

## templates/graph.html: interactive explorer

Cytoscape + ELK layered layout. Views as tabs, three information levels, kind filters, search, direction toggle, theme toggle, inspector with responsibility, file, status, evidence, notes and edges, neighborhood isolation, keyboard (`f` fit, `/` search, `Esc` clear).

Fill only `<title>` and the JSON inside `<script id="graph" type="application/json">`:

```json
{
  "title": "Pedido pago gera email via fila, em dois processos",
  "subtitle": "shop-api · lido em src/ e docs/ · 2026-10-10",
  "basis": "code",
  "views": [
    {
      "id": "overview", "title": "Visão geral", "direction": "RIGHT",
      "groups": [ { "id": "api", "label": "Processo API", "file": "src/api/server.js", "view": "api" } ],
      "nodes": [
        { "id": "hooks", "label": "POST /webhooks/stripe", "sub": "marca pago, enfileira recibo",
          "kind": "critical", "group": "api", "file": "src/api/webhooks.js", "status": "verified",
          "evidence": "webhooks.js:12-16 não consulta event.id antes de enfileirar (inferido).",
          "notes": ["Evento duplicado gera dois emails."] },
        { "id": "redis", "label": "Redis", "sub": "fila BullMQ email", "kind": "queue", "status": "verified" }
      ],
      "edges": [ { "from": "hooks", "to": "redis", "label": "job send", "kind": "event", "step": 6 } ],
      "annotations": [ "API responde 200 ao Stripe antes do email sair." ]
    },
    { "id": "api", "title": "Processo API", "direction": "DOWN", "nodes": [], "edges": [] }
  ]
}
```

A single-view page may put `direction`, `groups`, `nodes`, `edges`, `annotations` at the top level instead of `views`.

Rules:

- `basis`: `code` (read in the repo), `docs` (per documentation or spec), `proposal` (designed, not built). It changes how status tags read: verified becomes "Verificado no código", "Conforme documentação" or "Decidido"; unknown becomes "Desconhecido", "Não documentado" or "Em aberto".
- `direction`: `RIGHT` for flows, `DOWN` for layers and trees.
- `groups`: one per process, service or host. `label` names the boundary; `file` its entry point; `view` links to the view that details it (double-click or the inspector button opens it).
- `nodes.kind`: `entry`, `component`, `external`, `store`, `queue`, `decision`, `error`, `critical`. `status`: `verified`, `inferred`, `unknown`. `sub` is required. `file` is the path the reader opens. `evidence` says what proves the claim or why it is inferred. `notes` hold failure modes.
- `edges.kind`: `data`, `control`, `event`, `error`. `label` is required. `step` numbers edges for flows and shows at level 3.
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
