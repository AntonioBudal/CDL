# Implementation Plan: F02 — Hierarquia Interativa

**Branch**: `020-hierarquia-interativa` | **Date**: 2026-09-19 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/020-hierarquia-interativa/spec.md`

---

## Summary

Implementação da estrutura hierárquica autêntica para estudos no Caderno de Leitura, permitindo relações de parentesco (estudos pais e filhos) em até 5 níveis de profundidade, ordenação estável entre irmãos (`position`), reorganização interativa por arrastar e soltar (HTML5 nativo), menu de ações táteis acessíveis (mínimo de 44x44px no mobile), prevenção matemática estrita contra referências circulares (DAG) com rejeição HTTP 422, tratamento em cascata lógica na lixeira e persistência reativa no SQLite com concorrência otimista.

---

## Technical Context

**Language/Version**: Python 3.13 de 64 bits (backend) / TypeScript 5+ com Vue 3 (Composition API, `<script setup>`) no frontend.  
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0, Alembic, Uvicorn, Vite, Lucide Vue Next, Pinia/Reatividade nativa do Vue 3.  
**Storage**: SQLite local em modo WAL com chaves estrangeiras ativas (`PRAGMA foreign_keys = ON`).  
**Testing**: pytest com SQLite em memória/bancos efêmeros em `tmp_path` (backend); Vitest/node tests (frontend).  
**Target Platform**: Windows 11 local (desktops, laptops e navegadores de dispositivos móveis via rede local/Tailscale).  
**Project Type**: Aplicação web local full-stack única (FastAPI servindo API e interface empacotada Vite).  
**Performance Goals**: Animações a 60fps; reorganização e persistência em < 100ms; renderização de árvores de até 100 estudos em < 50ms.  
**Constraints**: 
- Isolamento absoluto: nunca tocar no banco ativo `backend/data/caderno.db`.
- Zero bibliotecas pesadas de terceiros para drag-and-drop.
- Limite máximo seguro de 5 níveis de aninhamento (0 a 4).
- Alvos de toque de no mínimo 44x44px em resoluções móveis (< 768px).
- Respeito à preferência de movimento reduzido (`prefers-reduced-motion`).
**Scale/Scope**: Até 100 estudos por capítulo; até 5 níveis hierárquicos; suporte concorrente PC/móvel.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [X] **I. Proteção Absoluta do Acervo e Privacidade de Dados**: Nenhum dado do acervo real é lido ou modificado. Metadados e textos originais são estritamente preservados.
- [X] **II. Isolamento Estrito de Testes e Operações Locais**: Testes executam contra SQLite efêmero em `tmp_path`, portas efêmeras, sem disputar porta 8000 nem tocar no banco de produção.
- [X] **III. Fidelidade Arquitetural e Tecnológica**: Python 3.13, FastAPI, SQLAlchemy 2.0, Alembic, Vue 3, TS estrito, Vite, SQLite local.
- [X] **IV. Governança por Especificação Delimitada (SDD)**: Ciclo formal seguido (`specify` -> `clarify` -> `plan` -> `tasks` -> `analyze` -> `implement`).
- [X] **V. Resiliência Operacional e Migrações Seguras**: Migração 0006 idempotente e segura, adicionando `parent_study_id` e `position` com defaults seguros e índices adequados.

---

## Project Structure

### Documentation (this feature)

```text
specs/020-hierarquia-interativa/
├── spec.md              # Especificação formal aprovada
├── checklists/
│   └── requirements.md  # Checklist de qualidade (16/16 aprovado)
├── plan.md              # Este plano de implementação
├── research.md          # Decisões técnicas e arquiteturais consolidadas
├── data-model.md        # Modelos relacionais, entidades e validações
├── contracts/
│   └── study-hierarchy-api.yaml # Contrato OpenAPI para movimentação hierárquica
├── quickstart.md        # Guia executável de testes e validação
└── tasks.md             # Tarefas atômicas (geradas pelo /speckit-tasks)
```

### Source Code Impacted

```text
caderno-leitura-0.1/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   └── study.py                        # Adicionar parent_study_id, position e relationships
│   │   ├── schemas/
│   │   │   └── study.py                        # Atualizar StudySummary, StudyRead, StudyPatch, criar StudyMove
│   │   ├── services/
│   │   │   ├── study_service.py                # Lógica DAG, verificação de ciclos, limite de 5 níveis
│   │   │   └── trash_service.py                # Cascata lógica na lixeira (soft delete e restore)
│   │   └── routers/
│   │       └── studies.py                      # Endpoint POST /api/studies/{study_id}/move e query atualizada
│   ├── migrations/versions/
│   │   └── 0006_add_study_hierarchy_and_position.py # Migração Alembic para colunas e índices
│   └── tests/
│       ├── test_study_hierarchy.py             # Testes de ordenação, aninhamento, DAG e limite 5 níveis
│       └── test_trash.py                       # Testes de soft delete em cascata pai/filhos
│
└── frontend/
    ├── src/
    │   ├── types.ts                            # Adicionar parent_study_id, position, StudyTreeNode, StudyMovePayload
    │   ├── composables/
    │   │   └── useStudyHierarchy.ts            # Lógica reativa: árvore hierárquica, drag-and-drop, DAG check
    │   └── components/
    │       └── views/
    │           ├── StudyTreeView.vue           # Refatoração com nós recursivos, drag handles e drop zones
    │           └── StudyTreeNodeItem.vue       # Componente atômico recursivo de nó da árvore com ações móveis
    └── tests/
        └── study-tree.test.mjs                 # Testes unitários de renderização, aninhamento e acessibilidade
```

**Structure Decision**: Aplicação Web Full-Stack existente (`caderno-leitura-0.1`), mantendo a separação limpa entre backend Python/FastAPI e frontend Vue 3/TypeScript.

---

## Complexity Tracking

> Nenhuma violação aos princípios da Constituição detectada. Arquitetura enxuta, sem adição de dependências externas.
