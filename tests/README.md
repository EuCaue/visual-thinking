# Test scenarios

Run each prompt in a fresh general-purpose subagent against a small fixture repo (two Node processes: Express API with Stripe webhook, BullMQ worker sending email; Postgres and Redis). Do not name the skill in the prompt; discovery is part of the test. Ask the agent to append "ARQUIVOS LIDOS" and "SKILLS INVOCADAS" to its answer.

| Id | Prompt | Pass when |
|---|---|---|
| A | "Desenhe a arquitetura atual do aplicativo." | Reads entry points and imports. Overview holds only processes, stores, externals, entry points. One sub-diagram per process. Verified vs inferred tagged. file:line only from read output. |
| B | Long pasted explanation + "Estou com preguiça de ler, desenhe." | Diagram first, title names the mechanism, at most 3 annotations, one-sentence conclusion or none. |
| C | Two options in context + "Compare essas duas abordagens visualmente. Não quero ler muito." | Same layout per option, differing edge highlighted, short criteria table, at most 3 annotations. Opens the real handler in the repo. |
| D | "Qual a diferença entre `express.json()` e `express.raw()`? Por que o webhook usa raw?" | Prose only. No diagram. Skill not loaded. |
| E | "Não entendi, faz um desenho. Quero mostrar pro novato amanhã." | Investigates, draws the sequence, and writes a file the user can share. |

Validate every Mermaid block by rendering it (a page importing `mermaid.esm.min.mjs` and calling `mermaid.parse` on each block is enough).

## Results, 2026-10-10

Baseline (no skill): A, B, E used ASCII in a code fence; A put the whole system in one drawing and repeated it in prose; C wrote three paragraphs after "não quero ler muito" and did not open the repo.

With the skill: A, B, C, E loaded the skill on their own and passed the contract. D answered in prose without loading the skill. Two refactor rounds were needed: A kept helper modules in the overview until the overview rule became two separate triggers with process-level edges; E told the user to paste the block somewhere until file delivery became a conditional on the user saying they will share it. One generated block broke on a `;` inside a sequence message; formats.md now lists it.
