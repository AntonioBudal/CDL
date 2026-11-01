<script setup lang="ts">
import { computed, nextTick, ref } from 'vue'
import { useVisitorTheme } from '../../composables/useVisitorTheme'
import { vReveal } from '../../composables/useReveal'
import { CANONICAL_THEME_PREVIEWS } from '../../types/settings'
import type { CanonicalThemeId } from '../../types/settings'
import Icon from '../ui/Icon.vue'

const { activeTheme, statusMessage, applyTheme } = useVisitorTheme()

const themes = CANONICAL_THEME_PREVIEWS
const itemRefs = ref<HTMLElement[]>([])

const activeIndex = computed(() => Math.max(0, themes.findIndex((t) => t.id === activeTheme.value)))
const preview = computed(() => themes[activeIndex.value])

// As cores da prévia vêm do catálogo do tema; a transição de cor faz a troca parecer contínua.
const previewStyle = computed(() => ({
  '--p-page': preview.value.colors.page,
  '--p-surface': preview.value.colors.surface,
  '--p-text': preview.value.colors.text,
  '--p-accent': preview.value.colors.accent,
  '--p-border': preview.value.colors.border,
}))

function select(id: CanonicalThemeId, index: number) {
  applyTheme(id)
  nextTick(() => itemRefs.value[index]?.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' }))
}

function step(delta: number) {
  const index = (activeIndex.value + delta + themes.length) % themes.length
  select(themes[index].id, index)
}
</script>

<template>
  <section id="temas" class="theme-showcase-section" aria-labelledby="themes-heading">
    <div v-reveal class="showcase-intro">
      <h2 id="themes-heading" class="showcase-title">Temas</h2>
      <p class="showcase-lead">
        Dez temas, claros e escuros, e fonte de leitura ajustável. Escolha um para ver esta página com ele.
      </p>
    </div>

    <div v-reveal="100" class="showcase-body">
      <div class="preview-frame" :style="previewStyle" aria-hidden="true">
        <div class="preview-bar">
          <span class="preview-brand">Leitorum</span>
          <span class="preview-btn">Criar conta</span>
        </div>
        <div class="preview-content">
          <div class="preview-card">
            <span class="preview-kicker">Resumo</span>
            <span class="preview-line w90"></span>
            <span class="preview-line w75"></span>
            <span class="preview-line w60"></span>
          </div>
          <div class="preview-swatches">
            <span v-for="(color, key) in preview.colors" :key="key" class="swatch" :style="{ background: color }"></span>
          </div>
        </div>
        <span class="preview-name">{{ preview.label }}</span>
      </div>

      <div class="rail-wrap">
        <button type="button" class="rail-nav" aria-label="Tema anterior" @click="step(-1)">
          <Icon name="chevron-left" :size="18" />
        </button>

        <ul class="rail" aria-label="Temas disponíveis">
          <li v-for="(theme, idx) in themes" :key="theme.id">
            <button
              :ref="(el) => { if (el) itemRefs[idx] = el as HTMLElement }"
              type="button"
              class="theme-chip"
              :class="{ 'is-active': theme.id === activeTheme }"
              :aria-pressed="theme.id === activeTheme"
              @click="select(theme.id, idx)"
            >
              <span class="chip-swatch" :style="{ background: theme.colors.page, borderColor: theme.colors.border }" aria-hidden="true">
                <span :style="{ background: theme.colors.accent }"></span>
                <span :style="{ background: theme.colors.text }"></span>
              </span>
              <span class="chip-label">{{ theme.label }}</span>
            </button>
          </li>
        </ul>

        <button type="button" class="rail-nav" aria-label="Próximo tema" @click="step(1)">
          <Icon name="chevron-right" :size="18" />
        </button>
      </div>

      <p v-if="statusMessage" role="status" aria-live="polite" class="live-status-message">
        {{ statusMessage }}
      </p>
    </div>
  </section>
</template>

<style scoped>
.theme-showcase-section {
  padding-block: clamp(2.5rem, 6vw, 4.5rem);
  border-bottom: 1px solid var(--color-border-divider, var(--color-border));
}

.showcase-intro {
  max-width: 68ch;
  margin-bottom: 1.5rem;
}

.showcase-title {
  font-family: var(--font-reading, "Caderno EB Garamond", serif);
  font-size: clamp(1.75rem, 3vw, 2.4rem);
  font-weight: 600;
  line-height: 1.2;
  margin: 0 0 0.75rem 0;
  color: var(--color-text);
}

.showcase-lead {
  font-size: 1rem;
  line-height: 1.6;
  color: var(--color-text);
  margin: 0;
}

.showcase-body {
  display: grid;
  gap: 1.25rem;
  min-width: 0;
}

/* Prévia */
.preview-frame {
  position: relative;
  background: var(--p-page);
  border: 1px solid var(--p-border);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 24px 48px -28px rgba(0, 0, 0, 0.45);
  transition: background-color 0.5s ease, border-color 0.5s ease;
}

.preview-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: var(--p-surface);
  border-bottom: 1px solid var(--p-border);
  transition: background-color 0.5s ease, border-color 0.5s ease;
}

.preview-brand {
  font-family: var(--font-reading, "Caderno EB Garamond", serif);
  font-weight: 700;
  color: var(--p-text);
  transition: color 0.5s ease;
}

.preview-btn {
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.3rem 0.7rem;
  border-radius: 6px;
  background: var(--p-accent);
  color: var(--p-page);
  transition: background-color 0.5s ease, color 0.5s ease;
}

.preview-content {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 1rem;
  align-items: center;
  padding: 1.25rem 1rem 2.5rem;
}

.preview-card {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 1rem;
  background: var(--p-surface);
  border: 1px solid var(--p-border);
  border-radius: 10px;
  transition: background-color 0.5s ease, border-color 0.5s ease;
}

.preview-kicker {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--p-accent);
  transition: color 0.5s ease;
}

.preview-line {
  height: 8px;
  border-radius: 4px;
  background: var(--p-text);
  opacity: 0.55;
  transition: background-color 0.5s ease;
}

.w90 { width: 90%; }
.w75 { width: 75%; }
.w60 { width: 60%; }

.preview-swatches {
  display: grid;
  grid-template-columns: repeat(5, 22px);
  gap: 6px;
}

.swatch {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 1px solid var(--p-border);
  transition: background-color 0.5s ease;
}

.preview-name {
  position: absolute;
  right: 1rem;
  bottom: 0.75rem;
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--p-text);
  transition: color 0.5s ease;
}

/* Trilho */
.rail-wrap {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 0;
}

.rail {
  list-style: none;
  margin: 0;
  padding: 0.35rem 0.15rem;
  display: flex;
  gap: 0.6rem;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  scrollbar-width: thin;
  flex: 1;
  min-width: 0;
}

.rail li {
  scroll-snap-align: center;
  flex-shrink: 0;
}

.theme-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
  min-height: 44px;
  padding: 0.4rem 0.85rem 0.4rem 0.4rem;
  border-radius: 999px;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text);
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: border-color 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
}

.theme-chip:hover {
  background: var(--color-surface-hover, var(--color-surface));
  color: var(--color-hover-text, var(--color-text));
  transform: translateY(-2px);
}

.theme-chip.is-active {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--color-accent) 35%, transparent);
}

.theme-chip:focus-visible,
.rail-nav:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

.chip-swatch {
  position: relative;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  border: 1px solid;
  overflow: hidden;
  flex-shrink: 0;
}

.chip-swatch span {
  position: absolute;
  width: 50%;
  height: 50%;
  bottom: 0;
}

.chip-swatch span:first-child { left: 0; }
.chip-swatch span:last-child { right: 0; }

.rail-nav {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  flex-shrink: 0;
  border-radius: 50%;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text);
  cursor: pointer;
}

.rail-nav:hover {
  background: var(--color-surface-hover, var(--color-surface));
  color: var(--color-hover-text, var(--color-text));
}

.live-status-message {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--color-text);
}

@media (max-width: 480px) {
  .rail-nav {
    display: none;
  }

  .preview-content {
    grid-template-columns: 1fr;
  }
}

@media (prefers-reduced-motion: reduce) {
  .preview-frame,
  .preview-frame *,
  .theme-chip {
    transition: none;
  }

  .theme-chip:hover {
    transform: none;
  }
}

/* Neutraliza o estilo global de <button> (destaque como fundo) nos controles da vitrine. */
.showcase-body .rail-wrap .rail-nav.rail-nav,
.showcase-body .rail-wrap .theme-chip.theme-chip {
  --button-bg: var(--color-surface);
  --button-fg: var(--color-text);
  --button-border: var(--color-border);
  --button-hover-bg: var(--color-surface-hover, var(--color-surface));
  --button-hover-fg: var(--color-hover-text, var(--color-text));
  box-shadow: none;
  min-height: 44px;
  width: auto;
}

.showcase-body .rail-wrap .rail-nav.rail-nav {
  width: 44px;
  padding: 0;
  border-radius: 50%;
}

.showcase-body .rail-wrap .theme-chip.theme-chip {
  border-radius: 999px;
  padding: 0.4rem 0.85rem 0.4rem 0.4rem;
}

.showcase-body .rail-wrap .theme-chip.theme-chip.is-active {
  --button-border: var(--color-accent);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--color-accent) 35%, transparent);
}
</style>
