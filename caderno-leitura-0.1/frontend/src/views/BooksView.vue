<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { api, errorMessage } from '../services/api'
import { useUnsavedChanges } from '../composables/useUnsavedChanges'
import type { Book } from '../types'

const router = useRouter()
const books = ref<Book[]>([])
const loading = ref(true)
const loadError = ref('')
const title = ref('')
const titleInput = ref<HTMLInputElement | null>(null)
const author = ref('')
const saving = ref(false)
const saveError = ref('')
let request: AbortController | null = null
let disposed = false
useUnsavedChanges(() => !!(title.value || author.value), () => saving.value)

async function load() {
  request?.abort()
  const controller = new AbortController()
  request = controller
  loading.value = true
  loadError.value = ''
  try {
    const result = await api.listBooks(controller.signal)
    if (!controller.signal.aborted) books.value = result
  } catch (error) {
    if (!controller.signal.aborted) loadError.value = errorMessage(error)
  } finally {
    if (!controller.signal.aborted) loading.value = false
  }
}

async function createBook() {
  if (saving.value || !title.value.trim()) return
  saving.value = true
  saveError.value = ''
  let created: Book | null = null
  try {
    created = await api.createBook(title.value, author.value)
    title.value = ''; author.value = ''
  } catch (error) {
    if (!disposed) saveError.value = errorMessage(error)
  } finally { saving.value = false }
  if (created && !disposed) await router.push({ name: 'book', params: { bookId: created.id } })
}

onMounted(load)
onBeforeUnmount(() => { disposed = true; request?.abort() })
</script>

<template>
  <header class="page-header">
    <p class="eyebrow">Seu acervo</p>
    <h1>Meus livros</h1>
  </header>
  <div class="library-layout">
    <section aria-label="Livros cadastrados" :aria-busy="loading">
      <p v-if="loading" class="state-panel" role="status">Carregando livros…</p>
      <div v-else-if="loadError" class="notice error" role="alert">
        <p>{{ loadError }}</p>
        <button class="secondary" type="button" @click="load">Tentar novamente</button>
      </div>
      <div v-else-if="books.length === 0" class="empty-state">
        <h2>Seu primeiro livro começa aqui.</h2>
        <p>Cadastre o livro e, em seguida, adicione um capítulo para organizar seus estudos.</p>
        <a href="#book-title" class="text-link" @click.prevent="titleInput?.focus()">Cadastrar meu primeiro livro</a>
      </div>
      <template v-else>
        <p class="list-caption">{{ books.length }} {{ books.length === 1 ? 'livro cadastrado' : 'livros cadastrados' }}</p>
        <ul class="book-grid">
          <li v-for="(book, index) in books" :key="book.id">
            <RouterLink class="book-card" :to="{ name: 'book', params: { bookId: book.id } }">
              <span class="book-number" aria-hidden="true">{{ String(index + 1).padStart(2, '0') }}</span>
              <h2>{{ book.title }}</h2>
              <p>{{ book.author || 'Autor não informado' }}</p>
              <span class="card-action">Ver capítulos</span>
            </RouterLink>
          </li>
        </ul>
      </template>
    </section>
    <aside class="panel form-panel" aria-labelledby="new-book-heading">
      <h2 id="new-book-heading">Novo livro</h2>
      <form @submit.prevent="createBook">
        <fieldset :disabled="saving">
          <div class="field">
            <label for="book-title">Título do livro</label>
            <input id="book-title" ref="titleInput" v-model="title" required placeholder="Como aparece na capa" />
          </div>
          <div class="field">
            <label for="book-author">Autor <span class="optional">opcional</span></label>
            <input id="book-author" v-model="author" autocomplete="off" />
          </div>
          <p v-if="saveError" class="notice error" role="alert">{{ saveError }}</p>
          <button class="primary full-width" :disabled="saving || !title.trim()">{{ saving ? 'Cadastrando…' : 'Cadastrar livro' }}</button>
        </fieldset>
      </form>
    </aside>
  </div>
</template>
