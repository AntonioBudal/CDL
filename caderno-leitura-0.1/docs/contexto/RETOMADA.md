# Registro de Retomada e Transição

Este documento registra as evidências consolidadas em cada ciclo de trabalho e define o ponto exato de continuação para a próxima sessão.

---

## Sessão: Transição e Auditoria Inicial (15/09/2026)

### Evidências Verificadas nesta Rodada
1. **Mapeamento de Diretórios:**
   - Raiz do Git: `C:\Users\User` (Git iniciado no perfil de usuário).
   - Raiz do Workspace Antigravity: `C:\Users\User\caderno`.
   - Raiz Real da Aplicação: `C:\Users\User\caderno\caderno-leitura-0.1`.
2. **Ambiente e Runtimes:**
   - Python 3.13.15 instalado (`py -3.13`) e presente em `backend\.venv\Scripts\python.exe`.
   - Node.js v24.14.1 e npm 11.11.0 disponíveis.
   - uv 0.11.21 e GitHub Spec Kit CLI 1.0.1 disponíveis.
3. **Spec Kit & Antigravity:**
   - Integração `agy` validada com sucesso via `specify integration status` na raiz real (`caderno-leitura-0.1`) e refletida no workspace.
   - Constituição oficial definida em `.specify/memory/constitution.md`.
   - Regras do Antigravity configuradas em `.agents/rules/caderno-leitura.md`.
   - Regras gerais para agentes estabelecidas em `AGENTS.md`.
4. **Auditoria do Patch `infra-0.3.patch`:**
   - Análise de bytes confirmou que a linha 1957 encerra sem caractere de quebra de linha (`\n`) e sem marcação `\ No newline at end of file`.
   - O comando histórico `git apply --check` abortou corretamente sem aplicar qualquer alteração.
   - A base de código está limpa, intacta e consistente com a consolidação da Alpha 0.1 / 0.2.
5. **Banco de Dados e Acervo:**
   - Banco de produção: `backend/data/caderno.db` (32.768 bytes, 10/09/2026).
   - Nenhum arquivo WAL/SHM pendente.
   - O acervo foi preservado sem leitura de registros ou vazamento de dados.
6. **Esquema e Migrações:**
   - Alembic aponta para migração única: `0001_initial_schema.py`.
   - Esquema atual contempla `books`, `chapters` e `studies`.
7. **Recursos de 0.2 Identificados no Código:**
   - `iniciar.py`: Inicialização em rede e QR Code no terminal.
   - `backend/app/services/backups.py` e `routers/backups.py`: Endpoint `/api/backup` já implementa snapshot consistente via SQLite Backup API (`original.backup(snapshot)`).
8. **Preservação de Código:**
   - Nenhuma linha de código da aplicação (`backend/app`, `frontend/src`, `iniciar.py`, `instalar.py`) foi modificada.
9. **Estado das Tarefas do Roadmap 0.3:**
   - **T01 a T10 permanecem estritamente NÃO INICIADAS.**

---

---

## Sessão: Especificação da Feature 001 (17/09/2026)

### Evidências Verificadas nesta Rodada
1. **Especificação Gerada e Clarificada:**
   - Feature: `001-snapshot-protecao-acervo` (vinculada à fundação de segurança de T09 e T10).
   - Diretório: `specs/001-snapshot-protecao-acervo/`.
   - Arquivo principal: `spec.md` (Status: Ready for Planning).
2. **Decisões de Design Alinhadas com o Usuário:**
   - Local e nomenclatura dos snapshots: subdiretório dedicado `backend/data/backups/` com carimbo UTC `caderno-pre-migracao-YYYYMMDD-HHMMSS.db`.
   - Política de retenção: rotação automática mantendo os 5 snapshots pré-migração mais recentes, sem tocar em backups manuais.
3. **Validação do Checklist:**
   - `specs/001-snapshot-protecao-acervo/checklists/requirements.md`: 100% dos critérios de qualidade e completude atendidos.
4. **Governança e Estado das Tarefas:**
   - Todas as dez tarefas da 0.3 (T01 a T10) permanecem **NÃO INICIADAS**.
   - Nenhuma linha de código de aplicação ou migração de banco foi executada.
5. **Configuração do Spec Kit:**
   - `.specify/feature.json` atualizado com o diretório ativo da feature.

---

---

## Sessão: Planejamento Técnico da Feature 001 (17/09/2026)

### Evidências Verificadas nesta Rodada
1. **Planejamento Técnico Completo (Fase 0 e Fase 1):**
   - Feature: `001-snapshot-protecao-acervo`.
   - `plan.md`: Plano de implementação com Technical Context e Constitution Check (100% PASS).
   - `research.md`: Decisões técnicas D1 a D6 consolidadas (SQLite Backup API, caminhos canônicos absolutos, retenção de 5 cópias, hook no Alembic e inspeção quantitativa não destrutiva).
   - `data-model.md`: Entidades lógicas `DatabaseLocation`, `PreUpgradeSnapshot` e `SnapshotInspectionReport`.
   - `contracts/`: Especificados `contracts/backup-service.md` e `contracts/cli-maintenance.md`.
   - `quickstart.md`: 4 cenários executáveis com dados sintéticos e bancos descartáveis em `tmp_path`.
2. **Governança e Estado das Tarefas:**
   - **T01 a T10 permanecem estritamente NÃO INICIADAS.**
   - Nenhuma alteração foi realizada no código-fonte da aplicação nem no banco de produção.

---

---

## Sessão: Decomposição em Tarefas da Feature 001 (17/09/2026)

### Evidências Verificadas nesta Rodada
1. **Geração de Tarefas (`tasks.md`):**
   - Feature: `001-snapshot-protecao-acervo`.
   - Arquivo: `specs/001-snapshot-protecao-acervo/tasks.md`.
   - Total de tarefas: 18 tarefas atômicas sequenciadas por histórias de usuário e com caminhos exatos de arquivos.
   - Distribuição:
     - Setup & Foundational (T001–T005): 5 tarefas (resolução canônica, caminhos absolutos e modularização da primitiva de backup).
     - US1 (P1 - MVP, T006–T010): 5 tarefas (testes de snapshot, orquestrador pré-migração, rotação de 5 cópias e hook no Alembic).
     - US2 (P2, T011–T013): 3 tarefas (testes de caminhos com acentos/espaços e integração em `iniciar.py`).
     - US3 (P3, T014–T016): 3 tarefas (testes de integridade sem vazamento e utilitário CLI de verificação).
     - Polish (T017–T018): 2 tarefas (validação de quickstart e documentação).
2. **Governança e Estado das Tarefas do Roadmap:**
   - **T01 a T10 permanecem estritamente NÃO INICIADAS.**
   - Nenhum código de aplicação ou migração de banco foi executado.

---

---

## Sessão: Implementação da Feature 001 (17/09/2026)

### Evidências Verificadas nesta Rodada
1. **Implementação da Feature 001 (`001-snapshot-protecao-acervo`):**
   - Infraestrutura de segurança pré-migração entregue com sucesso (fundação crítica para T09 e T10).
   - `backend/app/core/config.py`: Implementado `get_backup_dir()` e validação estrita de caminho absoluto canônico para `get_database_path()`.
   - `backend/app/services/backups.py`: Primitiva `create_database_backup` modularizada aceitando `source` customizado, com limpeza de fragmentos atômica e verificação de chaves.
   - `backend/app/services/maintenance.py`: Criado módulo de manutenção completo contendo:
     - `create_pre_upgrade_snapshot()`: Criação consistente com carimbo UTC em `backend/data/backups/`.
     - `ensure_pre_upgrade_snapshot()`: Barreira atômica pré-migração que aborta a operação caso o backup falhe.
     - `rotate_pre_upgrade_snapshots()`: Política de retenção automática dos 5 snapshots mais recentes, com preservação de backups manuais.
     - `inspect_snapshot()`: Diagnóstico e contagem quantitativa estrita (`SELECT COUNT(*)`), sem qualquer leitura ou vazamento de campos textuais do acervo.
     - Interface de linha de comando (`verificar-snapshot` e `criar-snapshot`).
   - `backend/migrations/env.py`: Hook pré-migração integrado ao ciclo de vida do Alembic (`run_migrations_online` e `run_migrations_offline`), garantindo proteção antes de qualquer DDL.
   - `iniciar.py`: Tratamento defensivo de erro em caminhos na inicialização.
2. **Validação Automatizada com Isolamento Estrito (tmp_path):**
   - Criado `backend/tests/test_backup_pre_upgrade.py` com 11 testes cobrindo todos os cenários do Quickstart (100% PASS).
   - Suíte de regressão do backend: 77 testes executados com sucesso (1 skipped de symlink Windows, 0 falhas).
   - Suíte de testes do frontend: 35 testes executados com sucesso (0 falhas).
3. **Privacidade e Integridade dos Dados:**
   - O banco de produção `backend/data/caderno.db` foi mantido 100% isolado e intocado.
   - Nenhum texto confidencial de acervo foi lido, logado ou exposto.
4. **Governança e Estado das Tarefas do Roadmap 0.3:**
   - **REGRA DE ESTADO: As dez tarefas T01 a T10 do Roadmap 0.3 continuam rigorosamente NÃO INICIADAS.**
   - A Feature 001 entregue nesta sessão cumpre a função de fundação de segurança e infraestrutura prévia indispensável antes de qualquer migração do acervo.

---

## Próximo Passo Recomendado

1. Revisar o relatório de entrega e walkthrough da Feature 001.
2. Com a primitiva de backup atômico e proteção do acervo plenamente operacional, definir junto ao usuário o início planejado da primeira tarefa do Roadmap 0.3 (iniciando pela especificação formal via `/speckit-specify`).

---

## Sessão: Implementação da Feature 002 (17/09/2026)

### Evidências Verificadas nesta Rodada
1. **Implementação Completa da Feature 002 (`002-edicao-livros-estudos`):**
   - **User Story 1 (P1 MVP — Edição de Metadados de Livros):**
     - Novos campos `subtitle`, `year`, `created_at`, `updated_at` no modelo `Book` e migração Alembic incremental `0002_add_book_metadata_and_concurrency.py`.
     - Endpoint `PATCH /api/books/{book_id}` com validação de campos obrigatórios/opcionais (`title` obrigatório e não vazio; `author`, `subtitle` e `year` opcionais no intervalo 1000..2100).
     - Componente modal acessível `BookEditModal.vue` com controle por teclado (foco automático, navegação e fechamento com Escape).
     - Integração na tela `BookView.vue` com exibição de subtítulo, ano e botão "Editar livro".
   - **User Story 2 (P2 — Edição e Reordenação de Capítulos):**
     - Endpoint de renomeação `PATCH /api/books/{book_id}/chapters/{chapter_id}` com validação não vazia e atualização de `updated_at`.
     - Endpoint de reordenação atômica `POST /api/books/{book_id}/chapters/{chapter_id}/move` com direções `"up"` e `"down"`, normalização sequencial e proteção de limites (400 ao ultrapassar extremidades).
     - Controles integrados de movimentação (▲ / ▼) e renomeação inline na lista de capítulos em `BookView.vue`.
   - **User Story 3 (P3 — Blindagem de Concorrência e Imutabilidade de Origem):**
     - Concorrência otimista via `expected_updated_at` e utilitário `check_optimistic_lock()` retornando `409 Conflict`.
     - Imutabilidade absoluta da resposta de origem (`source_response` nunca aceita no PATCH de estudos e mantida inalterada no banco).
     - Proteção contra perda de dados em concorrência no frontend: `StudyEditView.vue` e `useStudyEdit.ts` exibem banner de aviso em caso de HTTP 409 e preservam 100% dos dados digitados no formulário.
2. **Validação Automatizada e Cobertura (100% PASS):**
   - Criados 14 testes de integração isolados em `backend/tests/test_edit_acervo.py` cobrindo todos os cenários de `quickstart.md` e regras da feature (100% aprovados).
   - Suíte de regressão backend: 92 testes aprovados (1 skipped), 0 falhas.
   - Suíte de testes frontend: 36 testes aprovados (1 novo teste de conflito 409), 0 falhas.
   - Build do frontend: `npm run build` executado com sucesso (TypeScript + Vite).
3. **Privacidade e Integridade dos Dados:**
   - O banco de produção `backend/data/caderno.db` foi mantido 100% isolado e intocado.
   - Todos os testes rodaram com bancos SQLite descartáveis em `tmp_path`.
   - Nenhum dado privado do usuário foi lido ou exposto.
4. **Governança e Estado das Tarefas do Roadmap 0.3:**
   - **REGRA DE ESTADO: As dez tarefas T01 a T10 do Roadmap 0.3 continuam registradas como NÃO INICIADAS.**
   - Todas as 22 tarefas atômicas de `specs/002-edicao-livros-estudos/tasks.md` foram 100% concluídas e marcadas com `[X]`.

---

## Próximo Passo Recomendado

1. Validar visualmente a interface ou iniciar o ciclo da próxima fatia de evolução do Caderno de Leitura via GitHub Spec Kit.

---

## Sessão: Implementação da Feature 003 (18/09/2026)

### Evidências Verificadas nesta Rodada
1. **Implementação Completa da Feature 003 (`003-lixeira-soft-delete`):**
   - **User Story 1 (P1 MVP — Envio para a Lixeira e Proteção contra Exclusão Acidental):**
     - Campo `deleted_at: Mapped[datetime | None]` com índices `ix_books_deleted_at` e `ix_studies_deleted_at` nos modelos `Book` e `Study`.
     - Migração Alembic incremental `0003_add_trash_soft_delete.py` com suporte a SQLite e rollback seguro.
     - Serviço centralizado `trash_service.py` (`trash_book`, `trash_study`, `restore_book`, `restore_study`, `permanent_delete_book`, `permanent_delete_study`, `get_trash_items`, `empty_trash`, `purge_expired_trash`).
     - Endpoints `POST /api/books/{id}/trash` e `POST /api/studies/{id}/trash`.
     - Filtro `WHERE deleted_at IS NULL` integrado em todas as consultas normais de acervo ativo (`/books`, `/books/{id}`, `/chapters/{id}/studies`, `/studies/{id}`).
     - Componente reutilizável `TrashConfirmModal.vue` com acessibilidade por teclado (Escape/Enter), armadilha de foco e variantes perigosas.
     - Ações de mover para a lixeira integradas nas visualizações `BookView.vue` (cabeçalho do livro e lista de estudos) e `StudyView.vue`.
   - **User Story 2 (P2 — Visualização da Lixeira e Restauração de Itens):**
     - Router dedicado `backend/app/routers/trash.py` com `GET /api/trash` retornando contagem agregada, livros e estudos com dias restantes até o expurgo de 30 dias.
     - Endpoints de restauração `POST /api/books/{id}/restore` e `POST /api/studies/{id}/restore`.
     - Suporte a restauração em cascata ascendente: ao restaurar um estudo cujo livro pai estava na lixeira, reativa automaticamente o livro e capítulo no acervo ativo.
     - Tela dedicada `TrashView.vue` com filtros por abas (Todos, Livros, Estudos Individuais), contadores de dias restantes e avisos visuais de expurgo iminente.
     - Rota `/lixeira` configurada em `router/index.ts` e link de acesso com ícone SVG no cabeçalho global em `App.vue`.
   - **User Story 3 (P3 — Exclusão Definitiva Consciente e Esvaziamento da Lixeira):**
     - Endpoints de exclusão definitiva atômica: `DELETE /api/books/{id}/permanent` (com remoção de capítulos e estudos subordinados sem violação de chaves estrangeiras) e `DELETE /api/studies/{id}/permanent`.
     - Endpoints de gerenciamento em massa: `POST /api/trash/empty` e `POST /api/trash/purge-expired`.
     - Rotina de purga automática de 30 dias integrada no ciclo de vida da aplicação (`lifespan` em `main.py`) e na leitura de `GET /api/trash`.
     - Diálogos de confirmação enfáticos para exclusão definitiva e esvaziamento total da lixeira em `TrashView.vue`.
2. **Validação Automatizada e Cobertura (100% PASS):**
   - Criados 9 testes de integração herméticos em `backend/tests/test_trash_soft_delete.py` cobrindo todos os 5 cenários do `quickstart.md` (100% aprovados).
   - Suíte completa de regressão do backend: 102 testes aprovados (1 skipped), 0 falhas.
   - Suíte de testes do frontend: 36 testes aprovados, 0 falhas.
   - Build de produção do frontend: `npm run build` executado com sucesso (TypeScript + Vite, sem erros de tipagem).
3. **Privacidade e Integridade dos Dados:**
   - O banco de produção `backend/data/caderno.db` foi mantido 100% isolado e intocado.
   - Todos os testes foram executados com bancos SQLite descartáveis em diretórios efêmeros (`tmp_path`).
   - Nenhum dado privado do acervo do usuário foi lido ou exposto.
4. **Governança e Estado das Tarefas do Roadmap 0.3:**
   - **REGRA DE ESTADO: As dez tarefas T01 a T10 do Roadmap 0.3 continuam registradas como NÃO INICIADAS.**
   - Todas as 31 tarefas atômicas de `specs/003-lixeira-soft-delete/tasks.md` foram 100% concluídas e marcadas com `[X]`.

---

## Próximo Passo Recomendado

1. Apresentar o relatório da Feature 003 e aguardar instruções do usuário para os próximos passos no Caderno de Leitura.

---

## Sessão: Implementação das 5 Superclasses de Interface (18–19/09/2026)

### Evidências Verificadas nesta Rodada
1. **Implementação Completa do Ecossistema das 5 Superclasses de Interface:**
   - **Feature 007 (Zero-G — Flutuante & Magnética):** Físicas de levitação suave, elevação multicamada, sombras amplas difusas, atração magnética via composable `useMagneticHover.ts` e amortecimento elástico (`zero-g.css`).
   - **Feature 008 (Mecânica — Tátil & Responsiva):** Física tátil de resposta imediata, cantos facetados de 2px, sombras sólidas de 3px sem blur, afundamento mecânico push-down (+3px), corte seco de rota (100ms) e switches rápidos em 60ms (`mecanica.css`).
   - **Feature 009 (Invisível — Silenciosa & Editorial) & Poda de Ajustes:** Desmaterialização de caixas e sombras, microinterações horizontais de leitura (+4px) e sublinhado progressivo, transição de rota em cascata temporal (*staggered fade-up*) (`invisivel.css`). Poda limpa dos controles redundantes de `style`, `surface` e `button-style` com retrocompatibilidade e normalização tolerante.
   - **Feature 010 (Dimensional — Cinemática & Profunda):** Ponto de fuga óptico de 1000px, inclinação 3D delimitada nos cartões (rotateX: ±1.5°, rotateY: ±2.0°), sombras dinâmicas projetadas no sentido oposto ao cursor, relevo multicamada escalonado (capa 1px, título 2px, marcadores 3px) e aproximação Z cinemática em ~300ms (`dimensional.css`).
   - **Feature 011 (Monolítica — Pesada & Solene):** Estética brutalista e arquivo perpétuo, cantos estritamente retos (`border-radius: 0px !important`), eliminação total de sombras difusas (`box-shadow: none !important`), hierarquia por bordas sólidas (`calc(var(--border-width, 1px) + 1px)`), microinterações ponderadas (~380ms), inversão de alto contraste no clique (`:active`), dissolução de rotas lapidar em opacidade (~380ms) e blindagem estrita de leitura (`monolitica.css`).
2. **Validação Automatizada e Cobertura (100% PASS):**
   - Suíte de testes do frontend: **71 testes unitários aprovados** em `frontend/tests/superclasses.test.mjs` (100% verde).
   - Build de produção do frontend: `npm run build` (`vue-tsc -b && vite build`) executado com sucesso em 1.60s sem erros de tipagem.
3. **Privacidade e Integridade dos Dados:**
   - O banco de produção `backend/data/caderno.db` foi mantido **100% isolado, intacto e sem modificações**.
   - Nenhum dado privado do acervo do usuário foi lido ou exposto.
4. **Governança e Estado das Tarefas do Roadmap 0.3:**
   - **REGRA DE ESTADO: As dez tarefas T01 a T10 do Roadmap 0.3 continuam registradas como NÃO INICIADAS.**
   - Todas as tarefas atômicas das Features 007, 008, 009, 010 e 011 foram 100% concluídas e marcadas com `[X]`.

---

## Próximo Passo Recomendado

1. Validar visualmente as 5 superclasses no navegador via `iniciar.py` ou `npm run dev`.
2. Iniciar o ciclo de especificação conjunta de infraestrutura consistente para T09 e T10 da versão 0.3 (Backup consistente e restauração atômica pré-migração).

---

## Sessão: Feature 012 — Roteamento, Fonte Global e Limpeza de Ajustes (19/09/2026)

### Evidências Verificadas nesta Rodada
1. **Implementação da Feature 012 (Roteamento, Fonte Global e Limpeza de Ajustes):**
   - **User Story 1 (P1 — Navegação Fluida e Confiável sem Telas Vazias):**
     - Identificada a causa-raiz da falha de renderização: transições `<Transition mode="out-in">` do Vue 3 falhavam silenciosamente ao desmontar/montar views com múltiplos nós raiz (fragmentos no `<template>`).
     - Configurado `:key="$route.fullPath"` no `<component :is="Component" :key="$route.fullPath" />` sob `<Transition>` em `App.vue`.
     - Envolvidas todas as 5 visualizações que continham fragmentos em nós raiz únicos: `BooksView.vue` (`<div class="books-view">`), `BookView.vue` (`<div class="book-view">`), `StudyView.vue` (`<div class="study-view">`), `StudyEditView.vue` (`<div class="study-edit-view">`) e `ImportView.vue` (`<div class="import-view">`).
   - **User Story 2 (P2 — Herança Global e Preview Imediato da Tipografia Escolhida):**
     - Elevada a variável `--font-reading` para a interface global vinculando `--font-ui: var(--font-reading);` em `tokens.css`.
     - Aplicada de forma irrestrita a regra `font-family: var(--font-reading)` a `:root, body, #app, button, input, select, textarea, code, pre` em `style.css`, proporcionando preview imediato de qualquer família de fontes em toda a interface do sistema sem recarregar a página.
   - **User Story 3 (P3 — Poda de Ajustes Redundantes, Purga de `localStorage` e Renumeração Limpa):**
     - Excluídas as 3 opções redundantes absorvidas pelas Superclasses: `5. Movimento` (`motion`), `7. Botões` (`button-width`) e `8. Abas` (`tabs`).
     - Removidos tipos legados em `appearance.d.ts`.
     - Atualizado bootstrap para a versão 72 (`appearance-bootstrap.js`), limpando atributos `data-motion`, `data-button-width`, `data-tabs` do `<html>` e purgando ativamente chaves obsoletas do `localStorage` na inicialização (`caderno.aparencia.v2`).
     - Renumerados sequencialmente os 7 grupos restantes de 1 a 7 (1. Cor de destaque, 2. Densidade, 3. Leitura, 4. Marcação, 5. Acervo, 6. Largura da interface, 7. Superclasse de Interface).
     - Atualizados os textos de dicas contextuais em `AppearanceControls.vue`.
2. **Validação Automatizada e Cobertura (100% PASS):**
   - Suíte de testes do frontend: **74 testes unitários aprovados** em `frontend/tests/superclasses.test.mjs` (100% verde).
   - Build de produção do frontend: `npm run build` (`vue-tsc -b && vite build`) executado com sucesso em 1.94s sem erros de tipagem.
3. **Privacidade e Integridade dos Dados:**
   - O banco de produção `backend/data/caderno.db` foi mantido **100% isolado, intacto e sem modificações**.
   - Nenhum dado privado do acervo do usuário foi lido ou exposto.
4. **Governança e Estado das Tarefas do Roadmap 0.3:**
   - **REGRA DE ESTADO: As dez tarefas T01 a T10 do Roadmap 0.3 continuam registradas como NÃO INICIADAS.**
   - Todas as 20 tarefas atômicas de `specs/012-roteamento-fonte-ajustes/tasks.md` foram 100% concluídas e marcadas com `[X]`.

---

## Próximo Passo Recomendado

1. Testar e navegar pelo Caderno de Leitura em execução local via `iniciar.py` ou `npm run dev`.
2. Iniciar o ciclo de especificação de infraestrutura consistente para T09 e T10 da versão 0.3 (Backup consistente e restauração atômica pré-migração).

---

## Sessão: Feature 013 — Dashboard de Leitura com Calendário e Timeline (19/09/2026)

### Evidências Verificadas nesta Rodada
1. **Implementação da Feature 013 (Dashboard de Leitura com Calendário e Timeline — T06 do Roadmap 0.3):**
   - **User Story 1 (P1 — Visão Geral de Produtividade e Métricas Principais — MVP):**
     - Criados schemas Pydantic de entrada e saída em `backend/app/schemas/dashboard.py` (`DashboardSummary`, `HeatmapPoint`, `TimelineItem`, `DashboardResponse`).
     - Criadas interfaces TypeScript correspondentes em `frontend/src/types.ts` e método `getDashboard` no cliente HTTP `frontend/src/services/api.ts`.
     - Implementado serviço de agregação direta em `backend/app/services/dashboard_service.py` com cálculo de métricas (livros ativos, estudos ativos, total de dias de leitura, média de estudos/livro e streak consecutivo) sem alteração nem migração no banco de dados ativo.
     - Implementado router `GET /api/dashboard` com suporte a `tz_offset`, `days`, `date` e `limit` em `backend/app/routers/dashboard.py` e registrado em `backend/app/main.py`.
     - Registrada a rota `/dashboard` em `frontend/src/router/index.ts` e inserido o atalho de navegação com ícone SVG em `frontend/src/App.vue`.
     - Criada a visualização `frontend/src/views/DashboardView.vue` com envoltório de nó raiz único `<div class="dashboard-view wrap">`, cartões de métricas responsivos e estado vazio acolhedor.
   - **User Story 2 (P2 — Mapa de Calor Responsivo e Frequência em Calendário):**
     - Implementada a projeção de datas no `dashboard_service.py` para gerar pontos do heatmap com 4 níveis de intensidade (0 a 3).
     - Criado componente `frontend/src/components/HeatmapCalendar.vue` com grade de semanas e dias, tooltips por data, suporte a modo E-Ink monocromático e estilização nativa via `color-mix` harmonizada com as Superclasses.
     - Implementado recorte responsivo adaptativo com alternância entre visualização compacta (4 meses) e completa (12 meses com scroll horizontal) para dispositivos móveis.
   - **User Story 3 (P3 — Linha do Tempo Cronológica de Atividades Recentes e Filtros):**
     - Implementada consulta da timeline no `dashboard_service.py` abrangendo criação de livros, criação de estudos e edição de anotações (> 60s), com filtro `?date=YYYY-MM-DD` e exclusão estrita de itens da lixeira.
     - Integrada a timeline em `DashboardView.vue` com badges semânticos de ação, links diretos de leitura e chip de filtro ativo com limpeza.
     - Criada suíte de testes frontend em `frontend/tests/dashboard.test.mjs`.
2. **Validação Automatizada e Cobertura (100% PASS):**
   - **Backend**: 6 testes automatizados específicos em `backend/tests/test_dashboard.py` (e 128 testes na suíte geral do backend) aprovados com 100% de sucesso.
   - **Frontend**: 78 testes automatizados aprovados via `npm test` (incluindo `frontend/tests/dashboard.test.mjs`).
   - **Build**: Compilação estrita de tipos TypeScript e empacotamento Vite via `npm run build` executados com sucesso (0 erros).
3. **Privacidade e Integridade dos Dados:**
   - O banco de produção `backend/data/caderno.db` foi mantido **100% isolado, intacto e sem modificações**.
   - Zero migrações necessárias no SQLite local; cálculo executado via agregação on-the-fly sobre tabelas existentes.
4. **Governança e Estado das Tarefas do Roadmap 0.3:**
   - **REGRA DE ESTADO: As dez tarefas T01 a T10 do Roadmap 0.3 continuam registradas como NÃO INICIADAS.**
   - Todas as 24 tarefas atômicas de `specs/013-dashboard-calendario-timeline/tasks.md` foram 100% concluídas e marcadas com `[X]`.

---

## Sessão: Planejamento Arquitetural e Emissão do Roadmap 0.4 (19/09/2026)

### Evidências Verificadas nesta Rodada
1. **Emissão Oficial do Roadmap 0.4 (`ROADMAP-0.4.md`):**
   - Documento oficial criado e espelhado em:
     - `docs/contexto/ROADMAP-0.4.md`
     - `caderno-leitura-0.1/docs/contexto/ROADMAP-0.4.md`
     - `ROADMAP-0.4.md` (raiz do repositório).
   - Definição completa das 10 features estruturantes (**F01 a F10**):
     - `F01` — Sistema de Visualizações (Grade, Lista, Árvore, Mapa, Canvas)
     - `F02` — Hierarquia Interativa (Árvore expansível, drag-and-drop de reordenação e prevenção formal de ciclos)
     - `F03` — Canvas de Estudos (Espaço 2D infinito, pan, zoom, seleção, minimapa e coordenadas desacopladas)
     - `F04` — Relações entre Estudos (Grafo semântico transversal, backlinks e arestas rotuladas)
     - `F05` — Agrupamento Visual (Projeções modulares por hierarquia, categoria, livro, status, data, cluster e molduras manuais)
     - `F06` — Painéis Redimensionáveis (Split panes ajustáveis, persistência de largura e adaptação mobile)
     - `F07` — Dashboard 2.0 (Cockpit operacional de entrada, retomada rápida de estudos e monitoramento de conexões)
     - `F08` — Busca Global Contextual (Indexação transversal em notas/conceitos com destaque `<mark>` e foco imediato)
     - `F09` — Sistema Visual Profissional (Design sóbrio, substituição total de emojis por iconografia vetorial e erradicação de rótulos de IA)
     - `F10` — Interação Avançada, Movimento e Experiências Visuais (Física inercial, calibração cinemática das Superclasses e renderização acelerada por GPU/WebGL)
2. **Separação Canônica de Responsabilidades (O Quadrilátero do Conhecimento):**
   - Estrutura (Árvore canônica e paternidade de dados).
   - Relações (Grafo semântico transversal com tabela `study_relations`).
   - Agrupamentos (Particionamentos e projeções visuais efêmeras ou molduras do Canvas).
   - Visualizações (Renderers desacoplados e intercambiáveis sem perda de contexto).
3. **Escopo Delimitado e Não-Escopo:**
   - Descartados expressamente da 0.4: Modo Foco / Modo Leitura, Command Palette global / atalhos de teclado e métricas artificiais/gamificação.
4. **Governança e Estado das Features:**
   - **REGRA DE ESTADO: Todas as 10 features (F01 a F10) estão estritamente NÃO INICIADAS.**
   - Nenhuma linha de código de produção, migração de banco ou alteração no schema foi realizada nesta etapa de planejamento.
   - Os dados e banco de produção (`backend/data/caderno.db`) permanecem 100% isolados, protegidos e intactos.
5. **Grafo de Dependências e Ordem Técnica Recomendada:**
   - Ordem sequencial para o fluxo Spec Kit: `F09` → `F06` → `F01` → `F02` → `F04` → `F05` → `F03` → `F07` → `F08` → `F10`.

---

## Sessão: Conclusão do Roadmap 0.4 e Reorganização do Histórico Git (19/09/2026)

### Evidências Verificadas nesta Rodada
1. **Homologação Integral do Roadmap 0.4:**
   - 10 features (F01 a F10) implementadas através do ciclo Spec Kit com 100% de conformidade.
   - Suíte frontend: 223 testes passando (`npm test`).
   - Suíte backend: 199 testes passando, 1 ignorado intencionalmente (`pytest`).
   - Compilação de produção Vite: 0 erros (`npm run build` em 3.07s).
2. **Reconstrução do Histórico Git por Marcos de Roadmap (0.1 a 0.4):**
   - Repositório local inicializado e isolado em `c:\Users\User\caderno\.git`, configurado na branch `main`.
   - Remote oficial configurado: `https://github.com/AntonioBudal/CDL.git`.
   - Cadeia linear de 4 commits autênticos:
     - `485b29a`: `versão 0.1 — base inicial do acervo e estudos` (10/09/2026)
     - `bad8099`: `versão 0.2 — acesso em rede e personalização` (15/09/2026)
     - `3d7fb06`: `versão 0.3 — gestão, visualização e produtividade` (19/09/2026 12:00)
     - `89dc0cd`: `versão 0.4 — navegação espacial, relações e movimento` (19/09/2026 23:20)
   - Zero dados privados ou arquivos `.db`/`.zip` rastreados (`git ls-files` auditado).
3. **Nova Convenção de Versionamento Estabelecida (Roadmap 0.5+):**
   - A partir da versão 0.5: **1 Feature Implementada e Validada = 1 Commit Atômico**.
   - Regra registrada em `docs/HISTORICO-ROADMAPS.md`, `docs/contexto/CONVENCAO-GIT.md` e `AGENTS.md`.

---

## Sessão: Planejamento Arquitetural e Emissão do Roadmap 0.5 (20/09/2026)

### Evidências Verificadas nesta Rodada
1. **Emissão Oficial do Roadmap 0.5 (`ROADMAP-0.5.md`):**
   - Documento oficial criado e espelhado em:
     - `ROADMAP-0.5.md` (raiz do workspace)
     - `docs/contexto/ROADMAP-0.5.md`
     - `caderno-leitura-0.1/docs/contexto/ROADMAP-0.5.md`
   - Definição completa das 10 features estruturantes (**F01 a F10**):
     - `F01` — Fundação Multiusuário e CRUD Geral (Propriedade dos dados `user_id`, migração sem perdas do acervo existente e autorização server-side)
     - `F02` — Autenticação e Sessões (Identidade local, hash adaptativo Argon2id, sessões em cookies HttpOnly/SameSite e controle de dispositivos)
     - `F03` — Conta Google e Vinculação de Identidade (Google Identity Services GIS, claim `sub` estável, ExternalIdentity e suporte a HTTPS Tailscale *.ts.net)
     - `F04` — Sincronização Multidispositivo (PC e celular sincronizados com estado remoto como fonte da verdade e detecção explícita de conflitos HTTP 409)
     - `F05` — Perfil e Privacidade (Identidade pública com `@username` sem vazar e-mails e controles granulares de exposição: Público, Amigos, Privado)
     - `F06` — Sistema de Amizades (Ciclo de vida social completo: solicitar, aceitar, recusar, cancelar, remover, bloquear e busca de descobríveis)
     - `F07` — Compartilhamento e Permissões por Recurso (ACL granular somente-leitura por livro, estudo e dashboard)
     - `F08` — Administração e RBAC (Controle de papéis `ADMIN` vs `USER` validado no servidor e painel administrativo central)
     - `F09` — Notificações e Atividade Social (Feed desacoplado de eventos, solicitações e compartilhamentos com rastreamento de leitura)
     - `F10` — Segurança, Auditoria e Ciclo de Vida da Conta (Rate limiting, audit log sem segredos, desativação/exclusão e portabilidade LGPD/ANPD em ZIP)
2. **Princípios de Arquitetura e Decisões de Engenharia:**
   - O servidor permanece no PC local via `iniciar.py`, atendendo PC e dispositivos móveis (Tailscale).
   - SQLite WAL continua viável para baixa concorrência; camada de dados preparada para eventual migração para PostgreSQL sem refatorar regras de negócio.
   - Compartilhamento é estritamente **Read-Only** nesta versão (edição colaborativa/CRDTs fora de escopo).
3. **Governança e Estado das Features:**
   - **REGRA DE ESTADO: Todas as 10 features (F01 a F10) do Roadmap 0.5 estão estritamente NÃO INICIADAS.**
   - O acervo ativo (`backend/data/caderno.db`) permanece 100% isolado, protegido e intacto.
4. **Grafo de Dependências e Ordem Técnica Sequencial:**
   - Ordem estrita: `F01` → `F02` → `F03` → `F04` → `F05` → `F06` → `F07` → `F08` → `F09` → `F10`.

---

## Sessão: Implementação e Validação da Feature 05 — Perfil e Privacidade (24/09/2026)

### Evidências Verificadas nesta Rodada
1. **Especificação, Arquitetura e Contratos (Spec Kit):**
   - Ciclo formal Spec Kit completado para `specs/032-perfil-e-privacidade/` (`spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/`, `tasks.md`, `checklists/`).
   - Todas as 32 tarefas de `tasks.md` executadas e marcadas como `[X]`.
2. **Backend e Migrações (Alembic):**
   - Modelo relacional `UserProfile` com relacionamento 1:1 com `User` e exclusão em cascata.
   - Migração `0015_add_user_profile.py` com criação de índices e auto-provisionamento para contas existentes.
   - Pipeline de processamento gráfico de avatar via Pillow (`ImageOps.fit`) gerando arquivos quadrados 256x256 WebP em `backend/data/avatars/`.
3. **Validação:**
   - 276 testes de backend passando e 223 testes de frontend passando.

---

## Sessão: Implementação e Validação da Feature 06 — Sistema de Amizades (26/09/2026)

### Evidências Verificadas nesta Rodada
1. **Especificação, Arquitetura e Contratos (Spec Kit):**
   - Ciclo formal Spec Kit completado para `specs/033-sistema-de-amizades/` (`spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/`, `tasks.md`, `checklists/`).
   - Alinhamentos deliberados com o usuário:
     - Q1: A — Recusa de solicitação retorna ao estado neutro (`none`), permitindo novo envio futuro; para impedir em definitivo, utiliza-se o Bloqueio.
     - Q2: A — Hub Social posicionado na barra superior em `/amigos` para usuários autenticados, com 4 abas estruturadas: "Meus Amigos", "Solicitações", "Descobrir Leitores" e "Bloqueados".
     - Q3: A — No perfil público (`/@username`), é exposto unicamente o contador quantitativo (`friends_count`); a listagem nominal é estritamente privada.
   - Todas as 32 tarefas de `tasks.md` executadas e marcadas como `[x]`.
2. **Backend e Migrações (Alembic):**
   - Modelo relacional `Friendship` com par ordenado normalizado `(user_id_a < user_id_b)`.
   - Migração `0016_add_friendships_table.py` com constraints `UNIQUE`, `CHECK` anti-autoamizade e índices compostos de busca.
   - Serviço `friendship_service.py` e router `friends.py` com `commit_changes(session)` em todas as mutações:
     - Resolução automática e atômica de solicitações cruzadas simultâneas.
     - Recusa neutra, cancelamento pelo autor e desfazimento de amizades soberano.
     - Bloqueio unilateral com **blindagem 404 anti-enumeração** e exclusão recíproca em buscas descobríveis.
     - Resumo de contadores consolidados para badges em tempo real (`GET /api/friends/summary`).
3. **Frontend e Experiência do Leitor (Vue 3 / TypeScript):**
   - Composable reativo `useFriends.ts` com gerenciamento de estado e feedback de carregamento.
   - Wrapper de cliente `friendsApi` em `frontend/src/api/friends.ts` e métodos estendidos em `services/api.ts`.
   - Componente tátil `FriendActionButtons.vue` com alvos mínimos de 44px e atributos de acessibilidade WAI-ARIA.
   - Visão centralizada `FriendsView.vue` na rota `/amigos` com 4 abas acessíveis.
   - Navegação global no cabeçalho em `App.vue` com ícone `users` e crachá numérico dinâmico de solicitações pendentes recebidas.
   - Exibição de `friends_count` no perfil público `UserProfileCard.vue`.
4. **Validação e Suítes de Teste:**
   - 284 testes de backend passando (`pytest backend/tests`), incluindo 8 testes dedicados de ponta a ponta em `test_friendships.py`.
   - 230 testes de frontend passando (`npm test`), incluindo suíte dedicada em `friends.test.mjs`.
   - Build de produção do frontend (`npm run build` / `vue-tsc`) 100% aprovado sem erros de tipagem.
   - Commit atômico consolidado: `af45609` (`feature — sistema de amizades`).
5. **Documentação Técnica:**
   - Documento arquitetural criado em `caderno-leitura-0.1/docs/contexto/SISTEMA-DE-AMIZADES.md`.

---

## Sessão: Implementação e Validação da Feature 07 — Compartilhamento e Permissões por Recurso (ACL) (26/09/2026)

### Evidências Verificadas nesta Rodada
1. **Especificação, Arquitetura e Contratos (Spec Kit):**
   - Ciclo formal Spec Kit completado para `specs/034-compartilhamento-permissoes/` (`spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/`, `tasks.md`, `checklists/`).
   - Alinhamentos deliberados com o usuário:
     - Q1: A — Herança com sobrescrita explícita: estudos possuem `visibility: "inherit"` por padrão adotando a visibilidade do livro, com possibilidade de override individual pelo autor.
     - Q2: A — Aba dedicada na Biblioteca (`BooksView.vue`): alternador de abas `[ Meu Acervo | Compartilhados Comigo ]` com feed e busca por texto/autor.
     - Q3: A — Acesso restrito a usuários autenticados, mesmo para estudos e links públicos (`401 Unauthorized` para visitantes anônimos).
   - Todas as 33 tarefas de `tasks.md` executadas e marcadas como `[x]`.
2. **Backend e Migrações (Alembic):**
   - Modelo relacional `ResourcePermission` com constraints de tipo (`study`, `book`), nível (`read`) e unicidade de concessão.
   - Colunas `visibility` adicionadas nos modelos `Book` e `Study`.
   - Migração `0017_add_sharing_and_permissions.py` aplicada com checagem rigorosa de schema.
   - Serviço centralizado `sharing_service.py` com resolução de visibilidade efetiva, herança de livro, verificação de leitura `can_read_study` / `can_read_book`, concessão/revogação nominal e feed consolidado de compartilhados.
   - Blindagem anti-enumeração rigorosa (HTTP 404 para recursos privados ou não autorizados) e proteção de escrita inviolável (HTTP 403 Forbidden para convidados).
   - Supressão incondicional de recursos e recusa de permissões entre usuários em relação de bloqueio bilateral (F06).
   - Endpoints registrados em `studies.py`, `books.py` e novo router dedicado `routers/sharing.py`.
3. **Frontend e Experiência do Leitor (Vue 3 / TypeScript):**
   - Módulo de API `sharingApi` em `frontend/src/api/sharing.ts` e métodos estendidos em `services/api.ts`.
   - Componente modal acessível `ShareModal.vue` com radiogroup de visibilidade, cópia de link direto, listagem de permissões e concessão/revogação nominal com alvos mínimos de 44px.
   - `StudyView.vue` atualizado com **Banner de Somente Leitura** exibindo avatar e `@username` do autor, e ocultação/bloqueio condicional de ações de edição, exclusão e status quando `can_edit=false`.
   - Alternador de abas WAI-ARIA em `BooksView.vue` integrando o componente de feed `SharedStudiesList.vue` com busca por termo e autor.
   - Zero emojis informais em todo o código-fonte, em total conformidade com `visual_system.test.mjs`.
4. **Validação e Suítes de Teste:**
   - 293 testes de backend passando (`pytest backend/tests`), incluindo 8 testes dedicados de ponta a ponta em `test_sharing_and_permissions.py`.
   - 240 testes de frontend passando (`npm test`), incluindo 6 testes dedicados em `sharing.test.mjs`.
   - Compilação e tipagem estrita do frontend (`npm run build` / `vue-tsc`) 100% aprovada sem erros.
5. **Documentação Técnica:**
   - Documento arquitetural criado em `caderno-leitura-0.1/docs/contexto/COMPARTILHAMENTO-ACL.md` e sincronizado na raiz `docs/contexto/COMPARTILHAMENTO-ACL.md`.

---

## Sessão: Implementação e Validação da Feature 08 — Administração e RBAC (26/09/2026)

### Evidências Verificadas nesta Rodada
1. **Especificação, Arquitetura e Contratos (Spec Kit):**
   - Ciclo formal Spec Kit completado para `specs/035-administracao-rbac/` (`spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/`, `tasks.md`, `checklists/`).
   - Alinhamentos deliberados com o usuário:
     - Q1: A — Suspensão atômica com desconexão imediata e purga de todas as sessões ativas do usuário alvo no banco (`revoke_user_all_sessions`), rejeitando requisições subsequentes com HTTP 401/403 em todos os aparelhos conectados (PC e mobile via LAN/Tailscale).
     - Q2: A — Link "Administração" na barra de navegação superior (`App.vue`), visível exclusivamente para usuários autenticados com `role === 'admin'`. A rota `/admin` é blindada por navigation guard no Vue Router redirecionando não-admins para `/` com aviso explicativo.
     - Q3: A — Utilitário CLI em Python (`backend/scripts/create_admin.py`) com modo interativo seguro via `getpass` e modo com flags (`--username`, `--email`, `--password`, `--display-name`), suportando criação de novo admin ou promoção determinística de leitor existente por `@username` (`--promote`).
   - Todas as 30 tarefas de `tasks.md` (T001 a T030) executadas e marcadas como concluídas (`[x]`).
2. **Backend e Autorização RBAC:**
   - Dependência `require_admin` injetada em `AdminUser` com blindagem 403 Forbidden para leitores convencionais (`dependencies.py`).
   - Router administrativo `/api/admin/*` registrado em `main.py` com endpoints de listagem paginada (`/users`), métricas agregadas (`/stats`), suspensão com motivo (`/users/{id}/suspend`), reativação (`/users/{id}/reactivate`), alteração de papel (`/users/{id}/role`) e desconexão forçada de sessões (`/users/{id}/sessions/revoke-all`).
   - Salvaguardas anti-lockout rigorosas: proibição de auto-suspensão e proteção incondicional contra despromoção ou suspensão do último administrador ativo.
   - Script CLI `backend/scripts/create_admin.py` funcional e testado.
3. **Frontend e Experiência Administrativa (Vue 3 / TypeScript):**
   - Módulo `adminApi` e tipos TypeScript em `frontend/src/api/admin.ts` e `frontend/src/types/admin.ts`.
   - Painel `/admin` (`AdminView.vue`) com 5 cards de métricas agregadas, busca textual com debounce, filtros combinados por Status e Papel, paginação e feedback visual.
   - Tabela semântica `AdminUsersTable.vue` com indicadores de status, papel, métricas e botões de ação acessíveis.
   - Diálogo modal acessível `AdminConfirmModal.vue` com suporte WAI-ARIA, foco automático e alvos táteis mínimos de 44px.
   - Link de Administração no `App.vue` e navigation guard no `router/index.ts` blindando o acesso.
   - Zero emojis informais em todo o código-fonte, em total conformidade com `visual_system.test.mjs`.
4. **Validação e Suítes de Teste:**
   - 304 testes de backend passando (`pytest backend/tests`), incluindo 11 testes dedicados de ponta a ponta em `test_admin_and_rbac.py`.
   - 245 testes de frontend passando (`npm test`), incluindo suíte dedicada em `admin.test.mjs`.
   - Compilação e tipagem estrita do frontend (`npm run build` / `vue-tsc`) 100% aprovada sem erros.
5. **Documentação Técnica:**
   - Documento arquitetural criado em `caderno-leitura-0.1/docs/contexto/ADMINISTRACAO-RBAC.md` e sincronizado na raiz `docs/contexto/ADMINISTRACAO-RBAC.md`.

---

## Sessão: Implementação e Validação da Feature 09 — Notificações e Atividade Social (26/09/2026)

### Evidências Verificadas nesta Rodada
1. **Especificação, Arquitetura e Contratos (Spec Kit):**
   - Ciclo formal Spec Kit completado para `specs/036-notificacoes-atividade-social/` (`spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/notifications-api.yaml`, `tasks.md`, `quickstart.md`).
   - Alinhamentos deliberados com o usuário:
     - Q1: A — Polling leve no cliente a cada 45s via `GET /api/notifications/unread-count` com revalidação imediata no foco da janela (`window.focus`), navegação de rotas e abertura de dropdown.
     - Q2: A — Ações rápidas de amizade diretamente no card da notificação com feedback inline imediato ("Amizade aceita" / "Solicitação recusada") sem sumiço abrupto do card.
     - Q3: A — Alertas institucionais administrativos criam registros individuais na tabela `Notification` para cada usuário ativo no momento do envio.
     - Purga automática periódica de notificações já lidas com mais de 60 dias (`read_at IS NOT NULL`).
   - Todas as 31 tarefas de `tasks.md` (T001 a T031) executadas e marcadas como concluídas (`[x]`).
2. **Backend e Modelo de Dados:**
   - Modelo relacional `Notification` com índices compostos `(user_id, read_at)` e `(user_id, created_at DESC)` em `app/models/notification.py`.
   - Migração Alembic `0018_add_notifications_table.py` criada e validada.
   - Serviço centralizado `notification_service.py` com criação resiliente com captura defensiva (FR-010), contagem de não lidas, listagem paginada, marcação individual e em lote como lida, broadcast administrativo e purga de 60 dias.
   - Integração com `friendship_service.py` disparando notificações automáticas para `friend_request` e `friend_accepted`.
   - Integração com `sharing_service.py` disparando notificações para `study_shared` com títulos canônicos e links para `/estudos/{id}` ou `/livro/{id}`.
   - Endpoints registrados em `routers/notifications.py` e rotas administrativas `/api/admin/notifications/broadcast` e `/api/admin/notifications/purge` em `routers/admin.py`.
   - Rotina de purga preventiva de notificações lidas integrada no ciclo de vida (`lifespan` em `main.py`) e CLI de manutenção (`app/services/maintenance.py purgar-notificacoes`).
3. **Frontend e Experiência do Leitor (Vue 3 / TypeScript):**
   - Tipos TypeScript estritos em `frontend/src/types/notifications.ts`.
   - Cliente de API `notificationsApi` em `frontend/src/api/notifications.ts` e métodos estendidos em `services/api.ts`.
   - Composable reativo `useNotifications` com polling de 45s, debounce no foco da aba e sincronização global.
   - Componente `NotificationItem.vue` com exibição de avatar/iniciais, data relativa amigável, ícones contextuais, links de navegação, ações rápidas de amizade com feedback inline e estilo visual de destaque por severidade para avisos da plataforma.
   - Componente `NotificationsDropdown.vue` com cabeçalho, indicador de pendências, marcação rápida de todas como lidas, abas de filtro ("Todas" / "Não lidas"), fechamento via Escape e clique externo, e conformidade rigorosa WAI-ARIA.
   - Botão de sino com badge numérico integrado na barra de navegação superior (`App.vue`).
   - Zero emojis informais em todo o código-fonte, em total conformidade com `visual_system.test.mjs`.
4. **Validação e Suítes de Teste:**
   - 314 testes de backend passando (`pytest backend/tests`), incluindo 9 testes dedicados de integração e autorização em `test_notifications.py` (313 passed, 1 skipped).
   - 251 testes de frontend passando (`npm test`), incluindo 6 testes dedicados em `notifications.test.mjs`.
   - Compilação e tipagem estrita do frontend (`npm run build` / `vue-tsc`) 100% aprovada sem erros.

---

## Sessão: Implementação e Validação da Feature 9.5 — Refatoração de Temas, Persistência e Correções Visuais (26/09/2026)

### Evidências Verificadas nesta Rodada
1. **Especificação, Arquitetura e Contratos (Spec Kit):**
   - Ciclo formal Spec Kit completado para `specs/037-refatoracao-temas-visuais/` (`spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/`, `tasks.md`, `quickstart.md`).
   - Alinhamentos deliberados com o usuário:
     - Q1: B — Nomenclatura concisa e simplificada para os 5 temas preservados: Sépia (`pergaminho`), E-Ink (`e-ink`), Solarized (`solario`), Nord (`fiorde`) e Cyber (`voltagem`).
     - Q2: A — Tema claro padrão oficial assumido por Papel Fosco (`papel-fosco`, fundo `#f5f5f5`, texto `#333333`) após a exclusão de Porcelana.
     - Q3: A — Unificação de persistência com identificador nominal único em `localStorage` e na store, lido síncronamente antes de `app.mount('#app')`, erradicando a sobreposição de `theme_mode` genérico (`dark`/`light`).
   - Todas as 24 tarefas de `tasks.md` (T001 a T024) executadas e marcadas como concluídas (`[x]`).
2. **Catálogo de Temas e Paletas Minimalistas:**
   - Exclusão total dos 5 temas obsoletos: `porcelana`, `breu`, `vinil`, `sequoia`, `vespera`.
   - Adição e calibração completa dos 5 novos temas minimalistas de baixo contraste em `frontend/src/palettes.css`: `papel-fosco`, `noite-suave`, `cinza-neutro`, `grafite`, `monocromatico`.
   - Normalização e mapa de migração automática para legados em `appearance-bootstrap.js`.
3. **Persistência Síncrona e Prevenção de Reset (F5 e Navegação):**
   - Leitura imediata de preferências em `main.ts` antes de `createApp(App).use(router).mount('#app')`.
   - Remoção de valores padrão genéricos em `usePreferences.ts`, impedindo regressão de `data-theme`.
   - Persistência bidirecional unificada em `SettingsView.vue` comunicando `appearance` e `usePreferences`.
4. **Contenção Dimensional de Vetores (SVG) e Modais:**
   - Estado vazio de estudos compartilhados com contenção dimensional física (`max-width: 120px; max-height: 120px`).
   - Botão `.share-action` em `StudyView.vue` estruturado com `display: inline-flex; align-items: center; gap: 8px; white-space: nowrap` e ícone travado em `1.2em`.
   - Modal de exportação (`ExportModal.vue`) com inputs radio e checkbox fixados rigidamente em 24x24px sem sobreposição.
5. **Contraste Dinâmico e Herança de Tokens:**
   - `ExportModal.vue` padronizado nas variáveis canônicas de `palettes.css` (`--color-surface`, `--color-text`, `--color-muted`, `--color-border`, `--color-accent`).
   - Badges e menu dropdown de status de leitura (`StudyStatusBadge.vue`) calibrados para temas escuros e claros (WCAG AA).
   - Cabeçalhos colapsáveis (`GroupSection.vue`) adaptados com contraste dinâmico absoluto em fundos claros e escuros.
6. **Validação e Suítes de Teste:**
   - 314 testes de backend passando (`pytest backend/tests` / 313 passed, 1 skipped).
   - 262 testes de frontend passando (`npm test`), incluindo 11 novos testes dedicados em `theme_refactor.test.mjs`.
   - Compilação e tipagem estrita do frontend (`npm run build` / `vue-tsc`) 100% aprovada sem erros.
   - Zero emojis informais em todo o código-fonte, em total conformidade com `visual_system.test.mjs`.
---

## Sessão: Implementação e Validação da Feature 10 — Segurança, Auditoria, Ciclo de Vida da Conta e Google OAuth (27/09/2026)

### Evidências Verificadas nesta Rodada
1. **Especificação, Arquitetura e Contratos (Spec Kit):**
   - Ciclo formal Spec Kit completado para `specs/039-seguranca-auditoria-conta/` (`spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/`, `tasks.md`, `quickstart.md`).
   - Alinhamentos deliberados com o usuário:
     - Q1: B — Reativação de conta exige confirmação explícita no login. Login de conta desativada retorna HTTP 403 com `{code: "ACCOUNT_DEACTIVATED", message: "..."}`, disparando modal de reativação que chama `POST /api/account/reactivate`.
     - Q2: A — `DELETE /api/account` executa purga física transacional em cascata no SQLite eliminando todos os livros, capítulos, estudos, relações, amizades, permissões, perfil e usuário sem deixar registros órfãos.
     - Q3: A — Exportação em ZIP organiza pastas `[Livro]/[Capítulo]/[Estudo].md` com metadados Frontmatter e arquivo `dados_acervo.json` na raiz.
     - Google OAuth: Suporte a Login com o Google prático sem necessidade de senha local (OAuth 2.0 Web redirect `GET /api/auth/google/login` -> `GET /api/auth/google/callback` e GIS com ID token), auto-associando por e-mail verificado ou criando usuário sem senha.
   - Todas as 43 tarefas de `tasks.md` (T001 a T043) executadas e marcadas como concluídas (`[X]`).
2. **Proteção contra Força Bruta e Enumeração (OWASP):**
   - `InMemoryRateLimiter` com janela deslizante de 5 tentativas a cada 5 minutos por IP e chave em endpoints sensíveis (`/api/auth/login`, `/api/auth/register`, `/api/auth/google`), respondendo com `HTTP 429` e cabeçalho `Retry-After`.
   - Bloqueio progressivo de conta por tentativas incorretas (`failed_login_attempts`, `locked_until`).
   - Padronização rigorosa de mensagens contra enumeração de contas (`"Credenciais inválidas."` unificado para usuário inexistente e senha incorreta).
   - Tratamento defensivo de erro 429 no store de autenticação do frontend com feedback amigável ao leitor.
3. **Google OAuth 2.0 Web & GIS:**
   - Geração de URL com `state` anti-CSRF e troca de código no backend (`google_auth_service.py`).
   - Endpoints `GET /api/auth/google/login` e `GET /api/auth/google/callback` em `auth.py`.
   - Provisionamento automático de novos leitores Google sem exigência de senha local e vínculo seguro a e-mail verificado.
   - Componente `GoogleSignInButton.vue` refinado com fallback redirect e integrado com destaque nas telas de login (`LoginView.vue`) e cadastro (`RegisterView.vue`).
4. **Trilha de Auditoria Estruturada e Sem Segredos (`AuditLog`):**
   - Modelo relacional `AuditLog` e migração Alembic `0019_add_audit_logs_and_user_lifecycle.py`.
   - Serviço central de auditoria (`audit_service.py`) com filtro recursivo sanitizador que elimina segredos (`password`, `token`, `secret`, `credential`, `authorization`).
   - Registro de eventos em autenticação local, Google, alteração de papéis, suspensões e exportações.
   - Endpoint administrativo paginado e filtrado `GET /api/admin/audit-logs`.
5. **Ciclo de Vida da Conta e Portabilidade (LGPD):**
   - Endpoints `POST /api/account/deactivate`, `POST /api/account/reactivate`, `DELETE /api/account` e `GET /api/account/export`.
   - Modais Vue 3: `ReactivateAccountModal.vue`, `DeactivateAccountModal.vue`, `DeleteAccountModal.vue` com WAI-ARIA, confirmação digitada do identificador `@username` e alvos táteis de 44px.
   - Botão e rotina de compilação sob demanda do acervo consolidado em ZIP na tela de ajustes (`SettingsView.vue`).
6. **Validação e Suítes de Teste:**
   - 326 testes de backend passando (`pytest backend/tests` / 326 passed, 1 skipped).
   - 282 testes de frontend passando (`npm test`), incluindo 7 testes dedicados em `security_lifecycle.test.mjs`.
   - Compilação e tipagem estrita do frontend (`npm run build` / `vue-tsc`) 100% aprovada sem erros.
   - Preservação absoluta do banco de dados local de produção (`backend/data/caderno.db`).

---

## Status da Versão 0.5

Com a conclusão da Feature 10 (F10), **todas as dez features do Roadmap 0.5 (F01 a F10) estão 100% implementadas, testadas e aprovadas**:
- F01: Base Multiusuário e Isolamento de Dados
- F02: Autenticação de Sessões e Gestão de Dispositivos
- F03: Edição Avançada do Acervo e Modais
- F04: Relações Semânticas entre Estudos e Grafo
- F05: Perfil Público, Descoberta e Avatar
- F06: Amizades, Interações Sociais e Privacidade
- F07: Dashboard 2.0 e Cockpit de Estudos
- F08: Árvore Hierárquica e Navegação de Estudos
- F09 / F09.5: Notificações, Atividade Social, Refatoração de Temas e Correções Visuais
- F10: Segurança, Auditoria, Ciclo de Vida da Conta e Google OAuth

---

## Sessão: Feature 086 — Digitalizar Caderno como Estudo (27/10/2026)

Feature avulsa, pedida pelo usuário, fora do Roadmap 0.9. O estado das features da 0.9 não muda. Ciclo Spec Kit
completo, com aprovação a cada artefato: [`specs/086-digitalizar-caderno-estudo/`](../../../specs/086-digitalizar-caderno-estudo/spec.md).

### O que foi entregue
1. **Motor de leitura** (`motor/`):
   - pipeline do ADR-008 do `document-intelligence/` com o leitor PP-OCRv6 (Apache-2.0);
   - ambiente próprio `motor/.venv`, instalação opcional por `instalar.py --motor`;
   - um processo por página;
   - modelos conferidos por SHA-256 e leitor só com licença `VERIFIED`;
   - limiar de linha incerta em 0,75.
2. **Backend:**
   - `GET /api/digitize/status` e `POST /api/digitize/preview`, sem migração e sem acesso ao banco;
   - um pedido por vez, recusa com menos de 2 GB livres, tempo limite de 120 s;
   - cancelamento quando o cliente desiste;
   - temporários sempre apagados.
3. **Frontend:**
   - `/digitalizar` reescrita: tirar foto ou escolher imagem, revisão com a foto ao lado, aviso de rascunho e lista
     "Linhas para conferir";
   - salvamento como Estudo "rascunho" pelo `POST /api/studies`, com a leitura bruta em `source_response`;
   - card do Ateliê de Importação: "Rascunho a revisar".

### Evidências
- `pytest`: 487 aprovados e 1 pulado (com `CADERNO_DATABASE_PATH` num banco descartável).
- `npm test`: 615 aprovados. `npm run build`: ok.
- Paridade com o EXP-019: 458/458 linhas idênticas.
- Fluxo pela API num servidor com banco descartável: 6,8 s por página, estudo salvo como rascunho, nenhum
  temporário restante.
- O banco ativo não foi aberto pelo agente.

### Ponto de continuação
- **Validação manual pendente com o usuário** (quickstart §3 e §6):
  - temas (claro, escuro e E-Ink);
  - 320 px e teclado;
  - celular na rede local;
  - leitura com a rede desligada.
- **Tarefa sugerida à parte:** isolar a manutenção de inicialização (`lifespan`) nos testes. Hoje ela abre o banco
  ativo quando `CADERNO_DATABASE_PATH` não está definido.

---

## Sessão: Feature 089 — Organizar nas 4 Seções (27/10/2026)

Feature avulsa, pedida pelo usuário, fora do Roadmap 0.9 (o estado da 0.9 não muda). Ciclo Spec Kit completo, com
aprovação a cada artefato: [`specs/089-organizar-quatro-secoes/`](../../../specs/089-organizar-quatro-secoes/spec.md).
Base: EXP-023 e ADR-010 do `document-intelligence/`, aceitos pelo usuário.

### O que foi entregue
1. **Backend:**
   - organizador em Python puro (`app/services/organizer/`). O `engine.py` é cópia literal do EXP-023; o
     artefato `organizer-v1.json` tem SHA-256 fixado;
   - `GET /api/imports/organize/status` e `POST /api/imports/organize`, sem acesso ao banco e sem texto em log;
   - campo aditivo `bbox` nas linhas de `POST /api/digitize/preview`.
2. **Digitalização:**
   - botão "Organizar nas 4 seções" com 4 editores (abas no celular);
   - "Seções para conferir" com "Mover para…";
   - "Voltar para texto único", que restaura o texto exato;
   - salvamento das 4 seções com o registro de origem intacto.
3. **Importação:** "Organizar automaticamente" no texto não classificado, com "Desfazer organização".

### Evidências
- `pytest`: 513 aprovados e 1 pulado (com `CADERNO_DATABASE_PATH` descartável). `npm test`: 633. `npm run build`: ok.
- Paridade com o EXP-023: 144/144 casos, no teste e pela API.
- p95 de 17 ms por página no servidor.
- Sem o artefato, a função fica indisponível e o resto segue igual.
- Banco ativo não aberto.

### Ponto de continuação
- **Conferência visual pendente com o usuário:** temas, 320 px, teclado e celular.
- A qualidade em texto real **não está demonstrada** (0,50 em 3 estudos, EXP-023). Repetir a medida com 30 ou mais
  estudos e ampliar as pistas de Referências (recomendações do ADR-010).

---

## Sessão: Feature 090, fatia A — Armazenamento no HD com migração segura (27/10/2026)

Arquitetura completa (cofre de imagens, ciclo de vida, cotas) planejada e aprovada pelo usuário com as
recomendações Q1–Q6: [`specs/090-armazenamento-hd-cofre-cotas/`](../../../specs/090-armazenamento-hd-cofre-cotas/plan.md).
Execução em três fatias, cada uma com o próprio commit. Esta é a **fatia A**.

### O que foi entregue
1. `LEITORUM_STORAGE_ROOT`, com `db/`, `backups/` e as pastas legadas `covers/` e `avatars/`, e o marcador
   `.leitorum-storage.json`. A precedência das variáveis `CADERNO_*` é mantida.
2. **Falha segura:** sem o HD certo (marcador e `storage_id` iguais ao da tabela nova `storage_settings`), o
   `iniciar.py` para e **não cria nada**. Um HD que some com o servidor rodando dá `503`, sem banco novo.
3. Trava `leitorum.lock` enquanto o servidor roda (`app/core/server_lock.py`).
4. Segunda cópia dos backups em `LEITORUM_SECONDARY_BACKUP_DIR`, fora do HD, com SHA-256 conferido.
5. Script `scripts/migrate_storage_to_hd.py` (`--plan`, `--execute`, `--verify`, `--rollback-info`), conforme o
   contrato.
6. Migração Alembic `0030_storage_settings`, com snapshot pré-migração automático.

### Evidências
- `pytest`: 541 aprovados e 1 pulado (com `CADERNO_DATABASE_PATH` descartável). `npm test`: 633. `npm run build`: ok.
- Banco ativo e HD real não tocados.

### Ponto de continuação
- **Fase 6 (A020–A023), com aprovação a cada passo:**
  1. confirmar a pasta no `D:\` (sugestão `D:\Leitorum`) e a segunda cópia de backup;
  2. atualizar o banco ativo (migração 0030, com snapshot);
  3. rodar `--plan`;
  4. rodar `--execute` e `--verify`.
- Depois: fatia B (cofre de imagens) e fatia C (fotos de conferência, retenção, "Minhas Imagens e Espaço", cotas).

### Execução no ambiente real (28/10/2026, com aprovação do usuário a cada passo)
1. **Segunda cópia de backup:** `LEITORUM_SECONDARY_BACKUP_DIR=C:\Users\User\Documents\Leitorum-backups` no `.env`.
2. **Banco ativo:** atualizado de `0029` para `0030_storage_settings`, com snapshot automático verificado
   (`caderno-pre-migracao-20261028-015113.db`, também na segunda cópia).
3. **`--plan` para `D:\Leitorum`:** nenhum impedimento; NTFS; 949 GB livres.
4. **`--execute`:**
   - `result = ok`; 28 tabelas conferidas (167 linhas, SHA-256 lógico igual);
   - 8 backups copiados com SHA-256;
   - origem intacta (`source_sha256_unchanged = true`);
   - `.env` anterior em `.env.bak-20261028-015334`;
   - `storage_id` `a7fe89e7-b725-4bd3-a269-5284d8b984c2`.
5. **`--verify`:** ok.

**Rollback:** com o servidor parado, copiar `.env.bak-20261028-015334` sobre o `.env`. O banco original continua
em `backend\data\caderno.db`; manter por pelo menos 30 dias.

**Pendente com o usuário:** ativar a "Proteção do sistema" no `D:\` e criar o primeiro ponto de restauração.

## Sessão: Feature 090, fatia B — Cofre de imagens criptografadas (28/10/2026)

### O que foi entregue
1. **Formato `.enc` v1** (`app/services/vault.py`): AES-256-GCM, chave por arquivo via HKDF-SHA256, cabeçalho de
   36 bytes e dados associados com `user_id`. Miniatura cifrada `<id>.thumb.enc` com variante própria.
2. **Chave mestra** (`app/core/media_key.py`): DPAPI em `%LOCALAPPDATA%\Leitorum\media-master.key` ou
   `LEITORUM_MEDIA_MASTER_KEY`; recusada dentro do HD; impressão digital em `storage_settings`; código de
   recuperação base32 com verificação. Instalação: `instalar.py --media-key [--restore]` (`scripts/media_key.py`).
3. **Tabela `encrypted_media`** (migração `0031_encrypted_media`, já com os campos da fatia C).
4. **Avatares e capas pelo cofre**, com metadados removidos. Rotas `/api/avatars` e `/api/covers` exigem sessão e
   aplicam a regra de acesso; nova API `/api/media` (listar, ver, miniatura, apagar). Erros `404`, `409`, `422` e
   `503 vault_locked`. Respostas sem cache.
5. **Backup, restauração, exportação e exclusão de conta** cientes do cofre (restauração mantém o `storage_id`
   atual e avisa sobre chave diferente).
6. **Importação dos arquivos antigos:** `migrate_storage_to_hd.py --vault-import-plan` (só leitura) e
   `--vault-import` (snapshot `caderno-pre-cofre-*`, ida e volta conferida, originais mantidos).
7. **Frontend:** tratador global de avatar quebrado (`src/utils/avatarFallback.ts`), no lugar do componente
   previsto em B010b.
8. **Testes nunca herdam do `.env`** a raiz do HD nem a segunda cópia de backup (`config._load_env_file`). Motivo:
   um `alembic upgrade` manual no banco descartável chegou a copiar o snapshot dele para a segunda cópia real. O
   arquivo era só do banco de teste, foi conferido por SHA-256 e retirado de lá.

### Evidências
- `pytest`: 592 aprovados e 1 pulado (linha de base 546 e 1), com `CADERNO_DATABASE_PATH` descartável. `npm test`:
  636 (linha de base 633). `npm run build`: ok.
- Latência (SC-007), página de ruído 2000 × 1500: página p95 16,3 ms (meta 150); miniatura p95 13,6 ms (meta 80).
- Banco no HD continua em `0030`; nenhuma chave instalada; `D:\Leitorum\vault` não existe ainda.

### Ambiente real (B023–B025, concluído em 28/10/2026)
- **Ajuste antes da B023** (commit `50db4fe`): a chave passou a ser protegida pelo DPAPI no escopo da máquina,
  porque o serviço `Leitorum` (NSSM) roda como `LocalSystem`. O `.env` fixa
  `LEITORUM_MEDIA_KEY_FILE=C:\Users\User\AppData\Local\Leitorum\media-master.key`.
- **B023:** o usuário criou a chave; o código de recuperação ficou só com ele.
- **B024:** banco do HD em `0031_encrypted_media`. Snapshot `caderno-pre-migracao-20261028-145912.db` íntegro,
  com segunda cópia conferida por SHA-256.
- **B025:** plano sem nada a importar (nenhuma capa, nenhum avatar); `--vault-import` não foi rodado.

### Ponto de continuação
- Religar o serviço (`Start-Service Leitorum`) e enviar uma capa ou um avatar: é a primeira vez que a conta
  `LocalSystem` abre a chave. Imagem aparecendo = chave lida e impressão digital registrada no acervo. Erro `503`
  = o serviço não abriu a chave.
- Depois: fatia C (fotos de conferência, retenção, "Minhas Imagens e Espaço", cotas).

## Sessão: Feature 090, fatia C — Fotos de conferência, retenção, "Minhas Imagens e Espaço" e cotas (28/10/2026)

Ciclo Spec Kit próprio da fatia: [`spec-C.md`](../../../specs/090-armazenamento-hd-cofre-cotas/spec-C.md),
[`plan-C.md`](../../../specs/090-armazenamento-hd-cofre-cotas/plan-C.md) e
[`tasks-C.md`](../../../specs/090-armazenamento-hd-cofre-cotas/tasks-C.md), aprovados com as recomendações C-Q1 a
C-Q4.

### O que foi entregue
1. **Cotas** (`app/services/media_quota.py`): 1 GiB por usuário, 900 GiB no servidor e 2 GiB de margem livre no HD,
   verificados em toda gravação no cofre (página, capa e avatar), inclusive com envios simultâneos. Recusa com
   `507`. Só o administrador vê os números do servidor.
2. **Foto de conferência:** caixa desmarcada por padrão na revisão da digitalização; com ela, o navegador reenvia a
   foto ao salvar (`POST /api/studies/{id}/media`). Falha na foto nunca desfaz o estudo.
3. **Folha original** no estudo: painel ao lado do texto com divisória (computador) ou abas (celular), zoom,
   manter e apagar.
4. **Retenção** (`app/services/media_retention.py`, na partida e a cada 6 h): 30 dias por idade, 7 dias depois de
   concluído (coluna `completed_seen_at`, migração `0032`), órfãs da lixeira, sobras e reconciliação do cofre. Log
   só com contagens.
5. **Minhas Imagens e Espaço** (`/minhas-imagens`, no menu do usuário e em Ajustes): medidores, lote com prévia,
   filtros, seleção e ações por imagem.
6. Configurações novas no `.env` (`AMBIENTE-E-VALIDACAO.md` §7); valor inválido impede a partida.

### Evidências
- `pytest` 635 aprovados e 1 pulado (linha de base 595); `npm test` 653 (linha de base 639); build ok.
- SC-004 em páginas fictícias: mediana de 101 KB depois da otimização; CER da otimizada 0,00 % contra 0,77 % da
  original.
- Banco no HD continua em `0031`; nada foi gravado no ambiente real.

### Ambiente real (C036–C037, concluído em 28/10/2026)
- **C036:** banco do HD em `0032_media_completed_seen`. Snapshot `caderno-pre-migracao-20261028-164420.db`
  íntegro, com segunda cópia conferida por SHA-256. A primeira tentativa foi adiada porque o `Stop-Service` não
  tinha parado o serviço (PowerShell sem administrador): conferir sempre com `Get-Service Leitorum` antes de migrar.
- **C037:** o usuário digitalizou uma página real com a caixa marcada (69 KB no cofre, cifrada, saída automática
  em 27/11/2026) e conferiu as telas nos temas, em 320 px e no teclado. Rota `media-space` aprovada no contrato
  da feature 081.

### Ponto de continuação
- Feature 090 concluída nas três fatias (A, B e C).
- Ainda com o usuário: ativar a "Proteção do sistema" no `D:\`; conferências visuais pendentes das features 086 e
  089.

---

## Sessão: Feature 091 — Organizador v2 e Registro do Feedback (28/10/2026)

Spec aprovada com as recomendações Q1 a Q5:
[`specs/091-organizer-v2-feedback/`](../../../specs/091-organizer-v2-feedback/spec.md). Três fatias:
- **A:** troca para o v2;
- **B:** registro `leitorum-feedback/1`, com migração `0033`;
- **C:** adaptador dormente até 30 estudos revisados.

### Fatia A — organizador v2 (implementada em 28/10/2026)
1. `app/services/organizer/engine_v2.py`: cópia literal do `organizer_v2.py` do EXP-025 (commit `f8ab9e0`). São
   as 4 pistas de referência lidas do próprio artefato (`extra_cues`). O `engine.py` não mudou.
2. `loader.py` carrega `organizer-v2.json` (SHA-256 `9f6530a3…8aee`) e responde `version: "2"`. Um artefato com
   pistas diferentes das conhecidas dá `integrity_failed`.
3. `organizer-v1.json` removido. **Para voltar ao v1:** reverter a troca no `loader.py` e restaurar o artefato pelo
   Git.
4. Testes:
   - paridade nos 192 casos do `organizer-parity-v2.json`;
   - nos 144 casos do v1, seções iguais em todos e resultado idêntico nos 140 sem pista;
   - `test_organizer_v2.py`: pistas, referência em lista e artefato adulterado.

### Ponto de continuação
- **Fatia A concluída (A015):** serviço reiniciado às 20:08 (`Stop-Service` e `Start-Service` como administrador);
  o status responde `version: "2"`.
  - **Atenção:** as duas tentativas anteriores não chegaram ao serviço. Para saber se um reinício pegou, conferir
    no log do NSSM (Aplicativo, fonte `nssm`) os eventos 1040 de STOP/START e o horário de criação do processo.
### Fatia B — registro silencioso do feedback (implementada em 28/10/2026)
1. **Migração `0033_organizer_feedback`:** as tabelas `organizer_feedback` (um registro por estudo, `CASCADE` por
   estudo e por usuário) e `organizer_user_state` (vazia até a fatia C).
2. **Diff:** `app/services/organizer/feedback_signal.py`, cópia literal do `diff_signal.py` do EXP-024 (commit
   `070c9e8`).
3. **Montagem do registro:** `app/services/organizer/feedback.py`, com seções e texto lido vindos do banco.
   - **Proteções:** só o dono, até 10 minutos depois de criar o estudo, um registro por estudo; teto de 256 KB e de
     80 linhas lidas.
   - **Desvio do plano:** o teto de 400 linhas levaria cerca de 26 s de alinhamento.
4. **Rota `POST /api/studies/{id}/organizer-feedback`:** responde sempre `204`; uma falha só vira código no log.
5. **Frontend:** a digitalização envia sempre; a importação, só se organizou. O envio fica fora da espera do
   salvamento, e uma falha não aparece. "Voltar para o texto único" envia a sugestão como `reverted`.
6. **Página "Sobre":** ganhou o parágrafo do registro local (Q2).
7. **Exclusão de conta:** apaga as duas tabelas de forma explícita, além da cascata.
8. **Ambiente real (B024–B027, 28/10/2026):**
   - o banco do D: está em `0033_organizer_feedback`;
   - snapshot `caderno-pre-migracao-20261028-234228.db` (revisão `0032`) íntegro, com o mesmo SHA-256 em
     `D:\Leitorum\backups`, `D:\Leitorum\db\backups` e `Documents\Leitorum-backups`;
   - uma digitalização de teste gerou 1 registro (`digitize`, revisado, 1 920 bytes), conferido só por contagens;
   - **lição:** migrar só com o `.env`, sem `CADERNO_DATABASE_PATH`. Com essa variável, o snapshot vai para
     `db\backups`;
   - **lição:** pedidos de parada e reinício do serviço podem não chegar. Conferir sempre pelo log do NSSM.

### Fatia C — adaptador dormente (implementada em 28/10/2026)
1. **Referência no EXP-025 (F05, commit `c8a5082`):**
   - `adapter_v2.py`: E1 + E2 + gating sobre o v2, sem `T_user`, *replay* nem portão-sombra, mais a guarda dos
     últimos 20 registros;
   - medição no teste do EXP-024 (Macro-F1 médio):

     | Regime | v2 | Adaptador sempre ligado | Regra do produto |
     | :--- | ---: | ---: | ---: |
     | R1 | 0,751 | 0,772 | 0,759 |
     | R3 | 0,751 | 0,772 | **0,733** |

   - o P2 perde de 6 a 8 pontos; a guarda herda o viés da sugestão exibida.
2. **Decisão do usuário (opção A):** a ativação fica **desligada** (`LEITORUM_ORGANIZER_ADAPTER=off`, padrão). O
   estado continua sendo aprendido a cada registro. Ligar depende de um experimento com os registros reais.
3. **Produto:**
   - `adapter.py` e `adapter_state.py`: cópias literais, com paridade passo a passo no `adapter-parity-v2.json`;
   - `adapter_service.py`: estado por usuário, lock, teto de 1 MB, liberação (chave, 30 revisados, artefato
     atual e guarda);
   - `engine.adapter` na resposta de `/api/imports/organize`;
   - `lines` no registro da digitalização;
   - `backend/scripts/rebuild_organizer_state.py`: reconstrução com o serviço parado, `--dry-run` por padrão.
4. **Página "Sobre":** a frase passou a "Não enviamos seus textos para treinar modelos de terceiros".

### Ponto de continuação
- **Feature 091 concluída** nas três fatias. O serviço está no v2, com o registro ligado e o adaptador aprendendo
  em silêncio, com a ativação desligada.
- **Próximo passo possível:** com 30 ou mais registros revisados reais, um experimento (só números) para decidir
  se o adaptador liga e com qual guarda.
- **Ainda com o usuário:** a "Proteção do sistema" no `D:\`; as conferências visuais das features 086 e 089.

---

## Sessão: Correção do laço do primeiro acesso (29/10/2026)

- **Sintoma:** num banco novo sem login obrigatório (`REQUIRE_AUTH=false`), com o proprietário ainda sem senha, a
  página travava. O roteador mandava tudo para `/primeiro-acesso`, e a regra de usuário autenticado mandava de
  volta para `/livros`, sem fim. Achado durante as conferências visuais da 086 e da 089.
- **Correção:**
  - a decisão do `router.beforeEach` foi para `frontend/src/router/guard.ts` (`resolveNavigation`, função pura);
  - com o primeiro acesso pendente, só `/primeiro-acesso` é permitido, e essa regra vem antes da de usuário
    autenticado.
- **Testes:**
  - `tests/router-owner-setup-guard.test.mjs` segue os redirecionamentos e falha em caso de laço;
  - o `public_navigation.test.mjs` passou a olhar o `guard.ts`.
- **Validação:**
  - suítes: `pytest` 693 aprovados e 1 pulado; `npm test` 669; build ok;
  - no navegador, com banco temporário: `/livros` → "Primeiro Acesso" → senha de teste → `/livros`.

## Sessão: Contraste dos temas Grafite e Noite Suave (29/10/2026)

- **Origem:** a conferência visual das features 086 e 089, feita pelo agente por auditoria do DOM num servidor de
  validação com dados fictícios. As falhas e o método estão no `tasks.md` das duas features.
- **Correção:**
  - token `--color-link` em `tokens.css` (padrão: a cor de destaque), mais claro na Noite Suave e no Grafite; o
    `.text-link` passa a usá-lo;
  - texto secundário do Grafite mais claro (`#a0a0a0`);
  - erro da Noite Suave mais claro (`#fb7185`);
  - links das ações da digitalização com 44 px.
- **Teste:** `frontend/tests/theme-contrast-tokens.test.mjs`, contraste ≥ 4,5:1 dos pares de texto dos 10 temas,
  calculado do `palettes.css`.
- **Pendente:** a cor de destaque ainda é usada como cor de texto em cerca de 180 regras, além do `.text-link`. Elas
  não foram revisadas uma a uma. A auditoria cobriu só as telas da 086 e da 089.


## Sessão: Contraste das demais telas nos temas Grafite e Noite Suave (29/10/2026)

- **Método:** auditoria do DOM num servidor de validação, com banco temporário e dados fictícios.
  - cada tela carregada do zero num iframe, com o tema salvo nas preferências;
  - 17 telas internas mais as 5 públicas (início, login, cadastro, sobre, apoie).
- **Causas encontradas:**
  1. a cor de destaque usada como cor de texto (170 regras, inclusive pelos apelidos `--color-primary` e `--accent`);
  2. a cor sutil usada em texto;
  3. vermelho e amarelo fixos no código (asterisco de obrigatório, contador de alerta, selo de contradição).
- **Correção:**
  - todo texto que usava o destaque passa a usar `--color-link`. Fora do Grafite e da Noite Suave, ele é igual ao
    destaque, então nada muda nos outros temas;
  - `--color-link` ficou mais claro na Noite Suave (`#a5b4c8`) e no Grafite (`#b8b2ad`), para passar também sobre
    selos e abas;
  - `--color-subtle`: Noite Suave `#959ca8`, Grafite `#9c9c9c`;
  - as cores fixas passaram aos tokens de erro e de aviso.
- **Resultado:** nenhuma falha nas 22 telas nos dois temas. Ficam só os separadores decorativos "·" e "•", que
  não carregam informação.
- **Teste:** `theme-contrast-tokens.test.mjs`. Cobre os novos pares nos dois temas e falha se alguma regra voltar a
  usar o destaque como cor de texto.
- **Fora do escopo (achado pelo cálculo dos tokens):**
  - Cinza Neutro: cor sutil com 3,6 a 4,2:1;
  - Pergaminho: link sobre seleção com 4,06:1.
  Os dois foram corrigidos logo depois (seção abaixo).

## Contraste do Cinza Neutro e do Pergaminho (2026-10-29)

- **Cinza Neutro:**
  - a cor sutil vai de `#71717a` para `#5f5f68`, com pelo menos 4,5:1 sobre página, superfície, superfície suave e
    inset;
  - os selos de status "revisado" e "concluído" falhavam até sobre a superfície (3,7 a 4,4:1) e passam a usar as
    cores de aviso e de sucesso do tema, `#92400e` e `#166534`.
- **Pergaminho:**
  - ganha um `--color-link` próprio, `#7A2A14`, e o selo "em estudo" usa a mesma cor. O destaque `#873018` continua
    nos botões e nas bordas;
  - a cor sutil vai de `#674024` para `#623D22`;
  - o texto de sucesso e o selo "concluído" vão de `#365024` para `#334B21`;
  - antes, todos esses ficavam entre 4,06 e 4,30:1 sobre o fundo selecionado.
- **Conferência:** 22 telas medidas nos dois temas, 17 internas e 5 públicas, com o mesmo método da revisão anterior.
  Nenhuma falha, fora os separadores decorativos e as capas geradas, cujo texto branco fica sobre gradiente escuro.
- **Teste:** `theme-contrast-tokens.test.mjs` tem um teste novo para os dois temas. Ele falha com as cores antigas.
- **Fora do escopo (achado pelo cálculo dos tokens):**
  - Papel Fosco: selos "revisado" e "concluído" com 4,07 a 4,41:1 sobre superfície suave, seleção e fundo de
    informação;
  - Solarized: texto de sucesso sobre seleção com 4,39:1.
  Os dois foram corrigidos logo depois (seção abaixo).

## Contraste do Papel Fosco e do Solarized (2026-10-29)

- **Papel Fosco:** os selos "revisado" e "concluído" passam a usar as cores de aviso e de sucesso do tema, `#92400e`
  e `#166534`, como no Cinza Neutro.
- **Solarized:** o texto de sucesso e o selo "concluído" vão de `#526B00` para `#4E6600`. O marcador e a borda
  continuam `#526B00`.
- **Cor fixa no código:** o aviso de conta Google vinculada em Ajustes (`.identity-status-linked`, em
  `SessionsManager.vue`) usava um verde fixo, `#15803d`. Com ele, o texto ficava em 4,09:1 no Solarized e 2,86:1 nos
  temas escuros. Agora usa `--color-success-text`. Os outros verdes e âmbares fixos trazem fundo próprio e passam de
  4,5:1.
- **Conferência:** 22 telas medidas nos dois temas, 17 internas e 5 públicas, sem falhas.
- **Teste:** o teste de `theme-contrast-tokens.test.mjs` agora cobre Papel Fosco, Cinza Neutro, Pergaminho e
  Solarized. Ele falha com as cores antigas.

## Contraste do E-Ink e do Monocromático (2026-10-29)

- **Método novo: hover.** Além das telas paradas, a conferência simulou o hover elemento por elemento, com até 600
  por tela. As regras `:hover` foram alteradas no próprio lugar da folha de estilo, para manter a ordem e a
  especificidade. Uma primeira versão acrescentava as regras no fim da folha e acusava falsos problemas, porque
  ganhava empates que a regra `.selected` vence no navegador.
- **Causa:** nos dois temas, a seleção é preta. No E-Ink, o hover também era preto: `--color-surface-hover` e
  `--color-tab-hover` com texto branco. Muitos componentes usam esses fundos sem trocar a cor do texto:
  - no hover: abas de navegação, abas de Ajustes, abas da biblioteca, cartões de estudo e linhas de tabela;
  - parados: o contador do painel, o selo da caixa de entrada e o `code` da lista de citações.

  Os apelidos `--color-primary-subtle`, `--color-accent-subtle` e `--accent-subtle` valem a cor de seleção, e com
  isso o selo "Você", a pílula "Modelo" e outros 13 selos de modais e da revisão ficavam com texto preto sobre
  fundo preto.
- **Correção:**
  - **Hover no E-Ink:** sublinha em vez de inverter. O fundo de hover e o de aba em hover viraram branco, e o texto
    de hover, preto. Uma regra no `themes.css` sublinha links, botões e abas sob o mouse;
  - **Tons suaves:** no E-Ink e no Monocromático, `--color-primary-subtle`, `--color-accent-subtle` e
    `--accent-subtle` deixam de ser a seleção: branco no E-Ink, `#f1f5f9` no Monocromático. Nos outros temas nada
    muda;
  - **Seleção:**
    - o número do capítulo selecionado e o botão de foco ativo, na página do livro, passam ao texto de seleção;
    - a linha em foco da lista de estudos passa ao tom suave;
  - **Capas geradas no E-Ink:** fundo preto sólido. O E-Ink remove gradientes, e o texto branco ficava sobre branco.
- **Resultado:** nenhuma falha nas 22 telas nos dois temas, paradas e com hover.
- **Testes:** três novos em `theme-contrast-tokens.test.mjs`:
  - os pares de hover e tom suave nos dois temas;
  - uma varredura que exige o texto de seleção em toda regra com o fundo de seleção;
  - a presença do sublinhado e do fundo das capas no E-Ink.

  Os três falham com o código antigo.
- **Pendente:** os outros oito temas foram conferidos só com as telas paradas, sem a simulação de hover. Feito logo
  depois (seção abaixo).

## Hover nos outros oito temas (2026-10-29)

- **Simulação:** a mesma do E-Ink, nas 22 telas dos oito temas. Ela mede também a página inteira com o `html` em
  hover, e assim cobriu as telas internas paradas do Fiorde e do Voltagem, que ainda não tinham sido conferidas.
- **Achados:**
  - **Branco fixo sobre o destaque:** 27 regras usavam `#fff`, `#ffffff` ou `white` como texto sobre
    `--color-accent` ou `--color-primary`. No Fiorde e no Voltagem o destaque é claro, e o texto ficava com 1,1 a
    1,7:1. Entre elas: selo do segmento ativo da caixa de entrada, aba ativa do editor, botões de login e cadastro,
    botões principais de modais. Também o indicador da aba ativa do editor, numa regra à parte. Todas passam a
    `--color-on-accent`, que nos temas claros já era branco ou quase branco;
  - **Hover do destaque sem trocar o texto:** 13 regras pintavam `--color-accent-hover` sem trocar a cor. Na Noite
    Suave e no Grafite esse fundo é claro, e o texto branco ficava com 2,5:1, por exemplo em "Continuar Leitura" e
    "Criar Conta". Todas passam a `--color-accent-hover-text`, e o mesmo vale para `.hero-continue-btn:hover`;
  - **Descrição das abas de Ajustes:** no hover, sobre `--color-tab-hover`, ficava com 3,9 a 4,1:1 na Noite Suave e
    no Grafite. Agora acompanha `--color-tab-hover-text`.
- **Resultado:** os 10 temas estão sem falhas nas 22 telas, paradas e com hover. Depois da última correção, as
  telas internas foram repetidas nos quatro temas escuros; nos claros, o teste de tokens garante o par.
- **Testes:** em `theme-contrast-tokens.test.mjs`:
  - uma varredura que proíbe branco fixo sobre o destaque;
  - uma varredura que exige `--color-accent-hover-text` onde o fundo é o hover do destaque;
  - a descrição da aba de Ajustes no hover;
  - o par texto e fundo do hover do destaque nos 10 temas.

  As varreduras falham com o código antigo.

## F0.10.01 — Header leve e variante neutra de botão (2026-11-01)

- **Plano:** primeira feature do Roadmap 0.10 (o plano mestre de 2026-11-01 foi renumerado para 0.10, 0.11 e 1.0,
  porque 0.8 e 0.9 já eram roadmaps entregues). Spec, plano e tarefas em `specs/092-header-leve-botao-neutro/`.
- **Causa do "efeito blocos de Lego":** a regra global `:root :is(button, .button):not([role='tab'])…` de
  `appearance-advanced.css` tem especificidade (0,4,0) e pinta todo `<button>` com o destaque. Os estilos dos
  componentes, com (0,2,0), perdem. Abas são `<a>` e escapavam; os controles da direita do header são `<button>`.
- **Solução:** variante `.quiet` (base, hover e disabled) logo depois das regras `outline`, `ghost` e `block`, no
  padrão da `.secondary`: só troca as variáveis `--button-*`, mais `width: auto` contra o modo `block`. Ganchos
  `--quiet-bg` e `--quiet-border` deixam o componente dar fundo e borda sutis.
- **Onde entrou:** "Mais" (header e barra inferior do celular), sincronização, busca, notificações, perfil,
  ferramentas da pílula do capítulo, botões de limpar e modo de visualização não selecionado da estante, e os
  controles do carrossel e da vitrine de temas da landing (que tinham reforços caso a caso). "Capturar" continua
  como a única ação com destaque.
- **Busca em pílula:** "Buscar · Ctrl K" só quando o header tem espaço. Com a grade `1fr auto 1fr` e o contêiner
  padrão de 74rem, a coluna da direita tem ~236 px e a pílula pede ~314 px; com a media query de 1024 px da spec,
  ela invadia o "Mais". Ficou uma container query de 1400 px no `.header-inner`: na prática, a pílula aparece no
  contêiner fluido em telas largas, e no resto o botão é só o ícone.
- **Sincronização:** ícone com ponto de estado (sucesso, sincronizando, offline, erro), sem os hex de fallback;
  alvo de 44 px em telas de toque.
- **Estante:** `LibraryToolbar.vue` trocou aliases antigos com hex de fallback (`--muted`, `--text`, `--bg-hover`,
  `--border`, `--bg-surface`, `--card`, `--accent`) pelos tokens canônicos.
- **Verificação no navegador (servidor de validação, banco fictício):** 2.880 medições na página do livro (10 temas
  × 6 configurações de superclasse × estilos padrão, outline e ghost × largura padrão e block) e 180 na estante:
  nenhum controle neutro com o fundo do destaque, nenhum esticado no modo block, "Capturar" sempre com destaque e o
  modo de visualização ativo também. Contraste em repouso e com hover simulado: 380 medições, nenhuma abaixo de
  4,5:1. Sem rolagem horizontal em 1920, 1366, 768 e 375 px.
- **Testes:** `feature-092-header-leve.test.mjs` (posição das regras, classe `quiet` em cada controle, "Capturar"
  sem ela, modo de visualização, sem hex de fallback); 3 pares novos em `theme-contrast-tokens.test.mjs`. O teste
  da F0.8.01 que proibia o atalho "Ctrl K" na busca passou a exigir a pílula só com espaço no header.

## F0.10.02 — Endurecimento de segurança e privacidade verificável (2026-11-01)

- **Spec, plano e tarefas:** `specs/093-endurecimento-seguranca/` (entregues juntos, aprovação única).
- **CSP:** montada por `build_csp()` a cada pedido. Sem domínios de fontes (são locais), `img-src 'self' data:
  blob:` (imagem externa num Markdown não carrega mais), `object-src 'none'` e `script-src` sem `'unsafe-inline'`.
  `https://accounts.google.com` entra em `script-src`, `connect-src` e `frame-src` só quando `GOOGLE_CLIENT_ID`
  está definido.
- **Bootstrap de aparência:** no build, o plugin do Vite emite `dist/appearance-bootstrap.js` e o chama por
  `<script src>` clássico no `<head>` (bloqueante, antes da pintura); no `vite dev` segue inline.
- **Cabeçalhos:** `Referrer-Policy: same-origin`; `X-Robots-Tag: noindex, nofollow` em tudo, exceto `/`, `/sobre`,
  `/apoie`, `/compartilhado/*`, `/robots.txt`, `/sitemap.xml` e `/.well-known/*`.
- **Origem:** `core/origin_guard.py` recusa com 403 `POST`/`PUT`/`PATCH`/`DELETE` em `/api/` vindos de outra
  origem; aceita `Host`, `X-Forwarded-Host`, `CADERNO_CORS_ORIGINS` e `LEITORUM_TRUSTED_ORIGINS`. Sem `Origin`, só
  recusa com `Sec-Fetch-Site` cross-site ou same-site.
- **`/.well-known/security.txt`:** RFC 9116; contato padrão nos avisos de segurança do GitHub,
  `LEITORUM_SECURITY_CONTACT` substitui.
- **Exclusão física:** `PRAGMA secure_delete=ON` em toda conexão e `checkpoint_after_purge()` (`wal_checkpoint(
  TRUNCATE)` com autocommit, porque a conexão do engine vive em transação) depois de exclusão permanente de livro
  ou estudo, esvaziar a lixeira, expurgo de 30 dias (só se algo saiu) e exclusão de conta (no router, depois do
  commit). Teste com sentinela fictício confere os bytes do `.db` e do `-wal`; o controle sem o pragma encontra o
  sentinela.
- **Verificação:** 34 testes novos; 212 testes de backend relacionados (segurança, SEO, lixeira, conta, auth,
  sessão) passam; build ok. No navegador: landing e `/livros` só com o próprio servidor na aba Rede; `/login` com
  o botão do Google e só `accounts.google.com`; nenhuma violação de CSP no console; criar livro, lixeira e
  restaurar funcionando com a conferência de origem.
- **Limitações registradas:** backups antigos guardam o conteúdo até a rotação; `style-src 'unsafe-inline'` e o
  sanitizador por lista de bloqueio continuam; o efeito do `Referrer-Policy: same-origin` no login com Google só
  foi visto até o botão carregar (sem concluir um login real).
- **Achado:** o sitemap e o `robots.txt` anunciam `/compartilhado/{id}`, rota que não existe no frontend (404).
  Fica para a feature de cadernos públicos do Roadmap 1.0.

## F0.10.02.5 — Correções visuais e gerenciamento de capítulos (2026-11-02, emergência)

- **Spec, plano e tarefas:** `specs/094-correcoes-capa-capitulos/`.
- **Capa no celular:** a regra móvel de `BookView.vue` mirava `:deep(.book-cover)`, classe que não existe mais; o
  `BookCover.vue` usa `.book-cover-container` (140 px no tamanho `md`). A imagem encolhia para 48×72 e o container
  seguia com 140×210, cobrindo o título. Agora a regra mira o container. Desktop sem mudança.
- **Ícones do capítulo selecionado:** as ferramentas usam a variante `.quiet` (texto do tema), mas ficam sobre
  `--color-selected-bg`; nos temas claros davam 1,0 a 2,0:1. A variante ganhou os ganchos `--quiet-fg` e
  `--quiet-fg-disabled`, e a pílula selecionada passa `--color-selected-text`: mínimo de 5,1:1 nos 10 temas (os
  desabilitados ficam em ~2,9:1, visíveis e apagados).
- **Excluir capítulo:** `DELETE /api/books/{id}/chapters/{id}` só para capítulo vazio; com estudos (ativos ou na
  lixeira) responde 409 e nada é apagado; senão renumera as posições. Na interface, botão de lixeira nas
  ferramentas do capítulo (desktop) e item "Excluir" no menu móvel, com confirmação (`TrashConfirmModal`, `danger`);
  com estudos ativos, o aviso aparece antes, sem abrir a confirmação.
- **Celular:** menu "Gerenciar capítulo" (⋯) ao lado do seletor, com mover para trás, mover para frente, renomear e
  excluir; renomear abre um campo abaixo do seletor.
- **Defeitos antigos corrigidos no caminho (mesma tela, mesmas ações):**
  - mover o capítulo selecionado sem `?chapter=` na URL fazia a seleção pular para o novo primeiro capítulo; agora
    a URL fixa o capítulo movido;
  - `editChapterInputRef` dentro do `v-for` vira lista, e `.focus()` lançava erro: nenhum campo de renomear recebia
    foco (desktop inclusive);
  - o rótulo "Selecione o capítulo" usava `.sr-only`, classe inexistente, e aparecia na tela espremendo o seletor.
- **Testes:** `test_chapter_delete.py` (5) e `feature-094-capa-capitulos.test.mjs` (4); o teste da F0.10.01 passou
  a contar 4 ferramentas e a aceitar o gancho `--quiet-fg`. `npm test` 693, 93 testes de backend de capítulos,
  livros e lixeira, build ok.
- **Navegador (banco fictício, 1366 e 375 px):** capa 48×72 sem cobrir o título; renomear, mover e excluir no
  desktop e no celular, conferidos também pela API depois de cada ação; capítulo com estudos recusado.
- **Complemento (mesmo dia): mudar o estudo de capítulo.** `POST /api/studies/{id}/chapter` (`change_study_chapter`
  em `study_service.py`): só capítulos do mesmo livro e do mesmo dono; o estudo vira raiz no fim do capítulo de
  destino, os irmãos da origem são renumerados e a subárvore inteira (inclusive subestudos na lixeira) acompanha;
  aceita `expected_version` (409 se desatualizado). Na tela de leitura, item "Mudar de capítulo" no menu "Mais
  opções", que abre o `ChangeChapterModal` (capítulo atual listado e desabilitado); depois de mover, o contexto é
  recarregado e a trilha mostra o capítulo novo. Testes: `test_study_chapter_change.py` (6) e mais um caso em
  `feature-094-capa-capitulos.test.mjs`; `npm test` 694; 133 testes de backend de estudos e capítulos; navegador em
  1366 e 375 px com dados fictícios.

## F0.10.03 — Painel de Sistema: segurança, backups e soberania (2026-11-03)

- **Spec, plano e tarefas:** `specs/095-painel-sistema-soberania/`.
- **Versão em execução:** `core/build_info.py` lê o commit de `LEITORUM_BUILD_COMMIT` ou do `.git` (HEAD, ref solta,
  `packed-refs`, HEAD destacado, `gitdir:`), sem chamar o `git`, subindo no máximo 3 pastas acima de `backend/`
  (mais que isso acharia repositórios alheios, como um `.git` na pasta do usuário). A interface leva o próprio
  commit no build (`__BUILD_COMMIT__`, `vite.config.ts`). O painel avisa quando os dois diferem — o caso do 405 de
  2026-11-02 — e quando a revisão do banco não é a última migração do código.
- **API:** `GET /api/system/status` (versão, commit, revisão atual e esperada, Google ligado, `secure_delete`; bloco
  de backups só para administrador, sem caminhos) e `POST /api/system/integrity-check` (administrador;
  `quick_check` + `foreign_key_check` em modo somente leitura, mensagem sem o caminho do banco).
- **Backups:** `maintenance.auto_backup_status()` — ligado, intervalo, quantos guardar, quantos há, último, atrasado
  (mais que o dobro do intervalo) e segunda cópia configurada.
- **Tela:** `SystemSovereigntyCard.vue` na aba Sistema, com "Seus dados e a exclusão" (só o que o código faz,
  conferido na F0.10.02) e link para a exportação na aba Conta; o card de conexão mostra o commit da interface; o
  `DatabaseBackup` (backup manual e restauração) passou a aparecer só para administrador, porque a API sempre
  recusava os demais.
- **Testes:** `test_system_status.py` (12) e `feature-095-painel-sistema.test.mjs` (4); `npm test` 698; 142 testes
  de backend relacionados; build ok. Navegador (banco fictício, `LEITORUM_BUILD_COMMIT=1111111` forçado): aviso de
  divergência, integridade "Banco íntegro", bloco de backups, link para Conta, 1366 e 375 px sem rolagem lateral.

## F0.10.04 — Revisão: baldes, sessões de 5/10/15 e gaveta de contexto (2026-11-03)

- **Spec, plano e tarefas:** `specs/096-revisao-baldes-sessao/`.
- **Baldes:** Novos, Difícil, Médio e Fácil, derivados de `last_rating` (sem migração). `GET /api/review/stats`
  devolve `buckets` e aceita `book_id`, `chapter_id` e `kind` só para eles (a faixa de prontidão segue global);
  `GET /api/review/items?bucket=` filtra sem mudar a ordem. Filtros comuns em `_scope_filters()`.
- **Sessão estruturada sem balde:** ao reabrir, o servidor recalcula os cartões pendentes a partir do escopo gravado
  em `study_sessions`, que não guarda o balde; guardar exigiria migração. A tela avisa quando há balde escolhido.
- **Tamanho da sessão:** 5, 10 ou 15 (padrão 10), em `localStorage` (`caderno_review_session_size`), nas três
  entradas (prática no hub, revisar mais e sessão estruturada).
- **Gaveta "Ver o estudo":** `StudyContextDrawer.vue` (Drawer + MarkdownContent com as 4 partes), só depois de
  revelar a resposta, no hub e na sessão estruturada; com a gaveta aberta, os atalhos de teclado do cartão (Espaço,
  1, 2, 3) ficam desligados.
- **Filtros da revisão:** os botões de tipo, balde e tamanho usavam o fundo de destaque mesmo sem estar
  selecionados (regra global de botões) e, no celular, encolhiam cortando o texto. Agora só o selecionado tem
  destaque (`.quiet` nos demais) e eles quebram linha.
- **Testes:** `test_review_buckets.py` (9) e `feature-096-revisao-baldes.test.mjs` (3). Navegador (dados
  fictícios): pedido `limit=5&bucket=hard`, sessão com 3 itens difíceis, gaveta, atalho bloqueado, contraste dos
  filtros nos 10 temas (240 medições, sem falhas), 375 px sem rolagem lateral nem texto cortado.
- **Fecho do lote de 5 (F0.10.01, .02, .02.5, .03 e .04):** `npm test` 701; `pytest` completo 759 aprovados e 1
  pulado depois de corrigir `test_local_server.py` (exigia todo script em `/assets/`; desde a F0.10.02 o bootstrap
  de aparência fica na raiz, com `no-cache`), em commit próprio; build ok.

## F0.10.05 — Destaques: cópia ABNT e tipografia citação × anotação (2026-11-07)

- **Spec, plano e tarefas:** `specs/098-destaques-abnt-tipografia/`. Primeira feature do lote 2.
- **Citação literal × texto do leitor:** quase todo destaque é feito sobre o texto do próprio leitor, mas todo
  cartão aparecia entre aspas e era copiado como citação direta. Agora o leitor marca "Citação literal" no cartão
  (`aria-pressed`, só para Destaque, Anotação e Citação), que grava `kind = quote` pelo `PATCH` existente (sem
  migração; desmarcar volta a `note` se houver nota, senão `highlight`). Atualização otimista com reversão em erro
  e ajuste do resumo por tipo.
- **Tipografia:** citação literal em serifa, com aspas e o rótulo "Palavras do autor"; texto do leitor em sans, sem
  aspas, borda tracejada e o rótulo da seção de origem ("Do seu Resumo", "Do fichamento importado" etc.).
- **ABNT:** `citationFormatter.ts` reescrito. Chamada da NBR 10520:2023 (sobrenome em maiúsculas e minúsculas,
  "Nome Sobrenome" e "Sobrenome, Nome", Júnior/Filho/Neto/Sobrinho, até 3 autores com `;`, 4 ou mais com `et al.`,
  sem autor pela primeira palavra do título, sem ano `[s. d.]`, sem página). Literal → citação direta com aspas
  (aspas internas viram simples); texto do leitor → citação indireta. Novo item "Referência (NBR 6023)", com HTML
  (título em itálico) via `utils/clipboard.ts` (`ClipboardItem` → `writeText` → `textarea`). Markdown com o ano.
- **API:** a biblioteca devolve `book_year` e `book_subtitle`.
- **Cartão:** menu de formatos fecha com Esc (foco volta ao gatilho), clique fora e depois de copiar; "Copiado"
  anunciado em `aria-live`; controles secundários com `.quiet` (Salvar e Confirmar mantêm o destaque).
- **Testes:** `test_highlight_library_book_meta.py` (2) e `feature-098-destaques-abnt.test.mjs` (19); ajustado
  `citation_formatter.test.mjs` ao formato novo; 43 testes de Destaques no frontend e 8 no backend; build ok.
  Navegador (dados fictícios): cópias direta, indireta, referência em texto e HTML, menu com Esc e clique fora,
  alternância persistida, contraste nos 10 temas (mínimo 4,83:1), menu dentro da tela em 375 px.
- **Fora:** página da citação, editora e cidade (exigem migração; referências do 0.11) e a cópia da tela do estudo.

## F0.10.06 — Importar: faixa de metadados da obra e ganchos para referências (2026-11-07)

- **Spec, plano e tarefas:** `specs/099-importar-metadados-referencias/`. O plano mestre não detalhava a feature; a
  leitura aprovada: 3 escopos = **obra** (livro), **trecho** (capítulo e localização do estudo) e **obras citadas**
  (seção Referências). Sem migração e sem mudança no backend.
- **Ganchos:** `utils/referenceScopes.ts` (puro): `parseLocator` ("p. 32–34", "pp. 32-34", "pág. 7", "32-34" →
  página com meia-risca; "Loc. 1820", "posição 1820" → `loc.`; o resto fica como texto), `referenceLines`,
  `buildReferenceScopes` (com `missing` da obra) e `abntCallWithLocator` (reaproveita `abntAuthorCall` da F0.10.05).
  O 0.11 deve gerar CSL-JSON, BibTeX e ABNT/APA a partir dele.
- **Tela:** `components/import/ImportWorkMetaStrip.vue` dentro da faixa da Importar: linha `Autor · Ano · Subtítulo`
  ("sem autor"/"sem ano" em tom neutro), aviso do efeito na citação, "Completar dados do livro" na própria faixa
  (`PATCH /api/books/{id}` com `expected_version`; ano 1000–2100; erro mostrado sem perder o digitado; só com
  `can_edit`), e a prévia "Como este estudo será citado" com a chamada (`(Sobrenome, ano, p. X)`) e os 3 escopos.
  O campo da faixa passou a se chamar "Página ou localização", como no ajuste manual.
- **Testes:** `feature-099-importar-metadados.test.mjs` (9); vizinhos da Importar passando; build ok. Navegador
  (dados fictícios): livro sem ano completado na faixa (ano inválido recusado), prévia `(Modelo Júnior, 1999, p.
  32–34)`, contraste nos 10 temas (mínimo 5,49:1), 320 e 375 px sem rolagem lateral.
- **Achado fora do escopo:** no worktree, `tests/superclasses.test.mjs` (US1 da Invisível) falha porque o CSS saiu
  com CRLF no checkout e o teste procura `button,\n  .button`; no checkout principal passa. Ver no fecho do lote.

## F0.10.07 — Amigos: leituras e estudos em comum (2026-11-07)

- **Spec, plano e tarefas:** `specs/100-amigos-em-comum/`. Sem migração.
- **API:** `GET /api/users/{username}/in-common` (`services/in_common_service.py`, `schemas/in_common.py`). Bloqueio,
  usuário inexistente ou o próprio visitante → 404; não amigo → `is_friend: false` sem listas. Do lado do amigo, só
  livros `friends`/`public` não excluídos e estudos que passam em `can_read_study`; livros privados dele nunca
  aparecem, nem como contagem. Casamento por `normalize_title_key` (sem acentos, caixa, pontuação e subtítulo depois
  de `:`) e, quando os dois têm autor, pelo sobrenome do primeiro autor (`first_author_surname_key`, aceita
  "Sobrenome, Nome" e Júnior/Filho/Neto/Sobrinho). Até 30 livros (`books_truncated`) e 5 estudos por livro (com o
  total); `shared_with_me_total` vem de `get_shared_studies_for_user(author=...)`.
- **Tela:** `components/profile/ProfileInCommon.vue` no perfil de outro leitor (some para quem não é amigo): livros
  em comum com "Seu livro", estudos do amigo com link de leitura, e "N estudos compartilhados com você — Ver todos",
  que abre `/livros?aba=compartilhados&autor=usuario` (a Biblioteca e a `SharedStudiesList` passaram a ler esses
  parâmetros).
- **Testes:** `test_users_in_common.py` (8) e `feature-100-amigos-em-comum.test.mjs` (5); vizinhos de amizade,
  compartilhamento, perfil e Biblioteca passando; build ok. Navegador (banco temporário, amiga fictícia semeada):
  livro privado e estudo privado da amiga ausentes, "Ver todos" abrindo a aba filtrada, contraste nos 10 temas
  (mínimo 5,35:1), 375 px sem rolagem lateral.
- **Fora:** ISBN (0.11), contagem "em comum" nos cartões da lista de amigos, destaques em comum.

## F0.10.08 — Landing: Desafio F12 e custo com fontes e datas (2026-11-07)

- **Spec, plano e tarefas:** `specs/101-landing-confianca-f12/`. Só frontend. O Notion entrou a pedido do usuário.
- **Desafio F12** (`components/landing/TrustChallengeSection.vue`, `#desafio-f12`): três passos para abrir a aba
  Rede; painel "Conferir nesta página" com os endereços que o navegador contatou (Resource Timing, agrupados por
  origem em `utils/networkAudit.ts`, ignorando `data:`/`blob:`), "Conferir de novo" com `aria-live`; a CSP lida do
  cabeçalho de um `HEAD` à raiz (ou o aviso de que não veio); nota sobre extensões e o login com Google.
- **Quanto custa** (`components/landing/CostComparison.vue`, `#custo`, dados em `costSources.ts`): Leitorum
  US$ 0 de licença, sem estimar energia nem máquina; Readwise (Full 9,99/12,99, Highlights 7,99/8,99, Lite
  5,59/6,99 — anual por mês/mensal) e Notion (Free 0; Plus 10/12 por vaga), em dólar, conferidos nas páginas
  oficiais em 07/11/2026. Cada linha mostra a fonte e a data; o teste recusa preço sem `sourceUrl` https ou
  `checkedAt` ISO. **Para atualizar:** conferir as páginas e trocar valores e `checkedAt` no arquivo.
- **Testes:** `feature-101-landing-confianca.test.mjs` (8); vizinhos da landing passando; build ok. Navegador
  (servidor de validação com login exigido, visitante anônimo): painel com só `http://127.0.0.1:8010`, CSP real
  (`default-src`, `script-src`, `img-src`, `connect-src`, `frame-ancestors`), contraste nos 10 temas (mínimo
  5,35:1), 375 px sem rolagem da página (a tabela rola no próprio contêiner, focável).

## F0.10.10 — Correções reservadas do 0.10 (2026-11-07)

- **Spec, plano e tarefas:** `specs/102-correcoes-reservadas-010/`. Não havia lista no repositório; o usuário aprovou
  seis itens (um do HANDOFF, três das pendências do HANDOFF §5, dois achados no lote 2). Sem migração.
- **1. Revisão:** o hub tinha "Praticar Revisão Agora" e "Prática Rápida neste Hub" (a mesma função) e "Iniciar
  Sessão Estruturada". Agora: "Praticar agora (N itens)" na faixa de prontidão e uma única ação secundária
  `.quiet`, "Sessão registrada (até N itens)", com "Fica no histórico e pode ser retomada depois." O resumo do fim
  de sessão dizia "Revisar mais 10" fixo; passou a usar o tamanho escolhido (`moreCount`).
- **2. Licença:** rodapé (`App.vue`, `AppFooter.vue`) diz "Código-fonte público" com link para o repositório; a
  página Apoie diz "com código-fonte público". Escolher uma licença continua com o dono do projeto.
- **3. Digitalização:** `busy` e `low_memory` (`DIGITIZE_TRANSIENT_CODES`) guardam a foto; a tela diz "Não deu para
  ler agora" e oferece "Tentar de novo" (`draft.retry()`), com "Tentar outra foto" como secundário.
- **4. SEO:** `seo_service.PUBLIC_STUDY_PAGES_ENABLED = False` tira `Allow: /compartilhado/` do `robots.txt` e os
  estudos do sitemap enquanto a rota não existe; o 1.0 liga. Testes nos dois estados.
- **5. Cópia na tela do estudo:** a barra flutuante copia citação indireta ABNT com a página do estudo
  (`formatIndirectCitationWithLocator` em `referenceScopes.ts`). `formatQuoteText` ficou (tem testes próprios).
- **6. Teste:** `superclasses.test.mjs` normaliza CRLF ao ler arquivos; passa também no worktree.
- **Testes:** `feature-102-correcoes-reservadas.test.mjs` (5), `test_seo_public_pages_flag.py` (3); ajustados
  `feature-068-revisao-hub`, `review-hub-view`, `feature-086-digitalizar-caderno-estudo` (mais dois casos de "Tentar de
  novo") e `test_seo_and_public_presence` (estado ligado). Navegador: hub com duas entradas em 1366 e 375 px,
  rodapé, `robots.txt` e sitemap sem `/compartilhado/`. A tela de erro passageiro da digitalização e a cópia no
  estudo foram conferidas só pelos testes (o servidor de validação não tem o motor de leitura).

## Fecho do lote 2 do 0.10 (2026-11-07)

- **Features:** F0.10.05 (`e6ad68f`), F0.10.06 (`da4a675`), F0.10.07 (`d17ee7e`), F0.10.08 (`1ab3ae8`), F0.10.10
  (`f7dbc58`). Não há F0.10.09. **Roadmap 0.10 concluído.**
- **Suítes:** `npm test` 749/749 e `pytest` completo 788 aprovados e 4 pulados (sozinho, banco descartável,
  `LEITORUM_SECONDARY_BACKUP_DIR=""`, `LEITORUM_STORAGE_ROOT=""`); build ok.
- **Falha antiga corrigida em commit próprio** (`0214933`): quatro testes de código-fonte (`theme-contrast-tokens`,
  `dashboard-theme-contrast`, `feature-077-shell-mobile`, `friends`) falhavam quando o arquivo lido estava com CRLF
  — no checkout principal, o `DigitizeNotebookView.vue` passou a sair com CRLF depois do merge. Novo
  `tests/helpers/normalize-eol.mjs`, importado por eles.
- **Conversa em worktree:** cada commit foi levado ao `main` por fast-forward e o build refeito no checkout
  principal. Push e `Restart-Service -Name Leitorum` ficam com o usuário.

## F0.11.01 — Estados de leitura do livro (2026-11-09)

- **Spec, plano e tarefas:** `specs/103-estados-leitura-livro/`. Primeira feature do Roadmap 0.11. **Com migração**
  (`0034_book_reading_state`).
- **Banco:** `books.reading_state` (`quero_ler`, `lendo`, `lido`, `abandonado` ou nulo, com `CHECK` na coluna),
  `reading_started_on` e `reading_finished_on` (datas), índice `ix_books_user_reading_state`. `ADD COLUMN` simples
  (recriar `books` no SQLite esbarraria no `RESTRICT` de `chapters`); `downgrade` com `DROP COLUMN`. Livros antigos
  ficam sem estado.
- **API:** `BookPatch` aceita os três; `apply_reading_state_rules` (em `routers/books.py`) preenche início ao passar a
  "Lendo" e fim ao passar a "Lido" quando vazios e recusa fim antes do início (422). `GET /api/books/{id}` zera os
  três para quem não é o dono. Exportação do livro só leva o estado quando quem exporta é o dono
  (`ExportOptions.include_reading_state`); o `.zip` da conta e a sincronização levam sempre (são do próprio dono).
- **Tela:** `components/books/BookReadingState.vue` na página do livro (radiogroup com setas, datas, grava com
  `expected_version`; durante a gravação usa `aria-busy` em vez de desabilitar, para não perder o foco); selo e
  filtro "Leitura" na biblioteca (`useLibraryFilter`, `caderno_library_reading_state` no `localStorage`).
- **Snapshot:** o script `migrar_com_backup.py` previsto na spec não foi criado — o `migrations/env.py` já faz o
  snapshot validado antes de qualquer migração e aborta se falhar.
- **Testes:** `test_book_reading_state.py` (10, inclusive migração subindo e descendo com dados fictícios e o snapshot
  antes da 0034) e `feature-103-estados-leitura.test.mjs` (5); vizinhos passando; build ok. Navegador (banco
  temporário migrado): estados, datas automáticas, recusa de fim < início, setas com foco, selo, filtro lembrado,
  contraste nos 10 temas (mínimo 4,76:1), 320 px sem rolagem lateral.
- **Implantação (banco ativo):** o `iniciar.py` recusa subir com migração pendente. Procedimento:
1. Parar o serviço (PowerShell como administrador): `Stop-Service -Name Leitorum`.
  2. Migrar, na pasta `caderno-leitura-0.1\backend` do checkout principal:
     `.\.venv\Scripts\python.exe -m alembic upgrade head`. Antes de mexer no banco, o Alembic cria e valida o
     snapshot `backups\caderno-pre-migracao-AAAAMMDD-HHMMSS.db` (com cópia na segunda pasta de backups, se configurada)
     e aborta a migração se o snapshot falhar.
  3. Conferir o snapshot: `.\.venv\Scripts\python.exe -m app.services.maintenance verificar-snapshot <caminho>`.
  4. Iniciar o serviço: `Start-Service -Name Leitorum` (ou `Restart-Service`).

## F0.11.02 — Bandeja de triagem por capítulo (2026-11-09)

- **Spec, plano e tarefas:** `specs/104-bandeja-triagem-capitulo/`. **Com migração** (`0035_inbox_capture_chapter`).
- **Banco:** `inbox_captures.chapter_id` (FK para `chapters`, `ON DELETE SET NULL`) e índice
  `ix_inbox_captures_user_chapter_status`. `ADD COLUMN` simples; `downgrade` com `DROP COLUMN`.
- **API:** criar/editar captura com `chapter_id` (capítulo de livro do próprio leitor e fora da lixeira, senão 404
  "Capítulo associado não encontrado."); o capítulo define o livro; trocar só o livro limpa o capítulo; `null`
  explícito limpa o capítulo. `GET /api/inbox?chapter_id=` e `GET /api/inbox/book-tray?book_id=` (contagens das
  pendentes por capítulo e sem capítulo).
- **Tela:** captura rápida com "Capítulo (Opcional)"; a página do livro informa livro e capítulo abertos
  (`useQuickCapture().setPageContext`), então o botão global "Capturar" já vem preenchido. `ChapterTray.vue` na
  área do capítulo (recolhível; "Virar estudo", "Arquivar", "Abrir na Mesa de Triagem", "Capturar neste capítulo";
  texto recortado em 3 linhas — uma regra global troca o `display` de `<p>`, por isso há `max-height` além do
  `line-clamp`); contagem nas pílulas dos capítulos; linha "N capturas do livro sem capítulo". Importar escolhe o
  capítulo da captura promovida; o cartão da Mesa mostra "Livro · Capítulo" e edita o capítulo; a Mesa aceita
  `?livro=ID`.
- **Testes:** `test_inbox_chapter_tray.py` (6, inclusive migração e snapshot antes da 0035) e
  `feature-104-bandeja-capitulo.test.mjs` (5); vizinhos passando; build ok. Navegador (banco temporário): contagens,
  arquivar, captura global preenchida com livro e capítulo, "Virar estudo" com capítulo na Importar, Mesa filtrada,
  contraste nos 10 temas (mínimo 5,35:1), 320 e 375 px sem rolagem lateral.
- **Implantação:** o banco ativo ainda está antes da 0034; o mesmo `alembic upgrade head` aplica 0034 e 0035 com um
  snapshot antes (procedimento no HANDOFF).

## F0.11.03 — Importar destaques do Kindle e do Kobo (2026-11-09)

- **Spec, plano e tarefas:** `specs/105-importar-kindle-kobo/`. **Sem migração.**
- **Parsers** (`services/ereader_import/`): `kindle.py` lê `My Clippings.txt` (BOM, CRLF, cabeçalho em inglês ou
  português, título com parênteses, fim de posição abreviado "100-02", marcadores ignorados, seleção ajustada vira um
  destaque só — o mais longo —, nota juntada ao destaque do mesmo lugar); `kobo.py` lê `KoboReader.sqlite` numa
  cópia temporária aberta `mode=ro`, com `quick_check`, só `SELECT` em `Bookmark`/`content`, até 50 mil marcações;
  a cópia é apagada no `finally`. `detect_format` reconhece pelo conteúdo.
- **API:** `POST /api/inbox/ereader/preview` (só lê: por livro, contagens, duplicatas e sugestão de livro do acervo
  — título normalizado, também sem os parênteses finais que o Kindle anexa, e sobrenome do primeiro autor) e
  `POST /api/inbox/ereader/import` (arquivo + escolhas `existing`/`create`/`skip`). Cada destaque vira captura
  `inbox` sem capítulo; `source_hint` como `Kindle · p. 32 · pos. 488–489 · 03/03/2025`; duplicata = mesmo livro +
  texto + origem. Limites: Kindle 20 MB, Kobo 200 MB (leitura em blocos de 1 MB).
- **Tela:** `views/EreaderImportView.vue` em `/inbox/importar-leitor` (nome `ereader-import`, registrado nos contratos de
  responsividade das specs 076 e 081), botão na Mesa de Triagem.
- **Testes:** `test_ereader_import.py` (11, com `My Clippings.txt` e `KoboReader.sqlite` sintéticos) e
  `feature-105-importar-kindle-kobo.test.mjs` (3); vizinhos e guardas de rotas passando; build ok. Navegador (banco
  temporário): Kindle e Kobo de ponta a ponta, reenvio sem duplicar, capturas na linha "sem capítulo" da bandeja,
  contraste nos 10 temas (mínimo 5,49:1), 320/375/768/1024/1440 px sem rolagem lateral.

## F0.11.04 — ISBN sob demanda (2026-11-09)

- **Spec, plano e tarefas:** `specs/106-isbn-sob-demanda/`. **Com migração** (`0036_book_isbn_publisher`) e **uma saída
  de rede nova**, só a pedido.
- **Banco:** `books.isbn` (ISBN-13 sem separadores), `publisher` e `publication_place`, índice `ix_books_user_isbn`.
- **Busca** (`services/isbn_service.py`): `normalize_isbn` (ISBN-10/13, dígito verificador, 10 → 13); `lookup_isbn`
  consulta do **servidor** a BrasilAPI e, se não achar, a Open Library (`httpx`, 5 s, sem seguir redirecionamentos,
  resposta até 512 KB, `User-Agent: Leitorum`, só o ISBN sai). `GET /api/books/isbn/{isbn}` → sugestão (com
  `existing_book` se o leitor já tem o ISBN), 422 inválido, 404 não encontrado ou desligado, 503 fora do ar.
  `LEITORUM_ISBN_LOOKUP=off` desliga; `/api/system/status` informa `isbn_lookup_enabled`. Transporte trocável
  (`set_transport`) para testes — nenhum teste vai à internet.
- **Tela:** `components/books/IsbnLookup.vue` no cadastro (gaveta) e na edição do livro: confere o ISBN antes de
  buscar, mostra a sugestão com a fonte, "Usar estes dados" preenche só o que está vazio (ou tudo, se marcado),
  avisa ISBN repetido. A página do livro mostra "Editora · Local · ISBN". A referência ABNT dos Destaques passa a
  sair com "Local: Editora, ano." (`[S. l.]`/`[s. n.]` para o que faltar); a biblioteca de destaques devolve
  `book_publisher` e `book_publication_place`. Exportações levam os três campos.
- **Landing:** "Conexões externas" inclui a busca pelo ISBN ("sempre a seu pedido"); o Desafio F12 explica que capa por
  endereço e ISBN saem do servidor, por isso não aparecem na lista do navegador. CSP inalterada.
- **Testes:** `test_isbn_lookup.py` (11, com `httpx.MockTransport`) e `feature-106-isbn.test.mjs` (4); vizinhos
  passando; build ok. Navegador (servidor de validação com transporte falso, sem rede): cadastro pelo ISBN-10,
  inválido recusado sem ir à rede, autor digitado preservado, aviso de ISBN repetido, "não encontrado", contraste nos
  10 temas (mínimo 5,49:1), 375 px sem rolagem lateral.
- **Implantação:** o mesmo `upgrade head` do HANDOFF agora aplica 0034, 0035 e 0036.

## F0.11.05 — Referências em 3 escopos (2026-11-09)

- **Spec, plano e tarefas:** `specs/107-referencias-tres-escopos/`. Só frontend; sem migração.
- **Formatos** (`utils/referenceFormats.ts`, puro): ABNT (NBR 6023, via `formatReferenceABNT`), APA 7ª ed. (iniciais,
  partículas ignoradas, hífen "J.-P.", `&` antes do último, reticências acima de 20 autores, `(s.d.)`), BibTeX `@book`
  (chave `sobrenome+ano+palavra`, escape numa passada só — escapar em etapas transformava `\` em
  `\textbackslash\{\}` —, nome único entre chaves, `chapter`/`pages`/`note` no trecho) e CSL-JSON `type: book`
  (`page` e `note` no trecho). Chamadas ABNT e APA (`p.`/`pp.`, `pos.`), `bibliography()` com ordem alfabética e chaves
  únicas (`a`, `b`, …), `missingReferenceFields`.
- **Tela:** `components/references/ReferencePanel.vue` (gaveta com abas ABNT/APA/BibTeX/CSL-JSON, Copiar com HTML para
  ABNT/APA, Baixar, aviso do que falta com atalho para Editar livro, chamada do trecho, obras citadas "como você
  escreveu", só em texto). As abas têm estilo próprio: a regra global de botões exclui `role="tab"`. Na página do
  livro (botão e menu "Referência"), na do estudo (menu "Mais opções do estudo") e "Baixar bibliografia" na Biblioteca
  sobre os livros filtrados.
- **Testes:** `feature-107-referencias.test.mjs` (8); vizinhos e guarda de tokens (075 recusou `--color-focus`, que não
  existe; usado `--ring-focus`) passando; build ok. Navegador (dados fictícios): quatro formatos com trecho, copiar
  (texto + HTML), baixar `.txt`/`.bib`, obras citadas, aviso de campos ausentes, bibliografia BibTeX dos 6 livros,
  contraste nos 10 temas (mínimo 5,11:1), 375 px sem rolagem lateral (conferido pela captura).

## Fecho do lote 1 do 0.11 (2026-11-09)

- **Features:** F0.11.01 (`e433f23`, migração 0034), F0.11.02 (`22b3b32`, migração 0035), F0.11.03 (`a5354c4`),
  F0.11.04 (`3480a4a`, migração 0036), F0.11.05 (`b1db1e9`).
- **Suítes:** `npm test` 774/774 (no checkout principal) e `pytest` completo 825 aprovados e 4 pulados (sozinho, banco
  descartável); build ok.
- **Falha de feature anterior, em commit próprio** (`fd2c5fc`): o `alembic check` (`test_migration_matches_models`)
  acusou a `0035`: a chave estrangeira de `inbox_captures.chapter_id` foi criada sem nome (`ADD COLUMN ... REFERENCES`),
  e o SQLite só guarda o nome de chave declarada na tabela. A migração passou a usar o modo batch (recria
  `inbox_captures`, que nenhuma tabela referencia) com `fk_inbox_captures_chapter_id_chapters`. Ela ainda não tinha sido
  aplicada no banco ativo; os testes de migração da F0.11.02 (subir com captura fictícia e descer) continuam passando.
- **Lição:** chave estrangeira em migração nova vai por `batch_alter_table` com nome da convenção; `ADD COLUMN` serve
  para colunas sem FK (como na 0034 e na 0036).

## F0.11.06 — Léxico de conceitos e `[[conceito:…]]` (2026-11-12)

- **Spec, plano e tarefas:** `specs/108-lexico-conceitos/`. Primeira feature do lote 2 do 0.11. **Sem migração.**
- **Léxico derivado** (`services/concept_lexicon.py`): `parse_concepts` lê a seção Conceitos (`- **Termo**: def`,
  `**Termo** — def`, `Termo: def`, `Termo – def`, `### Termo` + parágrafo; termo de até 80 caracteres e 8 palavras;
  o resto é ignorado); `concept_key` sem acento/caixa (`mimese`); plural simples fundido só se a forma singular existe;
  `extract_concept_mentions` com trecho legível (colchetes removidos). Só estudos do próprio leitor, fora da lixeira.
- **API** (`routers/concepts.py`): `GET /api/concepts?q=&page=&per_page=`, `/api/concepts/candidates`,
  `/api/concepts/{key}` (404 se não existir).
- **Tela:** `views/LexiconView.vue` (`/conceitos`, rota `lexicon`) e `views/ConceptView.vue` (`/conceitos/:key`, rota
  `concept`), com entradas "Léxico" na barra secundária, no menu "Mais" do celular e no menu do usuário; rotas nos
  contratos 076/081. Markdown: `[[conceito:Termo]]` → `<a class="study-concept-mention">` (antes das menções a estudo,
  fora de `code`); `MarkdownContent` navega para o conceito. Editor: `[[` sugere estudos e conceitos
  (`[[conceito:` filtra só conceitos) e insere `[[conceito:Termo]]`.
- **Testes:** `test_concept_lexicon.py` (4) e `feature-108-lexico.test.mjs` (4); vizinhos passando; build ok. Navegador
  (dados fictícios): léxico, link do estudo para o conceito, página com definições e menções, autocompletar no
  editor, contraste nos 10 temas (mínimo 5,35:1), 375 e 1024 px sem rolagem lateral.

## F0.11.07 — Validador de paráfrase (2026-11-12)

- **Spec, plano e tarefas:** `specs/109-validador-parafrase/`. Segunda feature do lote 2 do 0.11. **Sem migração.**
- **Cálculo no navegador** (`utils/paraphraseCheck.ts`): frases do Resumo, Explicação e Conceitos (6+ palavras, sem
  Markdown, sem trechos entre aspas, `>` ou marcados como citação literal) contra janelas de 1 a 3 frases da fonte;
  Jaccard de trigramas de palavras + maior sequência comum. **Cópia** (≥ 0,50 ou 12+ palavras seguidas), **Muito
  próxima** (0,25 a 0,49). Índice invertido de trigramas (200 mil palavras: verificação < 300 ms no teste).
  `markAsQuote` põe aspas e a chamada `(SOBRENOME, ano, p. )`.
- **Fontes** (`services/paraphrase_sources.py`, `routers/paraphrase.py`): `GET /api/studies/{id}/paraphrase-sources`
  e `GET /api/chapters/{id}/paraphrase-sources` — só **texto do livro**: capturas da Mesa do mesmo livro e citações
  literais (`quote`) de outros estudos do mesmo livro; as `quote` do próprio estudo voltam como `declared_quotes`.
  **O fichamento (`source_response`) não é fonte**: é o texto que vira as seções na importação ou a página manuscrita
  na digitalização (correção feita na execução; registrada na spec).
- **Tela:** `components/studies/ParaphrasePanel.vue` na edição do estudo e na importação (fechado por padrão;
  atualiza 400 ms depois de parar de digitar; "Marcar como citação").
- **Testes:** `test_paraphrase_sources.py` (3) e `feature-109-parafrase.test.mjs` (8); vizinhos passando; build ok.
  Navegador (dados fictícios): edição e importação, cópia e "muito próxima", paráfrase real não sinalizada, citação
  declarada fora, "Marcar como citação", contraste nos 10 temas (mínimo 5,19:1), 375 px sem rolagem lateral e botões
  de 46 px.

## F0.11.08 — Evolução da revisão (2026-11-12)

- **Spec, plano e tarefas:** `specs/110-evolucao-revisao/`. Terceira feature do lote 2 do 0.11. **Migração `0037`**
  (`study_highlights.difficulty_weight` preenchida pela última nota; tabela `concept_reviews`), **não aplicada ao
  banco ativo**.
- **Peso e fila** (`services/review_weights.py`): `peso = 0,5 × anterior + 0,5 × alvo` (difícil 1, médio 0,5, fácil 0);
  intervalo 1/3/7/14 dias pelo peso; fila nunca revisados → vencidos → demais, do mais pesado. Sem peso guardado vale
  o equivalente da última nota (`effective_weight`). Os baldes seguem pela última nota.
- **Cartões de conceito** (`services/concept_review_service.py`): `GET /api/review/items?kind=concept` (livro,
  capítulo, balde, `fragile=true`), `POST /api/review/concepts/{key}/record`; com `kind=concept`, `/review/stats`
  devolve baldes e totais dos cartões. **Conceitos frágeis**: peso ≥ 0,6 pelo cartão ou pela média das perguntas dos
  estudos que definem o conceito; `GET /api/review/fragile-concepts`; `fragile` no léxico.
- **Memória do Dia** (`services/daily_memory.py`, `GET /api/dashboard/memory?tz_offset=`): 30+ dias; aniversário →
  mesmo dia do mês → sorteio fixo do dia; `hidden` e lixeira fora.
- **Tela:** filtro "Conceitos" e verso com definições (`ReviewStatsHeader`, `ReviewCard`, `useReviewSession` grava no
  endpoint certo), `FragileConceptsPanel.vue` na Central, etiqueta "Frágil" no Léxico e no conceito,
  `DailyMemoryCard.vue` no Painel (`utils/timeAgo.ts`).
- **Testes:** `test_review_weights.py`, `test_concept_reviews.py`, `test_daily_memory.py`, `test_migration_0037.py`
  (13) e `feature-110-revisao.test.mjs` (3); vizinhos (104 no backend, 85 no frontend) e build ok. Navegador (dados
  fictícios): Memória do dia, prática de conceitos gravando em `/review/concepts/…`, bloco de frágeis, etiqueta;
  contraste ≥ 4,83:1 nos 10 temas; 375 px sem rolagem lateral; alvos de 44–46 px.

## F0.11.09 — Receptor KOReader/Readest (2026-11-12)

- **Spec, plano e tarefas:** `specs/111-receptor-koreader-readest/`. Quarta feature do lote 2 do 0.11. **Migração
  `0038`** (tabela `receiver_tokens`: um token por leitor, só o SHA-256 e o começo), **não aplicada ao banco ativo**.
- **Token** (`services/receiver_tokens.py`): `lt_` + 32 bytes; `GET/POST/DELETE /api/account/receiver-token`;
  autenticação por `Authorization: Token …` (ou `Bearer`), recusa conta inativa, grava o último uso.
- **Readest** (`routers/receiver.py`): API compatível com o Readwise v2 em `/api/receptor/readwise/v2`: `GET auth/`
  (204) e `POST highlights/` (com e sem barra). `ereader_import/readwise.py` agrupa por título/autor e pula marcadores
  de página; `service.receive_parsed` escolhe o livro pela regra da F0.11.03 (ou cria) e grava na Mesa sem duplicar.
  Limites: 1000 destaques, 20 mil caracteres, 25 MB. `origin_guard` isenta só `/api/receptor/` (só token vale ali).
  Log só com contagens.
- **KOReader** (`ereader_import/koreader.py`): JSON do exportador (`version: "json/…"`, um livro ou `documents`),
  reconhecido por `detect_format`; a tela virou "Importar de leitor digital" e aceita `.json`.
- **Tela:** `components/settings/ReceiverTokenCard.vue` em Ajustes → Leitura (URL, token mostrado uma vez, gerar
  outro, revogar, instruções do Readest e do KOReader).
- **Testes:** `test_receiver.py` (5), `test_ereader_koreader.py` (4), `test_migration_0038.py` (1),
  `feature-111-receptor.test.mjs` (2); o teste da F0.11.03 passou a esperar o rótulo novo do botão da Mesa. Vizinhos
  (170 no backend, 69 no frontend) e build ok. Navegador (dados fictícios): gerar token, envio no formato do Readest
  chegando à Mesa (livro existente e livro novo; marcador pulado), importação de JSON do KOReader; contraste ≥ 5,35:1
  nos 10 temas; 375 px sem rolagem lateral depois de encurtar o rótulo "Gerar outro".

## F0.11.10 — Recorte de foto na digitalização (2026-11-12) e fecho do lote 2 do 0.11

- **Spec, plano e tarefas:** `specs/112-recorte-foto-digitalizacao/`. Quinta feature do lote 2. **Sem migração** e
  sem mudança de API.
- **Geometria pura** (`utils/photoCrop.ts`): recorte em frações da imagem girada; alças, mover, limites (mínimo 10%),
  giro de 90° (o recorte acompanha), tamanho de saída com redução até 40 MP, transformação do `canvas`, descrição.
- **Composable** (`useDigitizeDraft`): fase `adjust`; `prepare(file)` abre a etapa, `read(file)` lê o recortado (ou o
  original), `discardAdjust()` volta; `choose(file)` continua lendo direto (testes da 086 intactos).
- **Tela** (`components/digitize/PhotoCropper.vue`): "Ajustar a foto" com máscara, 8 alças de 44 px (ponteiro e
  teclado; setas 1%, Shift 5%), giro, "Ler a página", "Usar a foto inteira", "Escolher outra foto"; EXIF por
  `createImageBitmap(..., { imageOrientation: 'from-image' })`; foto com menos de 300 px no lado menor é lida direto.
- **Testes:** `feature-112-recorte-foto.test.mjs` (5). Navegador (imagem fictícia gerada na página; servidor de
  validação com leitura falsa): arraste, teclado, giro, envio de 1230×1240 px conferido no servidor e com a orientação
  certa, "Usar a foto inteira" enviando a original; contraste ≥ 4,76:1 nos 10 temas; 375 px sem rolagem lateral.
  Achado e corrigido: a seta numa alça também movia o recorte inteiro (evento subindo); agora para na alça.
- **Fecho do lote 2 do 0.11 (F0.11.06 a .10):** `npm test` 796/796, `pytest` 854 aprovados e 4 pulados (banco
  descartável), build ok; nenhuma falha de feature anterior.

## F0.11.11 — Cadernos de síntese com transclusão (2026-11-14)

- **Spec, plano e tarefas:** `specs/113-cadernos-sintese/`. Primeira feature do lote 3 do 0.11 (último item do
  roadmap). **Migração `0039`** (tabela `synthesis_notebooks`, com `version` e `deleted_at`), **não aplicada ao banco
  ativo**.
- **Marcas** (cada uma sozinha na linha, fora de bloco de código): `![[Título|id]]` (estudo inteiro),
  `![[Título|id#resumo|explicacao|conceitos|referencias]]` (seção), `![[destaque:id]]`. Mesmo analisador no servidor
  (`services/synthesis_service.py`) e no navegador (`utils/synthesisEmbeds.ts`), com os mesmos casos nos testes.
- **API** (`routers/syntheses.py`): lista, lixeira própria (30 dias, limpeza ao listar), criar, ler, `PATCH` com
  versão (409), excluir/restaurar/excluir de vez, `GET /{id}/resolved` (resolve só conteúdo do próprio leitor e fora da
  lixeira; senão "Trecho indisponível", sem vazar nada; limite de 200 trechos), `GET /{id}/export` (Markdown com os
  trechos resolvidos em citação + origem, cercados de linhas em branco). O pacote da conta inclui `sinteses/`.
- **Tela:** `views/SynthesesView.vue` (`/sinteses`, com "Excluídos"), `views/SynthesisView.vue` (`/sinteses/:id`, ler e
  editar, aviso de alterações), `components/synthesis/EmbedBlock.vue` e `InsertEmbedDialog.vue` (`<dialog>`; o
  fechamento avisa o pai na hora). Menus "Sínteses" (barra, "Mais", usuário); rotas nos contratos 076/081 (linhas 30 e
  31).
- **Testes:** `test_synthesis.py` (3), `test_migration_0039.py` (1), `feature-113-sinteses.test.mjs` (3); vizinhos (78
  no backend, 112 no frontend) e build ok. Navegador (dados fictícios): criar, inserir 3 trechos pelo diálogo (na
  posição do cursor, em linha própria), marca no meio do parágrafo avisada, trecho atualizado depois de editar o
  estudo, origem na lixeira como indisponível, exportação, Excluídos; contraste ≥ 4,76:1 nos 10 temas; 375 e 1024 px sem
  rolagem lateral. Achados e corrigidos: diálogo que não reabria (dependia do evento nativo `close`) e exportação que
  colava a linha seguinte na citação.

## Fecho do Roadmap 0.11 (2026-11-14)

- Suítes completas depois da F0.11.11: `npm test` 799/799; `pytest` 857 aprovados, 4 pulados e **1 falha
  intermitente** de feature anterior (086, `test_client_disconnect_kills_engine_and_cleans`): a desconexão simulada
  pela contagem de chamadas chegava antes de o motor falso subir quando a máquina estava carregada (a suíte levou 20
  minutos, o dobro do normal). O produto estava certo; o teste passou a desconectar só depois que o motor gravou o
  rastro. Commit próprio `9a93645`; conferido 8 vezes seguidas; arquivo de digitalização inteiro 37/37 duas vezes.
- Roadmap 0.11 concluído: F0.11.01 a F0.11.11. Em 2026-11-14 o usuário migrou o banco ativo até a 0039 (snapshot
  validado em `D:\Leitorum\backups\`, a raiz de armazenamento) e reiniciou o serviço, que funciona. (Antes: sem as
  migrações 0034 a 0039, procedimento do
  HANDOFF, pelo usuário).
