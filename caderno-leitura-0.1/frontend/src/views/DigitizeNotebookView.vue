<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { DOCUMENT_INTELLIGENCE_STAGES, DIGITIZE_EXIT_SHORTCUTS } from '../types/digitize'
</script>

<template>
  <main
    class="digitize-notebook-view"
    role="main"
    aria-labelledby="digitize-main-title"
  >
    <div class="digitize-container">
      <!-- 1. Cabeçalho Editorial & Manifesto de Privacidade Soberana -->
      <header class="digitize-header">
        <div class="status-pill" role="status">
          <svg class="status-icon" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
          </svg>
          <span>Pesquisa Experimental — Subprojeto Document Intelligence</span>
        </div>

        <h1 id="digitize-main-title" class="page-title">
          Digitalizar Caderno
        </h1>

        <p class="page-lead">
          Um espaço dedicado a transformar fotografias de páginas de cadernos físicos manuscritos em
          <strong>estudos estruturados</strong>, preservando a hierarquia de parágrafos, anotações de margem, diagramas e o ritmo autêntico da sua leitura.
        </p>

        <!-- Manifesto de Soberania de Dados e Processamento Local -->
        <div class="privacy-card" role="region" aria-label="Compromisso de Soberania e Privacidade">
          <div class="privacy-badge-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <div class="privacy-content">
            <h2 class="privacy-title">Processamento Estritamente Local no seu Computador</h2>
            <p class="privacy-text">
              No Leitorum, seus cadernos pertencem somente a você. Quando a funcionalidade estiver operacional,
              toda a análise de imagem e o reconhecimento manuscrito serão executados <strong>localmente, na sua própria máquina</strong>.
              Nenhuma foto, rascunho ou texto será transmitido a servidores em nuvem ou modelos externos de inteligência artificial.
            </p>
            <p class="privacy-status-note">
              <strong>Estágio Atual:</strong> Esta funcionalidade está em fase de pesquisa laboratorial. Não existe serviço ou modelo ativo em produção no momento, e não há promessa de data de lançamento.
            </p>
          </div>
        </div>
      </header>

      <!-- 2. Como a Estruturação Funcionará (Do Papel ao Fichamento) -->
      <section class="concept-section" aria-labelledby="concept-heading">
        <div class="section-header">
          <h2 id="concept-heading" class="section-title">Do Papel ao Estudo Estruturado</h2>
          <p class="section-subtitle">
            Diferente de um scanner tradicional que apenas extrai um bloco desordenado de texto corrido, a tecnologia busca reconstituir a lógica espacial da página:
          </p>
        </div>

        <div class="concept-grid">
          <div class="concept-card">
            <div class="concept-icon-wrap" aria-hidden="true">
              <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h7" />
              </svg>
            </div>
            <h3 class="concept-card-title">Linhas e Parágrafos</h3>
            <p class="concept-card-desc">
              Identificação exata do corpo de texto principal, separando títulos, subtítulos e blocos de parágrafos conforme a diagramação manuscrita.
            </p>
          </div>

          <div class="concept-card">
            <div class="concept-icon-wrap" aria-hidden="true">
              <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
              </svg>
            </div>
            <h3 class="concept-card-title">Notas de Margem</h3>
            <p class="concept-card-desc">
              Preservação de anotações laterais, interpolações e observações de rodapé como reflexões subordinadas associadas ao trecho principal.
            </p>
          </div>

          <div class="concept-card">
            <div class="concept-icon-wrap" aria-hidden="true">
              <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 class="concept-card-title">Diagramas e Esquemas</h3>
            <p class="concept-card-desc">
              Detecção de caixas delimitadoras e regiões gráficas, permitindo manter desenhos e esquemas conceituais integrados ao estudo.
            </p>
          </div>

          <div class="concept-card">
            <div class="concept-icon-wrap" aria-hidden="true">
              <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </div>
            <h3 class="concept-card-title">Ordem Natural de Leitura</h3>
            <p class="concept-card-desc">
              Ordenação topológica inteligente que reconstrói a sequência coerente do pensamento entre múltiplas colunas e notas soltas.
            </p>
          </div>
        </div>
      </section>

      <!-- 3. Ilustração Conceitual Rotulada (Texto Fictício) -->
      <section class="mockup-section" aria-labelledby="mockup-heading">
        <div class="mockup-header">
          <span class="mockup-tag">Ilustração Conceitual</span>
          <h2 id="mockup-heading" class="mockup-title">Visualização da Segmentação Geométrica</h2>
          <p class="mockup-subtitle">
            Demonstração gráfica de como as caixas delimitadoras mapeiam os blocos na folha sem confundir corpo e margens:
          </p>
        </div>

        <div class="mockup-page-canvas" aria-hidden="true">
          <div class="mockup-box box-title">
            <span class="box-badge">1 · Título</span>
            <p class="box-content-mock">Capítulo I — Do Hábito da Leitura Ativa</p>
          </div>

          <div class="mockup-body-row">
            <div class="mockup-box box-paragraph">
              <span class="box-badge">2 · Parágrafo Principal</span>
              <p class="box-content-mock">
                A disciplina de anotar à mão em um caderno físico desacelera o ritmo da leitura,
                permitindo que as ideias fundamentais amadureçam antes de se transformarem em síntese...
              </p>
            </div>

            <div class="mockup-box box-margin-note">
              <span class="box-badge">3 · Nota Marginal</span>
              <p class="box-content-mock">
                Confrontar com a tese de Schopenhauer sobre pensar por conta própria.
              </p>
            </div>
          </div>

          <div class="mockup-reading-flow-indicator">
            <span class="flow-step">1</span>
            <span class="flow-arrow">→</span>
            <span class="flow-step">2</span>
            <span class="flow-arrow">→</span>
            <span class="flow-step">3</span>
            <span class="flow-label">Ordem topológica de reconstituição</span>
          </div>
        </div>
      </section>

      <!-- 4. Matriz de Maturidade da Pesquisa (4 Etapas Fixas) -->
      <section class="maturity-section" aria-labelledby="maturity-heading">
        <div class="section-header">
          <h2 id="maturity-heading" class="section-title">Estágio Real da Pesquisa</h2>
          <p class="section-subtitle">
            Transparência técnica absoluta sobre o que já foi validado em laboratório e os desafios em investigação:
          </p>
        </div>

        <div class="stages-table-container">
          <div
            v-for="stage in DOCUMENT_INTELLIGENCE_STAGES"
            :key="stage.id"
            class="stage-row-card"
          >
            <div class="stage-status-col">
              <span
                class="stage-badge"
                :class="{
                  'badge-validating': stage.status === 'validating',
                  'badge-researching': stage.status === 'researching',
                  'badge-not-started': stage.status === 'not_started',
                }"
              >
                {{ stage.statusLabel }}
              </span>
            </div>

            <div class="stage-info-col">
              <h3 class="stage-title">{{ stage.title }}</h3>
              <p class="stage-desc">{{ stage.description }}</p>
              <p v-if="stage.technicalNote" class="stage-technical-note">
                <span class="note-prefix">Diagnóstico:</span> {{ stage.technicalNote }}
              </p>
            </div>
          </div>
        </div>
      </section>

      <!-- 5. Caminhos Disponíveis Hoje (Saídas Úteis) -->
      <section class="exit-actions-section" aria-labelledby="exit-heading">
        <div class="section-header">
          <h2 id="exit-heading" class="section-title">Enquanto a pesquisa avança, estude com o Leitorum</h2>
          <p class="section-subtitle">
            Utilize os fluxos já operacionais para registrar seus fichamentos e reflexões imediatas:
          </p>
        </div>

        <div class="exit-cards-grid">
          <div
            v-for="shortcut in DIGITIZE_EXIT_SHORTCUTS"
            :key="shortcut.routePath"
            class="exit-card"
          >
            <div class="exit-card-body">
              <h3 class="exit-card-title">{{ shortcut.title }}</h3>
              <p class="exit-card-desc">{{ shortcut.description }}</p>
            </div>
            <div class="exit-card-footer">
              <RouterLink :to="shortcut.routePath" class="btn-exit-action">
                <span>{{ shortcut.actionLabel }}</span>
                <svg viewBox="0 0 20 20" width="16" height="16" fill="currentColor" aria-hidden="true">
                  <path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </RouterLink>
            </div>
          </div>
        </div>
      </section>
    </div>
  </main>
</template>

<style scoped>
.digitize-notebook-view {
  min-height: 100vh;
  padding: 2.5rem 1.5rem 5rem;
  background-color: var(--color-background, #f8fafc);
  color: var(--color-text, #0f172a);
}

.digitize-container {
  max-width: 880px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 3.5rem;
}

/* 1. Cabeçalho */
.digitize-header {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.status-pill {
  align-self: flex-start;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.35rem 0.85rem;
  border-radius: 9999px;
  font-size: 0.8125rem;
  font-weight: 600;
  background-color: var(--color-surface-soft, rgba(0, 0, 0, 0.04));
  color: var(--color-text-secondary, #64748b);
  border: 1px solid var(--color-border-subtle, #e2e8f0);
}

.status-icon {
  flex-shrink: 0;
  color: var(--color-accent, #3b82f6);
}

.page-title {
  font-family: var(--font-serif, "EB Garamond", Garamond, Georgia, serif);
  font-size: 2.5rem;
  font-weight: 700;
  line-height: 1.15;
  letter-spacing: -0.02em;
  color: var(--color-text, #0f172a);
  margin: 0;
}

.page-lead {
  font-size: 1.125rem;
  line-height: 1.6;
  color: var(--color-text-secondary, #475569);
  margin: 0;
}

/* Card de Privacidade Soberana */
.privacy-card {
  display: flex;
  gap: 1.25rem;
  padding: 1.5rem;
  border-radius: var(--radius-card, 1rem);
  background-color: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border-subtle, #e2e8f0);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04);
}

.privacy-badge-icon {
  flex-shrink: 0;
  width: 44px;
  height: 44px;
  border-radius: 10px;
  background-color: var(--color-surface-soft, rgba(0, 0, 0, 0.03));
  color: var(--color-accent, #3b82f6);
  display: flex;
  align-items: center;
  justify-content: center;
}

.privacy-content {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.privacy-title {
  font-size: 1.0625rem;
  font-weight: 600;
  color: var(--color-text, #0f172a);
  margin: 0;
}

.privacy-text {
  font-size: 0.9375rem;
  line-height: 1.55;
  color: var(--color-text-secondary, #475569);
  margin: 0;
}

.privacy-status-note {
  font-size: 0.875rem;
  line-height: 1.5;
  padding: 0.65rem 0.85rem;
  border-radius: 8px;
  background-color: var(--color-surface-soft, rgba(0, 0, 0, 0.02));
  border-left: 3px solid var(--color-accent, #3b82f6);
  color: var(--color-text-secondary, #64748b);
  margin: 0.25rem 0 0;
}

/* Seções Comuns */
.section-header {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.section-title {
  font-family: var(--font-serif, "EB Garamond", Garamond, Georgia, serif);
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--color-text, #0f172a);
  margin: 0;
  letter-spacing: -0.015em;
}

.section-subtitle {
  font-size: 0.95rem;
  line-height: 1.5;
  color: var(--color-text-secondary, #64748b);
  margin: 0;
}

/* 2. Grid de Conceitos */
.concept-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.25rem;
}

.concept-card {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 1.25rem;
  border-radius: var(--radius-card, 0.75rem);
  background-color: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border-subtle, #e2e8f0);
}

.concept-icon-wrap {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background-color: var(--color-surface-soft, rgba(0, 0, 0, 0.03));
  color: var(--color-accent, #3b82f6);
  display: flex;
  align-items: center;
  justify-content: center;
}

.concept-card-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text, #0f172a);
  margin: 0;
}

.concept-card-desc {
  font-size: 0.875rem;
  line-height: 1.5;
  color: var(--color-text-secondary, #64748b);
  margin: 0;
}

/* 3. Ilustração Conceitual Rotulada */
.mockup-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.5rem;
  border-radius: var(--radius-card, 1rem);
  background-color: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border-subtle, #e2e8f0);
}

.mockup-header {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.mockup-tag {
  align-self: flex-start;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  background-color: var(--color-surface-soft, rgba(0, 0, 0, 0.06));
  color: var(--color-text-secondary, #64748b);
}

.mockup-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text, #0f172a);
  margin: 0;
}

.mockup-subtitle {
  font-size: 0.875rem;
  color: var(--color-text-secondary, #64748b);
  margin: 0;
}

.mockup-page-canvas {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.5rem;
  border-radius: 8px;
  background-color: var(--color-surface-soft, rgba(0, 0, 0, 0.02));
  border: 1px dashed var(--color-border-subtle, #cbd5e1);
}

.mockup-box {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  padding: 0.85rem 1rem;
  border-radius: 6px;
  background-color: var(--color-surface, #ffffff);
  border: 1px solid var(--color-accent, #3b82f6);
}

.box-title {
  border-left-width: 4px;
}

.mockup-body-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1rem;
}

.box-paragraph {
  border-left-width: 4px;
  border-color: var(--color-border-subtle, #94a3b8);
}

.box-margin-note {
  border-left-width: 4px;
  border-color: var(--color-accent, #3b82f6);
  background-color: var(--color-surface-soft, rgba(0, 0, 0, 0.01));
}

.box-badge {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-secondary, #64748b);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.box-content-mock {
  font-family: var(--font-serif, "EB Garamond", Garamond, Georgia, serif);
  font-size: 0.95rem;
  font-style: italic;
  line-height: 1.4;
  color: var(--color-text, #334155);
  margin: 0;
}

.mockup-reading-flow-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid var(--color-border-subtle, #e2e8f0);
  font-size: 0.8125rem;
  color: var(--color-text-secondary, #64748b);
}

.flow-step {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background-color: var(--color-accent, #3b82f6);
  color: var(--color-on-accent, #ffffff);
  font-size: 0.75rem;
  font-weight: 700;
}

.flow-arrow {
  color: var(--color-text-secondary, #94a3b8);
}

.flow-label {
  margin-left: 0.5rem;
}

/* 4. Matriz de Maturidade (4 Etapas) */
.stages-table-container {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.stage-row-card {
  display: flex;
  align-items: flex-start;
  gap: 1.25rem;
  padding: 1.15rem 1.25rem;
  border-radius: var(--radius-card, 0.75rem);
  background-color: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border-subtle, #e2e8f0);
}

.stage-status-col {
  flex-shrink: 0;
  width: 140px;
}

.stage-badge {
  display: inline-block;
  padding: 0.25rem 0.65rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  text-align: center;
  letter-spacing: 0.02em;
}

.badge-validating {
  background-color: var(--color-surface-soft, rgba(0, 0, 0, 0.05));
  color: var(--color-accent, #2563eb);
  border: 1px solid var(--color-accent, #93c5fd);
}

.badge-researching {
  background-color: var(--color-surface-soft, rgba(0, 0, 0, 0.05));
  color: var(--color-warning, #d97706);
  border: 1px solid var(--color-warning, #fcd34d);
}

.badge-not-started {
  background-color: var(--color-surface-soft, rgba(0, 0, 0, 0.03));
  color: var(--color-text-secondary, #64748b);
  border: 1px solid var(--color-border-subtle, #cbd5e1);
}

.stage-info-col {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  flex: 1;
}

.stage-title {
  font-size: 0.975rem;
  font-weight: 600;
  color: var(--color-text, #0f172a);
  margin: 0;
}

.stage-desc {
  font-size: 0.875rem;
  line-height: 1.45;
  color: var(--color-text-secondary, #475569);
  margin: 0;
}

.stage-technical-note {
  font-size: 0.8125rem;
  line-height: 1.4;
  color: var(--color-text-secondary, #64748b);
  margin: 0.25rem 0 0;
}

.note-prefix {
  font-weight: 600;
}

/* 5. Ações de Saída */
.exit-cards-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.25rem;
}

.exit-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 1.25rem;
  border-radius: var(--radius-card, 0.75rem);
  background-color: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border-subtle, #e2e8f0);
  gap: 1.25rem;
}

.exit-card-body {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.exit-card-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text, #0f172a);
  margin: 0;
}

.exit-card-desc {
  font-size: 0.875rem;
  line-height: 1.5;
  color: var(--color-text-secondary, #64748b);
  margin: 0;
}

.btn-exit-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  min-height: 44px;
  padding: 0.65rem 1.25rem;
  border-radius: var(--radius-button, 8px);
  background-color: var(--color-surface-soft, rgba(0, 0, 0, 0.04));
  color: var(--color-text, #0f172a);
  border: 1px solid var(--color-border-subtle, #e2e8f0);
  font-size: 0.875rem;
  font-weight: 600;
  text-decoration: none;
  transition: background-color 150ms ease, border-color 150ms ease, transform 150ms ease;
  width: 100%;
}

.btn-exit-action:hover {
  background-color: var(--color-accent, #3b82f6);
  color: var(--color-on-accent, #ffffff);
  border-color: transparent;
  transform: translateY(-1px);
}

.btn-exit-action:focus-visible {
  outline: 2px solid var(--color-accent, #3b82f6);
  outline-offset: 2px;
}

/* Responsividade Mobile (< 768px) */
@media (max-width: 768px) {
  .digitize-notebook-view {
    padding: 1.5rem 1rem 4rem;
  }

  .digitize-container {
    gap: 2.5rem;
  }

  .page-title {
    font-size: 2rem;
  }

  .privacy-card {
    flex-direction: column;
  }

  .concept-grid {
    grid-template-columns: 1fr;
  }

  .mockup-body-row {
    grid-template-columns: 1fr;
  }

  .stage-row-card {
    flex-direction: column;
    gap: 0.75rem;
  }

  .stage-status-col {
    width: auto;
  }

  .exit-cards-grid {
    grid-template-columns: 1fr;
  }
}
</style>
