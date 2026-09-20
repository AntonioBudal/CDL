<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { api, errorMessage } from '../services/api'
import { useImportDraft } from '../composables/useImportDraft'
import { useUnsavedChanges } from '../composables/useUnsavedChanges'
import StudyEditorFields from '../components/StudyEditorFields.vue'
import { positiveId, type Book, type Chapter } from '../types'

const route = useRoute()
const draft = useImportDraft(api)
const { state, stale, hasManualChanges, hasAnalysis, canSave } = draft
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
        <div class="field">
          <label for="source-response">Fichamento da Fonte</label>
          <p id="source-hint" class="field-hint">Use os títulos Resumo, Explicação, Conceitos e Referências em linhas próprias.</p>
          <textarea id="source-response" ref="sourceInput" v-model="state.sourceResponse" class="source-text" rows="10" aria-describedby="source-hint" placeholder="Cole o texto-base do fichamento aqui…" spellcheck="false"></textarea>
        </div>
        <p v-if="state.previewError" class="notice error" role="alert">{{ state.previewError }}</p>
        <p v-if="stale" class="notice warning" role="status">O fichamento da fonte mudou. A prévia abaixo ainda corresponde ao texto anterior; prepare-a novamente antes de salvar.</p>
        <div class="actions wrap"><button type="button" class="primary" :disabled="!state.sourceResponse.trim() || state.preparing" @click="prepare">{{ state.preparing ? 'Preparando prévia…' : state.preview ? 'Preparar novamente' : 'Preparar prévia' }}</button><span class="muted">Você poderá corrigir as seções antes de salvar.</span></div>
      </section>

      <section v-if="state.preview" class="panel import-step" aria-labelledby="review-heading">
        <div class="step-heading"><span class="step-number" aria-hidden="true">2</span><h2 id="review-heading" ref="reviewHeading" tabindex="-1">Conferir e salvar</h2></div>
        <div v-if="state.preview.warnings.length" class="notice warning" role="status">
          <h3>Avisos da divisão inicial</h3>
          <ul><li v-for="(warning, index) in state.preview.warnings" :key="index">{{ warning.message }}<span v-if="warning.line !== null" class="warning-line"> Linha {{ warning.line }}.</span></li></ul>
          <p>Os avisos descrevem o texto-base colado. Confira abaixo o resultado das suas correções.</p>
        </div>
        <div v-if="state.preview.unassigned_text.trim()" class="unassigned field">
          <label for="unassigned-text">Texto não associado</label>
          <p id="unassigned-hint" class="field-hint">Copie para a seção adequada. Este texto também será preservado no fichamento da fonte.</p>
          <textarea id="unassigned-text" :value="state.preview.unassigned_text" readonly rows="5" aria-describedby="unassigned-hint"></textarea>
        </div>
        <StudyEditorFields id-prefix="import" v-model:title="state.title" v-model:location="state.location" v-model:sections="state.sections" v-model:notes="state.notes" />
        <p v-if="!hasAnalysis" class="notice warning">Preencha ao menos uma das quatro seções para salvar.</p>
        <p v-if="!selectedBook || !selectedChapter" class="notice">Escolha o livro e o capítulo no início do formulário.</p>
        <p v-if="state.saveError" class="notice error" role="alert">{{ state.saveError }}</p>
        <div class="save-bar"><p class="muted">O fichamento da fonte será guardado junto das seções revisadas.</p><button class="primary" :disabled="!canSave || !selectedBook || !selectedChapter || chaptersLoading">{{ state.saving ? 'Salvando estudo…' : 'Salvar estudo' }}</button></div>
      </section>
    </fieldset>
  </form>
  </div>
</template>
