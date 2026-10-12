<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { LANDING_SIMULATOR_DATA } from '../../data/landingSimulator'
import type { SimulatorDimensionId } from '../../data/landingSimulator'
import Icon from '../ui/Icon.vue'

const activeDimensionId = ref<SimulatorDimensionId>('resumo')
const expandedMobile = ref<boolean>(false)
const tabRefs = ref<HTMLElement[]>([])

const dimensions = LANDING_SIMULATOR_DATA.dimensions
const work = LANDING_SIMULATOR_DATA.work

const activeDimension = computed(() => {
  return dimensions.find((d) => d.id === activeDimensionId.value) || dimensions[0]
})

function selectDimension(id: SimulatorDimensionId) {
  activeDimensionId.value = id
}

function onTabKeydown(event: KeyboardEvent, currentIndex: number) {
  const total = dimensions.length
  let targetIndex = -1

  switch (event.key) {
    case 'ArrowRight':
    case 'ArrowDown':
      event.preventDefault()
      targetIndex = (currentIndex + 1) % total
      break
    case 'ArrowLeft':
    case 'ArrowUp':
      event.preventDefault()
      targetIndex = (currentIndex - 1 + total) % total
      break
    case 'Home':
      event.preventDefault()
      targetIndex = 0
      break
    case 'End':
      event.preventDefault()
      targetIndex = total - 1
      break
    default:
      return
  }

  if (targetIndex >= 0) {
    const nextId = dimensions[targetIndex].id
    selectDimension(nextId)
    nextTick(() => {
      tabRefs.value[targetIndex]?.focus()
    })
  }
}
</script>

<template>
  <section id="metodo" class="simulator-section" aria-labelledby="simulator-heading">
    <div class="simulator-container">
      <!-- Cabeçalho da Seção -->
      <div class="section-intro">
        <span class="section-eyebrow">Simulador In-Place</span>
        <h2 id="simulator-heading" class="section-title">
          A bancada do método: quatro camadas sobre o mesmo texto.
        </h2>
        <p class="section-lead">
          Experimente na prática. À esquerda está a página da obra de Machado de Assis; à direita, o caderno analítico dividindo o estudo em quatro perguntas estruturadas. Clique nas abas e veja o texto se iluminar.
        </p>
      </div>

      <!-- Livro Aberto: Metáfora da Obra ao Lado do Caderno -->
      <div class="open-book-workbench">
        <!-- Lado Esquerdo: Página da Obra -->
        <article class="work-page" aria-label="Página da obra literária">
          <header class="work-header">
            <div class="work-meta">
              <span class="work-author">{{ work.author }}</span>
              <span class="work-title"><em>{{ work.title }}</em> ({{ work.year }})</span>
            </div>
            <div class="work-section-badge">{{ work.sectionTitle }}</div>
          </header>

          <div
            class="work-body"
            :class="{ 'is-collapsed-mobile': !expandedMobile }"
          >
            <!-- Parágrafo 1 -->
            <p class="work-paragraph">
              Que Stendhal confessasse haver escrito um de seus livros para cem leitores, coisa é que admira e consterna. O que não admira, nem provavelmente consternará é se este outro livro não tiver os cem leitores de Stendhal, nem cinquenta, nem vinte e, quando muito, dez. Dez? Talvez cinco.
            </p>

            <!-- Parágrafo 2 com Destaques -->
            <p class="work-paragraph">
              <span
                class="highlight-text"
                :class="{
                  'is-active': activeDimensionId === 'explicacao',
                  'is-dimmed': activeDimensionId !== 'explicacao',
                }"
              >
                Trata-se, na verdade, de uma obra difusa, na qual eu, Brás Cubas,
              </span>
              <span
                class="highlight-text"
                :class="{
                  'is-active': activeDimensionId === 'referencias',
                  'is-dimmed': activeDimensionId !== 'referencias',
                }"
              >
                se adotei a forma livre de um Sterne ou de um Xavier de Maistre,
              </span>
              <span
                class="highlight-text"
                :class="{
                  'is-active': activeDimensionId === 'conceitos',
                  'is-dimmed': activeDimensionId !== 'conceitos',
                }"
              >
                não sei se lhe meti algumas rabugens de pessimismo.
              </span>
              Pode ser.
              <span
                class="highlight-text"
                :class="{
                  'is-active': activeDimensionId === 'resumo',
                  'is-dimmed': activeDimensionId !== 'resumo',
                }"
              >
                Obra de finado. Escrevi-a com a pena da galhofa e a tinta da melancolia, e não é difícil antever o que poderá sair de semelhante conúbio.
              </span>
            </p>

            <!-- Parágrafo 3 -->
            <p class="work-paragraph">
              Acresce que a gente grave achará no livro umas aparências de puro romance, ao passo que a gente frívola não achará nele o seu romance usual; ei-lo aí conchegado e desdenhado pelos sérios e pelos fúteis. Mas eu ainda espero angariar as simpatias da posteridade, deixando aos vermes que primeiro roerem as frias carnes do meu cadáver uma dedicatória expressa.
            </p>

            <!-- Nota Marginal Estilizada -->
            <aside class="marginal-note" aria-label="Anotação na margem do texto">
              <span class="marginal-label">{{ work.marginalia.label }}</span>
              <p class="marginal-text">{{ work.marginalia.text }}</p>
            </aside>
          </div>

          <!-- Controle Mobile para Expandir Trecho -->
          <div class="mobile-expand-wrapper">
            <button
              type="button"
              class="btn-expand-mobile"
              @click="expandedMobile = !expandedMobile"
            >
              <span>{{ expandedMobile ? 'Recolher trecho' : 'Ler o trecho inteiro' }}</span>
              <Icon :name="expandedMobile ? 'chevron-up' : 'chevron-down'" :size="16" />
            </button>
          </div>
        </article>

        <!-- Lado Direito: Caderno Analítico em 4 Dimensões -->
        <div class="notebook-panel" aria-label="Caderno analítico de estudo">
          <!-- Abas das 4 Dimensões (Tablist) -->
          <div class="notebook-tabs-wrapper">
            <div
              class="notebook-tabs"
              role="tablist"
              aria-label="Dimensões metodológicas de estudo"
            >
              <button
                v-for="(dim, index) in dimensions"
                :key="dim.id"
                :ref="(el) => { if (el) tabRefs[index] = el as HTMLElement }"
                type="button"
                role="tab"
                :id="`tab-${dim.id}`"
                :aria-selected="activeDimensionId === dim.id"
                :aria-controls="`panel-${dim.id}`"
                :tabindex="activeDimensionId === dim.id ? 0 : -1"
                class="notebook-tab-btn"
                :class="{ 'is-active-tab': activeDimensionId === dim.id }"
                @click="selectDimension(dim.id)"
                @keydown="onTabKeydown($event, index)"
              >
                <Icon :name="dim.iconName" :size="16" class="tab-icon" />
                <span class="tab-label">{{ dim.labelShort }}</span>
              </button>
            </div>
          </div>

          <!-- Painel Analítico Ativo (Tabpanel) -->
          <div
            :id="`panel-${activeDimension.id}`"
            role="tabpanel"
            :aria-labelledby="`tab-${activeDimension.id}`"
            tabindex="0"
            class="notebook-content-panel"
          >
            <div class="dimension-header">
              <div class="dim-question-badge">
                <Icon name="search" :size="14" />
                <span>{{ activeDimension.question }}</span>
              </div>
              <h3 class="dim-heading">{{ activeDimension.title }}</h3>
              <p class="dim-subheading">{{ activeDimension.subtitle }}</p>
            </div>

            <div class="dim-body-text">
              <p>{{ activeDimension.content }}</p>
            </div>

            <div class="dim-insights-box">
              <h4 class="insights-title">Núcleos de fixação analítica:</h4>
              <ul class="insights-list">
                <li
                  v-for="(insight, idx) in activeDimension.keyInsights"
                  :key="idx"
                  class="insight-item"
                >
                  <Icon name="check" :size="16" class="insight-icon" />
                  <span>{{ insight }}</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.simulator-section {
  padding-block: clamp(4rem, 8vw, 7.5rem);
  background-color: var(--color-page);
  color: var(--color-text);
  border-bottom: 1px solid var(--color-border-divider, var(--color-border));
}

.simulator-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 clamp(1rem, 4vw, 3rem);
}

.section-intro {
  max-width: 68ch;
  margin-bottom: clamp(2.5rem, 5vw, 4rem);
}

.section-eyebrow {
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--color-accent);
  display: block;
  margin-bottom: 0.75rem;
}

.section-title {
  font-family: var(--font-reading, "Caderno EB Garamond", serif);
  font-size: clamp(2rem, 3.5vw, 3rem);
  font-weight: 600;
  line-height: 1.15;
  letter-spacing: -0.015em;
  margin: 0 0 1rem 0;
  color: var(--color-text);
}

.section-lead {
  font-size: 1.1rem;
  line-height: 1.6;
  color: var(--color-text);
  margin: 0;
  opacity: 0.95;
}

/* Bancada Estilo Livro Aberto */
.open-book-workbench {
  display: grid;
  grid-template-columns: 1fr 1fr;
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg, 12px);
  overflow: hidden;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.05);
}

/* Lado Esquerdo: Página da Obra */
.work-page {
  padding: clamp(1.75rem, 3.5vw, 3rem);
  border-right: 1px solid var(--color-border-divider, var(--color-border));
  display: flex;
  flex-direction: column;
  background-color: var(--color-page);
}

.work-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--color-border);
}

.work-author {
  display: block;
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-accent);
}

.work-title {
  font-size: 0.95rem;
  color: var(--color-text);
}

.work-section-badge {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.25rem 0.65rem;
  border-radius: var(--radius-sm, 4px);
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  color: var(--color-text);
}

.work-body {
  font-family: var(--font-reading, "Caderno EB Garamond", serif);
  font-size: 1.25rem;
  line-height: 1.7;
  color: var(--color-text);
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.work-paragraph {
  margin: 0;
  text-indent: 1.5rem;
}

/* Marcações de Texto Sincronizadas */
.highlight-text {
  transition: background-color 0.15s ease, border-bottom 0.15s ease, color 0.15s ease;
  padding: 0 2px;
  border-radius: 2px;
}

.highlight-text.is-active {
  background-color: var(--color-selected-bg, #f3d7b5);
  color: var(--color-selected-text, var(--color-text));
  border-bottom: 2px double var(--color-accent);
  font-weight: 500;
}

.highlight-text.is-dimmed {
  border-bottom: 1px dashed var(--color-border);
  opacity: 0.85;
}

/* Nota Marginal */
.marginal-note {
  margin-top: 1rem;
  padding: 0.85rem 1.25rem;
  background-color: var(--color-surface);
  border-left: 3px solid var(--color-accent);
  border-radius: 0 var(--radius-sm, 4px) var(--radius-sm, 4px) 0;
}

.marginal-label {
  display: block;
  font-family: var(--font-sans, sans-serif);
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-accent);
  margin-bottom: 0.25rem;
}

.marginal-text {
  margin: 0;
  font-size: 0.95rem;
  line-height: 1.45;
  color: var(--color-text);
}

.mobile-expand-wrapper {
  display: none;
  margin-top: 1rem;
}

.btn-expand-mobile {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--color-accent);
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md, 6px);
  cursor: pointer;
  min-height: 44px;
}

/* Lado Direito: Caderno Analítico */
.notebook-panel {
  display: flex;
  flex-direction: column;
  background-color: var(--color-surface);
}

.notebook-tabs-wrapper {
  border-bottom: 1px solid var(--color-border);
  background-color: var(--color-page);
  overflow-x: auto;
}

.notebook-tabs {
  display: flex;
  padding: 0.5rem 0.75rem 0 0.75rem;
  gap: 0.35rem;
}

.notebook-tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.75rem 1.15rem;
  font-size: 0.925rem;
  font-weight: 600;
  color: var(--color-text);
  background-color: transparent;
  border: 1px solid transparent;
  border-bottom: none;
  border-radius: var(--radius-md, 6px) var(--radius-md, 6px) 0 0;
  cursor: pointer;
  min-height: 44px;
  position: relative;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.notebook-tab-btn:hover:not(.is-active-tab) {
  background-color: var(--color-surface-hover, rgba(0, 0, 0, 0.04));
}

.notebook-tab-btn:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: -2px;
}

.notebook-tab-btn.is-active-tab {
  background-color: var(--color-surface);
  color: var(--color-accent);
  border-color: var(--color-border);
  border-bottom-color: var(--color-surface);
  margin-bottom: -1px;
}

.tab-icon {
  flex-shrink: 0;
}

/* Painel de Conteúdo Analítico */
.notebook-content-panel {
  padding: clamp(1.75rem, 3.5vw, 3rem);
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 460px; /* Previne CLS */
  outline: none;
}

.notebook-content-panel:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: -2px;
}

.dim-question-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.3rem 0.65rem;
  border-radius: var(--radius-sm, 4px);
  background-color: var(--color-page);
  color: var(--color-accent);
  border: 1px solid var(--color-border);
  margin-bottom: 0.75rem;
}

.dim-heading {
  font-family: var(--font-reading, "Caderno EB Garamond", serif);
  font-size: 1.85rem;
  font-weight: 600;
  line-height: 1.2;
  margin: 0 0 0.4rem 0;
  color: var(--color-text);
}

.dim-subheading {
  font-size: 1rem;
  color: var(--color-text);
  opacity: 0.85;
  margin: 0 0 1.5rem 0;
}

.dim-body-text {
  font-size: 1.05rem;
  line-height: 1.65;
  color: var(--color-text);
  margin-bottom: 1.75rem;
}

.dim-body-text p {
  margin: 0;
}

.dim-insights-box {
  margin-top: auto;
  padding: 1.25rem;
  background-color: var(--color-page);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md, 8px);
}

.insights-title {
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-text);
  margin: 0 0 0.75rem 0;
}

.insights-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.insight-item {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  font-size: 0.925rem;
  line-height: 1.45;
  color: var(--color-text);
}

.insight-icon {
  color: var(--color-accent);
  flex-shrink: 0;
  margin-top: 2px;
}

/* Responsividade */
@media (max-width: 900px) {
  .open-book-workbench {
    grid-template-columns: 1fr;
  }

  .work-page {
    border-right: none;
    border-bottom: 1px solid var(--color-border-divider, var(--color-border));
  }

  .work-body.is-collapsed-mobile {
    max-height: 240px;
    overflow: hidden;
    position: relative;
  }

  .work-body.is-collapsed-mobile::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 80px;
    background: linear-gradient(to bottom, transparent, var(--color-page));
  }

  .mobile-expand-wrapper {
    display: block;
  }

  .notebook-content-panel {
    min-height: auto;
  }
}
</style>
