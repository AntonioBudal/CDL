# Contract: Composição Espacial e Ergonomia Móvel da Página do Livro

**Feature**: `specs/083-ergonomia-mobile-pagina-livro`  
**Date**: 2026-10-21  

---

## 1. Contrato do Cabeçalho Condensado no Mobile (`BookView.vue`)

### Estrutura Semântica HTML5

```html
<header class="page-header wrap book-header">
  <div class="book-header-main">
    <!-- Linha 1: Miniatura da Capa + Informações Principais -->
    <div class="book-header-cover">
      <BookCover :cover-image="book.cover_image" :title="book.title" :author="book.author" size="md" />
    </div>
    <div class="book-info">
      <p class="eyebrow">Livro</p>
      <h1 class="book-title">{{ book.title }}</h1>
      <p v-if="book.subtitle" class="book-subtitle">{{ book.subtitle }}</p>
      <p class="intro">
        {{ book.author || 'Autor não informado' }}
        <span v-if="book.year"> · {{ book.year }}</span>
      </p>

      <!-- Linha 2: Categorias + Gatilho Móvel de Ações -->
      <div class="book-meta-actions-row">
        <div v-if="book.categories && book.categories.length > 0" class="book-categories-strip">
          <CategoryBadge
            v-for="cat in book.categories"
            :key="cat.id"
            :category="cat"
            clickable
            size="sm"
            @click="router.push({ path: '/books', query: { categoria: cat.id } })"
          />
        </div>

        <!-- Menu Agrupado de Ações no Mobile (<= 767px) -->
        <div class="book-mobile-actions-wrapper">
          <DropdownMenu align="right" aria-label="Ações do livro">
            <template #trigger="{ isOpen, toggle, onKeydown }">
              <button
                type="button"
                class="secondary button-sm book-mobile-actions-trigger"
                :aria-expanded="isOpen"
                @click="toggle"
                @keydown="onKeydown"
              >
                <Icon name="more-horizontal" :size="16" />
                <span>Ações do livro</span>
              </button>
            </template>
            <template #default="{ close }">
              <div class="book-mobile-actions-menu" role="menu">
                <button
                  type="button"
                  class="dropdown-item"
                  role="menuitem"
                  @click="toggleFocusMode(); close()"
                >
                  <Icon :name="isFocusMode ? 'minimize-2' : 'maximize-2'" :size="16" />
                  <span>{{ isFocusMode ? 'Sair do modo foco' : 'Ativar modo foco' }}</span>
                </button>
                <button
                  type="button"
                  class="dropdown-item"
                  role="menuitem"
                  @click="exportModalOpen = true; close()"
                >
                  <Icon name="download" :size="16" />
                  <span>Exportar anotações</span>
                </button>
                <button
                  type="button"
                  class="dropdown-item"
                  role="menuitem"
                  @click="isEditingBook = true; close()"
                >
                  <Icon name="pencil" :size="16" />
                  <span>Editar livro</span>
                </button>
                <button
                  type="button"
                  class="dropdown-item danger-item"
                  role="menuitem"
                  @click="confirmTrashBookOpen = true; close()"
                >
                  <Icon name="trash" :size="16" />
                  <span>Mover para a lixeira</span>
                </button>
              </div>
            </template>
          </DropdownMenu>
        </div>
      </div>
    </div>
  </div>

  <!-- Barra de Ações Desktop (>= 768px) -->
  <div class="header-actions desktop-actions">
    <!-- Botões em formato de pílula expandida mantidos intactos no desktop -->
  </div>
</header>
```

### Regras de Estilo e Visibilidade

- No desktop (`>= 768px`):
  - `.book-mobile-actions-wrapper`: `display: none !important;`
  - `.header-actions.desktop-actions`: `display: flex !important;`
  - `.book-header-cover`: dimensões padrão (160x240px).
- No mobile (`<= 767px`):
  - `.book-mobile-actions-wrapper`: `display: block;`
  - `.header-actions.desktop-actions`: `display: none !important;`
  - `.book-header-cover img, .book-header-cover .book-cover`: largura máxima travada em `48px`, altura `72px`, `object-fit: cover`, `border-radius: var(--radius-sm, 4px)`.
  - `.book-title`: `-webkit-line-clamp: 2`, `display: -webkit-box`, `-webkit-box-orient: vertical`, `overflow: hidden`, `font-size: 1.15rem`, `line-height: 1.3`.

---

## 2. Contrato da Faixa de Capítulos Unificada no Mobile

### Estrutura Semântica

- Em dispositivos móveis (`<= 767px`):
  - `.chapters-nav-strip`: `display: none !important;` (oculta a esteira rolável redundante).
  - `.chapters-mobile-select-wrap`: `display: flex; align-items: center; gap: 0.5rem; width: 100%;`
  - O elemento `<select class="chapters-mobile-select">` preenche a largura disponível com altura mínima de 44px (`min-height: 44px;`).
  - O botão de novo capítulo inline (`.add-chapter-pill-btn`) permanece acessível ao lado ou integrado na barra móvel, com altura mínima de 44px e foco visual evidente.

---

## 3. Contrato da Faixa do Inspetor Analítico Recolhível

### Estrutura Semântica

```html
<footer
  v-if="!isFocusMode"
  class="inspector-horizontal-bar panel"
  aria-label="Metadados e contexto do livro"
>
  <!-- Gatilho de Alternância para Telas Móveis (<= 767px) -->
  <button
    type="button"
    class="inspector-mobile-toggle mobile-only"
    :aria-expanded="isInspectorExpandedMobile"
    aria-controls="inspector-content-panel"
    @click="isInspectorExpandedMobile = !isInspectorExpandedMobile"
  >
    <Icon name="info" :size="15" />
    <span>{{ isInspectorExpandedMobile ? 'Ocultar detalhes do livro' : 'Ver detalhes do livro' }}</span>
    <Icon :name="isInspectorExpandedMobile ? 'chevron-up' : 'chevron-down'" :size="16" class="toggle-icon" />
  </button>

  <!-- Conteúdo de Métricas Analíticas -->
  <div
    id="inspector-content-panel"
    class="inspector-bar-content"
    :class="{ 'is-collapsed-mobile': !isInspectorExpandedMobile }"
  >
    <div class="inspector-metrics-grid">
      <!-- Indicadores de capítulos, estudos e card de foco -->
    </div>
  </div>
</footer>
```

### Regras de Visibilidade e Comportamento

- No desktop (`>= 768px`):
  - `.inspector-mobile-toggle`: `display: none !important;`
  - `.inspector-bar-content`: `display: flex !important;`
- No mobile (`<= 767px`):
  - `.inspector-mobile-toggle`: `display: inline-flex; align-items: center; justify-content: space-between; width: 100%; min-height: 44px; padding: 0.5rem 0.75rem;`
  - `.inspector-bar-content.is-collapsed-mobile`: `display: none !important;`
  - `.inspector-bar-content:not(.is-collapsed-mobile)`: `display: flex; flex-direction: column; gap: 0.75rem; padding-top: 0.75rem; border-top: var(--border-width) solid var(--color-border-divider);`

---

## 4. Contrato de Acessibilidade e Alvos de Toque

1. **Alvos de Toque Mínimos:**
   - Todos os botões clicáveis no mobile (gatilho de ações, opções de menu, seletor de capítulos, botão de adicionar capítulo e alternador do inspetor) possuem `min-height: 44px; min-width: 44px;`.
2. **Acessibilidade WAI-ARIA:**
   - O menu de ações móvel possui `role="menu"` e itens com `role="menuitem"`.
   - O alternador do inspetor utiliza `:aria-expanded` e `aria-controls`.
3. **Imunidade Cromática aos 10 Temas:**
   - Fundo do menu: `var(--color-surface)`.
   - Texto de rótulos: `var(--color-text)`.
   - Texto secundário/metadados: `var(--color-muted)`.
   - Bordas: `var(--color-border)`.
   - Foco/Destaque: `var(--color-accent)`.
