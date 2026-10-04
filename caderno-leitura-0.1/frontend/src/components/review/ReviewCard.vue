<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue'
import type { ReviewItemRead, ReviewRating } from '../../types.ts'

const props = withDefaults(
  defineProps<{
    item: ReviewItemRead
    isRevealed: boolean
    busy?: boolean
  }>(),
  {
    busy: false,
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
    } else if (event.key === '3' || event.code === 'Digit3' || event.code === 'Numpad3') {
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
    class="review-card"
    role="region"
    aria-label="Card de revisão atual"
  >
    <!-- Anúncio de leitor de tela -->
    <div class="sr-only" aria-live="polite" aria-atomic="true">
      {{ liveAnnouncement }}
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
      <transition name="fade">
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
  background-color: var(--color-bg-surface, #ffffff);
  border: 1px solid var(--color-border-subtle, #e2e8f0);
  border-radius: 1rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  min-height: 380px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.75rem;
  background-color: var(--color-bg-surface-secondary, #f8fafc);
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
  color: var(--color-text-primary, #0f172a);
}

.breadcrumb-separator {
  color: var(--color-text-muted, #94a3b8);
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
  padding: 0.25rem 0.625rem;
  border-radius: 9999px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.badge-question {
  background-color: #e0e7ff;
  color: #3730a3;
}

.badge-hidden {
  background-color: #fef3c7;
  color: #92400e;
}

.history-badge {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  background-color: var(--color-bg-surface, #ffffff);
  border: 1px solid var(--color-border-subtle, #e2e8f0);
  color: var(--color-text-muted, #64748b);
}

.cognitive-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 2.5rem 2rem;
  gap: 1.5rem;
}

.question-text {
  font-size: 1.375rem;
  line-height: 1.6;
  font-weight: 600;
  color: var(--color-text-primary, #0f172a);
  text-align: center;
  margin: 0;
}

.cloze-text {
  font-size: 1.25rem;
  line-height: 1.7;
  color: var(--color-text-primary, #0f172a);
  text-align: center;
  margin: 0;
}

.cloze-gap {
  display: inline-block;
  padding: 0.125rem 0.625rem;
  border-radius: 0.375rem;
  background-color: #fef3c7;
  color: #b45309;
  font-weight: 700;
  transition: all 0.2s ease;
  border-bottom: 2px solid #f59e0b;
}

.cloze-gap.revealed {
  background-color: #dcfce7;
  color: #15803d;
  border-bottom-color: #22c55e;
}

.revealed-answer-box {
  background-color: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 0.75rem;
  padding: 1.25rem 1.5rem;
  text-align: center;
  margin-top: 1rem;
}

.answer-label {
  display: block;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #166534;
  letter-spacing: 0.05em;
  margin-bottom: 0.375rem;
}

.expected-answer {
  font-size: 1.125rem;
  font-weight: 600;
  color: #14532d;
  margin: 0;
  line-height: 1.5;
}

.card-footer {
  padding: 1.5rem 2rem;
  background-color: var(--color-bg-surface-secondary, #f8fafc);
  border-top: 1px solid var(--color-border-subtle, #e2e8f0);
}

.reveal-action {
  display: flex;
  justify-content: center;
}

.btn-reveal {
  min-height: 48px;
  min-width: 200px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 0.75rem 2rem;
  background-color: var(--color-primary, #2563eb);
  color: #ffffff;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2);
  transition: all 0.15s ease;
}

.btn-reveal:hover:not(:disabled) {
  background-color: var(--color-primary-hover, #1d4ed8);
  transform: translateY(-1px);
}

.kbd-shortcut {
  background: rgba(255, 255, 255, 0.2);
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-family: inherit;
  font-weight: 700;
}

.rating-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.rating-prompt {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-secondary, #64748b);
}

.rating-buttons {
  display: flex;
  justify-content: center;
  gap: 1rem;
  width: 100%;
  max-width: 500px;
}

.rating-btn {
  flex: 1;
  min-height: 48px;
  min-width: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.15s ease;
}

.rate-hard {
  background-color: #fee2e2;
  color: #991b1b;
  border-color: #fca5a5;
}

.rate-hard:hover:not(:disabled) {
  background-color: #fecaca;
}

.rate-medium {
  background-color: #fef3c7;
  color: #92400e;
  border-color: #fcd34d;
}

.rate-medium:hover:not(:disabled) {
  background-color: #fde68a;
}

.rate-easy {
  background-color: #dcfce7;
  color: #166534;
  border-color: #86efac;
}

.rate-easy:hover:not(:disabled) {
  background-color: #bbf7d0;
}

.rate-kbd {
  background: rgba(0, 0, 0, 0.08);
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 700;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
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
    padding: 1.5rem 1rem;
  }

  .question-text {
    font-size: 1.125rem;
  }

  .cloze-text {
    font-size: 1.0625rem;
  }

  .rating-buttons {
    gap: 0.5rem;
  }

  .rating-btn {
    min-height: 44px;
    padding: 0.625rem 0.5rem;
    font-size: 0.875rem;
  }
}
</style>
