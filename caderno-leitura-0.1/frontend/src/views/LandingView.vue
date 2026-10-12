<script setup lang="ts">
import PublicHeader from '../components/landing/PublicHeader.vue'
import HeroSection from '../components/landing/HeroSection.vue'
import MethodSimulator from '../components/landing/MethodSimulator.vue'
import ThemeShowcase from '../components/landing/ThemeShowcase.vue'
import SovereigntySection from '../components/landing/SovereigntySection.vue'
import PublicFooter from '../components/landing/PublicFooter.vue'
import { buildWebApplicationSchema, useSeoMeta } from '../composables/useSeoMeta'

useSeoMeta({
  title: 'Leitorum — Caderno de leitura e estudo em camadas',
  description:
    'Ambiente calmo para ler e estudar obras fundamentais. Fichamento analítico em 4 camadas cognitivas, privacidade absoluta, zero anúncios e soberania local-first.',
  canonicalUrl: typeof window !== 'undefined' ? `${window.location.origin}/` : 'https://leitorum.com/',
  ogType: 'website',
  robots: 'index, follow',
  jsonLd: buildWebApplicationSchema(),
})
</script>

<template>
  <div class="landing-page">
    <!-- Cabeçalho Público Institucional -->
    <PublicHeader />

    <!-- Conteúdo Principal -->
    <main id="main-content">
      <!-- Links de acessibilidade direta e indexação institucional -->
      <nav class="visually-hidden" aria-label="Acesso rápido institucional">
        <RouterLink to="/registro">Criar Conta</RouterLink>
        <RouterLink to="/login">Entrar</RouterLink>
        <RouterLink to="/sobre">Sobre o Leitorum</RouterLink>
        <RouterLink to="/apoie">Apoie o Leitorum</RouterLink>
      </nav>

      <!-- 1. Hero Editorial e Ficha de Leitura -->
      <HeroSection />

      <!-- 2. Bancada Interativa do Simulador em 4 Dimensões -->
      <MethodSimulator />

      <!-- 3. Ateliê Vitrine dos 10 Temas Canônicos -->
      <ThemeShowcase />

      <!-- 4. Soberania de Dados e Linhagem Histórica -->
      <SovereigntySection />
    </main>

    <!-- Rodapé Reflexivo e Institucional -->
    <PublicFooter />
  </div>
</template>

<style scoped>
.landing-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--color-page);
  color: var(--color-text);
  font-family: var(--font-sans, "Caderno Source Sans 3", sans-serif);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}
</style>
