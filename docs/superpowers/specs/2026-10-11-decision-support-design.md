# Especificação de Design: Evolução da Skill Visual Thinking para Comunicação e Tomada de Decisão

**Data:** 2026-10-11  
**Status:** Validado via Brainstorming / Pronto para Planejamento  
**Objetivo:** Evoluir a skill `visual-thinking` de um gerador de explicações visuais estáticas para um framework completo de raciocínio, comunicação visual e suporte à tomada de decisão.

---

## 1. Propósito da Skill

A skill `visual-thinking` transforma ideias, sistemas, processos, trade-offs e escolhas complexas em representações visuais interativas e autocontidas (HTML/SVG/Canvas).
Seu objetivo primário é **reduzir o esforço cognitivo** do usuário. Quando um texto demandaria múltiplos parágrafos para correlacionar opções ou quando a decisão envolve múltiplos critérios concorrentes, a skill projeta a representação visual que melhor externaliza o modelo mental necessário para compreender e decidir.

A visualização não é decorativa: **ela é uma ferramenta de pensamento**. O artefato visual deve ser autossuficiente — um leitor que veja apenas a página gráfica gerada deve ser capaz de compreender o diagnóstico, o modelo de decisão ou o sistema sem depender de explicações paralelas no chat.

---

## 2. Modos de Operação (Taxonomia de Modos)

A skill opera em **7 modos**, ativados pelo contexto da solicitação:

| Modo | Gatilhos típicos | Base conceitual (`basis`) | Comportamento e regras |
|---|---|---|---|
| **Sketch** | "faz um esquema", "desenha aí", ideia rápida | `inferred` / `proposal` | Enxuto: 1 visão, 1–2 blocos. Assume premissas no subtítulo sem interromper com perguntas. |
| **Explain** | "não entendi X", conceito, algoritmo, protocolo | `docs` | Explica mecanismo/conceito a partir de documentação/especificações. Tags explícitas para inferências. |
| **Document** | "arquitetura atual", "como funciona aqui", arquivos do repo | `code` | Investiga o código obrigatoriamente antes de desenhar. Mapeia fronteiras, arquivos e evidências verificadas. |
| **Plan** | "planeje", "proponha arquitetura", "como você faria" | `proposal` | Propõe um caminho arquitetural com itens verificados, inferidos e abertos destacados. |
| **Compare** | "compare A e B", "qual a diferença", antes e depois | `docs` ou `code` | Foco em diferenciação neutra: mesma estrutura para ambos, realce no elemento divergente. |
| **Summarize** | texto colado + "preguiça de ler", "resuma" | `text` | Extrai e projeta estritamente o que o texto afirma, sem alucinar conexões externas. |
| **Decide (Novo)** | "ajuda a decidir", "A ou B?", "trade-offs", "qual é melhor?", "o que acontece se?" | `decision` | **Estrutura a escolha**: explicita alternativas, critérios ponderados, consequências de 1ª/2ª ordem, riscos e reversibilidade. Habilita interatividade (sliders de pesos, toggles de cenários, caminhos de consequência). |

---

## 3. Taxonomia de Intenções e Estruturas Visuais

A pipeline de raciocínio da skill é:
$$\text{Intent} \longrightarrow \text{Estrutura de Informação} \longrightarrow \text{Estratégia Visual} \longrightarrow \text{Blocos e Marcas}$$

### 3.1 Intenções de Compreensão e Explicação (Existentes mantidas)
- **Trend**: Observações ordenadas no tempo $\rightarrow$ `chart` (line, area).
- **Proportion**: Relação parte-todo $\rightarrow$ `chart` (donut até 5 partes, barras ordenadas acima).
- **Magnitude**: Comparação quantitativa de grandezas $\rightarrow$ `chart` (bar horizontal/vertical).
- **Distribution**: Dispersão e densidade $\rightarrow$ `chart` (histogram, dot plot).
- **Relationship / Architecture**: Nós, arestas tipadas e fronteiras $\rightarrow$ `graph`.
- **Sequence**: Passos encadeados lineares ou protocolos $\rightarrow$ `steps` ou `mermaid` (sequenceDiagram).
- **Hierarchy**: Contenção ou subordinação $\rightarrow$ `tree` ou `mindmap`.
- **Position**: Localização em 2 critérios contínuos $\rightarrow$ `quadrant`.
- **Lifecycle**: Estados e transições de uma entidade $\rightarrow$ `mermaid` (stateDiagram).
- **Temporal events**: Marcos e períodos datados $\rightarrow$ `timeline`.

### 3.2 Intenções Decisórias (Novas)

| Sub-intenção decisória | Tipo de decisão | Estrutura de Informação | Estratégia Visual Primária | Bloco / Template |
|---|---|---|---|---|
| **Evaluate** (Avaliação multi-critério) | Multi-alternativas (1 de N) ou critérios ponderados | Alternativas $\times$ Critérios ponderados + notas | Matriz de decisão interativa com pesos deslizantes, pontuação normalizada, veto e ranking | `decision` (novo bloco em `canvas.html`) |
| **Contrast / Bilateral** | Binária (A vs B) | Duas alternativas com vetores de ganho e perda pareados | Comparação bilateral (Butterfly chart ou cards lado a lado com pareamento explícito de trade-off) | `cards` (layout pareado) ou `svg.html` |
| **Explore consequences** | Consequencial / "E se...?" | Grafo causal ramificado a partir de um ponto de escolha | Grafo direcionado da decisão para consequências de 1ª, 2ª e 3ª ordem com polaridade (+ / -) e reversibilidade | `graph` (extensão com nós de decisão e arcos de impacto) |
| **Assess risk** | Baseada em risco e incerteza | Ameaças/Impactos mapeados em probabilidade $\times$ severidade | Matriz de risco em 4 quadrantes discretos com zonas de ação (Aceitar, Monitorar, Mitigar, Evitar) | `quadrant` (preset `risk`) ou overlay de risco |
| **Compare trade-offs** | Escolha com perdas explícitas | Opções atreladas a sacrifícios imediatos vs ganhos | Cards de compensação onde cada prós é amarrado ao contra correspondente ("compra X ao custo de Y") | `cards` com marcação de pareamento |
| **Prioritize** | Priorização e backlog | Itens em eixos de impacto vs esforço | Quadrante com destaque imediato para "Ganhos Rápidos" (Quick Wins) e "Apostas Estratégicas" | `quadrant` (preset `prioritize`) |
| **Explore scenarios** | Decisão sob incerteza futura | Mesma estrutura com valores alternativos por premissa | Controles de premissas no topo da visão alternando dados dos blocos em tempo real | Visão com controle `scenarios` |
| **Test robustness / Sensitivity** | Teste de robustez de ranking | Variação de resultado de acordo com a oscilação de variáveis | Gráfico Tornado com ranking de sensibilidade (qual critério vira o jogo) | `chart` (kind: `tornado`) |
| **Diagnose** | Diagnóstico / troubleshooting | Árvore de testes e caminhos de descarte | Árvore de eliminação guiada por checagens binárias | `tree` ou `graph` com layout top-down |
| **Navigate dependencies** | Decisão com bloqueios / restrições | Grafo de restrições (escolher A força B e anula C) | Grafo com arestas de restrição (`forces`, `blocks`) | `graph` com arestas de restrição |

---

## 4. Requisitos de Informação e Novos Componentes

### 4.1 Bloco `decision` (Novo Bloco em `canvas.html`)

O bloco `decision` implementa o framework de Análise de Decisão Multi-Critério (MCDA / Modelo Keeney & Raiffa e Pugh Matrix).

#### Esquema de Dados (Scene JSON):
```json
{
  "type": "decision",
  "id": "dec_db",
  "title": "Postgres vence no perfil atual; Dynamo lidera se escala for o único critério",
  "mode": "weighted",
  "options": [
    { "id": "pg", "label": "PostgreSQL", "sub": "16 gerenciado", "reversibility": "two-way" },
    { "id": "dynamo", "label": "DynamoDB", "sub": "On-demand", "reversibility": "one-way" }
  ],
  "criteria": [
    {
      "id": "cost",
      "label": "Custo Operacional",
      "weight": 35,
      "unit": "US$/mês",
      "scores": { "pg": { "raw": 480, "score": 8, "note": "Previsível" }, "dynamo": { "raw": 910, "score": 4, "note": "Picos caros" } },
      "vetoBelow": null
    },
    {
      "id": "latency",
      "label": "Latência p99",
      "weight": 40,
      "unit": "ms",
      "scores": { "pg": { "raw": 12, "score": 6 }, "dynamo": { "raw": 4, "score": 10 } },
      "vetoBelow": 5
    }
  ],
  "weightBasis": "Pesos calibrados com foco em custo inicial e latência aceitável",
  "recommendation": {
    "optionId": "pg",
    "rationale": "Pontuação ponderada superior (7.1 vs 6.8) e baixo custo de reversão."
  }
}
```

#### Arquitetura de Informação em 3 Níveis:
- **Nível 1 (Imediato / Repouso):**
  - Tabela com colunas (opções) e linhas (critérios com pesos e scores).
  - Barras proporcionais de score dentro de cada célula.
  - Coluna/Barra resumo com a pontuação ponderada final $\sum (w_j \cdot s_{ij}) / \sum w_j$.
  - Destaque visual inconfundível para a opção vencedora recomendada.
  - Alerta imediato se alguma opção violar cláusula de corte (`vetoBelow`).
- **Nível 2 (Hover / Tooltip):**
  - Contribuição exata do critério para o total daquela opção.
  - Notas de evidência e dados brutos (`raw`).
- **Nível 3 (Clique / Inspetor & Interatividade):**
  - **Sliders Interativos:** O leitor pode arrastar sliders de peso ($0\text{–}100$) diretamente na página.
  - Recálculo reativo instantâneo das pontuações totais e reordenação com animação suave.
  - Indicador de Sensibilidade / Ponto de Virada: indica quanto um peso precisaria mudar para outra opção assumir a liderança.

---

### 4.2 Gráfico `tornado` (Novo kind em `chart`)

Utilizado para análise de sensibilidade determinística.
- **Eixo Central:** Linha de base (`baseline`).
- **Barras Horizontais Bidirecionais:** Variação do desfecho do cenário pessimista ao otimista para cada variável.
- **Ordenação:** Ordenado do maior impacto (topo) para o menor (base), formando o funil de tornado.

---

### 4.3 Extensões no Bloco `graph` para Tomada de Decisão

1. **Nós de Decisão (`kind: "decision"`):**
   - Geometria destacada, contendo a pergunta/dilema central.
   - Nós de alternativas filhas exibem metadados de reversibilidade (`reversibility: "one-way" | "two-way"`).
2. **Caminhos de Consequência (`consequence` nas arestas e nós downstream):**
   - Arestas com probabilidade/confiança (`prob: 0.8`) e polaridade (`polarity: "ok" | "danger" | "neutral"`).
   - Nós de desfecho downstream marcados com ordem de efeito (`order: 1 | 2 | 3`).
3. **Interatividade de Inspeção de Trajetória:**
   - Clicar em uma opção acende o caminho completo até os desfechos terminais e esmaece os caminhos alternativos.
   - O inspetor sumariza métricas acumuladas daquele caminho (custo cumulativo, riscos agregados).

---

### 4.4 Controle de Cenários em Vistas (`scenarios`)

No nível da view, é possível declarar controles de hipóteses:
```json
"scenarios": {
  "controls": [
    { "id": "scale", "label": "Volume de dados", "options": ["100k req/s", "1M req/s"], "default": "100k req/s" }
  ],
  "overrides": { ... }
}
```
A interface renderiza radio-buttons/chips discretos no cabeçalho da visão. Ao alternar, os dados dos blocos são atualizados sem recarregar a página.

---

## 5. Regras de Fidelidade Semântica e Salvaguardas Cognitivas

Para evitar distorções cognitivas mapeadas na ciência da decisão (Kahneman, Tversky, Pugh, Cleveland & McGill):

1. **Vedação ao Falso Empate por Peso Implícito (Equal-Weight Fallacy):**
   - Nenhuma matriz decisória pode omitir pesos. Se o usuário não definiu relevância, o agente deve inferir pesos a partir das restrições do contexto e declarar explicitamente: `"weightBasis": "Pesos inferidos a partir do foco em X"`.
2. **Neutralidade de Enquadramento (Loss Aversion & Framing):**
   - Comparação de prós e contras deve usar formulação consistente. Prós não podem ser hiper-específicos enquanto contras são genéricos, ou vice-versa.
3. **Pareamento Obrigatório de Trade-offs:**
   - Não listar apenas colunas de "Vantagens" e "Desvantagens" desconectadas. Toda vantagem estrutural de uma alternativa deve ter seu custo explicitado (ex: "Latência ultra-baixa $\longleftrightarrow$ Flexibilidade de queries nula").
4. **Alerta de Reversibilidade (Portas de Uma Via vs Duas Vias):**
   - Escolhas com alto custo de migração retroativa (banco de dados, protocolo de mensageria principal) devem ser grafadas visualmente como irreversíveis (`one-way` / ícone de bloqueio/borda sólida forte), diferenciando de escolhas de baixo acoplamento (`two-way` / borda pontilhada ou tag flexível).
5. **Proibição de Falsa Precisão Contínua:**
   - Matrizes de risco e quadrantes não devem usar escalas de 0.0 a 1.0 como se fossem dados científicos exatos quando forem estimativas. Devem mapear zonas discretas (Baixo, Médio, Alto, Crítico).
6. **Autossuficiência Visual (The Reader Test):**
   - Se o texto do chat for suprimido, a visualização DEVE conter os nomes das opções, os critérios, as notas de evidência e a justificativa da melhor escolha.

---

## 6. Critérios de Qualidade e Anti-Patterns

### Anti-Patterns Específicos de Decisão:
- **Árvores de decisão intermináveis (Bushy Tree):** Mais de 3 níveis de ramificação tornam o canvas ilegível. Devem ser decompostas em visões de detalhe.
- **Recomendação desvinculada (Authority Bias):** Dizer "Escolha a Opção A" no título ou no callout sem que a Opção A lidere o modelo de critérios ponderados.
- **Comparação sem Datum / Baseline:** Propor uma nova arquitetura complexa sem desenhar a opção "Manter o que existe hoje com ajustes pontuais".
- **Omissão de Critérios Eliminatórios:** Ignorar requisitos mandatórios (ex: compliance LGPD/HIPAA, orçamento fixo). Devem ser modelados como `vetoBelow`.

---

## 7. Tratamento de Incerteza e Informação Ausente

- **Dados Mensurados vs Estimados:**
  - Valores com evidência no repositório ou benchmarks oficiais são exibidos em formato regular (`verified`).
  - Valores baseados em suposições razoáveis recebem o prefixo `~` e a tag `estimated` com nota no inspetor.
  - Critérios sem dado confiável são marcados como `unknown` e destacados em âmbar.
- **Incerteza no Desfecho:**
  - Ramos probabilísticos mostram faixas ou níveis de confiança (ex: "Provável (70%)", "Imprevisível").

---

## 8. Estratégia de Implementação no Código

1. **Modelos e Validação (`scripts/build-scene.py`):**
   - Atualizar validador Python para aceitar `type: "decision"`, validar opções, critérios, pesos e vetos.
   - Validar novo chart kind: `tornado`.
   - Validar propriedades de nós/arestas decisórias em `graph`.
2. **Template e Runtime (`templates/canvas.html`):**
   - Implementar renderizador SVG/DOM para o bloco `decision` com suporte a sliders e recalculo reativo.
   - Adicionar gerador de gráfico de Tornado via D3.
   - Implementar realce de caminho interativo no layout ELK do `graph`.
   - Adicionar seletor de cenários no cabeçalho das visões.
3. **Documentação e Guias (`SKILL.md`, `strategy.md`, `formats.md`, `examples.md`):**
   - Atualizar contagem e tabela de modos em `SKILL.md` (7 modos).
   - Expandir a tabela de estratégia com as 10 novas intenções decisórias.
   - Documentar os novos esquemas em `formats.md`.
4. **Exemplos e Testes:**
   - Criar exemplos `11-decisao-arquitetural.json` e `12-analise-cenarios.json`.
   - Adicionar cenários de teste específicos para tomadas de decisão em `tests/`.
