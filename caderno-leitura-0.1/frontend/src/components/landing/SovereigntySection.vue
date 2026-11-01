<script setup lang="ts">
import Icon from '../ui/Icon.vue'
import { vReveal } from '../../composables/useReveal'
import type { IconName } from '../../types'

interface DataFact {
  title: string
  description: string
  icon: IconName
  tags: string[]
}

// Afirmações conferidas no código: export_service (Markdown, texto e .zip da conta), ausência de scripts de
// análise no frontend e de clientes de IA no backend; as únicas saídas de rede são google_auth_service e
// cover_service (e o script de login do Google no navegador, quando o login com Google está ativado).
const facts: DataFact[] = [
  {
    title: 'Onde ficam',
    description: 'No servidor em que este Leitorum está instalado.',
    icon: 'folder',
    tags: ['SQLite'],
  },
  {
    title: 'Exportação',
    description: 'Livro ou estudo em Markdown ou texto; a conta inteira em um .zip.',
    icon: 'download',
    tags: ['Markdown', 'JSON', '.zip'],
  },
  {
    title: 'Sem anúncios',
    description: 'Sem ferramentas de análise de terceiros e sem envio de textos a serviços de IA.',
    icon: 'shield',
    tags: ['Sem análise de uso'],
  },
  {
    title: 'Conexões externas',
    description: 'Só no login com Google, se ativado, e ao buscar uma capa por endereço.',
    icon: 'globe',
    tags: ['Opcional'],
  },
]
</script>

<template>
  <section id="dados" class="sovereignty-section" aria-labelledby="data-heading">
    <h2 v-reveal id="data-heading" class="section-title">Seus dados</h2>

    <ul class="facts-grid">
      <li v-for="(fact, idx) in facts" :key="fact.title" v-reveal="idx * 80" class="fact-card">
        <span class="fact-icon" aria-hidden="true"><Icon :name="fact.icon" :size="20" /></span>
        <h3 class="fact-title">{{ fact.title }}</h3>
        <p class="fact-desc">{{ fact.description }}</p>
        <ul class="tags" aria-label="Formatos e características">
          <li v-for="tag in fact.tags" :key="tag" class="tag">{{ tag }}</li>
        </ul>
      </li>
    </ul>

    <a
      v-reveal="320"
      class="source-card"
      href="https://github.com/AntonioBudal/CDL"
      target="_blank"
      rel="noopener noreferrer"
    >
      <span class="fact-icon" aria-hidden="true">
        <svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true">
          <path
            fill="currentColor"
            d="M12 .5a12 12 0 0 0-3.8 23.4c.6.1.8-.3.8-.6v-2c-3.3.7-4-1.6-4-1.6-.6-1.4-1.4-1.8-1.4-1.8-1-.7.1-.7.1-.7 1.2.1 1.8 1.2 1.8 1.2 1 1.8 2.8 1.3 3.5 1 .1-.8.4-1.3.7-1.6-2.7-.3-5.5-1.3-5.5-6 0-1.2.5-2.3 1.2-3.1-.1-.4-.5-1.6.1-3.2 0 0 1-.3 3.3 1.2a11.5 11.5 0 0 1 6 0C17.3 4.7 18.3 5 18.3 5c.7 1.6.2 2.8.1 3.2.8.8 1.2 1.9 1.2 3.1 0 4.7-2.8 5.7-5.5 6 .4.4.8 1.1.8 2.2v3.3c0 .3.2.7.8.6A12 12 0 0 0 12 .5Z"
          />
        </svg>
      </span>
      <span class="source-label">
        <strong>Código-fonte no GitHub</strong>
        <span>Repositório público AntonioBudal/CDL</span>
      </span>
      <Icon name="external-link" :size="18" class="source-arrow" />
    </a>
  </section>
</template>

<style scoped>
.sovereignty-section {
  padding-block: clamp(2.5rem, 6vw, 4.5rem);
}

.section-title {
  font-family: var(--font-reading, "Caderno EB Garamond", serif);
  font-size: clamp(1.75rem, 3vw, 2.4rem);
  font-weight: 600;
  line-height: 1.2;
  margin: 0 0 1.75rem 0;
  color: var(--color-text);
}

.facts-grid {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 15rem), 1fr));
  gap: 1rem;
}

.fact-card {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 1.25rem;
  min-width: 0;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 14px;
  transition: border-color 0.25s ease, transform 0.25s ease;
}

.fact-card:hover {
  border-color: var(--color-accent);
  transform: translateY(-2px);
}

.fact-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  flex-shrink: 0;
  border-radius: 10px;
  color: var(--color-link);
  background: color-mix(in srgb, var(--color-accent) 12%, transparent);
  border: 1px solid color-mix(in srgb, var(--color-accent) 28%, transparent);
}

.fact-title {
  margin: 0.25rem 0 0;
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--color-text);
}

.fact-desc {
  margin: 0;
  font-size: 0.95rem;
  line-height: 1.5;
  color: var(--color-text);
}

.tags {
  list-style: none;
  margin: auto 0 0;
  padding: 0.5rem 0 0;
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.tag {
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  color: var(--color-text);
  background: var(--color-page);
  border: 1px solid var(--color-border);
  font-family: var(--font-mono, ui-monospace, monospace);
}

.source-card {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  margin-top: 1rem;
  padding: 1rem 1.25rem;
  min-height: 44px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 14px;
  color: var(--color-text);
  text-decoration: none;
  transition: border-color 0.25s ease, box-shadow 0.25s ease;
}

.source-card:hover {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--color-accent) 30%, transparent);
}

.source-card:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

.source-label {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
  font-size: 0.9rem;
}

.source-label strong {
  font-size: 1rem;
}

.source-arrow {
  color: var(--color-link);
  transition: transform 0.25s ease;
}

.source-card:hover .source-arrow {
  transform: translate(2px, -2px);
}

@media (prefers-reduced-motion: reduce) {
  .fact-card,
  .fact-card:hover,
  .source-card:hover .source-arrow {
    transition: none;
    transform: none;
  }
}
</style>
