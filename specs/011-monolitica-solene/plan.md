# Implementation Plan: 011 — Monolítica: Superclasse Pesada & Solene (Brutalista & Arquitetura em Pedra)

**Branch**: `011-monolitica-solene` | **Date**: 2026-09-19 | **Spec**: [specs/011-monolitica-solene/spec.md](file:///c:/Users/User/caderno/specs/011-monolitica-solene/spec.md)

**Input**: Feature specification from `/specs/011-monolitica-solene/spec.md`

## Summary

Implementação da quinta e última Superclasse de Interface do sistema: **Monolítica** (`.superclass-monolitica`), concebida sob princípios de arquitetura brutalista, blocos prismáticos densos, cantos estritamente retos (`border-radius: 0px !important`), ausência total de sombras flutuantes (`box-shadow: none !important`), microinterações com preenchimento ponderado (~380ms) e inversão de alto contraste no active, transições de rota solenes (dissolução lapidar) e blindagem rigorosa do leitor.
A arquitetura preserva 100% da soberania do usuário (24 fontes, 10 temas), mantém o texto de leitura estritamente imóvel e o banco de dados intocado.

---

## Technical Context

**Language/Version**: TypeScript 5.7+ / CSS3 / HTML5 / Vue 3 (Composition API)  
**Primary Dependencies**: Vue 3 (`vue`, `vue-router`), Vite, Tailwind/CSS custom properties  
**Storage**: `localStorage` no cliente (`caderno.aparencia.v2` com `superclass: 'monolitica'`, zero impacto no backend)  
**Testing**: Node test runner (`node --test tests/superclasses.test.mjs`), `vue-tsc -b` e `vite build`  
**Target Platform**: Desktop e Mobile locais (Windows / Edge / Chrome / Firefox / Safari / Dispositivos E-Ink)  
**Project Type**: Web Application Frontend  
**Performance Goals**: 60fps constantes acelerados por hardware GPU com renderização otimizada para alto contraste e telas de baixa taxa de atualização (E-Ink)  
**Constraints**:
1. *Fronteira Estática*: Soberania do usuário preservada em tipografia, cores e densidade.
2. *Geometria Prismática Pura*: Cantos estritamente retos (`border-radius: 0px`) em todos os recipientes e botões.
3. *Supressão de Sombras*: `box-shadow: none !important` em repouso e interações; peso demarcado por bordas sólidas (`calc(var(--border-width, 1px) + 1px)`).
4. *Isolamento de Leitura*: `.markdown-content` 100% imóvel (`transform: none !important; animation: none !important;`).
5. *Acessibilidade Universal*: `prefers-reduced-motion: reduce` e `data-motion="off"` convertem todas as transições ponderadas em cortes imediatos (`0ms`).
6. *Zero Impacto no Banco*: 100% frontend; o banco de dados `caderno.db` e o backend não são modificados.

**Scale/Scope**: Folha modular CSS dedicada (`styles/superclasses/monolitica.css`), import em `style.css` e testes unitários em `superclasses.test.mjs`.

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
specs/011-monolitica-solene/
├── spec.md                  # Especificação funcional e requisitos
├── checklists/
│   └── requirements.md      # Checklist de qualidade (16/16)
├── plan.md                  # Plano técnico de implementação (este arquivo)
├── research.md              # Decisões arquiteturais e resolução de incógnitas
├── data-model.md            # Mapeamento de entidades, tokens e diagrama de estados
├── quickstart.md            # Roteiro de validação e testes
├── contracts/               # Contratos formais de interface
│   └── monolitica-tokens.contract.md
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
│   │   │   │   ├── dimensional.css   # Superclasse Dimensional
│   │   │   │   └── monolitica.css    # [NEW] Superclasse Monolítica
│   │   │   └── style.css             # [MODIFY] Import de monolitica.css
│   │   └── App.vue                   # Transição de rota integrada
│   └── tests/
│       └── superclasses.test.mjs     # [MODIFY] Testes de tokens, cantos retos e transições solenes
```

**Structure Decision**: 
A Superclasse Monolítica segue o mesmo padrão modular desacoplado estabelecido por `zero-g.css`, `mecanica.css`, `invisivel.css` e `dimensional.css`. Ela atua exclusivamente via regras CSS puras ativadas no elemento ancestral `:is(:root[data-superclass="monolitica"], .superclass-monolitica)`.

---

## Complexity Tracking

> Nenhuma violação constitucional identificada. Arquitetura segue estritamente os princípios de design do projeto.
