<script setup lang="ts">
/**
 * F0.12.02 (spec 115): "Publicar na web" — escolha explícita, à parte da visibilidade. Diz exatamente o que sai e o que
 * não sai; publicar dá o endereço /compartilhado/<id>; despublicar tira do ar na hora.
 */
import { computed, ref, watch } from 'vue'
import { api, errorMessage } from '../../services/api'

const props = defineProps<{ studyId: number; publishedAt?: string | null }>()
const emit = defineEmits<{ (e: 'changed', publishedAt: string | null): void }>()

const publishedAt = ref<string | null>(props.publishedAt ?? null)
const busy = ref(false)
const error = ref('')
const message = ref('')

watch(() => props.publishedAt, (value) => { publishedAt.value = value ?? null })

const path = computed(() => `/compartilhado/${props.studyId}`)
const url = computed(() => `${window.location.origin}${path.value}`)

async function publish() {
  busy.value = true
  error.value = ''
  try {
    const res = await api.publishStudy(props.studyId)
    publishedAt.value = res.published_at
    message.value = 'Estudo publicado na web.'
    emit('changed', res.published_at)
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    busy.value = false
  }
}

async function unpublish() {
  busy.value = true
  error.value = ''
  try {
    await api.unpublishStudy(props.studyId)
    publishedAt.value = null
    message.value = 'Estudo despublicado: a página saiu do ar.'
    emit('changed', null)
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    busy.value = false
  }
}

async function copy() {
  try {
    await navigator.clipboard.writeText(url.value)
    message.value = 'Link copiado.'
  } catch {
    message.value = 'Não consegui copiar; selecione o endereço e copie à mão.'
  }
}
</script>

<template>
  <section class="publish-card" aria-labelledby="publish-heading">
    <h3 id="publish-heading" class="publish-title">Publicar na web</h3>
    <p class="publish-muted">
      Cria uma página pública, que qualquer pessoa pode abrir sem conta e que buscadores podem encontrar. É separado da
      visibilidade acima.
    </p>
    <ul class="publish-list">
      <li><strong>Sai:</strong> o título, as quatro seções (Resumo, Explicação, Conceitos, Referências), a referência do
        livro e o seu nome de exibição.</li>
      <li><strong>Não sai:</strong> notas pessoais, fichamento da fonte, destaques, e-mail e nome de usuário. Menções a
        estudos não publicados aparecem só como texto.</li>
    </ul>

    <template v-if="publishedAt">
      <p class="publish-status">Publicado. Endereço:</p>
      <code class="publish-url">{{ url }}</code>
      <div class="publish-actions">
        <button type="button" class="quiet publish-button" :disabled="busy" @click="copy">Copiar link</button>
        <a class="button quiet publish-button" :href="path" target="_blank" rel="noopener">Abrir</a>
        <button type="button" class="quiet publish-button" :disabled="busy" @click="unpublish">Despublicar</button>
      </div>
    </template>
    <div v-else class="publish-actions">
      <button type="button" class="quiet publish-button" :disabled="busy" @click="publish">Publicar na web</button>
    </div>

    <p class="publish-muted">
      A página só é alcançável fora da sua rede se o Leitorum estiver exposto na internet (domínio próprio ou Tailscale
      Funnel).
    </p>
    <p v-if="error" class="publish-error" role="alert">{{ error }}</p>
    <p class="publish-muted" role="status" aria-live="polite">{{ message }}</p>
  </section>
</template>

<style scoped>
.publish-card {
  border-top: 1px solid var(--color-border);
  margin-top: 16px;
  padding-top: 12px;
  color: var(--color-text);
  min-width: 0;
}
.publish-title {
  margin: 0 0 4px;
  font-size: 1rem;
}
.publish-muted {
  color: var(--color-muted);
  font-size: 0.9rem;
  margin: 6px 0;
}
.publish-list {
  margin: 6px 0;
  padding-left: 1.2rem;
  font-size: 0.9rem;
}
.publish-status {
  margin: 8px 0 2px;
  font-weight: 600;
}
.publish-url {
  display: block;
  overflow-wrap: anywhere;
  word-break: break-all;
}
.publish-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 8px 0;
}
.publish-button {
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  white-space: normal;
}
.publish-error {
  color: var(--color-danger-text);
}
</style>
