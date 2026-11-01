# Tasks — F0.10.01: Header Leve e Variante Neutra de Botão

**Input**:
- [spec.md](spec.md): US1 a US3, FR-001 a FR-010, SC-001 a SC-005;
- [plan.md](plan.md): decisões técnicas 1 a 8, arquivos, testes e verificação.

**Status**: T001–T018 concluídas em 2026-11-01; T019 concluída com o aceite do usuário.

Caminhos relativos a `C:\Users\User\caderno`; `F/` = `caderno-leitura-0.1/frontend/`.

**Regras em todas as tarefas**:
- **Dados:** só fictícios; a conferência visual usa o servidor de validação (porta 8010, banco temporário em
  `scratchpad/visual/`).
- **Banco:** nenhuma migração; o `pytest` roda com `CADERNO_DATABASE_PATH` descartável, `LEITORUM_STORAGE_ROOT=""`
  e `LEITORUM_SECONDARY_BACKUP_DIR=""`. Nada toca o banco ativo nem o `D:\`.
- **Cores:** só tokens existentes; nenhum hex novo.
- **Build:** nunca rodar `npm run build` junto com o `pytest`.
- **Quebras de linha:** preservar LF dos arquivos tocados (o `core.autocrlf` converte no commit).
- `[P]` = pode ser feita em paralelo com as outras `[P]` da mesma fase (arquivos diferentes).

---

## Phase 1: Setup

- [x] T001 Linha de base: `npm test`, `npm run build` e `pytest` no estado atual, registrando os totais.
- [x] T002 Confirmar que nenhuma classe `quiet` existe em `F/src/` (busca em `.vue`, `.css` e `.ts`).
- [x] T003 Decidir a FR-010: se a reformulação visual da landing (sem commit desde 2026-10-29) entrar antes desta
  feature, a T016 fica; se não, a T016 sai deste commit e vai junto com a landing.

## Phase 2: Fundação (bloqueia as fases 3 e 4)

- [x] T004 Teste que falha primeiro: criar `F/tests/feature-092-header-leve.test.mjs` com as 5 verificações do
  plano: posição e conteúdo das 3 regras `.quiet`; classe `quiet` nos controles da FR-003; "Capturar" sem ela;
  modo de visualização ligado a `!active`; nenhum hex novo nos estilos tocados. Rodar e ver falhar.
- [x] T005 `F/src/appearance-advanced.css`: as 3 regras `.quiet` (base, hover, disabled) logo depois do bloco
  `data-button-width='block'`, com `--quiet-bg`/`--quiet-border`, `width: auto` e `flex: 0 0 auto` (plano,
  decisões 2 a 4). Rodar a parte 1 do teste da T004.

## Phase 3: User Story 1 — Header leve (P1)

- [x] T006 [P] [US1] `F/src/components/layout/GlobalHeader.vue`:
  - `quiet` na busca e nas notificações;
  - na busca, `<span class="search-label">Buscar</span>` e `<kbd class="search-kbd">Ctrl K</kbd>`, visíveis só em
    ≥ 1024 px; abaixo disso, botão de 36 px só com ícone;
  - `--quiet-bg: var(--color-surface-soft, var(--color-surface))` e `--quiet-border: var(--color-border)` locais
    na busca;
  - `aria-label` e atalho sem mudança; "Capturar" intocado.
- [x] T007 [P] [US1] `F/src/components/layout/NavigationTabs.vue`: `quiet` no `.more-trigger-btn`; o estado
  `.active` do menu aberto continua com `--color-surface-hover`.
- [x] T008 [P] [US1] `F/src/components/sync/SyncStatusBadge.vue`: `quiet`; ponto de estado de 8 px `aria-hidden`
  no canto do ícone, com `--color-link` (sincronizando), `--color-warning` (offline) e `--color-error-marker`
  (conflito ou erro); remover os fallbacks `#b45309` e `#dc2626`; `title` e `aria-label` sem mudança.
- [x] T009 [P] [US1] `F/src/components/layout/UserDropdown.vue`: `quiet` no `.user-trigger-btn`.

**Checkpoint US1**: partes 2 e 3 do teste da T004 passam para o header.

## Phase 4: User Story 2 — Controles neutros nas páginas de livros (P2)

- [x] T010 [P] [US2] `F/src/views/BookView.vue`: `quiet` nas 3 `.pill-tool-btn` (mover para trás, mover para
  frente, editar); `aria-label` e a regra de 44 px no celular (l. 1666) sem mudança.
- [x] T011 [P] [US2] `F/src/components/LibraryToolbar.vue`:
  - `quiet` em `.search-clear-btn`, `.category-clear-btn` e `.clear-filters-btn`;
  - nos dois `.view-mode-btn`: `:class="{ active: viewMode === 'grid', quiet: viewMode !== 'grid' }"` (e o par
    equivalente para `list`);
  - trocar `var(--muted, #888)`, `var(--text, #111)` e `var(--bg-hover, rgba(0, 0, 0, 0.05))` por
    `--color-muted`, `--color-text` e `--color-surface-hover`; em `.clear-filters-btn`, usar `--color-link` sem
    o fallback `#3b82f6`.

**Checkpoint US2**: o teste da T004 passa inteiro.

## Phase 5: User Story 3 — Sem regressão (P1) e testes de contraste

- [x] T012 [US3] `F/tests/theme-contrast-tokens.test.mjs`: novo par "texto sobre a pílula de busca"
  (`--color-text` sobre `--color-surface-soft`) em todos os temas; confirmar que os pares `--color-text` sobre
  `--color-surface` e `--color-hover-text` sobre `--color-surface-hover` já cobrem a variante.
- [x] T013 [US3] `npm test` e `npm run build`; depois, sozinho, `pytest` com banco descartável. Comparar com a
  linha de base da T001; se algum teste antigo falhar, corrigir a causa, nunca afrouxar o teste.

## Phase 6: Verificação no navegador

- [x] T014 Servidor de validação sem `auth-on`. Em `/livros` e `/livros/:id`, script que percorre 10 temas × 6
  configurações de superclasse e os estilos `outline`, `ghost` e `block`, e registra o fundo calculado dos
  controles da FR-003 e de "Capturar". Esperado: neutros diferentes de `--color-accent` e "Capturar" igual
  (SC-001, SC-002). Painel oculto: forçar o estado final das animações por script, como nas correções anteriores.
- [x] T015 Hover simulado (reescrita de `:hover` por `.__fh`) nos mesmos controles, nos 10 temas: zero pares de
  texto abaixo de 4,5:1 (FR-008). Larguras 1366, 768 e 375 px: sem rolagem horizontal, rótulo da busca só em
  ≥ 1024 px, `.pill-tool-btn` com 44 px no celular (SC-003). Capturas de Papel Fosco, Noite Suave e Voltagem.

## Phase 7: Landing (condicional, ver T003)

- [x] T016 [P] `F/src/components/landing/HeroShowcase.vue` e `ThemeShowcase.vue`: trocar as regras de reforço caso
  a caso pela classe `quiet` (controles do carrossel, setas e chips de tema; o chip ativo mantém o anel de
  destaque). Rodar `npm test` e conferir a landing em 1280 e 375 px.

## Phase 8: Fechamento

- [x] T017 `caderno-leitura-0.1/docs/contexto/RETOMADA.md`: seção "F0.10.01 — Header leve", com causa, solução,
  arquivos e resultados das verificações.
- [x] T018 Marcar as tarefas concluídas aqui e o status da spec como concluída; reportar ao usuário com os totais
  e as capturas, e aguardar o aceite antes do commit.
- [x] T019 Depois do aceite: commit atômico em português, por exemplo `feature — header leve e variante neutra de
  botão`, sem `query`, `stop` e `.claude/`.

---

## Dependências

- T004 → T005 → (T006, T007, T008, T009, T010, T011 em paralelo) → T012 → T013 → T014 → T015 → T017 → T018 → T019.
- T016 depende da T003 e da T005; se entrar, precisa estar pronta antes da T013.

## Fora destas tarefas

Tudo o que a spec põe fora do escopo: o resto do Roadmap 0.10, a troca da regra global por opt-in, o status de
leitura do livro e os documentos dos roadmaps 0.10, 0.11 e 1.0.
