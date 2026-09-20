# Implementation Plan: F01 — Sistema de Visualizações e Dashboard Responsivo

**Branch**: `019-sistema-visualizacoes` | **Date**: 2026-09-19 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/019-sistema-visualizacoes/spec.md`

## Summary

Implementar a infraestrutura de modos de visualização intercambiáveis no Caderno de Leitura (**Grade**, **Lista**, **Árvore**, **Mapa** e **Canvas**) com uma barra de controle de visualizações (`ViewSwitcher`) acessível e ergonômica, preservação do estudo em foco, persistência híbrida em `localStorage` e reajuste responsivo do Dashboard no celular (grade de métricas em 2 colunas, auto-scroll do mapa de calor para a semana atual e botões táteis de 44x44px).

---

## Technical Context

**Language/Version**: TypeScript 5.8+ (Strict Mode), Vue 3.5+ (Composition API, `<script setup>`), CSS3 Moderno (Custom Properties, Flexbox, CSS Grid).  
**Primary Dependencies**: `vue`, `vue-router`, `lucide-vue-next`. Zero novas dependências externas.  
**Storage**: `localStorage` (chaves `caderno_default_view` e `caderno_preferred_view_{bookId}`). Zero impacto no SQLite ativo.  
**Testing**: Runner nativo do Node.js (`node --test`), com suíte unitária para `useViewPreference.ts` e renderers de visualização.  
**Target Platform**: Navegadores modernos (Desktop Windows/macOS/Linux, Tablets, Mobile iOS/Android via rede local ou Tailscale).  
**Project Type**: Web Application Frontend (FastAPI serve os arquivos estáticos compilados em `dist/`).  
**Performance Goals**: Alternância de visualizações em < 100ms a 60fps sem congelamentos do DOM; auto-scroll suave do mapa de calor no mobile.  
**Constraints**: Área de toque tátil mínima de 44x44px; preservação estrita do estudo em foco (`activeStudyId`).  
**Scale/Scope**: 5 renderers modulares integrados em `BookView.vue` e refinamentos responsivos em `DashboardView.vue` e `HeatmapCalendar.vue`.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Proteção Absoluta do Acervo e Privacidade de Dados**: ✅ Aprovado. A funcionalidade manipula exclusivamente renderização de dados já existentes na memória do cliente e preferências de visualização em `localStorage`. Zero leitura, resumo ou envio de dados privados para fora do ambiente local.
- **II. Isolamento Estrito de Testes**: ✅ Aprovado. Testes do frontend utilizam o runner do Node.js com mocks em memória, sem tocar no banco ativo `backend/data/caderno.db`.
- **III. Fidelidade Arquitetural e Tecnológica**: ✅ Aprovado. Solução 100% nativa em Vue 3 + TypeScript estrito com `<script setup>`, sem bibliotecas pesadas de terceiros e com total respeito ao motor de temas e Superclasses.
- **IV. Governança por Especificação Delimitada (Spec-Driven Development)**: ✅ Aprovado. A feature cumpre o ciclo formal (`specify` → `clarify` → `plan` → `tasks` → `analyze` → `implement`).
- **V. Resiliência Operacional**: ✅ Aprovado. Zero impacto estrutural no banco de dados SQLite ou nas rotinas de backup.

---

## Project Structure

### Documentation (this feature)

```text
specs/019-sistema-visualizacoes/
├── spec.md              # Especificação de requisitos e cenários
├── checklists/
│   └── requirements.md  # Checklist de qualidade da especificação (100% aprovado)
├── plan.md              # Este plano técnico de implementação
├── research.md          # Decisões técnicas e arquitetura dos renderers
├── data-model.md        # Tipos TypeScript e persistência no localStorage
├── contracts/
│   └── ui-components.md # Contratos de props, emits e acessibilidade WAI-ARIA
├── quickstart.md        # Roteiro de validação ponta a ponta
└── tasks.md             # Tarefas de implementação (gerado pelo /speckit-tasks)
```

### Source Code (repository root)

```text
caderno-leitura-0.1/frontend/
├── src/
│   ├── types.ts                                  # Tipos StudyViewMode, StudyViewOption, ViewPreferenceState
│   ├── composables/
│   │   └── useViewPreference.ts                  # Composable reativo de visualizações e persistência híbrida
│   ├── components/
│   │   ├── HeatmapCalendar.vue                   # Auto-scroll no mobile para data atual e refinamentos táteis
│   │   └── views/
│   │       ├── ViewSwitcher.vue                  # Barra seletora de visualizações com role="tablist"
│   │       ├── StudyGridView.vue                 # Renderer: Modo Grade
│   │       ├── StudyListView.vue                 # Renderer: Modo Lista
│   │       ├── StudyTreeView.vue                 # Renderer: Modo Árvore
│   │       ├── StudyMapView.vue                  # Renderer: Modo Mapa
│   │       └── StudyCanvasView.vue               # Renderer: Modo Canvas
│   └── views/
│       ├── BookView.vue                          # Integração do ViewSwitcher e renderers no palco central
│       └── DashboardView.vue                     # Grid responsivo de 2 colunas e botões táteis no celular
└── tests/
    └── study-views.test.mjs                      # Testes unitários do composable e do seletor
```

---

## Complexity Tracking

*Zero violações constitucionais detectadas. Solução nativa modular sem adição de pacotes externos.*
