# Tasks: F09 - Sistema Visual Profissional

**Branch**: `017-sistema-visual-profissional` | **Date**: 2026-09-19 | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

---

## Phase 1: Setup (Infraestrutura Compartilhada)

**Purpose**: Instalação de dependências e configuração básica de tipos e constantes do design system.

- [X] T001 Adicionar dependência `lucide-vue-next` em `caderno-leitura-0.1/frontend/package.json`
- [X] T002 Instalar dependências atualizadas no frontend via `npm install` em `caderno-leitura-0.1/frontend`
- [X] T003 [P] Declarar tipo `IconName` e interfaces `IconProps`, `EmptyStateProps`, `LoadingSkeletonProps`, `StatusBadgeProps` em `caderno-leitura-0.1/frontend/src/types.ts`
- [X] T004 [P] Criar dicionário canônico de vocabulário editorial `EDITORIAL_TERMS` em `caderno-leitura-0.1/frontend/src/constants/editorial.ts`

---

## Phase 2: Foundational (Componentes Base de Interface)

**Purpose**: Blocos de UI fundamentais que suportam todas as histórias de usuário.

**CRITICAL**: Nenhuma alteração nas views pode iniciar antes da conclusão desta fase.

- [X] T005 [P] Criar componente envelope unificado `Icon.vue` com catálogo Lucide, suporte a `size`, `strokeWidth` e acessibilidade (`role="img"` vs `aria-hidden="true"`) em `caderno-leitura-0.1/frontend/src/components/ui/Icon.vue`
- [X] T006 [P] Criar componente `LoadingSkeleton.vue` com proporções configuráveis (`shape`, `width`, `height`, `lines`), shimmer gradiente via `color-mix`, desativação sob `prefers-reduced-motion` e texto acessível em `caderno-leitura-0.1/frontend/src/components/ui/LoadingSkeleton.vue`
- [X] T007 [P] Criar componente `EmptyState.vue` com ícone vetorial, título semântico, texto orientador e slot para ação primária em `caderno-leitura-0.1/frontend/src/components/ui/EmptyState.vue`
- [X] T008 [P] Criar componente `StatusBadge.vue` com variantes cromáticas (`neutral`, `accent`, `warning`, `danger`, `success`) e ícone opcional em `caderno-leitura-0.1/frontend/src/components/ui/StatusBadge.vue`

**Checkpoint**: Componentes básicos de design system criados e prontos para integração.

---

## Phase 3: User Story 1 - Iconografia Vetorial Sóbria e Erradicação de Emojis (Priority: P1) 🎯 MVP

**Goal**: Substituir 100% dos emojis e botões informais por ícones vetoriais Lucide elegantes e acessíveis em toda a aplicação.

**Independent Test**: Navegar por todas as vistas do sistema e validar visualmente e no DOM que nenhum emoji permanece em botões, menus e cabeçalhos, com área de toque mínima preservada de 44x44px em mobile.

### Testes para User Story 1

- [X] T009 [P] [US1] Criar suíte de testes unitários para o sistema visual em `caderno-leitura-0.1/frontend/tests/visual_system.test.mjs`

### Implementação para User Story 1

- [X] T010 [P] [US1] Refatorar barra de navegação principal em `caderno-leitura-0.1/frontend/src/App.vue` substituindo SVGs manuais pelo componente `Icon` com ícones Lucide
- [X] T011 [P] [US1] Substituir caracteres de edição `✎` e exclusão `🗑` em `caderno-leitura-0.1/frontend/src/views/BookView.vue` pelos ícones `pencil` e `trash`
- [X] T012 [P] [US1] Substituir emoji de capa padrão `'📖'` em `caderno-leitura-0.1/frontend/src/components/BookCover.vue` por SVG vetorial padronizado
- [X] T013 [P] [US1] Substituir emoji de alerta `⚠️` e caracteres de fechar `✕` por ícones Lucide em `caderno-leitura-0.1/frontend/src/components/TrashConfirmModal.vue`, `caderno-leitura-0.1/frontend/src/components/BookEditModal.vue` e `caderno-leitura-0.1/frontend/src/components/ExportModal.vue`
- [X] T014 [P] [US1] Substituir caractere `✓` em `caderno-leitura-0.1/frontend/src/components/RestoreModal.vue` pelo ícone `check-circle`
- [X] T015 [P] [US1] Substituir caracteres `✕` de limpar pesquisa em `caderno-leitura-0.1/frontend/src/components/LibraryToolbar.vue` e filtro de data em `caderno-leitura-0.1/frontend/src/views/DashboardView.vue` pelo ícone `x`
- [X] T016 [P] [US1] Substituir emoji de sequência `🔥` em `caderno-leitura-0.1/frontend/src/views/DashboardView.vue` pelo ícone `flame`

**Checkpoint**: MVP concluído! A interface está livre de emojis informais e padronizada com iconografia vetorial sóbria.

---

## Phase 4: User Story 2 - Purificação Semântica e Erradicação de Rótulos de IA (Priority: P2)

**Goal**: Erradicar todas as referências a "IA", "ChatGPT" e "prompt", instituindo o termo canônico "Fichamento da Fonte" para o campo `source_response`.

**Independent Test**: Abrir os formulários de importação, leitura e edição de estudos confirmando que os textos orientam o leitor de forma autoral e clássica sem menções a agentes externos.

### Implementação para User Story 2

- [X] T017 [P] [US2] Atualizar descrições e mensagens de validação no backend em `caderno-leitura-0.1/backend/app/schemas/imports.py` removendo menções a "ChatGPT" e adotando vocabulário editorial
- [X] T018 [P] [US2] Atualizar mensagens de validação e orientação no composable `caderno-leitura-0.1/frontend/src/composables/useImportDraft.ts` removendo "ChatGPT" e adotando "texto-base do fichamento"
- [X] T019 [P] [US2] Refatorar visualização `caderno-leitura-0.1/frontend/src/views/ImportView.vue` aplicando rótulos canônicos ("Importar Fichamento", "Fichamento da Fonte", placeholders e notas de preservação)
- [X] T020 [P] [US2] Atualizar visualização `caderno-leitura-0.1/frontend/src/views/StudyView.vue` substituindo "Consultar resposta original" por "Consultar Fichamento da Fonte"
- [X] T021 [P] [US2] Atualizar modal `caderno-leitura-0.1/frontend/src/components/ExportModal.vue` substituindo "Resposta Original de Importação" por "Fichamento da Fonte"
- [X] T022 [P] [US2] Atualizar mensagens orientadoras e textos vazios em `caderno-leitura-0.1/frontend/src/views/BookView.vue` removendo referências a "ChatGPT"

**Checkpoint**: Vocabulário editorial 100% purificado no frontend e backend, mantendo o banco SQLite intacto.

---

## Phase 5: User Story 3 - Padronização de Estados de Interface: Carregamento, Vazio e Feedback (Priority: P3)

**Goal**: Padronizar estados vazios informativos e esqueletos de carregamento com shimmer adaptativo para evitar layout shift.

**Independent Test**: Simular carregamento assíncrono e navegar por listas vazias confirmando a presença de skeletons e empty states harmonizados com as Superclasses.

### Implementação para User Story 3

- [X] T023 [P] [US3] Integrar componente `EmptyState` em `caderno-leitura-0.1/frontend/src/views/TrashView.vue` substituindo a div de emoji `🗑️` por estado vazio com ação de retorno
- [X] T024 [P] [US3] Integrar componente `EmptyState` em `caderno-leitura-0.1/frontend/src/views/DashboardView.vue` substituindo o emoji `📖` por estado acolhedor de leitura
- [X] T025 [P] [US3] Integrar componente `EmptyState` em `caderno-leitura-0.1/frontend/src/views/BookView.vue` para capítulos e estudos vazios
- [X] T026 [P] [US3] Integrar esqueletos de carregamento `LoadingSkeleton` em `caderno-leitura-0.1/frontend/src/views/BooksView.vue` e `caderno-leitura-0.1/frontend/src/views/BookView.vue` para mitigar layout shift durante requisições
- [X] T027 [US3] Calibrar animações de shimmer e tokens de contraste dos novos componentes de UI em `caderno-leitura-0.1/frontend/src/styles/tokens.css` harmonizando com os temas (Claro, Escuro, Sépia) e as 5 Superclasses de interface

**Checkpoint**: Todos os estados de carregamento e vazio estão padronizados e elegantes.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verificação global de integridade, testes automatizados e compilação de produção.

- [X] T028 Executar varredura automatizada no frontend e backend confirmando ausência total de emojis e termos alusivos a IA
- [X] T029 Executar build estrito de produção do frontend via `npm run build` em `caderno-leitura-0.1/frontend`
- [X] T030 Executar suíte completa de testes automatizados do frontend via `npm test` e do backend via `pytest`
- [X] T031 Validar acessibilidade (`aria-label`, foco ordenado por teclado e `prefers-reduced-motion`) conforme `quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup 
   └──> Phase 2: Foundational (Icon.vue, LoadingSkeleton.vue, EmptyState.vue)
           ├──> Phase 3: User Story 1 (P1 - Iconografia e Erradicação de Emojis) [MVP]
           ├──> Phase 4: User Story 2 (P2 - Purificação Semântica de IA)
           └──> Phase 5: User Story 3 (P3 - Estados de Carregamento e Vazio)
                   └──> Phase 6: Polish & Cross-Cutting Concerns
```

- **Setup (Phase 1)**: Sem dependências — inicia imediatamente.
- **Foundational (Phase 2)**: Depende da instalação de `lucide-vue-next` (T001-T002) — BLOQUEIA as histórias de usuário.
- **User Stories (Phases 3, 4, 5)**: Podem ser executadas em sequência ordenada (P1 → P2 → P3) ou em paralelo após a Phase 2.
- **Polish (Phase 6)**: Executada após a conclusão das histórias de usuário para homologação final.

### Parallel Opportunities

- **Phase 1**: T003 e T004 podem ser implementadas em paralelo.
- **Phase 2**: T005, T006, T007 e T008 trabalham em arquivos independentes e podem ser implementadas em paralelo.
- **Phase 3**: T010 a T016 atuam em arquivos Vue distintos e podem ser implementadas em paralelo.
- **Phase 4**: T017 a T022 operam em arquivos isolados e podem ser implementadas em paralelo.
- **Phase 5**: T023 a T026 atuam em views distintas e podem ser implementadas em paralelo.

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Concluir Setup (T001–T004) e Foundational (T005–T008).
2. Executar User Story 1 (T009–T016): Substituição de 100% dos emojis por Lucide Icons.
3. **Validar MVP**: A interface atinge imediatamente nível visual profissional e editorial sóbrio.

### Incremental Delivery
1. Setup + Foundational → Componentes base prontos.
2. US1 → Emojis erradicados e Lucide Icons ativos (MVP).
3. US2 → "Fichamento da Fonte" e eliminação de termos de IA.
4. US3 → Empty states acolhedores e skeletons fluidos.
5. Polish → Verificação global de testes e build 100% verde.
