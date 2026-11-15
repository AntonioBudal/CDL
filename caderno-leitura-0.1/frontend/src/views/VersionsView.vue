<script setup lang="ts">
import { uiLocale } from '../i18n/format.ts'
/**
 * F0.12.01 (spec 114): "Evolução das versões" — tela escondida (sem menu; só um botão no fim do Sobre), pública como
 * o Sobre e fora dos buscadores. Conteúdo do projeto, nunca do acervo.
 */
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { VERSION_HISTORY, type RoadmapEntry } from '../data/versionHistory'
import { appVersion, parseSemver, roadmapOf } from '../utils/appVersion'

const current = appVersion()
const semver = parseSemver(current)
const currentRoadmap = roadmapOf(current)
const stage = computed(() => {
  const pre = semver?.prerelease ?? ''
  const match = /^alpha\.(\d+)$/.exec(pre)
  return match ? Number(match[1]) : null
})

function formatDate(iso: string): string {
  const [y, m, d] = iso.split('-').map(Number)
  return new Date(y!, (m ?? 1) - 1, d ?? 1).toLocaleDateString(uiLocale(), { day: 'numeric', month: 'short', year: 'numeric' })
}

function period(entry: RoadmapEntry): string {
  if (entry.status === 'in_progress') return `desde ${formatDate(entry.started)}`
  if (entry.closed) return `${formatDate(entry.started)} a ${formatDate(entry.closed)}`
  return `iniciado em ${formatDate(entry.started)}`
}

function featuresLabel(entry: RoadmapEntry): string {
  if (entry.featureCount === null) return ''
  if (entry.status === 'in_progress' && entry.features) {
    const done = entry.features.filter((f) => f.done).length
    return `${done} de ${entry.featureCount} features entregues`
  }
  return `${entry.featureCount} features`
}
</script>

<template>
  <section class="versions-view wrap" aria-labelledby="versions-heading">
    <RouterLink to="/sobre" class="versions-back">← Sobre o Leitorum</RouterLink>
    <header class="page-header">
      <p class="eyebrow">Bastidores</p>
      <h1 id="versions-heading">Evolução das versões</h1>
      <p class="versions-lead">
        Versão atual: <strong>v{{ current }}</strong>.
      </p>
      <p class="versions-muted">
        A numeração segue o <strong>Versionamento Semântico</strong>. O <code>0.</code> na frente diz que o Leitorum
        ainda não chegou à 1.0: ele ainda muda bastante de uma versão para outra. O segundo número
        (<code>{{ currentRoadmap || '0.12' }}</code>) é o roadmap, um conjunto de features planejadas juntas.
        <template v-if="stage !== null">
          O final <code>alpha.{{ stage }}</code> conta quantas features desse roadmap já foram entregues; quando todas
          estiverem prontas e testadas, a versão vira <code>{{ currentRoadmap }}.0</code>.
        </template>
      </p>
    </header>

    <ol class="versions-timeline">
      <li v-for="entry in VERSION_HISTORY" :key="entry.roadmap">
        <article class="versions-entry" :class="{ 'is-current': entry.status === 'in_progress' }" :aria-labelledby="`v-${entry.roadmap}`">
          <header class="versions-entry-head">
            <h2 :id="`v-${entry.roadmap}`" class="versions-entry-title">
              <span class="versions-number">{{ entry.version }}</span>
              <span>{{ entry.title }}</span>
            </h2>
            <span class="versions-status">{{ entry.status === 'in_progress' ? 'Em andamento' : 'Fechado' }}</span>
          </header>
          <p class="versions-muted">
            {{ period(entry) }}<template v-if="featuresLabel(entry)"> · {{ featuresLabel(entry) }}</template>
          </p>
          <ul class="versions-highlights">
            <li v-for="item in entry.highlights" :key="item">{{ item }}</li>
          </ul>
          <ul v-if="entry.features" class="versions-features" aria-label="Features deste roadmap">
            <li v-for="feature in entry.features" :key="feature.id" :class="{ done: feature.done }">
              <span class="versions-feature-mark">{{ feature.done ? 'Entregue' : 'A fazer' }}</span>
              <span>{{ feature.id }} · {{ feature.title }}</span>
            </li>
          </ul>
        </article>
      </li>
    </ol>
  </section>
</template>

<style scoped>
.versions-view {
  max-width: 48rem;
  margin: 0 auto;
  padding-block: 1.5rem 3rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-width: 0;
}
.versions-back {
  color: var(--color-link);
  display: inline-flex;
  align-items: center;
  min-height: 44px;
  align-self: flex-start;
}
.versions-lead {
  font-size: 1.05rem;
  margin: 0.25rem 0;
}
.versions-muted {
  color: var(--color-muted);
  margin: 0.25rem 0;
}
.versions-timeline {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.75rem;
  border-left: 2px solid var(--color-border);
}
.versions-entry {
  margin-left: 1rem;
  padding: 0.75rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--color-surface);
  color: var(--color-text);
  min-width: 0;
  overflow-wrap: anywhere;
}
.versions-entry.is-current {
  border-color: var(--color-border-strong);
}
.versions-entry-head {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.25rem 0.75rem;
}
.versions-entry-title {
  margin: 0;
  font-size: 1.05rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem 0.6rem;
}
.versions-number {
  font-variant-numeric: tabular-nums;
}
.versions-status {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0 0.6rem;
  border-radius: 999px;
  background: var(--color-selected-bg);
  color: var(--color-selected-text);
}
.versions-highlights {
  margin: 0.4rem 0 0;
  padding-left: 1.2rem;
}
.versions-features {
  list-style: none;
  margin: 0.6rem 0 0;
  padding: 0;
  display: grid;
  gap: 0.25rem;
  font-size: 0.92rem;
}
.versions-features li {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem 0.5rem;
}
.versions-feature-mark {
  font-weight: 600;
  color: var(--color-muted);
  min-width: 5.5rem;
}
.versions-features li.done .versions-feature-mark {
  color: var(--color-text);
}
</style>
