# Feature Specification: F0.10.04 — Revisão: Baldes por Dificuldade, Sessões de 5/10/15 e Gaveta de Contexto

**Feature Branch**: `096-revisao-baldes-sessao`

**Created**: 2026-11-03

**Status**: Concluída em 2026-11-03 (com o ajuste da sessão estruturada descrito na US1).

**Input**: Feature 03 do plano mestre ("Revisão — Bancada de Fixação Cognitiva Calma": baldes de prioridade
Difícil/Médio/Fácil, seletor de sessão de 5, 10 ou 15 itens, gaveta de contexto imediato e estado vazio
pedagógico). É a 5ª feature do lote: fecha com as suítes completas (`npm test`, `pytest`, build).

---

## 1. Contexto (auditoria de 2026-11-03)

| Pedido | Situação | Onde |
|---|---|---|
| Trocar os 5 cartões de métricas | **Já feito**: virou a faixa de prontidão ("N cartões prontos para hoje", perguntas, termos ocultos, revisados hoje) | `components/review/ReviewStatsHeader.vue` |
| Estado vazio pedagógico | **Já feito** | `components/review/ReviewPedagogicalEmpty.vue` |
| Baldes Difícil/Médio/Fácil | **Não**: a fila já prioriza nunca revisados, depois difíceis, depois os mais antigos (`review_service.get_review_items`), mas a tela não mostra quantos itens há em cada nível nem deixa praticar um nível só | `services/review_service.py` |
| Sessão de 5, 10 ou 15 itens | **Não**: fixo em 10 nas três entradas (`startReview`, `handleReviewMore`, `startStructuredSession`); a API já aceita `limit` (até 50 no hub, 100 na sessão estruturada) | `views/ReviewHubView.vue` |
| Gaveta de contexto | **Não**: o cartão mostra só o trecho em volta da lacuna (`context_prefix`/`suffix`); não dá para consultar as 4 partes do estudo | `components/review/ReviewCard.vue`, `views/StudySessionView.vue` |

**Decisão de dados:** os baldes vêm do `last_rating` que já existe em `study_highlights` (`easy`, `medium`, `hard`
ou vazio). Não há migração. O peso de dificuldade (`difficulty_weight`), os conceitos frágeis e a "Memória do
Dia" continuam no Roadmap 0.11 (item 4.4).

---

## 2. User Stories

### US1 — Ver e escolher os baldes (P1)

Como leitor, quero ver quantos itens estão em cada nível e poder praticar só um deles.

**Acceptance**:
1. Abaixo da faixa de prontidão, quatro baldes: **Novos** (nunca avaliados), **Difícil**, **Médio** e **Fácil**,
   cada um com a contagem dentro do filtro atual (tipo, livro, capítulo).
2. Os baldes funcionam como filtro de seleção única, com "Todos" como padrão (`role="radiogroup"`, teclado como
   os filtros de tipo que já existem). Balde vazio aparece desabilitado.
3. Com um balde escolhido, a prática no hub traz só itens daquele nível, na ordem que a API já usa. A sessão
   estruturada continua com todos os níveis e avisa isso quando há balde escolhido. *(Revisado na execução: ao
   reabrir uma sessão estruturada, o servidor recalcula os cartões pendentes a partir do escopo gravado em
   `study_sessions`, que não tem onde guardar o balde; guardá-lo exigiria migração, fora deste plano.)*

### US2 — Escolher o tamanho da sessão (P1)

**Acceptance**:
1. Seletor "5 · 10 · 15 itens" (padrão 10), lembrado no navegador.
2. Vale para "Praticar agora", "Revisar mais" e "Iniciar sessão estruturada"; os rótulos mostram o número
   escolhido (ou menos, se houver menos itens elegíveis).

### US3 — Consultar o estudo sem perder o foco (P1)

**Acceptance**:
1. Depois de revelar a resposta, o cartão mostra "Ver o estudo", que abre uma gaveta lateral (o `Drawer` que já
   existe) com título, livro e capítulo e as quatro partes (Resumo, Explicação, Conceitos, Referências) em
   Markdown sanitizado.
2. Antes de revelar, o botão não aparece: consultar o estudo entregaria a resposta e estragaria a recuperação ativa.
3. Fechar a gaveta (Esc, botão ou fundo) volta ao cartão no mesmo ponto; a avaliação continua disponível.
4. Vale no hub e na sessão estruturada.

### Edge Cases

- Item cujo estudo foi para a lixeira no meio da sessão: a gaveta mostra "Este estudo não está mais disponível".
- Balde escolhido sem itens depois de uma avaliação (ex.: o último "Difícil" virou "Fácil"): a contagem atualiza ao
  voltar ao hub; a sessão em andamento não muda.
- Celular: a gaveta ocupa a largura da tela; os baldes e o seletor de tamanho quebram linha sem rolagem lateral.

---

## 3. Requirements

- **FR-001**: `GET /api/review/stats` passa a devolver `buckets: {new, hard, medium, easy}` e aceita filtros
  opcionais `book_id`, `chapter_id` e `kind` só para os baldes (os campos atuais continuam globais).
- **FR-002**: `GET /api/review/items` aceita `bucket` (`new`, `hard`, `medium`, `easy`); sem ele, nada muda. A
  sessão estruturada não recebe balde (ver US1, cenário 3).
- **FR-003**: `ReviewStatsHeader` ganha a linha de baldes e o seletor de tamanho; emite as escolhas para o hub.
- **FR-004**: `ReviewHubView` usa o tamanho e o balde nas três entradas de sessão; tamanho em `localStorage`
  (`caderno_review_session_size`), com `try/catch`.
- **FR-005**: Novo `StudyContextDrawer.vue` (usa `Drawer` e `MarkdownContent`); botão "Ver o estudo" no
  `ReviewCard` e na `StudySessionView`, só com a resposta revelada.
- **FR-006**: Só tokens de cor; contraste ≥ 4,5:1 nos 10 temas para os baldes (inclusive o selecionado e o hover);
  alvos de 44 px; `prefers-reduced-motion` respeitado na gaveta.
- **FR-007**: Sem migração e sem mudança no algoritmo de ordenação.

## 4. Success Criteria

- **SC-001**: Testes de backend: contagem dos baldes (com e sem filtros), `items?bucket=` para os quatro níveis,
  sessão estruturada com `bucket`, valor inválido recusado (422).
- **SC-002**: Teste de frontend: baldes como `radiogroup`, seletor 5/10/15 aplicado às três entradas, gaveta só após
  revelar, nos dois modos.
- **SC-003**: Navegador (dados fictícios com itens nos quatro níveis): baldes e contagens, sessão de 5 itens do balde
  "Difícil", gaveta com as 4 partes, 1366 e 375 px, contraste nos 10 temas.
- **SC-004**: Fecho do lote de 5: `npm test`, `pytest` completo (com banco descartável) e build; falha de feature
  anterior vira commit próprio.

## 5. Fora do escopo

- `difficulty_weight`, detector de conceitos frágeis, cartões automáticos de conceito e "Memória do Dia" (0.11).
- Mudar a ordem da fila ou o significado de "pendente hoje".
- Unificar os três botões de início de sessão (registrado como possível item da F0.10.10, de correções).
