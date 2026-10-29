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
