# Design system

One visual language for every page the skill produces. Source of truth for values: `templates/_tokens.css` (synced into each template by `scripts/sync-tokens.py`). This file explains the intent so the agent fills templates without inventing styles.

## Stance

Technical documentation, not a dashboard. The page is read and operated: a reader scans the drawing, clicks what matters, reads the inspector. Brand lives in precision: alignment, spacing, one accent, type that stays quiet. Mode: operate/read. Variance low, motion minimal, density medium.

## Type

| Role | Token | Face | Size |
|---|---|---|---|
| UI, headings, labels | `--font-ui` | IBM Plex Sans (Google Fonts), fallback Segoe UI / system-ui | 12.5 to 20px |
| Files, symbols, numbers, edge labels | `--font-data` | IBM Plex Mono, fallback ui-monospace | 11 to 12.5px |

Scale: `--fs-xs` 11, `--fs-sm` 12.5, `--fs-md` 14, `--fs-lg` 16, `--fs-xl` 20. Title is `--fs-xl` weight 600. Section labels in the inspector are `--fs-xs` uppercase with `--track-caps`, weight 600, color `--fg-muted`. Numbers use tabular figures. Mono is for code, paths and data, never as a costume.

## Color

Neutrals carry a slight cool bias. One accent hue (blue) for selection, focus, links and control edges. Semantic colors have one meaning each and appear in both the drawing and the inspector:

| Meaning | Token | Where |
|---|---|---|
| Entry point, event flow, verified | `--ok` | entry nodes, event edges, status tag |
| Data store, queue, data edges, inferred | `--warn` | store and queue nodes, data edges, status tag |
| Critical point, error path, unknown | `--danger` | critical nodes, error edges, status tag |
| Component, call edge, selection | `--accent` | component nodes, control edges, selected node, focus ring |
| External system | `--line-strong` on `--bg-inset` | external nodes, dashed border |

No other hues. A drawing never needs a legend entry the tokens do not already define.

Contrast (checked by `scripts/contrast.py`): `--fg` and `--fg-muted` on `--bg` and `--bg-elev` ≥ 4.5:1 in both themes; `--accent`, `--ok`, `--warn`, `--danger` on their soft fills ≥ 3:1 as node borders and ≥ 4.5:1 as text where used as text.

## Surfaces and shape

Two layers only. Structure (header, inspector) is `--bg-elev` separated by a 1px `--line` hairline, never a shadow. Floating chrome over the canvas (level control, search, zoom group, tooltip, toast) is a translucent material (`--chrome` with backdrop blur) with one soft offset shadow (`--shadow-float`), because it sits above content and must read as above it. One radius scale: controls 8px, nodes 10px, groups and floating chrome 14px. Segmented controls carry the selected segment on `--bg-elev` inside a `--bg-inset` track. No nested cards: a group box in the canvas is the only container inside the canvas, and the inspector uses spacing and hairlines, not boxes.

## Spacing

4px base. Controls 8px vertical, 12px horizontal. Inspector sections separated by 24px, items by 8px. Header 16px padding. More space above a heading than below it.

## Diagram marks

- Node: fill and stroke from its kind; name in `--font-ui` weight 600; responsibility below in `--fg-muted` at level 2 and up; file path in `--font-data` at level 3.
- Status: verified solid border, inferred dashed, unknown dotted and 70% opacity.
- Edge: orthogonal route from ELK, 1.5px, arrowhead filled, color from kind; event edges dashed, error edges dotted. Label in `--font-data` 12px, horizontal, on a `--bg-elev` plate with a `--line` border, placed inline on the edge by ELK so it never overlaps a node or another label.
- Group: `--n-group-fill` with `--line` border, label top-left in `--fs-xs` caps.
- Selected: 2px `--accent` border plus a soft 6px ring at 22% opacity. Hover: stroke thickens to 1.5px, neighborhood keeps full opacity, everything else drops to 16%.
- Legend doubles as the kind filter: each kind row shows its count and toggles visibility; edge and status rows are informational.

## Levels of information

1. Map: names, groups, edges without labels.
2. Context: responsibilities on nodes, labels on edges. Default.
3. Details: file paths on nodes, step numbers, status marks. The inspector always shows everything for the selected node.

Nothing essential hides behind a click: the default level shows every responsibility and every edge label.

## Motion

One ease (`--ease`, an ease-out) and three durations: `--d-fast` 120ms for hover, press and selection; `--d-base` 200ms for content swaps, theme change and fades; `--d-slow` 320ms for nodes gliding to a new layout and for programmatic zoom or fit. A re-layout keeps every node on screen and glides it from its previous place (FLIP) while edges and labels fade in, so the reader never loses the node they were looking at. Wheel zoom and drag track the pointer 1:1 with no easing. Press states scale to 0.97. Nothing moves on its own. `prefers-reduced-motion` sets the durations to zero; `prefers-reduced-transparency` makes the floating chrome opaque.

## Theme

Light is the base. Dark redefines the same tokens (not an inversion: fills get darker and less saturated, strokes get lighter and more saturated, accent shifts to a lighter blue so it stays readable on dark). The page follows the system preference until the viewer picks a theme; the pick is stored in `localStorage` under `vt-theme` when storage is available and applied on load before first paint. The canvas restyles on theme change.

## Copy

Controls name their action ("Ajustar", "Isolar vizinhança"). Section labels name content ("Sai para", "Recebe de", "Evidência"). No instructions about how to use the page; the first inspector state summarizes the view instead.
