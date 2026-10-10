# Implementation Plan: F0.8.01 — Curadoria Editorial, Biblioteca Ativa e Novo Header Global

**Branch**: `065-livros-header` | **Date**: 2026-10-10 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/065-livros-header/spec.md`

---

## Summary

Reestruturar a arquitetura do cabeçalho global do sistema (*App Shell*) em 3 zonas operacionais semanticamente delimitadas (Alternativa A: Marca à esquerda, Navegação Primária com 4 abas + Menu retrátil "Mais ▾" ao centro, e Ferramentas + Dropdown do Usuário à direita com logout seguro encapsulado). Ao mesmo tempo, redesenhar a página de Livros (`/livros`) eliminando a coluna estática lateral de cadastro para expandir o acervo para 100% da largura útil, introduzindo um Hero Card da leitura ativa ("Em Andamento"), um componente acessível e animado de gaveta lateral deslizante (`Drawer.vue`) para cadastro focado de livros, e preservando integralmente os modos de visualização Grade/Lista, filtros por categoria e os 10 temas nativos (imunidade cromática estrita).

---

## Technical Context

**Language/Version**: TypeScript 5.9+ / Node.js 20+ (Frontend) e Python 3.13 (Backend)

**Primary Dependencies**:
- Frontend: Vue 3 (Composition API, `<script setup>`), Vite, Tailwind CSS (classes de utilidade / tokens)
- Backend: FastAPI, SQLAlchemy 2.0 (sem alterações necessárias no backend)

**Storage**: SQLite 3 local com modo WAL (sem alteração no schema)

**Testing**:
- Frontend: `node:test` e `node:assert/strict` via `npm test`
- Build: `npm run build`

**Target Platform**: Windows local (processo único `iniciar.py`) atendendo PC e dispositivos móveis

**Project Type**: Web application local-first (Vue 3 SPA)

**Performance Goals**:
- Transição do Drawer em $\le 220$ms com aceleração GPU (`transform`) a 60 FPS estáveis
- Backdrop suave em $\le 200$ms (`opacity`)
- Hover nos livros em $\le 150$ms
- Comportamento instantâneo (0.01ms) sob `prefers-reduced-motion: reduce`

**Constraints**:
- Imunidade cromática absoluta: consumir exclusivamente as variáveis CSS dos 10 temas existentes (`--color-surface`, `--color-page`, `--color-text`, `--color-border`, etc.)
- Ausência total de cores hexadecimais fixas nos novos estilos
- Ausência total de emojis no frontend (usar ícones SVG do `Icon.vue`)
- Alvos de toque $\ge 44 \times 44$px para resoluções móveis
- Fechamento do Drawer via `Esc`, botão fechar e clique no backdrop
- Foco automático no primeiro campo ao abrir o Drawer e retorno ao botão disparador ao fechar

**Scale/Scope**: Refatoração do `App.vue` (App Shell) e `BooksView.vue`, criação de `GlobalHeader.vue`, `NavigationTabs.vue`, `UserDropdown.vue` e `Drawer.vue`.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Status | Justificativa / Verificação |
|---|---|---|
| **I. Proteção do Acervo e Privacidade** | APROVADO | O redesign preserva 100% dos dados dos livros e não expõe nenhum conteúdo privado de produção. |
| **II. Isolamento Estrito de Testes** | APROVADO | Testes executados exclusivamente na suíte frontend (`npm test`) com mocks e componentes isolados. Nenhuma leitura ou escrita em `caderno.db`. |
| **III. Fidelidade Arquitetural** | APROVADO | Stack oficial mantida (Vue 3, TypeScript estrito, Vite). Não adiciona dependências externas ou bibliotecas pesadas de UI. |
| **IV. Spec-Driven Development (SDD)** | APROVADO | Ciclo de especificação e planejamento formal respeitado antes da implementação. |
| **V. Resiliência e Integridade** | APROVADO | Não há alterações no banco de dados SQLite ou migrações Alembic necessárias. |

---

## Project Structure

### Documentation (this feature)

```text
specs/065-livros-header/
├── spec.md                          # Especificação de requisitos e cenários
├── checklists/
│   └── requirements.md              # Validação de qualidade da especificação
├── research.md                      # Decisões de pesquisa técnica (Phase 0)
├── data-model.md                    # Modelos de dados e contratos de componentes (Phase 1)
├── contracts/
│   └── header-and-books-ui.yaml     # Contratos da interface e endpoints consumidos (Phase 1)
├── quickstart.md                    # Roteiro de testes rápidos e validação (Phase 1)
├── plan.md                          # Este plano de implementação
└── tasks.md                         # Tarefas de implementação (/speckit-tasks)
```

### Source Code

```text
frontend/src/
├── components/
│   ├── layout/
│   │   ├── GlobalHeader.vue         # Cabeçalho global em 3 zonas operacionais
│   │   ├── NavigationTabs.vue       # Abas primárias e dropdown retrátil "Mais ▾"
│   │   └── UserDropdown.vue         # Menu do usuário com perfil e botão Sair integrado
│   ├── ui/
│   │   └── Drawer.vue               # Gaveta lateral deslizante acessível (420px desktop, 100% mobile)
│   └── library/
│       └── BookHeroCard.vue         # Hero Card destacado da leitura ativa ("Em Andamento")
├── views/
│   └── BooksView.vue                # Página de livros em largura total (sem coluna fixa)
├── App.vue                          # Integração do novo GlobalHeader no App Shell
├── style.css                        # Estilos globais e tokens semânticos ajustados
└── tests/
    └── feature-065-livros-header.test.ts # Testes unitários do Header e Drawer
```

---

## Implementation Steps

### Phase 0: Research & Alignment (Concluída)
- Decisões consolidadas em `research.md`.

### Phase 1: Design & Contracts (Concluída)
- `data-model.md`, `contracts/header-and-books-ui.yaml`, `quickstart.md` gerados.

### Phase 2: Tasks Decomposição
- Geração de `tasks.md` via `/speckit-tasks`.
