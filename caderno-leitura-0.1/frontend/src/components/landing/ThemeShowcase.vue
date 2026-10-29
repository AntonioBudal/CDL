<script setup lang="ts">
import { useVisitorTheme } from '../../composables/useVisitorTheme'
import ThemePreviewGrid from '../ThemePreviewGrid.vue'

const { activeTheme, statusMessage, applyTheme } = useVisitorTheme()
</script>

<template>
  <section id="temas" class="theme-showcase-section" aria-labelledby="themes-heading">
    <div class="showcase-intro">
      <h2 id="themes-heading" class="showcase-title">Temas</h2>
      <p class="showcase-lead">
        Há dez temas de cor, claros e escuros, e a fonte de leitura também pode ser trocada nos ajustes. Escolha um tema abaixo para ver esta página com ele.
      </p>
      <p
        v-if="statusMessage"
        role="status"
        aria-live="polite"
        class="live-status-message"
      >
        {{ statusMessage }}
      </p>
    </div>

    <ThemePreviewGrid
      :model-value="activeTheme"
      @update:model-value="applyTheme"
    />
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
  font-size: clamp(1.5rem, 2.5vw, 1.9rem);
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

.live-status-message {
  margin: 0.75rem 0 0 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--color-text);
}
</style>
