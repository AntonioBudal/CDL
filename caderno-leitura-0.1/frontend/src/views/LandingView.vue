<script setup lang="ts">
import HeroSection from '../components/landing/HeroSection.vue'
import MethodSimulator from '../components/landing/MethodSimulator.vue'
import FeatureList from '../components/landing/FeatureList.vue'
import ThemeShowcase from '../components/landing/ThemeShowcase.vue'
import SovereigntySection from '../components/landing/SovereigntySection.vue'
import { buildWebApplicationSchema, useSeoMeta } from '../composables/useSeoMeta'

const origin = typeof window !== 'undefined' ? window.location.origin : 'https://leitorum.com'

// O título recebe o sufixo " — Leitorum" em updateSeoMeta.
useSeoMeta({
  title: 'Caderno de leitura e fichamento',
  description:
    'Organize livros por capítulo e escreva estudos com resumo, explicação, conceitos e referências. Marque trechos, revise o que marcou e exporte em Markdown.',
  canonicalUrl: `${origin}/`,
  ogType: 'website',
  robots: 'index, follow',
  jsonLd: buildWebApplicationSchema(origin),
})
</script>

<template>
  <!-- Cabeçalho, rodapé e o elemento main vêm do App.vue (GlobalHeader e app-footer). -->
  <div class="landing-page">
    <HeroSection />
    <MethodSimulator />
    <FeatureList />
    <ThemeShowcase />
    <SovereigntySection />
  </div>
</template>

<style scoped>
.landing-page {
  display: flex;
  flex-direction: column;
  color: var(--color-text);
}
</style>

<style>
/* Revelação ao rolar (diretiva v-reveal em composables/useReveal.ts); global para valer em todas as seções. */
.landing-page .reveal {
  opacity: 0;
  transform: translateY(22px);
  transition: opacity 0.6s ease, transform 0.6s cubic-bezier(0.22, 1, 0.36, 1);
  transition-delay: var(--reveal-delay, 0ms);
}

.landing-page .reveal.is-revealed {
  opacity: 1;
  transform: none;
}

@media (prefers-reduced-motion: reduce) {
  .landing-page .reveal {
    opacity: 1;
    transform: none;
    transition: none;
  }
}
</style>
