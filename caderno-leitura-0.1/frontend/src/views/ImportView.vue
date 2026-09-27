<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { api, errorMessage } from '../services/api'
import { useImportDraft } from '../composables/useImportDraft'
import { useUnsavedChanges } from '../composables/useUnsavedChanges'
import StudyEditorFields from '../components/StudyEditorFields.vue'
import MarkdownToolbar from '../components/MarkdownToolbar.vue'
import { positiveId, SECTION_LABELS, type Book, type Chapter } from '../types'

const route = useRoute()
const draft = useImportDraft(api)
const { state, stale, hasManualChanges, hasAnalysis, canSave, assignUnassignedToSection } = draft
useUnsavedChanges(() => draft.dirty.value, () => state.preparing || state.saving)
const books = ref<Book[]>([])
const chapters = ref<Chapter[]>([])
const booksLoading = ref(true)
const chaptersLoading = ref(false)
const booksError = ref('')
const chaptersError = ref('')
const reviewHeading = ref<HTMLElement | null>(null)
const sourceInput = ref<HTMLTextAreaElement | null>(null)
const successHeading = ref<HTMLElement | null>(null)
const selectedBook = computed(() => books.value.find(item => item.id === positiveId(state.bookId)))
const selectedChapter = computed(() => chapters.value.find(item => item.id === positiveId(state.chapterId) && item.book_id === positiveId(state.bookId)))
let bookRequest: AbortController | null = null
let chapterRequest: AbortController | null = null
let preferredChapter = positiveId(route.query.chapter)
state.bookId = positiveId(route.query.book)?.toString() ?? ''

async function loadBooks() {
  bookRequest?.abort()
  const controller = new AbortController()
  bookRequest = controller
  booksLoading.value = true
  booksError.value = ''
  try {
    const result = await api.listBooks(controller.signal)
    if (controller.signal.aborted) return
    books.value = result
    if (state.bookId && !selectedBook.value) state.bookId = ''
  } catch (error) {
    if (!controller.signal.aborted) booksError.value = errorMessage(error)
  } finally { if (!controller.signal.aborted) booksLoading.value = false }
}

async function loadChapters() {
  chapterRequest?.abort()
  const controller = new AbortController()
  chapterRequest = controller
  state.chapterId = ''
  chapters.value = []
  chaptersError.value = ''
  const id = positiveId(state.bookId)
  chaptersLoading.value = id !== null
  if (id === null) return
  try {
    const result = await api.listChapters(id, controller.signal)
    if (controller.signal.aborted) return
    chapters.value = result
    const preferred = result.find(item => item.id === preferredChapter)
    state.chapterId = preferred?.id.toString() ?? (result.length === 1 ? String(result[0]!.id) : '')
    preferredChapter = null
  } catch (error) {
    if (!controller.signal.aborted) chaptersError.value = errorMessage(error)
  } finally { if (!controller.signal.aborted) chaptersLoading.value = false }
}

async function prepare() {
  if (hasManualChanges.value && !window.confirm('Preparar novamente substituirá as correções das quatro seções. Suas anotações serão mantidas. Continuar?')) return
  if (await draft.prepare()) { await nextTick(); reviewHeading.value?.focus() }
}

async function onPaste(event: ClipboardEvent) {
  const text = event.clipboardData?.getData('text')
  if (text && text.trim()) {
    state.sourceResponse = text
    await nextTick()
    if (await draft.prepare()) {
      await nextTick()
      reviewHeading.value?.focus()
    }
  }
}

async function save() {
  if (!selectedBook.value || !selectedChapter.value || chaptersLoading.value) {
    state.saveError = 'Selecione um livro e um capítulo disponíveis.'
    return
  }
  if (await draft.save()) { await nextTick(); successHeading.value?.focus() }
}

async function startAnother() {
  draft.reset()
  await nextTick()
  sourceInput.value?.focus()
}

watch(() => state.bookId, loadChapters, { immediate: true })
onMounted(loadBooks)
onBeforeUnmount(() => { bookRequest?.abort(); chapterRequest?.abort() })
</script>

<template>
  <div class="import-view">
    <header class="page-header"><p class="eyebrow">Novo estudo</p><h1>Importar Fichamento</h1></header>
  <section v-if="state.saved" class="panel saved-panel" aria-labelledby="saved-heading">
    <p class="success-label" role="status">Salvamento concluído</p>
    <h2 id="saved-heading" ref="successHeading" tabindex="-1">{{ state.saved.title }}</h2>
    <p>{{ selectedBook?.title }} · {{ selectedChapter?.name }}</p>
    <p class="muted">{{ state.saved.location || 'Localização não informada' }}</p>
    <div class="actions wrap">
      <RouterLink class="button primary" :to="{ name: 'study', params: { bookId: state.bookId, studyId: state.saved.id } }">Ler estudo</RouterLink>
      <RouterLink class="text-link" :to="{ name: 'book', params: { bookId: state.bookId }, query: { chapter: state.saved.chapter_id } }">Ver estudos do capítulo</RouterLink>
      <button class="secondary" type="button" @click="startAnother">Importar outro estudo</button>
    </div>
  </section>
  <form v-else class="import-form" @submit.prevent="save">
    <fieldset :disabled="state.preparing || state.saving">
      <section class="panel import-step" aria-labelledby="destination-heading">
        <div class="step-heading"><span class="step-number" aria-hidden="true">1</span><h2 id="destination-heading">Livro e trecho</h2></div>
        <div v-if="booksError" class="notice error" role="alert"><p>{{ booksError }}</p><button type="button" class="secondary" @click="loadBooks">Tentar novamente</button></div>
        <div v-else-if="!booksLoading && books.length === 0" class="notice"><p>Cadastre um livro e um capítulo para escolher onde salvar.</p><RouterLink class="text-link" to="/">Cadastrar livro</RouterLink></div>
        <div class="form-grid">
          <div class="field">
            <label for="import-book">Livro</label>
            <select id="import-book" v-model="state.bookId" required :disabled="booksLoading || books.length === 0">
              <option value="">{{ booksLoading ? 'Carregando livros…' : 'Selecione um livro' }}</option>
              <option v-for="book in books" :key="book.id" :value="String(book.id)">{{ book.title }}</option>
            </select>
          </div>
          <div class="field">
            <label for="import-chapter">Capítulo</label>
            <select id="import-chapter" v-model="state.chapterId" required :disabled="chaptersLoading || !state.bookId || chapters.length === 0">
              <option value="">{{ chaptersLoading ? 'Carregando capítulos…' : 'Selecione um capítulo' }}</option>
              <option v-for="chapter in chapters" :key="chapter.id" :value="String(chapter.id)">{{ chapter.name }}</option>
            </select>
          </div>
        </div>
        <div v-if="chaptersError" class="notice error" role="alert"><p>{{ chaptersError }}</p><button type="button" class="secondary" @click="loadChapters">Tentar novamente</button></div>
        <p v-else-if="selectedBook && !chaptersLoading && chapters.length === 0" class="notice">Este livro ainda não tem capítulos. <RouterLink class="text-link" :to="{ name: 'book', params: { bookId: selectedBook.id } }">Adicionar capítulo</RouterLink></p>
        <div class="form-grid">
          <div class="field"><label for="import-location">Página ou localização <span class="optional">opcional</span></label><input id="import-location" v-model="state.location" placeholder="Ex.: p. 32–34 ou Loc. 1820" /></div>
          <div class="field"><label for="import-title">Título do estudo <span class="optional">opcional</span></label><input id="import-title" v-model="state.title" placeholder="Se vazio, será criado a partir do capítulo" /></div>
        </div>
        <div class="field field-with-toolbar">
          <label for="source-response">Fichamento da Fonte</label>
          <p id="source-hint" class="field-hint">Cole o texto completo da fonte. O Leitorum identifica automaticamente a estrutura das seções ao colar.</p>
          <MarkdownToolbar target-id="source-response" />
          <textarea id="source-response" ref="sourceInput" v-model="state.sourceResponse" @paste="onPaste" class="source-text textarea-with-toolbar" rows="10" aria-describedby="source-hint" placeholder="Cole o texto-base do fichamento aqui…" spellcheck="false"></textarea>
        </div>
        <p v-if="state.previewError" class="notice error" role="alert">{{ state.previewError }}</p>
        <p v-if="stale" class="notice warning" role="status">O texto colado foi modificado após a análise. Clique em "Atualizar prévia" para sincronizar as seções antes de salvar.</p>
        <div class="actions wrap">
          <button type="button" class="primary" :disabled="!state.sourceResponse.trim() || state.preparing" @click="prepare">
            {{ state.preparing ? 'Analisando texto…' : stale ? 'Atualizar prévia' : state.preview ? 'Reanalisar texto' : 'Analisar texto' }}
          </button>
          <span class="muted">{{ state.preview ? 'Confira as seções estruturadas na prévia abaixo.' : 'Dica: colar o texto (Ctrl+V) já aciona a prévia instantaneamente.' }}</span>
        </div>
      </section>

      <section v-if="state.preview" class="panel import-step" aria-labelledby="review-heading">
        <div class="step-heading"><span class="step-number" aria-hidden="true">2</span><h2 id="review-heading" ref="reviewHeading" tabindex="-1">Conferir e salvar</h2></div>
        
        <div v-if="state.preview.warnings.length" class="notice warning" role="status">
          <h3>Avisos da análise</h3>
          <ul>
            <li v-for="(warning, index) in state.preview.warnings" :key="index">
              {{ warning.message }}<span v-if="warning.line !== null" class="warning-line"> Linha {{ warning.line }}.</span>
            </li>
          </ul>
        </div>

        <!-- Conteúdo não classificado com ações rápidas de 1 clique -->
        <div v-if="state.preview.unassigned_text.trim()" class="unassigned-card notice warning" role="region" aria-label="Conteúdo Não Classificado">
          <div class="unassigned-header">
            <h3>Conteúdo Não Classificado</h3>
            <p class="field-hint">O trecho abaixo não foi identificado como título de seção. Atribua-o com 1 clique a uma das seções ou salve direto (será anexado à Explicação sem perda de conteúdo):</p>
          </div>
          <pre class="unassigned-preview">{{ state.preview.unassigned_text }}</pre>
          <div class="unassigned-actions">
            <span class="action-label">Mover para:</span>
            <button type="button" class="button secondary small" @click="assignUnassignedToSection('summary')">Resumo</button>
            <button type="button" class="button secondary small" @click="assignUnassignedToSection('explanation')">Explicação</button>
            <button type="button" class="button secondary small" @click="assignUnassignedToSection('concepts')">Conceitos</button>
            <button type="button" class="button secondary small" @click="assignUnassignedToSection('references')">Referências</button>
          </div>
        </div>

        <!-- Grade de Cards da Prévia Inteligente -->
        <div class="preview-cards-grid" role="region" aria-label="Prévia das Seções">
          <article v-for="sec in SECTION_LABELS" :key="sec.key" class="preview-section-card" :class="{ 'is-empty': !state.sections[sec.key].trim() }">
            <header class="section-card-header">
              <h3 class="section-card-title">{{ sec.label }}</h3>
              <span v-if="!state.sections[sec.key].trim()" class="empty-badge">Vazia</span>
            </header>
            <div class="section-card-content">
              <p v-if="state.sections[sec.key].trim()" class="section-text">{{ state.sections[sec.key] }}</p>
              <p v-else class="section-text empty-placeholder">Nenhum conteúdo identificado para esta seção.</p>
            </div>
          </article>
        </div>

        <!-- Barra de Salvamento Direto (Princípio UX: Colar -> Entender -> Conferir -> Salvar) -->
        <div class="save-bar">
          <p class="muted">O texto integral original do Fichamento da Fonte será preservado junto das seções estruturadas.</p>
          <button class="primary large save-button" :disabled="!canSave || !selectedBook || !selectedChapter || chaptersLoading">
            {{ state.saving ? 'Salvando estudo…' : 'Salvar estudo' }}
          </button>
        </div>
        <p v-if="!hasAnalysis" class="notice warning">Preencha ao menos uma das quatro seções para salvar.</p>
        <p v-if="!selectedBook || !selectedChapter" class="notice">Escolha o livro e o capítulo no início do formulário.</p>
        <p v-if="state.saveError" class="notice error" role="alert">{{ state.saveError }}</p>

        <!-- Ajuste manual detalhado (Accordion colapsável, opcional) -->
        <details class="manual-adjustment-panel">
          <summary class="manual-adjustment-summary">
            <span>Ajuste manual detalhado e anotações pessoais (opcional)</span>
          </summary>
          <div class="manual-adjustment-body">
            <p class="field-hint">Caso deseje editar o texto de cada seção individualmente ou incluir anotações adicionais antes de salvar:</p>
            <StudyEditorFields id-prefix="import" v-model:title="state.title" v-model:location="state.location" v-model:sections="state.sections" v-model:notes="state.notes" />
          </div>
        </details>
      </section>
    </fieldset>
  </form>
  </div>
</template>

<style scoped>
.field-with-toolbar {
  display: flex;
  flex-direction: column;
}

.textarea-with-toolbar {
  border-top-left-radius: 0 !important;
  border-top-right-radius: 0 !important;
  margin-top: -1px;
}

.preview-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.25rem;
  margin: 1.5rem 0;
}

.preview-section-card {
  background: var(--color-surface);
  border: var(--border-width, 1px) solid var(--color-border);
  border-radius: var(--radius-control, 8px);
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.preview-section-card.is-empty {
  opacity: 0.75;
  border-style: dashed;
}

.section-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--color-border);
}

.section-card-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0;
  color: var(--color-text);
}

.empty-badge {
  font-size: 0.75rem;
  padding: 0.15rem 0.5rem;
  border-radius: var(--radius-control, 4px);
  background: var(--color-surface-subtle);
  color: var(--color-text-muted);
}

.section-card-content {
  flex: 1;
}

.section-text {
  white-space: pre-wrap;
  font-size: 0.95rem;
  line-height: 1.5;
  margin: 0;
  color: var(--color-text);
}

.empty-placeholder {
  color: var(--color-text-muted);
  font-style: italic;
}

.unassigned-card {
  margin: 1.25rem 0;
  padding: 1.25rem;
  border-radius: var(--radius-control, 8px);
}

.unassigned-header h3 {
  margin: 0 0 0.5rem 0;
}

.unassigned-preview {
  background: var(--color-surface-subtle);
  border: var(--border-width, 1px) solid var(--color-border);
  border-radius: var(--radius-control, 6px);
  padding: 0.75rem;
  white-space: pre-wrap;
  font-family: inherit;
  font-size: 0.9rem;
  max-height: 160px;
  overflow-y: auto;
  margin: 0.75rem 0;
}

.unassigned-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.action-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-text-muted);
}

.unassigned-actions .button.small {
  padding: 0.35rem 0.75rem;
  font-size: 0.85rem;
}

.save-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  margin: 1.75rem 0 1.25rem 0;
  padding: 1rem 1.25rem;
  background: var(--color-surface-subtle);
  border: var(--border-width, 1px) solid var(--color-border);
  border-radius: var(--radius-control, 8px);
}

.save-button {
  min-width: 160px;
}

.manual-adjustment-panel {
  margin-top: 1.5rem;
  border: var(--border-width, 1px) solid var(--color-border);
  border-radius: var(--radius-control, 8px);
  background: var(--color-surface);
}

.manual-adjustment-summary {
  padding: 1rem 1.25rem;
  cursor: pointer;
  font-weight: 600;
  color: var(--color-text);
  user-select: none;
  outline: none;
}

.manual-adjustment-summary:focus-visible {
  outline: 2px solid var(--color-primary);
}

.manual-adjustment-body {
  padding: 0 1.25rem 1.25rem 1.25rem;
  border-top: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text);
}
</style>
