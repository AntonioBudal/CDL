<script setup lang="ts">
import { RouterLink } from 'vue-router'
import Icon from '../components/ui/Icon.vue'
import { buildWebApplicationSchema, useSeoMeta } from '../composables/useSeoMeta'
import type { IconName } from '../types'

useSeoMeta({
  title: 'Sobre o Leitorum',
  description: 'Conheça o Leitorum: caderno pessoal de leitura em camadas, metodologia de estudos em 4 partes, privacidade total e zero anúncios.',
  canonicalUrl: typeof window !== 'undefined' ? `${window.location.origin}/sobre` : 'https://leitorum.com/sobre',
  ogType: 'website',
  robots: 'index, follow',
  jsonLd: buildWebApplicationSchema(),
})

interface StudyPillar {
  step: string
  title: string
  icon: IconName
  description: string
}

const studyPillars: StudyPillar[] = [
  {
    step: '01',
    title: 'Resumo Analítico',
    icon: 'book-open',
    description: 'A síntese rigorosa do argumento central do autor, destacando a tese nuclear e os fios condutores da leitura sem ruídos.',
  },
  {
    step: '02',
    title: 'Explicação Detalhada',
    icon: 'network',
    description: 'Aprofundamento didático e reflexivo: desdobramento dos argumentos, contextos históricos, premissas implícitas e conclusões.',
  },
  {
    step: '03',
    title: 'Conceitos Chave',
    icon: 'sliders',
    description: 'Mapeamento preciso de vocabulário específico, termos técnicos, definições cunhadas pelo autor e ideias fundamentais.',
  },
  {
    step: '04',
    title: 'Referências e Citações',
    icon: 'link',
    description: 'Pontes intertextuais: conexões com outras obras lidas, passagens memoráveis marcadas e bibliografia recomendada.',
  },
]

interface CommitmentItem {
  icon: IconName
  title: string
  description: string
}

const commitments: CommitmentItem[] = [
  {
    icon: 'shield',
    title: 'Privacidade Constitucional',
    description: 'Suas notas e anotações pertencem unicamente a você. Não usamos seus textos para treinar modelos, nem vendemos seus hábitos de leitura.',
  },
  {
    icon: 'eye-off',
    title: 'Zero Anúncios e Distrações',
    description: 'Interface limpa, minimalista e focada exclusivamente no ato de ler, estudar e refletir em profundidade.',
  },
  {
    icon: 'monitor',
    title: 'Arquitetura Local-First',
    description: 'Desenhado para operar em sua máquina local com banco SQLite protegido, alta performance e capacidade de exportação em Markdown puro.',
  },
]
</script>

<template>
  <div class="about-page">
    <header class="about-hero">
      <div class="badge-tag">Filosofia Editorial & Metodologia</div>
      <h1 class="hero-title">Um refúgio para ler e estudar com profundidade.</h1>
      <p class="hero-subtitle">
        O <strong>Leitorum</strong> nasceu da necessidade de resgatar o estudo atento em tempos de fragmentação. Um caderno de leitura digital estruturado para transformar impressões passageiras em conhecimento duradouro.
      </p>
    </header>

    <!-- Seção: Metodologia em 4 Partes -->
    <section class="methodology-section" aria-labelledby="methodology-heading">
      <div class="section-header">
        <h2 id="methodology-heading" class="section-title">A Metodologia em 4 Partes</h2>
        <p class="section-lead">
          Cada estudo no Leitorum é articulado em quatro dimensões complementares, inspiradas nas tradições clássicas de fichamento analítico:
        </p>
      </div>

      <div class="pillars-grid">
        <article v-for="pillar in studyPillars" :key="pillar.step" class="pillar-card">
          <div class="pillar-header">
            <span class="pillar-step">{{ pillar.step }}</span>
            <div class="pillar-icon-box">
              <Icon :name="pillar.icon" :size="20" />
            </div>
          </div>
          <h3 class="pillar-title">{{ pillar.title }}</h3>
          <p class="pillar-desc">{{ pillar.description }}</p>
        </article>
      </div>
    </section>

    <!-- Seção: Organização em Camadas -->
    <section class="layers-section" aria-labelledby="layers-heading">
      <div class="section-header">
        <h2 id="layers-heading" class="section-title">Organização em Camadas</h2>
        <p class="section-lead">
          Do todo à parte: organize sua biblioteca por livros, divida em capítulos e ancore múltiplos estudos com relações semânticas entre si.
        </p>
      </div>
      <div class="layers-graphic">
        <div class="layer-step">
          <span class="layer-num">1</span>
          <div class="layer-content">
            <h4>O Livro</h4>
            <p>O acervo de obras com metadados, autores, ano de publicação e categorização canônica.</p>
          </div>
        </div>
        <div class="layer-arrow">↓</div>
        <div class="layer-step">
          <span class="layer-num">2</span>
          <div class="layer-content">
            <h4>Capítulos & Seções</h4>
            <p>A estrutura formal da obra respeitada e ordenada cronologicamente.</p>
          </div>
        </div>
        <div class="layer-arrow">↓</div>
        <div class="layer-step">
          <span class="layer-num">3</span>
          <div class="layer-content">
            <h4>Fichamentos & Estudos</h4>
            <p>Suas análises nas 4 partes, com marcações visuais, status de maturação e versões.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Seção: Compromissos Éticos -->
    <section class="ethics-section" aria-labelledby="ethics-heading">
      <div class="section-header">
        <h2 id="ethics-heading" class="section-title">Compromisso com o Leitor</h2>
        <p class="section-lead">Construído segundo princípios éticos e de soberania digital.</p>
      </div>

      <div class="commitments-grid">
        <div v-for="item in commitments" :key="item.title" class="commitment-card">
          <div class="commitment-icon-wrap">
            <Icon :name="item.icon" :size="24" />
          </div>
          <h3 class="commitment-title">{{ item.title }}</h3>
          <p class="commitment-desc">{{ item.description }}</p>
        </div>
      </div>
    </section>

    <!-- Seção: Chamada de Ação -->
    <section class="cta-banner">
      <h2>Pronto para elevar a qualidade de suas leituras?</h2>
      <p>Abra seu acervo agora mesmo ou apoie a continuidade do projeto.</p>
      <div class="cta-actions">
        <RouterLink to="/registro" class="cta-btn primary">Criar Conta Gratuita</RouterLink>
        <RouterLink to="/apoie" class="cta-btn secondary">Apoie o Leitorum</RouterLink>
      </div>
    </section>
  </div>
</template>

<style scoped>
.about-page {
  max-width: 54rem;
  margin: 0 auto;
  padding: 1.5rem 1rem 4rem;
}

.about-hero {
  text-align: center;
  margin-bottom: 3.5rem;
  padding: 1rem 0 2rem;
}

.badge-tag {
  display: inline-block;
  font-size: 0.8125rem;
  font-weight: 650;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 0.3rem 0.8rem;
  border-radius: 9999px;
  background: var(--color-surface-soft, rgba(0, 0, 0, 0.05));
  border: 1px solid var(--color-border);
  color: var(--color-muted);
  margin-bottom: 1.25rem;
}

.hero-title {
  font-size: clamp(2rem, 4.5vw, 3rem);
  line-height: 1.15;
  letter-spacing: -0.035em;
  margin-bottom: 1.25rem;
}

.hero-subtitle {
  font-size: 1.125rem;
  line-height: 1.6;
  color: var(--color-muted);
  max-width: 44rem;
  margin: 0 auto;
}

.section-header {
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.625rem;
  letter-spacing: -0.02em;
  margin-bottom: 0.5rem;
}

.section-lead {
  font-size: 1.0625rem;
  color: var(--color-muted);
  line-height: 1.5;
  margin: 0;
}

.methodology-section,
.layers-section,
.ethics-section {
  margin-bottom: 4rem;
}

.pillars-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.25rem;
}

.pillar-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-card, 10px);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  transition: transform 0.15s ease, border-color 0.15s ease;
}

.pillar-card:hover {
  border-color: var(--color-accent);
}

.pillar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.pillar-step {
  font-size: 0.875rem;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  color: var(--color-muted);
}

.pillar-icon-box {
  color: var(--color-accent);
}

.pillar-title {
  font-size: 1.1875rem;
  margin-bottom: 0.6rem;
}

.pillar-desc {
  font-size: 0.9375rem;
  color: var(--color-muted);
  line-height: 1.55;
  margin: 0;
}

.layers-graphic {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-width: 36rem;
  margin: 0 auto;
}

.layer-step {
  display: flex;
  align-items: flex-start;
  gap: 1.25rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-card, 10px);
  padding: 1.25rem;
}

.layer-num {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 50%;
  background: var(--color-accent);
  color: var(--color-on-accent, #fff);
  font-weight: 700;
  flex-shrink: 0;
}

.layer-content h4 {
  margin: 0 0 0.25rem;
  font-size: 1.0625rem;
}

.layer-content p {
  margin: 0;
  font-size: 0.9375rem;
  color: var(--color-muted);
}

.layer-arrow {
  text-align: center;
  font-size: 1.25rem;
  color: var(--color-muted);
}

.commitments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.25rem;
}

.commitment-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-card, 10px);
  padding: 1.5rem;
}

.commitment-icon-wrap {
  margin-bottom: 1rem;
  color: var(--color-accent);
}

.commitment-title {
  font-size: 1.125rem;
  margin-bottom: 0.5rem;
}

.commitment-desc {
  font-size: 0.9375rem;
  color: var(--color-muted);
  line-height: 1.5;
  margin: 0;
}

.cta-banner {
  background: var(--color-surface-soft, rgba(0, 0, 0, 0.03));
  border: 1px solid var(--color-border);
  border-radius: var(--radius-panel, 12px);
  padding: 2.5rem 1.5rem;
  text-align: center;
}

.cta-banner h2 {
  font-size: 1.625rem;
  margin-bottom: 0.5rem;
}

.cta-banner p {
  color: var(--color-muted);
  font-size: 1.0625rem;
  margin-bottom: 1.5rem;
}

.cta-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.cta-btn {
  padding: 0.75rem 1.5rem;
  font-weight: 650;
  text-decoration: none;
  border-radius: var(--radius-button, 8px);
  font-size: 0.9375rem;
  transition: all 0.15s ease;
}

.cta-btn.primary {
  background: var(--color-accent);
  color: var(--color-on-accent, #fff);
}

.cta-btn.secondary {
  background: var(--color-surface);
  color: var(--color-text);
  border: 1px solid var(--color-border);
}

.cta-btn.secondary:hover {
  background: var(--color-surface-hover);
}
</style>
