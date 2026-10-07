# Implementation Plan: F0.7.12 — Backlinks e Menções entre Estudos

**Branch**: `061-backlinks-mencoes-estudos` | **Date**: 2026-10-06 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/061-backlinks-mencoes-estudos/spec.md`

## Summary

Implementar suporte a referências contextuais cruzadas entre estudos utilizando sintaxe natural wiki `[[Título do Estudo]]` (e `[[Título|id]]` para desambiguação). O sistema inclui:
1. Autocomplete contextual no editor (`StudyEditorFields.vue`) com busca de estudos candidatos.
2. Extração síncrona de menções no backend e persistência relacional na tabela `study_mentions`.
3. Renderização de links internos no leitor (`MarkdownContent.vue`) com transição suave via router SPA.
4. Componente de rodapé (`StudyBacklinksList.vue`) em `StudyView.vue` listando estudos citadores ("Mencionado em...") com obra, capítulo e trecho da citação contextual.

## Technical Context

**Language/Version**: Python 3.13 (Backend), TypeScript 5+ / Vue 3 (Frontend)

**Primary Dependencies**: FastAPI, SQLAlchemy 2.0, Alembic, Vite, Vue Router 4, markdown-it, lucide-vue-next

**Storage**: SQLite (modo WAL, chaves estrangeiras ativas) com tabela `study_mentions`

**Testing**: Pytest no backend (`backend/tests/test_study_mentions.py`), Node Test Runner no frontend (`frontend/tests/study_mentions.test.mjs`)

**Target Platform**: Windows local (PowerShell, processo único local via `iniciar.py`) e visualização responsiva em navegadores modernos / mobile

**Project Type**: Web Application SPA (Frontend Vue 3 + Backend FastAPI)

**Performance Goals**: Extração de menções em < 5ms por salvamento; carregamento de backlinks em < 50ms; autocomplete responsivo em < 150ms

**Constraints**: Isolamento multiusuário estrito por `user_id`; integridade relacional quando estudos são movidos para a lixeira; zero emojis em código de frontend; alvos táteis móveis $\ge 44 \times 44$px

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Privacidade e Isolamento**: Sim. Consultas a `study_mentions` filtram estritamente por `user_id == current_user.id`. Dados de produção preservados.
- **Isolamento de Testes**: Sim. Testes utilizam bancos efêmeros descartáveis em `tmp_path`.
- **Fidelidade Arquitetural**: Sim. Respeita a convenção FastAPI + SQLAlchemy 2.0 + Alembic no backend e Vue 3 Composition API com `<script setup>` no frontend.
- **Convenção Git**: 1 Feature = 1 Commit ao concluir o ciclo completo.

## Project Structure

### Documentation (this feature)

```text
specs/061-backlinks-mencoes-estudos/
├── spec.md                  # Especificação refinada com esclarecimentos
├── plan.md                  # Este plano técnico de implementação
├── research.md              # Decisões arquiteturais e justificativas
├── data-model.md            # Entidades, esquemas Pydantic e tipos TypeScript
├── quickstart.md            # Guia de testes e validação ponta a ponta
├── contracts/
│   └── study-mentions-api.yaml # Contrato OpenAPI para backlinks e autocomplete
├── checklists/
│   └── requirements.md      # Validação de qualidade de especificação
└── tasks.md                 # Decomposição em tarefas atômicas (próxima etapa)
```

### Source Code

```text
caderno-leitura-0.1/
├── backend/
│   ├── migrations/versions/
│   │   └── 0026_add_study_mentions_table.py
│   ├── app/
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── study_mention.py
│   │   ├── schemas/
│   │   │   └── study_mention.py
│   │   ├── services/
│   │   │   └── study_mention_service.py
│   │   └── routers/
│   │       ├── studies.py (integração do trigger de sincronização de menções)
│   │       └── study_mentions.py (endpoints de backlinks e busca de candidatos)
│   └── tests/
│       └── test_study_mentions.py
└── frontend/
    ├── src/
    │   ├── types.ts (tipagem de BacklinkItem, BacklinksResponse, etc.)
    │   ├── services/
    │   │   └── api.ts (métodos getStudyBacklinks e searchStudyCandidates)
    │   ├── components/
    │   │   ├── MarkdownContent.vue (renderização de [[...]] e navegação SPA)
    │   │   ├── StudyEditorFields.vue (autocomplete de menções [[...)
    │   │   └── studies/
    │   │       └── StudyBacklinksList.vue (painel de rodapé com menções reversas)
    │   └── views/
    │       └── StudyView.vue (ancoragem do componente StudyBacklinksList)
    └── tests/
        └── study_mentions.test.mjs
```

## Implementation Phases

### Phase 0: Outline & Research
- Consolidação do padrão de sintaxe wiki `[[Título]]` e `[[Título|id]]`.
- Definição do parser e extração de contexto snippet.
- Concluído em `research.md`.

### Phase 1: Design & Contracts
- Modelo de dados relacional e migração Alembic documentados em `data-model.md`.
- Contrato da API documentado em `contracts/study-mentions-api.yaml`.
- Guia de validação documentado em `quickstart.md`.

### Phase 2: Execution (via `/speckit-tasks` e `/speckit-implement`)
- **Fase 1 (Setup)**: Migração `0026_add_study_mentions_table.py`, modelo `StudyMention`, tipagens frontend e esquemas Pydantic.
- **Fase 2 (Foundational)**: Serviço de extração/sincronização de menções, endpoints de API e cliente HTTP frontend.
- **Fase 3 (User Story 1 - P1)**: Autocomplete de menções no editor de estudo (`StudyEditorFields.vue`).
- **Fase 4 (User Story 2 - P2)**: Parser e renderização de links internos no leitor (`MarkdownContent.vue`) com navegação SPA.
- **Fase 5 (User Story 3 - P3)**: Painel de backlinks reversos (`StudyBacklinksList.vue`) em `StudyView.vue`.
- **Fase 6 (Polish)**: Mobile touch, ausência de emojis, testes unitários e de integração (`pytest`, `npm test`, `npm run build`).
