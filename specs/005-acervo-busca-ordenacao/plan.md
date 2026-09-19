# Implementation Plan: Acervo — Visualização, Busca e Ordenação

**Branch**: `005-acervo-busca-ordenacao` | **Date**: 2026-09-18 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/005-acervo-busca-ordenacao/spec.md`

---

## Summary

Esta feature implementa a capacidade de **visualização, busca instantânea e ordenação flexível do acervo** de livros no Caderno de Leitura, atendendo à entrega **T04** do Roadmap 0.3.
O leitor poderá:
1. **Buscar livros em tempo real** através de um campo dinâmico, com filtragem instantânea insensível a maiúsculas/minúsculas e acentos (normalização Unicode NFKD), cobrindo título, autor e subtítulo.
2. **Alternar instantaneamente entre a Grade de Capas e a Lista Compacta**, persistindo a preferência no navegador e convivendo harmonicamente com as configurações de tema e densidade.
3. **Ordenar o acervo** por título (A–Z e Z–A), autor, recentemente adicionados (`created_at`), recentemente modificados (`updated_at`), mais antigos adicionados e ano de publicação.
4. **Garantir isolamento da lixeira**, assegurando que livros excluídos (soft delete) nunca apareçam nas listagens ou buscas ativas.

---

## Technical Context

**Language/Version**: Python 3.13 (Backend), TypeScript 5.9+ / Vue 3 (Frontend)  
**Primary Dependencies**: FastAPI 0.115+, SQLAlchemy 2.0+, Alembic, Uvicorn (Backend); Vue 3 (Composition API), Vite 8+, Tailwind/CSS nativo (Frontend)  
**Storage**: SQLite 3 (modo WAL local), chave de preferência no `localStorage` do navegador  
**Testing**: `pytest` com banco e diretórios efêmeros em `tmp_path` (Backend); `node:test` e `vue-tsc` (Frontend)  
**Target Platform**: Windows local (PC), navegadores desktop e dispositivos móveis em rede privada / Tailscale  
**Project Type**: Aplicação Web local de processo único (`iniciar.py`)  
**Performance Goals**: Resposta de filtragem em menos de 50ms a cada tecla no frontend; transição entre grade e lista em menos de 50ms; ordenação determinística instantânea  
**Constraints**: Zero impacto no banco ativo de produção durante testes; itens da lixeira estritamente ocultos; acessibilidade visual com teclado e leitores de tela  
**Scale/Scope**: Acervos pessoais de centenas a milhares de obras com responsividade total  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Proteção Absoluta do Acervo e Privacidade de Dados**: PASS — Nenhum dado pessoal ou acervo real é exposto; busca é executada localmente sem telemetria externa.
- **II. Isolamento Estrito de Testes e Operações Locais**: PASS — Toda suíte de testes utiliza `tmp_path` descartável e portas efêmeras; `backend/data/caderno.db` não é acessado.
- **III. Fidelidade Arquitetural e Tecnológica**: PASS — Tecnologias oficiais mantidas (FastAPI, SQLAlchemy 2, Vue 3 Composition API, SQLite WAL local).
- **IV. Governança por Especificação Delimitada (SDD)**: PASS — Ciclo Spec Kit rigorosamente respeitado (`specify` → `clarify` → `plan` → `tasks` → `analyze` → `implement`).
- **V. Resiliência Operacional e Migrações Seguras**: PASS — Não há alteração destrutiva no esquema; campos `created_at`, `updated_at`, `deleted_at` e `cover_image` já existem no modelo de livros.

---

## Project Structure

### Documentation (this feature)

```text
specs/005-acervo-busca-ordenacao/
├── spec.md              # Especificação de requisitos e estórias de usuário
├── plan.md              # Este plano técnico de implementação
├── research.md          # Decisões de pesquisa técnica (Phase 0)
├── data-model.md        # Modelos de dados e preferências (Phase 1)
├── quickstart.md        # Guia rápido de validação passo a passo
├── contracts/           # Contratos de API e componentes
│   └── library-view-api.md
└── checklists/
    └── requirements.md  # Checklist de qualidade da especificação
```

### Source Code Impacted

```text
caderno-leitura-0.1/
├── backend/
│   ├── app/
│   │   └── routers/
│   │       └── books.py               # Adição de suporte opcional a parâmetros q, sort e order em GET /api/books
│   └── tests/
│       └── test_books_search_and_sort.py # Nova suíte de testes de busca e ordenação no backend
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── LibraryToolbar.vue     # Novo componente: barra de busca, menu de ordenação e alternador grade/lista
│   │   ├── composables/
│   │   │   └── useLibraryFilter.ts    # Composable: lógica reativa de normalização, busca, ordenação e persistência
│   │   ├── views/
│   │   │   └── BooksView.vue          # Integração da barra, modo grade e modo lista compacta
│   │   └── types.ts                   # Exportação de tipos LibraryViewMode e BookSortOption
│   └── tests/
│       └── library-filter.test.mjs    # Suíte unitária: busca sem acentos, ordenação de múltiplos tipos e persistência
```

---

## Complexity Tracking

> **Nenhuma violação constitucional detectada.** A arquitetura reaproveita composables e componentes nativos com zero complexidade acidental.

| Item | Necessidade | Alternativa Mais Simples Rejeitada Porque |
|---|---|---|
| Composable `useLibraryFilter.ts` | Centralizar normalização diacrítica, busca e ordenação | Deixar tudo inline em `BooksView.vue` dificultaria testes unitários isolados com `node:test`. |
