# Implementation Plan: F0.7.11 — Biblioteca Transversal de Highlights e Anotações

**Branch**: `060-biblioteca-highlights-anotacoes` | **Date**: 2026-10-06 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/060-biblioteca-highlights-anotacoes/spec.md`

## Summary

Construir uma visão transversal e pesquisável de todas as marcações, anotações de margem, citações, clozes e perguntas do usuário, permitindo filtragem multidimensional por obra, capítulo, tipo e cor cromática, sincronização de estado na URL, alternância entre modos "Recentes" e "Por Obra", gestão in-card e retorno imediato ao estudo de origem com rolagem suave e pulso luminoso guia.

A solução técnica introduz o endpoint consolidado `GET /api/highlights/library` no backend (com junção indexada entre destaques, estudos, capítulos e livros, filtragem de lixeira e isolamento multiusuário), novo índice Alembic em `study_highlights(user_id, kind, color)`, a visão `HighlightsLibraryView.vue` com os componentes `HighlightFilterToolbar.vue` e `HighlightCard.vue` no frontend, atalho de navegação no menu principal e integração com âncora `#highlight-{id}` em `StudyView.vue`.

## Technical Context

**Language/Version**: Python 3.13 (Backend), TypeScript 5.6+ / JavaScript (Frontend)

**Primary Dependencies**:
- Backend: FastAPI, SQLAlchemy 2.0 (declarative mapping), Alembic, Pydantic v2
- Frontend: Vue 3 (Composition API, `<script setup>`), Vue Router 4, Lucide Vue Next, Tailwind/CSS customizado

**Storage**: SQLite local (modo WAL), tabela `study_highlights` com índice composto de suporte `(user_id, kind, color)`

**Testing**:
- Backend: `pytest` com bancos descartáveis SQLite em `tmp_path`
- Frontend: `node:test` e asserções estritas (`node --test`)

**Target Platform**: Windows local (PowerShell, processo único local via `iniciar.py`)

**Project Type**: Web Application monorepo desacoplada (`backend/` FastAPI + `frontend/` Vue 3)

**Performance Goals**:
- Resposta de busca sob 300ms a partir do fim da digitação (debounce de 250ms)
- Paginação no backend limitando payloads a < 50KB por página
- Carregamento inicial da biblioteca em < 1 segundo

**Constraints**:
- Isolamento multiusuário rigoroso: todo highlight filtrado por `user_id == current_user.id`
- Ocultação automática de destaques pertencentes a estudos ou livros na lixeira (`deleted_at IS NOT NULL`)
- Alvos táteis móveis mínimos de $44 \times 44$px para ergonomia em telas $\le 768$px
- Sem emojis informais em arquivos de produção do `frontend/src`
- Acessibilidade WAI-ARIA com labels descritivos para leitores de tela

**Scale/Scope**: Suporte ágil para acervos com milhares de destaques distribuídos em dezenas de livros e centenas de capítulos

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Artigo I — Proteção Absoluta do Acervo e Privacidade de Dados**: Nenhum texto real ou banco de produção é acessado. Testes utilizam dados sintéticos.
- [x] **Artigo II — Isolamento Estrito de Testes e Operações Locais**: Testes utilizam bancos temporários em `tmp_path`, portas efêmeras e nunca tocam `backend/data/caderno.db`.
- [x] **Artigo III — Fidelidade Arquitetural e Tecnológica**: Uso rigoroso da stack oficial (Python 3.13, FastAPI, SQLAlchemy 2, Alembic, Vue 3, TS estrito, SQLite local).
- [x] **Artigo IV — Governança por Especificação Delimitada (SDD)**: Ciclo formal de especificação e planejamento executado através do Spec Kit (`agy`).
- [x] **Artigo V — Resiliência Operacional e Migrações Seguras**: A migração Alembic adiciona apenas um índice de consulta (`CREATE INDEX`), sem alterações destrutivas de colunas ou tabelas.

## Project Structure

### Documentation (this feature)

```text
specs/060-biblioteca-highlights-anotacoes/
├── spec.md              # Especificação refinada com decisões do usuário
├── plan.md              # Este plano técnico de implementação
├── research.md          # Consolidação de decisões técnicas e alternativas
├── data-model.md        # Modelos relacionais, esquemas Pydantic e TypeScript
├── quickstart.md        # Guia de validação automatizada e manual
├── contracts/           # Contratos OpenAPI do endpoint consolidado
│   └── highlights-library-api.yaml
└── checklists/
    └── requirements.md  # Checklist de validação de qualidade (100% aprovado)
```

### Source Code (repository layout)

```text
caderno-leitura-0.1/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   └── study_highlight.py            # Definição ORM existente e índice
│   │   ├── schemas/
│   │   │   └── study_highlight.py            # Novos esquemas HighlightLibraryItemRead e HighlightLibraryResponse
│   │   ├── services/
│   │   │   └── study_highlight_service.py    # Nova função list_library_highlights com junções e filtros
│   │   └── routers/
│   │       └── study_highlights.py           # Novo endpoint GET /api/highlights/library
│   ├── migrations/
│   │   └── versions/
│   │       └── 0025_add_highlight_library_index.py  # Migração Alembic do índice de apoio
│   └── tests/
│       └── test_highlights_library.py        # Suíte de testes automatizados do backend
│
└── frontend/
    ├── src/
    │   ├── types.ts                          # Tipos TypeScript para HighlightLibraryItem e query params
    │   ├── api.ts                            # Cliente HTTP com chamada getHighlightLibrary
    │   ├── router/
    │   │   └── index.ts                      # Registro da rota /highlights
    │   ├── components/
    │   │   ├── layout/
    │   │   │   └── AppHeader.vue             # Link de navegação no cabeçalho/menu para Destaques
    │   │   ├── highlights/
    │   │   │   ├── HighlightFilterToolbar.vue # Barra de busca, filtros de livro/tipo/cor e alternador de modo
    │   │   │   └── HighlightCard.vue         # Cartão individual com trecho, nota, edição in-card e salto
    │   │   └── views/
    │   │       ├── HighlightsLibraryView.vue # Visão principal da biblioteca de destaques
    │   │       └── StudyView.vue             # Suporte a âncora #highlight-{id} com scroll e pulso visual
    │   └── utils/
    │       └── highlightRenderer.ts          # Suporte e animação de foco visual
    └── tests/
        └── highlights_library_view.test.mjs  # Suíte de testes automatizados do frontend
```

**Structure Decision**: Padrão Web Application monolítica desacoplada do projeto Caderno de Leitura, com backend modular em `backend/app/` e frontend SPA Vue 3 em `frontend/src/`.

## Complexity Tracking

*Nenhuma violação constitucional detectada. Todas as soluções reutilizam a infraestrutura existente de banco, rotas, roteador e utilitários do sistema.*
