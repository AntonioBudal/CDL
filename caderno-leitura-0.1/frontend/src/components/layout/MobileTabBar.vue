<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import Icon from '../ui/Icon.vue'
import { useInboxCount } from '../../composables/useInboxCount.ts'
import { useFriends } from '../../composables/useFriends.ts'

const emit = defineEmits<{
  (e: 'open-more'): void
}>()

const route = useRoute()
const inboxService = useInboxCount()
const friendsService = useFriends()

const hasSecondaryBadge = computed(() => {
  return (inboxService.count.value > 0) || (friendsService.pendingReceivedCount.value > 0)
})

const isDashboardActive = computed(() => route.name === 'dashboard')
const isBooksActive = computed(() => ['books', 'book', 'study', 'study-edit'].includes(String(route.name)))
const isHighlightsActive = computed(() => route.name === 'highlights')
const isReviewActive = computed(() => ['review', 'study-session'].includes(String(route.name)))
</script>

<template>
  <nav class="mobile-tab-bar" aria-label="Navegação móvel principal">
    <!-- Início -->
    <RouterLink
      to="/dashboard"
      class="mobile-tab-item"
      :class="{ selected: isDashboardActive }"
      :aria-current="isDashboardActive ? 'page' : undefined"
    >
      <Icon name="layout-dashboard" :size="20" class="mobile-tab-icon" />
      <span class="mobile-tab-label">Início</span>
    </RouterLink>

    <!-- Livros -->
    <RouterLink
      to="/books"
      class="mobile-tab-item"
      :class="{ selected: isBooksActive }"
      :aria-current="isBooksActive ? 'page' : undefined"
    >
      <Icon name="book" :size="20" class="mobile-tab-icon" />
      <span class="mobile-tab-label">Livros</span>
    </RouterLink>

    <!-- Destaques -->
    <RouterLink
      to="/highlights"
      class="mobile-tab-item"
      :class="{ selected: isHighlightsActive }"
      :aria-current="isHighlightsActive ? 'page' : undefined"
    >
      <Icon name="pencil" :size="20" class="mobile-tab-icon" />
      <span class="mobile-tab-label">Destaques</span>
    </RouterLink>

    <!-- Revisão -->
    <RouterLink
      to="/review"
      class="mobile-tab-item"
      :class="{ selected: isReviewActive }"
      :aria-current="isReviewActive ? 'page' : undefined"
    >
      <Icon name="rotate-ccw" :size="20" class="mobile-tab-icon" />
      <span class="mobile-tab-label">Revisão</span>
    </RouterLink>

    <!-- Mais -->
    <button
      type="button"
      class="mobile-tab-item mobile-tab-more-trigger mobile-more-trigger"
      aria-haspopup="dialog"
      aria-label="Mais opções de navegação"
      @click="emit('open-more')"
    >
      <div class="mobile-tab-icon-wrap">
        <Icon name="more-horizontal" :size="20" class="mobile-tab-icon" />
        <span
          v-if="hasSecondaryBadge"
          class="mobile-tab-dot"
          aria-label="Notificações pendentes"
        />
      </div>
      <span class="mobile-tab-label">Mais</span>
    </button>
  </nav>
</template>

<style scoped>
.mobile-tab-bar {
  display: none;
}

@media (max-width: 767px) {
  .mobile-tab-bar {
    position: fixed;
    inset: auto 0 0;
    z-index: 80;
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    align-items: stretch;
    gap: calc(var(--space-unit, 1rem) * 0.15);
    width: 100%;
    min-height: 56px;
    height: var(--mobile-nav-offset, calc(56px + env(safe-area-inset-bottom, 0px)));
    margin: 0;
    padding-top: calc(var(--space-unit, 1rem) * 0.25);
    padding-bottom: calc(
      var(--space-unit, 1rem) * 0.25 + env(safe-area-inset-bottom, 0px)
    );
    padding-left: max(
      calc(var(--space-unit, 1rem) * 0.25),
      env(safe-area-inset-left, 0px)
    );
    padding-right: max(
      calc(var(--space-unit, 1rem) * 0.25),
      env(safe-area-inset-right, 0px)
    );
    border-top: var(--border-width, 1px) solid var(--color-border-strong, var(--color-border));
    background: var(--color-surface);
    box-shadow: var(--shadow-panel, 0 -2px 10px rgba(0, 0, 0, 0.08));
  }

  .mobile-tab-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 44px;
    min-width: 44px;
    padding: calc(var(--space-unit, 1rem) * 0.2);
    background: transparent;
    border: none;
    color: var(--color-muted);
    font-size: 0.75rem;
    line-height: 1.2;
    text-decoration: none;
    cursor: pointer;
    border-radius: var(--radius-control, 6px);
    transition: color 0.15s ease, background-color 0.15s ease;
    -webkit-tap-highlight-color: transparent;
  }

  .mobile-tab-item:hover {
    color: var(--color-text);
  }

  .mobile-tab-item.selected,
  .mobile-tab-item[aria-current="page"] {
    color: var(--color-accent);
    font-weight: 700;
  }

  .mobile-tab-item.selected .mobile-tab-label,
  .mobile-tab-item[aria-current="page"] .mobile-tab-label {
    font-weight: 750;
    text-decoration: underline;
    text-underline-offset: 0.2em;
  }

  .mobile-tab-icon-wrap {
    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }

  .mobile-tab-dot {
    position: absolute;
    top: -2px;
    right: -4px;
    width: 8px;
    height: 8px;
    border-radius: 9999px;
    background-color: var(--color-error-marker, #dc2626);
    border: 1.5px solid var(--color-surface);
  }

  .mobile-tab-label {
    margin-top: 2px;
    font-size: 0.7rem;
  }
}
</style>
