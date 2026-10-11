# Visual strategy: from intent to blocks

The pipeline the agent runs before drawing anything:

```
intent  →  information structure  →  visual strategy  →  blocks and marks  →  layout  →  tokens  →  render
```

The agent reasons through the first three columns; the templates own the last four. Nothing here matches words in the prompt; it classifies what the information *is*.

## 1. Read the intent

Ask which of these the user needs. Several may apply; pick the primary one and let the others shape secondary blocks.

| Intent | The user wants to | Typical words |
|---|---|---|
| Compare | choose between or tell apart options | compare, versus, diferença, qual é melhor, prós e contras |
| Trend | see change over time | evolução, crescimento, ao longo, histórico |
| Proportion | see parts of a whole | fatia, participação, percentual, composição |
| Magnitude | see which is bigger and by how much | quanto, maior, ranking, top |
| Distribution | see spread, typical value, outliers | distribuição, variação, p95, mediana |
| Relationship | see how things connect or depend | relação, depende, conecta, integra, arquitetura |
| Sequence | see what happens in which order | fluxo, passo a passo, como funciona, request |
| Hierarchy | see containment or ownership | estrutura, organização, dentro de, árvore |
| Position | see where things sit on two criteria | onde se encaixa, mapa, quadrante |
| Cause and effect | see what leads to what | por que, causa, consequência, impacto |
| Lifecycle | see states and transitions of one thing | estados, ciclo de vida, máquina de estados |
| Spatial exploration | organize loose ideas | organize, mapa mental, ideias |
| Change | see before and after | antes e depois, migração, o que muda |

## 2. Name the information structure

What the data actually is, independent of the chart you have in mind:

- **Entities with attributes**: a few things described by the same properties (qualitative, boolean, quantitative).
- **Ordered observations**: values indexed by time or by an ordered category.
- **Part-to-whole**: values that sum to a meaningful total.
- **Samples**: many values of one measure.
- **Pairs of measures**: each item has two numbers.
- **Nodes and edges**: things and typed connections, possibly inside boundaries.
- **Steps**: ordered actions, maybe with decisions and exits.
- **Tree**: parent and children.
- **States and transitions**.
- **Events in time**: dated points, maybe periods.
- **Options with arguments**: for and against each.
- **Loose concepts**: items with weak or many-to-many relations.

## 3. Choose the visual strategy

| Intent + structure | Strategy | Blocks (canvas.html) or template |
|---|---|---|
| Compare + entities with attributes | Comparison matrix: rows are attributes, columns are options; numbers get inline bars; best per row marked | `matrix`, often plus a `callout` naming the structural difference |
| Compare + options with arguments | Parallel columns with + and − points, same criteria order; add a `spectrum` when the answer is "depends on scale" | `cards` (pros and cons), `spectrum` |
| Compare + two architectures | Same layout for both, differing element marked, criteria table | `svg.html`, or two `graph` blocks in a `row` layout |
| Change (before and after) | Two aligned columns or two graphs, difference marked | `cards` with 2 items, or `row` of two `graph` blocks |
| Trend + ordered observations | Line (plus points when fewer than ~30), area when the quantity is cumulative or a volume; reference line for a target; annotations on the events that explain the shape | `chart` kind `line` or `area` |
| Trend + several series | Multiple lines sharing axes; legend toggles; never more than 6 | `chart` kind `line`, series |
| Magnitude + few values | Horizontal or vertical bars sorted, values written; reference line for a threshold | `chart` kind `bar`, marks `bar`, `label` |
| Magnitude + composition over categories | Stacked bars | `chart` kind `stackedBar` |
| Proportion + 2 to 5 parts | Donut with the total in the center and percentages on the ring | `chart` kind `donut` |
| Proportion + more than 5 parts | Sorted bars with percentages, never a pie | `chart` kind `bar` |
| Distribution + samples | Histogram; dot plot when under ~40 values and the individual values matter | `chart` kind `histogram` or `dot` |
| Relationship + pairs of measures | Scatter, labels when under ~40 points, annotation on outliers | `chart` kind `scatter` |
| Relationship + nodes and edges | Graph with boundaries, typed edges, labels placed by the layout engine; views per process when more than one | `graph`, or `graph.html` for a full explorer |
| Sequence + request through time | Sequence diagram | `mermaid.html` |
| Sequence + stages without branching | Pipeline of numbered steps | `steps` |
| Sequence + decisions and exits | Flow graph with decision nodes | `graph` with `kind: decision` |
| Hierarchy + tree | Tree, top-down for org and containment, left-right for deep trees | `tree` |
| Spatial exploration + loose concepts | Mind map (radial) with the topic in the center | `tree` with `layout: mindmap` |
| Position + two criteria | Quadrant with labeled axes and named quadrants | `quadrant` |
| Position + one criterion | Spectrum with items placed on it | `spectrum` |
| Cause and effect | Left-to-right graph, causes left, effects right, edge labels naming the mechanism | `graph`, direction RIGHT |
| Lifecycle + states | State machine with guards on transitions | `mermaid.html` (stateDiagram) |
| Events in time | Timeline, horizontal up to ~7 events, vertical beyond; periods as bands; milestones larger | `timeline` |
| Cycle + repeated stages | Ring of stages with arrows | `cycle` |
| Funnel + decreasing stages | Funnel with conversion per stage; pyramid for increasing layers | `funnel` |
| Overlap + sets | Venn for 2 or 3 sets only | `venn` |
| Status at a glance | Numbers first: value, delta, sparkline, no tiles | `kpi` |
| Anything the blocks do not fit | Free composition on an 8px grid: shapes, text, arrows, badges, groups | `free`, or `svg.html` |

Compose when one strategy is not enough: a comparison matrix plus a callout; a trend plus a stacked bar of its composition; a tree plus the cycle it runs. Use `layout.type` `stack` for a narrative order, `row` for things to compare side by side, `grid` for several equal panels. Put the answer to the user's question in the first block.

## 4. Anti-choices

- No pie or donut above 5 parts, and none when parts do not sum to a whole.
- No radar unless every axis is quantitative, on the same scale, and the shape itself means something; in practice, a matrix with bars.
- No 3D, no dual y-axes, no truncated axes on bars (bars start at zero).
- No chart for two numbers; write them, or one bar pair at most.
- No boxes and arrows for a comparison.
- No matrix for a trend.
- No stacked bars when the reader needs to compare the non-bottom series.
- No more than six series, six kinds, six colors.
- No block the user did not ask for, invented to fill space.

## 5. When to ask

Draw first when one strategy is clearly right. Ask only when two readings lead to materially different drawings and the context does not settle it:

- "Compare A e B" with no attribute, metric or context in reach: ask what to compare on, in one sentence, offering two likely axes.
- A trend with no data: ask for the numbers or the file; never invent them.
- An architecture with no repo and no description: ask for the components or the repo path.

Otherwise state the assumption in the page subtitle and draw.
