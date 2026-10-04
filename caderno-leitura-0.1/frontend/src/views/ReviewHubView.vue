<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../services/api.ts'
import { reviewApi } from '../api/review.ts'
import { useReviewSession } from '../composables/useReviewSession.ts'
import type { Chapter, ReviewStatsResponse } from '../types.ts'
import ReviewStatsHeader from '../components/review/ReviewStatsHeader.vue'
import ReviewCard from '../components/review/ReviewCard.vue'
import ReviewSummaryModal from '../components/review/ReviewSummaryModal.vue'

const router = useRouter()
const session = useReviewSession()

const loadingStats = ref(false)
const stats = ref<ReviewStatsResponse>({
  total_eligible: 0,
  total_questions: 0,
  total_hidden: 0,
  reviewed_today: 0,
  pending_review: 0,
  books: [],
})

const selectedBookId = ref<number | null>(null)
const selectedChapterId = ref<number | null>(null)
const selectedKind = ref<string>('all')
const chapters = ref<Chapter[]>([])
const isSessionActive = ref(false)

async function fetchStats() {
  loadingStats.value = true
  try {
    stats.value = await reviewApi.getStats()
  } catch (err: unknown) {
    console.error('Erro ao carregar estatísticas de revisão:', err)
  } finally {
    loadingStats.value = false
  }
}

async function fetchChaptersForBook(bookId: number) {
  try {
    chapters.value = await api.listChapters(bookId)
  } catch {
    chapters.value = []
  }
}

watch(selectedBookId, (newBookId) => {
  selectedChapterId.value = null
  if (newBookId) {
    void fetchChaptersForBook(newBookId)
  } else {
    chapters.value = []
  }
})

const eligibleCountForSelection = computed(() => {
  if (selectedBookId.value) {
    const found = stats.value.books.find((b) => b.book_id === selectedBookId.value)
    return found ? found.items_count : 0
  }
  return stats.value.total_eligible
})

async function startReview() {
  isSessionActive.value = true
  await session.loadItems({
    book_id: selectedBookId.value ?? undefined,
    chapter_id: selectedChapterId.value ?? undefined,
    kind: selectedKind.value !== 'all' ? selectedKind.value : undefined,
    limit: 10,
  })
}

function exitSession() {
  session.reset()
  isSessionActive.value = false
  void fetchStats()
}

async function handleReviewMore() {
  await session.restartOrContinue({
    book_id: selectedBookId.value ?? undefined,
    chapter_id: selectedChapterId.value ?? undefined,
    kind: selectedKind.value !== 'all' ? selectedKind.value : undefined,
    limit: 10,
  })
}

function handleFinishSession() {
  exitSession()
  void router.push('/livros')
}

onMounted(() => {
  void fetchStats()
})
</script>

<template>
  <main class="review-hub-view" :class="{ 'immersive-mode': isSessionActive }">
    <!-- MODO 1: HUB CENTRAL E SELEÇÃO DE ESCOPO -->
    <div v-if="!isSessionActive" class="hub-container">
      <div class="hub-header">
        <h1 class="page-title">Central de Revisão</h1>
        <p class="page-subtitle">
          Pratique Active Recall com perguntas de fixação e termos ocultos dos seus estudos.
        </p>
      </div>

      <!-- Cabeçalho de Estatísticas e Filtros -->
      <ReviewStatsHeader
        :stats="stats"
        :selected-book-id="selectedBookId"
        :selected-chapter-id="selectedChapterId"
        :selected-kind="selectedKind"
        :chapters="chapters"
        :loading="loadingStats"
        @update:selected-book-id="selectedBookId = $event"
        @update:selected-chapter-id="selectedChapterId = $event"
        @update:selected-kind="selectedKind = $event"
      />

      <!-- ESTADO VAZIO: Nenhum item elegível -->
      <section
        v-if="!loadingStats && stats.total_eligible === 0"
        class="empty-state empty-review"
        aria-label="Nenhum item para revisão"
      >
        <div class="empty-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
        </div>
        <h2 class="empty-title">Nenhum item interativo para revisar</h2>
        <p class="empty-description">
          Você ainda não possui perguntas ou termos ocultos criados. Ao ler seus estudos,
          selecione qualquer trecho e transforme-o em uma <strong>Pergunta</strong> ou <strong>Termo Oculto</strong>.
        </p>
        <router-link to="/livros" class="btn-goto-books">
          Explorar meus Livros
        </router-link>
      </section>

      <!-- AVISO: Todos revisados hoje -->
      <div
        v-else-if="!loadingStats && stats.total_eligible > 0 && stats.pending_review === 0"
        class="all-reviewed-banner"
      >
        <span class="banner-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </span>
        <div class="banner-text">
          <strong>Parabéns!</strong> Todos os seus itens prioritários foram revisados hoje.
          Você pode revisar novamente para reforçar a memória ou praticar outro livro.
        </div>
      </div>

      <!-- BOTÃO DE INÍCIO DE RODADA -->
      <div v-if="stats.total_eligible > 0" class="start-session-bar">
        <button
          type="button"
          class="start-review-btn"
          :disabled="loadingStats || session.state.loading"
          @click="startReview"
        >
          Iniciar Revisão ({{ Math.min(10, eligibleCountForSelection) }} de {{ eligibleCountForSelection }} itens)
        </button>
      </div>
    </div>

    <!-- MODO 2: SESSÃO ATIVA EM TELA LIMPA -->
    <div v-else class="session-container">
      <!-- Barra superior da sessão imersiva -->
      <header class="session-header">
        <button
          type="button"
          class="btn-exit-session"
          aria-label="Voltar para a Central de Revisão"
          @click="exitSession"
        >
          ← Voltar ao Hub
        </button>

        <div class="session-progress-info">
          <span class="progress-label">
            Item {{ session.progress.value.current }} de {{ session.progress.value.total }}
          </span>
          <div class="session-progress-bar" aria-hidden="true">
            <div
              class="session-progress-fill"
              :style="{ width: `${session.progress.value.percent}%` }"
            />
          </div>
        </div>
      </header>

      <!-- Card Central de Active Recall -->
      <div class="card-stage">
        <div v-if="session.state.loading" class="session-loading">
          <p>Carregando itens da rodada...</p>
        </div>

        <div v-else-if="session.state.items.length === 0" class="no-items-in-round">
          <p>Nenhum item encontrado para os filtros selecionados.</p>
          <button type="button" class="btn-return" @click="exitSession">Voltar</button>
        </div>

        <ReviewCard
          v-else-if="session.currentItem.value"
          :item="session.currentItem.value"
          :is-revealed="session.state.isRevealed"
          :busy="session.state.submitting"
          @reveal="session.revealAnswer"
          @rate="session.submitRating"
        />
      </div>

      <!-- Modal de Conclusão de Rodada -->
      <ReviewSummaryModal
        :is-open="session.state.isCompleted"
        :summary="session.summary.value"
        :has-more-items="stats.total_eligible > 0"
        @review-more="handleReviewMore"
        @finish="handleFinishSession"
      />
    </div>
  </main>
</template>

<style scoped>
.review-hub-view {
  width: 100%;
  max-width: 960px;
  margin: 0 auto;
  padding: 1.5rem 1rem 3rem;
}

.review-hub-view.immersive-mode {
  max-width: 800px;
}

.hub-header {
  margin-bottom: 1.75rem;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--color-text-primary, #0f172a);
  margin: 0 0 0.375rem;
}

.page-subtitle {
  font-size: 0.9375rem;
  color: var(--color-text-secondary, #64748b);
  margin: 0;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 3.5rem 1.5rem;
  border-radius: 1rem;
  background-color: var(--color-bg-surface, #ffffff);
  border: 1px dashed var(--color-border-subtle, #cbd5e1);
  margin: 2rem 0;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.empty-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text-primary, #0f172a);
  margin: 0 0 0.5rem;
}

.empty-description {
  max-width: 520px;
  font-size: 0.9375rem;
  line-height: 1.6;
  color: var(--color-text-secondary, #64748b);
  margin: 0 0 1.5rem;
}

.btn-goto-books {
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.625rem 1.5rem;
  border-radius: 0.5rem;
  background-color: var(--color-primary, #2563eb);
  color: #ffffff;
  font-weight: 600;
  text-decoration: none;
  transition: background-color 0.15s ease;
}

.btn-goto-books:hover {
  background-color: var(--color-primary-hover, #1d4ed8);
}

.all-reviewed-banner {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-radius: 0.75rem;
  background-color: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #166534;
  margin-bottom: 1.5rem;
  font-size: 0.875rem;
}

.banner-icon {
  font-size: 1.5rem;
}

.start-session-bar {
  display: flex;
  justify-content: center;
  margin-top: 1rem;
}

.start-review-btn {
  min-height: 52px;
  width: 100%;
  max-width: 480px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.875rem 2rem;
  border-radius: 0.75rem;
  background-color: var(--color-primary, #2563eb);
  color: #ffffff;
  font-size: 1.125rem;
  font-weight: 700;
  border: none;
  cursor: pointer;
  box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.25);
  transition: all 0.15s ease;
}

.start-review-btn:hover:not(:disabled) {
  background-color: var(--color-primary-hover, #1d4ed8);
  transform: translateY(-1px);
  box-shadow: 0 6px 8px -1px rgba(37, 99, 235, 0.3);
}

.start-review-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.session-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.session-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.btn-exit-session {
  min-height: 44px;
  padding: 0.5rem 1rem;
  border: none;
  background: transparent;
  color: var(--color-text-secondary, #64748b);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  border-radius: 0.375rem;
  transition: all 0.15s ease;
}

.btn-exit-session:hover {
  background-color: var(--color-bg-hover, #f1f5f9);
  color: var(--color-text-primary, #0f172a);
}

.session-progress-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
  width: 160px;
}

.progress-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-secondary, #64748b);
}

.session-progress-bar {
  width: 100%;
  height: 6px;
  border-radius: 9999px;
  background-color: var(--color-border-subtle, #e2e8f0);
  overflow: hidden;
}

.session-progress-fill {
  height: 100%;
  background-color: var(--color-primary, #2563eb);
  transition: width 0.3s ease;
}

.card-stage {
  margin-top: 0.5rem;
}

.session-loading,
.no-items-in-round {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 1rem;
  color: var(--color-text-secondary, #64748b);
  gap: 1rem;
}

.btn-return {
  min-height: 44px;
  padding: 0.5rem 1.5rem;
  border-radius: 0.5rem;
  border: 1px solid var(--color-border-subtle, #cbd5e1);
  background: transparent;
  cursor: pointer;
}
</style>
