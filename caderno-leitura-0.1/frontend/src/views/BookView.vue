<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { api, errorMessage } from '../services/api'
import { useUnsavedChanges } from '../composables/useUnsavedChanges'
import { positiveId, type Book, type Chapter, type StudySummary } from '../types'

const route = useRoute()
const router = useRouter()
const book = ref<Book | null>(null)
const chapters = ref<Chapter[]>([])
const studies = ref<StudySummary[]>([])
const loading = ref(true)
const loadError = ref('')
const studiesLoading = ref(false)
const studiesError = ref('')
const chapterName = ref('')
const chapterError = ref('')
const creatingChapter = ref(false)
const bookId = computed(() => positiveId(route.params.bookId))
const selectedChapter = computed(() => route.query.chapter == null
  ? chapters.value[0] ?? null
  : chapters.value.find(chapter => chapter.id === positiveId(route.query.chapter)) ?? null)
let bookRequest: AbortController | null = null
let studyRequest: AbortController | null = null
let disposed = false
useUnsavedChanges(() => !!chapterName.value, () => creatingChapter.value)

async function loadBook() {
  bookRequest?.abort()
  const controller = new AbortController()
  bookRequest = controller
  loading.value = true
  loadError.value = ''
  book.value = null
  chapters.value = []
  chapterName.value = ''
  chapterError.value = ''
  const id = bookId.value
  if (id === null) { loadError.value = 'Livro não encontrado.'; loading.value = false; return }
  try {
    const [allBooks, result] = await Promise.all([api.listBooks(controller.signal), api.listChapters(id, controller.signal)])
    if (controller.signal.aborted) return
    book.value = allBooks.find(item => item.id === id) ?? null
    if (book.value === null) { loadError.value = 'Livro não encontrado.'; return }
    chapters.value = result
  } catch (error) {
    if (!controller.signal.aborted) loadError.value = errorMessage(error)
  } finally {
    if (!controller.signal.aborted) loading.value = false
  }
}

async function loadStudies() {
  studyRequest?.abort()
  const controller = new AbortController()
  studyRequest = controller
  studies.value = []
  studiesError.value = ''
  const chapter = selectedChapter.value
  studiesLoading.value = chapter !== null
  if (!chapter) return
  try {
    const result = await api.listStudies(chapter.id, controller.signal)
    if (!controller.signal.aborted) studies.value = result
  } catch (error) {
    if (!controller.signal.aborted) studiesError.value = errorMessage(error)
  } finally {
    if (!controller.signal.aborted) studiesLoading.value = false
  }
}

async function createChapter() {
  const id = bookId.value
  if (creatingChapter.value || id === null || !chapterName.value.trim()) return
  creatingChapter.value = true
  chapterError.value = ''
  try {
    const chapter = await api.createChapter(id, chapterName.value)
    if (disposed || bookId.value !== id) return
    chapters.value.push(chapter)
    chapterName.value = ''
    await router.replace({ name: 'book', params: { bookId: id }, query: { chapter: chapter.id } })
  } catch (error) {
    if (!disposed && bookId.value === id) chapterError.value = errorMessage(error)
  } finally { creatingChapter.value = false }
}

watch(bookId, loadBook, { immediate: true })
watch(() => selectedChapter.value?.id, loadStudies, { immediate: true })
onBeforeUnmount(() => { disposed = true; bookRequest?.abort(); studyRequest?.abort() })
</script>

<template>
  <nav class="breadcrumb" aria-label="Caminho"><RouterLink to="/">Meus livros</RouterLink><span aria-hidden="true">/</span><span>Livro</span></nav>
  <p v-if="loading" class="state-panel" role="status">Carregando livro…</p>
  <div v-else-if="loadError" class="notice error" role="alert">
    <h1>Não foi possível abrir o livro.</h1>
    <p>{{ loadError }}</p>
    <button class="secondary" type="button" @click="loadBook">Tentar novamente</button>
  </div>
  <template v-else-if="book">
    <header class="page-header">
      <p class="eyebrow">Livro</p>
      <h1>{{ book.title }}</h1>
      <p class="intro">{{ book.author || 'Autor não informado' }}</p>
    </header>
    <div class="chapter-layout">
      <aside class="panel chapter-sidebar" aria-labelledby="chapters-heading">
        <div class="section-heading"><h2 id="chapters-heading">Capítulos</h2><span class="count">{{ chapters.length }}</span></div>
        <nav v-if="chapters.length" aria-label="Capítulos do livro">
          <ul class="chapter-list">
            <li v-for="chapter in chapters" :key="chapter.id">
              <RouterLink :to="{ name: 'book', params: { bookId: book.id }, query: { chapter: chapter.id } }"
                :class="{ selected: selectedChapter?.id === chapter.id }" :aria-current="selectedChapter?.id === chapter.id ? 'page' : undefined">
                {{ chapter.name }}
              </RouterLink>
            </li>
          </ul>
        </nav>
        <p v-else class="muted">Adicione o primeiro capítulo deste livro.</p>
        <form class="chapter-form" @submit.prevent="createChapter">
          <fieldset :disabled="creatingChapter">
            <div class="field">
              <label for="chapter-name">Novo capítulo</label>
              <input id="chapter-name" v-model="chapterName" required placeholder="Nome ou número do capítulo" />
            </div>
            <p v-if="chapterError" class="notice error" role="alert">{{ chapterError }}</p>
            <button class="secondary full-width" :disabled="creatingChapter || !chapterName.trim()">{{ creatingChapter ? 'Cadastrando…' : 'Adicionar capítulo' }}</button>
          </fieldset>
        </form>
      </aside>
      <section v-if="selectedChapter" class="studies-area" aria-labelledby="studies-heading" :aria-busy="studiesLoading">
        <header class="section-heading wrap">
          <div><p class="eyebrow">Estudos do capítulo</p><h2 id="studies-heading">{{ selectedChapter.name }}</h2></div>
          <RouterLink class="button primary" :to="{ name: 'import', query: { book: book.id, chapter: selectedChapter.id } }">Importar estudo</RouterLink>
        </header>
        <p v-if="studiesLoading" class="state-panel" role="status">Carregando estudos…</p>
        <div v-else-if="studiesError" class="notice error" role="alert"><p>{{ studiesError }}</p><button class="secondary" @click="loadStudies">Tentar novamente</button></div>
        <div v-else-if="studies.length === 0" class="empty-state">
          <h3>Nenhum estudo neste capítulo.</h3>
          <p>Importe uma resposta do ChatGPT para começar.</p>
        </div>
        <template v-else>
          <p class="list-caption">{{ studies.length }} {{ studies.length === 1 ? 'estudo salvo' : 'estudos salvos' }}</p>
          <ul class="study-list">
            <li v-for="study in studies" :key="study.id">
              <h3><RouterLink class="study-title-link" :to="{ name: 'study', params: { bookId: book.id, studyId: study.id } }">{{ study.title }}</RouterLink></h3>
              <div class="study-meta"><span>{{ study.location || 'Localização não informada' }}</span><time :datetime="study.created_at">{{ new Date(study.created_at).toLocaleDateString('pt-BR') }}</time></div>
            </li>
          </ul>
        </template>
      </section>
      <section v-else class="empty-state"><h2>{{ chapters.length ? 'Selecione um capítulo.' : 'Organize seu primeiro estudo.' }}</h2><p>{{ chapters.length ? 'Escolha um capítulo na lista para consultar os estudos.' : 'Cadastre um capítulo e depois importe a resposta que deseja estudar.' }}</p></section>
    </div>
  </template>
</template>
