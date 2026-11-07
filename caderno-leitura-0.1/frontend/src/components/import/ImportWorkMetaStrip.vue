<script setup lang="ts">
/**
 * F0.10.06 (spec 099): linha da obra na faixa de metadados da Importar e prévia da referência em 3 escopos
 * (obra, trecho, obras citadas). Completa autor, ano e subtítulo do livro pelo PATCH existente.
 */
import { computed, ref, watch } from 'vue'
import { api, errorMessage } from '../../services/api'
import type { Book, BookPatch, Chapter } from '../../types'
import {
  abntCallWithLocator,
  buildReferenceScopes,
  formatLocator,
} from '../../utils/referenceScopes'

const props = defineProps<{
  book: Book | null | undefined
  chapter: Chapter | null | undefined
  location: string
  referencesText: string
}>()

const emit = defineEmits<{
  (e: 'book-updated', book: Book): void
}>()

const scopes = computed(() =>
  buildReferenceScopes({
    book: props.book,
    chapter: props.chapter ? { name: props.chapter.name } : null,
    location: props.location,
    referencesText: props.referencesText,
  })
)

const citationPreview = computed(() => abntCallWithLocator(scopes.value))
const canEdit = computed(() => !!props.book && props.book.can_edit !== false)

const missingNotice = computed(() => {
  const missing = scopes.value.work.missing
  if (missing.length === 0) return ''
  if (missing.length === 2) return 'Sem autor e sem ano, a citação ABNT sai pelo título e com [s. d.].'
  return missing[0] === 'author'
    ? 'Sem autor, a citação ABNT sai pela primeira palavra do título.'
    : 'Sem ano, a citação ABNT sai com [s. d.].'
})

const passageText = computed(() => {
  const { chapter, locator } = scopes.value.passage
  const parts: string[] = []
  if (chapter) parts.push(chapter)
  parts.push(locator.kind === 'none' ? 'sem localização' : formatLocator(locator))
  return parts.join(' · ')
})

const citedText = computed(() => {
  const count = scopes.value.cited.count
  if (count === 0) return 'nenhuma'
  return count === 1 ? '1 linha na seção Referências' : `${count} linhas na seção Referências`
})

// Formulário "Completar dados do livro"
const editing = ref(false)
const saving = ref(false)
const formError = ref('')
const draftAuthor = ref('')
const draftYear = ref('')
const draftSubtitle = ref('')

const yearError = computed(() => {
  const value = draftYear.value.trim()
  if (!value) return ''
  const year = Number(value)
  if (!Number.isInteger(year) || year < 1000 || year > 2100) return 'Use um ano entre 1000 e 2100.'
  return ''
})

function openForm() {
  if (!props.book) return
  draftAuthor.value = props.book.author || ''
  draftYear.value = props.book.year ? String(props.book.year) : ''
  draftSubtitle.value = props.book.subtitle || ''
  formError.value = ''
  editing.value = true
}

function closeForm() {
  editing.value = false
  formError.value = ''
}

watch(
  () => props.book?.id,
  () => closeForm()
)

async function saveForm() {
  const book = props.book
  if (!book || yearError.value) return
  const payload: BookPatch = {
    author: draftAuthor.value.trim(),
    subtitle: draftSubtitle.value.trim(),
  }
  const year = draftYear.value.trim()
  if (year) payload.year = Number(year)
  if (typeof book.version === 'number') payload.expected_version = book.version
  saving.value = true
  formError.value = ''
  try {
    const updated = await api.updateBook(book.id, payload)
    emit('book-updated', updated)
    editing.value = false
  } catch (error) {
    formError.value = errorMessage(error)
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <section v-if="book" class="work-meta-strip" aria-label="Dados da obra e referência">
    <div class="work-meta-line">
      <span class="work-meta-label">Obra</span>
      <span class="work-meta-values">
        <span :class="{ 'work-meta-missing': !scopes.work.author }">{{ scopes.work.author || 'sem autor' }}</span>
        <span class="work-meta-sep" aria-hidden="true">·</span>
        <span :class="{ 'work-meta-missing': scopes.work.year === null }">{{ scopes.work.year ?? 'sem ano' }}</span>
        <template v-if="scopes.work.subtitle">
          <span class="work-meta-sep" aria-hidden="true">·</span>
          <span class="work-meta-subtitle">{{ scopes.work.subtitle }}</span>
        </template>
      </span>
      <button
        v-if="canEdit && !editing"
        type="button"
        class="quiet work-meta-complete-btn"
        :aria-expanded="editing"
        aria-controls="work-meta-form"
        @click="openForm"
      >
        {{ scopes.work.complete ? 'Editar dados do livro' : 'Completar dados do livro' }}
      </button>
    </div>

    <p v-if="missingNotice && !editing" class="work-meta-notice">{{ missingNotice }}</p>

    <div v-if="editing" id="work-meta-form" class="work-meta-form" role="group" aria-label="Completar dados do livro">
      <div class="work-meta-field">
        <label for="work-meta-author">Autor</label>
        <input id="work-meta-author" v-model="draftAuthor" placeholder="Ex.: Nome Sobrenome; Outro Autor" />
      </div>
      <div class="work-meta-field work-meta-field-year">
        <label for="work-meta-year">Ano</label>
        <input
          id="work-meta-year"
          v-model="draftYear"
          inputmode="numeric"
          maxlength="4"
          placeholder="Ex.: 2001"
          :aria-invalid="!!yearError"
          :aria-describedby="yearError ? 'work-meta-year-error' : undefined"
        />
      </div>
      <div class="work-meta-field">
        <label for="work-meta-subtitle">Subtítulo <span class="optional">opcional</span></label>
        <input id="work-meta-subtitle" v-model="draftSubtitle" />
      </div>
      <div class="work-meta-form-actions">
        <button type="button" class="primary" :disabled="saving || !!yearError" @click="saveForm">
          {{ saving ? 'Salvando…' : 'Salvar no livro' }}
        </button>
        <button type="button" class="quiet" :disabled="saving" @click="closeForm">Cancelar</button>
      </div>
      <p v-if="yearError" id="work-meta-year-error" class="work-meta-error" role="alert">{{ yearError }}</p>
      <p v-if="formError" class="work-meta-error" role="alert">{{ formError }}</p>
    </div>

    <div class="work-meta-scopes" aria-live="polite">
      <span class="work-meta-label">Como este estudo será citado</span>
      <code class="work-meta-citation">{{ citationPreview }}</code>
      <ul class="work-meta-scope-list">
        <li>
          <strong>Obra:</strong>
          {{ scopes.work.complete ? 'completa' : `falta ${scopes.work.missing.map(m => (m === 'author' ? 'autor' : 'ano')).join(' e ')}` }}
        </li>
        <li><strong>Trecho:</strong> {{ passageText }}</li>
        <li><strong>Obras citadas:</strong> {{ citedText }}</li>
      </ul>
    </div>
  </section>
</template>

<style scoped>
.work-meta-strip {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  width: 100%;
  padding-top: 0.75rem;
  border-top: 1px solid var(--color-border);
  font-size: 0.875rem;
  color: var(--color-text);
  min-width: 0;
}

.work-meta-line,
.work-meta-scopes {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem 0.75rem;
  min-width: 0;
}

.work-meta-label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-muted);
}

.work-meta-values {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  min-width: 0;
  overflow-wrap: anywhere;
}

.work-meta-sep {
  color: var(--color-muted);
}

.work-meta-missing {
  color: var(--color-muted);
  font-style: italic;
}

.work-meta-subtitle {
  font-style: italic;
}

.work-meta-complete-btn {
  --quiet-border: var(--color-border-strong, var(--color-border));
  min-height: 44px;
  font-size: 0.8125rem;
}

.work-meta-notice {
  margin: 0;
  font-size: 0.8125rem;
  color: var(--color-muted);
}

.work-meta-form {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 0.5rem 0.75rem;
}

.work-meta-field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  flex: 1 1 12rem;
  min-width: 0;
}

.work-meta-field-year {
  flex: 0 1 7rem;
}

.work-meta-field label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-muted);
}

.work-meta-field input {
  min-height: 44px;
  width: 100%;
  box-sizing: border-box;
}

.work-meta-form-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.work-meta-form-actions .quiet {
  --quiet-border: var(--color-border-strong, var(--color-border));
}

.work-meta-error {
  flex-basis: 100%;
  margin: 0;
  font-size: 0.8125rem;
  color: var(--color-danger-text, var(--color-error-text, var(--color-text)));
}

.work-meta-citation {
  font-family: var(--font-mono, ui-monospace, monospace);
  font-size: 0.8125rem;
  padding: 0.15rem 0.4rem;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background: var(--color-page);
  color: var(--color-text);
  overflow-wrap: anywhere;
}

.work-meta-scope-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem 1rem;
  margin: 0;
  padding: 0;
  list-style: none;
  flex-basis: 100%;
  font-size: 0.8125rem;
  color: var(--color-text);
}

.work-meta-scope-list strong {
  font-weight: 600;
}
</style>
