<script setup lang="ts">
import { computed, ref } from 'vue'
import { api, errorMessage } from '../../services/api.ts'
import Icon from '../ui/Icon.vue'
import type { InboxCapture } from '../../types.ts'

const props = withDefaults(
  defineProps<{
    capture: InboxCapture
    isSelected?: boolean
    isExiting?: boolean
  }>(),
  {
    isSelected: false,
    isExiting: false,
  }
)

const emit = defineEmits<{
  (e: 'promote', capture: InboxCapture): void
  (e: 'link', capture: InboxCapture): void
  (e: 'archive', capture: InboxCapture): void
  (e: 'unarchive', capture: InboxCapture): void
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
const localExiting = ref(false)

const isCardExiting = computed(() => props.isExiting || localExiting.value)

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

function handleArchive() {
  localExiting.value = true
  emit('archive', props.capture)
}

function handleUnarchive() {
  emit('unarchive', props.capture)
}

function handlePromote() {
  emit('promote', props.capture)
}

function handleLink() {
  emit('link', props.capture)
}

async function handleDelete() {
  if (isDeleting.value) return
  if (!confirm('Deseja realmente excluir esta captura do Inbox?')) return
  isDeleting.value = true
  actionError.value = null
  localExiting.value = true
  try {
    await api.deleteInboxCapture(props.capture.id)
    emit('deleted', props.capture.id)
  } catch (err) {
    localExiting.value = false
    actionError.value = errorMessage(err)
    isDeleting.value = false
  }
}
</script>

<template>
  <article
    class="capture-card"
    :class="{
      'is-keyboard-selected': isSelected,
      'is-exiting': isCardExiting,
      'status-promoted': capture.status === 'promoted',
      'status-linked': capture.status === 'linked',
      'status-archived': capture.status === 'archived',
    }"
    :tabindex="0"
    role="article"
    :aria-label="`Captura: ${capture.content.slice(0, 60)}`"
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
        aria-label="Editar conteúdo da captura"
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
      <div v-if="actionError" class="card-error" role="alert">{{ actionError }}</div>
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
    <footer v-if="!isEditing" class="card-footer">
      <!-- Se pendente: Promover, Vincular, Arquivar -->
      <template v-if="capture.status === 'inbox'">
        <button
          type="button"
          class="button button-sm button-primary promote-action-btn"
          title="Transformar esta captura em um novo estudo formal"
          @click="handlePromote"
        >
          <Icon name="plus" size="xs" />
          <span>Promover para Estudo</span>
        </button>

        <button
          type="button"
          class="button button-sm button-outline link-action-btn"
          title="Anexar esta captura a um estudo existente no acervo"
          @click="handleLink"
        >
          <Icon name="link" size="xs" />
          <span>Vincular a Estudo</span>
        </button>

        <button
          type="button"
          class="button button-sm button-ghost archive-action-btn"
          title="Arquivar captura (E)"
          @click="handleArchive"
        >
          <Icon name="inbox" size="xs" />
          <span>Arquivar</span>
        </button>
      </template>

      <!-- Se arquivado: Desarquivar, Promover -->
      <template v-else-if="capture.status === 'archived'">
        <button
          type="button"
          class="button button-sm button-outline unarchive-action-btn"
          title="Retornar para a caixa de pendentes"
          @click="handleUnarchive"
        >
          <Icon name="inbox" size="xs" />
          <span>Mover para Pendentes</span>
        </button>

        <button
          type="button"
          class="button button-sm button-primary promote-action-btn"
          title="Transformar esta captura em um novo estudo formal"
          @click="handlePromote"
        >
          <Icon name="plus" size="xs" />
          <span>Promover para Estudo</span>
        </button>
      </template>

      <!-- Se promovido ou vinculado: Ações secundárias -->
      <template v-else>
        <button
          type="button"
          class="button button-sm button-outline link-action-btn"
          title="Vincular a outro estudo ou livro"
          @click="handleLink"
        >
          <Icon name="link" size="xs" />
          <span>Reassociar</span>
        </button>
      </template>
    </footer>
  </article>
</template>

<style scoped>
.capture-card {
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md, 8px);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: border-color 0.15s ease, box-shadow 0.15s ease, transform 180ms cubic-bezier(0.2, 0, 0, 1), opacity 180ms ease;
  position: relative;
}

.capture-card:hover {
  border-color: var(--color-border-hover, var(--color-border));
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.capture-card.is-keyboard-selected {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

/* Transição de Saída Acelerada por GPU */
.capture-card.is-exiting {
  transform: translateX(30px);
  opacity: 0;
  pointer-events: none;
}

@media (prefers-reduced-motion: reduce) {
  .capture-card.is-exiting {
    transform: none;
    opacity: 0;
    transition: opacity 100ms ease;
  }
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

/* Imunidade cromática total aos 10 temas */
.badge-inbox {
  background-color: var(--color-surface-hover);
  color: var(--color-primary);
  border: 1px solid var(--color-border);
}

.badge-promoted {
  background-color: var(--color-surface-hover);
  color: var(--color-accent);
  border: 1px solid var(--color-border);
}

.badge-linked {
  background-color: var(--color-surface-hover);
  color: var(--color-text);
  border: 1px solid var(--color-border);
}

.badge-archived {
  background-color: var(--color-surface-hover);
  color: var(--color-text-muted);
  border: 1px solid var(--color-border-subtle);
}

.card-date {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.book-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.75rem;
  color: var(--color-text-muted);
  background-color: var(--color-bg);
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid var(--color-border-subtle);
  max-width: 200px;
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
  color: var(--color-text-muted);
  cursor: pointer;
  padding: 6px;
  border-radius: 4px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  min-height: 32px;
}

.card-action-btn:hover {
  background-color: var(--color-surface-hover);
  color: var(--color-text);
}

.delete-btn:hover {
  color: var(--color-accent);
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.capture-text {
  font-size: 0.95rem;
  line-height: 1.5;
  color: var(--color-text);
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
}

.expand-text-btn {
  align-self: flex-start;
  background: transparent;
  border: none;
  color: var(--color-primary);
  font-size: 0.8rem;
  cursor: pointer;
  padding: 0;
  text-decoration: underline;
}

.source-hint-row {
  display: flex;
  align-items: baseline;
  gap: 6px;
  font-size: 0.8rem;
  color: var(--color-text-muted);
}

.source-label {
  font-weight: 500;
}

.source-value {
  font-style: italic;
}

.promoted-reference {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8rem;
  color: var(--color-text-muted);
  background-color: var(--color-bg);
  padding: 4px 8px;
  border-radius: 4px;
  border: 1px solid var(--color-border-subtle);
  align-self: flex-start;
}

.promoted-study-link {
  color: var(--color-accent);
  text-decoration: underline;
}

.card-footer {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  padding-top: 8px;
  border-top: 1px solid var(--color-border-subtle);
}

.edit-textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md, 6px);
  background-color: var(--color-bg);
  color: var(--color-text);
  font-family: inherit;
  font-size: 0.95rem;
  line-height: 1.4;
  resize: vertical;
}

.edit-source-row {
  margin-top: 6px;
}

.edit-source-input {
  width: 100%;
  padding: 6px 10px;
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-md, 6px);
  background-color: var(--color-bg);
  color: var(--color-text);
  font-size: 0.85rem;
}

.edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 8px;
}

.card-error {
  margin-top: 6px;
  font-size: 0.8rem;
  color: var(--color-accent);
}

/* Responsividade móvel para alvos táteis */
@media (max-width: 640px) {
  .card-footer button {
    min-height: 44px;
    padding: 8px 14px;
  }
}
</style>
