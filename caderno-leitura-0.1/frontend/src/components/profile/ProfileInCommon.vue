<script setup lang="ts">
/**
 * F0.10.07 (spec 100): leituras e estudos em comum com um amigo, no perfil de outro leitor.
 * Só aparece entre amigos; do lado do amigo entram só livros e estudos que o visitante já pode ler.
 */
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { api, errorMessage } from '../../services/api'
import type { InCommonResponse } from '../../types'

const props = defineProps<{ username: string }>()

const data = ref<InCommonResponse | null>(null)
const loading = ref(true)
const loadError = ref('')
let controller: AbortController | null = null

async function load() {
  controller?.abort()
  const current = new AbortController()
  controller = current
  loading.value = true
  loadError.value = ''
  try {
    const result = await api.getInCommon(props.username, current.signal)
    if (current.signal.aborted) return
    data.value = result
  } catch (error) {
    if (current.signal.aborted) return
    data.value = null
    loadError.value = errorMessage(error)
  } finally {
    if (!current.signal.aborted) loading.value = false
  }
}

watch(() => props.username, () => void load(), { immediate: true })
onBeforeUnmount(() => controller?.abort())

const visible = computed(() => loading.value || !!loadError.value || !!data.value?.is_friend)

const sharedLink = computed(() => ({
  path: '/livros',
  query: { aba: 'compartilhados', autor: props.username },
}))

function studiesLabel(total: number): string {
  return total === 1 ? '1 estudo legível' : `${total} estudos legíveis`
}
</script>

<template>
  <section v-if="visible" class="in-common panel" aria-labelledby="in-common-heading">
    <h2 id="in-common-heading" class="in-common-title">Em comum com você</h2>

    <p v-if="loading" class="in-common-muted" role="status">Procurando leituras em comum…</p>

    <div v-else-if="loadError" class="in-common-error" role="alert">
      <p>{{ loadError }}</p>
      <button type="button" class="quiet in-common-retry" @click="load">Tentar novamente</button>
    </div>

    <template v-else-if="data">
      <p v-if="data.books.length === 0" class="in-common-muted">
        Nenhuma leitura em comum entre os livros que @{{ username }} compartilha com você.
      </p>

      <ul v-else class="in-common-books">
        <li v-for="book in data.books" :key="book.friend_book_id" class="in-common-book">
          <div class="in-common-book-head">
            <span class="in-common-book-title">{{ book.title }}</span>
            <span v-if="book.author" class="in-common-book-author">{{ book.author }}</span>
            <RouterLink :to="`/livros/${book.my_book_id}`" class="in-common-link">Seu livro</RouterLink>
          </div>

          <template v-if="book.friend_studies.length">
            <p class="in-common-muted in-common-studies-label">
              Estudos de @{{ username }} sobre este livro ({{ studiesLabel(book.friend_studies_total) }}):
            </p>
            <ul class="in-common-studies">
              <li v-for="study in book.friend_studies" :key="study.id">
                <RouterLink
                  :to="{ name: 'study', params: { bookId: study.book_id, studyId: study.id } }"
                  class="in-common-link"
                >
                  {{ study.title }}
                </RouterLink>
                <span v-if="study.chapter_name" class="in-common-muted"> · {{ study.chapter_name }}</span>
              </li>
            </ul>
            <p v-if="book.friend_studies_total > book.friend_studies.length" class="in-common-muted">
              e mais {{ book.friend_studies_total - book.friend_studies.length }}.
            </p>
          </template>
          <p v-else class="in-common-muted">Nenhum estudo de @{{ username }} sobre este livro está compartilhado com você.</p>
        </li>
      </ul>

      <p v-if="data.books_truncated" class="in-common-muted">Mostrando as primeiras leituras em comum.</p>

      <p class="in-common-shared">
        <span>
          {{ data.shared_with_me_total === 1 ? '1 estudo compartilhado' : `${data.shared_with_me_total} estudos compartilhados` }}
          com você por @{{ username }}.
        </span>
        <RouterLink v-if="data.shared_with_me_total > 0" :to="sharedLink" class="in-common-link">Ver todos</RouterLink>
      </p>
    </template>
  </section>
</template>

<style scoped>
.in-common {
  /* mesma largura do UserProfileCard */
  max-width: 44rem;
  margin: 1.25rem auto 0;
  box-sizing: border-box;
  padding: 1.25rem;
  border: var(--border-width, 1px) solid var(--color-border);
  border-radius: var(--radius-surface, 12px);
  background: var(--color-surface);
  color: var(--color-text);
}

.in-common-title {
  margin: 0 0 0.75rem;
  font-size: 1.1rem;
}

.in-common-muted {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-muted);
}

.in-common-error p {
  margin: 0 0 0.5rem;
}

.in-common-retry {
  --quiet-border: var(--color-border-strong, var(--color-border));
  min-height: 44px;
}

.in-common-books,
.in-common-studies {
  margin: 0;
  padding: 0;
  list-style: none;
}

.in-common-books {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.in-common-book {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  padding-bottom: 0.85rem;
  border-bottom: 1px solid var(--color-border);
  min-width: 0;
}

.in-common-book:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.in-common-book-head {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0.25rem 0.6rem;
  min-width: 0;
}

.in-common-book-title {
  font-weight: 600;
  overflow-wrap: anywhere;
}

.in-common-book-author {
  font-size: 0.875rem;
  color: var(--color-muted);
}

.in-common-studies {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.in-common-studies li {
  overflow-wrap: anywhere;
}

.in-common-link {
  display: inline-flex;
  align-items: center;
  min-height: 44px;
  color: var(--color-link);
  text-decoration: underline;
  text-underline-offset: 3px;
}

.in-common-shared {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.25rem 0.75rem;
  margin: 1rem 0 0;
  font-size: 0.875rem;
}
</style>
