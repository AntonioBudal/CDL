<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue'
import type { ReviewItemRead, ReviewRating } from '../../types.ts'

const props = withDefaults(
  defineProps<{
    item: ReviewItemRead
    isRevealed: boolean
    busy?: boolean
    progress?: { current: number; total: number; percent: number }
  }>(),
  {
    busy: false,
    progress: undefined,
  },
)

const emit = defineEmits<{
  (e: 'reveal'): void
  (e: 'rate', rating: ReviewRating): void
}>()

const liveAnnouncement = ref('')

watch(
  () => props.isRevealed,
  (revealed) => {
    if (revealed) {
      liveAnnouncement.value = `Resposta revelada: ${props.item.expected_answer}`
    } else {
      liveAnnouncement.value = ''
    }
  },
)

function handleKeydown(event: KeyboardEvent) {
  // Ignora se o foco estiver em campo de texto
  const tag = (event.target as HTMLElement)?.tagName?.toLowerCase()
  if (tag === 'input' || tag === 'textarea' || tag === 'select') return

  if (event.code === 'Space' || event.key === ' ') {
    if (!props.isRevealed && !props.busy) {
      event.preventDefault()
      emit('reveal')
    }
  } else if (props.isRevealed && !props.busy) {
    if (event.key === '1' || event.code === 'Digit1' || event.code === 'Numpad1') {
      event.preventDefault()
      emit('rate', 'hard')
    } else if (event.key === '2' || event.code === 'Digit2' || event.code === 'Numpad2') {
      event.preventDefault()
      emit('rate', 'medium')
    } else if (
      event.key === '3' ||
      event.code === 'Digit3' ||
      event.code === 'Numpad3' ||
      event.key === '4' ||
      event.code === 'Digit4' ||
      event.code === 'Numpad4'
    ) {
      event.preventDefault()
      emit('rate', 'easy')
    }
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<template>
  <article
    class="review-card review-flip-card"
    role="region"
    aria-label="Card de estudo ativo e fixação cognitiva"
  >
    <!-- Anúncio de leitor de tela -->
    <div class="sr-only" aria-live="polite" aria-atomic="true">
      {{ liveAnnouncement }}
    </div>

    <!-- Barra de Progresso da Rodada (se fornecida) -->
    <div v-if="progress && progress.total > 0" class="card-progress-bar" aria-hidden="true">
      <div class="progress-fill" :style="{ width: `${progress.percent}%` }" />
    </div>

    <!-- Cabeçalho do Card: Origem e Metadados -->
    <div class="card-header">
      <div class="origin-breadcrumbs">
        <span class="breadcrumb-book">{{ item.book_title }}</span>
        <span class="breadcrumb-separator" aria-hidden="true">›</span>
        <span class="breadcrumb-chapter">{{ item.chapter_name }}</span>
        <span class="breadcrumb-separator" aria-hidden="true">›</span>
        <span class="breadcrumb-study">{{ item.study_title }}</span>
      </div>

      <div class="card-badges">
        <span
          class="kind-badge"
          :class="item.kind === 'question' ? 'badge-question' : 'badge-hidden'"
        >
          {{ item.kind === 'question' ? 'Pergunta' : 'Termo Oculto' }}
        </span>
        <span v-if="item.last_rating" class="history-badge">
          Última: {{ item.last_rating === 'easy' ? 'Fácil' : item.last_rating === 'medium' ? 'Médio' : 'Difícil' }}
        </span>
        <span v-if="progress && progress.total > 0" class="round-counter">
          {{ progress.current }} / {{ progress.total }}
        </span>
      </div>
    </div>

    <!-- Área Cognitiva da Pergunta / Cloze -->
    <div class="cognitive-body">
      <div v-if="item.kind === 'question'" class="question-container">
        <p class="question-text">{{ item.question_text }}</p>
      </div>

      <div v-else class="cloze-container">
        <p class="cloze-text">
          <span v-if="item.context_prefix" class="cloze-prefix">{{ item.context_prefix }} </span>
          <span
            class="cloze-gap"
            :class="{ revealed: isRevealed }"
          >
            {{ isRevealed ? item.expected_answer : '[...]' }}
          </span>
          <span v-if="item.context_suffix" class="cloze-suffix"> {{ item.context_suffix }}</span>
        </p>
      </div>

      <!-- Resposta Revelada (para tipo question) -->
      <transition name="card-reveal">
        <div
          v-if="isRevealed && item.kind === 'question'"
          class="revealed-answer-box"
        >
          <span class="answer-label">Resposta:</span>
          <p class="expected-answer">{{ item.expected_answer }}</p>
        </div>
      </transition>
    </div>

    <!-- Barra de Ações: Revelar ou Avaliar -->
    <div class="card-footer">
      <div v-if="!isRevealed" class="reveal-action">
        <button
          type="button"
          class="btn-reveal"
          :disabled="busy"
          @click="emit('reveal')"
        >
          <span class="btn-text">Revelar Resposta</span>
          <kbd class="kbd-shortcut" aria-hidden="true">Espaço</kbd>
        </button>
      </div>

      <div v-else class="rating-actions">
        <div class="rating-prompt">Como foi recordar este conteúdo?</div>
        <div class="rating-buttons" role="group" aria-label="Avalie sua facilidade de recordação">
          <button
            type="button"
            class="rating-btn rate-hard"
            :disabled="busy"
            @click="emit('rate', 'hard')"
          >
            <span class="rate-title">Difícil</span>
            <kbd class="rate-kbd" aria-hidden="true">1</kbd>
          </button>

          <button
            type="button"
            class="rating-btn rate-medium"
            :disabled="busy"
            @click="emit('rate', 'medium')"
          >
            <span class="rate-title">Médio</span>
            <kbd class="rate-kbd" aria-hidden="true">2</kbd>
          </button>

          <button
            type="button"
            class="rating-btn rate-easy"
            :disabled="busy"
            @click="emit('rate', 'easy')"
          >
            <span class="rate-title">Fácil</span>
            <kbd class="rate-kbd" aria-hidden="true">3</kbd>
          </button>
        </div>
      </div>
    </div>
  </article>
</template>

<style scoped>
.review-card {
  display: flex;
  flex-direction: column;
  background-color: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border-subtle, #e2e8f0);
  border-radius: var(--radius-card, 1rem);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  min-height: 380px;
  position: relative;
}

.card-progress-bar {
  width: 100%;
  height: 4px;
  background-color: var(--color-border-subtle, #e2e8f0);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: var(--color-accent, #3b82f6);
  transition: width 220ms ease;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.15rem 1.5rem;
  background-color: var(--color-surface-soft, rgba(0, 0, 0, 0.02));
  border-bottom: 1px solid var(--color-border-subtle, #e2e8f0);
  gap: 1rem;
}

.origin-breadcrumbs {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.8125rem;
  color: var(--color-text-secondary, #64748b);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.breadcrumb-book {
  font-weight: 600;
  color: var(--color-text, #0f172a);
}

.breadcrumb-separator {
  opacity: 0.6;
}

.card-badges {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.kind-badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.2rem 0.55rem;
  border-radius: 9999px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.badge-question {
  background-color: var(--color-accent-subtle, rgba(59, 130, 246, 0.12));
  color: var(--color-link, #3b82f6);
}

.badge-hidden {
  background-color: var(--color-surface-soft, rgba(0, 0, 0, 0.06));
  color: var(--color-text-secondary, #475569);
}

.history-badge,
.round-counter {
  font-size: 0.75rem;
  color: var(--color-text-secondary, #64748b);
  padding: 0.15rem 0.5rem;
  border-radius: 6px;
  background-color: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border-subtle, #e2e8f0);
}

/* Corpo Cognitivo */
.cognitive-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 2.25rem 2rem;
  gap: 1.5rem;
}

.question-text {
  font-family: var(--font-serif, "EB Garamond", Garamond, Georgia, serif);
  font-size: 1.45rem;
  line-height: 1.55;
  color: var(--color-text, #0f172a);
  margin: 0;
  letter-spacing: -0.01em;
}

.cloze-text {
  font-family: var(--font-serif, "EB Garamond", Garamond, Georgia, serif);
  font-size: 1.4rem;
  line-height: 1.6;
  color: var(--color-text, #0f172a);
  margin: 0;
}

.cloze-gap {
  display: inline-block;
  padding: 0.15rem 0.55rem;
  border-radius: 6px;
  background-color: var(--color-accent-subtle, rgba(59, 130, 246, 0.12));
  color: var(--color-link, #3b82f6);
  font-weight: 600;
  border: 1px dashed var(--color-accent, currentColor);
  transition: all 220ms ease;
}

.cloze-gap.revealed {
  border-style: solid;
  border-color: var(--color-border-subtle, #cbd5e1);
  background-color: var(--color-surface-soft, rgba(0, 0, 0, 0.04));
  color: var(--color-text, #0f172a);
}

.revealed-answer-box {
  padding: 1.25rem 1.5rem;
  border-radius: 10px;
  background-color: var(--color-surface-soft, rgba(0, 0, 0, 0.03));
  border: 1px solid var(--color-border-subtle, #e2e8f0);
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.answer-label {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-link, #3b82f6);
}

.expected-answer {
  font-family: var(--font-serif, "EB Garamond", Garamond, Georgia, serif);
  font-size: 1.25rem;
  line-height: 1.5;
  color: var(--color-text, #0f172a);
  margin: 0;
}

/* Transição de Revelação */
.card-reveal-enter-active {
  transition: opacity 220ms ease, transform 220ms cubic-bezier(0.4, 0, 0.2, 1);
}
.card-reveal-enter-from {
  opacity: 0;
  transform: translateY(6px);
}

/* Rodapé */
.card-footer {
  padding: 1.25rem 2rem;
  background-color: var(--color-surface-soft, rgba(0, 0, 0, 0.02));
  border-top: 1px solid var(--color-border-subtle, #e2e8f0);
}

.reveal-action {
  display: flex;
  justify-content: center;
}

.btn-reveal {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  min-height: 44px;
  padding: 0.75rem 2rem;
  border-radius: var(--radius-button, 10px);
  background-color: var(--color-accent, var(--color-primary, #3b82f6));
  color: var(--color-on-accent, #ffffff);
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  border: none;
  box-shadow: 0 2px 6px -1px rgba(0, 0, 0, 0.08);
  transition: opacity 180ms ease, transform 180ms ease;
}

.btn-reveal:hover:not(:disabled) {
  opacity: 0.92;
  transform: translateY(-1px);
}

.kbd-shortcut {
  font-family: monospace;
  font-size: 0.75rem;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  background-color: rgba(255, 255, 255, 0.25);
  color: inherit;
}

.rating-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.rating-prompt {
  font-size: 0.85rem;
  color: var(--color-text-secondary, #64748b);
  font-weight: 500;
}

.rating-buttons {
  display: flex;
  gap: 1rem;
  width: 100%;
  max-width: 480px;
}

.rating-btn {
  flex: 1;
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  padding: 0.6rem 0.75rem;
  border-radius: 8px;
  border: 1px solid var(--color-border-subtle, #e2e8f0);
  background-color: var(--color-surface, #ffffff);
  cursor: pointer;
  gap: 0.25rem;
  transition: transform 150ms ease, border-color 150ms ease, background-color 150ms ease;
}

.rating-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.rate-hard:hover {
  border-color: var(--color-error, #ef4444);
}
.rate-medium:hover {
  border-color: var(--color-warning, #f59e0b);
}
.rate-easy:hover {
  border-color: var(--color-success, #10b981);
}

.rate-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--color-text, #0f172a);
}

.rate-kbd {
  font-family: monospace;
  font-size: 0.7rem;
  padding: 0.1rem 0.4rem;
  border-radius: 3px;
  background-color: var(--color-surface-soft, rgba(0, 0, 0, 0.06));
  color: var(--color-text-secondary, #64748b);
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

@media (max-width: 640px) {
  .cognitive-body {
    padding: 1.5rem 1.25rem;
  }
  .question-text, .cloze-text {
    font-size: 1.2rem;
  }
  .card-footer {
    padding: 1rem 1.25rem;
  }
  .rating-buttons {
    gap: 0.5rem;
  }
}
</style>
