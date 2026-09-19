# Tasks: Proteção do Acervo e Snapshot Consistente Pré-Atualização

**Feature Branch**: `001-snapshot-protecao-acervo` | **Date**: 2026-09-17 | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Preparação do ambiente de testes e estruturas básicas compartilhadas.

- [X] T001 Configurar estrutura de diretórios e contratos de ambiente em `backend/app/core/config.py`
- [X] T002 [P] Criar arquivo de testes isolados com fixtures `tmp_path` em `backend/tests/test_backup_pre_upgrade.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestrutura crítica e bloqueante que DEVE ser concluída antes de qualquer história de usuário.

- [X] T003 Implementar função de resolução do diretório de backups `get_backup_dir()` em `backend/app/core/config.py`
- [X] T004 [P] Validar estritamente obrigatoriedade de caminho absoluto em `get_database_path()` em `backend/app/core/config.py`
- [X] T005 Refatorar e modularizar a primitiva atômica de snapshot em `backend/app/services/backups.py`

**Checkpoint**: Fundação pronta — implementação das histórias de usuário desbloqueada.

---

## Phase 3: User Story 1 - Backup Consistente Automático Antes de Atualizações (Priority: P1) 🎯 MVP

**Goal**: Criar e validar atomicamente um snapshot em `backend/data/backups/caderno-pre-migracao-YYYYMMDD-HHMMSS.db` antes de qualquer migração, abortando a operação se a cópia falhar.

**Independent Test**: Executar uma migração com dados sintéticos em `tmp_path` e comprovar que o snapshot consistente é gerado e verificado antes de qualquer instrução DDL, mantendo a base intocada se o snapshot for bloqueado.

### Tests for User Story 1
> **Escrever os testes antes da implementação e garantir que falhem.**

- [X] T006 [P] [US1] Implementar teste de criação atômica e validação de snapshot pré-migração em `backend/tests/test_backup_pre_upgrade.py`
- [X] T007 [P] [US1] Implementar teste de aborto atômico de migração quando o snapshot falha em `backend/tests/test_backup_pre_upgrade.py`

### Implementation for User Story 1

- [X] T008 [US1] Implementar orquestração de snapshot pré-migração `ensure_pre_upgrade_snapshot()` em `backend/app/services/maintenance.py`
- [X] T009 [US1] Implementar política de rotação dos 5 snapshots pré-migração mais recentes em `backend/app/services/maintenance.py`
- [X] T010 [US1] Integrar barreira pré-migração de snapshot consistente no hook do Alembic em `backend/migrations/env.py`

**Checkpoint**: User Story 1 funcional e testável de forma 100% independente (MVP alcançado).

---

## Phase 4: User Story 2 - Resolução Determinística da Base Ativa (Priority: P2)

**Goal**: Garantir que o servidor, utilitários e migrações converjam sempre para o mesmo banco de dados, independentemente do diretório de trabalho do terminal.

**Independent Test**: Invocar a resolução do banco a partir de diretórios de trabalho distintos e com caminhos contendo acentos e espaços no Windows, comprovando convergência para o caminho canônico.

### Tests for User Story 2

- [X] T011 [P] [US2] Implementar teste de resolução canônica com caminhos contendo acentos e espaços em `backend/tests/test_backup_pre_upgrade.py`
- [X] T012 [P] [US2] Implementar teste de rejeição de caminho relativo em `CADERNO_DATABASE_PATH` em `backend/tests/test_backup_pre_upgrade.py`

### Implementation for User Story 2

- [X] T013 [US2] Alinhar resolução de caminho do banco na inicialização do servidor em `iniciar.py`

**Checkpoint**: User Stories 1 e 2 plenamente operacionais e integradas.

---

## Phase 5: User Story 3 - Inspeção e Diagnóstico de Integridade de Snapshots (Priority: P3)

**Goal**: Permitir inspecionar metadados, integridade física/referencial e contagens quantitativas de itens em snapshots sem exibir textos privados do acervo.

**Independent Test**: Inspecionar um snapshot contendo livros e estudos sintéticos e verificar que o relatório emite contagens corretas e status de integridade sem conter anotações ou textos.

### Tests for User Story 3

- [X] T014 [P] [US3] Implementar teste de inspeção de snapshot garantindo privacidade absoluta em `backend/tests/test_backup_pre_upgrade.py`

### Implementation for User Story 3

- [X] T015 [US3] Implementar função de diagnóstico e contagem agregada `inspect_snapshot()` em `backend/app/services/maintenance.py`
- [X] T016 [US3] Implementar utilitário CLI de verificação de snapshot em `backend/app/services/maintenance.py`

**Checkpoint**: Todas as três histórias de usuário implementadas e validadas.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verificação integrada, documentação e conformidade constitucional.

- [X] T017 Executar validação completa dos cenários de `specs/001-snapshot-protecao-acervo/quickstart.md`
- [X] T018 [P] Atualizar registros de evidências e histórico em `docs/contexto/RETOMADA.md`

---

## Dependencies & Execution Order

### Phase Dependencies

1. **Phase 1 (Setup)**: Pode iniciar imediatamente.
2. **Phase 2 (Foundational)**: Depende da Phase 1. Bloqueia todas as histórias de usuário.
3. **Phase 3 (User Story 1 - MVP)**: Depende da Phase 2. Entrega o valor central de proteção.
4. **Phase 4 (User Story 2)**: Depende da Phase 2. Pode ser executada sequencialmente após US1.
5. **Phase 5 (User Story 3)**: Depende das rotinas de manutenção criadas em US1.
6. **Phase 6 (Polish)**: Depende da conclusão de todas as histórias desejadas.

### Parallel Opportunities

- **Setup**: T001 e T002 podem ser desenvolvidos em paralelo.
- **Foundational**: T003 e T004 podem ser desenvolvidos em paralelo com T005.
- **US1 Tests**: T006 e T007 podem ser implementados em paralelo antes de T008.
- **US2 Tests**: T011 e T012 podem rodar em paralelo.

---

## Parallel Example: User Story 1

```powershell
# Escrever primeiro os testes de US1 em paralelo:
# T006: backend/tests/test_backup_pre_upgrade.py (teste de criação atômica)
# T007: backend/tests/test_backup_pre_upgrade.py (teste de falha e aborto)
```

---

## Implementation Strategy

### MVP First (User Story 1)
1. Executar Phase 1 (Setup) e Phase 2 (Foundational).
2. Executar Phase 3 (User Story 1 - Criação e validação do snapshot pré-migração + hook no Alembic).
3. **Validar MVP isoladamente:** comprovar que `alembic upgrade` não executa sem snapshot verificado.

### Incremental Delivery
- Incremento 1: Fundação + Proteção Pré-Migração (US1).
- Incremento 2: Resolução canônica de caminhos e tolerância Windows (US2).
- Incremento 3: Inspeção diagnóstica sem violação de privacidade (US3).
- Validação Final: Execução do roteiro de Quickstart e registro de conformidade.
