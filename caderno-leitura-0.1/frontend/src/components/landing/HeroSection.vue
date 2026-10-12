<script setup lang="ts">
import { RouterLink } from 'vue-router'
import Icon from '../ui/Icon.vue'
</script>

<template>
  <section id="conteudo-principal" class="hero-editorial" aria-labelledby="hero-title">
    <div class="hero-container">
      <!-- Coluna Editorial (Manifesto e Chamadas) -->
      <div class="hero-content">
        <div class="hero-eyebrow">
          Caderno de leitura e estudo em camadas
        </div>

        <h1 id="hero-title" class="hero-heading">
          Ler devagar é uma forma de pensar.
        </h1>

        <p class="hero-lead">
          O Leitorum é um ambiente calmo para quem estuda obras fundamentais. Em vez de acumular páginas lidas às pressas, pratique o fichamento em quatro camadas cognitivas: resuma a essência, explique os mecanismos, isole conceitos e teça conexões duradouras.
        </p>

        <div class="hero-cta-group">
          <RouterLink to="/registro" class="btn-primary-cta">
            <span>Criar Conta Gratuita</span>
            <Icon name="arrow-right" :size="18" />
          </RouterLink>

          <RouterLink to="/login" class="btn-secondary-cta">
            Já possuo conta (Entrar)
          </RouterLink>
        </div>
      </div>

      <!-- Coluna da Ficha de Leitura (Cartão Conceitual) -->
      <aside class="hero-card-column" aria-label="Ficha de leitura conceitual">
        <div class="reading-index-card">
          <div class="index-card-header">
            <span class="index-card-tag">Ficha de Leitura</span>
            <span class="index-card-ref">Método em 4 Dimensões</span>
          </div>

          <div class="index-card-quote">
            «Ler sem refletir é como comer sem digerir.»
            <cite class="quote-author">— Edmund Burke</cite>
          </div>

          <hr class="index-card-divider" />

          <ul class="method-preview-list">
            <li class="method-preview-item">
              <span class="dim-badge dim-1">1</span>
              <div class="dim-text">
                <strong>Resumo analítico</strong>
                <p>O que a obra diz em essência?</p>
              </div>
            </li>
            <li class="method-preview-item">
              <span class="dim-badge dim-2">2</span>
              <div class="dim-text">
                <strong>Explicação aprofundada</strong>
                <p>Como e por que o autor sustenta a tese?</p>
              </div>
            </li>
            <li class="method-preview-item">
              <span class="dim-badge dim-3">3</span>
              <div class="dim-text">
                <strong>Conceitos-chave</strong>
                <p>Quais categorias foram formuladas?</p>
              </div>
            </li>
            <li class="method-preview-item">
              <span class="dim-badge dim-4">4</span>
              <div class="dim-text">
                <strong>Referências e conexões</strong>
                <p>Com quais tradições o texto dialoga?</p>
              </div>
            </li>
          </ul>
        </div>
      </aside>
    </div>
  </section>
</template>

<style scoped>
.hero-editorial {
  padding-block: clamp(3.5rem, 8vw, 7.5rem) clamp(3rem, 6vw, 6rem);
  background-color: var(--color-page);
  color: var(--color-text);
  border-bottom: 1px solid var(--color-border-divider, var(--color-border));
}

.hero-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 clamp(1rem, 4vw, 3rem);
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 2rem;
  align-items: center;
}

.hero-content {
  grid-column: 1 / 8;
  display: flex;
  flex-direction: column;
}

.hero-eyebrow {
  font-size: 0.875rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--color-accent);
  margin-bottom: 1rem;
}

.hero-heading {
  font-family: var(--font-reading, "Caderno EB Garamond", serif);
  font-size: clamp(2.5rem, 5vw, 4.25rem);
  font-weight: 600;
  line-height: 1.1;
  letter-spacing: -0.02em;
  margin: 0 0 1.5rem 0;
  color: var(--color-text);
}

.hero-lead {
  font-size: clamp(1.05rem, 1.25vw, 1.25rem);
  line-height: 1.65;
  color: var(--color-text);
  max-width: 52ch;
  margin: 0 0 2.25rem 0;
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
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.btn-primary-cta:hover {
  opacity: 0.92;
  transform: translateY(-1px);
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
  color: var(--color-accent);
}

.btn-secondary-cta:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

/* Coluna Lateral da Ficha de Leitura */
.hero-card-column {
  grid-column: 8 / 13;
  display: flex;
  justify-content: flex-end;
}

.reading-index-card {
  width: 100%;
  max-width: 420px;
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg, 12px);
  padding: 1.75rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
}

.index-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.index-card-tag {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: 0.2rem 0.5rem;
  border-radius: var(--radius-sm, 4px);
  background-color: var(--color-surface-hover, rgba(0, 0, 0, 0.05));
  color: var(--color-accent);
}

.index-card-ref {
  font-size: 0.8rem;
  color: var(--color-text);
  opacity: 0.8;
}

.index-card-quote {
  font-family: var(--font-reading, "Caderno EB Garamond", serif);
  font-size: 1.15rem;
  font-style: italic;
  line-height: 1.45;
  color: var(--color-text);
  margin-bottom: 1rem;
}

.quote-author {
  display: block;
  font-size: 0.85rem;
  font-style: normal;
  font-family: inherit;
  margin-top: 0.35rem;
  opacity: 0.75;
}

.index-card-divider {
  border: 0;
  border-top: 1px solid var(--color-border);
  margin-bottom: 1.25rem;
}

.method-preview-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.875rem;
}

.method-preview-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}

.dim-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  font-size: 0.75rem;
  font-weight: 700;
  background-color: var(--color-accent);
  color: var(--color-on-accent, #ffffff);
  flex-shrink: 0;
  margin-top: 2px;
}

.dim-text strong {
  display: block;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--color-text);
  line-height: 1.3;
}

.dim-text p {
  font-size: 0.825rem;
  color: var(--color-text);
  opacity: 0.85;
  margin: 0.1rem 0 0 0;
  line-height: 1.35;
}

@media (max-width: 1024px) {
  .hero-content {
    grid-column: 1 / 8;
  }

  .hero-card-column {
    grid-column: 8 / 13;
  }
}

@media (max-width: 840px) {
  .hero-container {
    grid-template-columns: 1fr;
    gap: 3rem;
  }

  .hero-content {
    grid-column: 1 / -1;
  }

  .hero-card-column {
    grid-column: 1 / -1;
    justify-content: stretch;
  }

  .reading-index-card {
    max-width: 100%;
  }

  .hero-cta-group {
    flex-direction: column;
    align-items: stretch;
  }

  .btn-primary-cta {
    width: 100%;
  }

  .btn-secondary-cta {
    justify-content: center;
  }
}
</style>
