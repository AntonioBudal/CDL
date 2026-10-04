# Implementation Plan: F 0.7.6 — Redesenho da Tree View: Hierarquia Cognitiva e Estruturação de Tópicos

**Branch**: `055-redesenho-tree-view` | **Date**: 2026-10-04 | **Spec**: [specs/055-redesenho-tree-view/spec.md](spec.md)

**Input**: Feature specification from `/specs/055-redesenho-tree-view/spec.md`

---

## Summary

Redesenhar a `StudyTreeView.vue`, o componente filho `StudyTreeNodeItem.vue` e estender o composable `useStudyHierarchy.ts` para consolidar a Tree View como a interface definitiva de **subordinação hierárquica e síntese estrutural**. A entrega introduz:
1. Linhas guias estruturais elegantes em CSS puro conectando ancestrais e descendentes.
2. Controles globais de expansão ("Expandir Todos" e "Recolher Todos") com persistência no `localStorage` e padrão de abertura total inicial.
3. Indicadores de progresso agregado por ramo em micro-badges com fração (`2/4 concluídos`), mini-barra e tooltip detalhado, computando recursivamente todos os descendentes em tempo linear ($O(N)$).
4. Drag-and-drop aprimorado com distinção visual evidente entre inserção linear e aninhamento magnético subordinado, com bloqueio rígido de ciclos e profundidade máxima de 5 níveis.
5. Ergonomia mobile com alvos táteis mínimos de 44×44px e menu touch de ações expressas.

---

## Technical Context

**Language/Version**: TypeScript 5.x / Vue 3.5+ (Composition API, `<script setup>`), Python 3.13 (Backend)  
**Primary Dependencies**: Vue 3, Vue Router, Lucide Icons (`lucide-vue-next`), CSS puro com variáveis canônicas  
**Storage**: `localStorage` no navegador do cliente (chave `caderno_tree_collapsed_${bookId}`); SQLite local no backend (sem migração necessária, reutilizando `parent_study_id`)  
**Testing**: `node --test` para suíte frontend (`study-tree.test.mjs`, `study_tree_view.test.mjs`), `pytest` para backend  
**Target Platform**: Navegadores modernos (Desktop e Mobile responsivo no Windows/Android/iOS via rede local/Tailscale)  
**Project Type**: Aplicação Web híbrida SPA (Vue 3 / Vite) com servidor local FastAPI  
**Performance Goals**: Renderização da árvore em < 50ms para até 100 nós; recálculo de métricas de ramo em < 1ms; ações em lote ("Expandir/Recolher Todos") em < 100ms  
**Constraints**: Alvos de toque de no mínimo 44×44px no mobile (WCAG 2.2); profundidade máxima travada em 5 níveis (índices 0 a 4); conformidade WAI-ARIA Treeview 1.2  
**Scale/Scope**: Até dezenas/centenas de estudos por capítulo em até 5 níveis de aninhamento  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Princípio I (Proteção do Acervo e Privacidade)**: Nenhuma leitura ou vazamento de dados reais de usuários no chat ou código. Testes usam dados sintéticos.
- [x] **Princípio II (Isolamento de Testes)**: Zero impacto no banco de produção `caderno.db`. Testes backend rodam em `tmp_path`.
- [x] **Princípio III (Fidelidade Arquitetural)**: Vue 3 Composition API com TypeScript estrito, sem bibliotecas pesadas de terceiros; backend reutiliza endpoints existentes.
- [x] **Princípio IV (Governança por Especificação Delimitada)**: Ciclo formal Spec Kit respeitado etapa por etapa.
- [x] **Princípio V (Resiliência Operacional e Migrações Seguras)**: Nenhuma migração de banco necessária; modelo de dados preservado.

---

## Project Structure

### Documentation (this feature)

```text
specs/055-redesenho-tree-view/
├── spec.md              # Especificação formal da feature
├── checklists/
│   └── requirements.md  # Checklist de qualidade de requisitos (PASS)
├── plan.md              # Este plano de implementação
├── research.md          # Decisões técnicas e arquiteturais (Phase 0)
├── data-model.md        # Modelagem de dados e cálculo de progresso (Phase 1)
├── contracts/
│   └── study-tree-hierarchy.md # Contratos do composable e componentes (Phase 1)
├── quickstart.md        # Cenários de validação fim a fim (Phase 1)
└── tasks.md             # Tarefas atômicas geradas pelo /speckit-tasks (Phase 2)
```

### Source Code (repository root)

```text
caderno-leitura-0.1/
├── frontend/
│   ├── src/
│   │   ├── types.ts                               # Extensão de StudyTreeNode com BranchProgress
│   │   ├── composables/
│   │   │   └── useStudyHierarchy.ts               # Cálculo de BranchProgress, expandAll, collapseAll, persistência
│   │   └── components/
│   │       └── views/
│   │           ├── StudyTreeView.vue              # Redesenho da visualização em árvore, drag-and-drop e toolbar
│   │           └── StudyTreeNodeItem.vue          # Linhas guias CSS, micro-badges de progresso e alvos de 44px
│   └── tests/
│       ├── study-tree.test.mjs                    # Testes do composable useStudyHierarchy e métricas de progresso
│       └── study_tree_view.test.mjs               # Testes de integração de StudyTreeView e StudyTreeNodeItem
└── backend/
    └── tests/                                     # Suíte existente preservada sem regressão
```

**Structure Decision**: A implementação concentra-se no ecossistema de visualização do frontend Vue 3, preservando estritamente a API backend e o banco SQLite.

---

## Complexity Tracking

> Nenhuma violação constitucional.
