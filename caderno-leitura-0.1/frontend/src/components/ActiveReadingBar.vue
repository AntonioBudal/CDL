<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    active?: boolean
    revealedCount?: number
    totalCount?: number
    completionPercentage?: number
    currentIndex?: number
  }>(),
  {
    active: false,
    revealedCount: 0,
    totalCount: 0,
    completionPercentage: 0,
    currentIndex: -1,
  },
)

const emit = defineEmits<{
  (e: 'reveal-all'): void
  (e: 'hide-all'): void
  (e: 'next'): void
  (e: 'previous'): void
  (e: 'close'): void
}>()

const statusText = computed(() => {
  if (props.totalCount === 0) {
    return 'Nenhum trecho interativo nesta seção'
  }
  return `${props.revealedCount} de ${props.totalCount} revisados (${props.completionPercentage}%)`
})

const currentPositionText = computed(() => {
  if (props.totalCount === 0 || props.currentIndex < 0) return ''
  return `Trecho ${props.currentIndex + 1} de ${props.totalCount}`
})
</script>

<template>
  <aside
    v-if="active"
    class="active-reading-bar"
    role="region"
    aria-label="Barra de Leitura Ativa"
  >
    <div class="reading-bar-track" aria-hidden="true">
      <div
        class="reading-bar-fill"
        :style="{ width: `${completionPercentage}%` }"
      />
    </div>

    <div class="reading-bar-content">
      <div class="reading-bar-status" aria-live="polite">
        <span class="status-indicator-badge">
          <svg class="status-icon" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <circle cx="12" cy="12" r="10" />
            <path d="M12 6v6l4 2" />
          </svg>
          <span class="status-label">Leitura Ativa</span>
        </span>
        <span class="status-count">{{ statusText }}</span>
        <span v-if="currentPositionText" class="status-position">{{ currentPositionText }}</span>
      </div>

      <div class="reading-bar-actions">
        <!-- Navegação sequencial -->
        <div class="action-nav-group" role="group" aria-label="Navegação entre trechos">
          <button
            type="button"
            class="reading-bar-btn nav-btn"
            :disabled="totalCount === 0"
            title="Trecho anterior (K ou Seta Acima)"
            aria-label="Trecho anterior"
            @click="emit('previous')"
          >
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <polyline points="15 18 9 12 15 6" />
            </svg>
            <span class="btn-text">Anterior</span>
          </button>

          <button
            type="button"
            class="reading-bar-btn nav-btn"
            :disabled="totalCount === 0"
            title="Próximo trecho (J ou Seta Abaixo)"
            aria-label="Próximo trecho"
            @click="emit('next')"
          >
            <span class="btn-text">Próximo</span>
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <polyline points="9 18 15 12 9 6" />
            </svg>
          </button>
        </div>

        <!-- Ações em massa -->
        <div class="action-bulk-group" role="group" aria-label="Ações em massa">
          <button
            type="button"
            class="reading-bar-btn bulk-btn"
            :disabled="totalCount === 0"
            title="Ocultar todos os trechos interativos da seção"
            aria-label="Ocultar todos os trechos"
            @click="emit('hide-all')"
          >
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
              <line x1="1" y1="1" x2="23" y2="23" />
            </svg>
            <span class="btn-text">Ocultar todos</span>
          </button>

          <button
            type="button"
            class="reading-bar-btn bulk-btn"
            :disabled="totalCount === 0"
            title="Revelar todos os trechos interativos da seção"
            aria-label="Revelar todos os trechos"
            @click="emit('reveal-all')"
          >
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
              <circle cx="12" cy="12" r="3" />
            </svg>
            <span class="btn-text">Revelar todos</span>
          </button>
        </div>

        <!-- Botão de encerramento -->
        <button
          type="button"
          class="reading-bar-btn close-btn"
          title="Encerrar Leitura Ativa (Escape)"
          aria-label="Fechar barra de Leitura Ativa"
          @click="emit('close')"
        >
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.active-reading-bar {
  position: sticky;
  top: 0;
  z-index: 30;
  background-color: var(--color-bg-surface, var(--bg-surface, #ffffff));
  border-bottom: 1px solid var(--color-border, #e5e7eb);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  margin-bottom: 1rem;
  border-radius: 6px;
  overflow: hidden;
  transition: background-color 0.2s ease, border-color 0.2s ease;
}

.reading-bar-track {
  width: 100%;
  height: 3px;
  background-color: var(--color-border-subtle, rgba(0, 0, 0, 0.06));
}

.reading-bar-fill {
  height: 100%;
  background-color: var(--color-primary, #2563eb);
  transition: width 0.25s ease-out;
}

.reading-bar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.875rem;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.reading-bar-status {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  font-size: 0.875rem;
  color: var(--color-text-main, #1f2937);
  flex-wrap: wrap;
}

.status-indicator-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  background-color: var(--color-accent-subtle, rgba(37, 99, 235, 0.1));
  color: var(--color-primary, #2563eb);
  font-weight: 600;
  font-size: 0.8125rem;
}

.status-icon {
  flex-shrink: 0;
}

.status-count {
  font-weight: 500;
}

.status-position {
  font-size: 0.75rem;
  color: var(--color-text-muted, #6b7280);
  background-color: var(--color-bg-base, #f9fafb);
  padding: 0.125rem 0.375rem;
  border-radius: 3px;
  border: 1px solid var(--color-border-subtle, #e5e7eb);
}

.reading-bar-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.action-nav-group,
.action-bulk-group {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

.reading-bar-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  min-height: 36px;
  padding: 0.25rem 0.625rem;
  border-radius: 4px;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text-main, #374151);
  background-color: var(--color-bg-base, #f3f4f6);
  border: 1px solid var(--color-border, #d1d5db);
  cursor: pointer;
  transition: background-color 0.15s ease, color 0.15s ease, border-color 0.15s ease;
}

.reading-bar-btn:hover:not(:disabled) {
  background-color: var(--color-bg-hover, #e5e7eb);
  color: var(--color-text-contrast, #111827);
  border-color: var(--color-border-strong, #9ca3af);
}

.reading-bar-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.reading-bar-btn:focus-visible {
  outline: 2px solid var(--color-primary, #2563eb);
  outline-offset: 1px;
}

.close-btn {
  min-width: 36px;
  min-height: 36px;
  padding: 0;
  border-radius: 4px;
  color: var(--color-text-muted, #6b7280);
}

.close-btn:hover:not(:disabled) {
  background-color: var(--color-bg-danger-subtle, rgba(239, 68, 68, 0.1));
  color: var(--color-danger, #dc2626);
  border-color: var(--color-danger, #dc2626);
}

@media (max-width: 768px) {
  .reading-bar-content {
    padding: 0.5rem;
    gap: 0.5rem;
  }

  .reading-bar-btn {
    min-height: 44px;
    min-width: 44px;
    padding: 0.375rem 0.5rem;
  }

  .reading-bar-btn .btn-text {
    display: none;
  }

  .reading-bar-status {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
