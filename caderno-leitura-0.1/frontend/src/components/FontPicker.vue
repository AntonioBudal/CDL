<script setup lang="ts">
import { computed, ref } from 'vue'
import type { AppearancePreferences } from '../appearance'

const props = defineProps<{
  value: AppearancePreferences['font']
}>()

const emit = defineEmits<{
  change: [value: AppearancePreferences['font']]
}>()

const query = ref('')
const options = window.cadernoFontCatalog.options

const normalize = (value: string) => value
  .normalize('NFD')
  .replace(/[\u0300-\u036f]/g, '')
  .toLowerCase()
  .trim()

const matches = computed(() => options.filter(([id, name]) =>
  normalize(`${name} ${id}`).includes(normalize(query.value))
))

const currentName = computed(() =>
  options.find(([id]) => id === props.value)?.[1] ?? ''
)
</script>

<template>
  <div class="font-picker">
    <label for="font-search">Pesquisar fonte de leitura</label>

    <input
      id="font-search"
      v-model="query"
      type="search"
      placeholder="Ex.: Lora, Inter, Mono…"
      autocomplete="off"
      :spellcheck="false"
      aria-controls="font-results"
    />

    <p class="field-hint font-result-count" role="status">
      {{ matches.length }} resultado(s). Atual: {{ currentName }}.
    </p>

    <fieldset
      id="font-results"
      class="font-results"
      aria-label="Fontes de leitura"
    >
      <label
        v-for="[id, name] in matches"
        :key="id"
        class="font-option"
        :class="{ selected: value === id }"
      >
        <input
          type="radio"
          name="reading-font"
          :value="id"
          :checked="value === id"
          @change="emit('change', id)"
        />
        <span>{{ name }}</span>
      </label>

      <p v-if="!matches.length" class="muted">
        Nenhuma fonte encontrada.
      </p>
    </fieldset>
  </div>
</template>