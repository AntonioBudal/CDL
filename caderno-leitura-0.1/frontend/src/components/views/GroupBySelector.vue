<script setup lang="ts">
import type { StudyGroupByCriteria } from '../../types'
import Icon from '../ui/Icon.vue'

interface Props {
  modelValue?: StudyGroupByCriteria
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: 'chapter',
  disabled: false,
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: StudyGroupByCriteria): void
}>()

interface OptionItem {
  id: StudyGroupByCriteria
  label: string
  description: string
}

const options: OptionItem[] = [
  { id: 'chapter', label: 'Por Capítulo', description: 'Ordenação canônica dos capítulos' },
  { id: 'status', label: 'Por Status', description: 'Ciclo de maturação e progresso' },
  { id: 'category', label: 'Por Categoria', description: 'Taxonomia temática' },
  { id: 'date', label: 'Por Data', description: 'Ordem cronológica relativa' },
]

function onChange(event: Event) {
  const target = event.target as HTMLSelectElement
  emit('update:modelValue', target.value as StudyGroupByCriteria)
}
</script>

<template>
  <div class="group-by-selector" role="group" aria-label="Critério de Agrupamento">
    <label for="study-group-by-select" class="selector-label">
      <Icon name="sliders" :size="15" class="selector-icon" aria-hidden="true" />
      <span class="label-text">Agrupar:</span>
    </label>
    <div class="select-wrapper">
      <select
        id="study-group-by-select"
        class="group-by-native-select"
        :value="modelValue"
        :disabled="disabled"
        aria-label="Selecione o critério de agrupamento dos estudos"
        @change="onChange"
      >
        <option
          v-for="opt in options"
          :key="opt.id"
          :value="opt.id"
        >
          {{ opt.label }}
        </option>
      </select>
      <Icon name="chevron-down" :size="14" class="select-chevron" aria-hidden="true" />
    </div>
  </div>
</template>

<style scoped>
.group-by-selector {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-family: inherit;
}

.selector-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary, #4a5568);
  cursor: pointer;
  min-height: 44px;
}

.selector-icon {
  color: var(--text-muted, #718096);
}

.label-text {
  user-select: none;
}

.select-wrapper {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.group-by-native-select {
  appearance: none;
  -webkit-appearance: none;
  min-height: 44px;
  min-width: 140px;
  padding: 8px 32px 8px 12px;
  background-color: var(--bg-surface, #ffffff);
  border: 1px solid var(--border-color, #cbd5e1);
  border-radius: 6px;
  font-family: inherit;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-primary, #1e293b);
  cursor: pointer;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.group-by-native-select:hover:not(:disabled) {
  border-color: var(--border-hover, #94a3b8);
}

.group-by-native-select:focus {
  outline: none;
  border-color: var(--accent-color, #3b82f6);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.group-by-native-select:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background-color: var(--bg-disabled, #f1f5f9);
}

.select-chevron {
  position: absolute;
  right: 10px;
  pointer-events: none;
  color: var(--text-muted, #64748b);
}

@media (max-width: 768px) {
  .group-by-selector {
    width: 100%;
    justify-content: space-between;
  }

  .select-wrapper {
    flex-grow: 1;
  }

  .group-by-native-select {
    width: 100%;
    min-height: 48px;
    font-size: 0.95rem;
  }
}
</style>
