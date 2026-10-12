<script setup lang="ts">
import { RouterLink } from 'vue-router'
import Icon from '../ui/Icon.vue'
</script>

<template>
  <footer class="public-footer" role="contentinfo">
    <div class="footer-container">
      <!-- Bloco de Chamada Final Reflexiva -->
      <div class="footer-cta-block">
        <h2 class="footer-cta-title">
          Comece pelo próximo livro que você pretende ler devagar.
        </h2>
        <p class="footer-cta-lead">
          Livre de algoritmos e métricas de vaidade. Um caderno calmo dedicado exclusivamente à sua reflexão intelectual.
        </p>
        <div class="footer-cta-actions">
          <RouterLink to="/registro" class="btn-footer-primary">
            <span>Criar Conta Gratuita</span>
            <Icon name="arrow-right" :size="18" />
          </RouterLink>
          <RouterLink to="/login" class="btn-footer-secondary">
            <span>Já possuo conta (Entrar)</span>
          </RouterLink>
        </div>
      </div>

      <hr class="footer-divider" />

      <!-- Bloco Institucional e Navegação Secundária -->
      <div class="footer-institutional">
        <div class="footer-brand-meta">
          <div class="brand-row">
            <Icon name="book-open" :size="20" class="footer-brand-icon" />
            <span class="footer-brand-name">Leitorum</span>
          </div>
          <p class="footer-tagline">
            Caderno pessoal de leitura e estudos em camadas. Construído com respeito ao tempo, à atenção e à memória do leitor.
          </p>
        </div>

        <nav class="footer-nav" aria-label="Links institucionais do rodapé">
          <div class="footer-nav-col">
            <span class="nav-heading">Plataforma</span>
            <ul class="nav-links">
              <li><RouterLink to="/sobre">Sobre o Projeto</RouterLink></li>
              <li><RouterLink to="/apoie">Apoie o Leitorum</RouterLink></li>
              <li><RouterLink to="/login">Identificação</RouterLink></li>
              <li><RouterLink to="/registro">Criar Conta</RouterLink></li>
            </ul>
          </div>

          <div class="footer-nav-col">
            <span class="nav-heading">Transparência</span>
            <ul class="nav-links">
              <li><a href="https://github.com/AntonioBudal/CDL" target="_blank" rel="noopener noreferrer">Código Aberto</a></li>
              <li><a href="/robots.txt">robots.txt</a></li>
              <li><a href="/sitemap.xml">sitemap.xml</a></li>
            </ul>
          </div>
        </nav>
      </div>

      <div class="footer-bottom-bar">
        <p class="copyright-text">
          &copy; {{ new Date().getFullYear() }} Leitorum. Software livre sob licença MIT. Sem rastreamento comercial.
        </p>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.public-footer {
  background-color: var(--color-surface);
  color: var(--color-text);
  border-top: 1px solid var(--color-border-divider, var(--color-border));
  padding-block: clamp(4rem, 7vw, 6.5rem) clamp(2rem, 4vw, 3rem);
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 clamp(1rem, 4vw, 3rem);
}

/* Chamada Final */
.footer-cta-block {
  text-align: center;
  max-width: 64ch;
  margin: 0 auto clamp(3.5rem, 6vw, 5rem) auto;
}

.footer-cta-title {
  font-family: var(--font-reading, "Caderno EB Garamond", serif);
  font-size: clamp(2.2rem, 4vw, 3.25rem);
  font-weight: 600;
  line-height: 1.15;
  letter-spacing: -0.015em;
  margin: 0 0 1rem 0;
  color: var(--color-text);
}

.footer-cta-lead {
  font-size: 1.1rem;
  line-height: 1.6;
  color: var(--color-text);
  opacity: 0.9;
  margin: 0 0 2rem 0;
}

.footer-cta-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.btn-footer-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  height: 48px;
  padding: 0 2rem;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-on-accent, #ffffff);
  background-color: var(--color-accent);
  border-radius: var(--radius-md, 8px);
  text-decoration: none;
  min-height: 44px;
  min-width: 44px;
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.btn-footer-primary:hover {
  opacity: 0.92;
  transform: translateY(-1px);
}

.btn-footer-primary:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 3px;
}

.btn-footer-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 48px;
  padding: 0 1.5rem;
  font-size: 0.975rem;
  font-weight: 500;
  color: var(--color-text);
  background-color: var(--color-page);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md, 8px);
  text-decoration: none;
  min-height: 44px;
  min-width: 44px;
  transition: all 0.15s ease;
}

.btn-footer-secondary:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.btn-footer-secondary:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

.footer-divider {
  border: 0;
  border-top: 1px solid var(--color-border-divider, var(--color-border));
  margin-bottom: clamp(2.5rem, 5vw, 4rem);
}

/* Área Institucional */
.footer-institutional {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 3rem;
  margin-bottom: 3rem;
}

.brand-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.footer-brand-icon {
  color: var(--color-accent);
}

.footer-brand-name {
  font-family: var(--font-reading, "Caderno EB Garamond", serif);
  font-size: 1.35rem;
  font-weight: 600;
  color: var(--color-text);
}

.footer-tagline {
  font-size: 0.925rem;
  line-height: 1.55;
  color: var(--color-text);
  opacity: 0.85;
  max-width: 48ch;
  margin: 0;
}

.footer-nav {
  display: flex;
  gap: 4rem;
  justify-content: flex-end;
}

.nav-heading {
  display: block;
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-accent);
  margin-bottom: 1rem;
}

.nav-links {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.nav-links a {
  font-size: 0.925rem;
  color: var(--color-text);
  text-decoration: none;
  transition: color 0.15s ease;
  min-height: 32px;
  display: inline-flex;
  align-items: center;
}

.nav-links a:hover {
  color: var(--color-accent);
  text-decoration: underline;
  text-underline-offset: 3px;
}

.nav-links a:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
  border-radius: 2px;
}

.footer-bottom-bar {
  padding-top: 2rem;
  border-top: 1px solid var(--color-border);
  text-align: center;
}

.copyright-text {
  font-size: 0.85rem;
  color: var(--color-text);
  opacity: 0.75;
  margin: 0;
}

@media (max-width: 768px) {
  .footer-institutional {
    grid-template-columns: 1fr;
    gap: 2.5rem;
  }

  .footer-nav {
    justify-content: flex-start;
    gap: 3rem;
  }

  .footer-cta-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .btn-footer-primary,
  .btn-footer-secondary {
    width: 100%;
  }
}
</style>
