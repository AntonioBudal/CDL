# Implementation Plan: 009 — Invisível: Superclasse Silenciosa & Editorial e Limpeza de Ajustes

**Branch**: `009-invisivel-editorial` | **Date**: 2026-09-19 | **Spec**: [specs/009-invisivel-editorial/spec.md](file:///c:/Users/User/caderno/specs/009-invisivel-editorial/spec.md)

**Input**: Feature specification from `/specs/009-invisivel-editorial/spec.md`

## Summary

Implementação da Superclasse de Interface **Invisível** (`.superclass-invisivel`), com estética editorial, desmaterialização de caixas e bordas rígidas, microinterações horizontais de leitura (`translateX(4px)` e sublinhado progressivo) e transição de rota em cascata temporal (*staggered fade-up*).
Em conjunto com a nova superclasse, o plano executa a **limpeza e simplificação do frontend**, removendo do painel de Ajustes os campos e grupos obsoletos de estilo de caixas (`style`), contraste de cartões (`surface`) e preenchimento de botões (`button-style`), cujas responsabilidades foram integralmente absorvidas pelas Superclasses Físicas. A soberania de tipografia (24 fontes), temas cromáticos (10 paletas), alinhamento e densidade permanece intocada.

---

## Technical Context

**Language/Version**: TypeScript 5.7+ / CSS3 / HTML5 / Vue 3 (Composition API)  
**Primary Dependencies**: Vue 3 (`vue`, `vue-router`), Vite, Tailwind/CSS custom properties  
**Storage**: `localStorage` no cliente (`caderno.aparencia.v2` com migração transparente e tolerante a dados legados, zero impacto no backend)  
**Testing**: Node test runner (`node --test tests/superclasses.test.mjs`), `vue-tsc -b` e `vite build`  
**Target Platform**: Desktop e Mobile locais (Windows / Edge / Chrome / Firefox / Safari)  
**Project Type**: Web Application Frontend  
**Performance Goals**: 60fps constantes acelerados por GPU (`transform`, `opacity`), transição de rota em cascata em 120ms  
**Constraints**:
1. *Fronteira Estática*: Soberania do usuário preservada em tipografia, cores e densidade.
2. *Isolamento de Leitura*: `.markdown-content` 100% imóvel (`transform: none !important; animation: none !important;`).
3. *Acessibilidade Universal*: `prefers-reduced-motion: reduce` e `data-motion="off"` neutralizam todos os deslocamentos e cascatas (`--sc-intensity: 0.0 !important;`).
4. *Zero Regressão de Dados*: Usuários com chaves antigas de `style`, `surface` e `button-style` continuam com seus temas e fontes preservados sem falha de parsing.
5. *Zero Impacto no Banco*: 100% frontend; o banco de dados `caderno.db` e o backend não são modificados.

**Scale/Scope**: Folha modular CSS dedicada (`styles/superclasses/invisivel.css`), refatoração de `appearance-bootstrap.js`, `appearance.d.ts` e `AppearanceControls.vue`.

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
specs/009-invisivel-editorial/
├── spec.md                  # Especificação funcional e requisitos
├── checklists/
│   └── requirements.md      # Checklist de qualidade (16/16)
├── plan.md                  # Plano técnico de implementação (este arquivo)
├── research.md              # Decisões arquiteturais e resolução de incógnitas
├── data-model.md            # Mapeamento de entidades, tokens e diagrama de estados
├── quickstart.md            # Roteiro de validação e testes
├── contracts/               # Contratos formais de interface
│   ├── invisivel-tokens.contract.md
│   └── appearance-pruning.contract.md
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
│   │   │   │   └── invisivel.css     # [NEW] Superclasse Invisível
│   │   │   └── style.css             # [MODIFY] Import de invisivel.css
│   │   ├── appearance-bootstrap.js   # [MODIFY] Remoção de style, surface, button-style e normalização defensiva
│   │   ├── appearance.d.ts           # [MODIFY] Atualização tipada de AppearancePreferences
│   │   ├── components/
│   │   │   └── AppearanceControls.vue # [MODIFY] Remoção de campos e grupos órfãos
│   │   └── App.vue                   # Transição de rota integrada
│   └── tests/
│       └── superclasses.test.mjs     # [MODIFY] Testes de tokens da Invisível e catálogo podado
```

**Structure Decision**: 
A Superclasse Invisível segue o mesmo padrão modular de `zero-g.css` e `mecanica.css`. A poda de campos obsoletos de aparência é realizada diretamente na fonte (`appearance-bootstrap.js` e `appearance.d.ts`), garantindo propagação reativa automática para `AppearanceControls.vue`.

---

## Complexity Tracking

> Nenhuma violação constitucional identificada. Arquitetura segue estritamente os princípios de design do projeto.
