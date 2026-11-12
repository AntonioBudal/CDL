<script setup lang="ts">
/** F0.11.08 (spec 110): Memória do dia — um destaque ou estudo de 30+ dias atrás. Sem nada, não aparece. */
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { api } from '../../services/api'
import type { DailyMemory } from '../../types'
import { timeAgo } from '../../utils/timeAgo'

const memory = ref<DailyMemory | null>(null)

const when = computed(() => (memory.value ? timeAgo(memory.value.created_at) : ''))
const label = computed(() => {
  if (!memory.value) return ''
  if (memory.value.reason === 'anniversary') return `Neste dia, ${when.value}`
  if (memory.value.reason === 'month') return `Neste dia do mês, ${when.value}`
  return when.value.charAt(0).toUpperCase() + when.value.slice(1)
})

onMounted(async () => {
  try {
    memory.value = await api.getDailyMemory(-new Date().getTimezoneOffset())
  } catch {
    memory.value = null
  }
})
</script>

<template>
  <section v-if="memory" class="daily-memory" aria-labelledby="daily-memory-heading">
    <h2 id="daily-memory-heading" class="daily-memory-title">Memória do dia</h2>
    <p class="daily-memory-when">{{ label }} · {{ memory.kind === 'highlight' ? 'destaque' : 'estudo' }}</p>
    <blockquote class="daily-memory-text">{{ memory.text }}</blockquote>
    <p class="daily-memory-origin">
      <RouterLink :to="`/livros/${memory.book_id}/estudos/${memory.study_id}`" class="daily-memory-link">
        {{ memory.study_title }}
      </RouterLink>
      <span> · {{ memory.book_title }}</span>
    </p>
  </section>
</template>

<style scoped>
.daily-memory {
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 14px 16px;
  margin-bottom: 16px;
  background: var(--color-surface);
  color: var(--color-text);
}
.daily-memory-title {
  margin: 0;
  font-size: 1.05rem;
}
.daily-memory-when {
  margin: 2px 0 8px;
  color: var(--color-muted);
  font-size: 0.9rem;
}
.daily-memory-text {
  margin: 0;
  padding-left: 12px;
  border-left: 3px solid var(--color-border-strong);
  font-family: var(--font-serif, Georgia, serif);
  font-size: 1.1rem;
  line-height: 1.5;
  overflow-wrap: anywhere;
}
.daily-memory-origin {
  margin: 8px 0 0;
  color: var(--color-muted);
  font-size: 0.9rem;
}
.daily-memory-link {
  color: var(--color-link);
  display: inline-flex;
  align-items: center;
  min-height: 44px;
}
</style>
