# Implementation Plan: F0.9.02 — Ergonomia Mobile e Descongestionamento da Página do Livro

**Branch**: `083-ergonomia-mobile-pagina-livro` | **Date**: 2026-10-21 | **Spec**: [specs/083-ergonomia-mobile-pagina-livro/spec.md](./spec.md)

**Input**: Feature specification from `specs/083-ergonomia-mobile-pagina-livro/spec.md`

---

## Summary

Esta feature constitui a segunda fatia de engenharia da versão **0.9 — Revisão Geral de UI/UX, Ergonomia e Estabilização**, focando no redesenho e descongestionamento ergonômico da página do livro ([`BookView.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/views/BookView.vue)):
1. **Cabeçalho Condensado no Mobile:** Redução da altura vertical ocupada pelo cabeçalho em dispositivos móveis (`<= 767px`) através de uma estrutura de linha dupla (capa miniatura de 48x72px, título clamp 2 linhas, categorias compactas e menu de ações agrupadas via `DropdownMenu.vue`), liberando mais de 300px na primeira dobra da tela.
2. **Unificação da Faixa de Capítulos:** Supressão da esteira horizontal de pílulas roláveis duplicada no mobile, preservando exclusivamente um seletor unificado de capítulos com altura e alvos de toque adequados (>= 44x44px) e suporte a inserção rápida de capítulo inline.
3. **Inspetor Analítico Recolhível por Padrão no Celular:** Transformação da barra inferior estática em um painel colapsável sob demanda com alternador acessível WAI-ARIA (`:aria-expanded`), liberando a rolagem do rodapé exclusivamente para a leitura dos estudos.
4. **Preservação Integral do Desktop:** A rica arquitetura horizontal em 3 faixas empilhadas já consolidada permanece 100% preservada e intacta para viewports `>= 768px`.

---

## Technical Context

**Language/Version**: TypeScript 5.6+ / Vue 3.5 (Composition API, `<script setup>`), Node.js 20+  
**Primary Dependencies**: Vue Router 4, `DropdownMenu.vue` existente, `CategoryBadge.vue`, `BookCover.vue`, Lucide icons via `Icon.vue`  
**Storage**: N/A (zero alterações no backend FastAPI ou schema SQLite)  
**Testing**: `node:test` (Node test runner nativo) em `tests/` com assertions estritas  
**Target Platform**: Navegadores mobile modernos (iOS Safari, Android Chrome) e desktop (Chrome, Edge, Firefox, Safari)  
**Project Type**: Aplicação Web local-first (código em `caderno-leitura-0.1/frontend/`)  
**Performance Goals**: Tempo de renderização da primeira dobra < 100ms, transição de capítulos fluida a 60 FPS, zero layout shift (CLS < 0.05)  
**Constraints**: Zero emojis no código e documentação; conformidade estrita aos 10 temas oficiais sem cores hexadecimais fixas; alvos táteis mínimos de 44x44px; respeito à Constituição do projeto  
**Scale/Scope**: 1 view refatorada (`caderno-leitura-0.1/frontend/src/views/BookView.vue`), integração de `DropdownMenu.vue`, 1 suíte de testes unitários nova (`feature-083-book-mobile-layout.test.mjs`)  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **I. Proteção Absoluta do Acervo e Privacidade de Dados**: Nenhum dado do acervo do usuário ou do banco de dados `backend/data/caderno.db` é lido, modificado ou exposto.
- [x] **II. Isolamento Estrito de Testes e Operações Locais**: Testes unitários do frontend executam puramente em memória com o Node test runner, sem tocar o banco ativo.
- [x] **III. Fidelidade Arquitetural e Tecnológica**: Uso rigoroso da stack definida (Vue 3, TypeScript, CSS semântico com Superclasses e variáveis CSS), sem dependências externas volumosas.
- [x] **IV. Governança por Especificação Delimitada (Spec-Driven Development)**: Feature concebida e delimitada através do ciclo formal do Spec Kit, sem avanço não planejado.
- [x] **V. Resiliência Operacional, Transações e Migrações Seguras**: Zero alterações no schema de dados; banco de produção permanece intocado.

---

## Project Structure

### Documentation (this feature)

```text
specs/083-ergonomia-mobile-pagina-livro/
├── spec.md                  # Especificação funcional e histórias de usuário
├── checklists/
│   └── requirements.md      # Validação de qualidade da especificação
├── plan.md                  # Este plano de implementação técnica
├── research.md              # Pesquisa técnica e decisões consolidadas (Fase 0)
├── data-model.md            # Mapeamento de entidades e estados reativos (Fase 1)
├── quickstart.md            # Guia de validação automatizada e teste manual (Fase 1)
├── contracts/
│   └── book-mobile-layout.contract.md # Contratos de composição de interface (Fase 1)
└── tasks.md                 # Decomposição em tarefas (Fase 2 - gerado via /speckit-tasks)
```

### Source Code Layout

```text
caderno-leitura-0.1/
└── frontend/
    ├── src/
    │   ├── views/
    │   │   └── BookView.vue              # Refatoração do cabeçalho, capítulos e inspetor
    │   └── components/
    │       ├── ui/
    │       │   ├── DropdownMenu.vue      # Reutilização para ações agrupadas do livro
    │       │   └── Icon.vue              # Ícones de ação e alternância
    │       └── BookCover.vue             # Miniatura da capa no mobile
    └── tests/
        ├── book-horizontal-layout.test.mjs        # Suíte de regressão desktop existente
        └── feature-083-book-mobile-layout.test.mjs # Nova suíte de testes unitários mobile
```

**Structure Decision**: A implementação concentra-se em [`BookView.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/views/BookView.vue), modularizando a apresentação de estilos responsivos sob `@media (max-width: 767px)` e integrando o componente [`DropdownMenu.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/components/ui/DropdownMenu.vue) já auditado. A suíte de testes existente (`book-horizontal-layout.test.mjs`) continuará garantindo a estabilidade desktop enquanto a nova suíte (`feature-083-book-mobile-layout.test.mjs`) audita o comportamento móvel.

---

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*Nenhuma violação identificada. O design respeita 100% dos princípios constitucionais e limites de escopo da versão 0.9.*
