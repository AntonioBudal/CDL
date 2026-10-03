# Interface Contract: `StudyView.vue` Header Actions

**Arquivo Afetado**: `frontend/src/views/StudyView.vue`  
**Objetivo**: Estabelecer os contratos de leiaute, renderização condicional e classes utilitárias para o cabeçalho do leitor de estudos.

---

## 1. Estrutura do Template do Cabeçalho

```html
<header class="page-header reader-heading">
  <!-- Bloco Editorial Esquerdo -->
  <div class="reader-heading-main">
    <!-- Breadcrumb Desktop vs Mobile -->
    <nav class="breadcrumb-container" aria-label="Navegação hierárquica">
      <div class="breadcrumb-desktop">
        <RouterLink to="/">Meus livros</RouterLink>
        <span aria-hidden="true">/</span>
        <RouterLink :to="{ name: 'book', params: { bookId: state.context.book.id } }">
          {{ state.context.book.title }}
        </RouterLink>
        <span aria-hidden="true">/</span>
        <RouterLink :to="{ name: 'book', params: { bookId: state.context.book.id }, query: { chapter: state.context.chapter.id } }">
          {{ state.context.chapter.name }}
        </RouterLink>
      </div>

      <div class="breadcrumb-mobile">
        <RouterLink
          class="back-to-chapter-link"
          :to="{ name: 'book', params: { bookId: state.context.book.id }, query: { chapter: state.context.chapter.id } }"
        >
          <svg class="w-4 h-4" ... />
          <span class="truncate">Voltar a {{ state.context.chapter.name }}</span>
        </RouterLink>
      </div>
    </nav>

    <!-- Metadados e Título -->
    <div class="reader-meta-row">
      <span class="eyebrow">Estudo</span>
      <StudyStatusBadge
        :status="state.context.study.reading_status || 'rascunho'"
        :study-id="state.context.study.id"
        :interactive="canEdit"
        @change="handleStatusChange"
      />
    </div>

    <h1 class="reader-title">{{ state.context.study.title }}</h1>
    <p class="reader-location">{{ state.context.study.location || 'Localização não informada' }}</p>
  </div>

  <!-- Bloco de Ações do Cabeçalho Direito -->
  <div class="header-actions">
    <!-- Ação Primária Desktop e Mobile (se canEdit) -->
    <RouterLink
      v-if="canEdit"
      class="button primary edit-action"
      :to="{ name: 'study-edit', params: { bookId: state.context.book.id, studyId: state.context.study.id } }"
      aria-label="Editar estudo"
    >
      <svg class="w-4 h-4 icon-edit" ... />
      <span class="action-label">Editar estudo</span>
    </RouterLink>

    <!-- Ação Secundária em Destaque Desktop (se canEdit) -->
    <button
      v-if="canEdit"
      type="button"
      class="secondary share-action desktop-only"
      aria-label="Compartilhar estudo"
      @click="shareModalOpen = true"
    >
      <svg class="w-4 h-4" ... />
      <span>Compartilhar</span>
    </button>

    <!-- Menu Suspenso de Mais Ações (DropdownMenu.vue) -->
    <DropdownMenu aria-label="Mais opções do estudo">
      <template #default="{ close }">
        <!-- Compartilhar no Mobile (se canEdit) -->
        <button
          v-if="canEdit"
          type="button"
          class="dropdown-item mobile-only"
          role="menuitem"
          @click="close(); shareModalOpen = true"
        >
          <svg class="w-4 h-4" ... />
          <span>Compartilhar</span>
        </button>

        <!-- Histórico de Versões -->
        <button
          type="button"
          class="dropdown-item"
          role="menuitem"
          @click="close(); historyModalOpen = true"
        >
          <svg class="w-4 h-4" ... />
          <span>Histórico de versões</span>
        </button>

        <!-- Exportar Estudo -->
        <button
          type="button"
          class="dropdown-item"
          role="menuitem"
          @click="close(); exportModalOpen = true"
        >
          <svg class="w-4 h-4" ... />
          <span>Exportar estudo</span>
        </button>

        <!-- Divisor antes da ação perigosa -->
        <hr v-if="canEdit" class="dropdown-divider" />

        <!-- Mover para Lixeira (se canEdit) -->
        <button
          v-if="canEdit"
          type="button"
          class="dropdown-item danger-item"
          role="menuitem"
          @click="close(); confirmTrashOpen = true"
        >
          <svg class="w-4 h-4" ... />
          <span>Mover para a lixeira</span>
        </button>
      </template>
    </DropdownMenu>
  </div>
</header>
```

---

## 2. Contrato de Estilos e Responsividade

- **Linha Única Rígida**: `.header-actions` possui `flex-wrap: nowrap`, `align-items: center`, `gap: 0.5rem`.
- **Alvo Tátil**: Em `@media (max-width: 768px)`, botões em `.header-actions` possuem `min-height: 44px` e `min-width: 44px`.
- **Classes Utilitárias de Viewport**:
  - `.desktop-only`: `display: inline-flex;` no desktop, `display: none !important;` abaixo de 768px.
  - `.mobile-only`: `display: none !important;` no desktop, `display: flex;` abaixo de 768px.
- **Redução Vertical**: A transição para o botão inteligente `.breadcrumb-mobile` abaixo de 640px reduz a altura do cabeçalho em pelo menos 35%.
