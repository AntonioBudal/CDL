# Implementation Plan: Shell e Navegação Móvel

**Branch**: `077-shell-navegacao-movel` | **Spec**: [spec.md](spec.md)

---

## Summary
Implementar a restauração da navegação móvel de 5 colunas via barra inferior dedicada (`MobileTabBar.vue`), desacoplar o menu de abas do cabeçalho superior em telas móveis (< 768px), expandir a gaveta `MobileMoreMenu.vue` com todas as rotas secundárias, expor o token `--mobile-nav-offset` para impedir sobreposição de elementos flutuantes (toasts, batch bar e FAB), adaptar `NotificationsDropdown.vue` contra cortes laterais em telas $\le 430\text{px}$, reescrever `ShareModal.vue` com tokens CSS nativos sem classes Tailwind, purgar estilos mortos em `App.vue` e blindar os testes unitários de navegação móvel para garantir correspondência estrita com os templates reais.

---

## Technical Context
- **Stack**: Vue 3 (`<script setup>`, TypeScript), Vite 8, CSS autoral com tokens canônicos.
- **Breakpoints**: Regra canônica do contrato da Feature 076: móvel estrito em `< 768px` (`max-width: 767px`) e tablet/desktop em `≥ 768px`.
- **Arquitetura de Navegação**:
  - `GlobalHeader.vue`: Oculta as abas (`NavigationTabs.vue`) em `< 768px`, mantendo apenas marca, busca, captura rápida, notificações e avatar.
  - `MobileTabBar.vue`: Novo componente fixo no rodapé móvel (`position: fixed; bottom: 0`) com 5 botões: Início, Livros, Destaques, Revisão e gatilho "Mais".
  - `MobileMoreMenu.vue`: Drawer móvel cobrindo rotas secundárias com badges: Caixa de Entrada (`useInboxCount`), Amigos (`useFriends`), Ajustes, Lixeira, Importar estudo.
  - Token CSS: `--mobile-nav-offset: calc(56px + env(safe-area-inset-bottom, 0px))`.
  - `NotificationsDropdown.vue`: Regras para telas $\le 430\text{px}$ ocupando largura fluida total (`left: 0.5rem; right: 0.5rem; width: auto`).
  - `ShareModal.vue`: Remoção de 100% das classes Tailwind em favor de classes BEM/semânticas e `<style scoped>` com tokens canônicos.
  - `App.vue`: Remoção do CSS scoped legado e morto referente ao cabeçalho.
  - Testes: `tests/mobile_navigation_contrast.test.mjs` atualizado para checar a existência física das classes nos templates.

---

## Constitution Check
- **I. Preservação de Dados e Privacidade**: Operações estritamente em componentes de interface visual e de navegação. Nenhuma leitura ou exposição de dados pessoais. ✔
- **II. Integridade do Banco e Operações no Ambiente**: Nenhuma alteração no backend ou banco de dados. Banco ativo `backend/data/caderno.db` intocado. ✔
- **III. Estado do Roadmap e Versão 0.5**: A conformidade segue rigorosamente o ciclo Spec Kit. ✔
- **IV. Fluxo de Trabalho (Spec-Driven Development)**: Ciclo formal delimitado: specify → clarify → plan → tasks → analyze → implement. ✔
- **V. Convenção de Versionamento Git**: Feature atômica com commit individual ao final (1 Feature = 1 Commit). ✔

---

## Project Structure

```text
caderno-leitura-0.1/frontend/src/
├── components/
│   ├── layout/
│   │   ├── GlobalHeader.vue           # Ocultar abas em < 768px
│   │   ├── MobileTabBar.vue           # [NOVO] Barra inferior móvel com 5 colunas
│   │   └── NavigationTabs.vue         # Ocultação sob media query móvel
│   ├── navigation/
│   │   └── MobileMoreMenu.vue         # Completar com Inbox, Amigos, Importar + badges
│   ├── notifications/
│   │   └── NotificationsDropdown.vue  # Adaptação para telas <= 430px
│   └── sharing/
│       └── ShareModal.vue             # Reescrita nativa sem classes Tailwind
├── mobile-navigation.css              # Sincronização de regras com MobileTabBar
├── App.vue                            # Inclusão de MobileTabBar e purga de CSS morto
caderno-leitura-0.1/frontend/tests/
├── mobile_navigation_contrast.test.mjs# Amarração de seletores reais ao template
└── feature-077-shell-mobile.test.mjs  # [NOVO] Teste da suite de navegação e tokens da F0.8.12
```

---

## Abordagem de Implementação

1. **Criação de `MobileTabBar.vue` e Integração no Shell**:
   - Desenvolver `MobileTabBar.vue` com semântica `<nav class="mobile-tab-bar" aria-label="Navegação móvel principal">`.
   - Renderizar 5 itens: Início (`/dashboard`), Livros (`/books`), Destaques (`/highlights`), Revisão (`/review`) e "Mais" (emite evento `open-more`).
   - Cada botão com dimensão mínima de 44×44px e ícone Lucide de 20px com rótulo tátil.
   - Integrar no `App.vue`: exibir apenas se autenticado e fora de telas `cleanScreen`.
2. **Desacoplamento do Cabeçalho Superior em Telas Móveis**:
   - Em `GlobalHeader.vue` / `NavigationTabs.vue`, aplicar regra para que em `@media (max-width: 767px)` as abas recebam `display: none`.
   - Garantir que o topo exiba apenas marca e as ações rápidas sem estouro lateral.
3. **Expansão da Gaveta `MobileMoreMenu.vue`**:
   - Importar `useInboxCount` e `useFriends` para exibir contadores reativos.
   - Adicionar itens: Caixa de Entrada (`/inbox`), Amigos (`/amigos`), Importar Estudo (`/importar`), Lixeira (`/lixeira`), Ajustes (`/ajustes`), Meu Perfil e Sair.
   - Garantir alvos de 44px em todos os itens.
4. **Padronização de Tokens de Offset Inferior**:
   - Em `mobile-navigation.css`, declarar `--mobile-nav-offset: calc(56px + env(safe-area-inset-bottom, 0px))` em `:root`.
   - Atualizar componentes com elementos fixos no rodapé:
     - Toasts flutuantes: `bottom: calc(var(--mobile-nav-offset, 0px) + 1rem)`.
     - Barra de lote da Lixeira (`.trash-batch-bar`): `bottom: calc(var(--mobile-nav-offset, 0px) + 0.75rem)`.
     - FAB de Ajustes (`.fab-preview`): `bottom: calc(var(--mobile-nav-offset, 0px) + 1rem)`.
5. **Adaptação de `NotificationsDropdown.vue`**:
   - Em telas $\le 430\text{px}$, trocar `min-width: 360px; right: 0;` por posicionamento fluido centrado/alinhado com as bordas da tela (`left: 0.5rem; right: 0.5rem; width: auto; max-width: calc(100vw - 1rem)`).
6. **Reescrita de `ShareModal.vue` com CSS Canônico**:
   - Substituir classes Tailwind por classes semânticas (`.share-modal-backdrop`, `.share-modal-dialog`, `.share-modal-header`, `.share-modal-body`, `.share-modal-footer`).
   - Adicionar bloco `<style scoped>` usando os tokens nativos (`--color-surface`, `--color-border`, `--color-text`, `--color-accent`, etc.).
7. **Purga de CSS Morto em `App.vue`**:
   - Remover regras scoped não utilizadas de cabeçalho (`.user-chip`, `.user-avatar-icon`, etc.).
8. **Testes Automatizados**:
   - Atualizar `tests/mobile_navigation_contrast.test.mjs` para validar seletores reais de `MobileTabBar.vue`.
   - Criar `tests/feature-077-shell-mobile.test.mjs` cobrindo 100% dos requisitos da F0.8.12.

---

## Critérios de Conclusão e Gates
- **SC-001**: Barra móvel de 5 itens funcional em `< 768px` com alvos $\ge 44\text{px}$.
- **SC-002**: Gaveta "Mais" lista Inbox, Amigos e Importar com contadores.
- **SC-003**: Elementos flutuantes utilizam `--mobile-nav-offset` sem sobrepor a barra.
- **SC-004**: `ShareModal` livre de Tailwind e estilizado com tokens nativos.
- **SC-005**: `npm test` e `npm run build` passam com 100% de sucesso.
