# Docs Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every public-facing document of `visual-thinking` truthful against the implementation, scannable, and ready for a public GitHub debut, without changing skill behavior.

**Architecture:** Docs-only change on top of `master`. Fix measured falsehoods first (fonts, `preset: risk`, stale counts), then rewrite README, extend `design.md` for the new UI, add the minimum GitHub presentation files, and finish with a mechanical verification pass (links, commands, counts, full test suite).

**Tech Stack:** Markdown, `gh` CLI for repo settings, existing `scripts/` checks for proof.

**Spec:** The user's docs-review brief in session (README scope, `/docs` scope, skill-docs scope, GitHub scope, writing-quality bar). No separate spec file; the audit below is the source of truth.

## Audit findings (evidence, not opinion)

1. `formats.md:3,18` + `README.md:5` claim system font stack and "fully self-contained offline". Reality: `templates/canvas.html:4-5,20-21`, `templates/_tokens.css:6-7`, `templates/svg.html:4-5,18-19` load IBM Plex Sans/Mono from Google Fonts with system fallbacks. Offline the page still renders (fallback fonts); only charts/graphs/trees need the d3/elkjs CDNs (`cdn.jsdelivr.net/npm/elkjs@0.9.3`, `cdnjs.cloudflare.com/ajax/libs/d3/7.9.0`). Fix docs to match implementation; do not touch behavior.
2. `strategy.md:69` prescribes ``quadrant`` with `preset: risk`. `grep -n preset templates/canvas.html` returns nothing: the field does not exist and is silently ignored. Fix the row, not the renderer.
3. `SKILL.md:89` says "ten prompts, ten different pictures". `ls examples/*.json` counts 12. Fix the count.
4. `design.md` has no sections for the shipped UI: decision matrix, tornado chart, scenarios bar, right-click menu (`vt-menu`, 6 occurrences in `canvas.html`), `image`/`video` free elements, linkified source URLs (`linkUrls`, 2 occurrences). Add short token-focused rows; do not rewrite existing sections. Note: the file carries uncommitted WIP from another effort (font table hunk, `git diff design.md`); the font-row fix below overlaps it — keep their size text, change only the Face column back to Plex to match the implementation.
5. No `LICENSE`, no `CONTRIBUTING`, no `.github/`, no `.gitignore`. Repo is currently PRIVATE (`gh repo view --json visibility`); topics/description apply whenever it goes public. Recommend MIT (permissive, standard for skills) — confirm at plan review.
6. `tests/*.py` count is 7, `examples/*.json` count is 12, `scripts/contrast.py` prints 54 `ok` lines. README's "54 token pairs" is correct.
7. Untracked session scratch `PROGRESS.md` sits in the repo root. Delete it (superseded by `docs/superpowers/plans/`); add it to `.gitignore` so it never ships.
8. `docs/` holds only internal `docs/superpowers/{plans,specs}`. No public `/docs` tree exists and none is needed: the five root Markdown files are the whole manual. Do not create one.

## Global Constraints

- Zero behavior change: no edits to `templates/`, `scripts/`, `examples/`, or `tests/` in this plan.
- Every factual claim must be verifiable by `grep`, a listed command's real output, or a file that exists at the cited path.
- Docs voice: plain sentences, no marketing adjectives, no AI tells (no em-dash chains, no bold-everything lists, no "not X but Y" contrasts).
- Existing validator wording stays the source for rule statements (`weightBasis`, `vetoBelow`, duplicate venn/arrows, media `src`).

## Review Focus

- Offline behavior: a reader on disk without network must get exactly what the docs promise (fallback fonts render, charts/graphs/trees show the one-line message). Pinned by Task 1 wording + Task 5 offline re-read.
- `preset` remnants: no occurrence of the word `preset` may remain in `strategy.md`, `formats.md`, or `examples/` after Task 1. Pinned by `grep -rn preset` returning empty in the verification step.
- Counts: examples (12), test files (7), contrast pairs (54), block types (18 in `TYPES`), chart kinds (9 in `KINDS`). Pinned by the count commands in Task 5.
- Install commands: `npx skills add EuCaue/visual-thinking` was verified end-to-end on 2026-10-12 (clean-dir install produced `.agents/skills/visual-thinking/SKILL.md`); the `ln -sfn` commands match the live symlinks in `~/.agents/skills` and `~/.claude/skills`. Pinned by re-running the clean-dir install in Task 5.
- SKILL.md validator claims ("dangling ids, unlabeled edges, unknown kinds, empty groups, out-of-range values"): each noun must match a real validator message. Pinned by the `grep` step in Task 5.

---

### Task 1: Truth fixes (fonts, preset, counts)

**Files:**
- Modify: `formats.md:3,18`
- Modify: `README.md:5`
- Modify: `design.md` font table Face column only
- Modify: `strategy.md:69`
- Modify: `SKILL.md:89`

**Interfaces:**
- Consumes: implementation facts from the audit (Plex link/tags above, `grep preset` empty, 12 examples).
- Produces: wording later tasks link to and must not contradict.

- [ ] **Step 1: Fix `formats.md` font/offline claims**

Replace the parenthetical in line 3 `(system-ui for UI, monospace for data)` with `(IBM Plex Sans/Mono from Google Fonts, system stacks as fallback)`. Replace line 18's `No fonts, no build step: type is the system stack, so the page is fully self-contained offline.` with `No build step. Type loads IBM Plex from Google Fonts and falls back to the system stack offline; charts, trees and graphs additionally need the two CDN libraries, and show a one-line message without them.`

- [ ] **Step 2: Fix `README.md:5` the same way**

Replace `type is the system font stack, so nothing to fetch offline but those two` with `type loads IBM Plex from Google Fonts (system-stack fallback offline), so the CDNs stay the only hard network dependency`.

- [ ] **Step 3: Fix `design.md` Face column to Plex**

In the Type table only, set UI Face to `IBM Plex Sans (Google Fonts), fallback system-ui` and data Face to `IBM Plex Mono, fallback ui-monospace`. Keep the other effort's size text untouched.

- [ ] **Step 4: Drop the nonexistent `preset: risk`**

In `strategy.md:69`, replace ``quadrant`` with `preset: risk`` with ``quadrant`` with axes labeled probability and impact``. Then run `grep -rn "preset" SKILL.md strategy.md formats.md examples/ ; echo CLEAN` and require empty output before `CLEAN`.

- [ ] **Step 5: Fix the stale count**

In `SKILL.md:89`, replace `ten prompts, ten different pictures` with `twelve scenes, twelve different pictures`.

- [ ] **Step 6: Commit**

```bash
git add formats.md README.md design.md strategy.md SKILL.md
git commit -m "docs: match font, preset and count claims to the implementation"
```

---

### Task 2: Rewrite README

**Files:**
- Modify: `README.md` (keep the Install `npx` + symlink blocks and the Validation paragraph's verified numbers, reworded only if a check in Task 5 disproves them)

**Interfaces:**
- Consumes: Task 1 wording (fonts, counts), block inventory (18 types in `TYPES`, 9 chart kinds in `KINDS`), skill modes (7 in `SKILL.md`), install proof (Review Focus).
- Produces: the public front door every other doc links back to.

- [ ] **Step 1: Rewrite `README.md` with exactly these sections, in order**

`# visual-thinking` + one-paragraph what (skill turning explanations/architectures/data into standalone explorable HTML) → `## Why` (problem: prose buries structure; who: agents and the humans they draw for) → `## How it works` (intent → scene JSON → template renders; 4 lines max plus the minimal scene shape pointer to `formats.md`) → `## What it can draw` (compact table grouped by need: compare/decide/change/relate/sequence/position, naming the block for each; no more than 12 rows) → `## Install` (keep both existing blocks verbatim) → `## Use` (one minimal end-to-end: write scene, build command, open; link `SKILL.md` for the full contract) → `## Project layout` (one line per root entry, reuse the existing Files list, updated) → `## Limits` (CDN network need per formats.md:18 post-Task-1, 12-node graph guidance, no invented data rule) → `## Contributing` (link `CONTRIBUTING.md`) → `## Docs` (links to the five root files). No badges (no CI to back them), no screenshots (pages are interactive; link two example scenes by path instead).

- [ ] **Step 2: Verify every claim**

Run `ls examples/*.json | wc -l` (12), `ls tests/*.py | wc -l` (7), `python3 scripts/build-scene.py examples/01-arquitetura.json --validate-only`. Any number that disagrees gets fixed in the text, not the other way round.

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: rewrite README as the public front door"
```

---

### Task 3: Extend `design.md` for the shipped UI

**Files:**
- Modify: `design.md` (append-only: new rows and one subsection; never rewrite existing sections)

**Interfaces:**
- Consumes: token names from `templates/_tokens.css`, control strings from `templates/canvas.html` (`Inspecionar`, `Isolar vizinhança`, `Mostrar tudo`, `Ver resumo do bloco`, `Ajustar à tela`, `Buscar no desenho`, `Nível Mapa/Contexto/Detalhes`, `Alternar tema`).
- Produces: design rationale for UI the skill docs already promise.

- [ ] **Step 1: Add the new blocks to Data marks**

Append three bullets: decision matrix (summary row with weighted total, leader accent, veto badges in `--danger`, reversibility tags, weight sliders reusing `--accent`); tornado (bidirectional bars from a dashed baseline, `--warn` low vs `--accent` high, value labels dropped when they would collide); scenarios bar (segmented controls reusing `.seg` styles above the canvas).

- [ ] **Step 2: Add context menu + media to Surfaces/Copy**

Append to Surfaces: right-click menu reuses floating-chrome material (`--chrome`, `--shadow-float`, 14px radius) with row-style items. Extend the Copy controls list with the exact strings above. Add one line: `image`/`video` free elements render the remote file in place with native video controls; source URLs render as `--accent` links in the inspector.

- [ ] **Step 3: Commit**

```bash
git add design.md
git commit -m "docs: cover decision, tornado, scenarios, menu and media in design.md"
```

---

### Task 4: GitHub presentation files + repo hygiene

**Files:**
- Create: `LICENSE` (MIT text, only after the user confirms MIT at plan review)
- Create: `CONTRIBUTING.md`
- Create: `.github/ISSUE_TEMPLATE/bug.md`
- Create: `.gitignore`
- Delete: untracked `PROGRESS.md` (`rm PROGRESS.md`; it is session scratch, content already lives in `docs/superpowers/plans/`)
- Repo settings via `gh` (no file): topics + homepage leave empty until public; confirm description stays `Agent skill: turn explanations, architectures and data into standalone explorable HTML pages`

**Interfaces:**
- Consumes: repo state (`gh repo view --json`), existing check commands for CONTRIBUTING to reference.
- Produces: a repo that can go public without a second pass.

- [ ] **Step 1: Write `LICENSE`, `CONTRIBUTING.md`, bug template, `.gitignore`**

`CONTRIBUTING.md` contents, short: how to add an example (scene JSON + `sh scripts/build-examples.sh`), the mandatory gates before a PR (`python3 tests/test_*.py` all PASS, `scripts/contrast.py` all `ok`, no validator warnings on new scenes), docs rule (every claim must grep true). Bug template fields: scene JSON (minimal), expected vs actual, light/dark, viewport width. `.gitignore`: `.ruff_cache/`, `.superpowers/`, `PROGRESS.md`, `*.log`, `/tmp/` leftovers stay out of the tree anyway — keep the file to those four lines.

- [ ] **Step 2: Apply repo settings**

Run `gh repo edit EuCaue/visual-thinking --add-topic ai-skills --add-topic agent-skills --add-topic data-visualization --add-topic diagrams --add-topic d3js`. Do not set a homepage (no hosted demo while private). Record the exact command + output in the commit message body? No — run it, then verify with `gh repo view --json repositoryTopics`.

- [ ] **Step 3: Commit**

```bash
git add LICENSE CONTRIBUTING.md .github/ISSUE_TEMPLATE/bug.md .gitignore
git commit -m "docs: add license, contributing guide, issue template, gitignore"
```

---

### Task 5: Final verification pass

**Files:**
- Modify: none, unless the pass finds a discrepancy (then fix the doc, never the code, and amend the owning task's commit).

**Interfaces:**
- Consumes: every file Tasks 1–4 touched.
- Produces: the release-ready tree.

- [ ] **Step 1: Links**

Run `python3 -c` over every `.md` file collecting `[t](target)` targets ending in `.md` or `#anchor`; assert each target file exists. Expected: zero missing.

- [ ] **Step 2: Commands**

Run each command a doc tells the reader to run: `python3 scripts/build-scene.py --help`-equivalent usage line, one `--validate-only` build, `sh scripts/build-examples.sh`, `python3 scripts/contrast.py | grep -vc ok` expecting `0`, `python3 scripts/sync-tokens.py --check`. Expected: all exit 0 (grep counts as documented).

- [ ] **Step 3: Noun-match SKILL validator claims**

`grep -n "dangling\|unlabeled\|unknown kind\|empty group\|out-of-range\|out of range" scripts/build-scene.py` must hit at least one line per noun in SKILL.md's build step. Fix the sentence if a noun misses.

- [ ] **Step 4: Full suite + clean tree**

Run all 7 `tests/test_*.py` (PASS each), confirm `git status --short` shows only intended files, and confirm no `preset` remnants (`grep -rn preset` over docs+examples returns empty).

- [ ] **Step 5: Commit only if Step 1–4 changed a doc**

Otherwise finish with no commit and report the pass.
