<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const props = withDefaults(
  defineProps<{
    hasEligibleItems?: boolean
  }>(),
  {
    hasEligibleItems: false,
  },
)

const emit = defineEmits<{
  (e: 'go-to-books'): void
  (e: 'review-again'): void
}>()

const router = useRouter()
const isDemoRevealed = ref(false)

function toggleDemo() {
  isDemoRevealed.value = !isDemoRevealed.value
}

function handleGoToBooks() {
  emit('go-to-books')
  void router.push('/livros')
}

function handleReviewAgain() {
  emit('review-again')
}
</script>

<template>
  <section
    class="pedagogical-empty-container"
    role="region"
    aria-label="Guia Pedagógico de Revisão e Estudo Ativo"
  >
    <!-- Cabeçalho Acolhedor -->
    <div class="empty-hero">
      <div class="hero-icon-container" aria-hidden="true">
        <svg
          class="hero-svg"
          viewBox="0 0 24 24"
          width="40"
          height="40"
          fill="none"
          stroke="currentColor"
          stroke-width="1.6"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
          />
        </svg>
      </div>

      <h2 v-if="!hasEligibleItems" class="hero-title">
        Sua Bancada de Fixação Cognitiva está Pronta
      </h2>
      <h2 v-else class="hero-title">
        Meta Diária Concluída com Constância
      </h2>

      <p v-if="!hasEligibleItems" class="hero-subtitle">
        A Central de Revisão transforma o hábito passivo de reler em <strong>estudo ativo</strong>.
        Experimente a mecânica de fixação abaixo:
      </p>
      <p v-else class="hero-subtitle">
        Todos os seus cartões programados para hoje foram exercitados. Sua memória de longo prazo agradece a disciplina.
      </p>
    </div>

    <!-- Demonstração Interativa de Termo Oculto (Cloze) -->
    <div class="interactive-demo-card">
      <div class="demo-badge">
        <span>Demonstração Interativa de Termo Oculto</span>
      </div>

      <div class="demo-sentence">
        <span>A leitura reflexiva exige pausar e </span>
        <button
          type="button"
          class="demo-gap-btn"
          :class="{ revealed: isDemoRevealed }"
          :aria-expanded="isDemoRevealed"
          aria-label="Toque para revelar o termo oculto de demonstração"
          @click="toggleDemo"
        >
          <span v-if="!isDemoRevealed" class="gap-hidden">[ termo oculto ]</span>
          <span v-else class="gap-text">recuperar</span>
        </button>
        <span> o sentido com as próprias palavras.</span>
      </div>

      <transition name="fade">
        <div v-if="isDemoRevealed" class="demo-feedback">
          <div class="feedback-indicator" aria-hidden="true">
            <svg viewBox="0 0 20 20" width="16" height="16" fill="currentColor">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
          </div>
          <p class="feedback-text">
            <strong>Isto é Active Recall:</strong> ao tentar preencher o vazio mental antes de conferir a resposta,
            seu cérebro consolida sinapses duradouras. No Leitorum, você cria esses cartões grifando passagens nos livros.
          </p>
          <button
            type="button"
            class="btn-reset-demo"
            @click="isDemoRevealed = false"
          >
            Ocultar novamente
          </button>
        </div>
      </transition>
    </div>

    <!-- Guia Didático de 3 Passos -->
    <div v-if="!hasEligibleItems" class="guide-steps-grid">
      <div class="guide-step-card">
        <span class="step-number" aria-hidden="true">1</span>
        <h3 class="step-title">Abra qualquer Livro</h3>
        <p class="step-desc">
          Navegue pelo seu acervo e abra os capítulos ou notas que está estudando no momento.
        </p>
      </div>

      <div class="guide-step-card">
        <span class="step-number" aria-hidden="true">2</span>
        <h3 class="step-title">Grife o Conceito</h3>
        <p class="step-desc">
          Selecione com o cursor ou toque o trecho exato ou a dúvida que deseja fixar na memória.
        </p>
      </div>

      <div class="guide-step-card">
        <span class="step-number" aria-hidden="true">3</span>
        <h3 class="step-title">Crie a Pergunta</h3>
        <p class="step-desc">
          Na barra de ações, clique em <em>Pergunta</em> ou <em>Ocultar</em>. O Leitorum agendará a revisão automaticamente.
        </p>
      </div>
    </div>

    <!-- Ações Finais do Estado Vazio -->
    <div class="empty-actions-bar">
      <button
        v-if="!hasEligibleItems"
        type="button"
        class="primary-action-btn"
        title="Explorar meus Livros e Criar Estudos"
        aria-label="Explorar meus Livros e Criar Estudos"
        @click="handleGoToBooks"
      >
        <span class="btn-text-full">Explorar meus Livros e Criar Estudos</span>
        <span class="btn-text-short">Explorar Livros</span>
      </button>

      <div v-else class="all-reviewed-actions">
        <button
          type="button"
          class="primary-action-btn secondary-style"
          title="Praticar Novamente para Reforço"
          aria-label="Praticar Novamente para Reforço"
          @click="handleReviewAgain"
        >
          <span class="btn-text-full">Praticar Novamente para Reforço</span>
          <span class="btn-text-short">Praticar Novamente</span>
        </button>
        <button
          type="button"
          class="outline-action-btn"
          title="Retornar ao Acervo de Livros"
          aria-label="Retornar ao Acervo de Livros"
          @click="handleGoToBooks"
        >
          <span class="btn-text-full">Retornar ao Acervo de Livros</span>
          <span class="btn-text-short">Ir para Livros</span>
        </button>
      </div>
    </div>
  </section>
</template>

<style scoped>
.pedagogical-empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  max-width: 780px;
  margin: 1.5rem auto;
  padding: 2.25rem 1.75rem;
  background-color: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border-subtle, #e2e8f0);
  border-radius: var(--radius-card, 14px);
  box-shadow: 0 4px 14px -3px rgba(0, 0, 0, 0.04);
  text-align: center;
  gap: 1.75rem;
}

.empty-hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.6rem;
  max-width: 600px;
}

.hero-icon-container {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 68px;
  height: 68px;
  border-radius: 50%;
  background-color: var(--color-accent-subtle, rgba(59, 130, 246, 0.1));
  color: var(--color-link, var(--color-primary, #3b82f6));
  margin-bottom: 0.25rem;
}

.hero-title {
  font-family: var(--font-serif, "EB Garamond", Garamond, Georgia, serif);
  font-size: 1.65rem;
  font-weight: 600;
  color: var(--color-text, #0f172a);
  margin: 0;
  letter-spacing: -0.015em;
  line-height: 1.25;
}

.hero-subtitle {
  font-size: 0.95rem;
  line-height: 1.55;
  color: var(--color-text-secondary, #475569);
  margin: 0;
}

/* Demonstração Interativa */
.interactive-demo-card {
  width: 100%;
  background-color: var(--color-surface-soft, rgba(0, 0, 0, 0.02));
  border: 1px solid var(--color-border-subtle, #e2e8f0);
  border-radius: 12px;
  padding: 1.25rem 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.85rem;
}

.demo-badge {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-link, var(--color-primary, #3b82f6));
}

.demo-sentence {
  font-family: var(--font-serif, "EB Garamond", Garamond, Georgia, serif);
  font-size: 1.15rem;
  line-height: 1.6;
  color: var(--color-text, #0f172a);
}

.demo-gap-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.2rem 0.65rem;
  margin: 0 0.2rem;
  border-radius: 6px;
  background-color: var(--color-accent-subtle, rgba(59, 130, 246, 0.12));
  border: 1px dashed var(--color-accent, currentColor);
  color: var(--color-link, var(--color-primary, #3b82f6));
  font-family: inherit;
  font-size: 1.05rem;
  font-weight: 600;
  cursor: pointer;
  min-height: auto;
  line-height: 1.3;
  transition: transform 180ms ease, background-color 180ms ease, border-color 180ms ease;
}

.demo-gap-btn:hover {
  transform: translateY(-1px);
  background-color: var(--color-accent-hover-subtle, rgba(59, 130, 246, 0.2));
}

.demo-gap-btn.revealed {
  border-style: solid;
  border-color: var(--color-border-subtle, #cbd5e1);
  background-color: var(--color-surface, #ffffff);
  color: var(--color-text, #0f172a);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.demo-feedback {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 0.85rem 1rem;
  background-color: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border-subtle, #e2e8f0);
  border-radius: 8px;
  max-width: 580px;
  animation: fadeIn 220ms ease;
}

.feedback-indicator {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background-color: var(--color-accent, #3b82f6);
  color: var(--color-on-accent, #ffffff);
  font-size: 0.75rem;
  font-weight: bold;
}

.feedback-text {
  font-size: 0.875rem;
  line-height: 1.5;
  color: var(--color-text-secondary, #334155);
  margin: 0;
}

.btn-reset-demo {
  background: none;
  border: none;
  padding: 0.2rem 0.5rem;
  min-height: auto;
  font-size: 0.775rem;
  color: var(--color-link, #3b82f6);
  cursor: pointer;
  text-decoration: underline;
}

/* Guia de 3 Passos */
.guide-steps-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  width: 100%;
  text-align: left;
}

.guide-step-card {
  padding: 1rem 1.15rem;
  border: 1px solid var(--color-border-subtle, #e2e8f0);
  border-radius: 10px;
  background-color: var(--color-surface, #ffffff);
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.step-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background-color: var(--color-surface-soft, rgba(0, 0, 0, 0.05));
  color: var(--color-text-secondary, #475569);
  font-size: 0.8rem;
  font-weight: 700;
}

.step-title {
  font-size: 0.925rem;
  font-weight: 600;
  color: var(--color-text, #0f172a);
  margin: 0.25rem 0 0 0;
}

.step-desc {
  font-size: 0.825rem;
  line-height: 1.45;
  color: var(--color-text-secondary, #64748b);
  margin: 0;
}

/* Ações */
.empty-actions-bar {
  display: flex;
  justify-content: center;
  width: 100%;
}

.primary-action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  padding: 0.75rem 1.5rem;
  border-radius: var(--radius-button, 8px);
  background-color: var(--color-accent, var(--color-primary, #3b82f6));
  color: var(--color-on-accent, #ffffff);
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  border: 1px solid transparent;
  transition: opacity 180ms ease, transform 180ms ease;
}

.btn-text-short {
  display: none;
}

.btn-text-full {
  display: inline;
}

.primary-action-btn:hover {
  opacity: 0.92;
}

@media (hover: hover) and (pointer: fine) {
  .primary-action-btn:hover {
    transform: translateY(-1px);
  }
}

.all-reviewed-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  justify-content: center;
}

.secondary-style {
  background-color: var(--color-accent, #3b82f6);
}

.outline-action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  padding: 0.75rem 1.25rem;
  border-radius: var(--radius-button, 8px);
  background-color: transparent;
  border: 1px solid var(--color-border-strong, #cbd5e1);
  color: var(--color-text, #0f172a);
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
}

.outline-action-btn:hover {
  background-color: var(--color-surface-soft, rgba(0, 0, 0, 0.04));
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 680px) {
  .guide-steps-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .btn-text-full {
    display: none;
  }

  .btn-text-short {
    display: inline;
  }

  .primary-action-btn,
  .outline-action-btn {
    width: 100%;
    justify-content: center;
    white-space: nowrap;
    text-align: center;
  }

  .all-reviewed-actions {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
