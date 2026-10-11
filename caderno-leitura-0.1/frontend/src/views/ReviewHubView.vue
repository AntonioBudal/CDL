<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { api, startStudySession, getStudySessionsHistory } from '../services/api.ts'
import { reviewApi } from '../api/review.ts'
import { useReviewSession } from '../composables/useReviewSession.ts'
import type { Chapter, ReviewStatsResponse, StudySession, SessionScopeType } from '../types.ts'
import ReviewStatsHeader from '../components/review/ReviewStatsHeader.vue'
import ReviewCard from '../components/review/ReviewCard.vue'
import ReviewPedagogicalEmpty from '../components/review/ReviewPedagogicalEmpty.vue'
import ReviewSummaryModal from '../components/review/ReviewSummaryModal.vue'

const router = useRouter()
const session = useReviewSession()

const activeTab = ref<'practice' | 'history'>('practice')
const sessionHistory = ref<StudySession[]>([])
const loadingHistory = ref(false)
const startingStructured = ref(false)

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
const sessionElapsedSeconds = ref(0)
let timerId: ReturnType<typeof setInterval> | null = null

function startTimer() {
  stopTimer()
  sessionElapsedSeconds.value = 0
  timerId = setInterval(() => {
    sessionElapsedSeconds.value++
  }, 1000)
}

function stopTimer() {
  if (timerId !== null) {
    clearInterval(timerId)
    timerId = null
  }
}

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
  startTimer()
  await session.loadItems({
    book_id: selectedBookId.value ?? undefined,
    chapter_id: selectedChapterId.value ?? undefined,
    kind: selectedKind.value !== 'all' ? selectedKind.value : undefined,
    limit: 10,
  })
}

function exitSession() {
  stopTimer()
  session.reset()
  isSessionActive.value = false
  void fetchStats()
}

async function handleReviewMore() {
  startTimer()
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

async function fetchHistory() {
  loadingHistory.value = true
  try {
    sessionHistory.value = await getStudySessionsHistory({ limit: 30 })
  } catch (err: unknown) {
    console.error('Erro ao carregar histórico de sessões:', err)
  } finally {
    loadingHistory.value = false
  }
}

watch(activeTab, (tab) => {
  if (tab === 'history') {
    void fetchHistory()
  }
})

async function startStructuredSession(scope: SessionScopeType = 'quick') {
  startingStructured.value = true
  try {
    const payload = {
      scope_type: scope,
      book_id: scope === 'book' ? selectedBookId.value : null,
      limit: 10,
    }
    const created = await startStudySession(payload)
    void router.push(`/estudo/sessao/${created.id}`)
  } catch (err: unknown) {
    alert(err instanceof Error ? err.message : 'Não foi possível iniciar a sessão de estudo.')
  } finally {
    startingStructured.value = false
  }
}

function formatDuration(totalSecs: number): string {
  if (!totalSecs || totalSecs <= 0) return '0 s'
  const minutes = Math.floor(totalSecs / 60)
  const seconds = totalSecs % 60
  if (minutes === 0) return `${seconds} s`
  return `${minutes} min ${seconds} s`
}

function formatDate(isoStr: string): string {
  try {
    const date = new Date(isoStr)
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return isoStr
  }
}

onMounted(() => {
  void fetchStats()
})

onUnmounted(() => {
  stopTimer()
})
</script>

<template>
  <main class="review-hub-view" :class="{ 'immersive-mode': isSessionActive }">
    <!-- MODO 1: HUB CENTRAL E SELEÇÃO DE ESCOPO -->
    <div v-if="!isSessionActive" class="hub-container">
      <div class="hub-header">
        <h1 class="page-title">Central de Revisão</h1>
        <p class="page-subtitle">
          Bancada de Fixação Cognitiva: pratique Active Recall com perguntas e termos ocultos.
        </p>
      </div>

      <!-- Abas da Central de Revisão -->
      <div class="hub-tabs-nav" role="tablist" aria-label="Navegação da Central de Revisão">
        <button
          type="button"
          role="tab"
          class="hub-tab-item"
          :class="{ active: activeTab === 'practice' }"
          :aria-selected="activeTab === 'practice'"
          @click="activeTab = 'practice'"
        >
          Prática de Revisão
        </button>
        <button
          type="button"
          role="tab"
          class="hub-tab-item"
          :class="{ active: activeTab === 'history' }"
          :aria-selected="activeTab === 'history'"
          @click="activeTab = 'history'"
        >
          Histórico de Sessões
        </button>
      </div>

      <!-- ABA 1: PRÁTICA DE REVISÃO -->
      <div v-if="activeTab === 'practice'" class="practice-tab-content">
        <!-- Cabeçalho de Estatísticas e Barra de Prontidão -->
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
          @start-practice="startReview"
        />

        <!-- ESTADO VAZIO PEDAGÓGICO: Nenhum item elegível no acervo -->
        <ReviewPedagogicalEmpty
          v-if="!loadingStats && stats.total_eligible === 0"
          :has-eligible-items="false"
          @go-to-books="router.push('/livros')"
        />

        <!-- ESTADO VAZIO PEDAGÓGICO: Todos já revisados hoje -->
        <ReviewPedagogicalEmpty
          v-else-if="!loadingStats && stats.total_eligible > 0 && stats.pending_review === 0"
          :has-eligible-items="true"
          @go-to-books="router.push('/livros')"
          @review-again="handleReviewMore"
        />

        <!-- AÇÕES SECUNDÁRIAS (Sessão Estruturada / Prática Rápida Hub) -->
        <div v-if="stats.pending_review > 0" class="start-session-bar">
          <button
            type="button"
            class="start-structured-btn"
            :disabled="loadingStats || startingStructured"
            @click="startStructuredSession(selectedBookId ? 'book' : 'quick')"
          >
            <svg class="play-icon" viewBox="0 0 24 24" width="18" height="18" fill="currentColor" aria-hidden="true">
              <polygon points="5 3 19 12 5 21 5 3" />
            </svg>
            <span>
              Iniciar Sessão Estruturada
              <template v-if="selectedBookId">do Livro</template>
              <template v-else>Rápida (10 itens)</template>
            </span>
          </button>
          <button
            type="button"
            class="start-review-btn secondary-mode"
            :disabled="loadingStats || session.state.loading"
            @click="startReview"
          >
            Prática Rápida neste Hub ({{ Math.min(10, eligibleCountForSelection) }} itens)
          </button>
        </div>
      </div>

      <!-- ABA 2: HISTÓRICO DE SESSÕES -->
      <div v-else class="history-tab-content">
        <div v-if="loadingHistory" class="history-loading">
          <div class="spinner" aria-hidden="true" />
          <p>Carregando histórico de sessões...</p>
        </div>
        <div v-else-if="sessionHistory.length === 0" class="empty-state empty-history">
          <h2 class="empty-title">Nenhuma sessão registrada</h2>
          <p class="empty-description">
            Complete sua primeira sessão de estudo para acompanhar aqui seu histórico auditável de aprendizado e dedicação.
          </p>
        </div>
        <div v-else class="history-list">
          <div
            v-for="item in sessionHistory"
            :key="item.id"
            class="history-card"
          >
            <div class="history-card-header">
              <span class="history-date">{{ formatDate(item.started_at) }}</span>
              <span
                class="history-status-badge"
                :class="item.status"
              >
                {{ item.status === 'completed' ? 'Concluída' : 'Interrompida' }}
              </span>
            </div>
            <div class="history-card-body">
              <div class="history-detail-item">
                <span class="detail-label">Escopo</span>
                <span class="detail-value">
                  {{ item.book_title ? `Livro: ${item.book_title}` : (item.scope_type === 'quick' ? 'Sessão Rápida' : 'Geral') }}
                </span>
              </div>
              <div class="history-detail-item">
                <span class="detail-label">Itens</span>
                <span class="detail-value">{{ item.completed_items }} de {{ item.total_items }}</span>
              </div>
              <div class="history-detail-item">
                <span class="detail-label">Duração</span>
                <span class="detail-value">{{ formatDuration(item.duration_seconds) }}</span>
              </div>
              <div class="history-detail-item">
                <span class="detail-label">Recordação</span>
                <span class="detail-value">
                  <span class="count-easy">{{ item.easy_count }} fácil</span> ·
                  <span class="count-medium">{{ item.medium_count }} médio</span> ·
                  <span class="count-hard">{{ item.hard_count }} difícil</span>
                </span>
              </div>
            </div>
          </div>
        </div>
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
          :progress="session.progress.value"
          @reveal="session.revealAnswer"
          @rate="session.submitRating"
        />
      </div>

      <!-- Modal de Conclusão de Rodada -->
      <ReviewSummaryModal
        :is-open="session.state.isCompleted"
        :summary="session.summary.value"
        :has-more-items="stats.pending_review > 0"
        :elapsed-seconds="sessionElapsedSeconds"
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
  font-family: var(--font-serif, "EB Garamond", Garamond, Georgia, serif);
  font-size: 1.85rem;
  font-weight: 700;
  color: var(--color-text, #0f172a);
  margin: 0 0 0.375rem;
  letter-spacing: -0.015em;
}

.page-subtitle {
  font-size: 0.95rem;
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
  background-color: var(--color-surface, #ffffff);
  border: 1px dashed var(--color-border-subtle, #cbd5e1);
  margin: 2rem 0;
}

.empty-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text, #0f172a);
  margin: 0 0 0.5rem;
}

.empty-description {
  max-width: 520px;
  font-size: 0.9375rem;
  line-height: 1.6;
  color: var(--color-text-secondary, #64748b);
  margin: 0;
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
  background-color: var(--color-surface-soft, rgba(0, 0, 0, 0.04));
  color: var(--color-text, #0f172a);
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
  background-color: var(--color-accent, var(--color-primary, #3b82f6));
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
  color: var(--color-text, inherit);
}

/* Abas do Hub */
.hub-tabs-nav {
  display: flex;
  gap: 0.5rem;
  border-bottom: 1px solid var(--color-border-subtle, #e2e8f0);
  margin-bottom: 1.5rem;
}

.hub-tab-item {
  min-height: 44px;
  padding: 0.625rem 1.25rem;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--color-text-secondary, #64748b);
  font-family: inherit;
  font-size: 0.9375rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.hub-tab-item:hover {
  color: var(--color-text, #0f172a);
}

.hub-tab-item.active {
  color: var(--color-accent, var(--color-primary, #3b82f6));
  border-bottom-color: var(--color-accent, var(--color-primary, #3b82f6));
}

.hub-tab-item:focus-visible {
  outline: 2px solid var(--color-accent, #3b82f6);
  outline-offset: -2px;
}

/* Barra de Início e Botões */
.start-session-bar {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  margin-top: 1.5rem;
}

.start-structured-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.625rem;
  min-height: 48px;
  padding: 0.75rem 1.75rem;
  background-color: var(--color-accent, var(--color-primary, #3b82f6));
  color: var(--color-on-accent, #ffffff);
  border: 1px solid transparent;
  border-radius: 8px;
  font-family: inherit;
  font-size: 0.9375rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.start-structured-btn:hover {
  opacity: 0.92;
  transform: translateY(-1px);
}

.start-structured-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.start-structured-btn:focus-visible {
  outline: 2px solid var(--color-accent, #3b82f6);
  outline-offset: 2px;
}

.start-review-btn.secondary-mode {
  min-height: 48px;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  background-color: transparent;
  color: var(--color-text-secondary, #475569);
  border: 1px solid var(--color-border-strong, #cbd5e1);
  font-family: inherit;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
}

.start-review-btn.secondary-mode:hover {
  background-color: var(--color-surface-soft, rgba(0, 0, 0, 0.04));
  color: var(--color-text, #0f172a);
}

/* Histórico de Sessões */
.history-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  color: var(--color-text-secondary, #64748b);
  gap: 1rem;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--color-border-subtle, #e2e8f0);
  border-top-color: var(--color-accent, #3b82f6);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.history-card {
  background-color: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border-subtle, #e2e8f0);
  border-radius: 8px;
  padding: 1.25rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
}

.history-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.875rem;
}

.history-date {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text, #1e293b);
}

.history-status-badge {
  font-size: 0.6875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
}

.history-status-badge.completed {
  background-color: var(--color-surface-soft, rgba(34, 197, 94, 0.12));
  color: var(--color-success, #15803d);
}

.history-status-badge.interrupted {
  background-color: var(--color-surface-soft, rgba(245, 158, 11, 0.12));
  color: var(--color-warning, #b45309);
}

.history-card-body {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 0.75rem;
}

.history-detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.detail-label {
  font-size: 0.6875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-secondary, #94a3b8);
  font-weight: 600;
}

.detail-value {
  font-size: 0.875rem;
  color: var(--color-text, #334155);
  font-weight: 500;
}

.count-easy {
  color: var(--color-success, #16a34a);
  font-weight: 600;
}

.count-medium {
  color: var(--color-warning, #d97706);
  font-weight: 600;
}

.count-hard {
  color: var(--color-error, #dc2626);
  font-weight: 600;
}
</style>
