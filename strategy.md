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
| Evaluate | weigh options on weighted criteria | qual escolher, vale a pena, ponderar, critérios, pesos |
| Contrast | compare two options head to head | A vs B, bilateral, lado a lado |
| Consequences | see what follows a choice, orders of effect | e se, consequências, impacto, 2ª ordem |
| Risk | see what can go wrong and how likely | risco, probabilidade, pior caso |
| Trade-offs | see what each option buys at what cost | trade-off, abre mão, ao custo de |
| Prioritize | rank items by importance and effort | priorizar, roadmap, o que primeiro |
| Scenarios | compare futures under different hypotheses | cenário pessimista/otimista, e se o volume dobrar |
| Robustness | see what flips the answer | sensibilidade, ponto de virada, e se o peso mudar |
| Diagnose | find what drives an outcome | por que perdemos, causa raiz, gargalo |
| Dependencies | navigate what depends on what | depende de, bloqueia, pré-requisito |

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
- **Tables and keys**: records with fields that reference each other.
- **Flows of quantity**: amounts that split and merge between stages and keep their total.
- **Values on a grid**: one measure for each pair of two categories (day × hour, team × week).
- **Tasks in time**: activities with start, end and dependencies.

## 3. Choose the visual strategy

| Intent + structure | Strategy | Blocks (canvas.html) or template |
|---|---|---|
| Compare + entities with attributes | Comparison matrix: rows are attributes, columns are options; numbers get inline bars; best per row marked | `matrix`, often plus a `callout` naming the structural difference |
| Compare + options with arguments | Parallel columns with + and − points, same criteria order; add a `spectrum` when the answer is "depends on scale" | `cards` (pros and cons), `spectrum` |
| Evaluate + options with scores | Weighted matrix: rows are criteria with explicit weights and a stated `weightBasis`, columns are options, cells carry score plus raw value and note; summary row with the weighted total, leader highlighted, vetoes disqualifying | `decision` (`mode: weighted`, `vetoBelow`, `reversibility` tags) |
| Contrast + two options | Bilateral `decision` with two options, or paired trade-off cards ("buys X at the cost of Y") | `decision`, `cards` |
| Robustness + weighted scores | Tornado sorted by swing: what moves the answer and by how much | `chart` kind `tornado` (`baseline`, `low`/`high` per factor) |
| Consequences + a choice | Decision node with downstream consequence paths in 1st/2nd/3rd order, polarity and probability on edges; click isolates one path | `graph` with `kind: decision`, `consequence: {order, polarity}`, `prob` |
| Scenarios + hypotheses | Same view under named hypotheses; chips swap the data without reload | view-level `scenarios` (`controls` + `overrides`) |
| Risk + likelihood and impact | Position items on probability vs impact; tornado for the drivers | `quadrant` with axes labeled probability and impact, `chart` kind `tornado` |
| Prioritize + importance and effort | Ranked `decision` with two criteria, or quadrant with quick wins named | `decision`, `quadrant` |
| Compare + two architectures | Same layout for both, differing element marked, criteria table | `svg.html`, or two `graph` blocks in a `row` layout |
| Change (before and after) | Two aligned columns or two graphs, difference marked | `cards` with 2 items, or `row` of two `graph` blocks |
| Trend + ordered observations | Line (plus points when fewer than ~30), area when the quantity is cumulative or a volume; reference line for a target; annotations on the events that explain the shape | `chart` kind `line` or `area` |
| Trend + several series | Multiple lines sharing axes; legend toggles; never more than 6 | `chart` kind `line`, series |
| Magnitude + few values | Horizontal or vertical bars sorted, values written; reference line for a threshold | `chart` kind `bar`, marks `bar`, `label` |
| Magnitude + composition over categories | Stacked bars | `chart` kind `stackedBar` |
| Proportion + 2 to 5 parts | Donut with the total in the center and percentages on the ring | `chart` kind `donut` |
| Proportion + more than 5 parts | Sorted bars with percentages, never a pie | `chart` kind `bar` |
| Proportion + parts that nest | Treemap by area, hue per top-level part; sunburst when the levels matter more than the sizes | `treemap` (`layout: sunburst`) |
| Flow of quantity + stages | Sankey: band width is the amount, the total stays visible at each stage | `sankey` |
| Values on a grid | Heatmap: one hue, intensity is the value, numbers in the cells when they fit; diverging hues only around a meaningful middle | `heatmap` |
| Rhythm over days | Calendar heatmap, weeks as columns | `heatmap` with `calendar: true` |
| Values by place | Choropleth of the regions, one hue; points for sites | `map` |
| Explain code | The few lines that matter, highlighted, each with its note | `code` |
| Explain a formula | The formula once, its symbols named in the text | `math` |
| Distribution + samples | Histogram; dot plot when under ~40 values and the individual values matter | `chart` kind `histogram` or `dot` |
| Relationship + pairs of measures | Scatter, labels when under ~40 points, annotation on outliers | `chart` kind `scatter` |
| Relationship + nodes and edges | Graph with boundaries, typed edges, labels placed by the layout engine; views per process when more than one | `graph`, one view per process |
| Structure + tables and keys | Entity model: tables with fields, PK/FK marks, relations with cardinality; one view per domain past 12 tables | `entity` |
| Change + two versions of a system | One graph or model with added, changed and removed marked in place | `scene-diff.py` over two scenes |
| Sequence + request through time | Sequence diagram | `mermaid.html` |
| Sequence + stages without branching | Pipeline of numbered steps | `steps` |
| Sequence + decisions and exits | Flow graph with decision nodes | `graph` with `kind: decision` |
| Hierarchy + tree | Tree, top-down for org and containment, left-right for deep trees | `tree` |
| Spatial exploration + loose concepts | Mind map (radial) with the topic in the center | `tree` with `layout: mindmap` |
| Position + two criteria | Quadrant with labeled axes and named quadrants | `quadrant` |
| Position + one criterion | Spectrum with items placed on it | `spectrum` |
| Cause and effect | Left-to-right graph, causes left, effects right, edge labels naming the mechanism | `graph`, direction RIGHT |
| Lifecycle + states | State machine with guards on transitions | `mermaid.html` (stateDiagram) |
| Plan + tasks in time | Gantt: bars on a time axis, dependencies as arrows, milestones, today line, critical path in red | `gantt` |
| Events in time | Timeline, horizontal up to ~7 events, vertical beyond; periods as bands; milestones larger | `timeline` |
| Cycle + repeated stages | Ring of stages with arrows | `cycle` |
| Funnel + decreasing stages | Funnel with conversion per stage; pyramid for increasing layers | `funnel` |
| Overlap + sets | Venn for 2 or 3 sets only | `venn` |
| Status at a glance | Numbers first: value, delta, sparkline, no tiles | `kpi` |
| Show + photo, screenshot or clip | Image or video pinned on the grid with caption and a source link | `free` with `image`/`video` elements |
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
- No equal weights by default: unstated relevance is inferred from context and declared in `weightBasis`, never split evenly.
- No isolated pros/cons when the question is a trade-off: pair them ("buys X at the cost of Y").
- No speculation drawn as fact: hypotheses live in `scenarios` controls or are tagged `inferred`/`unknown`, never baked into the base numbers.
- No sankey when the amounts do not add up between stages, and none with cycles; that is a `graph`.
- No treemap for values that do not sum to a whole, and none for negatives.
- No heatmap with diverging colors unless the middle (`mid`) means something (zero, target, average).
- No gantt without dates; an order without dates is `steps`.
- No `entity` for runtime components; tables and keys only. Services and queues are a `graph`.
- No map when place does not change the answer; a sorted bar chart reads faster.
- No sketch style on numbers someone will quote or on a final document.
- No code block longer than the point; 60 lines is already a file, link it instead.

## 5. When to ask

Draw first when one strategy is clearly right. Ask only when two readings lead to materially different drawings and the context does not settle it:

- "Compare A e B" with no attribute, metric or context in reach: ask what to compare on, in one sentence, offering two likely axes.
- A trend with no data: ask for the numbers or the file; never invent them.
- An architecture with no repo and no description: ask for the components or the repo path.

Otherwise state the assumption in the page subtitle and draw.
