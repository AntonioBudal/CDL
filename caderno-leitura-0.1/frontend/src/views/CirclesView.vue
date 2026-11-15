<script setup lang="ts">
/** F0.12.07 (spec 120): círculos de leitura — meus círculos, convites pendentes e criar um novo. */
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { api, errorMessage } from '../services/api'
import { useCircleInvites } from '../composables/useCircleInvites'
import type { Book } from '../types'
import type { CircleInvite, CircleSummary } from '../types/circles'

const route = useRoute()
const router = useRouter()
const invitesCounter = useCircleInvites()
const circles = ref<CircleSummary[]>([])
const invites = ref<CircleInvite[]>([])
const books = ref<Book[]>([])
const loading = ref(true)
const busy = ref(false)
const error = ref('')
const message = ref('')
const bookId = ref<number | ''>('')
const name = ref('')

const sortedBooks = computed(() => [...books.value].sort((a, b) => a.title.localeCompare(b.title, 'pt-BR')))

function progressText(item: CircleSummary): string {
  if (item.finished) return 'Você terminou'
  if (!item.progress) return 'Você ainda não começou'
  return `Você está na parte ${item.progress} de ${item.part_count}`
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [list, mine] = await Promise.all([api.listCircles(), api.listBooks()])
    circles.value = list.circles
    invites.value = list.invites
    books.value = mine
    invitesCounter.setCount(list.invites.length)
    const fromBook = Number(route.query.livro)
    if (fromBook && mine.some((book) => book.id === fromBook)) bookId.value = fromBook
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    loading.value = false
  }
}

async function create() {
  if (!bookId.value) {
    error.value = 'Escolha um livro seu para o círculo.'
    return
  }
  busy.value = true
  error.value = ''
  try {
    const created = await api.createCircle(Number(bookId.value), name.value.trim() || undefined)
    await router.push({ name: 'circle', params: { id: created.id } })
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    busy.value = false
  }
}

async function answer(invite: CircleInvite, accept: boolean) {
  busy.value = true
  error.value = ''
  try {
    if (accept) {
      await api.acceptCircle(invite.id)
      await router.push({ name: 'circle', params: { id: invite.id } })
      return
    }
    await api.declineCircle(invite.id)
    message.value = `Convite para "${invite.name}" recusado.`
    await load()
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    busy.value = false
  }
}

onMounted(load)
</script>

<template>
  <section class="circles-view wrap" aria-labelledby="circles-heading">
    <header class="page-header">
      <p class="eyebrow">Ler junto</p>
      <h1 id="circles-heading">Círculos de leitura</h1>
      <p class="circles-lead">
        Leia um livro com amigos e converse parte por parte. Cada um marca em que parte está, e as mensagens das partes
        à frente ficam trancadas até você chegar lá: nada de spoiler.
      </p>
    </header>

    <p v-if="error" class="notice error" role="alert">{{ error }}</p>
    <p class="circles-muted" role="status" aria-live="polite">
      <template v-if="loading">Carregando…</template>
      <template v-else-if="message">{{ message }}</template>
    </p>

    <section v-if="invites.length" class="circles-block" aria-labelledby="circles-invites-heading">
      <h2 id="circles-invites-heading" class="circles-subtitle">Convites ({{ invites.length }})</h2>
      <ul class="circles-list">
        <li v-for="invite in invites" :key="invite.id" class="circles-item">
          <div class="circles-item-text">
            <strong>{{ invite.name }}</strong>
            <span class="circles-muted">
              {{ invite.book_title }}<template v-if="invite.book_author"> · {{ invite.book_author }}</template>
              · convite de {{ invite.invited_by.display_name }}
            </span>
          </div>
          <span class="circles-actions">
            <button type="button" class="primary circles-button" :disabled="busy" @click="answer(invite, true)">
              Entrar
            </button>
            <button type="button" class="quiet circles-button" :disabled="busy" @click="answer(invite, false)">
              Recusar
            </button>
          </span>
        </li>
      </ul>
    </section>

    <section class="circles-block" aria-labelledby="circles-mine-heading">
      <h2 id="circles-mine-heading" class="circles-subtitle">Meus círculos</h2>
      <p v-if="!loading && !circles.length" class="circles-muted">
        Você ainda não está em nenhum círculo. Crie um abaixo e convide amigos.
      </p>
      <ul v-else class="circles-list">
        <li v-for="item in circles" :key="item.id" class="circles-item">
          <div class="circles-item-text">
            <RouterLink :to="{ name: 'circle', params: { id: item.id } }" class="circles-title">{{ item.name }}</RouterLink>
            <span class="circles-muted">
              {{ item.book_title }} · {{ item.member_count === 1 ? '1 membro' : `${item.member_count} membros` }}
              · {{ progressText(item) }}
            </span>
          </div>
          <span v-if="item.role === 'owner'" class="circles-badge">Criado por você</span>
        </li>
      </ul>
    </section>

    <form class="circles-block circles-new" aria-labelledby="circles-new-heading" @submit.prevent="create">
      <h2 id="circles-new-heading" class="circles-subtitle">Novo círculo</h2>
      <p class="circles-muted">
        As partes do círculo começam iguais aos capítulos do livro escolhido; você pode renomear e acrescentar depois.
      </p>
      <label class="circles-field">
        <span>Livro</span>
        <select v-model="bookId" required>
          <option value="" disabled>Escolha um livro seu</option>
          <option v-for="book in sortedBooks" :key="book.id" :value="book.id">
            {{ book.title }}<template v-if="book.author"> — {{ book.author }}</template>
          </option>
        </select>
      </label>
      <label class="circles-field">
        <span>Nome do círculo (opcional)</span>
        <input v-model="name" type="text" maxlength="120" placeholder="Usa o título do livro se ficar vazio" />
      </label>
      <button type="submit" class="primary circles-button" :disabled="busy || !books.length">Criar círculo</button>
    </form>
  </section>
</template>

<style scoped>
.circles-view {
  max-width: 52rem;
  margin: 0 auto;
  padding-block: 1.5rem 3rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.circles-lead,
.circles-muted {
  color: var(--color-muted);
}

.circles-muted {
  font-size: 0.9rem;
  margin: 0;
}

.circles-block {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.circles-subtitle {
  margin: 0;
  font-size: 1.15rem;
}

.circles-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.circles-item {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-card);
  background: var(--color-surface);
}

.circles-item-text {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  min-width: 0;
  flex: 1 1 16rem;
}

.circles-title {
  font-weight: 600;
  min-height: 44px;
  display: inline-flex;
  align-items: center;
}

.circles-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.circles-button {
  min-height: 44px;
}

.circles-badge {
  font-size: 0.8rem;
  padding: 0.15rem 0.6rem;
  border-radius: 999px;
  border: 1px solid var(--color-border-subtle);
  color: var(--color-text-secondary);
}

.circles-new {
  padding: 1rem;
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-card);
}

.circles-field {
  display: grid;
  gap: 4px;
}

.circles-field input,
.circles-field select {
  min-height: 44px;
  width: 100%;
}

.circles-new .circles-button {
  align-self: flex-start;
}
</style>
