# Contract: Ajustes de Layout e Componentes UI (F0.8.10)

**Diretório**: `specs/075-correcoes-visuais-disposicao/contracts/`  
**Arquivo**: `ui-components.contract.md`  
**Status**: Normativo

---

## 1. Contrato de Alinhamento e Botões em Livros

| Componente | Elemento / Propriedade | Comportamento Contratado |
|---|---|---|
| `appearance-advanced.css` | `.book-grid` | `grid-template-columns: repeat(auto-fill, minmax(min(100%, 16rem), 1fr)); justify-content: start;` |
| `BookCover.vue` | `.placeholder-title` | Renderizado condicionalmente com `v-if="size !== 'sm'"`. Na miniatura pequena, exibe apenas monograma ou lombada/cor. |
| `CategoryBadge.vue` | `.category-badge` | Fundo transparente (`background-color: transparent`), borda e texto respeitando o tema. |
| `BooksView.vue` | `.add-book-btn` | Texto limpo `<span>Adicionar Livro</span>` e `<Icon name="plus" />`. Rótulo acessível sem caracteres soltos. |
| `LibraryToolbar.vue` | `.view-mode-toggle` | `background: transparent; border: none; gap: 0.35rem; display: inline-flex;` com botões individuais espaçados e delimitados. |

---

## 2. Contrato de Visualizações de Estudo (`/livros/:id`)

| Componente | Elemento | Comportamento Contratado |
|---|---|---|
| `StudyStatusBadge.vue` | Opções e Selos | Fundo transparente (`transparent`), borda no padrão do tema, indicador de forma/ícone distinto por estado. |
| `StudyListView.vue` | Cabeçalhos e Ordenação | Todos os títulos de coluna alinhados com o conteúdo de suas células; ordenação ativa indicada via componente `<Icon>` (`arrow-up`/`arrow-down`). |
| `StudyListView.vue` | Desmarcar seleção | Área de toque do botão de desmarcar $\ge 44 \times 44$px. |
| `StudyTreeNodeItem.vue` | Botões de Ação e Título | Substituição de `color: var(--color-inverse-bg)` por `var(--color-text)` ou `var(--color-hover-text)`. |
| `StudyMapView.vue` | Botões de Zoom | Contraste adequado em todos os 10 temas; remoção de `--color-inverse-bg`. |
| `StudyMapView.vue` | `.mobile-map-toolbar` | Oculta por padrão em telas desktop (`display: none;`) e habilitada sob `@media (max-width: 768px)`. |

---

## 3. Contrato de Layout Geral e Páginas Públicas

| Componente | Elemento | Comportamento Contratado |
|---|---|---|
| `AppFooter.vue` | Layout Desktop / Mobile | `display: flex; justify-content: space-between;` em desktop; coluna sem pontuações isoladas em mobile. |
| `UserDropdown.vue` | Gatilho (`.user-trigger-btn`) | Apenas avatar/iniciais com $\ge 44 \times 44$px, sem duplicação de nome fora do avatar e sem seta isolada. |
| `EmptyState.vue` | Moldura e Caixa | Superfície via `var(--color-surface)` e moldura de ícone via `var(--color-surface-soft)` ou transparente. |
| `FriendsView.vue` | Bloqueados Vazio | Uso padronizado de `<EmptyState icon="ban" ... />` centralizado. |
| `PublicFooter.vue` | Link de Código Aberto | Destino atualizado para `https://github.com/AntonioBudal/CDL`. |
| `SupportView.vue` | Exibição Institucional | Foco em transparência e colaboração aberta; sem formulários de pagamento vazios. |
| `useVisitorTheme.ts` | Ciclo de Vida da Visita | Preserva seleção em `sessionStorage` (`caderno_visitor_theme`) entre `/`, `/sobre`, `/apoie` sem resetar no `onBeforeUnmount`. |
