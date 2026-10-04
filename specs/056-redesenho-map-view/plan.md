# Implementation Plan: F 0.7.7 — Redesenho da Map View (Criação e Edição de Grafo Semântico)

**Branch**: `056-redesenho-map-view` | **Date**: 2026-10-04 | **Spec**: [specs/056-redesenho-map-view/spec.md](spec.md)

**Input**: Feature specification from `specs/056-redesenho-map-view/spec.md`

---

## Summary

Evoluir a `StudyMapView.vue` para uma ferramenta viva de pensamento relacional e modelagem argumentativa, implementando:
1. **Layout Radial Concêntrico e Destaque do Estudo Núcleo**: Anéis orbitais concêntricos com estudo focal centralizado em maior escala dimensional e halo luminoso, acompanhado de relaxamento por repulsão suave para evitar sobreposições.
2. **Traçado Interativo de Arestas e Popover de Relação**: Alça conectora nos nós permitindo arrastar linha elástica SVG até o nó de destino, abrindo o mini-popover contextual `MapRelationPopover.vue` com oração semântica ativa, seletor de tipo, botão de inversão de polaridade `⇄` e persistência imediata na API de relações.
3. **Criação Rápida de Estudos In-Place e Ergonomia Mobile**: Duplo clique no canvas ou botão flutuante para abrir o mini-card `MapQuickCreateCard.vue` registrando novo estudo no capítulo sem navegação externa, complementado por modo assistido de toque e alvos de 44×44px no mobile.

---

## Technical Context

**Language/Version**: Python 3.13 (Backend), TypeScript 5.x / Vue 3 Composition API (`<script setup>`) (Frontend)  
**Primary Dependencies**: FastAPI, SQLAlchemy 2, Alembic, Uvicorn, Vue 3, Vite, Lucide Icons  
**Storage**: SQLite local em modo Write-Ahead Logging (WAL) com chaves estrangeiras ativadas (`backend/data/caderno.db` isolado em produção)  
**Testing**: `node --test` nativo no frontend (`npm test`), `pytest` no backend (`tmp_path`)  
**Target Platform**: Windows local (PC loopback + Tailscale mobile)  
**Project Type**: Aplicação Web SPA (Vue 3) servida por API REST FastAPI local  
**Performance Goals**: Renderização a 60 fps em grafos de até 40 nós; latência de criação de estudo in-place < 100ms; resposta de pan/zoom < 16ms  
**Constraints**: Zero mutações não autorizadas em `caderno.db`; isolamento absoluto de dados nos testes; alvos táteis mínimos de 44×44px para WCAG 2.2  
**Scale/Scope**: Mapeamento relacional de estudos por capítulo ou livro  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Princípio I (Preservação de Dados e Privacidade)**: A Map View opera exclusivamente com metadados estruturais e IDs de estudos. Nenhum dado do acervo do usuário é exposto ou transmitido para serviços externos.
- [x] **Princípio II (Isolamento de Testes)**: Nenhuma operação da Map View toca no banco ativo `caderno.db`. Todas as validações automatizadas usam bancos temporários em `tmp_path` e mocks de gateway na suíte de testes.
- [x] **Princípio III (Fidelidade Arquitetural)**: Utiliza estritamente a stack oficial (FastAPI, SQLite WAL, Vue 3 Composition API com TypeScript e Tailwind/CSS tokens).
- [x] **Princípio IV (Spec-Driven Development)**: A feature F 0.7.7 segue o ciclo delimitado Spec Kit com 1 commit atômico final após validação de 100% dos testes.
- [x] **Princípio V (Resiliência Operacional)**: Reutiliza a tabela canônica `study_relations` e endpoints existentes sem exigir migrações destrutivas no banco de dados.

---

## Project Structure

### Documentation (this feature)

```text
specs/056-redesenho-map-view/
├── plan.md                                  # Este documento de planejamento técnico
├── research.md                              # Decisões de design e arquitetura (D1 a D5)
├── data-model.md                            # Modelos de nós, arestas, popover e mini-card
├── quickstart.md                            # Guia de validação dos 5 cenários fim a fim
├── contracts/
│   └── map-graph-contracts.md               # Contratos de componentes, composables e API
├── checklists/
│   └── requirements.md                      # Validação de qualidade da especificação (PASS)
└── tasks.md                                 # Tarefas atômicas geradas pelo /speckit-tasks
```

### Source Code

```text
caderno-leitura-0.1/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── views/
│   │   │       ├── StudyMapView.vue         # Componente principal do mapa redesenhado
│   │   │       └── map/
│   │   │           ├── MapRelationPopover.vue # Mini-popover de relações semânticas
│   │   │           └── MapQuickCreateCard.vue # Mini-card in-place de novo estudo
│   │   ├── composables/
│   │   │   ├── useMapLayout.ts              # Algoritmo de projeção radial e repulsão
│   │   │   └── useStudyRelations.ts         # Integração com API de relações
│   │   └── types.ts                         # Tipos MapNodeItem, MapConnectionEdge, etc.
│   └── tests/
│       └── study_map_view.test.mjs          # Testes unitários de interface e interação
```

**Structure Decision**: A implementação concentra-se no frontend (`StudyMapView.vue`, novos subcomponentes em `views/map/` e composable `useMapLayout.ts`), consumindo os endpoints já existentes de `/api/studies` e `/api/studies/{id}/relations`.

---

## Complexity Tracking

> **Nenhuma violação constitucional.** Arquitetura limpa sem migrações ou dependências externas pesadas.
