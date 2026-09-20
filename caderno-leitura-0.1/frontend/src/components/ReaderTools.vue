<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import type { AppearancePreferences } from '../appearance'
import ReadingSizeControl from './ReadingSizeControl.vue'

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