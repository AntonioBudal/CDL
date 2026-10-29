<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import type { HighlightKind, HighlightLibraryItem } from '../../types'
import { HIGHLIGHT_SEMANTIC_CATEGORIES } from '../../types'
import { formatCitationABNT, formatCitationMarkdown } from '../../utils/citationFormatter'
import Icon from '../ui/Icon.vue'

const props = defineProps<{
  item: HighlightLibraryItem
}>()

const emit = defineEmits<{
  (e: 'edit-note', id: number, studyId: number, note: string): void
  (e: 'delete', id: number, studyId: number): void
  (e: 'copied', text: string): void
}>()

const isEditing = ref(false)
const editedNote = ref(props.item.note || '')
const isConfirmingDelete = ref(false)
const isExpanded = ref(false)
const isCopied = ref(false)
const showCopyMenu = ref(false)
let copyTimer: ReturnType<typeof setTimeout> | null = null

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

const semanticCategory = computed(() => {
  return (
    HIGHLIGHT_SEMANTIC_CATEGORIES[props.item.color] || {
      key: props.item.color,
      label: 'Padrão',
      semanticName: 'Destaque',
      description: 'Marcação de estudo',
    }
  )
})

const kindLabel = computed(() => kindLabels[props.item.kind] || 'Destaque')

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

function fallbackCopyText(text: string) {
  try {
    const textArea = document.createElement('textarea')
    textArea.value = text
    textArea.style.position = 'fixed'
    textArea.style.left = '-999999px'
    textArea.style.top = '-999999px'
    document.body.appendChild(textArea)
    textArea.focus()
    textArea.select()
    document.execCommand('copy')
    textArea.remove()
  } catch {
    // Falha silenciosa
  }
}

async function handleCopyCitation(format: 'abnt' | 'markdown' = 'abnt') {
  showCopyMenu.value = false
  const formattedText =
    format === 'markdown'
      ? formatCitationMarkdown(props.item)
      : formatCitationABNT(props.item)

  try {
    if (navigator?.clipboard?.writeText) {
      await navigator.clipboard.writeText(formattedText)
    } else {
      fallbackCopyText(formattedText)
    }
  } catch {
    fallbackCopyText(formattedText)
  }

  isCopied.value = true
  if (copyTimer) clearTimeout(copyTimer)
  copyTimer = setTimeout(() => {
    isCopied.value = false
    copyTimer = null
  }, 1500)

  emit('copied', formattedText)
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
    class="highlight-card highlight-card-commonplace"
    :class="[`card-tone-${item.color}`, `card-kind-${item.kind}`]"
  >
    <!-- Cabeçalho da Ficha Literária: Obra, Capítulo e Ações de Estudo -->
    <header class="card-header">
      <div class="card-context">
        <RouterLink
          :to="`/livros/${item.book_id}`"
          class="context-book-link"
          :title="`Abrir acervo de ${item.book_title}`"
        >
          <Icon name="book" :size="14" class="context-icon" aria-hidden="true" />
          <strong class="book-title">{{ item.book_title }}</strong>
        </RouterLink>
        <span v-if="item.book_author" class="book-author"> — {{ item.book_author }}</span>
        <template v-if="item.chapter_title">
          <span class="context-separator" aria-hidden="true">•</span>
          <span class="context-chapter" :title="item.chapter_title">
            {{ item.chapter_title }}
          </span>
        </template>
      </div>

      <div class="card-actions-top">
        <!-- Categoria Semântica de Grifo -->
        <span
          class="badge badge-semantic"
          :class="`tone-${item.color}`"
          :title="semanticCategory.description"
        >
          <span class="semantic-dot" aria-hidden="true" />
          <span class="semantic-label">{{ semanticCategory.semanticName }}</span>
        </span>

        <!-- Tipo de Marcação -->
        <span class="badge badge-kind" :class="`kind-${item.kind}`">
          {{ kindLabel }}
        </span>

        <!-- Botão de Cópia Contextual com Microfeedback -->
        <div class="copy-action-wrapper">
          <button
            type="button"
            class="btn-copy-quote"
            :class="{ 'is-copied': isCopied }"
            :title="isCopied ? 'Citação copiada!' : 'Copiar citação (ABNT)'"
            :aria-label="isCopied ? 'Citação copiada' : 'Copiar citação formatada'"
            @click="handleCopyCitation('abnt')"
          >
            <Icon :name="isCopied ? 'check' : 'copy'" :size="15" aria-hidden="true" />
            <span class="copy-btn-text">{{ isCopied ? 'Copiado' : 'Copiar' }}</span>
          </button>

          <!-- Gatilho de Opções de Formato de Cópia -->
          <button
            type="button"
            class="btn-copy-dropdown-trigger"
            title="Mais formatos de citação"
            aria-label="Opções de citação"
            :aria-expanded="showCopyMenu"
            @click="showCopyMenu = !showCopyMenu"
          >
            <Icon name="chevron-down" :size="12" aria-hidden="true" />
          </button>

          <!-- Menu de Formatos -->
          <div v-if="showCopyMenu" class="copy-formats-menu" role="menu">
            <button
              type="button"
              class="copy-menu-item"
              role="menuitem"
              @click="handleCopyCitation('abnt')"
            >
              <Icon name="book-open" :size="14" aria-hidden="true" />
              <span>Formato ABNT (Acadêmico)</span>
            </button>
            <button
              type="button"
              class="copy-menu-item"
              role="menuitem"
              @click="handleCopyCitation('markdown')"
            >
              <Icon name="link" :size="14" aria-hidden="true" />
              <span>Formato Markdown (> citação)</span>
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Corpo da Ficha: Citação Editorial com Aspas Clássicas -->
    <div class="card-body">
      <blockquote
        class="highlight-quote editorial-quote commonplace-quote"
        :class="`border-tone-${item.color}`"
      >
        <span class="editorial-quote-mark" aria-hidden="true">“</span>
        <span class="quote-text">{{ displayText }}</span>
        <span class="editorial-quote-mark" aria-hidden="true">”</span>

        <button
          v-if="isLongText"
          type="button"
          class="btn-toggle-expand"
          :aria-expanded="isExpanded"
          @click="isExpanded = !isExpanded"
        >
          {{ isExpanded ? 'Ver menos' : 'Expandir contexto' }}
        </button>
      </blockquote>

      <!-- Área de Anotação Reflexiva do Leitor / Edição In-Card -->
      <div v-if="isEditing" class="note-edit-box">
        <label :for="`note-input-${item.id}`" class="note-edit-label">
          Anotação pessoal de estudo:
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
            <Icon name="check" :size="15" aria-hidden="true" />
            <span>Salvar nota</span>
          </button>
          <button
            type="button"
            class="btn-action btn-cancel"
            aria-label="Cancelar edição"
            @click="cancelEditing"
          >
            <Icon name="x" :size="15" aria-hidden="true" />
            <span>Cancelar</span>
          </button>
        </div>
      </div>

      <!-- Exibição de Nota Pessoal do Leitor (Bloco Subordinado) -->
      <div v-else-if="item.note" class="reader-note-box">
        <div class="reader-note-header">
          <Icon name="pencil" :size="13" class="reader-note-icon" aria-hidden="true" />
          <span>Anotação de Estudo</span>
          <button
            type="button"
            class="btn-edit-note-inline"
            title="Editar esta anotação"
            aria-label="Editar anotação"
            @click="startEditing"
          >
            <Icon name="pencil" :size="12" aria-hidden="true" />
            <span>Editar</span>
          </button>
        </div>
        <p class="reader-note-content">{{ item.note }}</p>
      </div>

      <!-- Sem nota: Botão Acolhedor para Adicionar Reflexão -->
      <div v-else class="add-note-prompt">
        <button
          type="button"
          class="btn-add-note-inline"
          aria-label="Adicionar anotação a este trecho"
          @click="startEditing"
        >
          <Icon name="plus" :size="13" aria-hidden="true" />
          <span>Adicionar reflexão</span>
        </button>
      </div>
    </div>

    <!-- Rodapé: Metadados Bibliográficos e Ações do Cartão -->
    <footer class="card-footer">
      <div class="footer-meta">
        <span class="date-text" :title="`Registrado em ${item.created_at}`">
          {{ formatDate(item.created_at) }}
        </span>
        <template v-if="item.study_title">
          <span class="meta-dot" aria-hidden="true">•</span>
          <span class="study-crumb" :title="`Estudo: ${item.study_title}`">
            {{ item.study_title }}
          </span>
        </template>
      </div>

      <div class="footer-actions">
        <!-- Confirmação Defensiva de Exclusão -->
        <div v-if="isConfirmingDelete" class="delete-confirmation-banner" role="alert">
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
            <Icon name="trash" :size="16" aria-hidden="true" />
          </button>

          <!-- Salto Contextual: Abrir no Estudo com Âncora -->
          <RouterLink
            :to="`/livros/${item.book_id}/estudos/${item.study_id}#highlight-${item.id}`"
            class="btn-card-action btn-open-study"
            title="Abrir este trecho no estudo original"
            aria-label="Abrir no Estudo"
          >
            <span>Abrir no Estudo</span>
            <Icon name="external-link" :size="14" aria-hidden="true" />
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
  border: 1px solid var(--color-border-subtle, var(--color-border, #e2e8f0));
  border-radius: 10px;
  padding: 1.25rem 1.35rem;
  transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
  position: relative;
  max-width: 100%;
  box-sizing: border-box;
  min-width: 0;
}

.highlight-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.06);
  border-color: var(--color-border-hover, var(--color-border-strong, #cbd5e1));
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
  color: var(--color-text-secondary, #64748b);
  min-width: 0;
}

.context-book-link {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  color: var(--color-text-primary, #0f172a);
  text-decoration: none;
  border-radius: 4px;
}

.context-book-link:hover .book-title {
  color: var(--color-link, var(--color-primary, #2563eb));
  text-decoration: underline;
}

.book-title {
  font-weight: 600;
  max-width: 220px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-author {
  color: var(--color-text-tertiary, var(--color-text-secondary, #64748b));
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.context-separator {
  color: var(--color-border, #cbd5e1);
}

.context-chapter {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-style: italic;
}

.card-actions-top {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
  position: relative;
}

/* Badges Semânticas */
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

.badge-semantic {
  background-color: var(--color-surface-soft, var(--color-surface-subtle, #f1f5f9));
  border: 1px solid var(--color-border-subtle, var(--color-border, #e2e8f0));
  color: var(--color-text-primary, #0f172a);
}

.semantic-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
  background-color: currentColor;
}

/* Tonalidades de Grifo Semânticas */
.badge-semantic.tone-yellow .semantic-dot { color: #eab308; }
.badge-semantic.tone-green .semantic-dot { color: #22c55e; }
.badge-semantic.tone-blue .semantic-dot { color: #3b82f6; }
.badge-semantic.tone-pink .semantic-dot { color: #ec4899; }
.badge-semantic.tone-purple .semantic-dot { color: #a855f7; }

.badge-kind {
  background-color: var(--color-surface-soft, #f8fafc);
  color: var(--color-text-secondary, #64748b);
  border: 1px solid var(--color-border-subtle, #e2e8f0);
}

/* Cópia Contextual */
.copy-action-wrapper {
  display: inline-flex;
  align-items: center;
  position: relative;
}

.btn-copy-quote {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  height: 32px;
  padding: 0 0.6rem;
  font-size: 0.75rem;
  font-weight: 500;
  border: 1px solid var(--color-border, #cbd5e1);
  border-right: none;
  border-radius: 6px 0 0 6px;
  background-color: var(--color-surface, #ffffff);
  color: var(--color-text-secondary, #475569);
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-copy-quote:hover {
  background-color: var(--color-surface-hover, var(--color-surface-soft, #f1f5f9));
  color: var(--color-text-primary, #0f172a);
}

.btn-copy-quote.is-copied {
  color: var(--color-success-text, #166534);
  background-color: var(--color-surface-soft, #f0fdf4);
  border-color: var(--color-border, #86efac);
}

.btn-copy-dropdown-trigger {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 32px;
  width: 24px;
  padding: 0;
  border: 1px solid var(--color-border, #cbd5e1);
  border-radius: 0 6px 6px 0;
  background-color: var(--color-surface, #ffffff);
  color: var(--color-text-secondary, #64748b);
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-copy-dropdown-trigger:hover {
  background-color: var(--color-surface-hover, var(--color-surface-soft, #f1f5f9));
  color: var(--color-text-primary, #0f172a);
}

.copy-formats-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 0.35rem;
  background-color: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #cbd5e1);
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  padding: 0.35rem;
  min-width: 220px;
  z-index: 20;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.copy-menu-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.65rem;
  font-size: 0.8rem;
  text-align: left;
  border: none;
  background: none;
  border-radius: 5px;
  color: var(--color-text-primary, #0f172a);
  cursor: pointer;
  transition: background-color 0.12s ease;
  min-height: 36px;
}

.copy-menu-item:hover {
  background-color: var(--color-surface-hover, var(--color-surface-soft, #f1f5f9));
}

/* Corpo e Citação Editorial */
.card-body {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 0.85rem;
}

.highlight-quote {
  margin: 0;
  padding: 0.85rem 1.1rem;
  background-color: var(--color-surface-soft, rgba(0, 0, 0, 0.02));
  border-radius: 6px;
  border-left: 4px solid var(--color-accent, var(--color-border-strong, #94a3b8));
  position: relative;
}

.border-tone-yellow { border-left-color: #eab308; }
.border-tone-green { border-left-color: #22c55e; }
.border-tone-blue { border-left-color: #3b82f6; }
.border-tone-pink { border-left-color: #ec4899; }
.border-tone-purple { border-left-color: #a855f7; }

.quote-text {
  white-space: pre-wrap;
  word-break: break-word;
}

.btn-toggle-expand {
  display: inline-block;
  margin-top: 0.45rem;
  background: none;
  border: none;
  padding: 0;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--color-link, var(--color-primary, #2563eb));
  cursor: pointer;
  text-decoration: underline;
  text-underline-offset: 3px;
}

.btn-toggle-expand:hover {
  opacity: 0.85;
}

/* Anotação Pessoal */
.note-edit-box {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.75rem;
  background-color: var(--color-surface-soft, #f8fafc);
  border: 1px solid var(--color-border, #cbd5e1);
  border-radius: 8px;
}

.note-edit-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-secondary, #64748b);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.note-textarea {
  width: 100%;
  font-family: inherit;
  font-size: 0.9rem;
  line-height: 1.5;
  padding: 0.5rem 0.65rem;
  border: 1px solid var(--color-border, #cbd5e1);
  border-radius: 6px;
  background-color: var(--color-surface, #ffffff);
  color: var(--color-text-primary, #0f172a);
  resize: vertical;
  outline: none;
  box-sizing: border-box;
}

.note-textarea:focus {
  border-color: var(--color-accent, var(--color-primary, #2563eb));
  box-shadow: 0 0 0 2px var(--ring-focus, rgba(37, 99, 235, 0.2));
}

.note-edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.btn-action {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.4rem 0.75rem;
  font-size: 0.8rem;
  font-weight: 500;
  border-radius: 5px;
  cursor: pointer;
  min-height: 36px;
  border: 1px solid transparent;
}

.btn-save {
  background-color: var(--color-accent, var(--color-primary, #2563eb));
  color: var(--color-on-accent, #ffffff);
}

.btn-save:hover {
  opacity: 0.92;
}

.btn-cancel {
  background: none;
  border-color: var(--color-border, #cbd5e1);
  color: var(--color-text-secondary, #64748b);
}

.btn-cancel:hover {
  background-color: var(--color-surface-hover, #f1f5f9);
}

.btn-edit-note-inline {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  margin-left: auto;
  background: none;
  border: none;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-link, var(--color-primary, #2563eb));
  cursor: pointer;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
}

.btn-edit-note-inline:hover {
  background-color: var(--color-surface-soft, rgba(0, 0, 0, 0.05));
}

.add-note-prompt {
  display: flex;
  margin-top: 0.2rem;
}

.btn-add-note-inline {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  background: none;
  border: 1px dashed var(--color-border, #cbd5e1);
  border-radius: 6px;
  padding: 0.35rem 0.7rem;
  font-size: 0.78rem;
  font-weight: 500;
  color: var(--color-text-secondary, #64748b);
  cursor: pointer;
  min-height: 36px;
  transition: all 0.15s ease;
}

.btn-add-note-inline:hover {
  background-color: var(--color-surface-soft, #f8fafc);
  border-color: var(--color-border-hover, #94a3b8);
  color: var(--color-text-primary, #0f172a);
}

/* Rodapé */
.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding-top: 0.85rem;
  border-top: 1px solid var(--color-border-subtle, var(--color-border, #f1f5f9));
  font-size: 0.75rem;
  color: var(--color-text-secondary, #64748b);
  flex-wrap: wrap;
}

.footer-meta {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.meta-dot {
  color: var(--color-border, #cbd5e1);
}

.study-crumb {
  max-width: 220px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.footer-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-left: auto;
}

.btn-card-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  min-height: 44px;
  min-width: 44px;
  padding: 0 0.75rem;
  font-size: 0.78rem;
  font-weight: 500;
  border-radius: 6px;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-delete {
  background: none;
  border: 1px solid transparent;
  color: var(--color-text-secondary, #94a3b8);
}

.btn-delete:hover {
  color: var(--color-error-text, #ef4444);
  background-color: var(--color-surface-soft, rgba(239, 68, 68, 0.08));
}

.btn-open-study {
  background-color: var(--color-surface-soft, #f8fafc);
  border: 1px solid var(--color-border, #cbd5e1);
  color: var(--color-text-primary, #0f172a);
}

.btn-open-study:hover {
  background-color: var(--color-surface-hover, var(--color-surface-subtle, #f1f5f9));
  border-color: var(--color-border-hover, #94a3b8);
}

/* Confirmação de Exclusão */
.delete-confirmation-banner {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.delete-confirm-text {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-primary, #0f172a);
}

.btn-confirm-delete {
  min-height: 36px;
  padding: 0 0.65rem;
  font-size: 0.75rem;
  font-weight: 600;
  background-color: var(--color-accent, #ef4444);
  color: var(--color-on-accent);
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.btn-cancel-delete {
  min-height: 36px;
  padding: 0 0.65rem;
  font-size: 0.75rem;
  font-weight: 500;
  background: none;
  border: 1px solid var(--color-border, #cbd5e1);
  color: var(--color-text-secondary, #64748b);
  border-radius: 5px;
  cursor: pointer;
}

@media (max-width: 640px) {
  .highlight-card {
    padding: 1rem;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .card-actions-top {
    width: 100%;
    justify-content: space-between;
  }

  .card-context {
    width: 100%;
    min-width: 0;
  }

  .book-title,
  .book-author,
  .context-chapter,
  .study-crumb {
    max-width: 100%;
  }

  .card-footer {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .footer-actions {
    width: 100%;
    flex-wrap: wrap;
    justify-content: flex-start;
    gap: 0.5rem;
  }
}
</style>
