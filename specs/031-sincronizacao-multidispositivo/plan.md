# Implementation Plan: Sincronização Multidispositivo (F04)

**Branch**: `031-sincronizacao-multidispositivo` | **Date**: 2026-09-22 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/031-sincronizacao-multidispositivo/spec.md`

---

## Summary

Implementar a arquitetura completa de sincronização multidispositivo (PC Desktop + Celular via Tailscale) e controle de concorrência com o backend local atuando como a única fonte da verdade. O sistema introduz:
1. Controle de concorrência otimista (OCC) em `studies`, `books` e `study_canvas_nodes` através de contador monotônico `version: int` e validação de `expected_version`, rejeitando escritas defasadas com `HTTP 409 Conflict`.
2. Diálogo modal acessível no frontend (`ConflictResolutionModal.vue`) para resolução transparente de conflitos (comparar lado a lado, adotar servidor ou sobrescrever com rascunho local), sem perda de texto digitado.
3. Feed incremental de alterações e exclusões (`GET /api/sync/changes?since=<timestamp>`) baseado em timestamps e soft-deletes (`deleted_at` tombstones).
4. Sincronização centralizada de preferências de leitura do usuário (`user_preferences`) e coordenadas 2D do Canvas, preservando zoom e pan da câmera como estado estritamente local por dispositivo.
5. Reconciliação reativa pós-reconexão e standby (`useSync.ts`) escutando eventos de conectividade e visibilidade, com indicador de status sem emojis.

---

## Technical Context

**Language/Version**: Python 3.13 / 3.14 (FastAPI, SQLAlchemy 2.0, Alembic), TypeScript 5.9 (Vue 3, Vite, Tailwind/CSS)  
**Primary Dependencies**: `fastapi`, `sqlalchemy`, `alembic`, `pydantic`, `lucide-vue-next`  
**Storage**: SQLite local em modo WAL (`backend/data/caderno.db`) com isolamento absoluto por `user_id`  
**Testing**: `pytest` (com bancos efêmeros SQLite via `tmp_path`), `npm test` (223+ testes) e `visual_system.test.mjs`  
**Target Platform**: Servidor local em processo único atendendo navegadores no PC e no celular via rede privada Tailscale  
**Project Type**: Web Application monorepo com `backend/` (FastAPI) e `frontend/` (Vue 3 SPA)  
**Performance Goals**: Endpoint de reconciliação (`/api/sync/changes`) responde em <100ms; detecção de concorrência atômica em <10ms; retomada após standby em <1s  
**Constraints**: Zero perda silenciosa de dados; ausência de emojis no frontend; testes nunca tocam banco de produção; sem dependências de serviços em nuvem externa  
**Scale/Scope**: Múltiplos dispositivos do mesmo leitor; acervos com milhares de notas e estudos organizados  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Artigo Constitucional | Requisito do Projeto | Status de Conformidade |
| :--- | :--- | :---: |
| **I. Proteção do Acervo** | Nunca permitir sobrescrita silenciosa nem perda de dados por concorrência. | **PASS** — OCC via `version` e `HTTP 409` previne atualizações cegas; rascunho local retido. |
| **II. Isolamento de Testes** | Testes usam bancos efêmeros e nunca conectam a `backend/data/caderno.db`. | **PASS** — Fixtures utilizam `tmp_path` e portas efêmeras. |
| **III. Fidelidade Tecnológica** | FastAPI + SQLAlchemy 2.0 + SQLite WAL + Vue 3 `<script setup>` + TypeScript estrito. | **PASS** — Modelos declarativos modernos, schemas Pydantic v2 e composables Vue 3. |
| **IV. Governança por Spec** | Ciclo formal de desenvolvimento Spec Kit (F04). | **PASS** — F04 executada passo a passo no fluxo oficial. |
| **V. Migração Segura** | Migração Alembic versionada e sem perda de dados existentes. | **PASS** — Migração `0014_add_sync_versioning_and_preferences.py` com valores default seguros. |

---

## Project Structure

### Documentation (this feature)

```text
specs/031-sincronizacao-multidispositivo/
├── plan.md              # Este plano de implementação
├── research.md          # Pesquisa técnica e decisões de arquitetura
├── data-model.md        # Diagramas ER, schemas Pydantic e tabela user_preferences
├── quickstart.md        # Procedimentos de teste e validação de ponta a ponta
├── checklists/
│   └── requirements.md  # Checklist de conformidade de requisitos
├── contracts/
│   ├── sync-api.yaml    # Especificação OpenAPI dos endpoints de sincronização
│   └── sync-flow.md     # Diagramas de sequência do ciclo de vida e concorrência
└── tasks.md             # Tarefas atômicas geradas pelo /speckit-tasks
```

### Source Code Impact

```text
caderno-leitura-0.1/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   ├── __init__.py                # Exporta UserPreference
│   │   │   ├── user_preference.py         # [NEW] Modelo ORM UserPreference
│   │   │   ├── study.py                   # Adiciona coluna version: int
│   │   │   ├── book.py                    # Adiciona coluna version: int
│   │   │   └── study_canvas_node.py       # Adiciona coluna version: int
│   │   ├── schemas/
│   │   │   ├── sync.py                    # [NEW] Schemas SyncChangesResponse, ConflictErrorResponse
│   │   │   ├── preferences.py             # [NEW] Schemas UserPreferenceRead, UserPreferenceUpdate
│   │   │   ├── study.py                   # Adiciona expected_version e version no StudyRead
│   │   │   └── book.py                    # Adiciona expected_version e version no BookRead
│   │   ├── services/
│   │   │   ├── sync_service.py            # [NEW] Lógica de agregação do feed de alterações e tombstones
│   │   │   └── preferences_service.py     # [NEW] Leitura e atualização de preferências do usuário
│   │   └── routers/
│   │       ├── sync.py                    # [NEW] Endpoint GET /api/sync/changes
│   │       ├── preferences.py             # [NEW] Endpoints GET e PUT /api/preferences
│   │       ├── studies.py                 # Validação OCC e emissão de HTTP 409
│   │       └── books.py                   # Validação OCC e emissão de HTTP 409
│   ├── migrations/versions/
│   │   └── 0014_add_sync_versioning_and_preferences.py  # [NEW] Migração Alembic
│   └── tests/
│       └── test_sync_and_concurrency.py   # [NEW] Suíte de testes herméticos de concorrência e sync
└── frontend/
    └── src/
        ├── api/
        │   ├── sync.ts                    # [NEW] Cliente HTTP para feed de sincronização
        │   └── preferences.ts             # [NEW] Cliente HTTP para preferências do usuário
        ├── composables/
        │   ├── useSync.ts                 # [NEW] Orquestrador reativo de eventos de rede, foco e polling
        │   └── usePreferences.ts          # Atualizado para sincronização bidirecional com backend
        ├── components/
        │   └── sync/
        │       ├── ConflictResolutionModal.vue  # [NEW] Diálogo acessível de resolução de 409
        │       └── SyncStatusBadge.vue          # [NEW] Indicador discreto sem emojis no rodapé/header
        └── views/
            └── StudyEditView.vue          # Interceptação de 409 com abertura do modal de resolução
```

---

## Complexity Tracking

Nenhuma violação constitucional. A arquitetura utiliza recursos nativos do FastAPI, SQLAlchemy 2 e SQLite WAL sem bibliotecas pesadas de terceiros ou complexidade desnecessária.
