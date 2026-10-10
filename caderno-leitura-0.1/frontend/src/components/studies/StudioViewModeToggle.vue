<script setup lang="ts">
export type StudioViewMode = 'split' | 'source' | 'preview'

defineProps<{
  modelValue: StudioViewMode
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: StudioViewMode): void
}>()

function setMode(mode: StudioViewMode) {
  emit('update:modelValue', mode)
}
</script>

<template>
  <div
    class="studio-view-toggle"
    role="group"
    aria-label="Modo de visualização do ateliê"
  >
    <button
      type="button"
      class="toggle-btn"
      :class="{ 'is-active': modelValue === 'split' }"
      :aria-pressed="modelValue === 'split'"
      title="Visualização dividida (50/50)"
      @click="setMode('split')"
    >
      <svg class="toggle-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <rect x="3" y="3" width="18" height="18" rx="2" />
        <line x1="12" y1="3" x2="12" y2="21" />
      </svg>
      <span class="toggle-label">Dividido</span>
    </button>

    <button
      type="button"
      class="toggle-btn"
      :class="{ 'is-active': modelValue === 'source' }"
      :aria-pressed="modelValue === 'source'"
      title="Foco exclusivo no editor da fonte"
      @click="setMode('source')"
    >
      <svg class="toggle-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <rect x="3" y="3" width="18" height="18" rx="2" />
        <line x1="7" y1="8" x2="17" y2="8" />
        <line x1="7" y1="12" x2="15" y2="12" />
        <line x1="7" y1="16" x2="12" y2="16" />
      </svg>
      <span class="toggle-label">Fonte</span>
    </button>

    <button
      type="button"
      class="toggle-btn"
      :class="{ 'is-active': modelValue === 'preview' }"
      :aria-pressed="modelValue === 'preview'"
      title="Foco exclusivo na prévia estruturada"
      @click="setMode('preview')"
    >
      <svg class="toggle-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <rect x="3" y="3" width="18" height="18" rx="2" />
        <path d="M7 12l3 3 7-7" />
      </svg>
      <span class="toggle-label">Prévia</span>
    </button>
  </div>
</template>

<style scoped>
.studio-view-toggle {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  padding: 3px;
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm, 6px);
}

.toggle-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 10px;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text-muted);
  background: transparent;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 150ms ease, color 150ms ease;
  min-height: 32px;
}

.toggle-btn:hover {
  color: var(--color-text);
  background-color: var(--color-page);
}

.toggle-btn.is-active {
  color: var(--color-accent);
  background-color: var(--color-page);
  font-weight: 600;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.toggle-icon {
  width: 14px;
  height: 14px;
}

.toggle-label {
  white-space: nowrap;
}

@media (max-width: 640px) {
  .toggle-label {
    display: none;
  }
}
</style>
