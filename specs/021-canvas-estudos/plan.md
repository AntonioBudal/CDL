# Implementation Plan: F03 — Canvas de Estudos

**Branch**: `021-canvas-estudos` | **Date**: 2026-09-19 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/021-canvas-estudos/spec.md`

---

## Summary

Implementação do espaço bidimensional livre e infinito (Canvas 2D) para exploração espacial do conhecimento no Caderno de Leitura, permitindo navegação contínua por deslocamento (pan) e aproximação (zoom fluido com limites de 0.25x a 2.0x), posicionamento livre de cards de estudos com persistência isolada na tabela `study_canvas_nodes` (sem alterar a hierarquia ou capítulos canônicos), seleção simples e em bloco por área retangular (*marquee*), mini-mapa radar de orientação topológica com teletransporte e função "Ajustar à Tela" (*Fit to View*), algoritmo de auto-grid ordenado por capítulo para novos estudos e ergonomia tátil para dispositivos móveis com alvos mínimos de 44x44px.

---

## Technical Context

**Language/Version**: Python 3.13 de 64 bits (backend) / TypeScript 5+ com Vue 3 (Composition API, `<script setup>`) no frontend.  
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0, Alembic, Uvicorn, Vite, Lucide Vue Next / Icon.vue, Reatividade nativa do Vue 3.  
**Storage**: SQLite local em modo WAL com chaves estrangeiras ativas (`PRAGMA foreign_keys = ON`).  
**Testing**: pytest com SQLite em bancos efêmeros em `tmp_path` (backend); `node:test` / Vitest (frontend).  
**Target Platform**: Windows 11 local (desktops, laptops e navegadores de dispositivos móveis via rede local/Tailscale).  
**Project Type**: Aplicação web local full-stack única (FastAPI servindo API REST e interface empacotada Vite).  
**Performance Goals**: Taxa de quadros contínua a 60fps em pan e zoom; latência de ponteiro < 16ms; persistência em lote com debounce de 300ms; cálculo de Bounding Box em < 50ms para até 100 cards.  
**Constraints**: 
- Isolamento absoluto: nunca ler ou modificar o banco ativo `backend/data/caderno.db`.
- Desacoplamento entre espaço e semântica: mover cards no canvas jamais altera `parent_study_id`, `position` ou capítulos na tabela `studies`.
- Zero dependências pesadas externas para o canvas (sem D3, Three.js ou PixiJS). Matemática matricial pura em TypeScript com CSS Transforms (`translate3d` + `scale`).
- Alvos de toque de no mínimo 44x44px em resoluções móveis.
- Respeito à preferência de movimento reduzido (`prefers-reduced-motion`).
**Scale/Scope**: Pranchas com até 100 estudos por livro; coordenadas mundiais contínuas; suporte integrado desktop e smartphone.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [X] **I. Proteção Absoluta do Acervo e Privacidade de Dados**: Nenhum dado do acervo real é lido ou exposto. O conteúdo e a integridade de `studies` permanecem intocados; coordenadas são mantidas em tabela auxiliar `study_canvas_nodes`.
- [X] **II. Isolamento Estrito de Testes e Operações Locais**: Testes executam exclusivamente contra bancos SQLite efêmeros em diretórios temporários (`tmp_path`), sem disputar portas e sem tocar no banco ativo.
- [X] **III. Fidelidade Arquitetural e Tecnológica**: Python 3.13, FastAPI, SQLAlchemy 2.0, Alembic, Vue 3, TS estrito, Vite e SQLite local.
- [X] **IV. Governança por Especificação Delimitada (SDD)**: Ciclo formal rigoroso (`specify` -> `clarify` -> `plan` -> `tasks` -> `analyze` -> `implement`).
- [X] **V. Resiliência Operacional e Migrações Seguras**: Migração `0007_add_study_canvas_nodes.py` limpa, idempotente, com chaves estrangeiras com `CASCADE` e restrição única `(study_id, book_id)`.

---

## Project Structure

### Documentation (this feature)

```text
specs/021-canvas-estudos/
├── spec.md              # Especificação formal aprovada
├── checklists/
│   └── requirements.md  # Checklist de qualidade (16/16 aprovado)
├── plan.md              # Este plano de implementação
├── research.md          # Decisões técnicas e arquiteturais consolidadas
├── data-model.md        # Modelos relacionais, entidades e validações
├── contracts/
│   └── study-canvas-api.yaml # Contrato OpenAPI para API do Canvas
├── quickstart.md        # Guia executável de testes e validação
└── tasks.md             # Tarefas atômicas (geradas pelo /speckit-tasks)
```

### Source Code Impacted

```text
caderno-leitura-0.1/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   ├── __init__.py                     # Exportar StudyCanvasNode
│   │   │   └── study_canvas_node.py            # Novo modelo StudyCanvasNode
│   │   ├── schemas/
│   │   │   └── study_canvas_node.py            # Schemas Pydantic de entrada e saída
│   │   ├── services/
│   │   │   └── canvas_service.py               # Lógica de persistência, batch upsert e isolamento
│   │   ├── routers/
│   │   │   └── canvas.py                       # Rotas GET/PUT /api/books/{id}/canvas e PATCH /api/studies/{id}/canvas
│   │   └── main.py                             # Registrar router de canvas
│   ├── migrations/versions/
│   │   └── 0007_add_study_canvas_nodes.py      # Migração Alembic para tabela study_canvas_nodes
│   └── tests/
│       └── test_canvas_api.py                  # Testes da API de persistência espacial e concorrência
│
└── frontend/
    ├── src/
    │   ├── types.ts                            # Tipos StudyCanvasNode, CanvasViewportState, CanvasBoundingBox
    │   ├── api.ts                              # Métodos de API para o Canvas
    │   ├── composables/
    │   │   ├── useCanvasViewport.ts            # Gestão de coordenadas de mundo/tela, pan, zoom e fitToView
    │   │   └── useCanvasNodes.ts               # Auto-grid, arrasto, seleção simples/marquee e batch sync
    │   └── components/
    │       └── views/
    │           ├── StudyCanvasView.vue         # Contêiner principal do Canvas com aceleração GPU
    │           └── canvas/
    │               ├── CanvasNode.vue          # Card de estudo posicionado no mundo com drag handle
    │               ├── CanvasToolbar.vue       # Barra de ferramentas flutuante de zoom e controles
    │               └── CanvasMinimap.vue       # Mini-mapa radar de navegação e teletransporte
    └── tests/
        ├── canvas-viewport.test.mjs            # Testes de matemática de coordenadas e zoom
        ├── canvas-auto-grid.test.mjs           # Testes do algoritmo de auto-grid por capítulo
        └── canvas-selection.test.mjs           # Testes de seleção simples, marquee e arrasto em bloco
```

**Structure Decision**: Aplicação Web Full-Stack existente (`caderno-leitura-0.1`), preservando a separação estrita entre backend FastAPI e frontend Vue 3/TypeScript.

---

## Complexity Tracking

> Nenhuma violação aos princípios da Constituição detectada. Arquitetura enxuta, sem dependências externas pesadas (sem D3 ou PixiJS), mantendo 60fps via aceleração nativa por CSS Transforms e GPU.
