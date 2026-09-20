# Implementation Plan: F06 — Painéis Redimensionáveis

**Branch**: `018-paineis-redimensionaveis` | **Date**: 2026-09-19 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/018-paineis-redimensionaveis/spec.md`

## Summary

Implementar a infraestrutura de painéis laterais ajustáveis e redimensionáveis (*split panes*) no Caderno de Leitura, articulando a área de trabalho em três colunas no desktop (Navegador à esquerda, Palco Principal ao centro e Inspetor de Contexto à direita) com barras divisoras interativas (`SplitGutter`), controle por teclado acessível, persistência híbrida em `localStorage` e adaptação ergonômica para gavetas deslizantes em tablets e smartphones.

---

## Technical Context

**Language/Version**: TypeScript 5.8+ (Strict Mode), Vue 3.5+ (Composition API, `<script setup>`), CSS3 Moderno (Custom Properties, Flexbox, Container Queries).  
**Primary Dependencies**: `vue`, `vue-router`, `lucide-vue-next` (adotada na F09 para ícones sóbrios). Zero novas bibliotecas externas.  
**Storage**: `localStorage` (chaves `caderno_pane_sizes_global` e `caderno_pane_sizes_book_{id}`). Zero impacto no SQLite.  
**Testing**: Node.js test runner nativo (`node --test`), com suites para `useSplitPanes.ts` e renderização de layout.  
**Target Platform**: Navegadores modernos (Desktop Windows/macOS/Linux, Tablets, Mobile iOS/Android via rede local ou Tailscale).  
**Project Type**: Web Application Frontend (FastAPI serve o build estático `dist/`).  
**Performance Goals**: Redimensionamento fluido a 60fps sem repaints excessivos do DOM (atualização de CSS custom properties durante o arrasto).  
**Constraints**: Área útil mínima do palco de leitura garantida em >= 360px; limites de painéis entre 240px e 600px; neutralização de seleção de texto durante o arrasto.  
**Scale/Scope**: Componente modular reutilizável aplicado prioritariamente em `BookView.vue` e `StudyView.vue`.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Proteção Absoluta do Acervo e Privacidade de Dados**: ✅ Aprovado. A funcionalidade manipula exclusivamente a geometria visual do cliente e chaves de layout em `localStorage`. Não lê, não transmite e não altera registros do acervo do usuário.
- **II. Isolamento Estrito de Testes**: ✅ Aprovado. Testes automatizados do frontend utilizam mocks em memória e runner do Node.js, sem tocar no banco ativo `backend/data/caderno.db`.
- **III. Fidelidade Arquitetural e Tecnológica**: ✅ Aprovado. Implementação 100% nativa em Vue 3 + TypeScript com `<script setup>`, sem bibliotecas externas pesadas e com total respeito ao motor de temas e Superclasses.
- **IV. Governança por Especificação Delimitada (Spec-Driven Development)**: ✅ Aprovado. A feature cumpre o ciclo rigoroso (`specify` → `clarify` → `plan` → `tasks` → `implement`).
- **V. Resiliência Operacional**: ✅ Aprovado. Zero impacto estrutural no banco de dados SQLite ou nas rotinas de backup.

---

## Project Structure

### Documentation (this feature)

```text
specs/018-paineis-redimensionaveis/
├── spec.md              # Especificação de requisitos e cenários
├── checklists/
│   └── requirements.md  # Checklist de qualidade da especificação
├── plan.md              # Este plano técnico de implementação
├── research.md          # Decisões arquiteturais (PointerEvents, Acessibilidade, Persistência)
├── data-model.md        # Entidades TypeScript e estrutura do localStorage
├── contracts/
│   └── ui-components.md # Contratos de props, emits, slots e WAI-ARIA
├── quickstart.md        # Guia de validação ponta a ponta
└── tasks.md             # Tarefas de implementação (gerado pelo /speckit-tasks)
```

### Source Code (repository root)

```text
caderno-leitura-0.1/frontend/
├── src/
│   ├── types.ts                                  # Interfaces PaneConfig, PaneState, SplitLayoutDimensions
│   ├── composables/
│   │   └── useSplitPanes.ts                      # Composable de geometria, arrasto e persistência híbrida
│   ├── components/
│   │   └── layout/
│   │       ├── SplitLayout.vue                   # Contêiner geral das 3 colunas e gavetas mobile
│   │       ├── SplitPane.vue                     # Painel individual colapsável
│   │       └── SplitGutter.vue                   # Barra divisora arrastável com WAI-ARIA separator
│   └── views/
│       ├── BookView.vue                          # Integração do SplitLayout na visão do livro
│       └── StudyView.vue                         # Integração opcional do SplitLayout na leitura de estudos
└── tests/
    └── split-panes.test.mjs                      # Testes unitários do composable e cálculo de limites
```

---

## Complexity Tracking

*Nenhuma violação constitucional detectada. Solução 100% nativa sem dependências adicionais.*
