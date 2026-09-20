# Implementation Plan: F08 — Busca Global Contextual

**Branch**: `025-busca-global-contextual` | **Date**: 2026-09-19 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/025-busca-global-contextual/spec.md`  

---

## Summary

Implementar um mecanismo transversal de busca e localização de conteúdo em toda a aplicação, indexando estudos, anotações, conceitos, explicações e referências com normalização de acentos, suporte a múltiplos termos (AND por padrão com sugestão assistida de OR), geração de fragmentos de contexto (*snippets*) destacados e navegação em 1 clique diretamente para a leitura do estudo. Inclui a persistência estruturada do histórico de pesquisas no backend (`search_history`), garantindo prontidão para sincronização em nuvem futura (ex.: conta Google).

---

## Technical Context

**Language/Version**: Python 3.13 (Backend) | TypeScript 5+ com Vue 3 (Frontend)  
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2 (Backend) | Vue 3, Vite, Tailwind CSS (Frontend)  
**Storage**: SQLite local em modo Write-Ahead Logging (WAL) com chaves estrangeiras ativas (`caderno.db`)  
**Testing**: `pytest` com bancos SQLite efêmeros em `tmp_path` (Backend) | `node --test` com JSDOM (Frontend)  
**Target Platform**: Windows 11 / 10 local (desktop e rede local privada/celular via `iniciar.py`)  
**Project Type**: Aplicação Web Local (FastAPI backend + Vue 3 SPA frontend empacotado em `dist/`)  
**Performance Goals**: Tempo de resposta da API de busca < 200ms para acervos de até 10.000 estudos; debounce de digitação de 250ms no frontend; abertura do modal < 100ms  
**Constraints**: Zero chamadas a serviços externos de IA em tempo de execução; isolamento absoluto do banco de dados ativo de produção (`backend/data/caderno.db`) durante testes; exclusão estrita de itens em soft delete (`deleted_at IS NULL`); sanitização rigorosa contra XSS nos snippets destacados  
**Scale/Scope**: Acervos pessoais de centenas a dezenas de milhares de estudos, 1 modal global responsivo, 1 nova tabela relacional (`search_history`), 4 novos endpoints REST  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Proteção do Acervo e Privacidade**: PASS. Nenhum dado do usuário ou texto do acervo é exposto ou enviado externamente. A busca opera 100% no SQLite local.
- **II. Isolamento de Testes**: PASS. Todos os testes unitários e de integração operam com fixtures utilizando `tmp_path` e portas efêmeras. O arquivo `backend/data/caderno.db` não é tocado.
- **III. Fidelidade Arquitetural**: PASS. Segue estritamente a stack Python 3.13 / FastAPI / SQLAlchemy 2.0 / Alembic e Vue 3 / TypeScript / Vite.
- **IV. Governança SDD**: PASS. O avanço cumpre a disciplina de fases do GitHub Spec Kit (`speckit-specify` → `speckit-plan` → `speckit-tasks` → `speckit-analyze` → `speckit-implement`).
- **V. Resiliência e Migrações Seguras**: PASS. A adição da tabela `search_history` ocorre via migração Alembic reversível (`0010_add_search_history.py`), protegida pelo hook obrigatório de snapshot pré-migração (`ensure_pre_upgrade_snapshot`).

---

## Project Structure

### Documentation (this feature)

```text
specs/025-busca-global-contextual/
├── plan.md              # Este plano de implementação
├── research.md          # Decisões de pesquisa técnica (Phase 0)
├── data-model.md        # Modelo de dados, schemas e DTOs (Phase 1)
├── quickstart.md        # Guia executável de validação (Phase 1)
├── contracts/
│   └── search-api.md    # Contrato formal da API REST
└── checklists/
    └── requirements.md  # Validação de requisitos funcionais
```

### Source Code (repository layout)

```text
caderno-leitura-0.1/
├── backend/
│   ├── app/
│   │   ├── db/
│   │   │   └── session.py            # Registro da UDF 'unaccent' na conexão SQLite
│   │   ├── models/
│   │   │   └── search_history.py     # Modelo declarativo SQLAlchemy SearchHistory
│   │   ├── schemas/
│   │   │   └── search.py             # Schemas Pydantic v2 (SearchMatchItem, SearchResponse, etc.)
│   │   ├── services/
│   │   │   └── search_service.py     # Lógica de busca, normalização, snippets e histórico
│   │   ├── routers/
│   │   │   └── search.py             # Endpoints /api/search e /api/search/history
│   │   └── main.py                   # Registro do router de busca na aplicação FastAPI
│   ├── migrations/
│   │   └── versions/
│   │       └── 0010_add_search_history.py # Migração da tabela search_history
│   └── tests/
│       └── test_search_api.py        # Suíte de testes automatizados com SQLite em tmp_path
└── frontend/
    ├── src/
    │   ├── types.ts                  # Tipagens TypeScript para busca e histórico
    │   ├── services/
    │   │   └── api.ts                # Métodos de API (search, getSearchHistory, deleteSearchHistory)
    │   ├── composables/
    │   │   └── useGlobalSearch.ts    # Composable reativo com debounce e atalho de teclado
    │   ├── components/
    │   │   └── search/
    │   │       ├── GlobalSearchModal.vue  # Modal global com focus trap e overlay mobile
    │   │       ├── SearchResultItem.vue   # Card de resultado com destaque e trilha do livro
    │   │       └── SearchHistoryList.vue  # Lista de pesquisas recentes com descarte rápido
    │   └── App.vue                   # Integração do botão e modal de busca global
    └── tests/
        ├── global-search.test.mjs    # Testes unitários do fluxo de busca e histórico
        └── global-search-a11y.test.mjs # Testes de acessibilidade e ergonomia móvel
```

**Structure Decision**: Padrão de aplicação web local desacoplada (`backend/` FastAPI e `frontend/` Vue 3 SPA), integrando o serviço de busca com a UDF SQLite `unaccent` e componentes de apresentação modulares em `components/search/`.

---

## Complexity Tracking

> **Nenhuma violação constitucional detectada. Todas as restrições foram cumpridas.**
