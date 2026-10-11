<script setup lang="ts">
import { computed } from 'vue'
import type { AppearancePreferences } from '../appearance'
import ReadingSizeControl from './ReadingSizeControl.vue'
import FontPicker from './FontPicker.vue'
import ThemePreviewGrid from './ThemePreviewGrid.vue'
import type { CanonicalThemeId } from '../types/settings'
import { useSuperclassPhysics } from '../composables/useSuperclassPhysics'

const props = withDefaults(
  defineProps<{
    preferences: AppearancePreferences
    tab?: 'aparencia' | 'leitura' | 'all'
  }>(),
  {
    tab: 'all',
  }
)

const emit = defineEmits<{
  change: [patch: Partial<AppearancePreferences>]
}>()

const physics = useSuperclassPhysics()

const APPEARANCE_KEYS = new Set([
  'theme',
  'accent',
  'container',
  'superclass',
  'superclass-intensity',
])

const READING_KEYS = new Set([
  'font',
  'reader-size',
  'density',
  'align',
  'highlight',
  'library',
])

const allFields = window.cadernoAppearance?.fields ?? []

const visibleFields = computed(() => {
  if (props.tab === 'aparencia') {
    return allFields.filter(f => APPEARANCE_KEYS.has(f.key))
  }
  if (props.tab === 'leitura') {
    return allFields.filter(f => READING_KEYS.has(f.key))
  }
  return allFields
})

const groups = computed(() => [
  ...new Set(visibleFields.value.map(field => field.group)),
])

function change(event: Event, key: keyof AppearancePreferences) {
  const value = (event.target as HTMLSelectElement).value

  emit('change', {
    [key]: value,
  } as Partial<AppearancePreferences>)

  if (event.target) {
    physics.triggerHapticPulse(event.target as HTMLElement, 'step')
  }
}

function onThemeChange(newTheme: CanonicalThemeId) {
  emit('change', {
    theme: newTheme,
  } as Partial<AppearancePreferences>)
}

function ignored(key: keyof AppearancePreferences) {
  return props.preferences.theme === 'e-ink'
    && ['accent', 'superclass-intensity'].includes(key)
}
</script>

<template>
  <div class="appearance-controls">
    <fieldset
      v-for="group in groups"
      :key="group"
      class="appearance-group"
    >
      <legend>{{ group }}</legend>

      <div class="form-grid">
        <div
          v-for="field in visibleFields.filter(item => item.group === group)"
          :key="field.key"
          class="field"
          :class="{ 'field-full-width': field.key === 'theme' }"
        >
          <FontPicker
            v-if="field.key === 'font'"
            :value="preferences.font"
            @change="emit('change', { font: $event })"
          />

          <ReadingSizeControl
            v-else-if="field.key === 'reader-size'"
            id="pref-reader-size"
            :value="preferences['reader-size']"
            @change="emit('change', { 'reader-size': $event })"
          />

          <div v-else-if="field.key === 'theme'" class="theme-field-wrapper">
            <label :for="`pref-${field.key}`" class="field-label-prominent">
              {{ field.label }}
            </label>
            <ThemePreviewGrid
              :model-value="preferences.theme"
              :disabled="ignored('theme')"
              @update:model-value="onThemeChange"
            />
          </div>

          <template v-else>
            <label :for="`pref-${field.key}`">
              {{ field.label }}
            </label>

            <select
              :id="`pref-${field.key}`"
              :value="preferences[field.key]"
              :disabled="ignored(field.key)"
              :aria-describedby="
                ignored(field.key) ? 'eink-preferences-hint' : undefined
              "
              @change="change($event, field.key)"
            >
              <option
                v-for="[value, label] in field.options"
                :key="value"
                :value="value"
              >
                {{ label }}
              </option>
            </select>
          </template>
        </div>
      </div>
    </fieldset>
  </div>

  <p
    v-if="preferences.theme === 'e-ink' && (tab === 'all' || tab === 'aparencia')"
    id="eink-preferences-hint"
    class="notice"
  >
    O E-Ink usa preto e branco, sem animações.
    As escolhas suspensas voltam a valer ao trocar de tema.
  </p>

  <p v-if="tab === 'all' || tab === 'aparencia'" class="field-hint">
    A redução de movimento do sistema prevalece sobre as animações.
    As Superclasses controlam a física e elevação sem alterar cores ou fontes.
  </p>

  <p v-if="tab === 'all' || tab === 'leitura'" class="field-hint">
    A fonte selecionada aplica-se a toda a interface literária. O tamanho do texto e o espaçamento ajustam a leitura confortavelmente.
  </p>
</template>

<style scoped>
.field-full-width,
.theme-field-wrapper {
  grid-column: 1 / -1;
  width: 100%;
}

.field-label-prominent {
  display: block;
  font-weight: 600;
  margin-bottom: 0.35rem;
  color: var(--color-text);
  font-size: 0.95rem;
}
</style>