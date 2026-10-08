<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SessionProgressHeader from '../components/session/SessionProgressHeader.vue'
import SessionSummaryModal from '../components/session/SessionSummaryModal.vue'
import { useStructuredStudySession } from '../composables/useActiveReadingSession.ts'

const route = useRoute()
const router = useRouter()
const studySession = useStructuredStudySession()

const sessionId = computed(() => Number(route.params.sessionId))

function onKeydown(e: KeyboardEvent) {
  studySession.handleKeydown(e, () => {
    void router.push('/revisao')
  })
}

function handleExitRequest() {
  studySession.requestExit()
}

function handleConfirmExit() {
  void studySession.interruptAndExit(() => {
    void router.push('/revisao')
  })
}

function handleCancelExit() {
  studySession.cancelExit()
}

function handleSummaryClose() {
  void router.push('/revisao')
}

function handleGoToBook(bookId: number) {
  void router.push(`/livros/${bookId}`)
}

onMounted(() => {
  window.addEventListener('keydown', onKeydown)
  if (sessionId.value) {
    void studySession.loadSession(sessionId.value)
  } else {
    void router.push('/revisao')
  }
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
})
</script>

<template>
  <div class="study-session-view">
    <!-- Cabeçalho de progresso -->
    <SessionProgressHeader
      :current="studySession.progress.value.current"
      :total="studySession.progress.value.total"
      :percent="studySession.progress.value.percent"
      :timer="studySession.formattedTimer.value"
      :book-title="studySession.session.value?.book_title"
      @exit="handleExitRequest"
    />

    <!-- Estado de Carregamento -->
    <div v-if="studySession.loading.value" class="state-container loading-state">
      <div class="spinner" aria-hidden="true" />
      <p>Preparando cartões de estudo...</p>
    </div>

    <!-- Estado de Erro -->
    <div v-else-if="studySession.error.value" class="state-container error-state">
      <h2>Não foi possível carregar a sessão</h2>
      <p>{{ studySession.error.value }}</p>
      <button type="button" class="btn-retry" @click="router.push('/revisao')">
        Voltar à Central de Revisão
      </button>
    </div>

    <!-- Cartão Ativo de Estudo -->
    <div v-else-if="studySession.currentCard.value" class="card-container">
      <div class="study-card">
        <!-- Metadados de Contexto Editorial -->
        <div class="card-context">
          <span class="context-kind-tag" :class="studySession.currentCard.value.kind">
            {{ studySession.currentCard.value.kind === 'question' ? 'Pergunta de Fixação' : 'Termo Oculto' }}
          </span>
          <span class="context-sep" aria-hidden="true">·</span>
          <span class="context-study" :title="studySession.currentCard.value.study_title">
            {{ studySession.currentCard.value.study_title }}
          </span>
          <span v-if="studySession.currentCard.value.chapter_name" class="context-chapter">
            ({{ studySession.currentCard.value.chapter_name }})
          </span>
        </div>

        <!-- Enunciado do Cartão -->
        <div class="card-prompt">
          <h2 class="prompt-text">
            {{ studySession.currentCard.value.question_text }}
          </h2>
        </div>

        <!-- Resposta Revelada -->
        <div v-if="studySession.isRevealed.value" class="card-answer-revealed">
          <span class="answer-badge">Resposta Esperada</span>
          <div class="answer-content">
            {{ studySession.currentCard.value.expected_answer }}
          </div>
        </div>

        <!-- Área de Ação e Avaliação -->
        <div class="card-action-bar">
          <!-- Ação inicial: Revelar Resposta -->
          <div v-if="!studySession.isRevealed.value" class="reveal-action-group">
            <button
              type="button"
              class="btn-reveal"
              @click="studySession.revealAnswer"
            >
              <span>Revelar Resposta</span>
              <kbd class="action-kbd">Espaço</kbd>
            </button>
          </div>

          <!-- Ação secundária: Avaliação de Retenção -->
          <div v-else class="rating-action-group">
            <span class="rating-prompt-label">Como foi sua recordação?</span>
            <div class="rating-buttons-grid">
              <button
                type="button"
                class="btn-rating btn-easy"
                :disabled="studySession.submitting.value"
                @click="studySession.answerCard('easy')"
              >
                <span class="btn-rating-title">Fácil</span>
                <span class="btn-rating-desc">Recordação imediata</span>
                <kbd class="rating-kbd">1</kbd>
              </button>

              <button
                type="button"
                class="btn-rating btn-medium"
                :disabled="studySession.submitting.value"
                @click="studySession.answerCard('medium')"
              >
                <span class="btn-rating-title">Médio</span>
                <span class="btn-rating-desc">Com algum esforço</span>
                <kbd class="rating-kbd">2</kbd>
              </button>

              <button
                type="button"
                class="btn-rating btn-hard"
                :disabled="studySession.submitting.value"
                @click="studySession.answerCard('hard')"
              >
                <span class="btn-rating-title">Difícil</span>
                <span class="btn-rating-desc">Não recordei</span>
                <kbd class="rating-kbd">3</kbd>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Diálogo Modal de Saída Segura -->
    <div
      v-if="studySession.showConfirmExit.value"
      class="exit-dialog-overlay"
      role="dialog"
      aria-modal="true"
      aria-labelledby="exit-dialog-title"
    >
      <div class="exit-dialog-card">
        <h3 id="exit-dialog-title" class="dialog-title">Interromper Sessão de Estudo?</h3>
        <p class="dialog-text">
          Seu progresso até este momento será salvo com segurança. Os cartões que você já avaliou
          terão suas repetições registradas e a sessão constará como interrompida no histórico.
        </p>
        <div class="dialog-actions">
          <button type="button" class="btn-dialog-cancel" @click="handleCancelExit">
            Continuar Estudando
          </button>
          <button type="button" class="btn-dialog-confirm" @click="handleConfirmExit">
            Sim, Interromper
          </button>
        </div>
      </div>
    </div>

    <!-- Modal Triunfante de Conclusão -->
    <SessionSummaryModal
      v-if="studySession.showSummaryModal.value && studySession.summary.value"
      :summary="studySession.summary.value"
      @close="handleSummaryClose"
      @go-to-book="handleGoToBook"
    />
  </div>
</template>

<style scoped>
.study-session-view {
  min-height: 100vh;
  background-color: var(--color-bg-subtle, #f9fafb);
  display: flex;
  flex-direction: column;
}

.state-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1.5rem;
  text-align: center;
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid var(--color-border-subtle, #e5e7eb);
  border-top-color: var(--color-accent, #2563eb);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.card-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 1.5rem 4rem;
  max-width: 840px;
  margin: 0 auto;
  width: 100%;
}

.study-card {
  width: 100%;
  background-color: var(--color-bg, #ffffff);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
  padding: 2.5rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.card-context {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  font-size: 0.8125rem;
  color: var(--color-text-muted, #6b7280);
}

.context-kind-tag {
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.6875rem;
  letter-spacing: 0.05em;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
}

.context-kind-tag.question {
  background-color: #eff6ff;
  color: #1d4ed8;
}

.context-kind-tag.hidden {
  background-color: #fef3c7;
  color: #b45309;
}

.context-study {
  font-weight: 500;
  color: var(--color-text-secondary, #374151);
}

.prompt-text {
  font-family: var(--font-serif, "EB Garamond", serif);
  font-size: 1.625rem;
  font-weight: 500;
  line-height: 1.45;
  color: var(--color-text, #111827);
  margin: 0;
}

.card-answer-revealed {
  background-color: var(--color-bg-subtle, #f9fafb);
  border-left: 3px solid var(--color-accent, #2563eb);
  border-radius: 0 8px 8px 0;
  padding: 1.25rem 1.5rem;
  animation: fadeIn 0.2s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.answer-badge {
  display: inline-block;
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-accent, #2563eb);
  margin-bottom: 0.5rem;
}

.answer-content {
  font-family: var(--font-serif, "EB Garamond", serif);
  font-size: 1.25rem;
  color: var(--color-text, #111827);
  line-height: 1.5;
}

.card-action-bar {
  margin-top: 1rem;
}

.reveal-action-group {
  display: flex;
  justify-content: center;
}

.btn-reveal {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  min-height: 52px;
  min-width: 220px;
  padding: 0.75rem 2rem;
  background-color: var(--color-accent, #2563eb);
  color: #ffffff;
  border: 1px solid transparent;
  border-radius: 8px;
  font-family: inherit;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-reveal:hover {
  background-color: var(--color-accent-hover, #1d4ed8);
}

.btn-reveal:focus-visible {
  outline: 2px solid var(--color-accent, #2563eb);
  outline-offset: 3px;
}

.action-kbd {
  font-size: 0.75rem;
  padding: 0.125rem 0.375rem;
  background-color: rgba(255, 255, 255, 0.25);
  border-radius: 4px;
}

.rating-action-group {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.rating-prompt-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-secondary, #4b5563);
  text-align: center;
}

.rating-buttons-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.btn-rating {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 64px;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-family: inherit;
  border: 1px solid var(--color-border, #d1d5db);
  background-color: var(--color-bg, #ffffff);
  cursor: pointer;
  position: relative;
  transition: all 0.15s ease;
}

.btn-rating:focus-visible {
  outline: 2px solid var(--color-accent, #2563eb);
  outline-offset: 2px;
}

.btn-rating-title {
  font-size: 1rem;
  font-weight: 600;
}

.btn-rating-desc {
  font-size: 0.6875rem;
  color: var(--color-text-muted, #6b7280);
  margin-top: 0.125rem;
}

.rating-kbd {
  position: absolute;
  top: 6px;
  right: 6px;
  font-size: 0.625rem;
  padding: 0.1rem 0.25rem;
  background-color: var(--color-bg-subtle, #f3f4f6);
  border: 1px solid var(--color-border-subtle, #e5e7eb);
  border-radius: 3px;
  color: var(--color-text-muted, #6b7280);
}

.btn-easy:hover {
  background-color: #f0fdf4;
  border-color: #86efac;
  color: #15803d;
}

.btn-medium:hover {
  background-color: #fffbeb;
  border-color: #fde68a;
  color: #b45309;
}

.btn-hard:hover {
  background-color: #fef2f2;
  border-color: #fca5a5;
  color: #b91c1c;
}

.exit-dialog-overlay {
  position: fixed;
  inset: 0;
  z-index: 90;
  background-color: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(2px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

.exit-dialog-card {
  max-width: 440px;
  width: 100%;
  background-color: var(--color-bg, #ffffff);
  border-radius: 10px;
  padding: 1.75rem;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.dialog-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text, #111827);
  margin: 0 0 0.75rem 0;
}

.dialog-text {
  font-size: 0.875rem;
  color: var(--color-text-secondary, #4b5563);
  line-height: 1.5;
  margin: 0 0 1.5rem 0;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.btn-dialog-cancel,
.btn-dialog-confirm {
  min-height: 44px;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-dialog-cancel {
  background-color: transparent;
  border: 1px solid var(--color-border, #d1d5db);
  color: var(--color-text, #374151);
}

.btn-dialog-cancel:hover {
  background-color: var(--color-bg-subtle, #f3f4f6);
}

.btn-dialog-confirm {
  background-color: var(--color-text-danger, #dc2626);
  border: 1px solid transparent;
  color: #ffffff;
}

.btn-dialog-confirm:hover {
  background-color: #b91c1c;
}

@media (max-width: 640px) {
  .study-card {
    padding: 1.5rem;
  }
  .prompt-text {
    font-size: 1.25rem;
  }
  .rating-buttons-grid {
    grid-template-columns: 1fr;
  }
  .dialog-actions {
    flex-direction: column-reverse;
  }
  .btn-dialog-cancel,
  .btn-dialog-confirm {
    width: 100%;
  }
}
</style>
