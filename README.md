# visual-thinking

Agent skill: turn explanations, architectures, processes, ideas, comparisons and data into standalone, explorable HTML pages. Loads when the user asks to draw ("desenhe", "faz um desenho", "compare visualmente", "mostre a evolução", "estou com preguiça de ler") or when a visual would replace several paragraphs of prose.

The skill is harness-neutral. Any agent that can read these Markdown files, write a JSON scene and run (or imitate) a one-line Python build produces the same page; publishing, sending or opening the page uses whatever tool the harness has, as described in `formats.md`. The page itself depends on nothing but two pinned CDN libraries (d3, elkjs) and Google Fonts.

Files:

- `SKILL.md`: when to draw, when not to, the intent → structure → strategy decision, five modes, how to build and deliver, output contract.
- `strategy.md`: the visual decision layer: intents, information structures, strategies, anti-choices, when to ask.
- `formats.md`: the templates, the scene schema, what every block shows at each information level, delivery per tool.
- `design.md`: the design system: type, semantic color, surfaces, information architecture per block, data and diagram marks, motion, responsive rules, theme.
- `examples.md`: generic versus annotated versions of the same diagrams.
- `templates/canvas.html`: the default runtime. Composable scene of blocks (charts with scale, axis, series, marks, legend, reference lines, annotations and tooltips; matrix, cards, timeline, steps, tree, mindmap, quadrant, spectrum, cycle, funnel, venn, kpi, callout, free canvas, graph with ELK layout and three levels), views, one inspector per block, computed legend, search, pan, zoom and pinch, theme.
- `templates/svg.html`: composed SVG for exact placements, with tooltip, inspector and theme toggle.
- `templates/mermaid.html`: Mermaid viewer themed from the same tokens.
- `templates/_tokens.css`, `scripts/sync-tokens.py`, `scripts/contrast.py`: the token source and its checks.
- `scripts/build-scene.py`: injects a scene into the template and wraps it as a standalone document (`--fragment` for publish tools that add their own skeleton). `scripts/build-examples.sh` rebuilds the examples.
- `examples/`: ten scenes, ten different pictures: a three-process architecture, three databases compared, a time series, a product timeline, an OAuth PKCE flow, a metrics dashboard, a concept map, a quantitative comparison, a monorepo hierarchy, a free explanation of a CDN.
- `tests/`: scenarios and results from the skill's TDD loop.

Install: point the agent's skills directory at this folder. Examples:

```bash
# Claude Code and OpenCode (both scan ~/.agents/skills; Claude Code also scans ~/.claude/skills)
ln -sfn "$PWD" ~/.agents/skills/visual-thinking && ln -sfn ../../.agents/skills/visual-thinking ~/.claude/skills/visual-thinking
```

```bash
# any other agent: copy or link the folder where it looks for skills, or paste SKILL.md into its instructions
ln -sfn "$PWD" ~/.config/<agent>/skills/visual-thinking
```

Validation: built with the Superpowers writing-skills loop (baseline versus with-skill subagents), browser checks of every example in light and dark, at 1400px and 375px, with real pointer clicks on nodes, edges, groups, cells, points and legend rows; the Impeccable detector (remaining findings are cross-theme false positives); `scripts/contrast.py` on 54 token pairs. See `tests/README.md`.
