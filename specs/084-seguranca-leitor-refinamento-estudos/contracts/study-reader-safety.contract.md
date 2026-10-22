# Interface Contracts: F0.9.03 — Segurança Operacional e Refinamento do Leitor de Estudos

**Feature**: `specs/084-seguranca-leitor-refinamento-estudos`  
**Parent Roadmap**: `docs/contexto/ROADMAP-0.9.md` (Feature F03)  
**Zero Emojis Policy**: Rigorosamente respeitada.

---

## 1. Contrato do Cabeçalho de Leitura (`StudyView.vue`)

### 1.1 Elementos Primários e Secundários
```html
<header class="reader-header">
  <div class="reader-header-main">
    <div class="reader-title-line">
      <!-- Breadcrumb compacto / Título / Subtítulo -->
    </div>
  </div>

  <div class="header-actions">
    <!-- Ação Primária: Editar Estudo (se canEdit) -->
    <RouterLink
      v-if="canEdit"
      class="button primary edit-action header-icon-btn"
      :to="{ name: 'study-edit', params: { bookId: state.context.book.id, studyId: state.context.study.id } }"
      aria-label="Editar estudo"
      title="Editar estudo"
    >
      <Icon name="pencil" :size="16" />
      <span class="edit-btn-text">Editar</span>
    </RouterLink>

    <!-- Menu Contextual de Ações Secundárias -->
    <DropdownMenu align="right" aria-label="Mais opções do estudo">
      <template #trigger="{ isOpen, toggle, onKeydown }">
        <button
          type="button"
          class="secondary header-icon-btn study-more-trigger"
          :aria-expanded="isOpen"
          aria-label="Mais opções do estudo"
          title="Mais opções do estudo"
          @click="toggle"
          @keydown="onKeydown"
        >
          <Icon name="more-horizontal" :size="18" />
        </button>
      </template>

      <template #default="{ close }">
        <div class="study-actions-menu" role="menu">
          <!-- Compartilhar (se canEdit) -->
          <button
            v-if="canEdit"
            type="button"
            class="dropdown-item"
            role="menuitem"
            @click="shareModalOpen = true; close()"
          >
            <Icon name="users" :size="16" />
            <span>Compartilhar</span>
          </button>

          <!-- Exportar estudo -->
          <button
            type="button"
            class="dropdown-item"
            role="menuitem"
            @click="exportModalOpen = true; close()"
          >
            <Icon name="download" :size="16" />
            <span>Exportar</span>
          </button>

          <!-- Histórico de versões -->
          <button
            type="button"
            class="dropdown-item"
            role="menuitem"
            @click="historyModalOpen = true; close()"
          >
            <Icon name="clock" :size="16" />
            <span>Histórico de versões</span>
          </button>

          <!-- Separador e ação destrutiva (se canEdit) -->
          <div v-if="canEdit" class="dropdown-divider" role="separator" aria-hidden="true"></div>
          <button
            v-if="canEdit"
            type="button"
            class="dropdown-item danger-item"
            role="menuitem"
            @click="confirmTrashOpen = true; close()"
          >
            <Icon name="trash" :size="16" />
            <span>Mover para a lixeira</span>
          </button>
        </div>
      </template>
    </DropdownMenu>
  </div>
</header>
```

---

## 2. Contrato da Pílula de Status no Editor (`StudyEditView.vue`)

### 2.1 Pílula de Status de Rascunho
```html
<div class="edit-title-row">
  <h1>Editar estudo</h1>
  <span
    class="draft-status-pill"
    :class="draftStatusClass"
    role="status"
    aria-live="polite"
  >
    <Icon :name="draftStatusIcon" :size="14" class="status-pill-icon" />
    <span>{{ draftStatusLabel }}</span>
  </span>
</div>
```

---

## 3. Contrato de Alvos Táteis Ergonômicos (WCAG 2.5.5)

### 3.1 Regras de Estilo para Toque
```css
@media (pointer: coarse), (max-width: 767px) {
  .header-icon-btn,
  .reading-bar-btn,
  .reading-bar-btn.close-btn,
  .study-tabs [role="tab"] {
    min-height: 44px;
    min-width: 44px;
  }
}
```
