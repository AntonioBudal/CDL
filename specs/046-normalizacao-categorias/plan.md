# Implementation Plan: F0.6.7 — Normalização e Simplificação de Categorias

**Branch**: `046-normalizacao-categorias` | **Date**: 2026-10-02 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/046-normalizacao-categorias/spec.md`

---

## Summary

Esta feature reestrutura a taxonomia de categorias do Leitorum, transitando de um catálogo extenso e inconsistente para uma **taxonomia estritamente plana (*flat*) de termos concisos e em forma singular** em língua portuguesa (ex.: *"Filosofia"*, *"História"*, *"Ciência"*). A solução implementa:
1. Um **serviço de normalização determinístico** no backend (`category_normalizer.py`) para lematização e busca insensível a maiúsculas/acentos.
2. Uma **migração Alembic segura e não destrutiva** com **atribuição distributiva** para categorias compostas e consolidação de junções em `book_categories`.
3. Uma **interface assistida com autocompletar** no frontend (`CategoryInput.vue`) que sugere formas canônicas e previne novos plurais ou termos desorganizados.
4. Preservação de 100% dos vínculos de livros existentes, sem perda de estudos ou acervo.

---

## Technical Context

**Language/Version**: Python 3.13 (Backend), TypeScript 5.x / Vue 3 (Frontend)  
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0 (ORM declarativo), Alembic, Pydantic v2, Vite, Tailwind/CSS  
**Storage**: SQLite 3 local em modo Write-Ahead Logging (WAL) com chaves estrangeiras ativadas (`PRAGMA foreign_keys = ON`)  
**Testing**: `pytest` (backend em `backend/tests/test_category_normalization.py`), `node --test` / vitest (frontend)  
**Target Platform**: Windows 11 local (PowerShell, CRLF/LF, caminhos canônicos), com acesso híbrido LAN/Tailscale  
**Project Type**: Web Application monoprocesso local (`caderno-leitura-0.1/iniciar.py`)  
**Performance Goals**: Tempo de resposta de listagem e filtros de categorias < 200ms; autocompletar em tempo real < 50ms  
**Constraints**: Zero perda de vínculos de livros existentes (Princípio I); isolamento total em `tmp_path` nos testes (Princípio II); migração segura com backup consistente prévio (Princípio V)  
**Scale/Scope**: Migração e consolidação de ~100+ termos legados para um catálogo de ~20-30 termos canônicos curtos

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Princípio I (Proteção do Acervo e Privacidade):** PASS. O acervo ativo é 100% preservado; a migração de categorias aplica atribuição distributiva sem excluir livros ou quebrar referências temáticas.
- [x] **Princípio II (Isolamento Estrito de Testes):** PASS. Toda a validação automatizada executa sobre bancos SQLite temporários descartáveis em `tmp_path`, sem tocar no banco ativo `caderno.db`.
- [x] **Princípio III (Fidelidade Arquitetural):** PASS. Uso exclusivo de FastAPI, SQLAlchemy 2.0, Alembic e Vue 3 Composition API em processo único.
- [x] **Princípio IV (Governança Spec Kit):** PASS. Especificação, clarificação e plano técnico formalmente elaborados antes de qualquer tarefa de código.
- [x] **Princípio V (Resiliência e Migrações Seguras):** PASS. O hook pré-migração existente dispara o snapshot consistente via SQLite Backup API antes de aplicar qualquer alteração em `book_categories`.

---

## Project Structure

### Documentation (this feature)

```text
specs/046-normalizacao-categorias/
├── spec.md              # Especificação de requisitos e histórias de usuário
├── plan.md              # Este plano de implementação técnica
├── research.md          # Decisões de arquitetura consolidadas (Phase 0)
├── data-model.md        # Modelagem de dados e regras relacionais (Phase 1)
├── quickstart.md        # Guia de validação executável ponta a ponta (Phase 1)
├── contracts/           # Contratos de API OpenAPI 3.0 (Phase 1)
│   └── categories-api.yaml
└── checklists/          # Checklists de qualidade
    └── requirements.md
```

### Source Code (Caminhos Reais da Aplicação)

```text
caderno-leitura-0.1/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   └── category.py            # Modelo Category com taxonomia plana e is_canonical
│   │   ├── schemas/
│   │   │   └── category.py            # Schemas Pydantic de entrada, saída e sugestões
│   │   ├── services/
│   │   │   ├── category_service.py    # Lógica de negócio, consultas e filtros
│   │   │   └── category_normalizer.py # Regras de normalização gramatical e singularização
│   │   └── routers/
│   │       └── categories.py          # Endpoints /api/categories, /suggest, /stats
│   ├── migrations/
│   │   └── versions/
│   │       └── 0023_normalize_categories.py # Migração Alembic distributiva
│   └── tests/
│       └── test_category_normalization.py  # Testes de integração de migração e CRUD
│
└── frontend/
    └── src/
        ├── components/
        │   └── CategoryInput.vue      # Componente com autocompletar e sugestão canônica
        ├── views/
        │   ├── BooksView.vue          # Filtro de categorias simplificado e plano
        │   └── BookView.vue           # Exibição das tags canônicas
        └── api/
            └── categories.ts          # Cliente HTTP para endpoints de categorias
```

**Structure Decision**: Aplicação Web existente (`caderno-leitura-0.1/`), com backend em FastAPI e frontend em Vue 3. Todas as modificações respeitam estritamente a arquitetura modular já homologada.

---

## Complexity Tracking

*Nenhuma violação constitucional detectada. Todas as soluções reutilizam tabelas, padrões e serviços existentes.*
