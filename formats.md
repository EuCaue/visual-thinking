# Formats and templates

The deliverable is a page built from `templates/`. The three templates share one design system (`templates/_tokens.css`, explained in [design.md](design.md)): the system font stacks (`system-ui` for UI, `monospace` for data), semantic color tokens, light and dark themes with a persisted toggle, one radius scale, focus states, reduced motion. Fill the slots; never restyle.

## Delivery

The skill assumes nothing about the agent or harness. Any agent that can write a file, and optionally open a browser or publish a page, can produce the same result.

| Tool present | Do |
|---|---|
| A publish or artifact tool that wraps HTML in its own document skeleton | Build with `--fragment` (or copy the template as it is) and publish. Title: a short name. Give the link. |
| A tool that sends or renders a file | Build the standalone page, send it with inline rendering. |
| A browser tool | Open the page once; check light and dark with the theme button; click one element and read the inspector. |
| None of the above | Write `docs/diagrams/<slug>.html` in the project and give the full absolute path. |

Build: `python3 scripts/build-scene.py scene.json out.html "Title"` validates the scene (dangling ids, unlabeled edges, unknown kinds, empty groups, out-of-range values; exit 1 with one line per problem, nothing built), then injects it into `templates/canvas.html` and wraps it as a complete document (`<!doctype html>`, `html`, `head`, `body`), so the file opens from disk or any static host. The first output line is the absolute path of the page. `--fragment` keeps the template as a fragment (no document tags) for publish tools that add their own skeleton; `--validate-only` checks without writing; `--self-contained` inlines the d3 and elkjs libraries into the file, so charts, trees and graphs work offline (the build needs network once; without it the flag keeps the CDN tags and warns). Without Python, copy the template and replace the JSON inside `<script id="scene">` and the `<title>` by hand; the fragment opens in a browser as well.

The page depends on two libraries loaded from CDNs with pinned versions (d3 7.9.0 on cdnjs for scales, shapes and number and date formats; elkjs 0.9.3 on jsDelivr for graph and tree layout). No fonts, no build step: type is the system stack. CSS, runtime and data are inside the file; charts, trees and graphs additionally load those two libraries, and show a one-line message offline unless the build used `--self-contained` (above).

## templates/canvas.html: composable canvas (default)

A scene is one or more views; a view is a layout of blocks. The runtime measures text, lays out, draws in SVG, animates, and gives every page the same controls: views as a segmented control, search (`/`), zoom, fit and pinch, theme toggle, a Texto/Desenho toggle, right-click menu with per-target actions (inspect, copy link and isolate on elements; summary, playback and export on blocks; fit, overview, search, levels, PNG/SVG export and theme on empty canvas), keyboard (`f` fit then overview, `+`, `-`, arrows, `Esc`, `p` play the first sequence, `1` `2` `3` levels and `d` direction when a view holds a graph). Scroll pans; ctrl or cmd with scroll, or a pinch, zooms.

Legibility comes first: the fit never shrinks below scale 0.75 (12px text stays readable). Blocks reflow to the width that keeps that scale: cards wrap into rows, steps and timelines turn vertical, KPIs wrap, a matrix wider than the screen stacks one option per section, charts and other fixed-width blocks shrink to it, a `row` or `grid` layout too wide falls back to `stack`, a left-to-right graph or entity model too wide turns top-down. What still does not fit is panned, never shrunk. A second press of `f` (or the fit button) shows the whole view at any scale.

Reading mode renders the view as an outline in normal flow: headings, lists and tables built from the same scene. Phones under 700px open in it; the header button switches; the choice persists per viewer; `?mode=read` or `?mode=draw` in the address, or `"mode": "read"` in the scene, decide first. The same outline is the accessible description of the canvas (`aria-describedby`), so screen readers get text on every screen size.

Deep links: selecting anything writes `#v=<view>&b=<block>&k=<element>` into the address; opening that address restores the view and the selection. "Copiar link para este elemento" in the right-click menu copies it.

Export: the right-click menu exports the view, or one block, as SVG (styles and the current theme's tokens inlined) or as PNG at 2x. `window.vtExport.svg(blockIndex?)` returns the same SVG string for scripts. No text leaves its box: all labels wrap through one `wrap()` function, which hard-breaks any word wider than the box (long paths, hashes, URLs); block and step/card titles wrap and are counted in the box height; a `free` shape grows vertically to fit its own text. Nothing needs to be kept short for the layout to hold.

Every block owns its inspector: the right panel (a bottom sheet on phones) shows the view summary at rest, the block's own summary when its title is clicked, and the selected element's details when something inside is clicked. A legend is computed from what was drawn (series, element kinds, connection kinds, status, marks) and filters where filtering makes sense. Hover gives the short version (tooltip), click the full one. Nothing essential hides: the drawing answers the question; the inspector adds depth.

```json
{
  "title": "Svelte troca runtime por build", "subtitle": "Comparação · fontes nos rodapés",
  "basis": "docs", "source": "Documentação oficial, benchmarks de 2025", "date": "2026-10-11", "period": "versões estáveis em out/2026",
  "summary": "O achado em uma frase: Svelte compila o que React e Vue fazem em runtime.",
  "views": [
    { "id": "main", "title": "Comparar", "summary": "O achado desta vista, em uma frase.",
      "layout": { "type": "stack", "gap": 40 },
      "blocks": [ { "type": "matrix", "id": "m", "title": "React, Vue e Svelte", "columns": [], "rows": [] } ],
      "annotations": [ "Texto que o desenho não carrega." ] }
  ]
}
```

Scene fields: `title` (the finding), `subtitle` (scope, date, source in short), `basis` (`code`, `docs`, `proposal`; sets the status vocabulary), `source` (URLs render as clickable links in the inspector), `date`, `period` (shown under the summary), `summary`, `views`, optional top-level `annotations` for the first view. Optional: `lang` (`pt`, default, or `en`: interface strings, number and date formats), `root` (absolute path of the repository; every `file` becomes an editor link, `path:line` included), `editor` (`vscode` default, `vscode-insiders`, `vscodium`, `cursor`, `windsurf`, `zed`, `idea`), `mode` (`read` opens in reading mode everywhere).

Text budget, warned by the build (`texto:` lines, `--no-text-lint` silences them): page `title` and `subtitle` 12 words, block `title` 8, node `sub` and card `meta` 6, `text` 15, `detail`, `note`, summaries and annotations 25, a whole view 250. Summaries and details that talk about the page or the navigation, details that repeat their node, and summaries that list the drawing's labels are flagged too.

`layout.type`: `stack` (one below the other, narrative order), `row` (side by side, for things to compare), `grid` with `columns` (a block with `"full": true` takes a whole row). On screens under 700px every layout stacks and graphs flow top-down; on wider screens a layout wider than the legible width stacks too.

A view may carry `scenarios: {controls: [{id, label, options, default}], overrides: {"<controlId>:<option>": <patch>, or "<option>": <patch>}}`. The runtime renders one segmented control per entry above the canvas; switching applies the matching patch onto the view (arrays of objects with `id` merge by id, objects merge key by key) and re-renders without reload. Switching views restores defaults.

Every block has `type`, `id`, `title` (what the reader learns; it is also the click target for the block inspector), optional `caption` (source, scope, shown under the drawing), optional `width`.

| Block | Fields | What the reader gets |
|---|---|---|
| `chart` | `kind`: `line`, `area`, `bar`, `stackedBar`, `scatter`, `dot`, `histogram`, `donut`, `tornado`. `series: [{name, data: [[x, y], ...], unit}]` (`values: [...]` for histogram; `[[label, value, note]]` for donut; `[[x, y, label]]` for scatter; `[{name, low, high, lowLabel, highLabel}]` for tornado with `baseline: {label, value}`). `x: {type: category|number|time, label}`; `y: {label, unit, min, max}`; `unit` (block level); `marks`: subset of `line`, `point`, `area`, `bar`, `label`; `curve: "smooth"`; `orientation: horizontal|vertical` (bars and dot plots go horizontal by themselves when category labels are long); `labels: false`; `endLabels: false`; `legend: false`; `refLines: [{y or x, label}]`; `annotations: [{x, y, text, side}]`; `height`, `width`; `source` | Axes with unit, gridlines, baseline at zero for bars and areas, values written on bars when few, name and last value at the end of each line, reference lines, annotated events. Tornado draws bidirectional bars from the baseline sorted by swing, dashed baseline, value labels, hover deltas vs baseline. Hover: scrub with every series at that x, or the mark's value with delta from the previous point. Click a mark: value, previous, change, share of total, position in the series, the other series at the same x. Click the title: period, unit, per-series min, max, last and change, references, events, source. Legend toggles series; the chart glides to the new scale. |
| `kpi` | `items: [{label, value, prefix, unit, delta, deltaKind: ok|danger|neutral, spark: [...], sparkUnit, text}]` | Numbers first, no tiles; they wrap to the next row at the legible width. Click: value, change, sparkline min, max and trend. |
| `matrix` | `columns: [{label, sub, text}]`, `rows: [{label, cells: [...], best: max|min|<column index>, unit, bars, text}]`; a cell is a string, number, boolean or `{value, note, unit}`; `stack: false` keeps the table on narrow screens | Numbers get an inline bar scaled to the row maximum; the best cell is bold; booleans are a check or a dash; each column header says in how many rows it wins. Wider than the screen, it stacks: one section per option with its criteria as label and value. Hover a cell: its note. Click a column: every criterion for that option. Click a criterion: the options ranked. |
| `decision` | `mode: weighted`, `options: [{id, label, sub, text, reversibility: one-way|two-way, vetoBelow}]`, `criteria: [{id, label, weight, unit, vetoBelow, scores: {<optionId>: {score, raw, note}}}]`, `weightBasis` (required: where the weights come from), `vetoBelow` (block level), `recommendation: {optionId, rationale}` | Weighted matrix with per-criterion weight sliders, score bars in every cell, summary row with the weighted total $S_i = \sum w_j s_{ij} / \sum w_j$, leader highlighted, veto badges disqualifying below-cut options, reversibility tags per option, sensitivity note naming the flip criterion. Dragging a slider recomputes totals, ranks and sensitivity live. Click an option or a cell: scores per criterion, raw values, notes, veto reasons. |
| `cards` | `items: [{title, meta, text, detail, file, points: [{kind: pro|con|neutral, text, detail}]}]`, `cardWidth` | Aligned columns with + and − points (a card without points shows its `text`); as many per row as fit the legible width. Click a card: points grouped as for, against and notes, with the balance. |
| `timeline` | `events: [{date, title, text, detail, kind: milestone}]`, `periods: [{from, to, label}]`, `orientation` | Horizontal up to 7 events, vertical beyond; periods as bands. Title, date and text keep fixed clear slots and the block grows to hold them. Click an event: position, time since the previous and since the start, period, neighbors. Click the title: range, counts, periods, events. |
| `steps` | `items: [{title, text, detail, kind}]`, `stepWidth`, `orientation: horizontal|vertical` | Numbered pipeline, vertical when it does not fit the width. Click: step n of N, detail, previous and next. The block inspector plays it step by step. Decisions belong in `graph`. |
| `tree` | `root: {label, text, detail, kind, children: [...]}`, `direction: DOWN|RIGHT`, `layout: tree|mindmap` | Click a node: path from the root, level, counts below, parent and children. Click the title: levels, item and leaf counts, first level. |
| `quadrant` | `x: {label, low, high}`, `y: {label, low, high}`, `quadrants: [4 labels]`, `items: [{label, x, y, text, detail}]` with x and y in 0..1 | Click an item: its quadrant and both coordinates in words. Click the title: counts per quadrant. |
| `spectrum` | `min`, `max` (labels), `items: [{label, value 0..1, text, detail}]` | Click: position and order between the two extremes. |
| `cycle` | `items: [{label, text, detail}]` | Click: stage n of N, what comes before and after. |
| `funnel` | `items: [{label, value, text, detail}]`, `shape: funnel|pyramid`, `unit` | Each stage shows the share of the previous one; click adds the share of the first; the title shows the total conversion. |
| `venn` | `sets: [{label, items, text}]` (2 or 3), `overlaps: [{sets: [0, 1], label, items, text}]` | Click a set or an intersection: its items. Overlap labels stack vertically when their lenses share the center, so they never sit on each other; a duplicated `sets` pair fails validation instead. |
| `callout` | `kind: note|warn|danger|ok`, `label`, `text` | The one sentence the reader must not miss. |
| `text` | `text`, `width` | A paragraph when the drawing needs it. |
| `free` | `width`, `height`, `elements: [...]` with `rect` and `ellipse` (`id, x, y, w, h, text, sub, kind, detail`), `text` (`size: lg|sm`, `mono`), `badge`, `group`, `line` and `arrow` (`from`/`to` by id or `x1, y1, x2, y2`, `route: straight|orthogonal|curve`, `label`, `detail`, `kind`, `dashed`), `image` and `video` (`id, x, y, w, h, src, alt, sub, detail`), `path` | Coordinates on an 8px grid. Click a shape: its detail and its connections. For what no block expresses. `src` is a link or a path relative to the page; an absolute local path warns, since it breaks when the page is sent. Opposite arrows between the same pair split their labels along the line; an exact duplicate pair fails validation, since the author must move or merge it. |
| `graph` | `direction`, `groups: [{id, label, sub, text, file, view}]`, `nodes: [{id, label, sub, kind, group, file, status, evidence, notes, detail, view, reversibility: one-way|two-way, consequence: {order: 1|2|3, polarity: ok|warn|danger|neutral}}]`, `edges: [{from, to, label, kind, detail, step, prob}]` | ELK layered layout, orthogonal edges, labels placed by the engine so they never cover a node. Three levels (`Mapa`, `Contexto`, `Detalhes`): names only; responsibilities and edge labels; files, step numbers and status marks. Hover a node: its neighborhood stays lit. Click a node: responsibility, file, kind, status, evidence, notes, outgoing and incoming edges (clickable), isolate neighborhood. Click a `decision` node or one of its outgoing edges: the full downstream consequence path stays lit, the rest dims, and the inspector aggregates the path (consequence count, reach by order, per-node order/polarity/probability). Click an edge or its label: kind, step, probability, detail, both ends. Click a group label: its members and a button to open the view it points to (double-click does the same). Legend counts kinds, connections and status, and hides kinds. |
| `entity` | `entities: [{id, label, sub, text, detail, file, diff, fields: [{name, type, pk, fk: true|"table.field", nullable, note}]}]`, `relations: [{from, to, card: "1:N"|"N:1"|..., label, detail, fromField, toField, diff}]`, `direction` | Data model: each table as a box with its fields, PK and FK marks, types right-aligned, optional fields with `?`; relations routed by ELK with cardinality on the line. Click a table: fields, what it points to, what references it. Click a relation: cardinality and both ends. |
| `heatmap` | `x: [labels]`, `y: [labels]`, `values: [[...]]` (rows follow `y`, `null` for no data), `unit`, `scale: seq|div`, `mid`, `reverse`, `cellSize`, `labels: false`; or `calendar: true` with `data: [[date, value]]` | One hue, intensity is the value (diverging: two hues around `mid`). Values written in cells when they fit. Calendar: one square per day, weeks as columns. Hover: the value; click a row label: mean, range and every value. |
| `gantt` | `tasks: [{id, label, start, end, group, kind: milestone|critical, deps: [ids], progress: 0..1, owner, text, detail}]`, `today`, `width` | Bars on a time axis grouped by `group`, milestones as diamonds, dependency arrows, done share darker, critical path red, a dashed line at `today`. Click a task: dates, duration, progress, what it depends on and what it unblocks. |
| `sankey` | `nodes: [{id, label, text, detail}]`, `links: [{from, to, value, label}]`, `unit`, `align: justify|left|right`, `color: source|target`, `height` | Quantities flowing between stages; band width is the value. One source: each first split gets a hue. Hover a node: its flows stay lit. Click a node: in, out, from where and to where. Cycles fail validation. |
| `treemap` | `root: {label, children: [{label, value, text, detail, children}]}`, `unit`, `layout: treemap|sunburst`, `height` | Parts of a whole that nest: area (or angle) is the value, hue follows the top-level part. Click: value, share of the total and of the group, what is inside. |

Graph and entity elements accept `diff: added|removed|changed` (written by `scripts/scene-diff.py`): added gets a green outline, changed amber, removed a dashed red outline and stays faded in place; the legend counts them under "Mudanças".

Graph rules: `kind` is one of `entry`, `component`, `external`, `store`, `queue`, `decision`, `error`, `critical`; `status` one of `verified`, `inferred`, `unknown` (wording follows `basis`); `sub` is required; `label` on edges is required and short (at most 4 words or 28 characters), the rest goes in `detail`; `step` numbers a flow; a group holds at least one node (empty groups are dropped with a console warning); one view stays under 12 nodes plus groups, with a `views` entry per process and `view` on the group that details it. Ids: letters, digits, `_`; node ids are per view.

Chart rules: bars and areas start at zero; lines may start above zero only when the data never approach zero; up to 6 series; donut only up to 5 parts; a block the data does not support is left out, not filled. Value labels that would sit on another label are dropped; the tooltip and the inspector keep every number.

Decision rules: no matrix without weights — every `decision` states `weightBasis`; eliminatory constraints are `vetoBelow`, not low scores; every score carries its evidence in `raw`/`note` or is tagged `inferred`/`unknown`; the title names the recommendation and the inspector traces it.

## templates/svg.html: composed drawing

Hand-placed SVG on an 8px grid with the design system's classes, a hover tooltip and click-to-inspect for any element with `data-name`, an optional criteria table, annotations, theme toggle. Use it for exact placements the blocks cannot express: two architectures side by side with one differing edge, annotated screens, packet layouts, or to embed an SVG produced by `d2` or `dot`.

Fill `<title>`, `<h1>`, the `<figure>` (SVG, `viewBox` sized to content, `figcaption` stating the one claim), the table and the annotation list.

Classes: `.node.entry|component|external|store|critical` (add `.inferred` for dashed), `.edge.data|control|event|error` (add `.diff` to thicken the edge that differs), `.panel` and `.panel-lbl` for option boxes, `.band` for a time band, `.lbl`, `.lbl-muted`, `.lbl-mono`, `.elbl` for edge labels with a background halo. Arrowheads: `marker-end` is set by the edge class. Interactivity: `data-name`, `data-sub`, `data-file`, `data-note` on a `<g>`.

Geometry: nodes 56px tall, widths in multiples of 8, 24px between a node and its label, 80px or more between columns. Text 12px for names, 11px for secondary labels. Nothing crosses; move a node before crossing an edge.

## templates/mermaid.html: viewer

Renders one Mermaid source with pan, zoom, copy-source and theme toggle; Mermaid theme variables come from the tokens, so both themes match the other templates. Fill `<title>`, `<h1>`, `<pre id="src">` and the annotation `<ul>`.

Source conventions:

- `sequenceDiagram` for time order; `Note over X: ...` for failure exits; `-->>` for replies; `alt`/`else` for branches; `participant W as webhooks.js<br/>POST /webhooks/stripe` to carry the file.
- `stateDiagram-v2` for lifecycles with guards on transitions (`pending --> paid : webhook ok`).
- `;` ends a statement anywhere, including inside a message or label. Use `,` instead.
- Quote labels that contain `:`, `(`, `)` or `/`. `%%` comments on their own line.
- Under about 12 participants or states; split otherwise.

## Mermaid in Markdown docs

Only when the user asks for a `.md` the repo will render (GitHub, docs site). Write the same diagram as a fenced `mermaid` block in that file, in addition to the page, never instead of it. Use `subgraph` for boundaries, `[(...)]` for stores, `{...}` for decisions, `<br/>` for line breaks, `LR` for flows and `TB` for layers.

## D2 and Graphviz

`d2 in.d2 out.svg` and `dot -Tsvg in.dot -o out.svg` need a binary on PATH (`command -v d2`, `command -v dot`). Use them for large dependency graphs or when the repo already keeps diagrams in that format. Paste the resulting `<svg>` into `templates/svg.html` and add `data-name` to the nodes that matter, so the page keeps the inspector and the theme.

## Maintenance

`python3 scripts/sync-tokens.py` copies `_tokens.css` into the templates; `--check` reports drift. `python3 scripts/contrast.py` checks the token pairs in both themes. `sh scripts/build-examples.sh` rebuilds `examples/*.html` from their scenes. ASCII diagrams are not a deliverable.
