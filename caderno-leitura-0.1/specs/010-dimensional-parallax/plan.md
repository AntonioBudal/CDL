# Implementation Plan: 010 — Dimensional: Superclasse Cinemática & Profunda (3D Parallax Espacial)

**Branch**: `010-dimensional-parallax` | **Date**: 2026-09-19 | **Spec**: [specs/010-dimensional-parallax/spec.md](file:///c:/Users/User/caderno/specs/010-dimensional-parallax/spec.md)

**Input**: Feature specification from `/specs/010-dimensional-parallax/spec.md`

## Summary

Implementação da quarta Superclasse de Interface do sistema: **Dimensional** (`.superclass-dimensional`), dotada de cinemática profunda, perspectiva tridimensional (`perspective: 1000px`), tilt 3D microcontrolado com limites estritos (±1.5° em X e ±2.0° em Y), sombras dinâmicas projetadas em perspectiva, relevo interno em camadas (parallax de 1px a 3px) e transição de rotas em aproximação escalar (~300ms).
A arquitetura se integra com o composable existente `useMagneticHover.ts` e preserva 100% da soberania do usuário (24 fontes, 10 temas), mantendo o texto de leitura estritamente estático e o banco de dados intocado.

---

## Technical Context

**Language/Version**: TypeScript 5.7+ / CSS3 / HTML5 / Vue 3 (Composition API)  
**Primary Dependencies**: Vue 3 (`vue`, `vue-router`), Vite, Tailwind/CSS custom properties  
**Storage**: `localStorage` no cliente (`caderno.aparencia.v2` com `superclass: 'dimensional'`, zero impacto no backend)  
**Testing**: Node test runner (`node --test tests/superclasses.test.mjs`), `vue-tsc -b` e `vite build`  
**Target Platform**: Desktop e Mobile locais (Windows / Edge / Chrome / Firefox / Safari)  
**Project Type**: Web Application Frontend  
**Performance Goals**: 60fps constantes acelerados por hardware GPU (`transform: perspective(...) rotateX(...) rotateY(...) translate3d(...)` e `box-shadow`)  
**Constraints**:
1. *Fronteira Estática*: Soberania do usuário preservada em tipografia, cores e densidade.
2. *Limites Físicos Estritos*: Tilt 3D delimitado em `rotateX` máximo de ±1.5° e `rotateY` de ±2.0° para evitar vertigem ou aspecto de vitrine comercial.
3. *Isolamento de Leitura*: `.markdown-content` 100% imóvel (`transform: none !important; animation: none !important;`).
4. *Acessibilidade Universal*: `prefers-reduced-motion: reduce` e `data-motion="off"` neutralizam todos os tilts 3D, rotações e aproximações Z (`--sc-intensity: 0.0 !important; transform: none !important;`).
5. *Zero Impacto no Banco*: 100% frontend; o banco de dados `caderno.db` e o backend não são modificados.

**Scale/Scope**: Folha modular CSS dedicada (`styles/superclasses/dimensional.css`), import em `style.css` e testes unitários em `superclasses.test.mjs`.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Artigo Constitucional | Avaliação | Justificativa / Evidência |
|---|---|---|
| **I. Proteção do Acervo e Privacidade** | **PASS** | A feature reside estritamente no frontend. Nenhum dado do acervo é lido ou transmitido. |
| **II. Isolamento de Testes** | **PASS** | Testes executam isoladamente em memória pelo test runner do Node sem tocar no `caderno.db`. |
| **III. Fidelidade Arquitetural** | **PASS** | Mantém Vue 3, TypeScript estrito, Vite e estilos modulares. |
| **IV. Governança Spec-Driven** | **PASS** | Ciclo formal de especificação e planejamento seguido rigorosamente. |
| **V. Resiliência Operacional e Banco** | **PASS** | Nenhuma migração ou alteração no SQLite. |

---

## Project Structure

### Documentation (this feature)

```text
specs/010-dimensional-parallax/
├── spec.md                  # Especificação funcional e requisitos
├── checklists/
│   └── requirements.md      # Checklist de qualidade (16/16)
├── plan.md                  # Plano técnico de implementação (este arquivo)
├── research.md              # Decisões arquiteturais e resolução de incógnitas
├── data-model.md            # Mapeamento de entidades, tokens e diagrama de estados
├── quickstart.md            # Roteiro de validação e testes
├── contracts/               # Contratos formais de interface
│   └── dimensional-tokens.contract.md
└── tasks.md                 # Fase 2: decomposição de tarefas (via /speckit-tasks)
```

### Source Code Layout

```text
caderno-leitura-0.1/
├── frontend/
│   ├── src/
│   │   ├── styles/
│   │   │   ├── superclasses/
│   │   │   │   ├── zero-g.css        # Superclasse Zero-G
│   │   │   │   ├── mecanica.css      # Superclasse Mecânica
│   │   │   │   ├── invisivel.css     # Superclasse Invisível
│   │   │   │   └── dimensional.css   # [NEW] Superclasse Dimensional
│   │   │   └── style.css             # [MODIFY] Import de dimensional.css
│   │   └── App.vue                   # Transição de rota integrada
│   └── tests/
│       └── superclasses.test.mjs     # [MODIFY] Testes de tokens, tilt 3D e paralaxe
```

**Structure Decision**: 
A Superclasse Dimensional segue o padrão modular estabelecido por `zero-g.css`, `mecanica.css` e `invisivel.css`. Ela aproveita os seletores existentes e o composable `useMagneticHover` já presente nos cartões de livro para aplicar a física tridimensional sem redundância de código.

---

## Complexity Tracking

> Nenhuma violação constitucional identificada. Arquitetura segue estritamente os princípios de design do projeto.
