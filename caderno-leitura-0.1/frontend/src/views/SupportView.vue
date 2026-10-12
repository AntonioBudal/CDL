<script setup lang="ts">
import { onMounted, ref } from 'vue'
import Icon from '../components/ui/Icon.vue'
import { getSupportInfo } from '../services/api'
import type { SupportPublicInfo } from '../types'

const loading = ref(true)
const error = ref('')
const supportData = ref<SupportPublicInfo>({
  pix_enabled: false,
  pix_key: null,
  pix_recipient_name: null,
  pix_qr_code_url: null,
  alternative_enabled: false,
  alternative_label: null,
  alternative_url: null,
  custom_message: null,
  has_any_method_active: false,
})

const copied = ref(false)
const copyFeedbackTimer = ref<number | null>(null)
const pixInputRef = ref<HTMLInputElement | null>(null)

async function fetchSupportData() {
  loading.value = true
  error.value = ''
  try {
    const data = await getSupportInfo()
    supportData.value = data
  } catch (err: unknown) {
    error.value = err instanceof Error ? err.message : 'Falha ao carregar opções de apoio.'
  } finally {
    loading.value = false
  }
}

async function handleCopyPix() {
  if (!supportData.value.pix_key) return

  const keyToCopy = supportData.value.pix_key

  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(keyToCopy)
    } else {
      fallbackCopyText(keyToCopy)
    }
    triggerCopyFeedback()
  } catch {
    fallbackCopyText(keyToCopy)
    triggerCopyFeedback()
  }
}

function fallbackCopyText(text: string) {
  if (pixInputRef.value) {
    pixInputRef.value.select()
    pixInputRef.value.setSelectionRange(0, 99999)
    try {
      document.execCommand('copy')
    } catch {
      // Falha silenciosa de execCommand
    }
  } else if (typeof document !== 'undefined') {
    const el = document.createElement('textarea')
    el.value = text
    document.body.appendChild(el)
    el.select()
    try {
      document.execCommand('copy')
    } catch {
      // Falha silenciosa de execCommand
    }
    document.body.removeChild(el)
  }
}

function triggerCopyFeedback() {
  copied.value = true
  if (copyFeedbackTimer.value) {
    window.clearTimeout(copyFeedbackTimer.value)
  }
  copyFeedbackTimer.value = window.setTimeout(() => {
    copied.value = false
  }, 3000)
}

onMounted(() => {
  fetchSupportData()
})
</script>

<template>
  <div class="support-page" role="region" aria-label="Apoie o Leitorum">
    <div class="support-container">
      <header class="support-header">
        <h1 class="support-title">Apoie o Leitorum</h1>
        <p class="support-lead">
          O Leitorum é uma plataforma independente, gratuita e de código aberto voltada à leitura atenta e aos estudos.
        </p>
      </header>

      <div v-if="loading" class="support-state loading">
        <p>Carregando opções de apoio…</p>
      </div>

      <div v-else-if="error" class="support-state error">
        <p>{{ error }}</p>
        <button type="button" class="btn-retry" @click="fetchSupportData">Tentar novamente</button>
      </div>

      <div v-else class="support-content">
        <!-- Propósito e Transparência -->
        <section class="support-card info-card" aria-labelledby="heading-purpose">
          <h2 id="heading-purpose" class="card-title">Desenvolvimento Aberto e Independente</h2>
          <p class="card-description">
            O Leitorum é desenvolvido de forma independente como software livre. A prioridade fundamental nesta fase é
            consolidar uma ferramenta sólida, privativa e sem distrações para leitura reflexiva, organização de notas e estudos contínuos.
          </p>
          <p v-if="supportData.custom_message" class="custom-note">
            {{ supportData.custom_message }}
          </p>
        </section>

        <!-- Apoio Comunitário e Técnico (Principal) -->
        <section class="support-card community-card" aria-labelledby="heading-community">
          <h2 id="heading-community" class="card-title">Como apoiar o projeto</h2>
          <p class="card-description">
            Nesta etapa, as formas mais valiosas de apoio são o uso real, o reporte de problemas e a colaboração técnica:
          </p>
          <ul class="community-list">
            <li><strong>Uso no dia a dia:</strong> Integre o Caderno às suas leituras habituais e exercícios de estudo.</li>
            <li><strong>Relato de falhas:</strong> Reporte comportamentos inesperados, problemas visuais ou inconsistências de navegação.</li>
            <li><strong>Sugestões de melhoria:</strong> Compartilhe ideias para aperfeiçoar a experiência de organização e revisão.</li>
            <li><strong>Contribuições no código:</strong> Participe com revisão de código, melhorias de acessibilidade e testes no repositório aberto.</li>
          </ul>

          <div class="repo-action-box">
            <a
              href="https://github.com/AntonioBudal/CDL"
              target="_blank"
              rel="noopener noreferrer"
              class="btn-github-link"
              aria-label="Acessar o repositório de código aberto no GitHub em nova aba"
            >
              <span>Repositório Oficial no GitHub</span>
              <Icon name="external-link" :size="18" />
            </a>
          </div>
        </section>

        <!-- Seção PIX (Exibida somente se método ativo e configurado) -->
        <section
          v-if="supportData.has_any_method_active && supportData.pix_enabled && supportData.pix_key"
          class="support-card pix-card"
          aria-labelledby="heading-pix"
        >
          <div class="card-header-line">
            <h2 id="heading-pix" class="card-title">Contribuição via PIX</h2>
            <span class="badge-direct">Transferência Direta</span>
          </div>

          <p class="card-description">
            Se desejar contribuir financeiramente com os custos de infraestrutura e hospedagem, utilize a chave abaixo:
          </p>

          <div v-if="supportData.pix_recipient_name" class="pix-meta">
            <span class="meta-label">Titular / Beneficiário:</span>
            <span class="meta-value">{{ supportData.pix_recipient_name }}</span>
          </div>

          <div v-if="supportData.pix_qr_code_url" class="pix-qr-container">
            <img
              :src="supportData.pix_qr_code_url"
              alt="QR Code para pagamento via PIX"
              class="pix-qr-image"
            />
          </div>

          <div class="pix-copy-box">
            <label for="pix-key-input" class="sr-only">Chave PIX</label>
            <input
              id="pix-key-input"
              ref="pixInputRef"
              type="text"
              class="pix-input"
              :value="supportData.pix_key"
              readonly
              aria-label="Chave PIX para transferência"
            />
            <button
              type="button"
              class="btn-copy-pix"
              :class="{ success: copied }"
              :aria-label="copied ? 'Chave PIX copiada para a área de transferência' : 'Copiar chave PIX'"
              @click="handleCopyPix"
            >
              <Icon :name="copied ? 'check' : 'copy'" :size="18" />
              <span>{{ copied ? 'Chave copiada' : 'Copiar chave PIX' }}</span>
            </button>
          </div>
          <div aria-live="polite" class="copy-alert-sr sr-only">
            {{ copied ? 'Chave PIX copiada para a área de transferência.' : '' }}
          </div>
        </section>

        <!-- Seção Meio Alternativo (Exibida somente se método ativo e configurado) -->
        <section
          v-if="supportData.has_any_method_active && supportData.alternative_enabled && supportData.alternative_url"
          class="support-card alternative-card"
          aria-labelledby="heading-alt"
        >
          <div class="card-header-line">
            <h2 id="heading-alt" class="card-title">
              {{ supportData.alternative_label || 'Pagamento Online / Link Externo' }}
            </h2>
          </div>
          <p class="card-description">
            Contribuição facultativa através de página externa segura.
          </p>
          <div class="alt-action-box">
            <a
              :href="supportData.alternative_url"
              target="_blank"
              rel="noopener noreferrer"
              class="btn-alt-link"
              aria-label="Abrir link externo de pagamento em nova aba"
            >
              <span>{{ supportData.alternative_label || 'Acessar página de contribuição' }}</span>
              <Icon name="external-link" :size="18" />
            </a>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<style scoped>
.support-page {
  display: flex;
  justify-content: center;
  padding: 2.5rem 1rem 4rem;
  min-height: calc(100vh - 120px);
  background-color: var(--color-page);
  color: var(--color-text);
}

.support-container {
  width: 100%;
  max-width: 680px;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.support-header {
  text-align: center;
  margin-bottom: 0.5rem;
}

.support-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--color-text);
  margin: 0 0 0.5rem;
  letter-spacing: -0.02em;
}

.support-lead {
  font-size: 1.05rem;
  color: var(--color-muted);
  line-height: 1.6;
  margin: 0;
}

.support-state {
  text-align: center;
  padding: 2.5rem;
  border-radius: var(--radius-card, 8px);
  border: 1px dashed var(--color-border);
  color: var(--color-muted);
}

.support-state.error {
  border-color: var(--color-danger, #dc2626);
  color: var(--color-danger, #dc2626);
}

.btn-retry {
  margin-top: 1rem;
  padding: 0.6rem 1.2rem;
  border-radius: var(--radius-control, 6px);
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text);
  cursor: pointer;
  min-height: 44px;
}

.support-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.support-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-card, 10px);
  padding: 1.5rem;
  box-shadow: var(--shadow-sm, 0 1px 3px rgba(0, 0, 0, 0.04));
}

.card-header-line {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.card-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.badge-direct {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 0.2rem 0.6rem;
  border-radius: 9999px;
  background: var(--color-surface-soft);
  color: var(--color-accent);
  border: 1px solid var(--color-border);
}

.card-description {
  font-size: 0.95rem;
  color: var(--color-muted);
  line-height: 1.55;
  margin: 0 0 1rem;
}

.custom-note {
  font-size: 0.9rem;
  font-style: italic;
  padding: 0.75rem 1rem;
  border-left: 3px solid var(--color-accent);
  background: var(--color-surface-soft);
  color: var(--color-text);
  border-radius: 0 6px 6px 0;
  margin: 0;
}

.repo-action-box {
  margin-top: 1.25rem;
  display: flex;
}

.btn-github-link {
  min-height: 44px;
  padding: 0 1.25rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  font-size: 0.95rem;
  font-weight: 600;
  border-radius: var(--radius-control, 6px);
  background-color: var(--color-surface-soft);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  text-decoration: none;
  transition: all 0.15s ease;
}

.btn-github-link:hover {
  background-color: var(--color-surface-hover);
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.btn-github-link:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

.pix-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
  font-size: 0.9rem;
  padding: 0.5rem 0.75rem;
  background: var(--color-surface-soft);
  border-radius: 6px;
  border: 1px solid var(--color-border);
}

.meta-label {
  color: var(--color-muted);
}

.meta-value {
  font-weight: 600;
  color: var(--color-text);
}

.pix-qr-container {
  display: flex;
  justify-content: center;
  margin-bottom: 1.25rem;
}

.pix-qr-image {
  max-width: 220px;
  width: 100%;
  height: auto;
  border-radius: 8px;
  border: 1px solid var(--color-border);
  padding: 0.5rem;
  background: #ffffff;
}

.pix-copy-box {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.pix-input {
  flex: 1;
  min-height: 44px;
  padding: 0 0.85rem;
  font-family: monospace;
  font-size: 0.9rem;
  background: var(--color-surface-soft);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  color: var(--color-text);
}

.pix-input:focus {
  outline: 2px solid var(--color-accent);
  outline-offset: 1px;
}

.btn-copy-pix {
  min-height: 44px;
  padding: 0 1.25rem;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  font-weight: 600;
  border-radius: 6px;
  background: var(--color-accent);
  color: var(--color-on-accent, #ffffff);
  border: none;
  cursor: pointer;
  white-space: nowrap;
  transition: opacity 0.15s ease;
}

.btn-copy-pix:hover {
  opacity: 0.9;
}

.btn-copy-pix.success {
  background: var(--color-accent);
}

.alt-action-box {
  display: flex;
  margin-top: 0.5rem;
}

.btn-alt-link {
  min-height: 44px;
  padding: 0 1.5rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-size: 0.95rem;
  font-weight: 600;
  border-radius: 6px;
  background: var(--color-accent);
  color: var(--color-on-accent, #ffffff);
  text-decoration: none;
  transition: opacity 0.15s ease;
}

.btn-alt-link:hover {
  opacity: 0.9;
}

.community-list {
  margin: 0;
  padding-left: 1.25rem;
  color: var(--color-text);
  line-height: 1.6;
}

.community-list li {
  margin-bottom: 0.6rem;
}

.sr-only {
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

@media (max-width: 640px) {
  .pix-copy-box {
    flex-direction: column;
    align-items: stretch;
  }

  .btn-copy-pix {
    justify-content: center;
  }
}
</style>
