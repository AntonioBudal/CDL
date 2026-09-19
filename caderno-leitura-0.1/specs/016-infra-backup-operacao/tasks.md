# Tasks: Infraestrutura — Integridade, Migrações, Concorrência e Operação de Backup/Restauração (T09-T10)

**Feature**: `016-infra-backup-operacao`  
**Input**: Design artifacts from `specs/016-infra-backup-operacao/` (`spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`)  
**Status**: Completed  

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Estruturas de dados, contratos Pydantic e resolução de caminhos compartilhados para backup, restauração e concorrência.

- [X] T001 Criar schemas Pydantic de manifesto, contagens e resultado de restauração em `caderno-leitura-0.1/backend/app/schemas/backups.py`
- [X] T002 [P] Atualizar definições de tipos TypeScript para manifesto, resposta de restore e estado de conflito em `caderno-leitura-0.1/frontend/src/types.ts`
- [X] T003 [P] Padronizar resolução de diretórios de capas físicas e backups automáticos em `caderno-leitura-0.1/backend/app/core/config.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Primitivas criptográficas, validações de integridade física SQLite, defesa contra Zip Slip e snapshots de salvaguarda.

**⚠️ CRITICAL**: Nenhuma história de usuário pode ser finalizada sem a conclusão destas primitivas de segurança.

- [X] T004 Implementar cálculo de hash SHA-256 e montagem/leitura de `manifest.json` em `caderno-leitura-0.1/backend/app/services/backups.py`
- [X] T005 [P] Implementar verificador de integridade física e chaves estrangeiras (`PRAGMA quick_check` e `PRAGMA foreign_key_check`) para cópias SQLite em `caderno-leitura-0.1/backend/app/services/backups.py`
- [X] T006 [P] Implementar rotina estrita de sanitização e validação contra Zip Slip / Path Traversal em `caderno-leitura-0.1/backend/app/services/restore_service.py`
- [X] T007 Implementar criação obrigatória de snapshot pré-restauração (`caderno-pre-restauracao-*.db`) com retenção em `caderno-leitura-0.1/backend/app/services/maintenance.py`

**Checkpoint**: Primitivas de integridade e segurança prontas. As histórias de usuário podem ser executadas.

---

## Phase 3: User Story 1 - Geração de Pacote Completo de Backup com Integridade Verificável (Priority: P1) 🎯 MVP

**Goal**: Permitir ao usuário baixar um arquivo `.zip` contendo a base consistente (`caderno.db`), o diretório de capas físicas (`covers/`) e o manifesto criptográfico (`manifest.json`) com hashes SHA-256, tanto via Web quanto via CLI.

**Independent Test**: Executar `test_backup_bundle.py`, baixar o arquivo `.zip` e verificar que contém `caderno.db`, pasta `covers/` e `manifest.json` com hashes coincidentes e integridade SQLite válida.

### Tests for User Story 1
- [X] T008 [P] [US1] Criar testes automatizados isolados de empacotamento ZIP e manifesto em `caderno-leitura-0.1/backend/tests/test_backup_bundle.py`

### Implementation for User Story 1
- [X] T009 [US1] Implementar função `create_backup_bundle` para gerar pacote `.zip` completo com `caderno.db`, `covers/` e `manifest.json` em `caderno-leitura-0.1/backend/app/services/backups.py`
- [X] T010 [US1] Implementar endpoint `GET /api/backup/bundle` com streaming do arquivo ZIP e headers de download em `caderno-leitura-0.1/backend/app/routers/backups.py`
- [X] T011 [US1] Implementar subcomando CLI `criar-backup` com suporte a `--destino` e `--json` em `caderno-leitura-0.1/backend/app/services/maintenance.py`
- [X] T012 [P] [US1] Adicionar método `downloadBackupBundle` no cliente de API em `caderno-leitura-0.1/frontend/src/services/api.ts`
- [X] T013 [US1] Atualizar componente `DatabaseBackup.vue` para incluir botão de download do pacote completo `.zip` em `caderno-leitura-0.1/frontend/src/components/DatabaseBackup.vue`
- [X] T014 [US1] Criar testes unitários para acionamento e download do bundle ZIP no frontend em `caderno-leitura-0.1/frontend/tests/backup-restore.test.mjs`

**Checkpoint**: User Story 1 (MVP) 100% funcional e testável de forma independente.

---

## Phase 4: User Story 2 - Restauração Segura com Validação Prévia e Proteção de Rollback (Priority: P2)

**Goal**: Permitir a restauração de pacotes de backup (`.zip` ou `.db`) com validação prévia em sandbox temporária, snapshot compulsório do acervo ativo e reversão (rollback) automática caso ocorra erro.

**Independent Test**: Executar `test_restore_safety.py`, submetendo arquivos corrompidos e maliciosos (Zip Slip) e verificando a rejeição sem tocar no banco ativo; em seguida, restaurar arquivo íntegro e comprovar a substituição atômica com criação do snapshot prévio.

### Tests for User Story 2
- [X] T015 [P] [US2] Criar testes automatizados de sandbox, integridade, Zip Slip, snapshot de salvaguarda e rollback em `caderno-leitura-0.1/backend/tests/test_restore_safety.py`

### Implementation for User Story 2
- [X] T016 [US2] Implementar serviço de restauração atômica `restore_backup_package` com sandbox, checagem de hashes SHA-256, substituição física e rollback em `caderno-leitura-0.1/backend/app/services/restore_service.py`
- [X] T017 [US2] Implementar endpoint `POST /api/backup/restore` (multipart/form-data) com respostas estruturadas em `caderno-leitura-0.1/backend/app/routers/backups.py`
- [X] T018 [US2] Implementar subcomandos CLI `restaurar-backup` e `verificar-backup` com confirmação e flag `--forcar` em `caderno-leitura-0.1/backend/app/services/maintenance.py`
- [X] T019 [P] [US2] Adicionar método `restoreBackupPackage` no cliente de API em `caderno-leitura-0.1/frontend/src/services/api.ts`
- [X] T020 [US2] Criar componente modal acessível `RestoreModal.vue` com seletor de arquivo, alerta de substituição e status em `caderno-leitura-0.1/frontend/src/components/RestoreModal.vue`
- [X] T021 [US2] Integrar `RestoreModal` na aba Sistema de `caderno-leitura-0.1/frontend/src/views/SettingsView.vue` e no componente `DatabaseBackup.vue`
- [X] T022 [US2] Adicionar testes unitários para o fluxo de restauração assistida no frontend em `caderno-leitura-0.1/frontend/tests/backup-restore.test.mjs`

**Checkpoint**: User Stories 1 e 2 funcionais e integradas de forma resiliente.

---

## Phase 5: User Story 3 - Concorrência Otimista e Proteção contra Sobrescrita entre Dispositivos (Priority: P3)

**Goal**: Impedir a perda silenciosa de edições quando múltiplos dispositivos modificarem o mesmo registro simultaneamente, alertando o usuário e oferecendo opções explícitas de sobrescrita assistida ou recarregamento dos dados mais novos.

**Independent Test**: Executar `test_concurrency_409.py` e `concurrency-conflict.test.mjs`, simulando tentativa de gravação com timestamp desatualizado, verificando retorno HTTP 409, preservação dos dados digitados no formulário e fluxo de sobrescrita.

### Tests for User Story 3
- [X] T023 [P] [US3] Criar testes automatizados de detecção de concorrência e tolerância de skew de relógio em `caderno-leitura-0.1/backend/tests/test_concurrency_409.py`

### Implementation for User Story 3
- [X] T024 [US3] Refinar `check_optimistic_lock` em `caderno-leitura-0.1/backend/app/services/persistence.py` com mensagens claras e tolerância de 1 segundo de clock skew
- [X] T025 [US3] Atualizar composable `useStudyEdit.ts` para capturar HTTP 409, preservar integralmente o formulário e prover ações `overwrite` e `reload` em `caderno-leitura-0.1/frontend/src/composables/useStudyEdit.ts`
- [X] T026 [P] [US3] Criar componente modal `ConcurrencyConflictModal.vue` com opções "Sobrescrever com minhas alterações" e "Recarregar versão externa" em `caderno-leitura-0.1/frontend/src/components/ConcurrencyConflictModal.vue`
- [X] T027 [US3] Integrar `ConcurrencyConflictModal` no formulário de edição de estudos em `caderno-leitura-0.1/frontend/src/views/StudyEditView.vue`
- [X] T028 [US3] Criar testes unitários para o fluxo de resolução de conflito de concorrência no frontend em `caderno-leitura-0.1/frontend/tests/concurrency-conflict.test.mjs`

**Checkpoint**: Concorrência otimista implementada e testada de ponta a ponta com salvaguarda das anotações do leitor.

---

## Phase 6: User Story 4 - Resiliência Operacional, Inicialização e Prevenção de Conflitos de Porta (Priority: P4)

**Goal**: Garantir que o inicializador `iniciar.py` verifique a disponibilidade de porta e integridade de migrações antes de iniciar o Uvicorn, exibindo diagnósticos amigáveis no terminal sem tracebacks feios do Windows (`[WinError 10048]`).

**Independent Test**: Executar teste simulando porta 8000 ocupada e verificar que o inicializador emite diagnóstico amigável em português orientando o encerramento da outra janela ou uso de `--port`.

### Implementation for User Story 4
- [X] T029 [US4] Implementar verificação prévia de porta ocupada com socket probe e mensagem amigável no terminal em `caderno-leitura-0.1/iniciar.py`
- [X] T030 [US4] Capturar exceção `[WinError 10048]` / `EADDRINUSE` no bloco de chamada do Uvicorn como segunda linha de defesa em `caderno-leitura-0.1/iniciar.py`
- [X] T031 [P] [US4] Padronizar avisos de migrações pendentes e rotas detectadas em `caderno-leitura-0.1/iniciar.py`
- [X] T032 [US4] Criar teste automatizado isolado de detecção de porta ocupada em `caderno-leitura-0.1/backend/tests/test_server_startup.py`

**Checkpoint**: Todas as 4 histórias de usuário do roadmap T09-T10 completas e robustas.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Verificação completa de integridade, testes de regressão, compilação estrita e conformidade com a Constituição.

- [X] T033 Executar suíte completa de testes do backend com `pytest` garantindo 100% de aprovação e isolamento em `tmp_path`
- [X] T034 Executar suíte completa de testes do frontend com `node --test` garantindo 100% de aprovação
- [X] T035 Executar build de produção do frontend (`npm.cmd run build`) garantindo 0 erros de compilação Vite/TypeScript
- [X] T036 Validar os cenários de uso fim a fim descritos em `specs/016-infra-backup-operacao/quickstart.md`
