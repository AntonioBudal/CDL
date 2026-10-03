# Implementation Plan: Responsividade Mobile, Toque Nativo e Micro-Toast de Ferramentas

**Branch**: `051-mobile-toque-microtoast` | **Date**: 2026-10-03 | **Spec**: [specs/051-mobile-toque-microtoast/spec.md](spec.md)

**Input**: Feature specification from `specs/051-mobile-toque-microtoast/spec.md`

---

## Summary

Esta feature entrega melhorias na ergonomia de toque e no leitor em dispositivos móveis. Aprimora o composable `useTextSelection.ts` para detecção confiável de duplo toque para seleção instantânea de palavras; refatora `FloatingActionsToolbar.vue` para exibir exclusivamente ícones puros de 44x44px no celular (ocultando legendas de texto sem comprometer a acessibilidade); e cria o mecanismo de micro-toast flutuante (`useFloatingToast.ts` integrado em `StudyView.vue`), que exibe confirmações rápidas ("Destaque aplicado", "Trecho ocultado") no topo da aba de leitura por 1.8 segundos com fade suave de 250ms e `pointer-events: none`.

---

## Technical Context

**Language/Version**: TypeScript 5.8 / Vue 3.5 (Composition API `<script setup>`)  
**Primary Dependencies**: Vue Router 4, Vite 6, CSS Design Tokens do Leitorum  
**Storage**: N/A (Feature 100% de interação e apresentação de interface, sem persistência ou migrações adicionais)  
**Testing**: Node test runner (`node --test`), Vitest / JSDOM (`npm test`), `vue-tsc -b` (`npm run build`)  
**Target Platform**: Navegadores móveis (Safari iOS, Chrome Android) e desktop moderno  
**Project Type**: Web Application SPA  
**Performance Goals**: Tempo de resposta do duplo toque < 50ms, transições de fade a 60 FPS  
**Constraints**: Alvos de toque de no mínimo 44x44px (WCAG 2.1 Critério 2.5.5), `pointer-events: none` no micro-toast, sem dependências externas  
**Scale/Scope**: 1 composable novo (`useFloatingToast.ts`), 1 composable aprimorado (`useTextSelection.ts`), 1 componente refatorado (`FloatingActionsToolbar.vue`), 1 view integrada (`StudyView.vue`), testes de unidade e integração  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Descrição | Status | Justificativa |
|---|---|---|---|
| **I. Proteção do Acervo** | Privacidade de dados do acervo | **PASS** | Interação e UI puras, zero leitura ou transmissão de dados privados. |
| **II. Isolamento de Testes** | Zero impacto no banco de produção | **PASS** | Testes rodam isolados no frontend sem tocar em `caderno.db`. |
| **III. Fidelidade Arquitetural** | Vue 3, TypeScript estrito, `<script setup>` | **PASS** | Segue a arquitetura existente sem adicionar bibliotecas externas. |
| **IV. Governança por SDD** | Spec Kit formal, 1 Feature = 1 Commit | **PASS** | Ciclo formal para a Feature 051. |
| **V. Resiliência Operacional** | Estabilidade de runtime | **PASS** | Sem impacto no backend ou em bancos de dados. |

---

## Project Structure

### Documentation (this feature)

```text
specs/051-mobile-toque-microtoast/
├── spec.md              # Especificação de requisitos e cenários
├── plan.md              # Este plano de implementação
├── research.md          # Decisões arquiteturais consolidadas
├── data-model.md        # Modelos e tipagens TypeScript
├── quickstart.md        # Guia de validação executável
├── checklists/
│   └── requirements.md  # Checklist de qualidade da especificação
└── contracts/
    ├── floating-toast.md # Contrato do micro-toast flutuante
    └── mobile-toolbar.md # Contrato visual dos botões da barra mobile
```

### Source Code (repository layout)

```text
caderno-leitura-0.1/
└── frontend/
    ├── src/
    │   ├── components/
    │   │   └── FloatingActionsToolbar.vue    # Botões mobile apenas com ícones de 44x44px
    │   ├── composables/
    │   │   ├── useTextSelection.ts           # Suporte a seleção de palavra por duplo toque
    │   │   └── useFloatingToast.ts           # Composable reativo para emissão do micro-toast
    │   └── views/
    │       └── StudyView.vue                 # Integração do micro-toast no topo do leitor
    └── tests/
        ├── mobile_touch_selection.test.mjs   # Testes da lógica de duplo toque e tolerância a scroll
        └── floating_toast.test.mjs           # Testes da máquina de estados do micro-toast
```

---

## Complexity Tracking

*Nenhuma violação aos princípios da Constituição foi identificada.*
