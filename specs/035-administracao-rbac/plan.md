# Implementation Plan: F08 — Administração e RBAC

**Branch**: `035-administracao-rbac` | **Date**: 2026-09-26 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/035-administracao-rbac/spec.md`

---

## Summary

Implementar governança administrativa e controle de acesso baseado em papéis (RBAC) com suporte a administradores (`admin`) e leitores convencionais (`user`). A solução provê:
1. Validação estrita no servidor via dependência FastAPI `require_admin` retornando `403 Forbidden` para não-administradores.
2. Painel Administrativo moderno no Vue 3 (`/admin`) com indicadores de topo, listagem tabular paginada com busca e filtros por status e papel.
3. Moderação atômica com suspensão temporária de contas e revogação imediata de todas as sessões ativas do usuário alvo.
4. Salvaguardas invioláveis contra auto-bloqueio e garantia de que o sistema nunca fique sem administradores ativos.
5. Utilitário CLI determinístico e seguro para provisionamento interativo ou promoção do administrador inicial.

---

## Technical Context

**Language/Version**: Python 3.13 (64-bit Windows) & TypeScript ~6.0 / Node.js >=24.0.0
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2, Uvicorn (Backend); Vue 3 (Composition API), Vite, Vue Router, Lucide Icons (Frontend).
**Storage**: SQLite local (modo WAL com `PRAGMA foreign_keys = ON`).
**Testing**: `pytest` (com bancos efêmeros `tmp_path`) no backend e `node --test` (`npm test`) no frontend.
**Target Platform**: Windows local (PowerShell, acessível via localhost e rede privada/Tailscale para dispositivos móveis).
**Project Type**: Aplicação Web cliente-servidor integrada (FastAPI + SPA Vue 3).
**Performance Goals**: Listagem e filtros administrativos em menos de 100ms para bases locais; revogação de sessões em menos de 50ms.
**Constraints**: Zero vazamento de e-mails em rotas de usuários comuns; zero emojis informais no código-fonte do frontend (`visual_system.test.mjs`); alvos de toque mínimos de 44x44px.
**Scale/Scope**: Gestão para servidor local/pessoal (1 a dezenas de usuários em rede privada), com suporte projetado para até 10.000 registros.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio Constitucional | Avaliação | Justificativa / Conformidade |
|---|---|---|
| **I. Proteção Absoluta do Acervo e Privacidade** | ✅ APROVADO | O painel exibe apenas contadores agregados (`studies_count`, `books_count`). Textos de estudos, fichamentos e anotações privadas continuam inacessíveis a administradores que não sejam os proprietários dos estudos. E-mails são confidenciais e restritos à visão do admin. |
| **II. Isolamento Estrito de Testes** | ✅ APROVADO | O banco de produção `backend/data/caderno.db` não é tocado. Todos os testes unitários e de integração utilizam instâncias SQLite descartáveis em `tmp_path`. |
| **III. Fidelidade Arquitetural** | ✅ APROVADO | Segue rigorosamente a stack FastAPI + SQLAlchemy 2.0 declarativo no backend e Vue 3 + TypeScript no frontend. Sem dependências externas de nuvem ou serviços proprietários. |
| **IV. Governança por Spec Kit (SDD)** | ✅ APROVADO | Sequência formal respeitada: `specify` → `clarify` → `plan` → `tasks` → `analyze` → `implement`. |
| **V. Resiliência Operacional e Migrações Seguras** | ✅ APROVADO | Todas as mutações realizam `commit_changes(session)` com durabilidade atômica garantida em SQLite WAL. |

---

## Project Structure

### Documentation (this feature)

```text
specs/035-administracao-rbac/
├── spec.md              # Especificação de requisitos e histórias de usuário
├── plan.md              # Este plano técnico de implementação
├── research.md          # Pesquisa técnica e decisões de arquitetura (Phase 0)
├── data-model.md        # Modelo de dados relacional e máquinas de estados (Phase 1)
├── quickstart.md        # Guia rápido com cenários de validação (Phase 1)
├── contracts/
│   └── admin-api.md     # Contratos de API REST dos endpoints administrativos (Phase 1)
├── checklists/
│   └── requirements.md  # Checklist de validação de qualidade dos requisitos
└── tasks.md             # Tarefas atômicas sequenciais (Phase 2 - speckit-tasks)
```

### Source Code (repository layout)

```text
caderno-leitura-0.1/
├── backend/
│   ├── app/
│   │   ├── dependencies.py          # Adição da dependência require_admin
│   │   ├── models/
│   │   │   └── user.py              # Constraints chk_user_role e chk_user_status
│   │   ├── routers/
│   │   │   └── admin.py             # Router com endpoints /api/admin/*
│   │   ├── schemas/
│   │   │   └── admin.py             # Schemas Pydantic AdminUserItem, AdminStatsSummary, etc.
│   │   ├── services/
│   │   │   ├── admin_service.py     # Lógica de negócio de listagem, suspensão, papéis e proteções
│   │   │   └── session_service.py   # Função revoke_user_all_sessions
│   │   └── main.py                  # Registro do admin router
│   ├── scripts/
│   │   └── create_admin.py          # Script CLI de provisionamento interativo de admin
│   └── tests/
│       └── test_admin_and_rbac.py   # Suíte hermética cobrindo US1 a US4
│
└── frontend/
    ├── src/
    │   ├── api/
    │   │   └── admin.ts             # Cliente de API adminApi
    │   ├── components/
    │   │   └── admin/
    │   │       ├── AdminUsersTable.vue    # Tabela com listagem, badges e ações
    │   │       └── AdminConfirmModal.vue  # Modal acessível de confirmação de moderação
    │   ├── router/
    │   │   └── index.ts             # Rota /admin com Navigation Guard
    │   ├── services/
    │   │   └── api.ts               # Métodos administrativos expostos no singleton api
    │   ├── types/
    │   │   └── admin.ts             # Tipos TypeScript para admin
    │   ├── views/
    │   │   └── AdminView.vue        # Visão principal do Painel Administrativo
    │   └── App.vue                  # Link de navegação "Administração" condicional ao papel admin
    └── tests/
        └── admin.test.mjs           # Suíte de testes de acessibilidade e contratos no frontend
```

---

## Phase 0: Outline & Research

Consolidado em [research.md](./research.md).
- Resolução de RBAC no FastAPI via `require_admin`.
- Suspensão com revogação atômica em `user_sessions`.
- Salvaguardas anti-lockout no rebaixamento/suspensão.
- Script CLI seguro com `getpass`.
- Layout do painel com alvos de 44px e sem emojis.

---

## Phase 1: Design & Contracts

- **Modelo de Dados**: Detalhado em [data-model.md](./data-model.md).
- **Contratos da API**: Especificados em [contracts/admin-api.md](./contracts/admin-api.md).
- **Guia de Validação**: Documentado em [quickstart.md](./quickstart.md).

---

## Constitution Check (Post-Design)

Todos os princípios permanecem 100% satisfeitos. Nenhuma violação detectada. O projeto está preparado para a geração de tarefas decompostas via `/speckit-tasks`.
