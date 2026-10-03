<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <footer class="app-footer" role="contentinfo">
    <div class="footer-inner">
      <span class="footer-brand">Leitorum</span>
      <span class="footer-sep" aria-hidden="true">·</span>
      <RouterLink to="/sobre" class="footer-link">Sobre o Leitorum</RouterLink>
      <span class="footer-sep" aria-hidden="true">·</span>
      <RouterLink to="/apoie" class="footer-link">Apoie o Leitorum</RouterLink>
      <span class="footer-sep" aria-hidden="true">·</span>
      <span class="footer-license">Software Livre</span>
    </div>
  </footer>
</template>

<style scoped>
.app-footer {
  width: min(100% - var(--page-gutter), var(--workspace-max-width));
  margin: 0 auto calc(var(--space-unit) * 2);
  border-top: var(--border-width) solid var(--color-border);
  padding-top: calc(var(--space-unit) * 1.25);
  color: var(--color-muted);
  font-size: 0.875rem;
}

.footer-inner {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 0.5rem 0.75rem;
}

.footer-sep {
  opacity: 0.4;
}

.footer-link {
  color: inherit;
  text-decoration: none;
  transition: color 0.15s ease;
}

.footer-link:hover {
  text-decoration: underline;
  color: var(--color-accent, #2563eb);
}

.footer-brand {
  font-weight: 600;
}

.footer-license {
  font-size: 0.8125rem;
  opacity: 0.8;
}
</style>
