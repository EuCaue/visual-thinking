# Brand sheet spec (shared by all five prototypes)

Goal: one self-contained HTML page per style, showing what the visual-thinking skill would look like if it had this identity. Same content in every page, so the owner compares style, not content. Portuguese UI text. Prototype only: the real template is not changed.

File: /home/caue/code/visual-thinking/docs/branding/<slug>.html. One file. CSS and JS inline. Fonts may come from Google Fonts (prototype); icons from Phosphor via https://unpkg.com/@phosphor-icons/web@2.1.1 (pinned) or authored SVG geometry. No external images.

Sections, in this order:

1. Brand bar: a logo mark (simple geometric SVG made for this style, it must say "diagram / connection / thinking", not a generic letter in a circle) + wordmark "visual-thinking" + the style name + a theme toggle (Claro / Escuro / Auto, persists in localStorage, respects prefers-color-scheme). Tagline: "Desenhos que explicam sistemas."

2. The canvas, recreated as real working UI (HTML + inline SVG, not a picture), about 1100x620 on desktop:
   - Page title "Pedido pago vira email por uma fila", subtitle "shop-api · lido no código em 14/10/2026".
   - View tabs: "Visão geral" (selected), "Processo API", "Processo worker".
   - Floating toolbar over the canvas: segmented "Mapa / Contexto / Detalhes" (Contexto selected) + a search button; zoom group (- / ajustar / +) at bottom right.
   - An SVG graph, laid out by hand, left to right: Cliente (entry, sub "SPA, envia JWT"), API (component, sub "valida e enfileira"), Stripe (external, sub "cobra o cartão"), Fila Redis (queue, sub "jobs de email"), emailWorker (component, sub "envia o recibo"), Postgres (store, sub "pedidos e usuários"). API and the Fila sit inside a group "Processo API"; emailWorker inside "Processo worker". Labeled edges: Cliente to API "POST /orders"; Stripe to API "webhook pago" (event, dashed in the default style); API to Fila "enfileira" (event); Fila to emailWorker "consome" (data); API to Postgres "grava" (data); emailWorker to Postgres "lê pedido" (data); one error edge emailWorker to Fila "retenta 5×". Mark one node as critical (the webhook handler idea: the API node gets a critical badge "assinatura") and one as inferred (Stripe, dashed or the style's equivalent).
   - Hover a node: its neighbors stay lit, others dim. Click a node: the inspector updates (at least for 3 nodes).
   - Inspector panel on the right (bottom sheet under 820px): crumb, node name "emailWorker", sub, file path `src/workers/emailWorker.js` as a link style, tags (Componente, Verificado), "Recebe de" and "Sai para" rows (clickable), a legend computed for the drawing (node kinds and edge kinds with counts), annotations list with one item "A API responde 200 antes do email sair."

3. Components sheet: buttons (primary, secondary, quiet), segmented control, status tags (Verificado / Inferido / Desconhecido), edge label pill, the six node kinds side by side (entry, component, store, queue, external, critical, plus decision), tooltip, a callout ("O worker parado não gera alerta"), empty state for the inspector.

4. Data: a small comparison matrix (PostgreSQL / MongoDB / DynamoDB × Consultas ad hoc yes/yes/no, p99 leitura 12/9/4 ms best min, Custo mensal 480/620/910 US$ best min) and a small line chart (p95 por mês, jan to jun, Catálogo 480 470 460 210 200 190 and Checkout 180 185 182 178 181 179, ms, reference line "SLO 300 ms", annotation "cache" at abr). Plus a KPI trio (Receita R$ 184.300 +6,1%, Contas 2.140 +92, Churn 2,8% +0,5 pp in danger).

5. Tokens: the palette as named swatches with hex for light and dark, and a type specimen (display, body, data) with the faces named.

Rules:
- Light and dark both designed, contrast WCAG AA for text in both.
- Responsive down to 375px without horizontal page scroll (the canvas may scale down or scroll inside its frame).
- Keyboard focus visible, reduced motion respected, selection and scrollbars themed.
- No em dashes or en dashes anywhere visible. No eyebrow labels above headings. No section numbers. No gradient text. No glow halos. No emoji.
- Semantic meanings stay: entry = start, store/queue = data at rest, critical/error = danger, external = outside our control, inferred = not verified. The style decides how to express them.
- Under each section heading at most one short sentence.
- At the bottom: "Por que este estilo" with 3 short lines: what it borrows, where it shines for this skill, its cost or risk.
