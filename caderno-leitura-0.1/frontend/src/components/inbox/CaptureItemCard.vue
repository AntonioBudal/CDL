<script setup lang="ts">
import { computed, ref } from 'vue'
import { api, errorMessage } from '../../services/api'
import Icon from '../ui/Icon.vue'
import type { InboxCapture } from '../../types'

const props = defineProps<{
  capture: InboxCapture
}>()

const emit = defineEmits<{
  (e: 'promote', capture: InboxCapture): void
  (e: 'link', capture: InboxCapture): void
  (e: 'updated', capture: InboxCapture): void
  (e: 'deleted', captureId: number): void
}>()

const isEditing = ref(false)
const editContent = ref(props.capture.content)
const editSourceHint = ref(props.capture.source_hint || '')
const isSaving = ref(false)
const isDeleting = ref(false)
const isExpanded = ref(false)
const actionError = ref<string | null>(null)

const isLongText = computed(() => props.capture.content.length > 280)
const displayContent = computed(() => {
  if (!isLongText.value || isExpanded.value) {
    return props.capture.content
  }
  return props.capture.content.slice(0, 280) + '...'
})

const formattedDate = computed(() => {
  try {
    const d = new Date(props.capture.created_at)
    return d.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return props.capture.created_at
  }
})

const statusLabel = computed(() => {
  switch (props.capture.status) {
    case 'inbox':
      return 'Pendente'
    case 'promoted':
      return 'Promovido'
    case 'linked':
      return 'Vinculado'
    case 'archived':
      return 'Arquivado'
    default:
      return props.capture.status
  }
})

function startEdit() {
  editContent.value = props.capture.content
  editSourceHint.value = props.capture.source_hint || ''
  actionError.value = null
  isEditing.value = true
}

function cancelEdit() {
  isEditing.value = false
  actionError.value = null
}

async function saveEdit() {
  if (!editContent.value.trim() || isSaving.value) return
  isSaving.value = true
  actionError.value = null
  try {
    const updated = await api.updateInboxCapture(props.capture.id, {
      content: editContent.value.trim(),
      source_hint: editSourceHint.value.trim() || null,
    })
    isEditing.value = false
    emit('updated', updated)
  } catch (err) {
    actionError.value = errorMessage(err)
  } finally {
    isSaving.value = false
  }
}

async function handleDelete() {
  if (isDeleting.value) return
  if (!confirm('Deseja realmente excluir esta captura do Inbox?')) return
  isDeleting.value = true
  actionError.value = null
  try {
    await api.deleteInboxCapture(props.capture.id)
    emit('deleted', props.capture.id)
  } catch (err) {
    actionError.value = errorMessage(err)
    isDeleting.value = false
  }
}
</script>

<template>
  <article
    class="capture-card"
    :class="{
      'status-promoted': capture.status === 'promoted',
      'status-linked': capture.status === 'linked',
      'status-archived': capture.status === 'archived',
    }"
  >
    <header class="card-header">
      <div class="card-meta">
        <span class="status-badge" :class="`badge-${capture.status}`">
          {{ statusLabel }}
        </span>
        <span class="card-date">{{ formattedDate }}</span>
        <span v-if="capture.book_title" class="book-badge" :title="`Livro: ${capture.book_title}`">
          <Icon name="book" size="xs" />
          <span class="truncate">{{ capture.book_title }}</span>
        </span>
      </div>

      <div class="header-actions">
        <button
          v-if="!isEditing"
          type="button"
          class="card-action-btn"
          aria-label="Editar captura"
          title="Editar captura"
          @click="startEdit"
        >
          <Icon name="pencil" size="xs" />
        </button>
        <button
          type="button"
          class="card-action-btn delete-btn"
          aria-label="Excluir captura"
          title="Excluir captura"
          :disabled="isDeleting"
          @click="handleDelete"
        >
          <Icon name="trash" size="xs" />
        </button>
      </div>
    </header>

    <!-- Visualização de Conteúdo -->
    <div v-if="!isEditing" class="card-body">
      <p class="capture-text">{{ displayContent }}</p>
      <button
        v-if="isLongText"
        type="button"
        class="expand-text-btn"
        @click="isExpanded = !isExpanded"
      >
        {{ isExpanded ? 'Ver menos' : 'Ver texto completo' }}
      </button>

      <div v-if="capture.source_hint" class="source-hint-row">
        <span class="source-label">Fonte:</span>
        <span class="source-value">{{ capture.source_hint }}</span>
      </div>

      <!-- Referência a Estudo Promovido ou Vinculado -->
      <div v-if="capture.promoted_study_id" class="promoted-reference">
        <Icon name="link" size="xs" />
        <span>Estudo associado:</span>
        <RouterLink
          :to="`/estudos/${capture.promoted_study_id}`"
          class="promoted-study-link"
        >
          {{ capture.promoted_study_title || `Estudo #${capture.promoted_study_id}` }}
        </RouterLink>
      </div>
    </div>

    <!-- Modo de Edição Inline -->
    <div v-else class="card-edit-form">
      <textarea
        v-model="editContent"
        class="edit-textarea"
        rows="3"
        required
        :disabled="isSaving"
      ></textarea>
      <div class="edit-source-row">
        <label for="edit-source-input" class="visually-hidden">Fonte</label>
        <input
          id="edit-source-input"
          v-model="editSourceHint"
          type="text"
          class="edit-source-input"
          placeholder="Fonte ou referência (opcional)"
          :disabled="isSaving"
        />
      </div>
      <div v-if="actionError" class="card-error">{{ actionError }}</div>
      <div class="edit-actions">
        <button
          type="button"
          class="button button-sm button-ghost"
          :disabled="isSaving"
          @click="cancelEdit"
        >
          Cancelar
        </button>
        <button
          type="button"
          class="button button-sm button-primary"
          :disabled="isSaving || !editContent.trim()"
          @click="saveEdit"
        >
          {{ isSaving ? 'Salvando...' : 'Salvar' }}
        </button>
      </div>
    </div>

    <!-- Rodapé de Ações de Triagem -->
    <footer v-if="!isEditing && capture.status === 'inbox'" class="card-footer">
      <button
        type="button"
        class="button button-sm button-primary promote-action-btn"
        title="Transformar esta captura em um novo estudo formal"
        @click="emit('promote', capture)"
      >
        <Icon name="plus" size="xs" />
        <span>Promover para Estudo</span>
      </button>

      <button
        type="button"
        class="button button-sm button-outline link-action-btn"
        title="Anexar esta captura a um estudo existente no acervo"
        @click="emit('link', capture)"
      >
        <Icon name="link" size="xs" />
        <span>Vincular a Estudo</span>
      </button>
    </footer>
  </article>
</template>

<style scoped>
.capture-card {
  background-color: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: var(--radius-md, 8px);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.capture-card:hover {
  border-color: var(--color-border-hover, #d1d5db);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.card-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.status-badge {
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding: 2px 6px;
  border-radius: 4px;
}

.badge-inbox {
  background-color: #eff6ff;
  color: #2563eb;
  border: 1px solid #bfdbfe;
}

.badge-promoted {
  background-color: #ecfdf5;
  color: #059669;
  border: 1px solid #a7f3d0;
}

.badge-linked {
  background-color: #f5f3ff;
  color: #7c3aed;
  border: 1px solid #ddd6fe;
}

.badge-archived {
  background-color: #f3f4f6;
  color: #6b7280;
  border: 1px solid #e5e7eb;
}

.card-date {
  font-size: 0.75rem;
  color: var(--color-text-muted, #9ca3af);
}

.book-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.75rem;
  background-color: var(--color-surface-hover, #f3f4f6);
  padding: 2px 6px;
  border-radius: 4px;
  color: var(--color-text-muted, #4b5563);
  max-width: 180px;
}

.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.card-action-btn {
  background: transparent;
  border: none;
  padding: 6px;
  border-radius: 4px;
  color: var(--color-text-muted, #9ca3af);
  cursor: pointer;
  min-height: 36px;
  min-width: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
}

.card-action-btn:hover {
  background-color: var(--color-surface-hover, #f3f4f6);
  color: var(--color-text-main, #111827);
}

.card-action-btn.delete-btn:hover {
  background-color: #fef2f2;
  color: #dc2626;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.capture-text {
  margin: 0;
  font-size: 0.95rem;
  line-height: 1.55;
  color: var(--color-text-main, #1f2937);
  white-space: pre-wrap;
  word-break: break-word;
}

.expand-text-btn {
  background: none;
  border: none;
  padding: 0;
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--color-primary, #4f46e5);
  cursor: pointer;
  text-align: left;
  margin-top: 2px;
}

.expand-text-btn:hover {
  text-decoration: underline;
}

.source-hint-row {
  display: flex;
  align-items: baseline;
  gap: 6px;
  font-size: 0.8rem;
  color: var(--color-text-muted, #6b7280);
  background-color: var(--color-surface-input, #fafafa);
  padding: 4px 8px;
  border-radius: 4px;
  border-left: 3px solid var(--color-border, #d1d5db);
}

.source-label {
  font-weight: 600;
}

.promoted-reference {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8rem;
  color: var(--color-text-muted, #6b7280);
  margin-top: 4px;
}

.promoted-study-link {
  color: var(--color-primary, #4f46e5);
  font-weight: 500;
  text-decoration: none;
}

.promoted-study-link:hover {
  text-decoration: underline;
}

.card-edit-form {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.edit-textarea {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid var(--color-border, #d1d5db);
  border-radius: 6px;
  font-family: inherit;
  font-size: 0.925rem;
  color: var(--color-text-main, #111827);
  resize: vertical;
}

.edit-source-input {
  width: 100%;
  padding: 6px 10px;
  border: 1px solid var(--color-border, #d1d5db);
  border-radius: 6px;
  font-size: 0.825rem;
}

.edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.card-error {
  font-size: 0.75rem;
  color: #dc2626;
}

.card-footer {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  padding-top: 10px;
  border-top: 1px solid var(--color-border-subtle, #f3f4f6);
}

.button {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
  border-radius: 6px;
  cursor: pointer;
  min-height: 40px;
  padding: 6px 12px;
  font-size: 0.825rem;
  transition: all 0.15s ease;
  border: 1px solid transparent;
}

.button-sm {
  min-height: 38px;
  padding: 4px 10px;
}

.button-primary {
  background-color: var(--color-accent, #2563eb);
  color: #ffffff;
}

.button-primary:hover:not(:disabled) {
  background-color: var(--color-accent-hover, #1d4ed8);
}

.button-outline {
  background-color: transparent;
  border-color: var(--color-border, #d1d5db);
  color: var(--color-text, #374151);
}

.button-outline:hover:not(:disabled) {
  background-color: var(--color-surface-hover, #f3f4f6);
  border-color: var(--color-border-hover, #9ca3af);
  color: var(--color-text, #111827);
}

.button-ghost {
  background-color: transparent;
  color: var(--color-muted, #6b7280);
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}
</style>
