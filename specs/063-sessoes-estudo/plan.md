# Implementation Plan: F0.7.14 — Sessões Estruturadas de Estudo e Auditoria de Aprendizado

**Branch**: `063-sessoes-estudo` | **Date**: 2026-10-10 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/063-sessoes-estudo/spec.md`

## Summary

Implementar a infraestrutura de Sessões Estruturadas de Estudo e Auditoria de Aprendizado, transformando o modo de Active Recall em blocos delimitados de estudo com ritmo, foco sensorial, início, meio e fim definidos. A solução engloba:
1. Persistência relacional em duas novas tabelas (`study_sessions` e `study_session_items`) via migração Alembic `0028_add_study_sessions_tables.py`.
2. Router backend `backend/app/routers/study_sessions.py` com endpoints REST para inicialização com escopo dinâmico (`/start`), registro atômico de item (`/{id}/items`), finalização com métricas (`/{id}/complete`), interrupção segura (`/{id}/interrupt`) e histórico retrospectivo (`/history`).
3. View imersiva dedicada `StudySessionView.vue` em modo tela limpa sem barras laterais de navegação, com barra de progresso horizontal (`SessionProgressHeader.vue`), atalhos de teclado e toque (`1`/`2`/`3` e `Espaço`).
4. Painel solene e triunfante de conclusão de sessão (`SessionSummaryModal.vue`) com cálculo de retenção, tempo de dedicação e próximas revisões agendadas.
5. Composable `useActiveReadingSession.ts` gerenciando o ciclo de vida reativo e a proteção contra saída involuntária.
6. Aba de Histórico de Sessões na Central de Revisão para auditoria da constância de leitura e aprendizado.

## Technical Context

**Language/Version**: Python 3.13 (Backend), TypeScript 5+ / Vue 3 (Frontend)

**Primary Dependencies**: FastAPI, SQLAlchemy 2.0, Alembic, Vite, Vue Router 4, lucide-vue-next

**Storage**: SQLite (modo WAL, chaves estrangeiras ativas) com tabelas `study_sessions` e `study_session_items`

**Testing**: Pytest no backend (`backend/tests/test_study_sessions.py`), Node Test Runner no frontend (`frontend/tests/study_sessions.test.mjs`)

**Target Platform**: Windows local (PowerShell, processo único local via `iniciar.py`) e visualização responsiva em navegadores modernos / dispositivos móveis

**Project Type**: Web Application SPA (Frontend Vue 3 + Backend FastAPI)

**Performance Goals**: Inicialização da sessão em < 50ms; transição entre cartões de estudo em < 100ms; registro atômico de resposta em < 30ms sem travamento de interface

**Constraints**: Isolamento multiusuário estrito por `user_id`; integridade relacional com `study_highlights`; ausência total de emojis no frontend; alvos táteis mínimos $\ge 44 \times 44$px

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Privacidade e Isolamento**: Sim. Consultas a `study_sessions` filtram estritamente por `user_id == current_user.id`. Nenhuma operação expõe dados privados ou afeta o banco ativo sem solicitação.
- **Isolamento de Testes**: Sim. Todas as validações automatizadas utilizam bancos efêmeros descartáveis em `tmp_path`.
- **Fidelidade Arquitetural**: Sim. Respeita a convenção FastAPI + SQLAlchemy 2.0 + Alembic no backend e Vue 3 Composition API com `<script setup>` e TypeScript estrito no frontend.
- **Convenção Git**: 1 Feature = 1 Commit ao concluir o ciclo completo com mensagens descritivas simples em português.

## Project Structure

### Documentation (this feature)

```text
specs/063-sessoes-estudo/
├── spec.md                  # Especificação funcional com decisões validadas
├── plan.md                  # Este plano técnico de implementação
├── research.md              # Decisões arquiteturais e justificativas
├── data-model.md            # Entidades, esquemas Pydantic e tipos TypeScript
├── quickstart.md            # Guia de testes e validação ponta a ponta
├── contracts/
│   └── study-sessions-api.yaml # Contrato OpenAPI para rotas de sessões
├── checklists/
│   └── requirements.md      # Checklist de validação de qualidade dos requisitos
└── tasks.md                 # Decomposição em tarefas atômicas (próxima etapa)
```

### Source Code

```text
caderno-leitura-0.1/
├── backend/
│   ├── migrations/versions/
│   │   └── 0028_add_study_sessions_tables.py
│   ├── app/
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── study_session.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── study_session.py
│   │   ├── services/
│   │   │   └── study_session_service.py
│   │   └── routers/
│   │       └── study_sessions.py
│   └── tests/
│       └── test_study_sessions.py
└── frontend/
    ├── src/
    │   ├── types.ts (adiciona tipos de StudySession, StudySessionItem, etc.)
    │   ├── services/
    │   │   └── api.ts (adiciona métodos de api de sessões de estudo)
    │   ├── composables/
    │   │   └── useActiveReadingSession.ts (gerenciamento reativo da sessão)
    │   ├── components/
    │   │   └── session/
    │   │       ├── SessionProgressHeader.vue (cabeçalho minimalista com progresso e cronômetro)
    │   │       └── SessionSummaryModal.vue (painel de conclusão triunfante)
    │   ├── views/
    │   │   ├── StudySessionView.vue (ambiente imersivo em tela limpa)
    │   │   └── ReviewHubView.vue (integração de gatilho para iniciar sessão e aba de histórico)
    │   └── router/
    │       └── index.ts (registro da rota /estudo/sessao/:sessionId)
```

## Complexity Tracking

> Sem violações constitucionais identificadas.
