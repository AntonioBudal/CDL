<script setup lang="ts">
import { RouterLink } from 'vue-router'
import Icon from '../ui/Icon.vue'
import type { IconName } from '../../types'

interface PrincipleItem {
  icon: IconName
  title: string
  description: string
}

interface HistoricalMilestone {
  era: string
  title: string
  description: string
}

const principles: PrincipleItem[] = [
  {
    icon: 'shield',
    title: 'Sem anúncios nem rastreadores ocultos',
    description:
      'Zero telemetria, zero cookies de rastreamento e zero monetização da sua atenção. Nenhum terceiro monitora quais livros você estuda ou que páginas você lê.',
  },
  {
    icon: 'lock',
    title: 'Suas notas não alimentam modelos externos',
    description:
      'Nenhum texto, citação ou comentário seu é transmitido a serviços externos de IA nem utilizado para treinamento de modelos de linguagem de terceiros.',
  },
  {
    icon: 'download',
    title: 'Você pode levar tudo embora a qualquer instante',
    description:
      'Soberania local-first: exporte seu acervo completo em formatos abertos e perenes (Markdown, JSON e backup SQLite). Seus cadernos pertencem a você para sempre.',
  },
  {
    icon: 'heart',
    title: 'Software independente mantido para leitores',
    description:
      'Código auditável e transparente, sem pressão de algoritmos ou de retenção comercial. Um projeto concebido para durar décadas, não apenas trimestres fiscais.',
  },
]

const milestones: HistoricalMilestone[] = [
  {
    era: 'Século XVI',
    title: 'Cadernos de Lugares-Comuns (Commonplace Books)',
    description:
      'De Erasmo de Roterdã a Montaigne, leitores mantinham cadernos artesanais onde transcreviam e agrupavam citações capitais sob rubricas temáticas, construindo uma extensão física da memória.',
  },
  {
    era: '1706',
    title: 'O Método de Índice de John Locke',
    description:
      'O filósofo inglês sistematiza em tratado o método de indexação alfabética rápida de anotações, resolvendo o problema de encontrar trechos cruzados sem desorganizar as páginas do caderno.',
  },
  {
    era: 'Hoje',
    title: 'O Fichamento em Camadas no Leitorum',
    description:
      'Reunimos cinco séculos de sabedoria leitora em uma bancada digital sem ruído: quatro camadas cognitivas, marcações marginais, revisão espaçada e independência absoluta de nuvens proprietárias.',
  },
]
</script>

<template>
  <section id="principios" class="sovereignty-section" aria-labelledby="principles-heading">
    <div class="sovereignty-container">
      <!-- Seção 1: Quatro Garantias de Soberania -->
      <div class="principles-block">
        <div class="section-intro">
          <span class="section-eyebrow">Soberania e Privacidade</span>
          <h2 id="principles-heading" class="section-title">
            Seus pensamentos não são matéria-prima de ninguém.
          </h2>
          <p class="section-lead">
            Cadernos íntimos de anotações exigem um pacto ético de confiança inviolável. Nossos quatro compromissos com a sua integridade:
          </p>
        </div>

        <div class="principles-grid">
          <div
            v-for="p in principles"
            :key="p.title"
            class="principle-card"
          >
            <div class="principle-icon-wrapper">
              <Icon :name="p.icon" :size="22" />
            </div>
            <h3 class="principle-title">{{ p.title }}</h3>
            <p class="principle-desc">{{ p.description }}</p>
          </div>
        </div>
      </div>

      <hr class="sovereignty-divider" />

      <!-- Seção 2: Linhagem Histórica dos Commonplace Books -->
      <div class="history-block">
        <div class="section-intro">
          <span class="section-eyebrow">Tradição Intelectual</span>
          <h2 class="section-title">
            Uma linhagem de quinhentos anos de leitura atenta.
          </h2>
          <p class="section-lead">
            O Leitorum não inventou o ato de ler devagar; apenas resgatou a tradição dos maiores pensadores da história e a colocou ao alcance das suas mãos.
          </p>
        </div>

        <div class="timeline-container">
          <div
            v-for="(m, idx) in milestones"
            :key="m.era"
            class="timeline-card"
          >
            <div class="timeline-era-badge">
              <span class="era-index">{{ idx + 1 }}</span>
              <span class="era-label">{{ m.era }}</span>
            </div>
            <h3 class="timeline-title">{{ m.title }}</h3>
            <p class="timeline-desc">{{ m.description }}</p>
          </div>
        </div>

        <div class="institutional-links-row">
          <RouterLink to="/sobre" class="text-link-button">
            <span>Ler o ensaio sobre a metodologia</span>
            <Icon name="arrow-right" :size="16" />
          </RouterLink>

          <RouterLink to="/apoie" class="text-link-button secondary">
            <span>Apoie o desenvolvimento independente</span>
            <Icon name="heart" :size="16" />
          </RouterLink>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.sovereignty-section {
  padding-block: clamp(4rem, 8vw, 7.5rem);
  background-color: var(--color-page);
  color: var(--color-text);
  border-bottom: 1px solid var(--color-border-divider, var(--color-border));
}

.sovereignty-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 clamp(1rem, 4vw, 3rem);
}

.section-intro {
  max-width: 68ch;
  margin-bottom: clamp(2rem, 4vw, 3.5rem);
}

.section-eyebrow {
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--color-accent);
  display: block;
  margin-bottom: 0.75rem;
}

.section-title {
  font-family: var(--font-reading, "Caderno EB Garamond", serif);
  font-size: clamp(2rem, 3.5vw, 3rem);
  font-weight: 600;
  line-height: 1.15;
  letter-spacing: -0.015em;
  margin: 0 0 1rem 0;
  color: var(--color-text);
}

.section-lead {
  font-size: 1.05rem;
  line-height: 1.65;
  color: var(--color-text);
  margin: 0;
  opacity: 0.95;
}

/* Grade de Princípios de Soberania */
.principles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.75rem;
}

.principle-card {
  padding: 1.75rem;
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg, 10px);
  display: flex;
  flex-direction: column;
}

.principle-icon-wrapper {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md, 8px);
  background-color: var(--color-page);
  color: var(--color-accent);
  border: 1px solid var(--color-border);
  margin-bottom: 1.25rem;
}

.principle-title {
  font-size: 1.1rem;
  font-weight: 600;
  line-height: 1.3;
  margin: 0 0 0.75rem 0;
  color: var(--color-text);
}

.principle-desc {
  font-size: 0.925rem;
  line-height: 1.55;
  color: var(--color-text);
  opacity: 0.88;
  margin: 0;
}

.sovereignty-divider {
  border: 0;
  border-top: 1px solid var(--color-border-divider, var(--color-border));
  margin: clamp(3.5rem, 6vw, 5.5rem) 0;
}

/* Linha do Tempo Histórica */
.timeline-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.75rem;
  margin-bottom: 2.5rem;
}

.timeline-card {
  padding: 1.75rem;
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg, 10px);
  display: flex;
  flex-direction: column;
}

.timeline-era-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.era-index {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  font-size: 0.75rem;
  font-weight: 700;
  background-color: var(--color-accent);
  color: var(--color-on-accent, #ffffff);
}

.era-label {
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-accent);
}

.timeline-title {
  font-family: var(--font-reading, "Caderno EB Garamond", serif);
  font-size: 1.35rem;
  font-weight: 600;
  line-height: 1.25;
  margin: 0 0 0.75rem 0;
  color: var(--color-text);
}

.timeline-desc {
  font-size: 0.925rem;
  line-height: 1.55;
  color: var(--color-text);
  opacity: 0.88;
  margin: 0;
}

.institutional-links-row {
  display: flex;
  align-items: center;
  gap: 2rem;
  flex-wrap: wrap;
}

.text-link-button {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.975rem;
  font-weight: 600;
  color: var(--color-accent);
  text-decoration: underline;
  text-underline-offset: 4px;
  min-height: 44px;
  transition: opacity 0.15s ease;
}

.text-link-button:hover {
  opacity: 0.8;
}

.text-link-button.secondary {
  color: var(--color-text);
}

.text-link-button:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 4px;
}
</style>
