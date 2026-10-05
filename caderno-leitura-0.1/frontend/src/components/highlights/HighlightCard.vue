<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import type { HighlightColor, HighlightKind, HighlightLibraryItem } from '../../types'
import Icon from '../ui/Icon.vue'

const props = defineProps<{
  item: HighlightLibraryItem
}>()

const emit = defineEmits<{
  (e: 'edit-note', id: number, studyId: number, note: string): void
  (e: 'delete', id: number, studyId: number): void
}>()

const isEditing = ref(false)
const editedNote = ref(props.item.note || '')
const isConfirmingDelete = ref(false)
const isExpanded = ref(false)

const maxLength = 260
const isLongText = computed(() => (props.item.selected_text || '').length > maxLength)
const displayText = computed(() => {
  const text = props.item.selected_text || ''
  if (!isLongText.value || isExpanded.value) return text
  return `${text.slice(0, maxLength)}…`
})

const kindLabels: Record<HighlightKind, string> = {
  highlight: 'Destaque',
  note: 'Anotação',
  quote: 'Citação',
  question: 'Pergunta',
  hidden: 'Termo Oculto',
}

const colorLabels: Record<HighlightColor, string> = {
  yellow: 'Amarelo',
  green: 'Verde',
  blue: 'Azul',
  pink: 'Rosa',
  purple: 'Roxo',
}

const kindLabel = computed(() => kindLabels[props.item.kind] || 'Destaque')
const colorLabel = computed(() => colorLabels[props.item.color] || 'Padrão')

watch(
  () => props.item.note,
  (newVal) => {
    if (!isEditing.value) {
      editedNote.value = newVal || ''
    }
  }
)

function startEditing() {
  editedNote.value = props.item.note || ''
  isEditing.value = true
}

function cancelEditing() {
  editedNote.value = props.item.note || ''
  isEditing.value = false
}

function saveNote() {
  isEditing.value = false
  emit('edit-note', props.item.id, props.item.study_id, editedNote.value.trim())
}

function promptDelete() {
  isConfirmingDelete.value = true
}

function cancelDelete() {
  isConfirmingDelete.value = false
}

function confirmDelete() {
  isConfirmingDelete.value = false
  emit('delete', props.item.id, props.item.study_id)
}

function formatDate(isoDate: string): string {
  try {
    const d = new Date(isoDate)
    return d.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    })
  } catch {
    return ''
  }
}
</script>

<template>
  <article
    :id="`highlight-card-${item.id}`"
    class="highlight-card"
    :class="[`card-color-${item.color}`, `card-kind-${item.kind}`]"
  >
    <!-- Cabeçalho do Card: Contexto da Obra e Badges -->
    <header class="card-header">
      <div class="card-context">
        <span class="context-book" :title="item.book_title">
          <Icon name="book" :size="14" class="context-icon" />
          <strong class="book-title">{{ item.book_title }}</strong>
          <span v-if="item.book_author" class="book-author"> — {{ item.book_author }}</span>
        </span>
        <span class="context-separator" aria-hidden="true">•</span>
        <span class="context-chapter" :title="item.chapter_title">
          {{ item.chapter_title }}
        </span>
        <span class="context-separator" aria-hidden="true">•</span>
        <span class="context-study" :title="item.study_title">
          {{ item.study_title }}
        </span>
      </div>

      <div class="card-badges">
        <!-- Badge de Tipo -->
        <span class="badge badge-kind" :class="`kind-${item.kind}`">
          {{ kindLabel }}
        </span>

        <!-- Badge de Cor Cromática -->
        <span class="badge badge-color" :title="`Cor: ${colorLabel}`">
          <span class="color-dot" :class="`dot-${item.color}`" aria-hidden="true" />
          <span class="color-text">{{ colorLabel }}</span>
        </span>
      </div>
    </header>

    <!-- Trecho Destacado -->
    <div class="card-body">
      <blockquote class="highlight-quote" :class="`border-${item.color}`">
        <p class="quote-text">
          <span class="quote-mark">“</span>{{ displayText }}<span class="quote-mark">”</span>
        </p>
        <button
          v-if="isLongText"
          type="button"
          class="btn-toggle-expand"
          @click="isExpanded = !isExpanded"
        >
          {{ isExpanded ? 'Ver menos' : 'Ver mais' }}
        </button>
      </blockquote>

      <!-- Área de Anotação Pessoal / Edição Rápida In-Card -->
      <div v-if="isEditing" class="note-edit-box">
        <label :for="`note-input-${item.id}`" class="note-edit-label">
          Editar nota pessoal:
        </label>
        <textarea
          :id="`note-input-${item.id}`"
          v-model="editedNote"
          rows="3"
          class="note-textarea"
          placeholder="Escreva sua reflexão, síntese ou pergunta..."
          @keydown.ctrl.enter="saveNote"
          @keydown.esc="cancelEditing"
        />
        <div class="note-edit-actions">
          <button
            type="button"
            class="btn-action btn-save"
            aria-label="Salvar anotação"
            @click="saveNote"
          >
            <Icon name="check" :size="16" />
            <span>Salvar</span>
          </button>
          <button
            type="button"
            class="btn-action btn-cancel"
            aria-label="Cancelar edição"
            @click="cancelEditing"
          >
            <Icon name="x" :size="16" />
            <span>Cancelar</span>
          </button>
        </div>
      </div>

      <!-- Exibição de Nota Existente -->
      <div v-else-if="item.note" class="note-display-box">
        <div class="note-header">
          <span class="note-tag">
            <Icon name="pencil" :size="13" class="note-icon" />
            <span>Anotação pessoal</span>
          </span>
          <button
            type="button"
            class="btn-edit-note-inline"
            title="Editar esta anotação"
            aria-label="Editar anotação"
            @click="startEditing"
          >
            <Icon name="pencil" :size="13" />
            <span>Editar</span>
          </button>
        </div>
        <p class="note-content">{{ item.note }}</p>
      </div>

      <!-- Sem nota: Botão para adicionar -->
      <div v-else class="add-note-prompt">
        <button
          type="button"
          class="btn-add-note-inline"
          aria-label="Adicionar anotação a este trecho"
          @click="startEditing"
        >
          <Icon name="plus" :size="13" />
          <span>Adicionar nota</span>
        </button>
      </div>
    </div>

    <!-- Rodapé: Data e Ações do Card -->
    <footer class="card-footer">
      <div class="footer-meta">
        <span class="date-text" :title="`Registrado em ${item.created_at}`">
          {{ formatDate(item.created_at) }}
        </span>
      </div>

      <div class="footer-actions">
        <!-- Confirmação de exclusão in-card -->
        <div v-if="isConfirmingDelete" class="delete-confirmation-banner">
          <span class="delete-confirm-text">Excluir este destaque?</span>
          <button
            type="button"
            class="btn-confirm-delete"
            aria-label="Confirmar exclusão"
            @click="confirmDelete"
          >
            Confirmar
          </button>
          <button
            type="button"
            class="btn-cancel-delete"
            aria-label="Cancelar exclusão"
            @click="cancelDelete"
          >
            Cancelar
          </button>
        </div>

        <template v-else>
          <!-- Botão de Excluir -->
          <button
            type="button"
            class="btn-card-action btn-delete"
            title="Excluir destaque"
            aria-label="Excluir destaque"
            @click="promptDelete"
          >
            <Icon name="trash" :size="16" />
          </button>

          <!-- Salto Contextual: Abrir no Estudo com Âncora -->
          <RouterLink
            :to="`/livros/${item.book_id}/estudos/${item.study_id}#highlight-${item.id}`"
            class="btn-card-action btn-open-study"
            title="Abrir este trecho no estudo original"
            aria-label="Abrir no Estudo"
          >
            <span>Abrir no Estudo</span>
            <Icon name="external-link" :size="15" />
          </RouterLink>
        </template>
      </div>
    </footer>
  </article>
</template>

<style scoped>
.highlight-card {
  display: flex;
  flex-direction: column;
  background-color: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e4e4e7);
  border-radius: 8px;
  padding: 1.15rem;
  transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.highlight-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.07);
  border-color: var(--color-border-hover, #d4d4d8);
}

/* Cabeçalho */
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.85rem;
  flex-wrap: wrap;
}

.card-context {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.35rem;
  font-size: 0.8125rem;
  color: var(--color-text-secondary, #71717a);
  min-width: 0;
}

.context-book {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  color: var(--color-text-primary, #18181b);
}

.book-title {
  font-weight: 600;
  max-width: 220px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-author {
  color: var(--color-text-muted, #a1a1aa);
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.context-separator {
  color: var(--color-text-muted, #d4d4d8);
}

.context-chapter,
.context-study {
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-badges {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.2rem 0.55rem;
  border-radius: 9999px;
  line-height: 1.2;
}

.badge-kind {
  background-color: var(--color-surface-subtle, #f4f4f5);
  color: var(--color-text-secondary, #52525b);
  border: 1px solid var(--color-border, #e4e4e7);
}

.badge-kind.kind-question {
  background-color: #fef3c7;
  color: #92400e;
  border-color: #fde68a;
}

.badge-kind.kind-hidden {
  background-color: #f3f4f6;
  color: #374151;
  border-color: #e5e7eb;
}

.badge-kind.kind-quote {
  background-color: #e0f2fe;
  color: #075985;
  border-color: #bae6fd;
}

.badge-kind.kind-note {
  background-color: #fdf2f8;
  color: #9d174d;
  border-color: #fbcfe8;
}

.badge-color {
  background-color: var(--color-surface-subtle, #f4f4f5);
  border: 1px solid var(--color-border, #e4e4e7);
  color: var(--color-text-secondary, #52525b);
}

.color-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  flex-shrink: 0;
}

.dot-yellow { background-color: #eab308; }
.dot-green { background-color: #22c55e; }
.dot-blue { background-color: #3b82f6; }
.dot-pink { background-color: #ec4899; }
.dot-purple { background-color: #a855f7; }

/* Corpo e Citação */
.card-body {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  margin-bottom: 0.85rem;
}

.highlight-quote {
  margin: 0;
  padding: 0.65rem 0.85rem;
  background-color: var(--color-surface-subtle, #fafafa);
  border-radius: 4px;
  border-left: 4px solid var(--color-primary, #eab308);
  font-size: 0.9375rem;
  line-height: 1.55;
  color: var(--color-text-primary, #18181b);
}

.border-yellow { border-left-color: #eab308; background-color: rgba(254, 240, 138, 0.15); }
.border-green { border-left-color: #22c55e; background-color: rgba(187, 247, 208, 0.15); }
.border-blue { border-left-color: #3b82f6; background-color: rgba(191, 219, 254, 0.15); }
.border-pink { border-left-color: #ec4899; background-color: rgba(251, 207, 232, 0.15); }
.border-purple { border-left-color: #a855f7; background-color: rgba(233, 213, 255, 0.15); }

.quote-text {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
}

.quote-mark {
  color: var(--color-text-muted, #a1a1aa);
  font-family: Georgia, serif;
}

.btn-toggle-expand {
  display: inline-block;
  margin-top: 0.4rem;
  padding: 0;
  background: none;
  border: none;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-primary, #2563eb);
  cursor: pointer;
  text-decoration: underline;
  text-underline-offset: 2px;
}

/* Área de Anotação */
.note-display-box {
  background-color: var(--color-surface-subtle, #f8fafc);
  border: 1px solid var(--color-border, #e2e8f0);
  border-radius: 6px;
  padding: 0.65rem 0.85rem;
}

.note-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.35rem;
}

.note-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-secondary, #64748b);
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.btn-edit-note-inline {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  background: none;
  border: none;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-text-secondary, #64748b);
  cursor: pointer;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  min-height: 28px;
  transition: background-color 0.15s ease, color 0.15s ease;
}

.btn-edit-note-inline:hover {
  background-color: var(--color-surface-hover, #e2e8f0);
  color: var(--color-text-primary, #0f172a);
}

.note-content {
  margin: 0;
  font-size: 0.875rem;
  line-height: 1.5;
  color: var(--color-text-primary, #334155);
  white-space: pre-wrap;
}

.add-note-prompt {
  display: flex;
}

.btn-add-note-inline {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  background: none;
  border: 1px dashed var(--color-border, #cbd5e1);
  border-radius: 6px;
  padding: 0.35rem 0.65rem;
  font-size: 0.8125rem;
  color: var(--color-text-secondary, #64748b);
  cursor: pointer;
  transition: border-color 0.15s ease, color 0.15s ease;
  min-height: 32px;
}

.btn-add-note-inline:hover {
  border-color: var(--color-primary, #3b82f6);
  color: var(--color-primary, #3b82f6);
}

/* Edição de Nota */
.note-edit-box {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  background-color: var(--color-surface-subtle, #f8fafc);
  border: 1px solid var(--color-border, #cbd5e1);
  border-radius: 6px;
  padding: 0.75rem;
}

.note-edit-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-secondary, #64748b);
}

.note-textarea {
  width: 100%;
  border: 1px solid var(--color-border, #cbd5e1);
  border-radius: 4px;
  padding: 0.5rem 0.65rem;
  font-size: 0.875rem;
  line-height: 1.45;
  color: var(--color-text-primary, #0f172a);
  background-color: var(--color-surface, #ffffff);
  resize: vertical;
  font-family: inherit;
  box-sizing: border-box;
}

.note-textarea:focus {
  outline: none;
  border-color: var(--color-primary, #3b82f6);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.note-edit-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  justify-content: flex-end;
}

.btn-action {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.8125rem;
  font-weight: 600;
  padding: 0.35rem 0.75rem;
  border-radius: 4px;
  cursor: pointer;
  min-height: 34px;
  border: 1px solid transparent;
}

.btn-save {
  background-color: var(--color-primary, #2563eb);
  color: #ffffff;
}

.btn-save:hover {
  background-color: var(--color-primary-hover, #1d4ed8);
}

.btn-cancel {
  background-color: var(--color-surface, #ffffff);
  border-color: var(--color-border, #cbd5e1);
  color: var(--color-text-secondary, #64748b);
}

.btn-cancel:hover {
  background-color: var(--color-surface-hover, #f1f5f9);
}

/* Rodapé */
.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-top: auto;
  padding-top: 0.75rem;
  border-top: 1px solid var(--color-border-subtle, #f1f5f9);
}

.footer-meta {
  font-size: 0.75rem;
  color: var(--color-text-muted, #94a3b8);
}

.footer-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-card-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  font-size: 0.8125rem;
  font-weight: 500;
  padding: 0.4rem 0.75rem;
  border-radius: 6px;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.15s ease;
  min-height: 36px;
}

.btn-delete {
  background: none;
  border: 1px solid var(--color-border, #e2e8f0);
  color: var(--color-text-muted, #94a3b8);
  width: 36px;
  padding: 0;
}

.btn-delete:hover {
  background-color: #fef2f2;
  border-color: #fecaca;
  color: #ef4444;
}

.btn-open-study {
  background-color: var(--color-surface-subtle, #f8fafc);
  border: 1px solid var(--color-border, #cbd5e1);
  color: var(--color-text-primary, #1e293b);
}

.btn-open-study:hover {
  background-color: var(--color-primary, #2563eb);
  border-color: var(--color-primary, #2563eb);
  color: #ffffff;
}

/* Confirmação de Exclusão */
.delete-confirmation-banner {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8125rem;
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  padding: 0.3rem 0.6rem;
  border-radius: 6px;
}

.delete-confirm-text {
  color: #b91c1c;
  font-weight: 500;
}

.btn-confirm-delete {
  background-color: #dc2626;
  color: #ffffff;
  border: none;
  border-radius: 4px;
  padding: 0.25rem 0.55rem;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  min-height: 30px;
}

.btn-confirm-delete:hover {
  background-color: #b91c1c;
}

.btn-cancel-delete {
  background: none;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  padding: 0.25rem 0.55rem;
  font-size: 0.75rem;
  color: #475569;
  cursor: pointer;
  min-height: 30px;
}

/* Responsividade e Acessibilidade Móvel (>= 44x44px touch targets) */
@media (max-width: 640px) {
  .highlight-card {
    padding: 1rem;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .card-context {
    font-size: 0.75rem;
  }

  .btn-open-study,
  .btn-action,
  .btn-delete {
    min-height: 44px;
    min-width: 44px;
  }

  .btn-card-action {
    padding: 0.5rem 0.85rem;
  }

  .delete-confirmation-banner {
    flex-wrap: wrap;
    width: 100%;
    justify-content: flex-end;
  }

  .btn-confirm-delete,
  .btn-cancel-delete {
    min-height: 44px;
    padding: 0.5rem 0.75rem;
  }
}
</style>
