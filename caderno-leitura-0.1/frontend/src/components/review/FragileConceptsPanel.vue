<script setup lang="ts">
/** F0.11.08 (spec 110): conceitos frágeis na Central de Revisão. Sem frágeis, não aparece. */
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { api } from '../../services/api'
import type { FragileConcept } from '../../types'

defineProps<{ busy?: boolean }>()
const emit = defineEmits<{ (e: 'practice'): void }>()

const items = ref<FragileConcept[]>([])
const loaded = ref(false)

const REASONS: Record<FragileConcept['reason'], string> = {
  card: 'cartão marcado como difícil',
  questions: 'perguntas dos estudos que o definem estão difíceis',
}

async function load() {
  try {
    items.value = await api.getFragileConcepts(5)
  } catch {
    items.value = []
  } finally {
    loaded.value = true
  }
}

defineExpose({ reload: load })
onMounted(load)
</script>

<template>
  <section v-if="loaded && items.length" class="fragile-panel" aria-labelledby="fragile-heading">
    <div class="fragile-head">
      <h2 id="fragile-heading" class="fragile-title">Conceitos frágeis</h2>
      <button type="button" class="quiet fragile-practice" :disabled="busy" @click="emit('practice')">
        Praticar conceitos frágeis
      </button>
    </div>
    <ul class="fragile-list">
      <li v-for="item in items" :key="item.key" class="fragile-item">
        <RouterLink :to="`/conceitos/${item.key}`" class="fragile-term">{{ item.term }}</RouterLink>
        <span class="fragile-reason">{{ REASONS[item.reason] }} · peso {{ Math.round(item.weight * 100) }}%</span>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.fragile-panel {
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 12px 16px;
  margin-top: 16px;
  background: var(--color-surface);
  color: var(--color-text);
}
.fragile-head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.fragile-title {
  margin: 0;
  font-size: 1.05rem;
}
.fragile-practice {
  min-height: 44px;
}
.fragile-list {
  list-style: none;
  margin: 8px 0 0;
  padding: 0;
  display: grid;
  gap: 4px;
}
.fragile-item {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px 10px;
  min-height: 44px;
}
.fragile-term {
  color: var(--color-link);
  font-weight: 600;
  min-height: 44px;
  display: inline-flex;
  align-items: center;
}
.fragile-reason {
  color: var(--color-muted);
  font-size: 0.9rem;
}
</style>
