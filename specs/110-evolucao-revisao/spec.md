# Feature Specification: F0.11.08 — Evolução da Revisão

**Feature Branch**: `110-evolucao-revisao`

**Created**: 2026-11-12

**Status**: Concluída em 2026-11-12

**Input**: Item "evolução da revisão (`difficulty_weight`, conceitos frágeis, cartões de conceito, Memória do Dia)" do
Roadmap 0.11 no HANDOFF. Terceira feature do lote 2 do 0.11. **Com migração (`0037`).**

---

## 1. Contexto (auditoria de 2026-11-12, só código)

| Ponto | Situação | Onde |
|---|---|---|
| Itens de revisão | Destaques `question` e `hidden` (lacuna). Cada um guarda só `last_reviewed_at`, `review_count` e `last_rating` (`easy`/`medium`/`hard`) | `models/study_highlight.py` |
| Ordem da fila | Nunca revisados → último "difícil" → mais antigos. Só a **última** nota conta: um item difícil 5 vezes e fácil uma vez vira "fácil" | `services/review_service.py` (`get_review_items`) |
| Prática | Central de Revisão: filtros (livro, capítulo, tipo, balde), "Praticar agora" e sessão registrada; avaliação em 3 botões | `views/ReviewHubView.vue`, `composables/useReviewSession.ts`, `views/StudySessionView.vue` |
| Conceitos | Léxico derivado das seções Conceitos (F0.11.06), sem nenhuma ligação com a revisão | `services/concept_lexicon.py` |
| `difficulty_weight`, conceitos frágeis, cartões de conceito, Memória do Dia | **Não existem** | — |

---

## 2. User Stories

### US1 — Peso de dificuldade que acumula o histórico (P1)

**Acceptance**:
1. Cada item ganha `difficulty_weight` (0 = fácil, 1 = difícil; sem revisão = vazio, tratado como 0,5). A cada
   avaliação: `peso = 0,5 × peso anterior + 0,5 × alvo` (difícil 1, médio 0,5, fácil 0). Dois "difícil" seguidos
   levam a 0,875; um "fácil" depois, a 0,44.
2. A migração preenche os itens já avaliados a partir da última nota (difícil 0,75, médio 0,5, fácil 0,25).
3. **Fila**: primeiro os nunca revisados; depois os **vencidos**, do mais pesado ao mais leve; por fim os demais, também
   do mais pesado (empate: revisado há mais tempo). Itens avaliados antes da `0037` e ainda sem peso usam o
   equivalente da última nota. Um item vence quando passou o intervalo do seu peso: peso ≥ 0,75 → 1 dia; ≥ 0,5 → 3 dias; ≥ 0,25 → 7 dias;
   abaixo → 14 dias.
4. Os baldes (novo, difícil, médio, fácil) continuam pela última nota, como hoje.

### US2 — Cartões de conceito (P1)

**Acceptance**:
1. Todo conceito do léxico com pelo menos uma definição vira um cartão: frente "O que é **Termo**?", verso com as
   definições (até 3, com livro e estudo).
2. Na Central de Revisão, o filtro de tipo ganha **"Conceitos"**; "Praticar agora" com ele usa os cartões de conceito,
   com as mesmas 3 notas e a mesma fila do US1. Os filtros de livro e capítulo valem para os cartões (conceitos
   definidos naquele livro/capítulo).
3. A nota do cartão fica guardada por leitor e chave do conceito (tabela nova `concept_reviews`). Conceito que some do
   léxico deixa de aparecer; se voltar, o histórico volta junto.
4. A sessão registrada e "Todos" continuam só com perguntas e lacunas (os cartões são uma prática à parte; a Central
   avisa isso com "Conceitos" selecionado).
5. Com "Conceitos" selecionado, os baldes e os totais da faixa (elegíveis, revisados hoje, pendentes) passam a ser os
   dos cartões de conceito (decidido na execução: sem isso, "Praticar agora" ficava preso aos números das perguntas).

### US3 — Conceitos frágeis (P2)

**Acceptance**:
1. Um conceito é **frágil** quando tem peso ≥ 0,6, sendo o peso o maior entre: o do seu cartão e a média dos pesos das
   perguntas e lacunas avaliadas dos estudos que o definem.
2. Na Central (aba Prática), o bloco **"Conceitos frágeis"** mostra até 5, do mais pesado, cada um com o motivo
   ("cartão marcado como difícil" ou "perguntas dos estudos que o definem estão difíceis"), link para a página do
   conceito e o botão **"Praticar conceitos frágeis"**.
3. No Léxico e na página do conceito, conceito frágil tem a etiqueta "Frágil" (texto, não só cor).
4. Sem conceitos frágeis o bloco não aparece.

### US4 — Memória do Dia (P2)

**Acceptance**:
1. No Painel, o cartão **"Memória do dia"** traz um destaque ou estudo do próprio leitor criado há pelo menos 30 dias:
   o texto (até 280 caracteres, sem Markdown), livro, estudo, "há 1 ano"/"há 3 meses" e link para o estudo.
2. Preferência: algo criado **neste mesmo dia** em ano anterior; senão no mesmo dia do mês em mês anterior; senão uma
   escolha fixa do dia (sorteio com semente "leitor + data", para não mudar ao recarregar).
3. Sem nada com 30 dias ou mais, o cartão não aparece. Estudos e livros na lixeira ficam de fora; lacunas ocultas
   (`hidden`) não são mostradas (estragariam a revisão).

### Edge Cases

- Avaliação concorrente do mesmo item: o peso é calculado na mesma transação da nota.
- Conceito com chave igual em livros diferentes: um cartão só (o léxico já funde por chave).
- Celular: blocos em uma coluna; botões de 44 px.
- Leitor sem conceitos: o filtro "Conceitos" mostra o estado vazio explicando como criar conceitos (seção Conceitos).

---

## 3. Requirements

- **FR-001**: Migração `0037_review_difficulty_concepts`: coluna `study_highlights.difficulty_weight` (`FLOAT`, nula),
  preenchimento a partir de `last_rating`; tabela `concept_reviews` (`id`, `user_id` → `users.id` `ON DELETE CASCADE`,
  `concept_key`, `last_reviewed_at`, `review_count`, `last_rating`, `difficulty_weight`, `created_at`, `updated_at`;
  único `user_id + concept_key`), com nomes de restrição pela convenção. Snapshot validado antes (já automático no
  `alembic upgrade`).
- **FR-002**: `services/review_weights.py` (puro): `next_weight(prev, rating)`, `interval_days(weight)`,
  `is_due(weight, last_reviewed_at, now)`, `queue_key(...)`. `record_review_rating` atualiza o peso;
  `get_review_items` ordena pela fila nova.
- **FR-003**: Cartões: `kind=concept` em `GET /api/review/items` (com `book_id`, `chapter_id`, `fragile=true`);
  `POST /api/review/concepts/{key}/record`; `ReviewItemRead` ganha `concept_key` e `definitions`.
- **FR-004**: `GET /api/review/fragile-concepts?limit=5`; `ConceptSummary`/`ConceptDetail` ganham `fragile`.
- **FR-005**: `GET /api/dashboard/memory` → item ou `null`.
- **FR-006**: Frontend: opção "Conceitos" no filtro, verso do cartão com definições, `useReviewSession` grava a nota
  no endpoint certo; `FragileConceptsPanel.vue`; etiqueta "Frágil"; `DailyMemoryCard.vue` no Painel. Só tokens,
  `.quiet`, 44 px, contraste ≥ 4,5:1 nos 10 temas.

## 4. Success Criteria

- **SC-001**: Testes puros dos pesos (sequências de notas, intervalos, vencimento) e da fila.
- **SC-002**: Testes de API: peso gravado ao avaliar; ordem da fila; cartões de conceito (listar, filtrar por livro,
  avaliar, isolamento entre leitores); conceitos frágeis pelos dois motivos; Memória do Dia (aniversário, mês,
  sorteio estável, 30 dias, lixeira e `hidden` fora, nada → `null`).
- **SC-003**: Migração: `test_migration_matches_models` e um teste de upgrade num banco descartável com dados
  fictícios (preenchimento do peso).
- **SC-004**: Testes de frontend (filtro, gravação pelo endpoint certo, componentes, rotas) e navegador (dados
  fictícios): prática de conceitos, bloco de frágeis, etiqueta, Memória do dia; 1366 e 375 px; contraste nos 10 temas.
- **SC-005**: Build e testes novos e vizinhos; commit; levar ao `main`. A migração **não** é aplicada ao banco ativo
  (procedimento do HANDOFF, pelo usuário).

## 5. Fora do escopo

- Algoritmo de repetição espaçada completo (SM-2/FSRS) e agendamento com datas de vencimento guardadas.
- Cartões de conceito na sessão registrada e em "Todos".
- Notificações da Memória do Dia; escolher outra memória no mesmo dia.
