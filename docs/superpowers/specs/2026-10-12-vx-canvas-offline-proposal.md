# Proposal: ideas from the VX Work canvas, and an offline build

Investigation note, 2026-10-12. Comparison between the canvas in `/home/caue/code/vx-work`
(web/features/diagrams + web/features/automations, React Flow) and this skill's
runtime (templates/canvas.html, vanilla SVG). Nothing here changes code; each
item carries problem, solution, reference, benefit, cost, risk and a call.

## What the two canvases are

VX Work runs an editable, collaborative drawing surface: people drag cards,
draw edges, and see each other's cursors live. The state is a mutable graph on
a server; React Flow (@xyflow/react 12) owns the viewport, persistence goes
through react-query mutations, and two surfaces (diagrams, automations) share
the same primitives (canvasBackground, GroupPanel, groupBounds, CanvasMenu).

visual-thinking renders a scene that an agent already decided. The JSON is
immutable data, the page is the artifact, ELK places the nodes, and the file
has to open on its own from disk. The two products agree on the vocabulary
(pan, zoom, inspect, isolate) and disagree on who moves what.

That disagreement is the filter for everything below: an idea only travels if
it serves a page nobody edits.

## Findings worth acting on

### 1. Self-contained build (offline)

Problem. Today a built page fetches two scripts at open time: d3 7.9.0
(280KB) and elkjs 0.9.3 (1.6MB, the layout engine behind graph and tree).
Without network, charts, trees and graphs show a one-line message; the rest of
the page still renders, styles and interactions are already inline. mermaid.html
has a third, larger dependency chain (mermaid 11 ESM with dynamic imports).
Fonts were already solved this session: system stacks, zero requests.

Solution. A build flag, `--self-contained`, that downloads the two libraries
once at build time and inlines them as plain `<script>` blocks in the same
order the CDN tags use. No code changes in the runtime; `hasD3`/`hasELK` guards
keep working. The build caches the downloads (`.vt-libs/`) so repeat builds
cost nothing.

Reference. Not from VX Work; theirs is server-fed. The constraint that matters
here is the file:// promise the skill already makes ("works from any static
host"), which inline satisfies and CDN cannot guarantee.

Benefit. The one file the user receives carries the whole experience: graph
layout, charts, zoom, offline, on a plane, via email attachment.

Cost. The page grows from ~190KB to ~2.1MB (inline JS adds nothing, the two
scripts are plain text). Build needs network once. The flag is opt-in; the
default build stays lean.

Risk. A stale cached lib could pin an old version; the cache file stores the
URL with version, so a changed version refetches. Inline scripts disable CSP
on some hosts; the default build keeps the CDN version for those.

Recommendation. Do it. It closes the last real gap between "standalone HTML"
and what the user gets today.

### 2. Packet motion on edges

Problem. An edge says what moves; nothing on screen moves with it. A reader
who never saw the system has to infer flow direction from the arrowhead alone.

Solution. Small packets traveling along an edge, SVG `animateMotion`, on data
and event edges, off by default, one class to turn on per graph block
(`motion: true`). Respect `prefers-reduced-motion` like every other animation.

Reference. VX Work's `flowMotion.ts` carries the exact shape: keyPoints and
keyTimes as a script per direction (forward, backward, both), and a rule worth
keeping: an undirected line carries no packet, because sending something along
it would claim a direction the author did not state.

Benefit. Direction reads without reading. Cheap: no redraw loop, the browser
drives the motion.

Cost. One function and a few CSS lines. Testing it means the two browser
passes (motion on, reduced motion on).

Risk. Pages with many animated edges could get noisy; default off, and the
computed legend can carry the toggle like it does for kinds.

Recommendation. Do it, default off.

### 3. Dot-grid background

Problem. On an empty zoom level the canvas is a flat color; distance and
direction are invisible until content enters the view.

Solution. A repeating dot grid that scales with the zoom and fades below
~0.4 zoom, as one CSS background with two offsets, no DOM nodes.

Reference. VX Work's `canvasBackground.ts`, including the reason it is CSS:
a backdrop must keep up with the drag, and a repeating background moves by
changing one offset. Also their honest postmortem on the three-ways-to-draw-a-
backdrop control they deleted: the backdrop says which way is straight, and
nothing more.

Benefit. Cheap spatial feedback; the field is quiet enough to draw over.

Cost. One function plus a wheel/pan hook updating two CSS variables we already
maintain (tx, ty).

Risk. None found. It is a background; no interaction surface.

Recommendation. Do it.

### 4. Context menu sections

Problem. Our menu grows one flat list per target; on an empty canvas it
already holds five unrelated items (fit, search, three levels, theme).

Solution. Sections with a hairline separator per group of actions, plus an
"add" section is not for us (no authoring on the page); the separator alone
fixes the reading.

Reference. VX Work's `CanvasMenu` types its target and renders `MenuSection`
groups from a shared `ContextMenu` primitive.

Benefit. Scannable menu when it grows past five items.

Cost. One `if` in `menuBtn` and three CSS lines (we already have a `.sep`).

Risk. None.

Recommendation. Do it as part of the next menu touch, not standalone.

### 5. fitView clamps

Problem. Our fit caps zoom at 1.15 and has no padding notion; a dense view
touches the edges of the canvas.

Solution. Add a padding factor (0.08 default) to the fit math and keep the
existing cap; match React Flow's insight that fitView should never zoom in
past 1 (ours allows 1.15, which is fine for reading text, keep it).

Reference. `fitViewOptions={{ padding: 0.3, maxZoom: 1 }}` in both VX Work
surfaces.

Benefit. Nothing clings to the canvas border on small windows.

Cost. Two lines in `fit()`.

Risk. Padding that is too generous shrinks dense diagrams; 0.08 is conservative.

Recommendation. Do it opportunistically.

### 6. Ideas rejected, with the reason

- Collaborative presence, cursors, selection boxes: the page is an artifact,
  not a workspace. No server, no realtime, out of scope forever.
- Drag-to-edit and node persistence: the scene is data an agent owns. An
  editable canvas would fork the truth away from the JSON and break the
  "rebuild from the scene" guarantee. Not now, not with these goals.
- drawingSignature (redraw guard against refetches): we have no refetches;
  the runtime rebuilds only on deliberate events.
- React Flow itself: 12 npm packages, a runtime the build would have to embed,
  and a layout model (user-owned coordinates) we do not have. ELK layered
  placement is the thing that makes agent-authored graphs legible; React Flow
  does not do that job.
- Minimap: our graphs cap at 12 nodes per view by design; the need the
  minimap answers should not exist.

## Offline dependency audit, exact numbers

| Asset | Where | Size | Without network today |
|---|---|---|---|
| d3 7.9.0 | cdnjs, `<script src>` | 280KB | charts show one-line message |
| elkjs 0.9.3 | jsDelivr, `<script src>` | 1.6MB | graph and tree show one-line message |
| mermaid 11.4.1 ESM | jsDelivr, dynamic import (mermaid.html only) | 30KB entry + dynamic imports | viewer does not render |
| fonts | none since `15089ec` | 0 | fine |
| CSS, runtime, icons, data | inline in the file | 0 | fine |

Icons are inline `<symbol>` defs. No dynamic imports in canvas/svg. One
request per library on first open (cached after).

## Order of attack

1. `--self-contained` flag (closes the offline gap; the item that matters).
2. Dot-grid background + fitView padding (small, independent).
3. Packet motion, default off.
4. Menu sections with the next menu change.

Each lands with its own regression test in `tests/` and a build of all 12
examples, in the worktree, never on master directly.
