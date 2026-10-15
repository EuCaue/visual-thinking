# Design system

One visual language for every page the skill produces. Source of truth for values: `templates/_tokens.css` (synced into each template by `scripts/sync-tokens.py`). This file explains the intent so the agent fills templates without inventing styles.

## Stance

Technical documentation, read and operated, not a dashboard and not a marketing page. The content is the protagonist: whitespace instead of borders, hierarchy instead of decoration, alignment instead of containers, typography instead of components, contextual actions instead of permanent controls, progressive disclosure instead of everything at once. Brand lives in precision: alignment, spacing, one accent, type that stays quiet. Apple-like means that discipline, not blur, radius or gradients.

## Type

| Role | Token | Face | Size |
|---|---|---|---|
| UI, headings, labels | `--font-ui` | system font stack (`system-ui`, fallback `-apple-system` / `sans-serif`) | 11 to 22px |
| Files, symbols, numbers, edge labels, ticks | `--font-data` | system `monospace` | 10.5 to 12.5px |

Page title 22px weight 600, tracking −0.02em; inspector name 17px, tracking −0.012em; block title 13.5px weight 600; body 12.5 to 14px; captions and ticks 10.5 to 11.5px muted. No label is set in capitals: inspector sections, graph group titles, scenario labels and callout labels are sentence case, weight 600; hierarchy comes from weight, size and hairlines, never from uppercase tracking. Numbers use tabular figures. Mono is for code, paths and data, never as a costume.

## Color

Apple system neutrals: light is `#F5F5F7` ground, white panels and cards, `#1D1D1F` text; dark is a graphite ladder, never pure black (ground `#18181A`, panels and cards `#222225`, wells `#2C2C30`), so elevation reads as a lighter step, not as a shadow. The accent is graphite (`--fg`'s value): selection, focus and links stay neutral and color is left to meaning. Node kinds carry the system colors as solid tiles with a white glyph. Semantic colors have one meaning each and appear in both the drawing and the inspector legend:

| Meaning | Token | Where |
|---|---|---|
| Entry point, event flow, verified, for | `--ok` | entry nodes, event edges, status tag, + points |
| Data store, queue, data edges, inferred, caution | `--warn` | store and queue nodes, data edges, status tag, warn callout |
| Critical point, error path, unknown, against | `--danger` | critical nodes, error edges, status tag, − points |
| Selection, focus | `--accent` | selected element, focus ring, links |
| External system | `--line-strong` on `--bg-inset` | external nodes, dashed border |
| Series | `--s1` to `--s6` | every data mark: chart series, heat and map scales, matrix and decision bars, custom drawings. Data never uses `--accent`, which stays for selection |

No other hues. A drawing never needs a legend entry the tokens do not already define; the page computes its legend from what it drew.

Contrast (checked by `scripts/contrast.py`, 54 pairs in both themes): `--fg` and `--fg-muted` on `--bg` and `--bg-elev` ≥ 4.5:1; `--accent`, `--ok`, `--warn`, `--danger` and `--s1` to `--s6` ≥ 3:1 as marks and ≥ 4.5:1 as text where used as text.

## Icons

One 16px icon set drawn in the runtime (`KICON`), one 1.4 stroke, geometry only, one icon per node kind: entry (play), component (square in square), store (cylinder), queue (slotted box), external (arrow out of a box), decision (diamond), critical (warning triangle), error (crossed circle). They appear in four places and nowhere else, so they mark kind without decorating: the tile at the left of a graph node (Contexto and Detalhes levels; the Mapa level drops it), the inspector title, the rows that list neighbors, and the legend of node kinds. The glyph is white on a tile of the kind's system color (`--k-*`), red on critical and error.

## Selection

A click keeps the selected element's neighborhood lit until something else is picked: the node gets one 2px accent ring 4px outside its card (the card keeps its own outline; never both), its edges thicken, everything else drops to 30% opacity. Keyboard focus reuses that ring at 60% instead of adding an outline. Hover shows the same neighborhood for a glance without committing.

Esc, a click on empty canvas, "Visão geral" in the inspector and "Limpar seleção" in the context menu all return to rest: no selection, no lit neighborhood, no isolated subgraph, the view summary in the inspector. The menu item appears only when there is something to clear.

## Tooltips

A tooltip appears after the pointer rests 320ms, then follows it; moving to the next element shows the next one at once. It holds only what the drawing does not show: the element's name, its `detail` cut to the first sentence (140 characters at most) and its file. The inspector keeps the rest.

## Notices and sources

A callout is a 12px-radius well (`--bg-inset`) tinted about 10% toward its kind's hue, never a colored side rule. Its label shows only when it says something the block title does not. In the inspector, sources read as short names (the last part of a path or URL) with the full value in the link title; past three, the rest fold under "mais N".

## Surfaces and shape

Two layers only. Structure (header, inspector) is `--bg-elev` separated by a 1px `--line` hairline, never a shadow. Floating chrome over the canvas (levels, search, zoom group, tooltip, result count) is a translucent material (`--chrome` with backdrop blur) with one soft offset shadow (`--shadow-float`), because it sits above content. One radius scale: controls 8px, nodes 10px, groups and floating chrome 14px. Segmented controls carry the selected segment on `--bg-elev` inside a `--bg-inset` track. No nested cards: a group box in a graph is the only container inside the canvas; the inspector uses spacing and hairlines, not boxes; blocks sit on whitespace with a title, the drawing and a caption.

## Inspector and toolbar

The canvas leads; the inspector is a tool beside it. It is 304px wide with 20px padding, and its type sits one step under the canvas: element name 16px, summary 13px, section labels 12px muted, rows 12.5px. Block titles on the canvas are 15px, card and table-group titles 13.5px, node names 12.5px. The header carries the page's tools as icons, in reading order: search (opens into an inset field, `/`), theme, text mode, inspector. Canvas-only controls float on the canvas: detail level top left, zoom bottom right.

## Text mode

One centered 880px column. Prose keeps a 66ch measure at 15px/1.6; the view title is 24px, its summary a 17px muted lead, each block opens with a hairline and an 18px title. KPIs become a row of figures (28px value over a 13px label). Tables take the full column with fixed widths, so grouped tables line up, and long codes break after `_`.

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
- Edge: orthogonal route from ELK; the kind is read from line and head, not hue. Call: 1.5px solid, filled triangle. Data: 2.25px, open triangle. Event: 1.25px dashed, chevron. Error: red, dotted, bar end. When a block names its main path (`main: true` or a `step`), those edges gain 0.75px and the rest drop to 1.25px at 70%. The legend draws each kind with the same head. A 14px invisible hit area makes it clickable. Label in `--font-data` 11.5px on a `--bg` plate with a `--line` border, placed inline on the edge by ELK; step number in accent at level 3.
- Group: `--n-group-fill` with a dashed `--line-strong` border; its title takes the first stretch of the top band that no edge crosses, and when there is none it keeps the corner and cuts the line under it with a halo of the group fill; file at level 3, `abrir ›` when it links to a view.
- Selected: see Selection. Hover: stroke thickens, neighborhood keeps full opacity, everything else drops to 16%.
- Legend doubles as the kind filter: each kind row shows its count and toggles visibility; connection and status rows are informational.

## Clearance

A line never runs under text it does not own. Each edge may touch only its two end nodes and its own label; group titles move along the top band to a free stretch; tree levels share a left edge so links never pass behind a wider sibling; the gantt's today label gets its own row above the dates. `tests/audit_layout.py` checks every view of every example for arrow → text, arrow → card, arrow → arrow, label → card and text → text, and a new drawing type is not done until it passes.

## Tables

A `matrix` is a table built for the canvas, not an HTML table pasted in. Column widths follow content (text columns up to 280px, number columns hold a bar and the value, booleans a mark); header alignment follows the cells (text left, numbers right, marks centered); rows grow to three lines, long codes break after `_ / . -`, and a cut cell shows its full value on hover. Rows with a `group` fold under a heading with a chevron and a count. A click opens the row as a record in the inspector. Zoomed far out, rows turn into bars so the shape of the data stays readable. Wider than the screen even after text columns shrink to 120px, the table stacks.

## Navigation and selection

A row in the inspector, "Ir para a origem" or "Ir para o destino" selects the element and glides the view until it sits centered in the free canvas at a legible scale; an element already in view does not move. Pan and zoom write the transform once per frame; trackpad zoom follows the gesture's size. Holding Alt (Option) turns dragging into text selection on the canvas; the context menu copies an element's text.

## Motion

One ease (`--ease`, an ease-out) and three durations: `--d-fast` 120ms for hover, press and selection; `--d-base` 200ms for inspector swaps and fades; `--d-slow` 320ms for lines drawing in, bars growing from the baseline, marks gliding to a new scale after a legend toggle, nodes gliding to a new layout (FLIP), and programmatic zoom or fit. Entrance and swaps use keyframes that end in the element's natural state, so a frame that is never painted (hidden tab) costs nothing. Wheel zoom, drag and pinch track the pointer 1:1 with no easing. Press states scale to 0.97. Nothing moves on its own. `prefers-reduced-motion` sets the durations to zero and disables keyframes; `prefers-reduced-transparency` makes the floating chrome opaque. The one exception that stays opt-in: a graph block with `motion: true` sends small packets along its data and event edges every 2.2 seconds; an undirected edge kind carries nothing, and the same reduced-motion switch stops the packets.

## Blocks added for decisions and media

- Decision matrix: one summary row per option carries the weighted total with the leader highlighted in `--accent`; options below a `vetoBelow` cut get a `--danger` badge and leave the ranking; each criterion row has a weight slider that recomputes totals, ranks and the flip-criterion note live, without redrawing the block.
- Tornado chart: horizontal bars from a dashed baseline at the case-base value, `--warn` for the low side and `--accent` for the high side, series sorted by swing, value labels dropped when they would land on the row name or the axis.
- Scenario bar: one segmented control per control above the canvas, reusing the `.seg` styles; switching applies the override patch and re-renders the view without a reload.
- Right-click menu: the same floating-chrome material as the tooltip and the zoom group (`--chrome`, `--shadow-float`, 14px radius) with rows styled like inspector rows; items come from the target (inspect or isolate on elements, fit, search, levels and theme on empty canvas).
- Media in `free`: `image` and `video` elements place a remote or page-relative file on the 8px grid; video uses its native controls and the canvas ignores presses on it, so the pan does not fight the player. Source URLs in the scene render as `--accent` links in the inspector.

## Responsive

Over 1100px the header is one row; below, the view tabs drop to their own row and scroll sideways. On desktop blocks are laid out for the width beside an open inspector, so opening or closing it refits the drawing and never reflows it. Under 820px the inspector becomes a bottom sheet with a handle, collapsed until something is selected; controls grow to 36px targets; the theme button keeps its icon only. Under 700px of canvas width every `row` or `grid` layout stacks, graphs flow top-down, KPIs wrap two per row, and pinch zooms. The canvas never scrolls the page sideways.

## Theme

Light is the base. Dark redefines the same tokens (not an inversion: fills get darker and less saturated, strokes get lighter and more saturated, the graphite accent turns light). The page follows the system preference until the viewer picks a theme; the pick is stored in `localStorage` under `vt-theme` when storage is available and applied on load before first paint. The drawing is CSS-colored, so a theme change never redraws.

## Copy

Controls name their action (`Ajustar`, `Isolar vizinhança`, `Abrir vista`). Section labels name content (`Sai para`, `Recebe de`, `Evidência`, `Por opção`). Block titles state what the reader learns, not the chart type. No instructions about how to use the page; the first inspector state summarizes the view instead.
