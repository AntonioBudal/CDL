<script setup lang="ts">
import { nextTick, ref, watch } from 'vue'
import type { Chapter } from '../types'
import Icon from './ui/Icon.vue'

// Escolha do capítulo de destino de um estudo (F0.10.02.5); mesma estrutura do TrashConfirmModal.
const props = withDefaults(
  defineProps<{
    open: boolean
    studyTitle: string
    chapters: Chapter[]
    currentChapterId: number
    loading?: boolean
    error?: string
  }>(),
  { loading: false, error: '' },
)

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'confirm', chapterId: number): void
}>()

const selectedId = ref<number | null>(null)
const selectRef = ref<HTMLSelectElement | null>(null)

watch(
  () => props.open,
  (isOpen) => {
    if (!isOpen) return
    selectedId.value = props.chapters.find(c => c.id !== props.currentChapterId)?.id ?? null
    nextTick(() => selectRef.value?.focus())
  },
  { immediate: true },
)

function close() {
  if (!props.loading) emit('close')
}

function confirm() {
  if (props.loading || selectedId.value === null || selectedId.value === props.currentChapterId) return
  emit('confirm', selectedId.value)
}
</script>

<template>
  <Teleport to="body">
    <div v-if="open" class="modal-backdrop" @click.self="close" @keydown.esc="close">
      <div class="modal-dialog panel" role="dialog" aria-modal="true" aria-labelledby="change-chapter-title">
        <header class="modal-header">
          <h2 id="change-chapter-title">Mudar de capítulo</h2>
          <button type="button" class="modal-close quiet" aria-label="Fechar diálogo" :disabled="loading" @click="close">
            <Icon name="x" :size="16" />
          </button>
        </header>

        <form class="modal-body" @submit.prevent="confirm">
          <p class="change-message">
            Escolha o capítulo para onde vai o estudo “{{ studyTitle }}”. Os subestudos vão junto, e ele entra no fim do
            capítulo escolhido.
          </p>
          <label for="change-chapter-select" class="change-label">Capítulo de destino</label>
          <select id="change-chapter-select" ref="selectRef" v-model="selectedId" class="change-select" :disabled="loading">
            <option v-for="(chapter, idx) in chapters" :key="chapter.id" :value="chapter.id" :disabled="chapter.id === currentChapterId">
              {{ idx + 1 }}. {{ chapter.name }}{{ chapter.id === currentChapterId ? ' (atual)' : '' }}
            </option>
          </select>
          <p v-if="chapters.length < 2" class="change-hint">Este livro tem um só capítulo. Crie outro na página do livro.</p>
          <p v-if="error" class="notice error" role="alert">{{ error }}</p>

          <footer class="modal-actions">
            <button type="button" class="secondary" :disabled="loading" @click="close">Cancelar</button>
            <button type="submit" class="primary" :disabled="loading || selectedId === null || selectedId === currentChapterId">
              {{ loading ? 'Movendo...' : 'Mover estudo' }}
            </button>
          </footer>
        </form>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background-color: color-mix(in srgb, var(--color-text) 55%, transparent);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
  padding: 1rem;
}

.modal-dialog {
  width: 100%;
  max-width: 480px;
  background: var(--color-surface);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--color-border);
}

.modal-header h2 {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 600;
}

.modal-close {
  min-width: 44px;
  min-height: 44px;
  padding: 0;
  border-radius: 6px;
}

.modal-body {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.change-message,
.change-hint {
  margin: 0;
  line-height: 1.5;
  font-size: 0.95rem;
}

.change-hint {
  color: var(--color-muted);
}

.change-label {
  font-weight: 600;
  font-size: 0.9rem;
}

.change-select {
  min-height: 44px;
  width: 100%;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-top: 0.5rem;
}

@media (max-width: 480px) {
  .modal-actions button {
    flex: 1 1 100%;
  }
}
</style>
