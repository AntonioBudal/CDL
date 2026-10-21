# Implementation Plan: F0.9.01 — Arquitetura de Navegação Global e Shell Responsivo

**Branch**: `082-navegacao-global-shell-responsivo` | **Date**: 2026-10-20 | **Spec**: [specs/082-navegacao-global-shell-responsivo/spec.md](spec.md)

**Input**: Feature specification from `specs/082-navegacao-global-shell-responsivo/spec.md`

---

## Summary

Esta feature constitui a primeira fatia de engenharia da versão **0.9 — Revisão Geral de UI/UX, Ergonomia e Estabilização**, focando na consolidação e estabilidade do *App Shell* do Leitorum:
1. **Unificação da Barra Desktop (`NavigationTabs.vue`):** Desacopla a exibição das abas primárias da preferência inicial `homeViewPreference`. As abas "Dashboard" (rota `/dashboard`) e "Livros" (rota `/livros`) passam a coexistir permanentemente na barra de navegação desktop, garantindo que o acervo nunca fique inacessível ou oculto em 1 clique.
2. **Eliminação de Sobreposição na Base Móvel (`App.vue` / `MobileTabBar.vue`):** Aplicação de espaçamento inferior compensatório centralizado (`--mobile-nav-offset` + safe-area) para o rodapé e conteúdos de páginas roláveis no celular, prevenindo que o rodapé global e ações de formulário fiquem ocultos sob a barra fixa de 5 abas.
3. **Padronização Universal de Trilhas de Navegação (`AppBreadcrumb.vue`):** Criação de um componente acessível (WCAG AA, HTML5 semântico com `<ol>`/`<li>`, `aria-label` e `aria-current="page"`) em `components/ui/AppBreadcrumb.vue`, substituindo as marcações ad-hoc e corrigindo links para a raiz `/` em `BookView.vue`, `StudyView.vue`, `StudyEditView.vue` e `UserProfileView.vue`.
4. **Remoção de Duplicação de Gatilhos Móveis (`GlobalHeader.vue`):** Eliminação do elemento residual `.mobile-more-trigger` no cabeçalho superior que estava ocultado via CSS forçado, consolidando o menu "Mais" exclusivamente como o 5º botão da barra inferior móvel.

---

## Technical Context

**Language/Version**: TypeScript 5.3+ / Node.js 20+ (frontend), Python 3.13 (backend inalterado)  
**Primary Dependencies**: Vue 3.4+ (Composition API, `<script setup>`), Vue Router 4, Pinia  
**Storage**: Nenhuma alteração no banco de dados SQLite. Preferências de leitura/navegação persistidas no `localStorage`  
**Testing**: Node.js Test Runner nativo (`node --test`), `vue-tsc -b && vite build` para validação de tipos e compilação  
**Target Platform**: Navegadores modernos (Desktop Chrome/Firefox/Edge/Safari e Mobile Web iOS/Android)  
**Project Type**: Aplicação Web local-first (código-fonte em `caderno-leitura-0.1/frontend/`)  
**Performance Goals**: Alternância de rotas instantânea (< 100ms), taxa de quadros estável a 60 FPS, zero *layout thrashing*  
**Constraints**: Zero emojis em código e documentação; conformidade estrita aos 10 temas canônicos sem cores hexadecimais fixas; alvos táteis mínimos de 44x44px; respeito à Constituição do projeto  
**Scale/Scope**: 5 componentes de interface refatorados/criados (`NavigationTabs.vue`, `App.vue`, `GlobalHeader.vue`, `AppBreadcrumb.vue`, `types/navigation.ts`), 4 views atualizadas (`BookView.vue`, `StudyView.vue`, `StudyEditView.vue`, `UserProfileView.vue`), 1 suíte de testes unitários nova  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Princípio I (Privacidade e Acervo)**: APROVADO. A feature lida exclusivamente com componentes de layout, navegação e casca de aplicação. Nenhum dado do acervo real do usuário é lido, exibido, resumido ou transmitido.
- **Princípio II (Isolamento de Testes)**: APROVADO. Os testes automatizados da feature operam em memória e sobre componentes estáticos, sem tocar no banco de dados ativo `backend/data/caderno.db`.
- **Princípio III (Fidelidade Arquitetural)**: APROVADO. Mantém a stack canônica (Vue 3, TypeScript estrito, Vite) sem adição de novas dependências de terceiros.
- **Princípio IV (Governança e SDD)**: APROVADO. Execução estrita do ciclo Spec Kit com branch dedicada `082-navegacao-global-shell-responsivo` e política 1 Feature = 1 Commit.
- **Princípio V (Resiliência e Segurança)**: APROVADO. Não há modificações em modelos de banco, migrações de dados ou arquivos de infraestrutura.

*Gate Status: 100% Aprovado sem violações.*

---

## Project Structure

### Documentation (this feature)

```text
specs/082-navegacao-global-shell-responsivo/
├── plan.md              # Este arquivo (plano técnico de implementação)
├── spec.md              # Especificação de requisitos funcionais e histórias de usuário
├── research.md          # Diagnóstico técnico, perguntas e decisões arquiteturais
├── data-model.md        # Tipos TypeScript de navegação e matriz de mapeamento
├── quickstart.md        # Roteiro de validação automatizada e teste manual
├── contracts/
│   └── navigation-shell.contract.md # Contratos do AppBreadcrumb e variáveis de offset
└── checklists/
    └── requirements.md  # Checklist de conformidade e qualidade de requisitos
```

### Source Code (repository root)

```text
caderno-leitura-0.1/
└── frontend/
    ├── src/
    │   ├── types/
    │   │   ├── index.ts                     # Re-export de tipos
    │   │   └── navigation.ts                # Tipos BreadcrumbItem, PrimaryNavItem, etc.
    │   ├── components/
    │   │   ├── layout/
    │   │   │   ├── GlobalHeader.vue         # Poda de gatilho móvel duplicado
    │   │   │   └── NavigationTabs.vue       # Inclusão simultânea de Dashboard e Livros
    │   │   └── ui/
    │   │       └── AppBreadcrumb.vue        # Novo componente unificado de breadcrumbs
    │   ├── views/
    │   │   ├── BookView.vue                 # Adoção de AppBreadcrumb
    │   │   ├── StudyView.vue                # Adoção de AppBreadcrumb
    │   │   ├── StudyEditView.vue            # Adoção de AppBreadcrumb
    │   │   └── UserProfileView.vue          # Adoção de AppBreadcrumb
    │   └── App.vue                          # Regra de offset para rodapé mobile
    └── tests/
        └── feature-082-navigation-shell.test.mjs # Teste unitário e de regressão
```

---

## Phase 0: Research & Decisions

1. **Abas Primárias Coexistentes:** A lista `primaryNavItems` em `NavigationTabs.vue` agora contém explicitamente Dashboard, Livros, Destaques, Revisão e Inbox. A chave `homeViewPreference` afeta unicamente o destino do clique na logo e o redirecionamento inicial.
2. **Offset Dinâmico Centralizado:** O rodapé `.app-footer` em `App.vue` recebe `margin-bottom: calc(var(--mobile-nav-offset, 56px) + env(safe-area-inset-bottom, 0px) + 1.5rem)` em `@media (max-width: 767px)` para contas autenticadas.
3. **AppBreadcrumb Semântico:** Implementado com `<ol>` ordenado e `aria-current="page"`, truncando rótulos longos com reticências e garantindo que o primeiro nível direcione confiavelmente para `/livros`.
4. **Poda de Código Morto:** O elemento `.mobile-more-trigger` em `GlobalHeader.vue` é removido, unificando a abertura do menu "Mais" na `MobileTabBar.vue`.

---

## Phase 1: Design & Contracts

- Contrato de dados e tipagem formalizado em [`data-model.md`](data-model.md).
- Contratos de interface e acessibilidade definidos em [`contracts/navigation-shell.contract.md`](contracts/navigation-shell.contract.md).
- Roteiro de validação e testes documentado em [`quickstart.md`](quickstart.md).

*Re-avaliação Constitucional pós-design: APROVADO.*
