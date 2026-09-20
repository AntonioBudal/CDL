# Implementation Plan: Fundação Multiusuário e CRUD Geral (F01)

**Branch**: `028-fundacao-multiusuario` | **Date**: 2026-09-20 | **Spec**: [spec.md](spec.md)  

**Input**: Feature specification from `specs/028-fundacao-multiusuario/spec.md`

---

## Summary

Implementar a fundação multiusuário do Caderno de Leitura, transformando todas as entidades de conteúdo em recursos formalmente associados a um proprietário (`user_id`). A entrega inclui a migração sem perdas do acervo legado para uma conta canônica soberana (`username: "proprietario"`), injeção de contexto de usuário via dependência do FastAPI com fallback retrocompatível, isolamento estrito de consultas em todas as rotas de CRUD e blindagem anti-enumeração (IDOR) padronizada em `HTTP 404 Not Found`.

---

## Technical Context

**Language/Version**: Python 3.13 (64-bit) no Windows; TypeScript / Node.js 24 no frontend.  
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0 (Mapped Columns declarativos), Alembic, Pydantic v2, Uvicorn.  
**Storage**: SQLite 3 local em modo Write-Ahead Logging (WAL) com chaves estrangeiras ativas (`PRAGMA foreign_keys = ON`).  
**Testing**: `pytest` com fixture `tmp_path` e isolamento total para o backend; `node --test` para o frontend.  
**Target Platform**: Windows local (processo único `iniciar.py` atendendo PC e dispositivos móveis via rede/Tailscale).  
**Project Type**: Web Application com API REST local (`/api`) e interface SPA em Vue 3.  
**Performance Goals**: Tempo de resolução de identidade e filtragem de escopo de usuário inferior a 15ms em consultas locais.  
**Constraints**: Zero perda de dados na migração do acervo existente; zero vazamento de dados entre usuários distintos; proteção estrita contra enumeração direta de objetos (IDOR).  
**Scale/Scope**: Multiusuário local sustentando coexistência de perfis e dados no mesmo ambiente.  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Art. I — Proteção do Acervo e Privacidade:** Migração sem perdas (`server_default` associando dados ao proprietário inicial). Textos reais e anotações nunca são expostos ou transmitidos.
- [x] **Art. II — Isolamento Estrito de Testes:** Todas as novas suítes de teste de isolamento (`test_multiuser_migration.py`, `test_multiuser_isolation.py`) utilizam bancos temporários em `tmp_path`. O banco ativo (`backend/data/caderno.db`) não é tocado.
- [x] **Art. III — Fidelidade Tecnológica:** FastAPI + SQLAlchemy 2.0 + Alembic (`batch_alter_table` para SQLite) e tipagem estrita.
- [x] **Art. IV — Governança por Especificação Delimitada:** Escopo focado estritamente na Feature 01 (Fundação e CRUD Geral), sem antecipar telas sociais ou formulários de autenticação de F02/F03.
- [x] **Art. V — Resiliência Operacional e Migrações Seguras:** Migração incremental atômica testada em bancos descartáveis antes de aplicação em produção.

---

## Project Structure

### Documentation (this feature)

```text
specs/028-fundacao-multiusuario/
├── spec.md              # Especificação de requisitos e critérios de aceite
├── plan.md              # Este plano de implementação técnica
├── research.md          # Pesquisa técnica e decisões de arquitetura
├── data-model.md        # Modelo de dados e especificação de entidades
├── quickstart.md        # Guia de validação e cenários de teste executáveis
├── contracts/           # Contratos de interface e segurança da API
│   ├── auth-context.md  # Contrato de resolução do usuário ativo
│   └── crud-isolation.md# Contrato de isolamento e regras de CRUD
├── checklists/          # Checklists de qualidade
│   └── requirements.md  # Checklist de validação da especificação
└── tasks.md             # Tarefas atômicas de implementação (gerado em /speckit-tasks)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── core/
│   │   ├── auth.py                  # [NEW] Utilitários de contexto e resolução de usuário
│   │   └── config.py                # Configurações de ambiente e identificadores canônicos
│   ├── dependencies.py              # Injeção de dependência CurrentUser com fallback
│   ├── models/
│   │   ├── user.py                  # [NEW] Modelo de dados User
│   │   ├── book.py                  # Adição de user_id e relacionamentos
│   │   ├── study.py                 # Adição de user_id e relacionamentos
│   │   ├── category.py              # Adição de user_id híbrido (nullable)
│   │   ├── study_relation.py        # Adição de user_id
│   │   ├── study_canvas_node.py     # Adição de user_id
│   │   ├── canvas_frame.py          # Adição de user_id
│   │   └── search_history.py        # Adição de user_id
│   ├── routers/
│   │   ├── auth.py                  # [NEW] Endpoint GET /api/auth/me
│   │   ├── books.py                 # Filtro por user_id e get_user_resource_or_404
│   │   ├── studies.py               # Filtro por user_id e validação de posse de capítulo
│   │   ├── chapters.py              # Validação de posse do livro vinculado
│   │   ├── categories.py            # Suporte ao modelo híbrido de categorias
│   │   ├── search.py                # Busca restrita ao acervo do usuário
│   │   └── trash.py                 # Lixeira restrita a itens do usuário
│   ├── schemas/
│   │   └── user.py                  # [NEW] Schemas Pydantic UserRead
│   └── services/
│       ├── persistence.py           # Função auxiliar get_user_resource_or_404
│       └── trash_service.py         # Exclusão lógica e purga restritas ao proprietário
├── migrations/
│   └── versions/
│       └── 0011_add_user_and_multiuser_foundation.py  # [NEW] Migração Alembic do schema
└── tests/
    ├── test_multiuser_migration.py  # [NEW] Teste de migração sem perdas
    └── test_multiuser_isolation.py  # [NEW] Teste de isolamento A vs B e anti-IDOR

frontend/
└── src/
    └── services/
        └── api.ts                   # Propagação opcional do contexto de usuário
```

**Structure Decision**: Aplicação Web cliente-servidor padrão com backend modular em FastAPI (Routers, Models, Schemas, Services) e frontend em Vue 3.

---

## Complexity Tracking

> **Nenhuma violação à Constituição identificada.** O design adota padrões nativos do SQLAlchemy 2 e FastAPI (injeção de dependência), sem adicionar bibliotecas externas pesadas ou alterar o motor SQLite WAL.
