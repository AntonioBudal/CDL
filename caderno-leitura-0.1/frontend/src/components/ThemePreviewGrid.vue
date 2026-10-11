<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { CANONICAL_THEME_PREVIEWS } from '../types/settings'
import type { CanonicalThemeId } from '../types/settings'
import Icon from './ui/Icon.vue'

const props = withDefaults(
  defineProps<{
    modelValue?: CanonicalThemeId | string
    disabled?: boolean
  }>(),
  {
    modelValue: 'papel-fosco',
    disabled: false,
  }
)

const emit = defineEmits<{
  'update:modelValue': [value: CanonicalThemeId]
  change: [value: CanonicalThemeId]
}>()

const buttonRefs = ref<HTMLElement[]>([])

function selectTheme(themeId: CanonicalThemeId) {
  if (props.disabled || props.modelValue === themeId) return
  emit('update:modelValue', themeId)
  emit('change', themeId)
}

function focusTheme(index: number) {
  const nextTheme = CANONICAL_THEME_PREVIEWS[index]
  if (!nextTheme) return
  selectTheme(nextTheme.id)
  nextTick(() => {
    buttonRefs.value[index]?.focus()
  })
}

function onKeydown(event: KeyboardEvent, currentIndex: number) {
  if (props.disabled) return

  const total = CANONICAL_THEME_PREVIEWS.length
  let targetIndex = -1

  switch (event.key) {
    case 'ArrowRight':
    case 'ArrowDown':
      event.preventDefault()
      targetIndex = (currentIndex + 1) % total
      break
    case 'ArrowLeft':
    case 'ArrowUp':
      event.preventDefault()
      targetIndex = (currentIndex - 1 + total) % total
      break
    case 'Home':
      event.preventDefault()
      targetIndex = 0
      break
    case 'End':
      event.preventDefault()
      targetIndex = total - 1
      break
    case ' ':
    case 'Enter':
      event.preventDefault()
      selectTheme(CANONICAL_THEME_PREVIEWS[currentIndex].id)
      return
    default:
      return
  }

  if (targetIndex >= 0) {
    focusTheme(targetIndex)
  }
}
</script>

<template>
  <div
    class="theme-preview-grid"
    role="radiogroup"
    aria-label="Seleção de temas visuais do Caderno de Leitura"
  >
    <button
      v-for="(theme, index) in CANONICAL_THEME_PREVIEWS"
      :key="theme.id"
      :ref="(el) => { if (el) buttonRefs[index] = el as HTMLElement }"
      type="button"
      role="radio"
      :aria-checked="modelValue === theme.id"
      :tabindex="modelValue === theme.id ? 0 : -1"
      :disabled="disabled"
      class="theme-preview-card"
      :class="{
        'is-active': modelValue === theme.id,
        'is-eink': theme.id === 'e-ink',
      }"
      @click="selectTheme(theme.id)"
      @keydown="onKeydown($event, index)"
    >
      <!-- Box visual estilo Windows 11 com as cores da paleta -->
      <div
        class="theme-color-box"
        :style="{
          backgroundColor: theme.colors.page,
          borderColor: theme.colors.border,
        }"
      >
        <div
          class="theme-window-mockup"
          :style="{
            backgroundColor: theme.colors.surface,
            borderColor: theme.colors.border,
          }"
        >
          <div
            class="mockup-header"
            :style="{ backgroundColor: theme.colors.page }"
          >
            <span
              class="mockup-accent-pill"
              :style="{ backgroundColor: theme.colors.accent }"
            ></span>
          </div>
          <div class="mockup-body">
            <span
              class="mockup-line"
              :style="{ backgroundColor: theme.colors.text }"
            ></span>
            <span
              class="mockup-line short"
              :style="{ backgroundColor: theme.colors.text }"
            ></span>
          </div>
        </div>
      </div>

      <!-- Rótulo do tema e indicador de ativo -->
      <div class="theme-card-footer">
        <span class="theme-name">{{ theme.label }}</span>
        <span
          v-if="modelValue === theme.id"
          class="theme-active-indicator"
          aria-hidden="true"
        >
          <Icon name="check" :size="14" stroke-width="2.5" />
        </span>
      </div>
    </button>
  </div>
</template>

<style scoped>
.theme-preview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: calc(var(--space-unit, 1rem) * 0.75);
  margin-top: calc(var(--space-unit, 1rem) * 0.5);
  margin-bottom: calc(var(--space-unit, 1rem) * 0.75);
}

.theme-preview-card {
  display: flex;
  flex-direction: column;
  padding: 0.5rem;
  border-radius: var(--radius-md, 8px);
  border: 1.5px solid var(--color-border);
  background-color: var(--color-surface);
  color: var(--color-text);
  cursor: pointer;
  text-align: left;
  transition: border-color 0.15s ease, transform 0.15s ease, box-shadow 0.15s ease;
  min-height: 44px;
  min-width: 44px;
}

.theme-preview-card:hover:not(:disabled) {
  border-color: var(--color-border-strong, var(--color-text));
  transform: translateY(-1px);
}

.theme-preview-card:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

.theme-preview-card.is-active {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 2px var(--color-accent);
}

.theme-preview-card:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Box visual das cores da paleta */
.theme-color-box {
  width: 100%;
  height: 64px;
  border-radius: var(--radius-sm, 6px);
  border-width: 1px;
  border-style: solid;
  padding: 0.35rem;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: center;
}

.theme-window-mockup {
  width: 100%;
  height: 100%;
  border-radius: 4px;
  border-width: 1px;
  border-style: solid;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.mockup-header {
  height: 12px;
  padding: 2px 4px;
  display: flex;
  align-items: center;
}

.mockup-accent-pill {
  width: 16px;
  height: 5px;
  border-radius: 2px;
  display: inline-block;
}

.mockup-body {
  flex: 1;
  padding: 4px;
  display: flex;
  flex-direction: column;
  gap: 3px;
  justify-content: center;
}

.mockup-line {
  height: 3px;
  width: 85%;
  border-radius: 1px;
  opacity: 0.85;
}

.mockup-line.short {
  width: 55%;
}

/* Rodapé do cartão */
.theme-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 0.4rem;
  padding: 0 0.15rem;
}

.theme-name {
  font-size: 0.825rem;
  font-weight: 500;
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.theme-active-indicator {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--color-accent);
  margin-left: 0.25rem;
}

/* Estilo estritamente monocromático para o E-Ink */
.theme-preview-card.is-eink .mockup-accent-pill {
  border: 1px solid #000000;
}

@media (max-width: 640px) {
  .theme-preview-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
