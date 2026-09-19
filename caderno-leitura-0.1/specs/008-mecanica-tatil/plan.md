# Implementation Plan: 008 — Mecânica: Superclasse Tátil & Responsiva

**Branch**: `008-mecanica-tatil` | **Date**: 2026-09-19 | **Spec**: [specs/008-mecanica-tatil/spec.md](file:///c:/Users/User/caderno/specs/008-mecanica-tatil/spec.md)

**Input**: Feature specification from `/specs/008-mecanica-tatil/spec.md`

## Summary

Implementação da Superclasse Física **Mecânica** (`.superclass-mecanica`), que introduz um arquétipo tátil, rígido e de resposta ultrarrápida inspirado em teclados mecânicos e painéis de instrumentos industriais.
A implementação estabelece um sistema de tokens físicos com cantos quase retos (`2px`), sombras duras e sem difusão (*solid offset*), animação de *push-down* linear no estado `:active` (com cancelamento exato da sombra para criar a ilusão de fim de curso em batente mecânico), inputs escavados com sombra interna *inset*, chaves seletoras (*switches*) com estalo elétrico de 60ms e transição de rotas Vue Router de corte seco em 100ms.
A soberania do usuário é rigorosamente preservada: nenhuma variável de tipografia, cor, contraste ou densidade de leitura é alterada.

---

## Technical Context

**Language/Version**: TypeScript 5.7+ / CSS3 / HTML5 / Vue 3 (Composition API)  
**Primary Dependencies**: Vue 3 (`vue`, `vue-router`), Vite, Tailwind/CSS custom properties  
**Storage**: N/A (preferência persistida localmente via `localStorage` através do composable `useAppearanceSettings`, sem impacto no backend)  
**Testing**: Node test runner (`node --test tests/superclasses.test.mjs`), `vue-tsc -b` e `vite build`  
**Target Platform**: Desktop e Mobile locais (Windows / Edge / Chrome / Firefox / Safari)  
**Project Type**: Web Application Frontend  
**Performance Goals**: 60fps garantidos por aceleração de GPU (`will-change: transform`), tempo de resposta de 100ms para botões e 60ms para switches, transições de rota em 100ms  
**Constraints**:
1. *Fronteira Estática*: NUNCA sobrescrever variáveis de tipografia (24 fontes), cores (10 temas), densidade de leitura ou layout base.
2. *Isolamento de Leitura*: `.markdown-content` 100% imóvel em qualquer situação (`transform: none !important; animation: none !important;`).
3. *Zero Idle / Zero Magnetismo*: Proibida qualquer oscilação em repouso (*idle breathing*) ou perseguição magnética de cursor.
4. *Acessibilidade Inegociável*: Sob `prefers-reduced-motion: reduce` ou `data-motion="off"`, `--sc-intensity: 0.0 !important;` e deslocamentos desativados.
5. *Zero Impacto no Banco*: 100% frontend; nenhum arquivo de backend ou banco de dados é modificado.

**Scale/Scope**: Módulo CSS dedicado (`styles/superclasses/mecanica.css`) aplicado sistemicamente a botões, cartões, formulários, caixas de ajustes, modais, switches e transição de páginas.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Artigo Constitucional | Avaliação | Justificativa / Evidência |
|---|---|---|
| **I. Proteção do Acervo e Privacidade** | **PASS** | A feature reside puramente na camada de apresentação CSS/Vue do frontend. Nenhum dado do usuário ou do acervo é acessado. |
| **II. Isolamento de Testes** | **PASS** | Os testes unitários do frontend executam de maneira isolada em memória, sem conectar ao `caderno.db`. |
| **III. Fidelidade Arquitetural** | **PASS** | Respeita a pilha tecnológica do frontend (Vue 3, TypeScript, Vite, CSS modular). |
| **IV. Governança Spec-Driven** | **PASS** | Ciclo formal seguido (`specify` $\to$ `plan` $\to$ `tasks` $\to$ `analyze` $\to$ `implement`). |
| **V. Resiliência Operacional e Banco** | **PASS** | Nenhuma alteração no SQLite ou nas migrações do Alembic. |

---

## Project Structure

### Documentation (this feature)

```text
specs/008-mecanica-tatil/
├── spec.md                  # Especificação funcional e requisitos
├── checklists/
│   └── requirements.md      # Validação formal de requisitos (16/16)
├── plan.md                  # Plano técnico de implementação (este arquivo)
├── research.md              # Decisões arquiteturais e resolução de incógnitas
├── data-model.md            # Mapeamento de entidades, tokens e diagrama de estados
├── quickstart.md            # Guia de validação automatizada e cenários manuais
├── contracts/               # Contratos formais de interface
│   ├── mecanica-tokens.contract.md
│   └── page-transitions.contract.md
└── tasks.md                 # Fase 2: decomposição ordenada de tarefas (gerado via /speckit-tasks)
```

### Source Code Layout

```text
caderno-leitura-0.1/
├── frontend/
│   ├── src/
│   │   ├── styles/
│   │   │   ├── superclasses/
│   │   │   │   ├── base.css          # Variáveis estruturais de intensidade e escopo base
│   │   │   │   ├── zero-g.css        # Superclasse Zero-G existente
│   │   │   │   └── mecanica.css      # [NEW] Superclasse Mecânica
│   │   │   └── style.css             # Import central de folhas de estilo
│   │   └── App.vue                   # Transição de rota <Transition name="page">
│   └── tests/
│       └── superclasses.test.mjs     # [MODIFY] Testes de tokens, push-down e regras da Mecânica
```

**Structure Decision**: 
A Superclasse Mecânica é implementada como folha de estilo CSS modular em `frontend/src/styles/superclasses/mecanica.css`, isolada da Zero-G, permitindo manutenção independente e sem acoplamento.

---

## Complexity Tracking

> Nenhuma violação constitucional identificada. Arquitetura segue estritamente os padrões modulares estabelecidos na Feature 007.
