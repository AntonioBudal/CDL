# Implementation Plan: Categorias e Taxonomia de Livros (T05)

**Branch**: `006-categorias-taxonomia` | **Date**: 2026-09-18 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/006-categorias-taxonomia/spec.md`

---

## Summary

Implementação da taxonomia estruturada do Caderno de Leitura correspondente à entrega **T05** do Roadmap 0.3. Inclui o fornecimento de catálogo canônico com mais de 100 categorias hierarquizadas em português (organizadas em árvore acíclica com caminhos desnormalizados), persistência relacional em SQLite via SQLAlchemy 2.0 (tabelas `categories` e associativa `book_categories` para suporte N:N), rotina de carga/sincronização estritamente idempotente, busca preditiva instantânea no frontend com exibição do caminho hierárquico, e filtragem inclusiva/recursiva no acervo (ao filtrar por uma categoria pai, inclui livros de suas subcategorias).

---

## Technical Context

**Language/Version**: Python 3.13 de 64 bits (backend) | TypeScript 5.8 e Vue 3.5 (frontend)  
**Primary Dependencies**: FastAPI 0.115, SQLAlchemy 2.0, Alembic 1.14, Pydantic v2 (backend); Vue 3 (Composition API), Vite 6, Tailwind/CSS (frontend)  
**Storage**: SQLite local (modo WAL, `PRAGMA foreign_keys = ON`). Novas tabelas: `categories` e `book_categories`. Arquivo canônico estático `backend/app/data/canonical_categories.json`  
**Testing**: `pytest` com SQLite efêmero em `tmp_path` (backend); `node:test` e `vue-tsc` (frontend)  
**Target Platform**: Windows local (PowerShell, processo único via `iniciar.py`, portas efêmeras em testes)  
**Project Type**: Aplicação Web local (SPA compilada servida por FastAPI)  
**Performance Goals**: Autocomplete de categorias em < 50ms; resolução recursiva de subcategorias em < 10ms; sincronização idempotente de catálogo em < 200ms  
**Constraints**: Zero impacto em `caderno.db` ativo durante testes; nenhuma geração de categorias por IA em tempo de execução; isolamento total de itens na lixeira; preservação de categorias em edições parciais (`PATCH`)  
**Scale/Scope**: ~120 categorias canônicas divididas em 10 grandes áreas do conhecimento, acervos de centenas a milhares de livros  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Art. I (Proteção e Privacidade)**: Apenas dados sintéticos/fictícios são utilizados em testes e no catálogo público de categorias. Zero dados reais do usuário são acessados ou transmitidos.
- [x] **Art. II (Isolamento de Testes)**: Todos os testes automatizados utilizam exclusivamente bancos SQLite descartáveis em `tmp_path`. O banco ativo local (`caderno.db`) não é tocado.
- [x] **Art. III (Fidelidade Tecnológica)**: Backend em Python 3.13 com SQLAlchemy 2.0 e migração incremental via Alembic; frontend em Vue 3 `<script setup>` e TypeScript estrito; SQLite com chaves estrangeiras ativadas.
- [x] **Art. IV (Governança SDD)**: O plano segue rigorosamente as especificações aprovadas e os esclarecimentos de T05.
- [x] **Art. V (Resiliência e Migrações)**: A migração `0005_add_categories_and_taxonomy.py` cria as tabelas com constraints seguras (`ON DELETE CASCADE` para livros, `ON DELETE RESTRICT` para categorias), preservando a integridade referencial.

---

## Project Structure

### Documentation (this feature)

```text
specs/006-categorias-taxonomia/
├── spec.md                  # Especificação funcional aprovada
├── plan.md                  # Este plano técnico de implementação
├── research.md              # Pesquisa técnica e decisões de arquitetura
├── data-model.md            # Modelagem de dados, diagramas e tabelas
├── contracts/               # Contratos de API e tipos TypeScript
│   └── categories-api.md
├── quickstart.md            # Roteiro prático de validação e testes
├── checklists/
│   └── requirements.md      # Checklist de qualidade dos requisitos
└── tasks.md                 # Decomposição de tarefas (/speckit-tasks)
```

### Source Code (repository layout)

```text
backend/
├── app/
│   ├── data/
│   │   └── canonical_categories.json       # Catálogo com >100 categorias canônicas
│   ├── models/
│   │   ├── __init__.py                     # Exportação de Book, Category, etc.
│   │   ├── book.py                         # Relacionamento N:N com Category
│   │   └── category.py                     # Modelo SQLAlchemy da entidade Category
│   ├── schemas/
│   │   ├── book.py                         # BookRead com categories, BookCreate/Patch com category_ids
│   │   └── category.py                     # Schemas CategoryRead, CategoryTree
│   ├── routers/
│   │   ├── books.py                        # GET /api/books com filtro ?category= recursivo
│   │   └── categories.py                   # GET /api/categories (busca e listagem da taxonomia)
│   ├── services/
│   │   └── category_service.py             # Validação, cálculo de paths, CTE recursiva e sync idempotente
│   └── main.py                             # Inclusão do router de categories e sync na inicialização
├── migrations/versions/
│   └── 0005_add_categories_and_taxonomy.py # Migração Alembic para categories e book_categories
└── tests/
    └── test_categories.py                  # Suíte de testes de taxonomia, integridade, seed e filtros

frontend/
├── src/
│   ├── types.ts                            # Interfaces Category, Book.categories, LibraryFilterState
│   ├── api.ts                              # Métodos fetchCategories, etc.
│   ├── composables/
│   │   ├── useCategories.ts                # Carregamento em cache, busca preditiva e mapa de descendentes
│   │   └── useLibraryFilter.ts             # Filtro por categoria inclusivo/recursivo integrado
│   ├── components/
│   │   ├── CategoryBadge.vue               # Tag/etiqueta visual da categoria com remoção opcional
│   │   ├── CategorySelector.vue            # Campo preditivo com busca, autocomplete e trilha hierárquica
│   │   ├── BookEditModal.vue               # Integração do seletor de categorias na criação/edição
│   │   └── LibraryToolbar.vue              # Seletor de categorias integrado na barra da estante
│   └── views/
│       ├── BooksView.vue                   # Exibição de badges na grade/lista e filtro integrado
│       └── BookView.vue                    # Exibição de badges no cabeçalho da obra
└── tests/
    └── categories.test.mjs                 # Testes unitários do composable e hierarquia
```

---

## Complexity Tracking

*Nenhuma violação constitucional detectada. A solução utiliza componentes e padrões nativos já consolidados na arquitetura do projeto.*
