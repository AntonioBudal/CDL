# Contrato de Componentes e Interface do Shell Móvel

**Feature**: `077-shell-navegacao-movel`  
**Escopo**: Estrutura de classes, seletores WAI-ARIA, tokens e eventos do Shell e Navegação Móvel.

---

## 1. Contrato de `MobileTabBar.vue`

### Estrutura Semântica
```html
<nav class="mobile-tab-bar" aria-label="Navegação móvel principal">
  <!-- 4 Abas Primárias -->
  <RouterLink to="/dashboard" class="mobile-tab-item" :aria-current="route.name === 'dashboard' ? 'page' : undefined">
    <Icon name="layout-dashboard" :size="20" />
    <span class="mobile-tab-label">Início</span>
  </RouterLink>
  <RouterLink to="/books" class="mobile-tab-item" :aria-current="route.name === 'books' || route.name === 'book' ? 'page' : undefined">
    <Icon name="book" :size="20" />
    <span class="mobile-tab-label">Livros</span>
  </RouterLink>
  <RouterLink to="/highlights" class="mobile-tab-item" :aria-current="route.name === 'highlights' ? 'page' : undefined">
    <Icon name="pencil" :size="20" />
    <span class="mobile-tab-label">Destaques</span>
  </RouterLink>
  <RouterLink to="/review" class="mobile-tab-item" :aria-current="route.name === 'review' ? 'page' : undefined">
    <Icon name="rotate-ccw" :size="20" />
    <span class="mobile-tab-label">Revisão</span>
  </RouterLink>

  <!-- 5º Botão: Gatilho da Gaveta Mais -->
  <button type="button" class="mobile-tab-item mobile-tab-more-trigger" aria-haspopup="dialog" aria-label="Mais opções de navegação" @click="emit('open-more')">
    <Icon name="more-horizontal" :size="20" />
    <span class="mobile-tab-label">Mais</span>
    <span v-if="hasSecondaryBadge" class="mobile-tab-dot" aria-label="Novas notificações" />
  </button>
</nav>
```

### Regras CSS Normativas
- Visibilidade: `display: none` em viewports $\ge 768\text{px}$; `display: grid` (5 colunas iguais) em `< 768px`.
- Posição: `position: fixed; bottom: 0; left: 0; right: 0; z-index: 80`.
- Altura e Safe Area: `min-height: 56px; padding-bottom: env(safe-area-inset-bottom, 0px)`.
- Alvo Tátil Mínimo: cada `.mobile-tab-item` possui `min-height: 48px; min-width: 48px`.

---

## 2. Contrato de Tokens de Offset

Declarado em `:root` em `mobile-navigation.css`:
```css
:root {
  --mobile-nav-height: 56px;
  --mobile-nav-offset: calc(var(--mobile-nav-height) + env(safe-area-inset-bottom, 0px));
}
```

Componentes com elementos fixos inferiores vinculam suas distâncias ao token:
- `useFloatingToast.ts`: `bottom: calc(var(--mobile-nav-offset, 0px) + 1rem)`.
- `TrashView.vue` (`.trash-batch-bar`): `bottom: calc(var(--mobile-nav-offset, 0px) + 0.75rem)`.
- `SettingsView.vue` (`.fab-preview`): `bottom: calc(var(--mobile-nav-offset, 0px) + 1rem)`.

---

## 3. Contrato de `ShareModal.vue`

### Estrutura Semântica sem Tailwind
```html
<div v-if="modelValue" class="share-modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="share-modal-title">
  <div class="share-modal-card">
    <header class="share-modal-header">
      <div class="share-modal-title-group">
        <Icon name="network" :size="20" class="share-modal-icon" />
        <h2 id="share-modal-title" class="share-modal-title">Compartilhar Estudo</h2>
      </div>
      <button type="button" class="share-modal-close-btn" aria-label="Fechar janela de compartilhamento" @click="close">
        <Icon name="x" :size="20" />
      </button>
    </header>
    <div class="share-modal-body">
      <!-- Conteúdo do modal -->
    </div>
    <footer class="share-modal-footer">
      <button type="button" class="button secondary share-modal-done-btn" @click="close">Concluir</button>
    </footer>
  </div>
</div>
```

### Regras CSS Normativas
- Backdrop: `position: fixed; inset: 0; z-index: 1000; background: rgba(0, 0, 0, 0.6); backdrop-filter: blur(2px)`.
- Diálogo: `background: var(--color-surface); border: 1px solid var(--color-border); border-radius: var(--radius-card, 12px); box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3)`.
- Zero classes Tailwind (`fixed`, `inset-0`, `z-50`, `bg-black/60`, `w-full`, etc.).
