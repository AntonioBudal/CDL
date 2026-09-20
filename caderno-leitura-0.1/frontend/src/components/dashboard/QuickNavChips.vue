<script setup lang="ts">
import type { IconName } from '../../types'
import Icon from '../ui/Icon.vue'

interface SectionChip {
  id: string
  label: string
  icon: IconName
}

const props = withDefaults(
  defineProps<{
    activeSection?: string
  }>(),
  {
    activeSection: 'resume',
  }
)

const emit = defineEmits<{
  (e: 'navigate', sectionId: string): void
}>()

const chips: SectionChip[] = [
  { id: 'resume', label: 'Retomar', icon: 'book-open' },
  { id: 'connect', label: 'Conectar', icon: 'network' },
  { id: 'timeline', label: 'Histórico', icon: 'calendar' },
]

function handleSelect(id: string) {
  emit('navigate', id)
  const targetEl = document.getElementById(`section-${id}`)
  if (targetEl) {
    targetEl.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}
</script>

<template>
  <nav class="quick-nav-chips" aria-label="Navegação rápida por seções do dashboard">
    <div class="chips-container" role="tablist">
      <button
        v-for="chip in chips"
        :id="`chip-btn-${chip.id}`"
        :key="chip.id"
        type="button"
        role="tab"
        class="chip-btn"
        :class="{ active: activeSection === chip.id }"
        :aria-selected="activeSection === chip.id"
        :aria-controls="`section-${chip.id}`"
        @click="handleSelect(chip.id)"
      >
        <Icon :name="chip.icon" :size="16" aria-hidden="true" />
        <span>{{ chip.label }}</span>
      </button>
    </div>
  </nav>
</template>

<style scoped>
.quick-nav-chips {
  position: sticky;
  top: 0;
  z-index: 20;
  background: var(--color-background);
  padding: 0.5rem 0;
  margin: -0.5rem 0 1rem 0;
  border-bottom: 1px solid var(--color-border);
}

.chips-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  padding: 0 0.25rem;
  scrollbar-width: none;
}

.chips-container::-webkit-scrollbar {
  display: none;
}

.chip-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  min-height: 44px;
  min-width: 44px;
  padding: 0.5rem 1rem;
  background: var(--color-surface);
  color: var(--color-text-muted);
  border: 1px solid var(--color-border);
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  flex-shrink: 0;
  transition: all 0.15s ease;
}

.chip-btn:hover {
  color: var(--color-text);
  border-color: var(--color-accent);
}

.chip-btn.active {
  background: var(--color-accent);
  color: var(--color-on-accent, #ffffff);
  border-color: var(--color-accent);
  box-shadow: var(--shadow-sm);
}
</style>
