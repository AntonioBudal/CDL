<script setup lang="ts">
import { useVisitorTheme } from '../../composables/useVisitorTheme'
import ThemePreviewGrid from '../ThemePreviewGrid.vue'
import Icon from '../ui/Icon.vue'

const { activeTheme, statusMessage, applyTheme } = useVisitorTheme()
</script>

<template>
  <section id="temas" class="theme-showcase-section" aria-labelledby="themes-heading">
    <div class="showcase-container">
      <!-- Coluna Editorial Explicativa -->
      <div class="showcase-intro">
        <span class="showcase-eyebrow">Ateliê de Paletas</span>
        <h2 id="themes-heading" class="showcase-title">
          Dez atmosferas cromáticas para ler sem cansar os olhos.
        </h2>
        <p class="showcase-lead">
          A luz ambiente muda ao longo do dia; o caderno deve acompanhar. Do papel amarelado clássico ao contraste estrito do E-Ink monocromático, cada tema equilibra luminância e tipografia segundo as mais rigorosas diretrizes de acessibilidade visual.
        </p>

        <div class="theme-active-card">
          <div class="active-badge-row">
            <Icon name="sliders" :size="16" class="active-icon" />
            <span class="active-badge-label">Experimente agora</span>
          </div>
          <p class="active-instruction">
            Selecione qualquer amostra ao lado. A página inteira será repintada instantaneamente para que você sinta o conforto antes de qualquer cadastro.
          </p>

          <!-- Região acessível de feedback -->
          <div
            v-if="statusMessage"
            role="status"
            aria-live="polite"
            class="live-status-message"
          >
            <Icon name="check" :size="14" />
            <span>{{ statusMessage }}</span>
          </div>
        </div>
      </div>

      <!-- Coluna da Grade de Temas -->
      <div class="showcase-grid-column">
        <ThemePreviewGrid
          :model-value="activeTheme"
          @update:model-value="applyTheme"
        />
      </div>
    </div>
  </section>
</template>

<style scoped>
.theme-showcase-section {
  padding-block: clamp(4rem, 8vw, 7.5rem);
  background-color: var(--color-page);
  color: var(--color-text);
  border-bottom: 1px solid var(--color-border-divider, var(--color-border));
}

.showcase-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 clamp(1rem, 4vw, 3rem);
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: clamp(2rem, 4vw, 3.5rem);
  align-items: flex-start;
}

.showcase-intro {
  grid-column: 1 / 6;
  display: flex;
  flex-direction: column;
}

.showcase-eyebrow {
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--color-accent);
  display: block;
  margin-bottom: 0.75rem;
}

.showcase-title {
  font-family: var(--font-reading, "Caderno EB Garamond", serif);
  font-size: clamp(2rem, 3.5vw, 3rem);
  font-weight: 600;
  line-height: 1.15;
  letter-spacing: -0.015em;
  margin: 0 0 1.25rem 0;
  color: var(--color-text);
}

.showcase-lead {
  font-size: 1.05rem;
  line-height: 1.65;
  color: var(--color-text);
  margin: 0 0 2rem 0;
  opacity: 0.95;
}

.theme-active-card {
  padding: 1.25rem;
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md, 8px);
}

.active-badge-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.active-icon {
  color: var(--color-accent);
}

.active-badge-label {
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-accent);
}

.active-instruction {
  font-size: 0.925rem;
  line-height: 1.45;
  color: var(--color-text);
  margin: 0;
}

.live-status-message {
  margin-top: 0.85rem;
  padding: 0.5rem 0.75rem;
  background-color: var(--color-page);
  border: 1px solid var(--color-accent);
  border-radius: var(--radius-sm, 4px);
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-text);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* Coluna da Grade */
.showcase-grid-column {
  grid-column: 6 / 13;
}

@media (max-width: 900px) {
  .showcase-container {
    grid-template-columns: 1fr;
  }

  .showcase-intro {
    grid-column: 1 / -1;
  }

  .showcase-grid-column {
    grid-column: 1 / -1;
  }
}
</style>
