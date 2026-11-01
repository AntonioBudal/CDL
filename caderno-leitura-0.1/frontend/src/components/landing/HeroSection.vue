<script setup lang="ts">
import { RouterLink } from 'vue-router'
import Icon from '../ui/Icon.vue'
import HeroShowcase from './HeroShowcase.vue'
</script>

<template>
  <section class="hero-editorial" aria-labelledby="hero-title">
    <div class="hero-bg" aria-hidden="true"></div>

    <div class="hero-grid">
      <div class="hero-content">
        <p class="hero-badge">
          <span class="badge-dot" aria-hidden="true"></span>
          Código-fonte público · Sem anúncios
        </p>

        <h1 id="hero-title" class="hero-heading">
          <span class="brand-word">Leitorum</span>: seu caderno de leitura e fichamento
        </h1>

        <p class="hero-lead">
          Estude livros por capítulo com resumo, explicação, conceitos e referências. Marque trechos, revise e exporte quando quiser.
        </p>

        <div class="hero-cta-group">
          <RouterLink to="/registro" class="btn-primary-cta">
            <span>Criar conta</span>
            <Icon name="arrow-right" :size="18" class="cta-arrow" />
          </RouterLink>

          <a href="#exemplo" class="btn-secondary-cta">
            <Icon name="book-open" :size="18" class="cta-book" />
            <span>Ver um exemplo</span>
          </a>
        </div>
      </div>

      <HeroShowcase class="hero-showcase" />
    </div>
  </section>
</template>

<style scoped>
.hero-editorial {
  position: relative;
  isolation: isolate;
  padding-block: clamp(2rem, 6vw, 4.5rem) clamp(2.5rem, 5vw, 4rem);
  border-bottom: 1px solid var(--color-border-divider, var(--color-border));
}

/* Brilho de fundo discreto, derivado das cores do tema ativo. */
.hero-bg {
  position: absolute;
  inset: 0;
  z-index: -1;
  background:
    radial-gradient(60% 55% at 12% 20%, color-mix(in srgb, var(--color-accent) 14%, transparent), transparent 70%),
    radial-gradient(45% 50% at 88% 40%, color-mix(in srgb, var(--color-link) 12%, transparent), transparent 70%);
  pointer-events: none;
}

.hero-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(0, 1fr);
  gap: clamp(2rem, 5vw, 4rem);
  align-items: center;
}

.hero-content {
  min-width: 0;
  animation: hero-in 0.7s ease both;
}

@keyframes hero-in {
  from { opacity: 0; transform: translateY(18px); }
  to { opacity: 1; transform: none; }
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 0 1.25rem 0;
  padding: 0.35rem 0.8rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-text);
  background: color-mix(in srgb, var(--color-surface) 80%, transparent);
  border: 1px solid var(--color-border);
  border-radius: 999px;
}

.badge-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-accent);
  box-shadow: 0 0 0 0 color-mix(in srgb, var(--color-accent) 60%, transparent);
  animation: pulse 2.4s ease-out infinite;
}

@keyframes pulse {
  to { box-shadow: 0 0 0 8px transparent; }
}

.hero-heading {
  font-family: var(--font-reading, "Caderno EB Garamond", serif);
  font-size: clamp(2.2rem, 5vw, 3.6rem);
  font-weight: 600;
  line-height: 1.08;
  letter-spacing: -0.015em;
  margin: 0 0 1.25rem 0;
  color: var(--color-text);
}

.brand-word {
  color: var(--color-link);
}

.hero-lead {
  font-size: clamp(1.05rem, 1.25vw, 1.2rem);
  line-height: 1.6;
  color: var(--color-text);
  max-width: 52ch;
  margin: 0 0 2rem 0;
}

.hero-cta-group {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.btn-primary-cta,
.btn-secondary-cta {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  min-height: 48px;
  height: auto;
  padding: 0.75rem 1.6rem;
  white-space: nowrap;
  font-size: 1rem;
  font-weight: 600;
  border-radius: var(--radius-md, 8px);
  text-decoration: none;
  min-width: 44px;
  transition: transform 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease, border-color 0.2s ease;
}

.btn-primary-cta {
  color: var(--color-on-accent, #ffffff);
  background-color: var(--color-accent);
  box-shadow: 0 8px 22px -10px color-mix(in srgb, var(--color-accent) 80%, transparent);
}

.btn-primary-cta:hover {
  background-color: var(--color-accent-hover, var(--color-accent));
  color: var(--color-accent-hover-text, var(--color-on-accent, #ffffff));
  transform: translateY(-2px);
  box-shadow: 0 14px 28px -12px color-mix(in srgb, var(--color-accent) 90%, transparent);
}

.btn-secondary-cta {
  color: var(--color-text);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
}

.btn-secondary-cta:hover {
  border-color: var(--color-accent);
  transform: translateY(-2px);
}

.cta-arrow,
.cta-book {
  transition: transform 0.25s ease;
}

.btn-primary-cta:hover .cta-arrow {
  transform: translateX(4px);
}

.btn-secondary-cta:hover .cta-book {
  transform: rotate(-8deg) scale(1.1);
}

.btn-primary-cta:focus-visible,
.btn-secondary-cta:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 3px;
}

.hero-showcase {
  min-width: 0;
}

@media (max-width: 900px) {
  .hero-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .hero-cta-group {
    flex-direction: column;
    align-items: stretch;
  }
}

@media (prefers-reduced-motion: reduce) {
  .hero-content,
  .badge-dot {
    animation: none;
  }

  .btn-primary-cta:hover,
  .btn-secondary-cta:hover,
  .btn-primary-cta:hover .cta-arrow,
  .btn-secondary-cta:hover .cta-book {
    transform: none;
  }
}
</style>
