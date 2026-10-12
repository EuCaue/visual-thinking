# Canvas upgrades from VX Work + offline build

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship four canvas/runtime upgrades from the VX Work comparison: a `--self-contained` offline build, packet motion on flow edges, grouped context-menu sections, and fitView padding. The dot-grid background is explicitly dropped (user call).

**Architecture:** All work in `scripts/build-scene.py` (new flag + lib inlining) and `templates/canvas.html` (motion, menu, fit). No dependency added; no behavior change on default builds.

**Tech Stack:** Python 3 stdlib (urllib for fetch + file cache), vanilla JS/SVG, existing test harness style.

**Spec:** `docs/superpowers/specs/2026-10-12-vx-canvas-offline-proposal.md` (items 1, 2, 4, 5; item 3 dot-grid vetoed).

## Global Constraints

- Default builds keep the CDN `<script src>` tags: same size, same behavior.
- `--self-contained` must work offline after build: no `https` request at open time.
- Motion respects `prefers-reduced-motion` (durations zeroed by tokens already; animateMotion must not run there).
- Every task: `python3 tests/test_*.py` all PASS + `sh scripts/build-examples.sh` exit 0 before commit.

## Review Focus

- file:// open of a self-contained page must render graphs/charts identically (verified in browser, not just grep).
- Reduced motion: packet animation must not run when the user disables motion.
- Menu readability: sections must not double-separate (no leading/trailing empty group).

---

### Task 1: `--self-contained` build flag

**Files:** Modify `scripts/build-scene.py`; Test `tests/test_selfcontained.py`.

**Interfaces:**
- Produces: flag usable as `python3 scripts/build-scene.py scene.json out.html --self-contained`; cache dir `.vt-libs/` at repo root (gitignored).

- [ ] **Step 1: Failing test**: build a minimal scene with the flag; assert output contains `d3.min.js` source inline (`var d3=` or `d3.` signature marker) and does NOT contain `<script src="https://cdnjs` and NOT `<script src="https://cdn.jsdelivr`. Also assert `.vt-libs/d3-7.9.0.min.js` exists after build.
- [ ] **Step 2: Run, expect FAIL.**
- [ ] **Step 3: Implement**: parse `--self-contained` from argv; for each CDN URL in canvas.html, fetch once to `.vt-libs/<name>` (stdlib `urllib.request`, 30s timeout), replace `<script src="URL"></script>` with `<script>…file content…</script>`; refetch when the cached file name (with version) changes. On fetch failure: keep CDN tags and print a warning, exit 0 (build must not hard-fail offline).
- [ ] **Step 4: Test PASS; run all suites + examples build.**
- [ ] **Step 5: Commit** `feat(build): --self-contained inlines d3 and elkjs`.

### Task 2: Packet motion on edges

**Files:** Modify `templates/canvas.html`; Test `tests/test_motion.py`.

- [ ] **Step 1: Failing test**: graph scene with `motion: true` → built page contains `animateMotion`; same scene without it → does not.
- [ ] **Step 2: FAIL.**
- [ ] **Step 3: Implement** in `drawGraph`: when `b.motion` and edge kind is `data` or `event`, for each visible edge path add a small circle (r=3, fill `--e-<kind>`) child of an `animateMotion` with `path=<edge d>`, `dur="2.2s"`, `repeatCount="indefinite"`, staggered `begin` (i*0.4s). Skip when `matchMedia('(prefers-reduced-motion: reduce)').matches`. Legend gains one informational row "Pacotes em movimento" when on.
- [ ] **Step 4: PASS + suites.**
- [ ] **Step 5: Commit** `feat(canvas): optional packet motion on flow edges`.

### Task 3: Context menu sections

**Files:** Modify `templates/canvas.html`; extend `tests/test_context_menu.py`.

- [ ] **Step 1: Failing test**: page contains the section separator usage in menu construction (assert `menuSep(` helper exists in source).
- [ ] **Step 2: FAIL.**
- [ ] **Step 3: Implement**: `menuSep(menu)` helper that appends `.sep` only if the menu already has buttons; use it between element actions and navigation actions (edge menu), and before levels/theme in the canvas menu. No double separator (helper checks last child).
- [ ] **Step 4: PASS + suites.**
- [ ] **Step 5: Commit** `feat(canvas): grouped sections in the context menu`.

### Task 4: fitView padding

**Files:** Modify `templates/canvas.html` (`fit()`, `centerBlock()`); Test via browser only (math is trivial).

- [ ] **Step 1: Implement**: effective viewport shrinks by 8% (`vw*0.92`, `vh*0.92`) before the min-ratio math in `fit()` and `centerBlock()`.
- [ ] **Step 2: Browser verify**: `examples/06-dashboard.html` at 1280px has a visible margin on all four sides at fit; `f` key refits identically.
- [ ] **Step 3: Suites + examples build.**
- [ ] **Step 4: Commit** `feat(canvas): padding margin on fit-to-view`.

### Task 5: Docs + final pass

- [ ] **Step 1**: formats.md build line gains `--self-contained`; design.md gains one Motion line for packets; SKILL.md build step mentions the flag; README Limits updated ("offline with the flag").
- [ ] **Step 2**: full suite, examples build, contrast, link check; browser pass on a self-contained build (offline: graphs render, no `https` request in the network tab).
- [ ] **Step 3: Commit** `docs: document self-contained builds and packet motion`.
