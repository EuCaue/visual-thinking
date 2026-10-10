# Test scenarios

Run each prompt in a fresh general-purpose subagent against a small fixture repo (two Node processes: Express API with Stripe webhook, BullMQ worker sending email; Postgres and Redis). Do not name the skill in the prompt; discovery is part of the test. Ask the agent to append "ARQUIVOS LIDOS" and "SKILLS INVOCADAS" to its answer.

| Id | Prompt | Pass when |
|---|---|---|
| A | "Desenhe a arquitetura atual do aplicativo." | Delivers an HTML page built from templates/graph.html (artifact link, sent file, or docs/diagrams path), never a Mermaid or ASCII fence as the deliverable. Reads entry points and imports. Overview holds only processes, stores, externals, entry points. One sub-diagram per process. Verified vs inferred tagged. file:line only from read output. |
| B | Long pasted explanation + "Estou com preguiça de ler, desenhe." | Diagram first, title names the mechanism, at most 3 annotations, one-sentence conclusion or none. |
| C | Two options in context + "Compare essas duas abordagens visualmente. Não quero ler muito." | Page built from templates/svg.html: same layout per option, differing edge marked, criteria table, at most 3 annotations. Opens the real handler in the repo. |
| D | "Qual a diferença entre `express.json()` e `express.raw()`? Por que o webhook usa raw?" | Prose only. No diagram. Skill not loaded. |
| E | "Não entendi, faz um desenho. Quero mostrar pro novato amanhã." | Investigates, draws the sequence, and writes a file the user can share. |
| F | No repo. "Não entendi como funciona OAuth com PKCE. Desenha pra mim." | Explain mode: page with `basis: docs`, mechanism drawn (verifier, challenge, code exchange), uncertain parts tagged, source spec named. No repo reads attempted. |
| G | In the fixture repo. "Planeje a arquitetura de um serviço de notificações (email, push, SMS, retry, preferências) e desenhe. Pode assumir." | Plan mode: `basis: proposal`, assumptions stated, decided vs suggested vs open marked, trade-offs in annotations, reuses the repo's real Redis/BullMQ and Postgres. |

Open every delivered page in a browser in light and dark, confirm it renders, that a node click fills the inspector, and that the page was not restyled (tokens block untouched). Validate every Mermaid source by rendering it (a page importing `mermaid.esm.min.mjs` and calling `mermaid.parse` on each block is enough).

## Results, 2026-10-10

Baseline (no skill): A, B, E used ASCII in a code fence; A put the whole system in one drawing and repeated it in prose; C wrote three paragraphs after "não quero ler muito" and did not open the repo.

With the skill: A, B, C, E loaded the skill on their own and passed the contract. D answered in prose without loading the skill. Two refactor rounds were needed: A kept helper modules in the overview until the overview rule became two separate triggers with process-level edges; E told the user to paste the block somewhere until file delivery became a conditional on the user saying they will share it. One generated block broke on a `;` inside a sequence message; formats.md now lists it.

## Results, 2026-10-10, design-system evolution

RED2 audit of the first templates: system font, ad hoc tints, static 12-row legend, filler "how to use" copy, no theme toggle, one information level, no views, no SVG template. Built: semantic tokens (`templates/_tokens.css`, 42 contrast pairs pass in both themes), explorer with views, three levels, filters, inspector with evidence, theme cycle persisted in `localStorage`, composed SVG template, themed Mermaid viewer. Impeccable detector run; remaining findings are cross-theme false positives (dark text token against light fill).

With the evolved skill, subagents: A built one page with three views (verified in a browser: both themes, inspector fills, no console errors); C built the comparison from the SVG template, tokens untouched; B summarized a pasted text as a sequence; F explained PKCE with RFC references and one tagged inference; G planned a notification service with `basis: proposal`, assumptions stated, open points marked, repo components reused. Token block intact in all six pages. ELK crossing options (`thoroughness`, `TWO_SIDED` greedy switch, `GREEDY_MODEL_ORDER`) were added after G's overview showed crossings.
