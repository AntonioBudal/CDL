<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import type { HighlightColor, StudyHighlight } from '../types.ts'

const props = withDefaults(
  defineProps<{
    highlight: StudyHighlight | null
    boundingRect: DOMRect | null
    canEdit?: boolean
  }>(),
  {
    canEdit: true,
  },
)

const emit = defineEmits<{
  (e: 'change-color', color: HighlightColor): void
  (e: 'update-note', note: string): void
  (e: 'delete'): void
  (e: 'close'): void
}>()

const popoverRef = ref<HTMLElement | null>(null)
const editingNote = ref(false)
const noteDraft = ref('')

const colors: { id: HighlightColor; label: string; bg: string; border: string }[] = [
  { id: 'yellow', label: 'Amarelo', bg: '#fef08a', border: '#facc15' },
  { id: 'green', label: 'Verde', bg: '#bbf7d0', border: '#4ade80' },
  { id: 'blue', label: 'Azul', bg: '#bae6fd', border: '#38bdf8' },
  { id: 'pink', label: 'Rosa', bg: '#fbcfe8', border: '#f472b6' },
  { id: 'purple', label: 'Lilás', bg: '#e9d5ff', border: '#c084fc' },
]

const positionStyle = computed(() => {
  if (!props.highlight || !props.boundingRect) return { display: 'none' }

  const rect = props.boundingRect
  const vpWidth = typeof window !== 'undefined' ? window.innerWidth : 1280
  const vpHeight = typeof window !== 'undefined' ? window.innerHeight : 800

  const popoverWidth = popoverRef.value?.offsetWidth || 260
  const popoverHeight = popoverRef.value?.offsetHeight || 44

  const horizontalCenter = rect.left + rect.width / 2
  const idealLeft = horizontalCenter - popoverWidth / 2
  const clampedLeft = Math.max(10, Math.min(idealLeft, vpWidth - popoverWidth - 10))

  let idealTop = rect.bottom + 8
  if (idealTop + popoverHeight > vpHeight - 10) {
    idealTop = rect.top - popoverHeight - 8
  }
  const clampedTop = Math.max(10, Math.min(idealTop, vpHeight - popoverHeight - 10))

  return {
    position: 'fixed' as const,
    top: `${Math.round(clampedTop)}px`,
    left: `${Math.round(clampedLeft)}px`,
    zIndex: 9999,
  }
})

function selectColor(color: HighlightColor) {
  emit('change-color', color)
}

function startEditingNote() {
  editingNote.value = true
  noteDraft.value = props.highlight?.note || ''
}

function saveNote() {
  emit('update-note', noteDraft.value.trim())
  editingNote.value = false
}

function cancelNote() {
  editingNote.value = false
}

function handleDelete() {
  emit('delete')
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') {
    emit('close')
  }
}

function handleClickOutside(e: MouseEvent) {
  if (!props.highlight || !popoverRef.value) return
  const target = e.target as Node
  if (!popoverRef.value.contains(target)) {
    emit('close')
  }
}

watch(
  () => props.highlight,
  (hl) => {
    editingNote.value = false
    noteDraft.value = hl?.note || ''
  },
)

onMounted(() => {
  if (typeof window !== 'undefined') {
    window.addEventListener('keydown', handleKeydown)
    document.addEventListener('mousedown', handleClickOutside)
  }
})

onBeforeUnmount(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('keydown', handleKeydown)
    document.removeEventListener('mousedown', handleClickOutside)
  }
})
</script>

<template>
  <div
    v-if="highlight && boundingRect"
    ref="popoverRef"
    class="highlight-popover"
    :style="positionStyle"
    role="dialog"
    aria-label="Gerenciar destaque"
  >
    <!-- Modo de Edição de Nota/Pergunta -->
    <div v-if="editingNote" class="popover-edit-note">
      <textarea
        v-model="noteDraft"
        class="popover-textarea"
        rows="2"
        :placeholder="highlight.kind === 'question' ? 'Edite a pergunta…' : 'Edite sua reflexão…'"
        @keydown.enter.prevent="saveNote"
      ></textarea>
      <div class="popover-note-actions">
        <button type="button" class="btn-save" @click="saveNote">Salvar</button>
        <button type="button" class="btn-cancel" @click="cancelNote">Cancelar</button>
      </div>
    </div>

    <!-- Barra de Ações Rápidas -->
    <div v-else class="popover-actions-row">
      <!-- Seletor de cores (apenas se for highlight ou note) -->
      <div v-if="canEdit && highlight.kind !== 'hidden'" class="color-picker-inline">
        <button
          v-for="color in colors"
          :key="color.id"
          type="button"
          class="color-dot-btn"
          :class="{ active: highlight.color === color.id }"
          :style="{ backgroundColor: color.bg, borderColor: color.border }"
          :title="color.label"
          :aria-label="color.label"
          @click="selectColor(color.id)"
        ></button>
      </div>

      <!-- Botão para editar nota/pergunta vinculada -->
      <button
        v-if="canEdit && (highlight.kind === 'note' || highlight.kind === 'question')"
        type="button"
        class="action-btn"
        :title="highlight.kind === 'question' ? 'Editar pergunta' : 'Editar anotação'"
        @click="startEditingNote"
      >
        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 20h9" />
          <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
        </svg>
      </button>

      <!-- Botão de exclusão do destaque -->
      <button
        v-if="canEdit"
        type="button"
        class="action-btn danger-btn"
        title="Remover marcação"
        aria-label="Remover marcação"
        @click="handleDelete"
      >
        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="3 6 5 6 21 6" />
          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
        </svg>
      </button>

      <!-- Fechar -->
      <button
        type="button"
        class="action-btn"
        title="Fechar"
        aria-label="Fechar popover"
        @click="emit('close')"
      >
        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18" />
          <line x1="6" y1="6" x2="18" y2="18" />
        </svg>
      </button>
    </div>
  </div>
</template>

<style scoped>
.highlight-popover {
  background: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e4e4e7);
  border-radius: 12px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.12), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  padding: 6px 8px;
  user-select: none;
  font-family: inherit;
  font-size: 0.8125rem;
}

.popover-actions-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.color-picker-inline {
  display: flex;
  align-items: center;
  gap: 4px;
}

.color-dot-btn {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 2px solid transparent;
  cursor: pointer;
  transition: transform 0.15s ease;
}

.color-dot-btn:hover {
  transform: scale(1.25);
}

.color-dot-btn.active {
  box-shadow: 0 0 0 2px var(--color-text-primary, #18181b);
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  color: var(--color-text-muted, #71717a);
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.15s ease, color 0.15s ease;
}

.action-btn:hover {
  background: var(--color-surface-hover, rgba(0, 0, 0, 0.06));
  color: var(--color-text-primary, #18181b);
}

.action-btn.danger-btn:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.action-btn svg {
  width: 14px;
  height: 14px;
}

.popover-edit-note {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 220px;
}

.popover-textarea {
  width: 100%;
  padding: 6px 8px;
  border: 1px solid var(--color-border, #e4e4e7);
  border-radius: 6px;
  background: var(--color-background, #fbfbfb);
  color: var(--color-text-primary, #18181b);
  font-family: inherit;
  font-size: 0.8125rem;
  resize: none;
  box-sizing: border-box;
}

.popover-textarea:focus {
  outline: 2px solid var(--color-primary, #3b82f6);
  border-color: transparent;
}

.popover-note-actions {
  display: flex;
  justify-content: flex-end;
  gap: 6px;
}

.btn-save {
  padding: 3px 8px;
  font-size: 0.75rem;
  font-weight: 500;
  background: var(--color-primary, #18181b);
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-cancel {
  padding: 3px 8px;
  font-size: 0.75rem;
  background: transparent;
  color: var(--color-text-muted, #71717a);
  border: none;
  cursor: pointer;
}
</style>
