<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { LANDING_SIMULATOR_DATA } from '../../data/landingSimulator'
import type { SimulatorDimensionId } from '../../data/landingSimulator'
import Icon from '../ui/Icon.vue'

const activeDimensionId = ref<SimulatorDimensionId>('resumo')
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
  <section id="exemplo" class="simulator-section" aria-labelledby="simulator-heading">
    <div class="simulator-container">
      <div class="section-intro">
        <h2 id="simulator-heading" class="section-title">Exemplo de estudo</h2>
        <p class="section-lead">
          Um estudo do prólogo de <em>{{ work.title }}</em>, de {{ work.author }}. Escolha uma das quatro partes para ver o que foi anotado e a que passagem ela se refere.
        </p>
      </div>

      <div class="open-book-workbench">
        <article class="work-page" aria-labelledby="work-heading">
          <header class="work-header">
            <h3 id="work-heading" class="work-meta">
              <span class="work-author">{{ work.author }}</span><span class="sr-only">, </span>
              <span class="work-title"><em>{{ work.title }}</em> ({{ work.year }}), {{ work.sectionTitle }}</span>
            </h3>
          </header>

          <p class="work-body">
            <template v-for="(segment, idx) in work.passage" :key="idx">
              <mark
                v-if="segment.dimensionId"
                class="highlight-text"
                :class="{ 'is-active': activeDimensionId === segment.dimensionId }"
              >{{ segment.text }}</mark>
              <template v-else>{{ segment.text }}</template>
            </template>
          </p>
        </article>

        <div class="notebook-panel">
          <div class="notebook-tabs-wrapper">
            <div class="notebook-tabs" role="tablist" aria-label="Partes do estudo">
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
                <span class="tab-label">{{ dim.label }}</span>
              </button>
            </div>
          </div>

          <div
            :id="`panel-${activeDimension.id}`"
            role="tabpanel"
            :aria-labelledby="`tab-${activeDimension.id}`"
            tabindex="0"
            class="notebook-content-panel"
          >
            <p class="dim-description">{{ activeDimension.description }}</p>
            <p v-if="activeDimension.content" class="dim-body-text">{{ activeDimension.content }}</p>
            <ul v-if="activeDimension.items.length" class="insights-list">
              <li v-for="(item, idx) in activeDimension.items" :key="idx" class="insight-item">{{ item }}</li>
            </ul>
          </div>
        </div>
      </div>

      <p class="simulator-note">
        No Leitorum, cada estudo fica no capítulo do livro e registra a página ou o local do trecho. O texto do livro aparece aqui só para o exemplo.
      </p>
    </div>
  </section>
</template>

<style scoped>
.simulator-section {
  padding-block: clamp(2.5rem, 6vw, 4.5rem);
  border-bottom: 1px solid var(--color-border-divider, var(--color-border));
}

.simulator-container {
  max-width: 1200px;
  margin: 0 auto;
}

.section-intro {
  max-width: 68ch;
  margin-bottom: 1.75rem;
}

.section-title {
  font-family: var(--font-reading, "Caderno EB Garamond", serif);
  font-size: clamp(1.75rem, 3vw, 2.4rem);
  font-weight: 600;
  line-height: 1.2;
  margin: 0 0 0.75rem 0;
  color: var(--color-text);
}

.section-lead {
  font-size: 1.05rem;
  line-height: 1.6;
  color: var(--color-text);
  margin: 0;
}

.open-book-workbench {
  display: grid;
  grid-template-columns: 1fr 1fr;
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg, 12px);
  overflow: hidden;
}

.work-page {
  padding: clamp(1.25rem, 3vw, 2.25rem);
  border-right: 1px solid var(--color-border-divider, var(--color-border));
  background-color: var(--color-page);
  min-width: 0;
}

.work-header {
  margin-bottom: 1.25rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--color-border);
}

.work-meta {
  margin: 0;
  font: inherit;
}

.work-author {
  display: block;
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--color-link);
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
}

.work-title {
  font-size: 0.95rem;
  font-weight: 400;
  color: var(--color-text);
}

.work-body {
  margin: 0;
  font-family: var(--font-reading, "Caderno EB Garamond", serif);
  font-size: 1.2rem;
  line-height: 1.7;
  color: var(--color-text);
}

.highlight-text {
  background-color: transparent;
  color: inherit;
  border-bottom: 1px dashed var(--color-border);
  padding: 0 2px;
  border-radius: 2px;
  transition: background-color 0.15s ease, color 0.15s ease;
}

.highlight-text.is-active {
  background-color: var(--color-selected-bg, #f3d7b5);
  color: var(--color-selected-text, var(--color-text));
  border-bottom: 2px solid var(--color-accent);
}

.notebook-panel {
  display: flex;
  flex-direction: column;
  background-color: var(--color-surface);
  min-width: 0;
}

.notebook-tabs-wrapper {
  border-bottom: 1px solid var(--color-border);
  background-color: var(--color-page);
  overflow-x: auto;
}

.notebook-tabs {
  display: flex;
  padding: 0.5rem 0.75rem 0 0.75rem;
  gap: 0.25rem;
}

.notebook-tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.7rem 0.9rem;
  font-size: 0.925rem;
  font-weight: 600;
  color: var(--color-text);
  background-color: transparent;
  border: 1px solid transparent;
  border-bottom: none;
  border-radius: var(--radius-md, 6px) var(--radius-md, 6px) 0 0;
  cursor: pointer;
  min-height: 44px;
  white-space: nowrap;
  transition: background-color 0.15s ease, color 0.15s ease;
}

.notebook-tab-btn:hover:not(.is-active-tab) {
  background-color: var(--color-surface-hover, rgba(0, 0, 0, 0.04));
  color: var(--color-hover-text, var(--color-text));
}

.notebook-tab-btn:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: -2px;
}

.notebook-tab-btn.is-active-tab {
  background-color: var(--color-surface);
  color: var(--color-link);
  border-color: var(--color-border);
  border-bottom-color: var(--color-surface);
  margin-bottom: -1px;
}

.tab-icon {
  flex-shrink: 0;
}

.notebook-content-panel {
  padding: clamp(1.25rem, 3vw, 2.25rem);
  flex: 1;
  min-height: 300px; /* evita salto de layout ao trocar de aba */
  outline: none;
}

.notebook-content-panel:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: -2px;
}

.dim-description {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--color-link);
  margin: 0 0 0.75rem 0;
}

.dim-body-text {
  font-size: 1.05rem;
  line-height: 1.65;
  color: var(--color-text);
  margin: 0;
}

.insights-list {
  margin: 0;
  padding-left: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.insight-item {
  font-size: 1rem;
  line-height: 1.55;
  color: var(--color-text);
}

.simulator-note {
  max-width: 68ch;
  margin: 1rem 0 0 0;
  font-size: 0.9rem;
  line-height: 1.5;
  color: var(--color-subtle, var(--color-text));
}

@media (max-width: 900px) {
  .open-book-workbench {
    grid-template-columns: 1fr;
  }

  .work-page {
    border-right: none;
    border-bottom: 1px solid var(--color-border-divider, var(--color-border));
  }

  .notebook-content-panel {
    min-height: 0;
  }
}

@media (max-width: 480px) {
  .tab-icon {
    display: none;
  }

  /* Quatro abas não cabem lado a lado em 320-480px; em grade 2x2 nenhuma fica escondida. */
  .notebook-tabs {
    display: grid;
    grid-template-columns: 1fr 1fr;
    padding: 0.5rem;
  }

  .notebook-tab-btn {
    justify-content: center;
    border-radius: var(--radius-md, 6px);
  }

  .notebook-tab-btn.is-active-tab {
    border-bottom: 1px solid var(--color-border);
    margin-bottom: 0;
  }
}
</style>
