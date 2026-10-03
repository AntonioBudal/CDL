<script setup lang="ts">
import { RouterLink } from 'vue-router'
import Icon from '../components/ui/Icon.vue'
import { buildWebApplicationSchema, useSeoMeta } from '../composables/useSeoMeta'
import type { IconName } from '../types'

useSeoMeta({
  title: 'Leitorum — Caderno de Leitura e Estudos',
  description: 'Caderno pessoal de leitura e estudos em camadas. Metodologia de fichamento em 4 partes, privacidade total, zero anúncios e dados sob seu controle.',
  canonicalUrl: typeof window !== 'undefined' ? `${window.location.origin}/` : 'https://leitorum.com/',
  ogType: 'website',
  robots: 'index, follow',
  jsonLd: buildWebApplicationSchema(),
})

interface HighlightItem {
  icon: IconName
  title: string
  description: string
}

const highlights: HighlightItem[] = [
  {
    icon: 'book-open',
    title: 'Fichamento em 4 Dimensões',
    description: 'Resumos analíticos, explicações aprofundadas, conceitos-chave e referências bibliográficas organizados com rigor metodológico.',
  },
  {
    icon: 'network',
    title: 'Biblioteca em Camadas',
    description: 'Estruture livros, capítulos e múltiplos estudos. Acompanhe o status de maturação de cada nota desde o rascunho até a consolidação.',
  },
  {
    icon: 'shield',
    title: 'Privacidade e Soberania',
    description: 'Seus pensamentos e anotações pertencem a você. Sem anúncios, sem rastreadores ocultos e sem modelos de IA devorando seus textos.',
  },
  {
    icon: 'flame',
    title: 'Leitura Ativa & Marcações',
    description: 'Destaques coloridos, comentários marginais e conexões visuais entre conceitos de diferentes obras e autores.',
  },
]
</script>

<template>
  <div class="landing-page">
    <!-- Hero Section -->
    <header class="landing-hero">
      <div class="hero-badge">Caderno Pessoal de Leitura</div>
      <h1 class="hero-title">
        Transforme o ato de ler em conhecimento duradouro.
      </h1>
      <p class="hero-subtitle">
        O Leitorum é um ambiente calmo e estruturado para quem lê não apenas para passar o tempo, mas para estudar, compreender e reter ideias essenciais.
      </p>

      <div class="hero-cta-group">
        <RouterLink to="/registro" class="btn-hero-primary">
          <span>Criar Conta Gratuita</span>
          <Icon name="arrow-right" :size="18" />
        </RouterLink>
        <RouterLink to="/login" class="btn-hero-secondary">
          <span>Já possuo conta (Entrar)</span>
        </RouterLink>
      </div>
    </header>

    <!-- Highlights Grid -->
    <section class="highlights-section" aria-labelledby="highlights-heading">
      <h2 id="highlights-heading" class="visually-hidden">Destaques da Plataforma</h2>
      <div class="highlights-grid">
        <div v-for="item in highlights" :key="item.title" class="highlight-card">
          <div class="highlight-icon">
            <Icon :name="item.icon" :size="24" />
          </div>
          <h3 class="highlight-title">{{ item.title }}</h3>
          <p class="highlight-desc">{{ item.description }}</p>
        </div>
      </div>
    </section>

    <!-- Methodology Preview & Secondary CTA -->
    <section class="deep-dive-card">
      <div class="deep-dive-content">
        <h2>Metodologia Editorial Própria</h2>
        <p>
          Inspirado em séculos de prática leitora e nas melhores tradições acadêmicas de notas em margens e cadernos de lugares-comuns (<em>commonplace books</em>).
        </p>
        <div class="deep-dive-links">
          <RouterLink to="/sobre" class="text-link-arrow">
            <span>Conheça os detalhes da metodologia</span>
            <Icon name="arrow-right" :size="16" />
          </RouterLink>
        </div>
      </div>
    </section>

    <!-- Institutional Bottom Banner -->
    <section class="support-banner">
      <div class="banner-inner">
        <h3>Independente e Sustentado pela Comunidade</h3>
        <p>O Leitorum é software livre e não possui publicidade. Apoie o desenvolvimento continuado desta ferramenta de estudo.</p>
        <RouterLink to="/apoie" class="btn-support">Apoie o Leitorum</RouterLink>
      </div>
    </section>
  </div>
</template>

<style scoped>
.landing-page {
  max-width: 58rem;
  margin: 0 auto;
  padding: 2rem 1rem 4rem;
}

.landing-hero {
  text-align: center;
  padding: 2.5rem 0 3.5rem;
}

.hero-badge {
  display: inline-block;
  font-size: 0.8125rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: 0.35rem 0.9rem;
  border-radius: 9999px;
  background: var(--color-surface-soft, rgba(0, 0, 0, 0.04));
  border: 1px solid var(--color-border);
  color: var(--color-accent);
  margin-bottom: 1.5rem;
}

.hero-title {
  font-size: clamp(2.25rem, 5vw, 3.5rem);
  line-height: 1.12;
  letter-spacing: -0.04em;
  font-weight: 800;
  margin-bottom: 1.25rem;
}

.hero-subtitle {
  font-size: 1.1875rem;
  line-height: 1.6;
  color: var(--color-muted);
  max-width: 44rem;
  margin: 0 auto 2.5rem;
}

.hero-cta-group {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.btn-hero-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.85rem 1.75rem;
  background: var(--color-accent);
  color: var(--color-on-accent, #fff);
  border-radius: var(--radius-button, 8px);
  font-weight: 700;
  font-size: 1rem;
  text-decoration: none;
  transition: transform 0.15s ease, background-color 0.15s ease;
}

.btn-hero-primary:hover {
  background: var(--color-accent-hover);
  transform: translateY(-1px);
}

.btn-hero-secondary {
  display: inline-flex;
  align-items: center;
  padding: 0.85rem 1.5rem;
  background: var(--color-surface);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-button, 8px);
  font-weight: 650;
  font-size: 1rem;
  text-decoration: none;
  transition: background-color 0.15s ease, border-color 0.15s ease;
}

.btn-hero-secondary:hover {
  background: var(--color-surface-hover);
  border-color: var(--color-border-hover, var(--color-accent));
}

.highlights-section {
  margin-bottom: 3.5rem;
}

.highlights-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.25rem;
}

.highlight-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-panel, 12px);
  padding: 1.75rem;
  display: flex;
  flex-direction: column;
  transition: border-color 0.15s ease;
}

.highlight-card:hover {
  border-color: var(--color-accent);
}

.highlight-icon {
  color: var(--color-accent);
  margin-bottom: 1rem;
}

.highlight-title {
  font-size: 1.2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.highlight-desc {
  font-size: 0.9375rem;
  color: var(--color-muted);
  line-height: 1.55;
  margin: 0;
}

.deep-dive-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-panel, 12px);
  padding: 2.25rem 2rem;
  margin-bottom: 3rem;
}

.deep-dive-content h2 {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.deep-dive-content p {
  color: var(--color-muted);
  font-size: 1.0625rem;
  line-height: 1.5;
  margin: 0 0 1.25rem;
}

.text-link-arrow {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  color: var(--color-accent);
  font-weight: 650;
  text-decoration: none;
}

.text-link-arrow:hover {
  text-decoration: underline;
}

.support-banner {
  background: var(--color-surface-soft, rgba(0, 0, 0, 0.03));
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-panel, 12px);
  padding: 2rem;
  text-align: center;
}

.banner-inner h3 {
  font-size: 1.25rem;
  margin-bottom: 0.5rem;
}

.banner-inner p {
  color: var(--color-muted);
  font-size: 0.9375rem;
  max-width: 36rem;
  margin: 0 auto 1.25rem;
}

.btn-support {
  display: inline-block;
  padding: 0.6rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 650;
  text-decoration: none;
  background: var(--color-surface);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-button, 8px);
  transition: all 0.15s ease;
}

.btn-support:hover {
  background: var(--color-surface-hover);
  border-color: var(--color-accent);
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
</style>
