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
