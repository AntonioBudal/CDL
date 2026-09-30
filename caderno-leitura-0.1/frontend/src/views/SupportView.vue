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
        <p>Carregando canais de contribuição…</p>
      </div>

      <div v-else-if="error" class="support-state error">
        <p>{{ error }}</p>
        <button type="button" class="btn-retry" @click="fetchSupportData">Tentar novamente</button>
      </div>

      <div v-else class="support-content">
        <!-- Propósito e Transparência -->
        <section class="support-card info-card" aria-labelledby="heading-purpose">
          <h2 id="heading-purpose" class="card-title">Por que apoiar?</h2>
          <p class="card-description">
            O projeto é mantido voluntariamente. As contribuições financeiras são 100% facultativas e ajudam a custear
            a infraestrutura de servidores, custos de domínio, tráfego de rede e a continuidade do desenvolvimento aberto.
          </p>
          <p v-if="supportData.custom_message" class="custom-note">
            {{ supportData.custom_message }}
          </p>
        </section>

        <!-- Seção PIX -->
        <section
          v-if="supportData.pix_enabled && supportData.pix_key"
          class="support-card pix-card"
          aria-labelledby="heading-pix"
        >
          <div class="card-header-line">
            <h2 id="heading-pix" class="card-title">Contribuição via PIX</h2>
            <span class="badge-direct">Transferência Direta</span>
          </div>

          <p class="card-description">
            Você pode transferir qualquer quantia através do aplicativo do seu banco lendo o QR Code ou copiando a chave abaixo.
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

        <!-- Seção Meio Alternativo (Google Pay / Link Externo) -->
        <section
          v-if="supportData.alternative_enabled && supportData.alternative_url"
          class="support-card alternative-card"
          aria-labelledby="heading-alt"
        >
          <div class="card-header-line">
            <h2 id="heading-alt" class="card-title">
              {{ supportData.alternative_label || 'Pagamento Online / Link Externo' }}
            </h2>
          </div>
          <p class="card-description">
            Contribua de forma protegida utilizando carteira digital ou página externa de doação.
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

        <!-- Apoio Comunitário (Sempre presente ou Fallback) -->
        <section class="support-card community-card" aria-labelledby="heading-community">
          <h2 id="heading-community" class="card-title">Outras formas de apoiar</h2>
          <p class="card-description">
            Se não puder ou não desejar contribuir financeiramente, você fortalece o projeto:
          </p>
          <ul class="community-list">
            <li>Recomendando o Leitorum para colegas, grupos de estudos e leitores.</li>
            <li>Enviando sugestões de recursos, relatos de problemas e ideias de melhoria.</li>
            <li>Colaborando com documentação e revisão no repositório de código aberto.</li>
          </ul>
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
  color: var(--text, #111827);
  margin: 0 0 0.5rem;
  letter-spacing: -0.02em;
}

.support-lead {
  font-size: 1.05rem;
  color: var(--text-muted, #4b5563);
  line-height: 1.6;
  margin: 0;
}

.support-state {
  text-align: center;
  padding: 2.5rem;
  border-radius: 8px;
  border: 1px dashed var(--border, #d1d5db);
  color: var(--text-muted, #6b7280);
}

.support-state.error {
  border-color: var(--danger, #dc2626);
  color: var(--danger, #dc2626);
}

.btn-retry {
  margin-top: 1rem;
  padding: 0.6rem 1.2rem;
  border-radius: 6px;
  border: 1px solid var(--border, #d1d5db);
  background: var(--card-bg, #ffffff);
  color: var(--text, #111827);
  cursor: pointer;
  min-height: 44px;
}

.support-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.support-card {
  background: var(--card-bg, #ffffff);
  border: 1px solid var(--border, #e5e7eb);
  border-radius: 10px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
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
  color: var(--text, #111827);
  margin: 0;
}

.badge-direct {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 0.2rem 0.6rem;
  border-radius: 9999px;
  background: var(--primary-light, #e0e7ff);
  color: var(--primary, #4338ca);
}

.card-description {
  font-size: 0.95rem;
  color: var(--text-muted, #4b5563);
  line-height: 1.55;
  margin: 0 0 1rem;
}

.custom-note {
  font-size: 0.9rem;
  font-style: italic;
  padding: 0.75rem 1rem;
  border-left: 3px solid var(--primary, #4338ca);
  background: var(--bg-muted, #f3f4f6);
  color: var(--text, #374151);
  border-radius: 0 6px 6px 0;
  margin: 0;
}

.pix-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
  font-size: 0.9rem;
  padding: 0.5rem 0.75rem;
  background: var(--bg-muted, #f9fafb);
  border-radius: 6px;
}

.meta-label {
  color: var(--text-muted, #6b7280);
}

.meta-value {
  font-weight: 600;
  color: var(--text, #111827);
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
  border: 1px solid var(--border, #e5e7eb);
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
  background: var(--bg-muted, #f9fafb);
  border: 1px solid var(--border, #d1d5db);
  border-radius: 6px;
  color: var(--text, #111827);
}

.pix-input:focus {
  outline: 2px solid var(--primary, #4338ca);
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
  background: var(--primary, #4338ca);
  color: #ffffff;
  border: none;
  cursor: pointer;
  white-space: nowrap;
  transition: background-color 0.15s ease;
}

.btn-copy-pix:hover {
  filter: brightness(0.95);
}

.btn-copy-pix.success {
  background: #059669;
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
  background: var(--primary, #4338ca);
  color: #ffffff;
  text-decoration: none;
  transition: filter 0.15s ease;
}

.btn-alt-link:hover {
  filter: brightness(0.95);
}

.community-list {
  margin: 0;
  padding-left: 1.25rem;
  color: var(--text-muted, #4b5563);
  line-height: 1.6;
}

.community-list li {
  margin-bottom: 0.4rem;
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
