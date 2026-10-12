<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <footer class="app-footer" role="contentinfo">
    <div class="footer-inner">
      <div class="footer-left">
        <span class="footer-brand">Leitorum</span>
        <span class="footer-license">Software Livre</span>
      </div>
      <nav class="footer-nav" aria-label="Navegação secundária do rodapé">
        <RouterLink to="/sobre" class="footer-link">Sobre o Leitorum</RouterLink>
        <RouterLink to="/apoie" class="footer-link">Apoie o Leitorum</RouterLink>
      </nav>
    </div>
  </footer>
</template>

<style scoped>
.app-footer {
  width: min(100% - var(--page-gutter, 2rem), var(--workspace-max-width, 74rem));
  margin: calc(var(--space-unit, 1rem) * 3) auto calc(var(--space-unit, 1rem) * 2.5);
  border-top: var(--border-width, 1px) solid var(--color-border);
  padding-top: calc(var(--space-unit, 1rem) * 1.5);
  padding-inline: clamp(0.5rem, 2vw, 1.5rem);
  color: var(--color-muted);
  font-size: 0.875rem;
  box-sizing: border-box;
}

.footer-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1.5rem;
  width: 100%;
}

.footer-left {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
}

.footer-nav {
  display: inline-flex;
  align-items: center;
  gap: 1.25rem;
}

.footer-brand {
  font-weight: 600;
  color: var(--color-text);
}

.footer-license {
  font-size: 0.8125rem;
  opacity: 0.8;
}

.footer-link {
  color: inherit;
  text-decoration: none;
  transition: color 0.15s ease;
}

.footer-link:hover {
  text-decoration: underline;
  color: var(--color-accent);
}

@media (max-width: 640px) {
  .footer-inner {
    flex-direction: column;
    align-items: center;
    gap: 0.75rem;
    text-align: center;
  }
}
</style>
