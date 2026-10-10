# visual-thinking

Agent skill: turn explanations, architectures, processes, ideas and comparisons into annotated diagrams. Loads when the user asks to draw ("desenhe", "faz um desenho", "compare visualmente", "estou com preguiça de ler") or when a visual would replace several paragraphs of prose.

Files:

- `SKILL.md`: when to draw, when not to, how to investigate a repo before drawing it, output contract, visual language.
- `examples.md`: generic versus annotated versions of the same diagrams.
- `formats.md`: Mermaid, D2, Graphviz, SVG, HTML and ASCII notes, and how to detect what renders.

Install (Claude Code, following the `~/.agents/skills` convention used on this machine):

```bash
ln -sfn "$PWD" ~/.agents/skills/visual-thinking && ln -sfn ../../.agents/skills/visual-thinking ~/.claude/skills/visual-thinking
```

Validation: the skill was built with the Superpowers writing-skills loop. Baseline runs without the skill produced ASCII-only, single crowded diagrams and prose that restated the drawing. With the skill, agents investigate the repo, pick Mermaid, label edges, tag inferences, deliver a file when the user will share the result, and answer one-hop questions in prose without a diagram.
