<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import type { AppearancePreferences } from '../appearance'
import ReadingSizeControl from './ReadingSizeControl.vue'

withDefaults(
  defineProps<{
    activeReadingEnabled?: boolean
    interactiveCount?: number
  }>(),
  {
    activeReadingEnabled: false,
    interactiveCount: 0,
  },
)

const emit = defineEmits<{
  (e: 'toggle-active-reading'): void
}>()

const appearance = window.cadernoAppearance
const size = ref(appearance.get()['reader-size'])
const focused = ref(false)
const focusButton = ref<HTMLButtonElement | null>(null)
const message = ref('')

function changeSize(value: AppearancePreferences['reader-size']) {
  const saved = appearance.set({ 'reader-size': value })

  size.value = appearance.get()['reader-size']
  message.value = saved
    ? ''
    : 'Tamanho aplicado, mas o navegador não permitiu salvar. A escolha pode ser perdida ao recarregar.'
}

function applyFocus(value: boolean) {
  focused.value = value

  if (value) {
    document.documentElement.setAttribute('data-reading-focus', 'on')
  } else {
    document.documentElement.removeAttribute('data-reading-focus')
  }
}

async function toggleFocus() {
  applyFocus(!focused.value)
  await nextTick()
  focusButton.value?.focus()
}

function onKeydown(event: KeyboardEvent) {
  if (
    event.key !== 'Escape'
    || !focused.value
    || event.defaultPrevented
    || event.isComposing
  ) return

  event.preventDefault()
  void toggleFocus()
}

onMounted(() => {
  window.addEventListener('keydown', onKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeydown)
  applyFocus(false)
})
</script>

<template>
  <div
    class="reader-tools"
    role="group"
    aria-label="Controles de leitura"
  >
    <button
      ref="focusButton"
      type="button"
      class="secondary"
      :aria-keyshortcuts="focused ? 'Escape' : undefined"
      @click="toggleFocus"
    >
      {{ focused ? 'Sair do modo foco' : 'Ativar modo foco' }}
    </button>

    <button
      type="button"
      class="secondary tool-btn active-reading-toggle"
      :class="{ 'is-active': activeReadingEnabled }"
      :title="activeReadingEnabled ? 'Desativar Leitura Ativa' : 'Ativar Leitura Ativa (Active Recall)'"
      :aria-pressed="activeReadingEnabled"
      aria-label="Alternar modo de leitura ativa"
      @click="emit('toggle-active-reading')"
    >
      <svg class="tool-icon" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
        <circle cx="12" cy="12" r="10" />
        <path d="M12 6v6l4 2" />
      </svg>
      <span>Leitura Ativa</span>
      <span v-if="interactiveCount > 0" class="badge-count" aria-label="Quantidade de trechos interativos">{{ interactiveCount }}</span>
    </button>

    <ReadingSizeControl
      id="reader-font-size"
      :value="size"
      @change="changeSize"
    />

    <p
      v-if="message"
      class="reader-tools-status notice"
      role="status"
    >
      {{ message }}
    </p>
  </div>
</template>

<style scoped>
.active-reading-toggle {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
}

.active-reading-toggle.is-active {
  background-color: var(--color-primary, #2563eb);
  color: #ffffff;
  border-color: var(--color-primary, #2563eb);
}

.tool-icon {
  flex-shrink: 0;
}

.badge-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 1.125rem;
  height: 1.125rem;
  padding: 0 0.3125rem;
  border-radius: 9999px;
  font-size: 0.6875rem;
  font-weight: 700;
  line-height: 1;
  background-color: var(--color-accent-subtle, rgba(37, 99, 235, 0.15));
  color: var(--color-primary, #2563eb);
}

.active-reading-toggle.is-active .badge-count {
  background-color: rgba(255, 255, 255, 0.25);
  color: #ffffff;
}
</style>