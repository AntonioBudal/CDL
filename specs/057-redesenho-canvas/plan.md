# Implementation Plan: F 0.7.8 — Redesenho do Canvas: Espaço Livre de Pensamento e Criação Espacial

**Branch**: `057-redesenho-canvas` | **Date**: 2026-10-04 | **Spec**: [specs/057-redesenho-canvas/spec.md](spec.md)

**Input**: Feature specification from `specs/057-redesenho-canvas/spec.md`

---

## Summary

Evolução da `StudyCanvasView.vue` para uma mesa espacial completa de pensamento livre, permitindo criação direta de cartões com duplo clique no espaço 2D, criação e movimentação solidária de Molduras Temáticas (Frames) com agrupamento de cartões, conexões direcionadas integradas com o repositório de relações semânticas, alinhamento magnético inteligente (Smart Guides) com alcance de $\pm 10$px, mini-mapa interativo reativo e ergonomia mobile com botões táteis de 44×44px.

---

## Technical Context

**Language/Version**: Python 3.13 (Backend) | TypeScript 5.6+, Vue 3.5+ (Frontend)  
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0, Vite, Lucide Vue Next, Tailwind/CSS Custom Tokens  
**Storage**: SQLite local (WAL mode), tabelas existentes `study_canvas_nodes`, `canvas_frames`, `study_relations` e `studies`  
**Testing**: `node --test` / `npm test` (Frontend), `pytest` (Backend)  
**Target Platform**: Windows local (PowerShell, browser desktop e mobile via rede privada)  
**Project Type**: Web Application (FastAPI REST backend + Vue 3 SPA frontend)  
**Performance Goals**: 60 fps contínuo durante pan, zoom e arrasto de múltiplos nós/molduras com até 50 elementos em tela  
**Constraints**: Zero impacto estrutural no banco de dados ativo (sem novas migrações), isolamento de dados de teste via `tmp_path`, alvos táteis mínimos de 44×44px no mobile, acessibilidade WCAG 2.2  
**Scale/Scope**: Operação no livro ou capítulo ativo, com persistência debounce de 500ms para nós e sincronização imediata para molduras  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Princípio I (Preservação de Dados e Privacidade)**: Nenhuma anotação pessoal ou conteúdo de estudos reais é exibido ou versionado. Todos os testes utilizam dados sintéticos.
- [x] **Princípio II (Integridade do Banco e Isolamento)**: Nenhuma alteração direta no banco `backend/data/caderno.db`. Todas as tabelas necessárias (`study_canvas_nodes`, `canvas_frames`, `study_relations`) já existem. Testes automatizados executam isoladamente em `tmp_path`.
- [x] **Princípio III (Fidelidade Arquitetural e Tecnológica)**: Stack oficial respeitada (Python 3.13, FastAPI, Vue 3 Composition API `<script setup>`, TypeScript estrito, SQLite local).
- [x] **Princípio IV (Governança por Especificação Delimitada)**: Ciclo formal Spec Kit seguido à risca (Specify → Clarify → Plan → Tasks → Analyze → Implement).
- [x] **Princípio V (Resiliência Operacional e Transações)**: Sem migrações de schema necessárias para esta feature. Persistência em lote com transações seguras no backend.

**Resultado do Gate**: APROVADO (100% em conformidade com a Constituição).

---

## Project Structure

### Documentation (this feature)

```text
specs/057-redesenho-canvas/
├── spec.md              # Especificação de requisitos e cenários de aceite
├── plan.md              # Este plano técnico de implementação
├── research.md          # Pesquisa técnica e consolidação das decisões D1 a D5
├── data-model.md        # Entidades, campos, diagramas ER e estados da mesa espacial
├── quickstart.md        # 5 cenários de validação fim a fim executáveis
├── contracts/           # Contratos de componentes Vue, composables e API REST
│   └── canvas-contracts.md
└── checklists/          # Checklists de qualidade
    └── requirements.md
```

### Source Code (repository root)

```text
caderno-leitura-0.1/
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   │   ├── canvas.py             # Endpoints existentes de nós e molduras do canvas
│   │   │   ├── studies.py            # Criação rápida de estudos
│   │   │   └── study_relations.py    # Conexões direcionadas
│   │   └── schemas/
│   │       ├── canvas.py             # Schemas de frames e batch updates
│   │       └── study_relation.py     # Schemas de relações
│   └── tests/
│       └── test_canvas_api.py        # Testes de integração de canvas e frames
└── frontend/
    ├── src/
    │   ├── components/
    │   │   └── views/
    │   │       ├── StudyCanvasView.vue       # Superfície principal do Canvas
    │   │       └── canvas/
    │   │           ├── CanvasToolbar.vue     # Seletor de ferramentas e zoom
    │   │           ├── CanvasNode.vue        # Cartão espacial com alça de conexão
    │   │           ├── CanvasFrameNode.vue   # Moldura retangular temática
    │   │           ├── CanvasMinimap.vue     # Mini-mapa interativo
    │   │           └── CanvasConnectionsLayer.vue # Camada de arestas vetoriais
    │   ├── composables/
    │   │   ├── useCanvasNodes.ts             # Gestão de cartões e sincronização
    │   │   ├── useCanvasFrames.ts            # Gestão e movimento solidário de molduras
    │   │   ├── useCanvasViewport.ts          # Controle de pan e zoom
    │   │   ├── useCanvasConnections.ts       # Arestas curvas e badges
    │   │   └── useSmartSnapping.ts           # Algoritmo de guias magnéticas (Novo)
    │   └── types.ts                          # Tipos TypeScript do Canvas
    └── tests/
        ├── canvas-nodes.test.mjs             # Testes de posicionamento de cartões
        ├── canvas-frames.test.mjs            # Testes de molduras e movimento solidário
        ├── canvas-snapping.test.mjs          # Testes de Smart Guides (Novo)
        └── study_canvas_view.test.mjs        # Testes de interface da view completa (Novo)
```

---

## Complexity Tracking

*Nenhuma violação identificada. O design reutiliza integralmente a infraestrutura de dados existente e introduz composables puros e componentes focados.*
