# Implementation Plan: Hierarquia e Ergonomia de Header Actions no Leitor

**Branch**: `050-ergonomia-header-actions` | **Date**: 2026-10-03 | **Spec**: [specs/050-ergonomia-header-actions/spec.md](spec.md)

**Input**: Feature specification from `specs/050-ergonomia-header-actions/spec.md`

---

## Summary

Esta feature reestrutura a arquitetura visual e a ergonomia do cabeçalho de estudos em `StudyView.vue`. No Desktop, introduz distinção nítida entre a ação primária de edição (`Editar estudo` em destaque), a ação de colaboração (`Compartilhar`) e reúne as ferramentas secundárias (`Histórico de versões`, `Exportar estudo`, `Mover para a lixeira`) em um componente modular `DropdownMenu.vue` acessível via `•••`. No Mobile, unifica as ações em exatamente uma linha horizontal sem quebras, garante alvos de toque mínimos de 44x44px e substitui a trilha de breadcrumbs por um botão inteligente `← Voltar ao capítulo`.

---

## Technical Context

**Language/Version**: TypeScript 5.8 / Vue 3.5 (Composition API `<script setup>`)  
**Primary Dependencies**: Vue Router 4, Vite 6, Design Tokens CSS e Superclasses Cinemáticas existentes  
**Storage**: N/A (Feature 100% de interface do usuário, sem persistência ou migrações adicionais)  
**Testing**: Vitest, `@vue/test-utils`, `jsdom` (`npm test`)  
**Target Platform**: Desktop (Chrome, Edge, Firefox, Safari) e Dispositivos Móveis (Safari iOS, Chrome Android)  
**Project Type**: Single Page Application (SPA Web)  
**Performance Goals**: Zero Cumulative Layout Shift (CLS = 0), transições de abertura do dropdown em menos de 16ms (60 FPS)  
**Constraints**: Área de toque mínima de 44x44px no mobile (WCAG 2.1 Critério 2.5.5), suporte a WAI-ARIA Menu com navegação circular por teclado, sem dependências externas adicionais  
**Scale/Scope**: 1 componente novo (`DropdownMenu.vue`), 1 view refatorada (`StudyView.vue`), testes de componente e regressão  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Descrição | Status | Justificativa |
|---|---|---|---|
| **I. Proteção do Acervo** | Privacidade absoluta e não violação de dados do usuário | **PASS** | Não lê, expõe ou altera conteúdo privado nem banco de dados. |
| **II. Isolamento de Testes** | Zero impacto no banco ativo local (`caderno.db`) | **PASS** | Testes executam 100% em memória no JSDOM via Vitest. |
| **III. Fidelidade Arquitetural** | Vue 3, TypeScript estrito, `<script setup>`, CSS Tokens | **PASS** | Componente segue padrão do design system sem bibliotecas externas. |
| **IV. Governança por SDD** | Fatias verificáveis via Spec Kit, 1 Feature = 1 Commit | **PASS** | Executando ciclo formal `speckit.plan` para a feature 050. |
| **V. Resiliência Operacional** | Não afetar estabilidade do servidor ou banco | **PASS** | Sem alterações no backend ou em migrações Alembic. |

---

## Project Structure

### Documentation (this feature)

```text
specs/050-ergonomia-header-actions/
├── spec.md              # Especificação de requisitos e cenários
├── plan.md              # Este plano de implementação
├── research.md          # Pesquisa técnica e decisões arquiteturais consolidadas
├── data-model.md        # Modelos de dados e interfaces TypeScript
├── quickstart.md        # Guia de validação executável
├── checklists/
│   └── requirements.md  # Checklist de qualidade da especificação
└── contracts/
    ├── dropdown-menu.md # Contrato do componente DropdownMenu.vue
    └── study-header.md  # Contrato do cabeçalho do leitor StudyView.vue
```

### Source Code (repository layout)

```text
caderno-leitura-0.1/
└── frontend/
    ├── src/
    │   ├── components/
    │   │   └── ui/
    │   │       └── DropdownMenu.vue       # Novo componente de menu suspenso reutilizável
    │   └── views/
    │       └── StudyView.vue              # Cabeçalho reestruturado (desktop & mobile)
    └── tests/
        ├── dropdown_menu.test.ts          # Testes unitários de acessibilidade e interação
        └── study_header_actions.test.ts   # Testes de integração do cabeçalho em StudyView
```

---

## Complexity Tracking

*Nenhuma violação aos princípios da Constituição foi identificada. O design preserva a simplicidade, elimina duplicação e utiliza apenas as capacidades nativas do Vue 3 e CSS.*
