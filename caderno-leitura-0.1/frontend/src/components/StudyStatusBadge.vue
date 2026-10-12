<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import type { ReadingStatus } from '../types.ts'
import { READING_STATUS_LABELS } from '../composables/useStudyGrouping.ts'
import { updateStudyStatus } from '../services/api.ts'
import Icon from './ui/Icon.vue'

interface Props {
  status?: ReadingStatus | string
  studyId?: number
  interactive?: boolean
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  status: 'rascunho',
  studyId: undefined,
  interactive: false,
  disabled: false,
})

const emit = defineEmits<{
  (e: 'change', newStatus: ReadingStatus): void
}>()

const isOpen = ref(false)
const isUpdating = ref(false)
const containerRef = ref<HTMLElement | null>(null)

function handleDocumentClick(e: MouseEvent) {
  if (isOpen.value && containerRef.value && !containerRef.value.contains(e.target as Node)) {
    isOpen.value = false
  }
}

function handleKeydown(e: KeyboardEvent) {
  if (isOpen.value && e.key === 'Escape') {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleDocumentClick)
  document.addEventListener('keydown', handleKeydown)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleDocumentClick)
  document.removeEventListener('keydown', handleKeydown)
})

const currentMeta = computed(() => {
  const norm = (props.status || 'rascunho').toLowerCase()
  return READING_STATUS_LABELS[norm] || READING_STATUS_LABELS.rascunho
})

const availableStatuses: { id: ReadingStatus; label: string; badgeClass: string }[] = [
  { id: 'rascunho', label: 'Rascunho', badgeClass: 'badge-rascunho' },
  { id: 'em_estudo', label: 'Em Estudo', badgeClass: 'badge-em-estudo' },
  { id: 'revisado', label: 'Revisado', badgeClass: 'badge-revisado' },
  { id: 'concluido', label: 'Concluído', badgeClass: 'badge-concluido' },
]

function toggleDropdown() {
  if (props.interactive && !props.disabled) {
    isOpen.value = !isOpen.value
  }
}

async function selectStatus(newStatus: ReadingStatus) {
  isOpen.value = false
  if (newStatus === props.status) return

  emit('change', newStatus)

  if (props.studyId) {
    try {
      isUpdating.value = true
      await updateStudyStatus(props.studyId, { reading_status: newStatus })
    } catch {
      // Reverter ou tratar erro
    } finally {
      isUpdating.value = false
    }
  }
}
</script>

<template>
  <div
    ref="containerRef"
    class="study-status-badge-container"
    :class="{ 'is-interactive': interactive, 'is-open': isOpen }"
  >
    <button
      v-if="interactive"
      type="button"
      class="status-badge-trigger"
      :class="[currentMeta.badgeClass, { 'is-loading': isUpdating }]"
      :disabled="disabled || isUpdating"
      :aria-expanded="isOpen"
      aria-haspopup="true"
      title="Alterar status de leitura"
      @click.stop="toggleDropdown"
    >
      <span class="status-dot" aria-hidden="true" />
      <span class="status-text">{{ currentMeta.label }}</span>
      <Icon name="chevron-down" :size="12" class="status-chevron" aria-hidden="true" />
    </button>

    <span v-else class="status-badge-pill" :class="currentMeta.badgeClass">
      <span class="status-dot" aria-hidden="true" />
      <span class="status-text">{{ currentMeta.label }}</span>
    </span>

    <div
      v-if="interactive && isOpen"
      class="status-dropdown-menu"
      role="menu"
      aria-label="Selecionar status de leitura"
    >
      <button
        v-for="st in availableStatuses"
        :key="st.id"
        type="button"
        class="status-option-btn"
        :class="{ 'is-current': st.id === status }"
        role="menuitem"
        @click.stop="selectStatus(st.id)"
      >
        <span class="status-pill-small" :class="st.badgeClass">{{ st.label }}</span>
        <Icon v-if="st.id === status" name="check" :size="14" class="current-check-icon" />
      </button>
    </div>
  </div>
</template>

<style scoped>
.study-status-badge-container {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.study-status-badge-container.is-open {
  z-index: 1000;
}

.status-badge-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 2px 8px;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  user-select: none;
}

.status-badge-trigger {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  min-height: 32px;
  padding: 4px 10px;
  border-radius: 9999px;
  font-family: inherit;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  cursor: pointer;
  background: transparent;
  transition: opacity 0.15s ease, transform 0.1s ease;
}

.status-badge-trigger:hover:not(:disabled) {
  opacity: 0.85;
}

.status-badge-trigger:focus-visible {
  outline: 2px solid var(--accent-color, #3b82f6);
  outline-offset: 1px;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: currentColor;
}

.status-chevron {
  opacity: 0.7;
  transition: transform 0.15s ease;
}

.badge-rascunho {
  background-color: transparent;
  color: var(--color-muted);
  border: 1px solid var(--color-border);
}

.badge-em-estudo {
  background-color: transparent;
  color: var(--color-accent);
  border: 1px solid var(--color-accent);
}

.badge-revisado {
  background-color: transparent;
  color: var(--color-warning-text);
  border: 1px solid var(--color-warning-border, var(--color-warning-text));
}

.badge-concluido {
  background-color: transparent;
  color: var(--color-success-text);
  border: 1px solid var(--color-success-text);
}

:root:is([data-theme='noite-suave'], [data-theme='grafite'], [data-theme='fiorde'], [data-theme='voltagem']) .badge-rascunho {
  background-color: transparent;
  color: #e2e8f0;
  border-color: rgba(148, 163, 184, 0.35);
}

:root:is([data-theme='noite-suave'], [data-theme='grafite'], [data-theme='fiorde'], [data-theme='voltagem']) .badge-em-estudo {
  background-color: transparent;
  color: #93c5fd;
  border-color: rgba(59, 130, 246, 0.4);
}

:root:is([data-theme='noite-suave'], [data-theme='grafite'], [data-theme='fiorde'], [data-theme='voltagem']) .badge-revisado {
  background-color: transparent;
  color: #fde68a;
  border-color: rgba(245, 158, 11, 0.4);
}

:root:is([data-theme='noite-suave'], [data-theme='grafite'], [data-theme='fiorde'], [data-theme='voltagem']) .badge-concluido {
  background-color: transparent;
  color: #6ee7b7;
  border-color: rgba(16, 185, 129, 0.4);
}

.status-dropdown-menu {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  z-index: 1000;
  min-width: 155px;
  padding: 4px;
  background-color: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e2e8f0);
  border-radius: 8px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.status-option-btn {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  min-height: 44px;
  padding: 6px 10px;
  background: transparent;
  color: var(--color-text, inherit);
  border: none;
  border-radius: 6px;
  cursor: pointer;
  text-align: left;
}

.status-option-btn:hover {
  background-color: var(--color-surface-soft, #f8fafc);
}

.status-pill-small {
  padding: 2px 8px;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.current-check-icon {
  color: var(--color-accent, #3b82f6);
}
</style>
