# Tasks: F0.8.03 — Revisão: Bancada de Fixação Cognitiva

**Branch**: `068-revisao-bancada-fixacao` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

---

## Phase 1: Setup & Shared Utilities

**Purpose**: Estruturas de dados, utilitários e regras de estilo compartilhadas da bancada de revisão

- [x] T001 [P] Adicionar tipos e constantes das métricas de prontidão (`ReviewReadinessMetrics`) e demonstração de termo oculto em `caderno-leitura-0.1/frontend/src/types/index.ts`
- [x] T002 [P] Definir regras de estilo da bancada de revisão, classes de cartão e transições cinemáticas aceleradas por GPU em `caderno-leitura-0.1/frontend/src/style.css`

---

## Phase 2: Foundational Components (Componentes de Base da Bancada)

**Purpose**: Componentes de interface e estado isolados que servem às histórias de usuário

- [x] T003 [P] Criar o componente de estado vazio e demonstração interativa de termo oculto `ReviewPedagogicalEmpty.vue` em `caderno-leitura-0.1/frontend/src/components/review/ReviewPedagogicalEmpty.vue`
- [x] T004 [P] Refinar o componente de resumo de conclusão de sessão `ReviewSummaryModal.vue` com encorajamento sereno e métricas em `caderno-leitura-0.1/frontend/src/components/review/ReviewSummaryModal.vue`

---

## Phase 3: User Story 1 - Barra Unificada de Prontidão Intelectual e Disparador de Sessão (Priority: P1) [MVP]

**Goal**: Transformar a área superior de status na Barra de Prontidão Intelectual, consolidando contadores, estimativa temporal e botão primário evidente

**Independent Test**: Acessar `/revisao` com cartões pendentes cadastrados, verificar a substituição das 5 caixas analíticas por uma seção coesa de prontidão e clicar em "Praticar Revisão Agora" para iniciar a sessão.

- [x] T005 [US1] Redesenhar `ReviewStatsHeader.vue` substituindo as 5 caixas analíticas por uma faixa editorial integrada de prontidão em `caderno-leitura-0.1/frontend/src/components/review/ReviewStatsHeader.vue`
- [x] T006 [US1] Adicionar cálculo e exibição de estimativa de tempo de sessão (~X min) e proporção equilibrada entre perguntas e termos ocultos em `caderno-leitura-0.1/frontend/src/components/review/ReviewStatsHeader.vue`
- [x] T007 [US1] Centralizar o botão de ação primária destacado ("Praticar Revisão Agora") com emissão do evento `@start-practice` em `caderno-leitura-0.1/frontend/src/components/review/ReviewStatsHeader.vue`
- [x] T008 [US1] Eliminar cores hexadecimais fixas e caixas azuis/verdes saturadas em `ReviewStatsHeader.vue`, consumindo exclusivamente variáveis dos 10 temas visuais em `caderno-leitura-0.1/frontend/src/components/review/ReviewStatsHeader.vue`

---

## Phase 4: User Story 2 - Bancada Imersiva de Active Recall e Operação por Teclado (Priority: P1) [MVP]

**Goal**: Permitir prática imersiva de estudo ativo com virada de cartão suave e atalhos ergonômicos de teclado (`Espaço` para virar e teclas `1-4` para classificar)

**Independent Test**: Iniciar uma rodada de revisão, navegar pelo ciclo completo de cartões virando com a barra de espaço, avaliar retenção através das teclas `1` a `4` e validar o avanço contínuo sem uso do mouse.

- [x] T009 [US2] Aprimorar `ReviewCard.vue` com tipografia editorial focada, supressão de distrações periféricas e realce visual elegante para o termo oculto revelado em `caderno-leitura-0.1/frontend/src/components/review/ReviewCard.vue`
- [x] T010 [US2] Implementar transição visual suave de virada do cartão ($\le 250$ms) acelerada por GPU com suporte a `prefers-reduced-motion` em `caderno-leitura-0.1/frontend/src/components/review/ReviewCard.vue`
- [x] T011 [US2] Conectar listeners globais de teclado na sessão ativa (`Espaço` para revelar verso e teclas `1`, `2`, `3`, `4` para avaliar retenção e avançar) com proteção defensiva de foco em `caderno-leitura-0.1/frontend/src/views/ReviewHubView.vue`
- [x] T012 [US2] Integrar barra de progresso tátil da rodada e botões de classificação acessíveis com rótulos semânticos em `caderno-leitura-0.1/frontend/src/components/review/ReviewCard.vue`

---

## Phase 5: User Story 3 - Estado Vazio Pedagógico com Demonstração Interativa (Priority: P2)

**Goal**: Exibir guia acolhedor com demonstração interativa de termo oculto que se revela ao clique quando não há revisões pendentes

**Independent Test**: Acessar `/revisao` sem pendências, interagir com o componente modelo de termo oculto verificando a revelação didática ao toque e conferir as orientações práticas de leitura ativa.

- [x] T013 [US3] Integrar a demonstração interativa de termo oculto com frase-modelo e revelação fluida ao clique/toque em `caderno-leitura-0.1/frontend/src/components/review/ReviewPedagogicalEmpty.vue`
- [x] T014 [US3] Adicionar guia visual instrucional de 3 passos ensinando como grifar passagens e formular perguntas no leitor de livros em `caderno-leitura-0.1/frontend/src/components/review/ReviewPedagogicalEmpty.vue`
- [x] T015 [US3] Conectar `ReviewPedagogicalEmpty.vue` na visualização principal quando não houver revisões pendentes em `caderno-leitura-0.1/frontend/src/views/ReviewHubView.vue`

---

## Phase 6: User Story 4 - Conclusão Serena de Sessão e Histórico de Prática (Priority: P2)

**Goal**: Oferecer encerramento contemplativo sereno ao concluir a fila diária e manter a consulta histórica de sessões anteriores com visual editorial

**Independent Test**: Concluir o último cartão de uma sessão, validar a transição suave para a tela de conclusão com o balanço de tempo e acessar a aba "Histórico de Sessões" confirmando a listagem harmoniosa.

- [x] T016 [US4] Integrar transição serena para o resumo comemorativo ao responder ao último cartão da rodada em `caderno-leitura-0.1/frontend/src/views/ReviewHubView.vue`
- [x] T017 [US4] Apresentar balanço da sessão no modal de conclusão: tempo total decorrido, total de cartões e divisão por níveis de facilidade em `caderno-leitura-0.1/frontend/src/components/review/ReviewSummaryModal.vue`
- [x] T018 [US4] Reestilizar os cartões de sessões passadas na aba "Histórico de Sessões" harmonizando-os com a linguagem visual editorial em `caderno-leitura-0.1/frontend/src/views/ReviewHubView.vue`

---

## Phase 7: User Story 5 - Filtros Contextuais e Experiência Móvel sem Distrações (Priority: P3)

**Goal**: Permitir filtragem por livro/capítulo/tipo de desafio e garantir ergonomia tátil em dispositivos móveis ($\ge 44 \times 44$px)

**Independent Test**: Filtrar a revisão por um livro específico confirmando a atualização do contador de prontidão, e redimensionar a tela para dimensões móveis verificando alvos de toque de 44px e layout em tela cheia.

- [x] T019 [US5] Reestruturar a barra de filtros contextuais (seletor por livro, capítulo e modalidade Todos / Perguntas / Ocultamentos) com recálculo dinâmico de prontidão em `caderno-leitura-0.1/frontend/src/views/ReviewHubView.vue`
- [x] T020 [US5] Ajustar layout responsivo móvel (< 768px): barra inferior tátil com touch targets $\ge 44 \times 44$px e modo de estudo em tela cheia em `caderno-leitura-0.1/frontend/src/components/review/ReviewCard.vue` e `caderno-leitura-0.1/frontend/src/views/ReviewHubView.vue`

---

## Phase 8: Testes Automatizados, Validação & Polimento

**Purpose**: Verificação completa de requisitos, contratos de UI e garantia de não-regressão

- [x] T021 [P] Criar suíte de testes unitários e de integração para a barra de prontidão intelectual e estado vazio pedagógico em `caderno-leitura-0.1/frontend/tests/feature-068-revisao-hub.test.mjs`
- [x] T022 [P] Criar suíte de testes para ergonomia por teclado (`Espaço`, `1-4`) e avanço de sessão de Active Recall em `caderno-leitura-0.1/frontend/tests/review_session_keyboard.test.mjs`
- [x] T023 Executar validação global de suítes (`npm test`, `npm run build`, `pytest backend/tests`) e cenários do `quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup & Foundational (Phases 1 & 2)**: Sem dependências de histórias de usuário — iniciam imediatamente.
- **User Story 1 (Phase 3 - P1 [MVP])**: Depende das Fases 1 e 2.
- **User Story 2 (Phase 4 - P1 [MVP])**: Depende das Fases 1 e 2; integra-se com a sessão disparada pela US1.
- **User Story 3 (Phase 5 - P2)**: Depende do componente de estado vazio criado na Fase 2 e integrado na US1.
- **User Story 4 (Phase 6 - P2)**: Depende do fluxo de conclusão da US2 e componente da Fase 2.
- **User Story 5 (Phase 7 - P3)**: Refinamento de responsividade e filtros sobre US1 e US2.
- **Validação & Polimento (Phase 8)**: Executada após a conclusão das histórias de usuário.

### Parallel Opportunities

- T001, T002, T003 e T004 podem ser preparados em paralelo.
- Os testes T021 e T022 podem ser criados em paralelo.
- Ajustes de estilo em CSS e tipagens TypeScript operam de forma independente.

---

## Implementation Strategy

### MVP Scope (Phases 1, 2, 3 e 4)
1. Concluir Setup e Componentes Base (T001 a T004).
2. Entregar a Barra Unificada de Prontidão Intelectual (T005 a T008) — elimina o visual SaaS e 5 caixas dispersas.
3. Entregar a Bancada Imersiva com operação por teclado (T009 a T012) — experiência ágil de *Active Recall*.
4. **Validação do MVP**: Praticar revisão completa usando exclusivamente teclado.

### Incremental Delivery
- **Incremento 1**: Barra de Prontidão + Disparador (US1).
- **Incremento 2**: Sessão Ativa com Atalhos por Teclado (US2).
- **Incremento 3**: Estado Vazio Pedagógico com demonstração de cloze (US3).
- **Incremento 4**: Conclusão Serena e Histórico de Sessões (US4).
- **Incremento 5**: Filtros contextuais e refinamento mobile (US5).
- **Validação Global**: Suíte completa de testes de frontend e backend.
