# Implementation Plan: F 0.7.10 — Central de Revisão de Perguntas e Clozes

**Branch**: `059-central-de-revisao` | **Date**: 2026-10-04 | **Spec**: [specs/059-central-de-revisao/spec.md](spec.md)

**Input**: Feature specification from `specs/059-central-de-revisao/spec.md`

---

## Summary

Implementar a **Central de Revisão de Perguntas e Clozes** (`/review`) no Leitorum para permitir a prática deliberada de Active Recall consolidada de todo o acervo ou filtrada por livro/capítulo:
1. Adicionar colunas de auditoria leve (`last_reviewed_at`, `review_count`, `last_rating`) e índice relacional em `study_highlights` via migração Alembic `0024_add_review_metadata_to_highlights.py`.
2. Desenvolver endpoints backend em `app/routers/review.py` e serviço de agregação em `app/services/review_service.py` com heurística de priorização inteligente simples (itens nunca revisados primeiro, seguidos pelos mais antigos e difíceis).
3. Construir a experiência no frontend com composable `useReviewSession.ts`, tela de hub `ReviewHubView.vue`, card interativo `ReviewCard.vue` e cabeçalho `ReviewStatsHeader.vue`, suportando atalhos rápidos de teclado (`Espaço`, `1`, `2`, `3`) e alvos táteis mínimos de $44 \times 44$px no mobile.

---

## Technical Context

**Language/Version**: Python 3.13 (FastAPI, SQLAlchemy 2.0, Pydantic v2), TypeScript 5.6+, Vue 3.5+ (Composition API).  
**Primary Dependencies**: FastAPI, SQLAlchemy 2, Alembic, Vue 3, Vue Router, `lucide-vue-next` (via `Icon.vue`).  
**Storage**: SQLite local (modo WAL), tabela `study_highlights` estendida com novas colunas e índice composto `ix_study_highlights_review`.  
**Testing**: `pytest` com banco SQLite descartável em `tmp_path` (backend); `node:test` + `node:assert/strict` (frontend); `vue-tsc -b && vite build` (tipagem estrita).  
**Target Platform**: Desktop (Windows/Linux/Mac) e Mobile/Touch (iOS/Android/Tailscale).  
**Project Type**: Web Application SPA local (FastAPI + Vue 3).  
**Performance Goals**: Tempo de carregamento do hub < 100ms; revelação e transição entre cards < 16ms (60fps); latência de registro de avaliação < 20ms.  
**Constraints**: Zero impacto no banco de dados ativo de produção (`caderno.db`) durante testes; migração Alembic puramente aditiva e reversível; exclusão automática de estudos na lixeira (`deleted_at IS NOT NULL`); conformidade WAI-ARIA com anúncio via `aria-live`.  
**Scale/Scope**: 1 nova migração Alembic, 1 novo router FastAPI, 1 novo serviço backend, 1 nova view Vue (`ReviewHubView.vue`), 3 novos componentes Vue e 1 novo composable.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio Constitucional | Status | Justificativa / Verificação |
|---|:---:|---|
| **I. Proteção do Acervo e Privacidade** | **PASS** | O acervo é estritamente privado; testes utilizam dados sintéticos. Consultas são escopadas unicamente pelo `user_id` autenticado. |
| **II. Isolamento de Testes e Operações** | **PASS** | Zero impacto no banco de dados ativo `backend/data/caderno.db`. Todas as suítes utilizam bancos efêmeros descartáveis em `tmp_path`. |
| **III. Fidelidade Arquitetural** | **PASS** | Respeito à stack declarativa: FastAPI, SQLAlchemy 2, Alembic, Vue 3 (`<script setup>`), TypeScript estrito e SQLite local em processo único. |
| **IV. Governança por Spec Kit** | **PASS** | Ciclo formal com especificação, esclarecimento, plano técnico e contratos antes de qualquer implementação. |
| **V. Resiliência Operacional e Migrações Seguras** | **PASS** | Migração Alembic estritamente incremental e segura (`ADD COLUMN` com valores nulos ou padrão padrão), com backup prévio verificado. |

---

## Project Structure

### Documentation (this feature)

```text
specs/059-central-de-revisao/
├── plan.md              # Este plano de implementação
├── research.md          # Decisões técnicas consolidadas (D1 a D5)
├── data-model.md        # Modelo de dados e máquina de estados
├── quickstart.md        # 5 cenários práticos de teste fim a fim
├── contracts/           # Contratos de API REST e componentes Vue
│   └── review-contracts.md
└── tasks.md             # Tarefas geradas pelo /speckit-tasks
```

### Source Code (repository layout)

```text
caderno-leitura-0.1/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   └── study_highlight.py              # Colunas last_reviewed_at, review_count, last_rating e índice
│   │   ├── schemas/
│   │   │   └── review.py                       # Schemas ReviewItemRead, ReviewRecordRequest, ReviewStatsResponse
│   │   ├── services/
│   │   │   └── review_service.py               # Agregação estatística, fila priorizada e persistência
│   │   └── routers/
│   │       └── review.py                       # Endpoints /api/review/stats, /api/review/items, /items/{id}/record
│   ├── migrations/versions/
│   │   └── 0024_add_review_metadata_to_highlights.py # Migração Alembic incremental
│   └── tests/
│       └── test_review_hub.py                  # Testes de integração de API e serviços de revisão
└── frontend/
    ├── src/
    │   ├── types.ts                            # Tipagem TypeScript para ReviewItem, ReviewStats, ReviewRating
    │   ├── api/
    │   │   └── review.ts                       # Gateway HTTP para /api/review
    │   ├── composables/
    │   │   └── useReviewSession.ts             # Gerenciamento de ciclo de vida e estado da sessão
    │   ├── components/
    │   │   └── review/
    │   │       ├── ReviewCard.vue              # Card interativo de Active Recall (revelação e avaliação)
    │   │       ├── ReviewStatsHeader.vue       # Barra de progresso, estatísticas e filtros
    │   │       └── ReviewSummaryModal.vue      # Tela de encerramento da rodada com métricas de assimilação
    │   ├── views/
    │   │   └── ReviewHubView.vue               # Tela principal da Central de Revisão (/review)
    │   ├── router/
    │   │   └── index.ts                        # Registro da rota /review
    │   └── App.vue                             # Item de navegação "Revisão" na barra principal
    └── tests/
        ├── review-session.test.mjs             # Testes de unidade do composable useReviewSession
        ├── review-card.test.mjs                # Testes de renderização, atalhos de teclado e acessibilidade
        └── review-hub-view.test.mjs            # Testes da view de hub e transição de estados
```

**Structure Decision**: Aplicação SPA web em `frontend/` e serviço modular FastAPI em `backend/`. Reutilização total da infraestrutura de `study_highlights`.

---

## Complexity Tracking

> **Nenhuma violação constitucional.** Arquitetura limpa com migração incremental segura e sem dependências externas.
