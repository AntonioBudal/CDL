# Implementation Plan: Infraestrutura — Integridade, Migrações, Concorrência e Operação de Backup/Restauração (T09-T10)

**Branch**: `016-infra-backup-operacao` | **Date**: 2026-09-19 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/016-infra-backup-operacao/spec.md` (T09 e T10 do Roadmap 0.3) com clarificações homologadas (Q1: A, Q2: A, Q3: A).

---

## Summary

Implementar a camada unificada de robustez operacional e integridade para o Caderno de Leitura:
1. **Pacote Universal de Backup (.zip)**: Geração e download atômico via `GET /api/backup/bundle` e CLI contendo cópia consistente do banco SQLite (`caderno.db` via SQLite Online Backup API com `journal_mode=DELETE`), diretório de capas físicas (`covers/`) e manifesto de autenticidade criptográfica (`manifest.json`) com somas de verificação SHA-256 de todos os itens.
2. **Restauração Segura com Sandbox e Rollback**: Processo atômico de restauração disponível via Web UI (`POST /api/backup/restore` na aba Sistema da Central de Ajustes) e CLI (`python -m app.services.maintenance restaurar-backup`), com proteção rigorosa contra Zip Slip, validação em sandbox temporária isolada (`PRAGMA quick_check` e `PRAGMA foreign_key_check`), snapshot prévio compulsório de salvaguarda do acervo ativo (`caderno-pre-restauracao-*.db`) e rollback automático e transparente em caso de falha.
3. **Concorrência Otimista com Resolução Assistida (HTTP 409)**: Preservação total das edições do leitor no formulário ao detectar alteração simultânea entre dispositivos (ex.: PC e smartphone), exibindo alerta explicativo com opções explícitas de "Sobrescrever com minhas alterações" (forçando salvamento com renovação de `updated_at`) ou "Recarregar versão externa" (descartando dados locais).
4. **Resiliência de Inicialização e Operação**: Detecção proativa de porta ocupada em `iniciar.py` com diagnóstico amigável em português (sem traceback não tratado do Windows `[WinError 10048]`), verificação segura de migrações e contratos unificados de resolução de caminhos.

---

## Technical Context

**Language/Version**: Python 3.13 de 64 bits (FastAPI, SQLAlchemy 2.0, Alembic, Uvicorn) no backend; TypeScript 5.8+ (Strict mode), Vue 3 (Composition API, `<script setup>`), Vite 6+ no frontend.  
**Primary Dependencies**:
- Backend: FastAPI, SQLAlchemy, Alembic, `zipfile` (nativo), `hashlib` (nativo), `sqlite3` (nativo com SQLite Online Backup API), `tempfile` (nativo), `socket` (nativo).
- Frontend: Vue 3, Vue Router 4, Tailwind CSS / Vanilla CSS tokens.  
**Storage**: SQLite local em modo WAL (`backend/data/caderno.db`), diretório físico de capas (`backend/data/covers/`), snapshots automáticos em `backend/data/backups/`.  
**Testing**: `pytest` com bancos efêmeros em `tmp_path` no backend (`test_backup_bundle.py`, `test_restore_safety.py`, `test_concurrency.py`); `node --test` no frontend (`backup-restore.test.mjs`, `concurrency-conflict.test.mjs`).  
**Target Platform**: Windows local (host) com suporte a rede local / Tailscale para dispositivos móveis.  
**Project Type**: Web Application pessoal (FastAPI + SPA Vue 3) com processo único local via `iniciar.py` e utilitário CLI `maintenance.py`.  
**Performance Goals**:
- Geração de backup `.zip` em menos de 2 segundos para acervos típicos (dezenas de livros e centenas de anotações).
- Restauração validada e executada em menos de 5 segundos.
- Diagnóstico de porta ocupada em menos de 500ms sem travamento do console.  
**Constraints**:
- Privacidade absoluta: NUNCA expor textos do acervo ou dados privados em logs ou endpoints públicos.
- Prevenção total contra Zip Slip / Path Traversal em arquivos recebidos.
- Nenhuma operação de restauração toca no acervo ativo antes da validação completa na sandbox e da geração do snapshot de salvaguarda.
- Tolerância de 1 segundo para relógios com skew em concorrência otimista.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Princípio I (Proteção Absoluta do Acervo e Privacidade de Dados):** PASS. O acervo ativo nunca é inspecionado nem transmitido para fora do ambiente do usuário. A concorrência otimista impede perda silenciosa de dados entre PC e celular.
- **Princípio II (Isolamento Estrito de Testes e Operações Locais):** PASS. Todos os testes automatizados criam bases descartáveis em `tmp_path` e portas efêmeras, sem tocar em `backend/data/caderno.db`.
- **Princípio III (Fidelidade Arquitetural e Tecnológica):** PASS. Uso de Python 3.13, SQLite Online Backup API oficial, FastAPI, Vue 3 Composition API e `iniciar.py`.
- **Princípio IV (Governança por Especificação Delimitada - SDD):** PASS. O Roadmap 0.3 mantém T09 e T10 como NÃO INICIADAS até a conclusão de todo o ciclo de planejamento e implementação assistida.
- **Princípio V (Resiliência Operacional, Transações e Migrações Seguras):** PASS. Foco central desta feature: backup consistente antes de qualquer alteração de schema, atomicidade na restauração com validação de chaves estrangeiras e integridade física, e rollback garantido.

---

## Project Structure

### Documentation (this feature)

```text
specs/016-infra-backup-operacao/
├── spec.md                       # Especificação funcional com clarificações resolvidas
├── checklists/
│   └── requirements.md          # Checklist de qualidade de especificação (16/16 PASS)
├── plan.md                       # Este plano de implementação
├── research.md                   # Pesquisa técnica e decisões de arquitetura (Phase 0)
├── data-model.md                 # Modelos de dados e schemas de manifesto/restauração (Phase 1)
├── contracts/                    # Contratos de API e CLI (Phase 1)
│   ├── backup-api-contract.md    # Contrato REST: GET /api/backup/bundle, POST /api/backup/restore
│   └── maintenance-cli-contract.md # Contrato CLI: maintenance.py (criar, verificar, restaurar)
├── quickstart.md                 # Guia de validação automatizada e cenários fim a fim (Phase 1)
└── tasks.md                      # Decomposição em tarefas atômicas (Phase 2 - /speckit-tasks)
```

### Source Code (repository root)

```text
caderno-leitura-0.1/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   └── config.py                 # [MODIFY] Resolução padronizada de diretórios de capas e backups
│   │   ├── schemas/
│   │   │   └── backups.py                # [NEW/MODIFY] Schemas Pydantic para BackupManifest e RestoreResponse
│   │   ├── services/
│   │   │   ├── backups.py                # [MODIFY] Geração de pacote ZIP com covers, SQLite backup e manifest.json
│   │   │   ├── restore_service.py        # [NEW] Extração sandbox, Zip Slip check, integridade, snapshot e rollback
│   │   │   ├── maintenance.py            # [MODIFY] Subcomandos CLI: criar-backup, verificar-backup, restaurar-backup
│   │   │   └── persistence.py            # [MODIFY] Otimização da verificação de concorrência e tolerância de skew
│   │   └── routers/
│   │       ├── backups.py                # [MODIFY] Endpoints GET /backup/bundle e POST /backup/restore
│   │       └── studies.py                # [MODIFY] Verificação e retorno explícito de concorrência com DTO atualizado
│   └── tests/
│       ├── test_backup_bundle.py         # [NEW] Testes de criação e conteúdo do pacote ZIP
│       ├── test_restore_safety.py        # [NEW] Testes de sandbox, Zip Slip, integridade e rollback
│       └── test_concurrency_409.py       # [NEW] Testes de concorrência otimista e sobrescrita controlada
├── frontend/
│   ├── src/
│   │   ├── types.ts                      # [MODIFY] Tipos de manifest, resultado de restore e conflito de concorrência
│   │   ├── services/
│   │   │   └── api.ts                    # [MODIFY] Funções downloadBackupBundle e restoreBackupPackage
│   │   ├── composables/
│   │   │   └── useStudyEdit.ts           # [MODIFY] Suporte a estado de conflito 409 (sobrescrever vs recarregar)
│   │   ├── components/
│   │   │   ├── DatabaseBackup.vue        # [MODIFY] Botão de download do pacote ZIP (.zip) e seção de restauração
│   │   │   ├── RestoreModal.vue          # [NEW] Modal com upload de arquivo, confirmação e feedback de progresso
│   │   │   └── ConcurrencyConflictModal.vue # [NEW] Diálogo para resolver conflitos de edição 409
│   │   └── views/
│   │       ├── SettingsView.vue          # [MODIFY] Integração da restauração assistida na aba Sistema
│   │       └── StudyEditView.vue         # [MODIFY] Apresentação do diálogo de concorrência em caso de 409
│   └── tests/
│       ├── backup-restore.test.mjs       # [NEW] Testes de interface para fluxo de backup e restore
│       └── concurrency-conflict.test.mjs # [NEW] Testes de resolução de concorrência no composable
└── iniciar.py                            # [MODIFY] Detecção prévia de porta ocupada com mensagem amigável no Windows
```

**Structure Decision**: A funcionalidade reaproveita as fundações existentes em `backend/app/services/backups.py` e `maintenance.py`, expandindo-as para o pacote `.zip` completo, sandbox de restauração segura e comandos CLI. No frontend, adiciona componentes dedicados (`RestoreModal.vue` e `ConcurrencyConflictModal.vue`) para manter o código modular e acessível.

---

## Complexity Tracking

*Nenhuma violação constitucional ou complexidade anômala detectada. Sem dependências externas adicionais; o empacotamento utiliza bibliotecas da biblioteca padrão do Python (`zipfile`, `hashlib`, `tempfile`, `sqlite3`).*
