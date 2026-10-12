# visual-thinking

Agent skill: turn explanations, architectures, processes, ideas, comparisons and data into standalone, explorable HTML pages. Loads when the user asks to draw ("desenhe", "faz um desenho", "compare visualmente", "mostre a evolução", "estou com preguiça de ler") or when a visual would replace several paragraphs of prose.

The skill is harness-neutral. Any agent that can read these Markdown files, write a JSON scene and run (or imitate) a one-line Python build produces the same page; publishing, sending or opening the page uses whatever tool the harness has, as described in `formats.md`. The page itself depends on nothing but two pinned CDN libraries (d3, elkjs); type is the system font stack, so nothing to fetch offline but those two.

Files:

- `SKILL.md`: when to draw, when not to, a fast intent → block lookup, seven modes (sketch, explain, document, plan, compare, summarize, decide), how to build and deliver, output contract.
- `strategy.md`: the deep reference for borderline choices: intents, information structures, strategies, compositions, anti-choices, when to ask. Most requests use the lookup table in `SKILL.md` alone.
- `formats.md`: the templates, the scene schema, what every block shows at each information level, delivery per tool.
- `design.md`: the design system: type, semantic color, surfaces, information architecture per block, data and diagram marks, motion, responsive rules, theme.
- `examples.md`: generic versus annotated versions of the same diagrams.
- `templates/canvas.html`: the default runtime. Composable scene of blocks (charts with scale, axis, series, marks, legend, reference lines, annotations and tooltips, including tornado sensitivity charts; matrix, weighted decision matrices with sliders and vetoes, cards, timeline, steps, tree, mindmap, quadrant, spectrum, cycle, funnel, venn, kpi, callout, free canvas with image and video elements, graph with ELK layout and three levels, decision nodes with consequence paths), views with scenario toggles, one inspector per block, computed legend, search, right-click menu, pan, zoom and pinch, theme.
- `templates/svg.html`: composed SVG for exact placements, with tooltip, inspector and theme toggle.
- `templates/mermaid.html`: Mermaid viewer themed from the same tokens.
- `templates/_tokens.css`, `scripts/sync-tokens.py`, `scripts/contrast.py`: the token source and its checks.
- `scripts/build-scene.py`: validates the scene, then injects it into the template and wraps it as a standalone document (`--fragment` for publish tools that add their own skeleton, `--validate-only` to check without writing). `scripts/build-examples.sh` rebuilds the examples.
- `examples/`: twelve scenes, twelve different pictures: a three-process architecture, three databases compared, a time series, a product timeline, an OAuth PKCE flow, a metrics dashboard, a concept map, a quantitative comparison, a monorepo hierarchy, a free explanation of a CDN, an architectural decision with sensitivity analysis, a migration scenario and consequence map.
- `tests/`: scenarios and results from the skill's TDD loop, plus regression tests for the validator and every canvas feature (decision, tornado, scenarios, context menu, text guards, media).

Install: point the agent's skills directory at this folder. Examples:

```bash
# any agent with the skills CLI (lists on skills.sh via install telemetry)
npx skills add EuCaue/visual-thinking
```

```bash
# Claude Code and OpenCode (both scan ~/.agents/skills; Claude Code also scans ~/.claude/skills)
ln -sfn "$PWD" ~/.agents/skills/visual-thinking && ln -sfn ../../.agents/skills/visual-thinking ~/.claude/skills/visual-thinking
```

```bash
# any other agent: copy or link the folder where it looks for skills, or paste SKILL.md into its instructions
ln -sfn "$PWD" ~/.config/<agent>/skills/visual-thinking
```

Validation: built with the Superpowers writing-skills loop (baseline versus with-skill subagents), browser checks of every example in light and dark, at 1400px and 375px, with real pointer clicks on nodes, edges, groups, cells, points and legend rows; the Impeccable detector (remaining findings are cross-theme false positives); `scripts/contrast.py` on 54 token pairs. See `tests/README.md`.
