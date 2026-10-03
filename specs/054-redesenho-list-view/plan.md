# Implementation Plan: F 0.7.5 — Redesenho da List View: Busca Rápida, Filtragem e Comparação Analítica

**Branch**: `054-redesenho-list-view` | **Date**: 2026-10-03 | **Spec**: [specs/054-redesenho-list-view/spec.md](spec.md)

**Input**: Feature specification from `/specs/054-redesenho-list-view/spec.md`

---

## Summary

Redesenhar a `StudyListView.vue` para consolidar sua responsabilidade central no Caderno de Leitura: **busca instantânea, alta densidade informacional, ordenação multicritério e comparação analítica entre estudos**.
A implementação integra:
1. Tabela densa e estruturada no desktop com cabeçalhos clicáveis para ordenação tripartite (`asc` -> `desc` -> `default`) e persistência no `localStorage`.
2. Composable modular `useStudyListFilters.ts` com busca textual reativa (< 50ms) insensível a acentos/diacríticos e filtro rápido por status de leitura.
3. Micro-chips fixos de seções analíticas (`R`, `E`, `C`, `Ref`) com flags de completude expostas em `StudySummary`.
4. Layout mobile adaptativo com 2 linhas por estudo, busca fixa no topo, gaveta expansível para filtros de status e alvos táteis mínimos de 44×44px.
5. Linhas de esqueleto animadas (*Skeleton Screens*) durante o carregamento dos estudos.

---

## Technical Context

**Language/Version**: Python 3.13 (Backend) / TypeScript 5.8+ (Frontend)  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2.0, Vue 3 (Composition API), Vite, Tailwind/CSS  
**Storage**: SQLite local (WAL mode, sem alteração de schema em banco — campos analíticos já existentes em `studies`)  
**Testing**: `node --test` (Frontend unitário), `pytest` (Backend integração), `vue-tsc -b` (Tipagem estrita)  
**Target Platform**: Windows local (processo único `iniciar.py`) / Web desktop e mobile (Tailscale)  
**Project Type**: Aplicação Web híbrida (Backend REST FastAPI + Frontend SPA Vue 3)  
**Performance Goals**: Filtragem reativa no cliente < 10ms; ordenação da tabela instantânea sem layout shift  
**Constraints**: Zero impacto em banco de produção (`backend/data/caderno.db`); testes em bancos efêmeros (`tmp_path`)  
**Scale/Scope**: Capítulos com dezenas a centenas de estudos; suporte sem paginação com virtualização pronta se necessário  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Princípio I (Privacidade e Acervo):** ✅ PASS. Nenhuma leitura de acervo real; dados sintéticos para testes.
- **Princípio II (Isolamento de Testes):** ✅ PASS. Testes usam `tmp_path` e instâncias descartáveis.
- **Princípio III (Fidelidade Arquitetural):** ✅ PASS. Stack Python 3.13 / FastAPI + Vue 3 / TS estrito.
- **Princípio IV (Spec-Driven Development):** ✅ PASS. Conduzido estritamente pelo ciclo Spec Kit.
- **Princípio V (Resiliência Operacional):** ✅ PASS. Sem migrações destrutivas de schema; dados persistidos com segurança.

---

## Project Structure

### Documentation (this feature)

```text
specs/054-redesenho-list-view/
├── spec.md              # Especificação refinada com esclarecimentos
├── plan.md              # Este plano técnico de implementação
├── research.md          # Decisões arquiteturais D1 a D5
├── data-model.md        # Schemas Pydantic, TypeScript e estados de filtro
├── quickstart.md        # 5 cenários de validação fim a fim
├── contracts/           # Contratos de composable e componente
│   └── study-list-filters.md
├── checklists/
│   └── requirements.md  # Checklist de qualidade (16/16 PASS)
└── tasks.md             # Tarefas atômicas (geradas pelo /speckit-tasks)
```

### Source Code

```text
caderno-leitura-0.1/
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   │   └── studies.py               # População de flags has_summary, has_explanation, etc.
│   │   └── schemas/
│   │       └── study.py                 # Extensão do StudySummary com flags de seções
│   └── tests/
│       └── test_study_list_summary.py   # Teste de integração backend das flags de completude
└── frontend/
    ├── src/
    │   ├── types.ts                     # Extensão da interface StudySummary e tipos de ordenação
    │   ├── composables/
    │   │   └── useStudyListFilters.ts   # Composable de busca, filtros de status e ordenação
    │   └── components/
    │       └── views/
    │           └── StudyListView.vue    # Redesenho da tabela densa, busca, micro-chips e mobile
    └── tests/
        ├── study_list_filters.test.mjs  # Testes unitários do composable de busca e ordenação
        └── study_list_view.test.mjs     # Testes unitários do componente e acessibilidade WAI-ARIA
```

**Structure Decision**: Web application padrão do repositório, com modelo modular backend FastAPI e componentes Vue 3 com composable dedicado no frontend.

---

## Complexity Tracking

*Nenhuma violação aos princípios da Constituição.*
