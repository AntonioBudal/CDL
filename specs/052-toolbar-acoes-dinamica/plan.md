# Implementation Plan: F 0.7.3 — Refatoração Dinâmica da Floating Actions Toolbar

**Branch**: `052-toolbar-acoes-dinamica` | **Date**: 2026-10-03 | **Spec**: [specs/052-toolbar-acoes-dinamica/spec.md](spec.md)

**Input**: Feature specification from `/specs/052-toolbar-acoes-dinamica/spec.md`

## Summary

Refatorar o componente `FloatingActionsToolbar.vue` e desacoplar formulários de anotação e perguntas em um popover contextual independente (`NoteQuestionPopover.vue`). A interação é reorganizada em duas camadas limpas: Camada de Ação Imediata (1 clique via Split Button com memorização no `localStorage`, oclusão rápida e cópia de citação) e Camada de Detalhe Ancorada (popover focado com atalhos `Enter` para salvar e `Escape` para cancelar, com recolhimento temporário da régua de botões e ancoragem adaptativa a `window.visualViewport` no mobile).

## Technical Context

**Language/Version**: TypeScript 5.8 / Node.js 24 / Vue 3.5 (Composition API, `<script setup>`)

**Primary Dependencies**: Vue 3, Vite 8, CSS nativo / Tailwind Tokens, `@vue/test-utils` / `node:test`

**Storage**: `localStorage` (chave canônica `caderno_last_highlight_color`)

**Testing**: Node Test Runner (`node:test`, `node:assert/strict`), `vue-tsc -b` (tipagem estrita)

**Target Platform**: Navegadores modernos Desktop e Mobile (Chrome, Edge, Firefox, Safari iOS e Android)

**Project Type**: Single-Page Application (Frontend SPA desacoplado)

**Performance Goals**: Posicionamento flutuante em < 16ms (60 fps); aplicação de destaque em < 300ms

**Constraints**:
- Alvos táteis mínimos de 44x44px no mobile (WCAG 2.1 Critério 2.5.5)
- Proteção da viewport móvel contra sobreposição do teclado virtual via `window.visualViewport`
- Régua de botões dimensionalmente estável (sem esticar ou quebrar layout sobre o texto lido)
- Preservação integral dos contratos de persistência de destaques (`/api/studies/{id}/highlights`)

**Scale/Scope**: Módulo de leitura do Caderno de Leitura (`caderno-leitura-0.1/frontend`)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Princípio I (Proteção do Acervo e Privacidade):** PASS — Nenhuma leitura ou transmissão de dados do banco de dados real. Operações limitadas a manipuladores de interface e dados fictícios em testes.
- **Princípio II (Isolamento de Testes):** PASS — Todas as suítes rodam com mocks in-memory no Node test runner sem tocar em arquivos de banco SQLite.
- **Princípio III (Fidelidade Tecnológica):** PASS — Stack estritamente alinhada a Vue 3, TypeScript estrito, Vite e padrões web modernos (DOM Range, Selection, Visual Viewport API).
- **Princípio IV (Governança por Especificação):** PASS — Feature F 0.7.3 seguindo o ciclo delimitado Spec Kit (`specify` → `clarify` → `plan` → `tasks` → `implement`).
- **Princípio V (Resiliência Operacional):** PASS — Fallbacks defensivos caso `localStorage` ou `visualViewport` estejam restritos no navegador.

## Project Structure

### Documentation (this feature)

```text
specs/052-toolbar-acoes-dinamica/
├── plan.md              # Este plano de implementação
├── research.md          # Decisões arquiteturais e padrões de engenharia (Phase 0)
├── data-model.md        # Entidades, tipos e máquinas de estado da toolbar (Phase 1)
├── quickstart.md        # Cenários de validação executáveis (Phase 1)
├── contracts/           # Contratos de componentes e eventos (Phase 1)
│   └── floating-toolbar-events.md
└── tasks.md             # Decomposição em tarefas atômicas (Phase 2 - /speckit-tasks)
```

### Source Code (repository root)

```text
caderno-leitura-0.1/frontend/
├── src/
│   ├── components/
│   │   ├── FloatingActionsToolbar.vue       # Régua de botões em 1 clique (Split Button)
│   │   └── NoteQuestionPopover.vue          # Novo componente: popover/gaveta desacoplada
│   ├── composables/
│   │   ├── useHighlightColorPreference.ts   # Novo composable: persistência da última cor
│   │   └── useTextSelection.ts              # Coleta e manutenção do contexto de seleção
│   ├── utils/
│   │   └── toolbarPosition.ts               # Cálculo de ancoragem e detecção de bordas
│   └── views/
│       └── StudyView.vue                    # Orquestração entre seleção, barra e popover
└── tests/
    └── floating_toolbar_dynamic.test.mjs    # Testes unitários de estados, eventos e atalhos
```

**Structure Decision**: Arquitetura modular no frontend dividindo responsabilidades entre o controle de ação rápida (`FloatingActionsToolbar.vue`), o formulário de redação detalhada (`NoteQuestionPopover.vue`), a gestão de preferências (`useHighlightColorPreference.ts`) e o posicionamento matemático geométrico (`toolbarPosition.ts`).

## Complexity Tracking

Nenhuma violação constitucional identificada. O design desacopla responsabilidades e simplifica o código existente, reduzindo a complexidade ciclomática de `FloatingActionsToolbar.vue`.
