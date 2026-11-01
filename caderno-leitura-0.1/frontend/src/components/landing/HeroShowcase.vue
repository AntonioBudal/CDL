<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import Icon from '../ui/Icon.vue'

// Ilustração da interface (acervo, estudo e marcações) desenhada em HTML/CSS; não usa dados de ninguém.
interface Slide {
  id: 'acervo' | 'estudo' | 'marcacoes'
  label: string
}

const slides: Slide[] = [
  { id: 'acervo', label: 'Acervo de livros' },
  { id: 'estudo', label: 'Estudo em quatro partes' },
  { id: 'marcacoes', label: 'Marcações coloridas' },
]

const covers = [
  { title: 'Memórias Póstumas de Brás Cubas', author: 'Machado de Assis', tone: 'c1', chapters: 160 },
  { title: 'Dom Casmurro', author: 'Machado de Assis', tone: 'c2', chapters: 148 },
  { title: 'O Cortiço', author: 'Aluísio Azevedo', tone: 'c3', chapters: 23 },
  { title: 'Iracema', author: 'José de Alencar', tone: 'c4', chapters: 33 },
]

const marks = [
  { kind: 'Destaque', color: 'yellow' },
  { kind: 'Citação', color: 'green' },
  { kind: 'Nota', color: 'blue' },
  { kind: 'Pergunta', color: 'pink' },
  { kind: 'Oculto', color: 'purple' },
]

const INTERVAL_MS = 5000
const current = ref(0)
const userPaused = ref(false)
const hoverPaused = ref(false)
let timer: ReturnType<typeof setInterval> | null = null

const isPlaying = computed(() => !userPaused.value && !hoverPaused.value)

function goTo(index: number) {
  current.value = (index + slides.length) % slides.length
}

function tick() {
  if (isPlaying.value) goTo(current.value + 1)
}

function togglePause() {
  userPaused.value = !userPaused.value
}

onMounted(() => {
  // Com movimento reduzido, começa parado; o visitante pode iniciar a troca pelo botão.
  userPaused.value = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches === true
  timer = setInterval(tick, INTERVAL_MS)
})

onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
})
</script>

<template>
  <div
    class="showcase"
    role="region"
    aria-roledescription="carrossel"
    aria-label="Ilustração da interface do Leitorum"
    @mouseenter="hoverPaused = true"
    @mouseleave="hoverPaused = false"
    @focusin="hoverPaused = true"
    @focusout="hoverPaused = false"
  >
    <div class="glow" aria-hidden="true"></div>

    <div class="stage">
      <div class="window">
        <div class="window-bar" aria-hidden="true">
          <span class="dot"></span><span class="dot"></span><span class="dot"></span>
          <span class="window-title">Leitorum</span>
        </div>

        <div class="slides" aria-live="off">
          <Transition name="slide" mode="out-in">
            <!-- Acervo -->
            <div
              v-if="slides[current].id === 'acervo'"
              key="acervo"
              class="slide"
              role="group"
              aria-roledescription="slide"
              :aria-label="`1 de 3: ${slides[0].label}`"
            >
              <div class="covers">
                <div v-for="(cover, idx) in covers" :key="cover.title" class="cover-card" :style="{ '--i': idx }">
                  <div class="cover" :class="cover.tone">
                    <span class="cover-title">{{ cover.title }}</span>
                    <span class="cover-author">{{ cover.author }}</span>
                  </div>
                  <span class="cover-meta">{{ cover.chapters }} capítulos</span>
                </div>
              </div>
            </div>

            <!-- Estudo -->
            <div
              v-else-if="slides[current].id === 'estudo'"
              key="estudo"
              class="slide"
              role="group"
              aria-roledescription="slide"
              :aria-label="`2 de 3: ${slides[1].label}`"
            >
              <div class="mock-tabs" aria-hidden="true">
                <span class="mock-tab is-on">Resumo</span>
                <span class="mock-tab">Explicação</span>
                <span class="mock-tab">Conceitos</span>
                <span class="mock-tab">Referências</span>
              </div>
              <p class="study-heading">Ao leitor, p. 1</p>
              <p class="study-text">
                Brás Cubas apresenta o livro e diz que, se Stendhal escreveu para cem leitores, ele espera ter cinco.
              </p>
              <div class="skeleton" aria-hidden="true">
                <span style="width: 92%"></span><span style="width: 78%"></span><span style="width: 85%"></span>
              </div>
            </div>

            <!-- Marcações -->
            <div
              v-else
              key="marcacoes"
              class="slide"
              role="group"
              aria-roledescription="slide"
              :aria-label="`3 de 3: ${slides[2].label}`"
            >
              <p class="marked-text">
                <mark class="hl yellow">Obra de finado.</mark> Escrevi-a com a
                <mark class="hl green">pena da galhofa</mark> e a
                <mark class="hl blue">tinta da melancolia</mark>; e não é difícil antever
                <mark class="hl pink">o que poderá sair desse conúbio</mark>.
              </p>
              <ul class="mark-legend">
                <li v-for="mark in marks" :key="mark.kind" class="mark-chip">
                  <span class="swatch" :class="mark.color" aria-hidden="true"></span>{{ mark.kind }}
                </li>
              </ul>
            </div>
          </Transition>
        </div>
      </div>

      <div class="float-chip chip-a" aria-hidden="true">
        <Icon name="check-circle" :size="14" /> Revisão: difícil primeiro
      </div>
      <div class="float-chip chip-b" aria-hidden="true">
        <Icon name="download" :size="14" /> Markdown · .zip
      </div>
    </div>

    <div class="controls">
      <button
        type="button"
        class="control-btn quiet"
        :aria-label="userPaused ? 'Retomar a troca automática' : 'Pausar a troca automática'"
        @click="togglePause"
      >
        <svg v-if="userPaused" width="14" height="14" viewBox="0 0 24 24" aria-hidden="true"><path d="M7 4l13 8-13 8z" fill="currentColor" /></svg>
        <svg v-else width="14" height="14" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 4h4v16H6zM14 4h4v16h-4z" fill="currentColor" /></svg>
      </button>
      <div class="dots">
        <button
          v-for="(slide, idx) in slides"
          :key="slide.id"
          type="button"
          class="dot-btn quiet"
          :class="{ 'is-current': idx === current }"
          :aria-label="`Mostrar ${slide.label}`"
          :aria-current="idx === current ? 'true' : undefined"
          @click="goTo(idx)"
        >
          <span class="dot-fill" :class="{ 'is-running': idx === current && isPlaying }"></span>
        </button>
      </div>
      <span class="slide-label">{{ slides[current].label }}</span>
    </div>
  </div>
</template>

<style scoped>
.showcase {
  position: relative;
  isolation: isolate;
}

.glow {
  position: absolute;
  inset: 8% 6%;
  z-index: -1;
  background:
    radial-gradient(closest-side, color-mix(in srgb, var(--color-accent) 35%, transparent), transparent),
    radial-gradient(closest-side at 80% 70%, color-mix(in srgb, var(--color-link) 25%, transparent), transparent);
  filter: blur(40px);
  opacity: 0.7;
  pointer-events: none;
}

.stage {
  position: relative;
  perspective: 1400px;
}

.window {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 14px;
  box-shadow:
    0 30px 60px -20px color-mix(in srgb, var(--color-text) 30%, transparent),
    0 0 0 1px color-mix(in srgb, var(--color-accent) 12%, transparent);
  transform: rotateY(-9deg) rotateX(5deg);
  transform-style: preserve-3d;
  animation: float 7s ease-in-out infinite;
  overflow: hidden;
}

@keyframes float {
  0%, 100% { transform: rotateY(-9deg) rotateX(5deg) translateY(0); }
  50% { transform: rotateY(-6deg) rotateX(3deg) translateY(-10px); }
}

.window-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0.6rem 0.85rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-page);
}

.dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: var(--color-border);
}

.window-title {
  margin-left: 0.5rem;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--color-text);
}

.slides {
  padding: 1.1rem;
  min-height: 268px;
}

.slide {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.slide-enter-active,
.slide-leave-active {
  transition: opacity 0.35s ease, transform 0.35s ease;
}

.slide-enter-from {
  opacity: 0;
  transform: translateX(24px);
}

.slide-leave-to {
  opacity: 0;
  transform: translateX(-24px);
}

/* Acervo */
.covers {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.6rem;
}

.cover-card {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  animation: rise 0.5s ease both;
  animation-delay: calc(var(--i) * 90ms);
}

@keyframes rise {
  from { opacity: 0; transform: translateY(14px); }
  to { opacity: 1; transform: none; }
}

.cover {
  aspect-ratio: 2 / 3;
  border-radius: 4px 8px 8px 4px;
  padding: 0.5rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  color: #fdfaf3;
  box-shadow: inset 4px 0 0 rgba(0, 0, 0, 0.18), 0 6px 14px -6px rgba(0, 0, 0, 0.45);
}

.cover.c1 { background: linear-gradient(160deg, #3b2f2f, #6b3a2e); }
.cover.c2 { background: linear-gradient(160deg, #1f3a4d, #2f6173); }
.cover.c3 { background: linear-gradient(160deg, #3c4a2a, #6a7a3a); }
.cover.c4 { background: linear-gradient(160deg, #4a2a4a, #7a3f63); }

.cover-title {
  font-family: var(--font-reading, "Caderno EB Garamond", serif);
  font-size: 0.72rem;
  font-weight: 600;
  line-height: 1.15;
}

.cover-author {
  font-size: 0.55rem;
  opacity: 0.85;
}

.cover-meta {
  font-size: 0.7rem;
  color: var(--color-subtle, var(--color-text));
}

/* Estudo */
.mock-tabs {
  display: flex;
  gap: 0.3rem;
  flex-wrap: wrap;
}

.mock-tab {
  font-size: 0.72rem;
  font-weight: 600;
  padding: 0.3rem 0.55rem;
  border-radius: 999px;
  border: 1px solid var(--color-border);
  color: var(--color-text);
}

.mock-tab.is-on {
  background: var(--color-accent);
  border-color: var(--color-accent);
  color: var(--color-on-accent);
}

.study-heading {
  margin: 0.25rem 0 0;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--color-link);
}

.study-text {
  margin: 0;
  font-family: var(--font-reading, "Caderno EB Garamond", serif);
  font-size: 1rem;
  line-height: 1.5;
  color: var(--color-text);
}

.skeleton {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.skeleton span {
  height: 8px;
  border-radius: 4px;
  background: linear-gradient(90deg, var(--color-border), color-mix(in srgb, var(--color-border) 40%, transparent), var(--color-border));
  background-size: 200% 100%;
  animation: shimmer 2.2s linear infinite;
}

@keyframes shimmer {
  to { background-position: -200% 0; }
}

/* Marcações */
.marked-text {
  margin: 0;
  font-family: var(--font-reading, "Caderno EB Garamond", serif);
  font-size: 1.05rem;
  line-height: 1.75;
  color: var(--color-text);
}

.hl {
  color: #1c1917;
  padding: 0 2px;
  border-radius: 3px;
  background-repeat: no-repeat;
  background-size: 0% 100%;
  animation: sweep 0.7s ease forwards;
}

.hl.yellow { background-image: linear-gradient(var(--hl-yellow, #fef08a), var(--hl-yellow, #fef08a)); animation-delay: 0.15s; }
.hl.green { background-image: linear-gradient(var(--hl-green, #bbf7d0), var(--hl-green, #bbf7d0)); animation-delay: 0.55s; }
.hl.blue { background-image: linear-gradient(var(--hl-blue, #bfdbfe), var(--hl-blue, #bfdbfe)); animation-delay: 0.95s; }
.hl.pink { background-image: linear-gradient(var(--hl-pink, #fbcfe8), var(--hl-pink, #fbcfe8)); animation-delay: 1.35s; }

@keyframes sweep {
  to { background-size: 100% 100%; }
}

.mark-legend {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.mark-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.72rem;
  font-weight: 600;
  padding: 0.25rem 0.55rem;
  border-radius: 999px;
  border: 1px solid var(--color-border);
  color: var(--color-text);
}

.swatch {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.swatch.yellow { background: var(--hl-yellow, #fef08a); }
.swatch.green { background: var(--hl-green, #bbf7d0); }
.swatch.blue { background: var(--hl-blue, #bfdbfe); }
.swatch.pink { background: var(--hl-pink, #fbcfe8); }
.swatch.purple { background: var(--hl-purple, #e9d5ff); }

/* Etiquetas flutuantes */
.float-chip {
  position: absolute;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.45rem 0.7rem;
  border-radius: 999px;
  background: var(--color-surface);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  box-shadow: 0 12px 24px -12px color-mix(in srgb, var(--color-text) 40%, transparent);
  animation: bob 6s ease-in-out infinite;
}

.chip-a { left: -14px; bottom: 22%; }
.chip-b { right: -10px; top: 14%; animation-delay: -3s; }

@keyframes bob {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

/* Controles */
.controls {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 1.25rem;
}

.control-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text);
  cursor: pointer;
}

.control-btn:hover {
  background: var(--color-surface-hover, var(--color-surface));
  color: var(--color-hover-text, var(--color-text));
}

.dots {
  display: flex;
  gap: 0.25rem;
}

.dot-btn {
  width: 44px;
  height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: 0;
  padding: 0;
  cursor: pointer;
}

.dot-fill {
  position: relative;
  display: block;
  width: 28px;
  height: 5px;
  border-radius: 3px;
  background: var(--color-border);
  overflow: hidden;
}

.dot-btn.is-current .dot-fill::after {
  content: '';
  position: absolute;
  inset: 0;
  background: var(--color-accent);
}

.dot-fill.is-running::after {
  transform-origin: left;
  animation: progress 5s linear;
}

@keyframes progress {
  from { transform: scaleX(0); }
  to { transform: scaleX(1); }
}

.control-btn:focus-visible,
.dot-btn:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

.slide-label {
  font-size: 0.85rem;
  color: var(--color-subtle, var(--color-text));
}

@media (max-width: 480px) {
  .float-chip {
    display: none;
  }

  .covers {
    grid-template-columns: repeat(2, 1fr);
  }

  .cover {
    aspect-ratio: 3 / 2;
  }
}

@media (prefers-reduced-motion: reduce) {
  .window,
  .float-chip,
  .cover-card,
  .skeleton span,
  .dot-fill.is-running::after {
    animation: none;
  }

  .hl {
    animation: none;
    background-size: 100% 100%;
  }

  .slide-enter-active,
  .slide-leave-active {
    transition: none;
  }
}

/* Cores pela variante .quiet (appearance-advanced.css). A geometria precisa vencer a regra global de botões
   (min-height) e as superclasses (raio e sombra), daí a especificidade reforçada. */
.control-btn {
  --quiet-bg: var(--color-surface);
  --quiet-border: var(--color-border);
}

.showcase .controls .control-btn.control-btn,
.showcase .controls .dot-btn.dot-btn {
  width: 44px;
  min-width: 44px;
  height: 44px;
  min-height: 44px;
  padding: 0;
  border-radius: 50%;
  box-shadow: none;
}
</style>
