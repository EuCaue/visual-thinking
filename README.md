# visual-thinking

Agent skill: turn explanations, architectures, processes, ideas and comparisons into annotated diagrams. Loads when the user asks to draw ("desenhe", "faz um desenho", "compare visualmente", "estou com preguiça de ler") or when a visual would replace several paragraphs of prose.

Files:

- `SKILL.md`: when to draw, when not to, the intent → structure → strategy decision, five modes, output contract.
- `strategy.md`: the visual decision layer: intents, information structures, strategies, anti-choices, when to ask.
- `examples.md`: generic versus annotated versions of the same diagrams.
- `formats.md`: the templates, their slots and schema, delivery per tool, Mermaid conventions.
- `design.md`: the design system (type, semantic color tokens, surfaces, levels of information, theme rules).
- `templates/canvas.html`: the default. Composable scene of blocks (charts with scale, axis, series, marks, legend, reference lines, annotations and tooltips; matrix, cards, timeline, steps, tree, mindmap, quadrant, spectrum, cycle, funnel, venn, kpi, callout, free canvas, graph), views, inspector, pan and zoom, level of detail, theme.
- `examples/showcase.json`: eight prompts, eight pictures; `scripts/build-scene.py` injects a scene into the template.
- `templates/graph.html`: interactive explorer (ELK layout, SVG renderer): views, three information levels, filters, search, inspector with evidence and summary, theme toggle, edge labels placed by the layout engine.
- `templates/svg.html`: composed SVG for comparisons, timelines and annotated screens, with tooltip, inspector and theme toggle.
- `templates/mermaid.html`: Mermaid viewer themed from the same tokens.
- `templates/_tokens.css`, `scripts/sync-tokens.py`, `scripts/contrast.py`: the token source and its checks.

Install (Claude Code, following the `~/.agents/skills` convention used on this machine):

```bash
ln -sfn "$PWD" ~/.agents/skills/visual-thinking && ln -sfn ../../.agents/skills/visual-thinking ~/.claude/skills/visual-thinking
```

Validation: the skill was built with the Superpowers writing-skills loop. Baseline runs without the skill produced ASCII-only, single crowded diagrams and prose that restated the drawing. With the skill, agents investigate the repo, build the interactive HTML page, label edges, tag inferences, deliver a file when the user will share the result, and answer one-hop questions in prose without a diagram.
