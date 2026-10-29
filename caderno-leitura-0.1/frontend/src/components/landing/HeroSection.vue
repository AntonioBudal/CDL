<script setup lang="ts">
import { RouterLink } from 'vue-router'
import Icon from '../ui/Icon.vue'
</script>

<template>
  <section class="hero-editorial" aria-labelledby="hero-title">
    <h1 id="hero-title" class="hero-heading">Caderno de leitura e fichamento</h1>

    <p class="hero-lead">
      Organize seus livros por capítulo e escreva, para cada trecho, um resumo, uma explicação, os conceitos e as referências. Marque passagens, revise o que marcou e exporte tudo quando quiser.
    </p>

    <div class="hero-cta-group">
      <RouterLink to="/registro" class="btn-primary-cta">
        <span>Criar conta</span>
        <Icon name="arrow-right" :size="18" />
      </RouterLink>

      <a href="#exemplo" class="btn-secondary-cta">Ver um exemplo</a>
    </div>
  </section>
</template>

<style scoped>
.hero-editorial {
  padding-block: clamp(2rem, 6vw, 4.5rem) clamp(2.5rem, 5vw, 4rem);
  border-bottom: 1px solid var(--color-border-divider, var(--color-border));
}

.hero-heading {
  font-family: var(--font-reading, "Caderno EB Garamond", serif);
  font-size: clamp(2.1rem, 5vw, 3.5rem);
  font-weight: 600;
  line-height: 1.1;
  letter-spacing: -0.015em;
  max-width: 20ch;
  margin: 0 0 1.25rem 0;
  color: var(--color-text);
}

.hero-lead {
  font-size: clamp(1.05rem, 1.25vw, 1.2rem);
  line-height: 1.65;
  color: var(--color-text);
  max-width: 60ch;
  margin: 0 0 2rem 0;
}

.hero-cta-group {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.btn-primary-cta {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  min-height: 48px;
  height: auto;
  padding: 0.75rem 1.75rem;
  white-space: nowrap;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-on-accent, #ffffff);
  background-color: var(--color-accent);
  border-radius: var(--radius-md, 8px);
  text-decoration: none;
  min-width: 44px;
  transition: background-color 0.15s ease;
}

.btn-primary-cta:hover {
  background-color: var(--color-accent-hover, var(--color-accent));
  color: var(--color-accent-hover-text, var(--color-on-accent, #ffffff));
}

.btn-primary-cta:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 3px;
}

.btn-secondary-cta {
  display: inline-flex;
  align-items: center;
  font-size: 1rem;
  font-weight: 500;
  color: var(--color-text);
  text-decoration: underline;
  text-underline-offset: 4px;
  min-height: 44px;
  min-width: 44px;
  transition: color 0.15s ease;
}

.btn-secondary-cta:hover {
  color: var(--color-link);
}

.btn-secondary-cta:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

@media (max-width: 640px) {
  .hero-cta-group {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
  }

  .btn-secondary-cta {
    justify-content: center;
  }
}
</style>
