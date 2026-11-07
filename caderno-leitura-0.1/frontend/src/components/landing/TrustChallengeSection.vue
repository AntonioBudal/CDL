<script setup lang="ts">
/**
 * Desafio F12 (F0.10.08, spec 101): em vez de pedir confiança, mostra o dado cru — os endereços que este
 * navegador contatou (Resource Timing) e a política de segurança enviada pelo servidor (cabeçalho CSP).
 */
import { onMounted, ref } from 'vue'
import { vReveal } from '../../composables/useReveal'
import {
  externalOrigins,
  groupEntriesByOrigin,
  summarizeCsp,
  type CspSummary,
  type OriginGroup,
} from '../../utils/networkAudit'

const supported = ref(true)
const groups = ref<OriginGroup[]>([])
const checkedAt = ref('')
const liveMessage = ref('')
const csp = ref<CspSummary | null>(null)
const cspError = ref(false)

const pageOrigin = typeof window !== 'undefined' ? window.location.origin : ''

const directiveHelp: Record<string, string> = {
  'default-src': 'regra geral para o que não tiver regra própria',
  'connect-src': 'para onde a página pode enviar ou buscar dados',
  'script-src': 'de onde a página pode carregar programas',
  'img-src': 'de onde a página pode carregar imagens',
  'frame-ancestors': 'quem pode embutir esta página',
}

function runCheck() {
  const perf = typeof performance !== 'undefined' ? performance : undefined
  if (!perf || typeof perf.getEntriesByType !== 'function') {
    supported.value = false
    liveMessage.value = 'Seu navegador não expõe esta lista; use o F12.'
    return
  }
  const entries = [...perf.getEntriesByType('navigation'), ...perf.getEntriesByType('resource')]
  groups.value = groupEntriesByOrigin(entries, pageOrigin)
  checkedAt.value = new Date().toLocaleTimeString('pt-BR')
  const external = externalOrigins(groups.value)
  liveMessage.value = external.length
    ? `Conferido: ${external.length} outro(s) endereço(s) além deste servidor.`
    : 'Conferido: todos os pedidos foram para este servidor.'
}

async function loadCsp() {
  cspError.value = false
  try {
    const response = await fetch(`${pageOrigin}/`, { method: 'HEAD', cache: 'no-store', credentials: 'same-origin' })
    csp.value = summarizeCsp(response.headers.get('Content-Security-Policy'))
  } catch {
    cspError.value = true
  }
}

onMounted(() => {
  const perf = typeof performance !== 'undefined' ? performance : undefined
  if (perf && typeof perf.setResourceTimingBufferSize === 'function') perf.setResourceTimingBufferSize(500)
  runCheck()
  void loadCsp()
})
</script>

<template>
  <section id="desafio-f12" class="trust-section" aria-labelledby="trust-heading">
    <h2 v-reveal id="trust-heading" class="section-title">Desafio F12: não acredite, confira</h2>
    <p v-reveal class="trust-lead">
      Qualquer página pode prometer privacidade. Esta pede que você confira no seu navegador, em um minuto.
    </p>

    <ol v-reveal class="trust-steps">
      <li>
        Abra as ferramentas do navegador: <kbd>F12</kbd> ou <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>I</kbd>
        (no Mac, <kbd>Cmd</kbd>+<kbd>Option</kbd>+<kbd>I</kbd>).
      </li>
      <li>Vá à aba <strong>Rede</strong> (Network) e recarregue a página.</li>
      <li>Confira a coluna de domínio: todos os pedidos vão para o mesmo endereço da barra.</li>
    </ol>

    <div v-reveal class="trust-panel" role="region" aria-labelledby="trust-panel-heading">
      <div class="trust-panel-head">
        <h3 id="trust-panel-heading" class="trust-panel-title">Conferir nesta página</h3>
        <button type="button" class="quiet trust-recheck" @click="runCheck">Conferir de novo</button>
      </div>

      <p v-if="!supported" class="trust-muted">Seu navegador não expõe esta lista; use o F12.</p>
      <template v-else>
        <p class="trust-muted">
          Endereços que este navegador contatou desde que a página abriu<span v-if="checkedAt"> (às {{ checkedAt }})</span>:
        </p>
        <ul class="trust-origins">
          <li v-for="group in groups" :key="group.origin" class="trust-origin">
            <code class="trust-origin-name">{{ group.origin }}</code>
            <span class="trust-origin-badge" :class="{ 'is-external': !group.sameOrigin }">
              {{ group.sameOrigin ? 'este servidor' : 'outro endereço' }}
            </span>
            <span class="trust-muted">{{ group.count === 1 ? '1 pedido' : `${group.count} pedidos` }}</span>
          </li>
        </ul>
      </template>
      <p class="trust-live" role="status" aria-live="polite">{{ liveMessage }}</p>

      <h4 class="trust-csp-title">Política de segurança enviada pelo servidor (CSP)</h4>
      <p v-if="cspError" class="trust-muted">Não foi possível ler a política agora.</p>
      <p v-else-if="csp && !csp.present" class="trust-muted">
        Este servidor não enviou o cabeçalho Content-Security-Policy (acontece no modo de desenvolvimento).
      </p>
      <dl v-else-if="csp" class="trust-csp">
        <template v-for="(value, name) in csp.directives" :key="name">
          <dt><code>{{ name }}</code> <span class="trust-muted">— {{ directiveHelp[name] }}</span></dt>
          <dd><code>{{ value }}</code></dd>
        </template>
      </dl>

      <p class="trust-note">
        A lista mostra o que este navegador registrou. Extensões instaladas podem fazer pedidos próprios. Se o login
        com Google estiver ativado, a tela de entrada fala com o Google; esta página, não.
      </p>
    </div>
  </section>
</template>

<style scoped>
.trust-section {
  padding-block: clamp(2.5rem, 6vw, 4.5rem);
}

.section-title {
  font-family: var(--font-reading, "Caderno EB Garamond", serif);
  font-size: clamp(1.75rem, 3vw, 2.4rem);
  font-weight: 600;
  line-height: 1.2;
  margin: 0 0 0.75rem 0;
  color: var(--color-text);
}

.trust-lead {
  margin: 0 0 1.25rem;
  font-size: 1.05rem;
  line-height: 1.55;
  color: var(--color-text);
  max-width: 46rem;
}

.trust-steps {
  margin: 0 0 1.5rem;
  padding-left: 1.4rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  line-height: 1.55;
  color: var(--color-text);
}

kbd {
  font-family: var(--font-mono, ui-monospace, monospace);
  font-size: 0.85em;
  padding: 0.05rem 0.4rem;
  border: 1px solid var(--color-border-strong, var(--color-border));
  border-bottom-width: 2px;
  border-radius: 4px;
  background: var(--color-surface);
  color: var(--color-text);
}

.trust-panel {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1.25rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 14px;
  min-width: 0;
}

.trust-panel-head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.trust-panel-title,
.trust-csp-title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--color-text);
}

.trust-csp-title {
  margin-top: 0.5rem;
  font-size: 0.95rem;
}

.trust-recheck {
  --quiet-border: var(--color-border-strong, var(--color-border));
  min-height: 44px;
}

.trust-muted {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-muted);
}

.trust-origins {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.trust-origin {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem 0.6rem;
  min-width: 0;
}

.trust-origin-name {
  font-family: var(--font-mono, ui-monospace, monospace);
  font-size: 0.875rem;
  overflow-wrap: anywhere;
  color: var(--color-text);
}

.trust-origin-badge {
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.15rem 0.55rem;
  border-radius: 999px;
  border: 1px solid var(--color-border);
  background: var(--color-page);
  color: var(--color-text);
}

.trust-origin-badge.is-external {
  border-style: dashed;
  border-color: var(--color-border-strong, var(--color-border));
}

.trust-live {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--color-text);
}

.trust-csp {
  margin: 0;
  display: grid;
  gap: 0.25rem 0;
  min-width: 0;
}

.trust-csp dt {
  font-size: 0.875rem;
  color: var(--color-text);
  margin-top: 0.35rem;
}

.trust-csp dd {
  margin: 0;
  min-width: 0;
}

.trust-csp code {
  font-family: var(--font-mono, ui-monospace, monospace);
  font-size: 0.8125rem;
  overflow-wrap: anywhere;
  color: var(--color-text);
}

.trust-note {
  margin: 0.25rem 0 0;
  font-size: 0.875rem;
  line-height: 1.5;
  color: var(--color-muted);
}
</style>
