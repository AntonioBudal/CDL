<script setup lang="ts">
defineProps<{
  current: number
  total: number
  percent: number
  timer: string
  bookTitle?: string | null
}>()

const emit = defineEmits<{
  (e: 'exit'): void
}>()
</script>

<template>
  <header class="session-progress-header" role="banner">
    <div class="header-content">
      <div class="left-section">
        <button
          type="button"
          class="btn-exit"
          aria-label="Interromper ou sair da sessão de estudo"
          title="Sair da sessão (Esc)"
          @click="emit('exit')"
        >
          <span class="exit-icon" aria-hidden="true">&times;</span>
          <span class="exit-label">Sair</span>
          <kbd class="exit-kbd">Esc</kbd>
        </button>

        <div v-if="bookTitle" class="session-scope-badge" :title="bookTitle">
          <span class="scope-label">Livro:</span>
          <span class="scope-title">{{ bookTitle }}</span>
        </div>
      </div>

      <div class="center-section">
        <div class="progress-meta">
          <span class="counter-text" aria-live="polite">
            Item {{ current }} de {{ total }}
          </span>
          <span class="percent-text">{{ percent }}%</span>
        </div>
        <div
          class="progress-track"
          role="progressbar"
          :aria-valuenow="current"
          :aria-valuemin="1"
          :aria-valuemax="total"
          :aria-label="`Progresso da sessão: item ${current} de ${total}`"
        >
          <div class="progress-fill" :style="{ width: `${percent}%` }" />
        </div>
      </div>

      <div class="right-section">
        <div class="timer-display" aria-label="Tempo de estudo decorrido" title="Tempo dedicado">
          <svg
            class="timer-icon"
            viewBox="0 0 24 24"
            width="16"
            height="16"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true"
          >
            <circle cx="12" cy="12" r="10" />
            <polyline points="12 6 12 12 16 14" />
          </svg>
          <span class="timer-digits">{{ timer }}</span>
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped>
.session-progress-header {
  position: sticky;
  top: 0;
  left: 0;
  right: 0;
  z-index: 50;
  background-color: var(--color-bg, #ffffff);
  border-bottom: 1px solid var(--color-border-subtle, #e5e7eb);
  padding: 0.75rem 1.5rem;
}

.header-content {
  max-width: 960px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
}

.left-section {
  display: flex;
  align-items: center;
  gap: 1rem;
  min-width: 140px;
}

.btn-exit {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  min-height: 44px;
  min-width: 44px;
  padding: 0.5rem 0.875rem;
  background-color: transparent;
  color: var(--color-text-muted, #6b7280);
  border: 1px solid var(--color-border-subtle, #e5e7eb);
  border-radius: 6px;
  font-family: inherit;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-exit:hover {
  background-color: var(--color-bg-subtle, #f3f4f6);
  color: var(--color-text-danger, #dc2626);
  border-color: var(--color-border-danger, #fca5a5);
}

.btn-exit:focus-visible {
  outline: 2px solid var(--color-accent, #2563eb);
  outline-offset: 2px;
}

.exit-icon {
  font-size: 1.25rem;
  line-height: 1;
}

.exit-kbd {
  font-size: 0.6875rem;
  padding: 0.125rem 0.3125rem;
  background: var(--color-bg-subtle, #f3f4f6);
  border: 1px solid var(--color-border-subtle, #d1d5db);
  border-radius: 3px;
  color: var(--color-text-muted, #6b7280);
}

.session-scope-badge {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.8125rem;
  color: var(--color-text-muted, #4b5563);
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.scope-label {
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.6875rem;
  letter-spacing: 0.05em;
  color: var(--color-text-dim, #9ca3af);
}

.scope-title {
  overflow: hidden;
  text-overflow: ellipsis;
}

.center-section {
  flex: 1;
  max-width: 480px;
}

.progress-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.375rem;
  font-size: 0.8125rem;
  color: var(--color-text-secondary, #4b5563);
  font-weight: 500;
}

.progress-track {
  width: 100%;
  height: 6px;
  background-color: var(--color-bg-subtle, #e5e7eb);
  border-radius: 9999px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: var(--color-accent, #2563eb);
  border-radius: 9999px;
  transition: width 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.right-section {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  min-width: 120px;
}

.timer-display {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  min-height: 44px;
  padding: 0.5rem 0.75rem;
  font-variant-numeric: tabular-nums;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-secondary, #374151);
  background-color: var(--color-bg-subtle, #f9fafb);
  border: 1px solid var(--color-border-subtle, #e5e7eb);
  border-radius: 6px;
}

.timer-icon {
  color: var(--color-text-muted, #9ca3af);
}

@media (max-width: 640px) {
  .session-progress-header {
    padding: 0.5rem 1rem;
  }
  .header-content {
    gap: 0.75rem;
  }
  .session-scope-badge {
    display: none;
  }
  .exit-kbd {
    display: none;
  }
  .left-section,
  .right-section {
    min-width: auto;
  }
}
</style>
