<script setup lang="ts">
import { RouterLink } from 'vue-router'
import Icon from '../ui/Icon.vue'
</script>

<template>
  <header class="public-header" role="banner">
    <!-- Link acessível para pular direto ao conteúdo principal -->
    <a href="#conteudo-principal" class="skip-link">
      Pular para o conteúdo
    </a>

    <div class="header-container">
      <div class="brand-wrapper">
        <RouterLink to="/" class="brand-link" aria-label="Leitorum — Início">
          <Icon name="book-open" :size="22" class="brand-icon" />
          <span class="brand-name">Leitorum</span>
        </RouterLink>
      </div>

      <nav class="nav-anchors" aria-label="Navegação da página inicial">
        <a href="#metodo" class="nav-anchor-link">Método</a>
        <a href="#temas" class="nav-anchor-link">Temas</a>
        <a href="#principios" class="nav-anchor-link">Princípios</a>
      </nav>

      <div class="header-actions">
        <RouterLink to="/login" class="btn-login-header">
          <span>Entrar</span>
          <Icon name="arrow-right" :size="16" />
        </RouterLink>
      </div>
    </div>
  </header>
</template>

<style scoped>
.public-header {
  position: relative;
  width: 100%;
  height: 64px;
  background-color: var(--color-page);
  border-bottom: 1px solid var(--color-border-divider, var(--color-border));
  z-index: 50;
  transition: background-color 0.2s ease, border-color 0.2s ease;
}

.skip-link {
  position: absolute;
  top: -100px;
  left: 1rem;
  background-color: var(--color-accent);
  color: var(--color-on-accent, #ffffff);
  padding: 0.5rem 1rem;
  border-radius: var(--radius-sm, 4px);
  font-size: 0.875rem;
  font-weight: 600;
  z-index: 100;
  text-decoration: none;
  transition: top 0.15s ease-out;
}

.skip-link:focus {
  top: 0.75rem;
  outline: 2px solid var(--color-on-accent, #ffffff);
  outline-offset: 2px;
}

.header-container {
  max-width: 1200px;
  margin: 0 auto;
  height: 100%;
  padding: 0 clamp(1rem, 4vw, 3rem);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.brand-wrapper {
  display: flex;
  align-items: center;
}

.brand-link {
  display: inline-flex;
  align-items: center;
  gap: 0.625rem;
  text-decoration: none;
  color: var(--color-text);
  min-height: 44px;
}

.brand-icon {
  color: var(--color-accent);
}

.brand-name {
  font-family: var(--font-reading, "Caderno EB Garamond", serif);
  font-size: 1.45rem;
  font-weight: 600;
  letter-spacing: -0.01em;
}

.nav-anchors {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.nav-anchor-link {
  font-size: 0.95rem;
  font-weight: 500;
  color: var(--color-text);
  text-decoration: none;
  padding: 0.5rem 0.25rem;
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  position: relative;
  transition: color 0.15s ease;
}

.nav-anchor-link:hover {
  color: var(--color-accent);
}

.nav-anchor-link:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 4px;
  border-radius: var(--radius-sm, 4px);
}

.header-actions {
  display: flex;
  align-items: center;
}

.btn-login-header {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.925rem;
  font-weight: 600;
  color: var(--color-text);
  text-decoration: none;
  padding: 0.45rem 0.9rem;
  border-radius: var(--radius-md, 6px);
  border: 1px solid var(--color-border);
  background-color: var(--color-surface);
  min-height: 44px;
  transition: all 0.15s ease;
}

.btn-login-header:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.btn-login-header:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

@media (max-width: 768px) {
  .public-header {
    height: 56px;
  }

  .nav-anchors {
    display: none;
  }
}
</style>
