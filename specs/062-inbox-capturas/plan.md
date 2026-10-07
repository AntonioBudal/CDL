# Implementation Plan: F0.7.13 — Caixa de Entrada de Capturas (Inbox de Conhecimento)

**Branch**: `062-inbox-capturas` | **Date**: 2026-10-10 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/062-inbox-capturas/spec.md`

## Summary

Implementar a Caixa de Entrada de Capturas Rápidas (Inbox de Conhecimento), viabilizando o registro instantâneo e descompromissado de ideias soltas, citações e trechos provisórios antes da formalização analítica em estudos completos. A solução contempla:
1. Modal global de captura rápida (`QuickCaptureModal.vue`) acionável via atalho universal `Ctrl+Shift+C` e botão de topo no layout `App.vue`.
2. Persistência em tabela relacional `inbox_captures` gerenciada pela migração Alembic `0027_add_inbox_captures_table.py`.
3. Router backend `backend/app/routers/inbox.py` com endpoints REST para CRUD, contagem reativa leve (`/count`), promoção (`/promote`) e vinculação (`/link`).
4. Central de Inbox (`InboxView.vue`) com cartões individuais (`CaptureItemCard.vue`), busca textual rápida, filtros por status e triagem em lote.
5. Fluxo de promoção com 1 clique para o editor de estudos e modal de vinculação a estudos existentes anexando notas contextuais.
6. Contador reativo de pendências no menu lateral com composable `useInboxCount`.

## Technical Context

**Language/Version**: Python 3.13 (Backend), TypeScript 5+ / Vue 3 (Frontend)

**Primary Dependencies**: FastAPI, SQLAlchemy 2.0, Alembic, Vite, Vue Router 4, lucide-vue-next

**Storage**: SQLite (modo WAL, chaves estrangeiras ativas) com tabela `inbox_captures`

**Testing**: Pytest no backend (`backend/tests/test_inbox.py`), Vitest / Node Test Runner no frontend (`frontend/tests/inbox.test.mjs`)

**Target Platform**: Windows local (PowerShell, processo único local via `iniciar.py`) e visualização responsiva em navegadores modernos / mobile

**Project Type**: Web Application SPA (Frontend Vue 3 + Backend FastAPI)

**Performance Goals**: Submissão de captura rápida em < 50ms; endpoint de contagem de pendências `GET /api/inbox/count` em < 20ms; triagem no Inbox instantânea sem recarregamento de página

**Constraints**: Isolamento multiusuário estrito por `user_id`; integridade relacional ao promover ou vincular a estudos; zero emojis em código de frontend; alvos táteis móveis $\ge 44 \times 44$px

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Privacidade e Isolamento**: Sim. Consultas a `inbox_captures` filtram estritamente por `user_id == current_user.id`. Nenhuma operação expõe dados privados ou afeta dados de produção.
- **Isolamento de Testes**: Sim. Testes utilizam bancos efêmeros descartáveis em `tmp_path`.
- **Fidelidade Arquitetural**: Sim. Respeita a convenção FastAPI + SQLAlchemy 2.0 + Alembic no backend e Vue 3 Composition API com `<script setup>` e TypeScript estrito no frontend.
- **Convenção Git**: 1 Feature = 1 Commit ao concluir o ciclo completo com mensagens descritivas simples em português.

## Project Structure

### Documentation (this feature)

```text
specs/062-inbox-capturas/
├── spec.md                  # Especificação funcional com decisões validadas
├── plan.md                  # Este plano técnico de implementação
├── research.md              # Decisões arquiteturais e justificativas
├── data-model.md            # Entidades, esquemas Pydantic e tipos TypeScript
├── quickstart.md            # Guia de testes e validação ponta a ponta
├── contracts/
│   └── inbox-api.yaml       # Contrato OpenAPI para rotas do Inbox
├── checklists/
│   └── requirements.md      # Checklist de validação de qualidade dos requisitos
└── tasks.md                 # Decomposição em tarefas atômicas (próxima etapa)
```

### Source Code

```text
caderno-leitura-0.1/
├── backend/
│   ├── migrations/versions/
│   │   └── 0027_add_inbox_captures_table.py
│   ├── app/
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── inbox_capture.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── inbox_capture.py
│   │   ├── services/
│   │   │   └── inbox_service.py
│   │   └── routers/
│   │       └── inbox.py
│   └── tests/
│       └── test_inbox.py
└── frontend/
    ├── src/
    │   ├── types.ts (adiciona tipos de InboxCapture, etc.)
    │   ├── services/
    │   │   └── api.ts (adiciona métodos de api do inbox)
    │   ├── composables/
    │   │   ├── useQuickCapture.ts (estado e controle global do modal de captura)
    │   │   └── useInboxCount.ts (contador reativo do badge do menu)
    │   ├── components/
    │   │   └── inbox/
    │   │       ├── QuickCaptureModal.vue (modal global com atalho Ctrl+Shift+C)
    │   │       ├── CaptureItemCard.vue (cartão de exibição e triagem de captura)
    │   │       └── LinkToStudyModal.vue (seletor de estudo existente para vinculação)
    │   ├── views/
    │   │   ├── InboxView.vue (tela principal da Caixa de Entrada)
    │   │   └── StudyEditView.vue (suporte a pré-preenchimento via query/state de promoção)
    │   ├── router/
    │   │   └── index.ts (registro da rota /inbox)
    │   └── App.vue (montagem do QuickCaptureModal, botão rápido no header e badge no menu)
    └── tests/
        └── inbox.test.mjs
```

## Implementation Phases

### Phase 0: Outline & Research
- Consolidação do ciclo de vida dos estados (`inbox`, `promoted`, `linked`, `archived`).
- Decisão sobre integração global sem bloqueio de tela com composable `useQuickCapture`.
- Definição do fluxo de promoção via pré-preenchimento e callback seguro para evitar estudos fantasmas.
- Mecânica de vinculação por injeção textual estruturada na seção `references`.
- Índice composto `(user_id, status)` para consulta de badge com tempo < 5ms.

### Phase 1: Design & Contracts
- Modelo de dados relacional e migração Alembic `0027_add_inbox_captures_table.py`.
- Esquemas Pydantic v2 com validações de texto não-vazio e tipagem TypeScript rigorosa.
- Contrato OpenAPI 3.1 em `contracts/inbox-api.yaml`.
- Guia de validação ponta a ponta em `quickstart.md`.
- Verificação da Constituição do Projeto: Aprovado.
