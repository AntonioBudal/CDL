<script setup lang="ts">
/** F0.12.02 (spec 115): "Publicados na web" em Ajustes — todos os estudos publicados, com despublicar. */
import { onMounted, ref } from 'vue'
import { api, errorMessage } from '../../services/api'
import type { PublishedStudyItem } from '../../types'

const items = ref<PublishedStudyItem[]>([])
const loading = ref(true)
const busy = ref(false)
const error = ref('')
const message = ref('')

async function load() {
  loading.value = true
  try {
    items.value = await api.listPublishedStudies()
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    loading.value = false
  }
}

async function unpublish(item: PublishedStudyItem) {
  busy.value = true
  error.value = ''
  try {
    await api.unpublishStudy(item.study_id)
    message.value = `"${item.title}" despublicado.`
    await load()
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    busy.value = false
  }
}

onMounted(load)
</script>

<template>
  <section class="published-card" aria-labelledby="published-heading">
    <h3 id="published-heading" class="published-title">Publicados na web</h3>
    <p class="published-muted">Estudos com página pública em <code>/compartilhado/…</code>. Despublicar tira a página do ar na hora.</p>
    <p v-if="loading" class="published-muted" role="status">Carregando…</p>
    <p v-else-if="!items.length" class="published-muted">Nenhum estudo publicado. Publique pelo botão de compartilhar de um estudo.</p>
    <ul v-else class="published-list">
      <li v-for="item in items" :key="item.study_id" class="published-item">
        <span class="published-text">
          <a :href="item.path" target="_blank" rel="noopener" class="published-link">{{ item.title }}</a>
          <span class="published-muted"> · {{ item.book_title }}<template v-if="!item.available"> · fora do ar (lixeira ou livro excluído)</template></span>
        </span>
        <button type="button" class="quiet published-button" :disabled="busy" @click="unpublish(item)">Despublicar</button>
      </li>
    </ul>
    <p v-if="error" class="published-error" role="alert">{{ error }}</p>
    <p class="published-muted" role="status" aria-live="polite">{{ message }}</p>
  </section>
</template>

<style scoped>
.published-card {
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 14px 16px;
  margin-top: 20px;
  background: var(--color-surface);
  color: var(--color-text);
  min-width: 0;
}
.published-title {
  margin: 0 0 4px;
  font-size: 1.1rem;
}
.published-muted {
  color: var(--color-muted);
  font-size: 0.9rem;
  margin: 4px 0;
}
.published-list {
  list-style: none;
  margin: 8px 0;
  padding: 0;
  display: grid;
  gap: 6px;
}
.published-item {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 6px 12px;
  min-width: 0;
}
.published-text {
  min-width: 0;
  overflow-wrap: anywhere;
}
.published-link {
  color: var(--color-link);
  font-weight: 600;
}
.published-button {
  min-height: 44px;
}
.published-error {
  color: var(--color-danger-text);
}
</style>
