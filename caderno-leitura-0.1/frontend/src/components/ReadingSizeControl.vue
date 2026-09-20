<script setup lang="ts">
import type { AppearancePreferences } from '../appearance'
import { useSuperclassPhysics } from '../composables/useSuperclassPhysics'

type ReadingSize = AppearancePreferences['reader-size']

defineProps<{ id: string; value: ReadingSize }>()
const emit = defineEmits<{ change: [value: ReadingSize] }>()

const physics = useSuperclassPhysics()

function change(event: Event) {
  const target = event.target as HTMLInputElement
  const value = target.value
  physics.triggerHapticPulse(target, 'step')
  const field = window.cadernoAppearance.fields.find(
    item => item.key === 'reader-size'
  )

  if (field?.options.some(([option]) => option === value)) {
    emit('change', value as ReadingSize)
  }
}
</script>

<template>
  <div class="reading-size-control">
    <label :for="id">
      <span>Tamanho do texto</span>
      <span aria-hidden="true">{{ value }}%</span>
    </label>

    <input
      :id="id"
      type="range"
      min="100"
      max="200"
      step="10"
      :value="value"
      :aria-valuetext="`${value}%`"
      @input="change"
    />
  </div>
</template>