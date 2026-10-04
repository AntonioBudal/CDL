# Implementation Plan: F 0.7.9 — Refinamento do Editor de Estudos e Correção de Ícones de Categorias

**Branch**: `058-refinamento-editor` | **Date**: 2026-10-04 | **Spec**: [specs/058-refinamento-editor/spec.md](spec.md)

**Input**: Feature specification from `specs/058-refinamento-editor/spec.md`

---

## Summary

Aprimorar a experiência de escrita e edição de estudos no Desktop e Mobile através de:
1. Navegação flexível por abas/seções individuais com opção de modo contínuo em `StudyEditorFields.vue`, reduzindo a rolagem vertical no mobile em mais de 60%.
2. Pré-visualização instantânea in-place do Markdown em cada seção ("Editar / Prévia") via biblioteca `markdown-it`.
3. Ergonomia tátil com alvos $\ge 44 \times 44$px na `MarkdownToolbar.vue` e atalhos de teclado universais (`Ctrl+B`, `Ctrl+I`, `Ctrl+K`).
4. Rede de segurança de dados com persistência volátil em `sessionStorage` e restauração automática com banner discreto de descarte.
5. Padronização definitiva de ícones em `CategoryBadge.vue` e `CategoryInput.vue` utilizando o componente oficial `<Icon.vue>`.

---

## Technical Context

**Language/Version**: TypeScript 5.6+, Vue 3.5+ (Composition API, `<script setup>`), Python 3.13 (FastAPI/pytest).  
**Primary Dependencies**: Vue 3, `markdown-it` (renderização e sanitização de HTML), `lucide-vue-next` via `Icon.vue`.  
**Storage**: `sessionStorage` (armazenamento volátil em sessão do rascunho de digitação); API REST SQLite (persistência definitiva).  
**Testing**: `node:test` + `node:assert/strict` (frontend); `pytest` (backend); `vue-tsc -b && vite build` (tipagem estrita).  
**Target Platform**: Desktop (Windows/Mac/Linux) e Mobile/Touch (iOS/Android/Tailscale).  
**Project Type**: Web Application SPA local (FastAPI + Vue 3).  
**Performance Goals**: Alternância de abas e modo de prévia Markdown instantâneos (< 16ms, 60fps), sem layout thrashing.  
**Constraints**: Preservação estrita de `useUnsavedChanges`; zero alterações no banco SQLite (`caderno.db`); conformidade WAI-ARIA com navegação por teclado e alvos táteis mínimos de 44px.  
**Scale/Scope**: 5 componentes de frontend (`StudyEditView.vue`, `StudyEditorFields.vue`, `MarkdownToolbar.vue`, `CategoryInput.vue`, `CategoryBadge.vue`) e 1 novo composable (`useStudyDraft.ts`).

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio Constitucional | Status | Justificativa / Verificação |
|---|---|---|
| **I. Proteção do Acervo e Privacidade** | **PASS** | Nenhum dado real é exposto; testes utilizam dados sintéticos. O salvamento em `sessionStorage` é volátil no navegador local do leitor. |
| **II. Isolamento de Testes e Operações** | **PASS** | Zero impacto no banco ativo `caderno.db`. Testes usam `tmp_path` e portas efêmeras. |
| **III. Fidelidade Arquitetural** | **PASS** | Stack estrita respeitada (Vue 3, TypeScript, `markdown-it`, SQLite inalterado). |
| **IV. Governança por Spec Kit** | **PASS** | Ciclo formal de especificações e planejamento em execução (`speckit-plan`). |
| **V. Resiliência Operacional e Transações** | **PASS** | Nenhuma migração de banco é necessária. |

---

## Project Structure

### Documentation (this feature)

```text
specs/058-refinamento-editor/
├── plan.md              # Este plano de implementação
├── research.md          # Decisões técnicas (D1 a D5)
├── data-model.md        # Entidade de rascunho e máquina de estados
├── quickstart.md        # 5 cenários de validação fim a fim
├── contracts/           # Contratos de componentes e composables
│   └── editor-contracts.md
└── tasks.md             # Tarefas geradas pelo /speckit-tasks
```

### Source Code (repository layout)

```text
caderno-leitura-0.1/frontend/
├── src/
│   ├── types.ts                                # Tipos de rascunho de estudo
│   ├── composables/
│   │   ├── useStudyDraft.ts                    # Composable de sessionStorage e auto-restore
│   │   └── useStudyEdit.ts                     # Estado de edição do estudo
│   ├── components/
│   │   ├── StudyEditorFields.vue               # Abas, foco, prévia in-place e modo contínuo
│   │   ├── MarkdownToolbar.vue                 # Alvos móveis 44px e atalhos de teclado
│   │   ├── CategoryInput.vue                   # Autocomplete com Icon.vue padronizado
│   │   └── CategoryBadge.vue                   # Badges com Icon.vue 'x' centralizado
│   └── views/
│       └── StudyEditView.vue                   # Integração do banner de rascunho e salvamento
└── tests/
    ├── study-edit.test.mjs                     # Testes de edição e rascunho de sessão
    ├── markdown-toolbar.test.mjs               # Testes de formatação e atalhos
    └── category_input.test.mjs                 # Testes de ícones e acessibilidade
```

**Structure Decision**: Aplicação SPA web em `caderno-leitura-0.1/frontend/`. Nenhuma alteração no backend é necessária.

---

## Complexity Tracking

> **Nenhuma violação constitucional.** Arquitetura limpa orientada a componentes Vue e composables desacoplados.
