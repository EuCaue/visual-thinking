# Design system

One visual language for every page the skill produces. Source of truth for values: `templates/_tokens.css` (synced into each template by `scripts/sync-tokens.py`). This file explains the intent so the agent fills templates without inventing styles.

## Stance

Technical documentation, read and operated, not a dashboard and not a marketing page. The content is the protagonist: whitespace instead of borders, hierarchy instead of decoration, alignment instead of containers, typography instead of components, contextual actions instead of permanent controls, progressive disclosure instead of everything at once. Brand lives in precision: alignment, spacing, one accent, type that stays quiet. Apple-like means that discipline, not blur, radius or gradients.

## Type

| Role | Token | Face | Size |
|---|---|---|---|
| UI, headings, labels | `--font-ui` | IBM Plex Sans (Google Fonts), fallback Segoe UI / system-ui | 11 to 22px |
| Files, symbols, numbers, edge labels, ticks | `--font-data` | IBM Plex Mono, fallback ui-monospace | 10.5 to 12.5px |

Page title 22px weight 600, tracking −0.02em; inspector name 17px, tracking −0.012em; block title 13.5px weight 600; body 12.5 to 14px; captions and ticks 10.5 to 11.5px muted. Section labels in the inspector are 12px uppercase with `--track-caps`, weight 600, `--fg-faint`. Numbers use tabular figures. Mono is for code, paths and data, never as a costume.

## Color

Neutrals carry a slight cool bias. One accent hue (blue) for selection, focus, links and control edges. Semantic colors have one meaning each and appear in both the drawing and the inspector legend:

| Meaning | Token | Where |
|---|---|---|
| Entry point, event flow, verified, for | `--ok` | entry nodes, event edges, status tag, + points |
| Data store, queue, data edges, inferred, caution | `--warn` | store and queue nodes, data edges, status tag, warn callout |
| Critical point, error path, unknown, against | `--danger` | critical nodes, error edges, status tag, − points |
| Component, call edge, selection | `--accent` | component nodes, control edges, selected element, focus ring |
| External system | `--line-strong` on `--bg-inset` | external nodes, dashed border |
| Series | `--s1` to `--s6` | chart series, donut parts, funnel stages |

No other hues. A drawing never needs a legend entry the tokens do not already define; the page computes its legend from what it drew.

Contrast (checked by `scripts/contrast.py`, 54 pairs in both themes): `--fg` and `--fg-muted` on `--bg` and `--bg-elev` ≥ 4.5:1; `--accent`, `--ok`, `--warn`, `--danger` and `--s1` to `--s6` ≥ 3:1 as marks and ≥ 4.5:1 as text where used as text.

## Surfaces and shape

Two layers only. Structure (header, inspector) is `--bg-elev` separated by a 1px `--line` hairline, never a shadow. Floating chrome over the canvas (levels, search, zoom group, tooltip, result count) is a translucent material (`--chrome` with backdrop blur) with one soft offset shadow (`--shadow-float`), because it sits above content. One radius scale: controls 8px, nodes 10px, groups and floating chrome 14px. Segmented controls carry the selected segment on `--bg-elev` inside a `--bg-inset` track. No nested cards: a group box in a graph is the only container inside the canvas; the inspector uses spacing and hairlines, not boxes; blocks sit on whitespace with a title, the drawing and a caption.

## Information architecture: three levels per block

Every block decides what the reader sees at once, on hover and on click. The runtime enforces the split; the agent fills the fields.

| Level | Where | What |
|---|---|---|
| 1. Immediate | the drawing | title that states the finding; the marks; every label needed to read the picture without the inspector (axes with unit, series end labels, values on few bars, edge labels, node responsibilities, best-of-row in bold) |
| 2. Exploration | hover, tooltip, highlight | the exact value with its delta, a cell note, an edge detail, a node's file, the neighborhood of a node |
| 3. Inspection | click, inspector | everything the block knows about the element: comparisons with siblings, position in the set, evidence, notes, connections as clickable rows, actions (open a view, isolate, change layout) |

At rest the inspector shows the view summary, the basis (`Lido no código`, `Baseado em documentação`, `Proposta`), source, date and period, the list of blocks in the view, the computed legend and the annotations. The test for level 1: a reader who did not see the prompt understands what is compared, measured or connected and in what unit. Formats.md lists what each block shows at each level.

## Data marks

- Series colors `--s1` to `--s6`, distinct in lightness so they survive grayscale; `--s1` is the accent. Never more than six series.
- Lines 2px with points when there are fewer than ~60 observations; area fills at 12% only for volumes and cumulative values; bars start at zero with 2px radius; donut ring with the total in the center and a list of parts beside it.
- Axes: one baseline in `--line-strong`, horizontal gridlines in `--grid`, ticks in `--font-data` 10.5px muted, the y label above the plot, the x label at the right end, dates in Portuguese short form. No vertical gridlines, no frame. Category labels never rotate: bars and dot plots turn horizontal instead.
- Reference lines dashed muted with a label at the end; annotations as short text with a thin leader and a dot on the point.
- End labels: name and last value at the end of each line when there are 2 to 4 series.
- Tooltip: a floating material with the x value, one row per series with its swatch and unit, and a one-line note (delta from the previous point, share of the stack).
- Matrix: numbers get an inline bar scaled to the row maximum; the best cell is bold with a stronger bar; booleans are a check or a dash; the column header says in how many rows the option wins.

## Diagram marks

- Node: fill and stroke from its kind; name in `--font-ui` weight 600; responsibility below in `--fg-muted` at level 2 and up; file path in `--font-data` at level 3.
- Status: verified solid border, inferred dashed, unknown dotted and 75% opacity.
- Edge: orthogonal route from ELK, 1.5px, arrowhead filled, color from kind; event edges dashed, error edges dotted; a 14px invisible hit area makes it clickable. Label in `--font-data` 11.5px on a `--bg` plate with a `--line` border, placed inline on the edge by ELK; step number in accent at level 3.
- Group: `--n-group-fill` with `--line` border, label top-left in caps, file at level 3, `abrir ›` when it links to a view.
- Selected: 2px `--accent` border plus a soft 6px ring at 22% opacity. Hover: stroke thickens, neighborhood keeps full opacity, everything else drops to 16%.
- Legend doubles as the kind filter: each kind row shows its count and toggles visibility; connection and status rows are informational.

## Motion

One ease (`--ease`, an ease-out) and three durations: `--d-fast` 120ms for hover, press and selection; `--d-base` 200ms for inspector swaps and fades; `--d-slow` 320ms for lines drawing in, bars growing from the baseline, marks gliding to a new scale after a legend toggle, nodes gliding to a new layout (FLIP), and programmatic zoom or fit. Entrance and swaps use keyframes that end in the element's natural state, so a frame that is never painted (hidden tab) costs nothing. Wheel zoom, drag and pinch track the pointer 1:1 with no easing. Press states scale to 0.97. Nothing moves on its own. `prefers-reduced-motion` sets the durations to zero and disables keyframes; `prefers-reduced-transparency` makes the floating chrome opaque.

## Responsive

Over 1100px the header is one row; below, the view tabs drop to their own row and scroll sideways. Under 820px the inspector becomes a bottom sheet with a handle, collapsed until something is selected; controls grow to 36px targets; the theme button keeps its icon only. Under 700px of canvas width every `row` or `grid` layout stacks, graphs flow top-down, KPIs wrap two per row, and pinch zooms. The canvas never scrolls the page sideways.

## Theme

Light is the base. Dark redefines the same tokens (not an inversion: fills get darker and less saturated, strokes get lighter and more saturated, accent shifts to a lighter blue so it stays readable on dark). The page follows the system preference until the viewer picks a theme; the pick is stored in `localStorage` under `vt-theme` when storage is available and applied on load before first paint. The drawing is CSS-colored, so a theme change never redraws.

## Copy

Controls name their action (`Ajustar`, `Isolar vizinhança`, `Abrir vista`). Section labels name content (`Sai para`, `Recebe de`, `Evidência`, `Por opção`). Block titles state what the reader learns, not the chart type. No instructions about how to use the page; the first inspector state summarizes the view instead.
