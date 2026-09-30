# Implementation Plan: F0.6.6 — Apoie o Leitorum

**Branch**: `045-apoie-o-leitorum` | **Date**: 2026-09-29 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/045-apoie-o-leitorum/spec.md`

## Summary

Implementar a funcionalidade institucional "Apoie o Leitorum", permitindo que simpatizantes e leitores contribuam voluntariamente com a sustentabilidade do projeto através de PIX e links externos configuráveis (como Google Pay), sem intermediação financeira própria na aplicação. A experiência será discreta e elegante, acessível por link no rodapé e pela rota pública `/apoie`, com gestão administrativa no painel `/admin` integrada a fallback em variáveis de ambiente.

---

## Technical Context

**Language/Version**: Python 3.13 / 3.14 (Backend) e TypeScript / Vue 3 (Frontend)  
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2, Vue Router, Pinia, Lucide-Vue-Next  
**Storage**: SQLite local (modo WAL), tabela singleton `support_settings` gerenciada por migração Alembic  
**Testing**: `pytest` (backend em bancos temporários `tmp_path`) e `node --test` / Vitest (`npm test` no frontend)  
**Target Platform**: Windows local (PowerShell, Uvicorn processo único) e visualização responsiva Web/Mobile  
**Project Type**: Aplicação Web cliente-servidor monorepo local  
**Performance Goals**: Carregamento público de `/apoie` em menos de 100ms; cópia de chave PIX em 1 clique sem latência  
**Constraints**: Zero emojis em código/interface; isolamento total de dados pessoais; alvos de toque >= 44x44px; sem dependência de serviços externos embutidos para intermediação bancária  
**Scale/Scope**: 1 rota pública, 1 tabela singleton, 3 endpoints REST (`/api/support`, `/api/admin/support`), 1 view Vue (`SupportView.vue`), atualização do rodapé global e aba em `AdminView.vue`  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Artigo da Constituição | Conformidade | Justificativa / Evidência |
|---|---|---|
| **I. Proteção do Acervo e Privacidade** | **PASS** | A funcionalidade trata exclusivamente de parâmetros públicos de doação. Nenhuma informação do acervo do usuário (livros, estudos, anotações) é lida, modificada ou transmitida. |
| **II. Isolamento Estrito de Testes** | **PASS** | Todas as suítes de testes (`test_support_settings.py`) utilizam bancos efêmeros criados em diretórios temporários (`tmp_path`). O arquivo `caderno.db` não é acessado. |
| **III. Fidelidade Arquitetural** | **PASS** | Stack padrão mantida: FastAPI + SQLAlchemy 2.0 + Alembic + Vue 3 Composition API com TypeScript estrito. Sem adição de novas dependências pesadas de terceiros. |
| **IV. Governança por SDD** | **PASS** | Ciclo completo Spec Kit em execução: `speckit-specify` concluído com checklist 100% aprovado; `speckit-plan` gerando `research.md`, `data-model.md`, `contracts/` e `quickstart.md`. |
| **V. Resiliência Operacional e Migrações** | **PASS** | Migração Alembic `0022_add_support_settings.py` sequenciada estritamente após `0021_add_study_versions`. Não toca o banco ativo sem comando explícito e backup prévio. |

---

## Project Structure

### Documentation (this feature)

```text
specs/045-apoie-o-leitorum/
├── spec.md              # Especificação refinada com decisões de produto
├── checklists/
│   └── requirements.md  # Checklist de qualidade (16/16 aprovados)
├── plan.md              # Este plano de implementação
├── research.md          # Decisões técnicas e arquiteturais (Phase 0)
├── data-model.md        # Modelo relacional e schemas Pydantic (Phase 1)
├── contracts/
│   └── support-api.md   # Contratos de API pública e administrativa (Phase 1)
└── quickstart.md        # Cenários de validação e testes automatizados (Phase 1)
```

### Source Code (repository root)

```text
caderno-leitura-0.1/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   ├── support_setting.py       # Modelo SQLAlchemy da tabela singleton
│   │   │   └── __init__.py              # Registro no Base do SQLAlchemy
│   │   ├── schemas/
│   │   │   └── support_setting.py       # Schemas Pydantic (Public/Admin/Update)
│   │   ├── services/
│   │   │   └── support_service.py       # Lógica de fallback banco/env e auditoria
│   │   ├── routers/
│   │   │   ├── support.py               # Endpoint público GET /api/support
│   │   │   └── admin.py                 # Extensão com GET/PUT /api/admin/support
│   │   └── main.py                      # Registro do novo roteador
│   ├── migrations/
│   │   └── versions/
│   │       └── 0022_add_support_settings.py  # Migração Alembic
│   └── tests/
│       └── test_support_settings.py     # Testes automatizados herméticos
└── frontend/
    └── src/
        ├── types.ts                     # Interfaces TypeScript para suporte/apoio
        ├── services/
        │   └── api.ts                   # Métodos de cliente HTTP para apoio
        ├── views/
        │   ├── SupportView.vue          # Nova view pública /apoie
        │   └── AdminView.vue            # Aba de configuração de apoio
        ├── router/
        │   └── index.ts                 # Registro das rotas /apoie e /apoiar
        ├── components/
        │   └── navigation/
        │       └── MobileMoreMenu.vue   # Link de apoio no menu móvel
        └── App.vue                      # Link discreto no rodapé global
```

---

## Phases & Implementation Strategy

### Phase 0: Outline & Research
- Consolidação de decisões arquiteturais em [`research.md`](research.md).
- Resolução de todas as dúvidas de produto: rota canônica `/apoie`, suporte híbrido de configuração (admin + env) e mensagem comunitária de fallback quando nenhum meio financeiro estiver ativo.

### Phase 1: Design & Contracts
- Modelagem de dados e schemas em [`data-model.md`](data-model.md).
- Especificação dos contratos REST em [`contracts/support-api.md`](contracts/support-api.md).
- Roteiro de validação end-to-end em [`quickstart.md`](quickstart.md).

### Phase 2: Implementation (após `/speckit-tasks` e autorização)
1. **Setup & Infraestrutura**: Tipos TypeScript e schemas Pydantic.
2. **Foundational**: Modelo `SupportSetting`, migração Alembic `0022` e serviço `support_service`.
3. **User Story 1 (P1 - MVP)**: View `SupportView.vue`, endpoint `GET /api/support` e botão de cópia de chave PIX com feedback e alvos táteis de 44px.
4. **User Story 2 (P2)**: Links institucionais discretos em `App.vue` (`app-footer`) e `MobileMoreMenu.vue`.
5. **User Story 3 (P3)**: Aba de configuração em `AdminView.vue`, endpoints administrativos `GET/PUT /api/admin/support` e auditoria em `audit_logs`.
6. **Polish**: Verificação estrita de ausência de emojis, auditoria de acessibilidade por teclado e execução de 100% das suítes de teste (`npm test`, `npm run build`, `pytest`).
