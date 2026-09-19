<script setup lang="ts">
import { nextTick, ref, watch } from 'vue'
import BookCover from './BookCover.vue'
import CategorySelector from './CategorySelector.vue'
import Icon from './ui/Icon.vue'
import { api, errorMessage } from '../services/api'
import type { Book } from '../types'

const props = defineProps<{
  book: Book
  open: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'saved', book: Book): void
}>()

const title = ref('')
const author = ref('')
const subtitle = ref('')
const year = ref<string>('')
const selectedCategoryIds = ref<string[]>([])
const error = ref('')
const saving = ref(false)
const titleInput = ref<HTMLInputElement | null>(null)

const currentCover = ref<string | null>(null)
const coverLoading = ref(false)
const coverError = ref('')
const coverSuccess = ref('')
const fileInput = ref<HTMLInputElement | null>(null)
const urlInput = ref('')

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      title.value = props.book.title
      author.value = props.book.author || ''
      subtitle.value = props.book.subtitle || ''
      year.value = props.book.year != null ? String(props.book.year) : ''
      selectedCategoryIds.value = (props.book.categories || []).map((c) => c.id)
      currentCover.value = props.book.cover_image ?? null
      error.value = ''
      coverError.value = ''
      coverSuccess.value = ''
      urlInput.value = ''
      nextTick(() => {
        titleInput.value?.focus()
        titleInput.value?.select()
      })
    }
  },
  { immediate: true },
)

async function onFileSelected(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  if (file.size > 5 * 1024 * 1024) {
    coverError.value = 'O arquivo de imagem excede o limite máximo permitido de 5 MB.'
    return
  }

  coverLoading.value = true
  coverError.value = ''
  coverSuccess.value = ''

  try {
    const res = await api.uploadBookCover(props.book.id, file)
    currentCover.value = res.cover_image
    coverSuccess.value = 'Capa atualizada com sucesso.'
    emit('saved', { ...props.book, cover_image: res.cover_image })
  } catch (err) {
    coverError.value = errorMessage(err)
  } finally {
    coverLoading.value = false
    if (fileInput.value) fileInput.value.value = ''
  }
}

async function importFromUrl() {
  const trimmedUrl = urlInput.value.trim()
  if (!trimmedUrl) {
    coverError.value = 'Informe uma URL direta de imagem.'
    return
  }

  coverLoading.value = true
  coverError.value = ''
  coverSuccess.value = ''

  try {
    const res = await api.importBookCoverFromUrl(props.book.id, trimmedUrl)
    currentCover.value = res.cover_image
    coverSuccess.value = 'Capa importada com sucesso.'
    urlInput.value = ''
    emit('saved', { ...props.book, cover_image: res.cover_image })
  } catch (err) {
    coverError.value = errorMessage(err)
  } finally {
    coverLoading.value = false
  }
}

async function removeCover() {
  coverLoading.value = true
  coverError.value = ''
  coverSuccess.value = ''

  try {
    await api.removeBookCover(props.book.id)
    currentCover.value = null
    coverSuccess.value = 'Capa removida.'
    emit('saved', { ...props.book, cover_image: null })
  } catch (err) {
    coverError.value = errorMessage(err)
  } finally {
    coverLoading.value = false
  }
}

function onKeyDown(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    close()
  }
}

function close() {
  if (saving.value) return
  emit('close')
}

async function save() {
  const trimmedTitle = title.value.trim()
  if (!trimmedTitle) {
    error.value = 'O título do livro é obrigatório.'
    titleInput.value?.focus()
    return
  }

  let parsedYear: number | null = null
  if (year.value.trim()) {
    parsedYear = Number(year.value.trim())
    if (!Number.isInteger(parsedYear) || parsedYear < 1000 || parsedYear > 2100) {
      error.value = 'O ano de publicação deve ser um ano válido com 4 dígitos (entre 1000 e 2100).'
      return
    }
  }

  saving.value = true
  error.value = ''

  try {
    const updated = await api.updateBook(props.book.id, {
      title: trimmedTitle,
      author: author.value.trim() || null,
      subtitle: subtitle.value.trim() || '',
      year: parsedYear,
      category_ids: selectedCategoryIds.value,
      expected_updated_at: props.book.updated_at ?? null,
    })
    emit('saved', updated)
    emit('close')
  } catch (err) {
    error.value = errorMessage(err)
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div
    v-if="open"
    class="modal-backdrop"
    role="presentation"
    @click.self="close"
    @keydown="onKeyDown"
  >
    <div
      class="modal-dialog panel"
      role="dialog"
      aria-modal="true"
      aria-labelledby="edit-book-title"
    >
      <header class="modal-header">
        <h2 id="edit-book-title">Editar metadados do livro</h2>
        <button
          type="button"
          class="modal-close"
          aria-label="Fechar modal"
          :disabled="saving"
          @click="close"
        >
          <Icon name="x" :size="16" />
        </button>
      </header>

      <form @submit.prevent="save">
        <fieldset :disabled="saving">
          <div class="field">
            <label for="edit-book-title-input">
              Título <span class="required" aria-hidden="true">*</span>
            </label>
            <input
              id="edit-book-title-input"
              ref="titleInput"
              v-model="title"
              type="text"
              required
              placeholder="Ex.: A Arte da Guerra"
            />
          </div>

          <div class="field">
            <label for="edit-book-author-input">
              Autor <span class="optional">(opcional)</span>
            </label>
            <input
              id="edit-book-author-input"
              v-model="author"
              type="text"
              placeholder="Ex.: Sun Tzu"
            />
          </div>

          <div class="field">
            <label for="edit-book-subtitle-input">
              Subtítulo <span class="optional">(opcional)</span>
            </label>
            <input
              id="edit-book-subtitle-input"
              v-model="subtitle"
              type="text"
              placeholder="Ex.: Edição Comentada"
            />
          </div>

          <div class="field">
            <label for="edit-book-year-input">
              Ano de publicação <span class="optional">(opcional)</span>
            </label>
            <input
              id="edit-book-year-input"
              v-model="year"
              type="number"
              min="1000"
              max="2100"
              step="1"
              placeholder="Ex.: 2021"
            />
          </div>

          <div class="field">
            <label>
              Categorias <span class="optional">(opcional)</span>
            </label>
            <CategorySelector
              v-model="selectedCategoryIds"
              :disabled="saving"
            />
          </div>

          <div class="field cover-field-section">
            <label class="section-label">Capa do livro</label>
            <div class="cover-manager-layout">
              <div class="cover-preview-box">
                <BookCover
                  :cover-image="currentCover"
                  :title="title || 'Livro'"
                  :author="author"
                  size="sm"
                />
              </div>
              <div class="cover-actions-box">
                <div class="cover-upload-buttons">
                  <input
                    ref="fileInput"
                    type="file"
                    accept="image/*,.jpg,.jpeg,.png,.webp,.gif,.bmp,.tiff"
                    style="display: none"
                    @change="onFileSelected"
                  />
                  <button
                    type="button"
                    class="secondary button-sm"
                    :disabled="coverLoading || saving"
                    @click="fileInput?.click()"
                  >
                    {{ coverLoading ? 'Processando…' : 'Enviar do dispositivo' }}
                  </button>
                  <button
                    v-if="currentCover"
                    type="button"
                    class="secondary danger-action button-sm"
                    :disabled="coverLoading || saving"
                    @click="removeCover"
                  >
                    Remover capa
                  </button>
                </div>
                <div class="cover-url-import">
                  <div class="url-input-group">
                    <input
                      v-model="urlInput"
                      type="url"
                      placeholder="Ou cole a URL direta da imagem"
                      :disabled="coverLoading || saving"
                      @keydown.enter.prevent="importFromUrl"
                    />
                    <button
                      type="button"
                      class="secondary button-sm"
                      :disabled="coverLoading || saving || !urlInput.trim()"
                      @click="importFromUrl"
                    >
                      Importar
                    </button>
                  </div>
                </div>
                <p v-if="coverError" class="notice error-notice" role="alert">{{ coverError }}</p>
                <p v-if="coverSuccess" class="notice success-notice" role="status">{{ coverSuccess }}</p>
              </div>
            </div>
          </div>

          <div v-if="error" class="notice error" role="alert">
            <p>{{ error }}</p>
          </div>

          <div class="modal-actions actions">
            <button
              type="submit"
              class="primary"
              :disabled="saving || !title.trim()"
            >
              {{ saving ? 'Salvando…' : 'Salvar alterações' }}
            </button>
            <button
              type="button"
              class="secondary"
              :disabled="saving"
              @click="close"
            >
              Cancelar
            </button>
          </div>
        </fieldset>
      </form>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: calc(var(--space-unit) * 1.5);
  z-index: 50;
  backdrop-filter: blur(2px);
}

.modal-dialog {
  width: min(100%, 34rem);
  max-height: 90vh;
  overflow-y: auto;
  background: var(--color-surface);
  border-radius: var(--radius-panel);
  box-shadow: var(--shadow-panel);
  padding: calc(var(--space-unit) * 2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: calc(var(--space-unit) * 1.5);
  padding-bottom: calc(var(--space-unit) * 0.75);
  border-bottom: var(--border-width) solid var(--color-border);
}

.modal-close {
  min-height: 2.25rem;
  width: 2.25rem;
  padding: 0;
  background: transparent;
  color: var(--color-muted);
  border: none;
  font-size: 1.125rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover:not(:disabled) {
  color: var(--color-text);
  background: var(--color-surface-hover);
}

.required {
  color: var(--color-accent);
}

.modal-actions {
  margin-top: calc(var(--space-unit) * 2);
  justify-content: flex-end;
}

.cover-field-section {
  margin-top: calc(var(--space-unit) * 1.5);
  padding-top: calc(var(--space-unit) * 1);
  border-top: var(--border-width) solid var(--color-border);
}

.section-label {
  font-weight: 600;
  display: block;
  margin-bottom: calc(var(--space-unit) * 0.75);
}

.cover-manager-layout {
  display: flex;
  gap: calc(var(--space-unit) * 1.5);
  align-items: flex-start;
}

.cover-preview-box {
  flex-shrink: 0;
}

.cover-actions-box {
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  gap: calc(var(--space-unit) * 0.75);
}

.cover-upload-buttons {
  display: flex;
  gap: calc(var(--space-unit) * 0.75);
  flex-wrap: wrap;
}

.cover-url-import .url-input-group {
  display: flex;
  gap: calc(var(--space-unit) * 0.5);
}

.cover-url-import input {
  flex: 1 1 auto;
  font-size: 0.875rem;
}

.button-sm {
  min-height: 2.25rem;
  padding: calc(var(--space-unit) * 0.35) calc(var(--space-unit) * 0.75);
  font-size: 0.875rem;
}

.danger-action {
  color: var(--color-danger, #b91c1c);
}

.danger-action:hover {
  background: var(--color-surface-hover);
  border-color: var(--color-danger, #b91c1c);
}

.success-notice {
  font-size: 0.875rem;
  color: #15803d;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  padding: 0.5rem 0.75rem;
  border-radius: var(--radius-sm, 4px);
  margin: 0;
}

.error-notice {
  font-size: 0.875rem;
  color: var(--color-error-text, #8b241d);
  background: var(--color-error-bg, #fff4f3);
  border: 1px solid var(--color-error-border, #e8b1ad);
  padding: 0.5rem 0.75rem;
  border-radius: var(--radius-sm, 4px);
  margin: 0;
}
</style>
