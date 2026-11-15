<script setup lang="ts">
// F0.12.06: imagem do cartão de oclusão — todas as áreas cobertas, a perguntada destacada; "Revelar" abre só ela.
import { ref } from 'vue'
import type { OcclusionRegion } from '../../types.ts'

const props = defineProps<{
  mediaId: string
  regions: OcclusionRegion[]
  targetId: number
  revealed: boolean
  label: string
}>()

const failed = ref(false)

function isTarget(region: OcclusionRegion) {
  return region.id === props.targetId
}
</script>

<template>
  <figure class="occlusion-image">
    <p v-if="failed" class="notice error" role="alert">
      Não foi possível abrir a imagem (o cofre de imagens pode estar trancado).
    </p>
    <div v-else class="occlusion-stage">
      <div class="occlusion-frame">
        <img
          :src="`/api/media/${encodeURIComponent(mediaId)}/content`"
          alt="Imagem do cartão com áreas cobertas"
          draggable="false"
          @error="failed = true"
        >
        <svg class="occlusion-layer" viewBox="0 0 1 1" preserveAspectRatio="none" aria-hidden="true">
          <rect
            v-for="region in regions"
            :key="region.id"
            :x="region.x"
            :y="region.y"
            :width="region.width"
            :height="region.height"
            :class="isTarget(region) ? (revealed ? 'occlusion-open' : 'occlusion-target') : 'occlusion-cover'"
            vector-effect="non-scaling-stroke"
          />
        </svg>
      </div>
    </div>
    <figcaption class="occlusion-caption">
      <template v-if="revealed">
        <span class="answer-label">Resposta:</span>
        {{ label || 'a área destacada foi aberta na imagem.' }}
      </template>
      <template v-else>A área perguntada está destacada.</template>
    </figcaption>
  </figure>
</template>

<style scoped>
.occlusion-image {
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.occlusion-stage {
  display: flex;
  justify-content: center;
  width: 100%;
  border-radius: var(--radius-card);
  border: 1px solid var(--color-border-subtle);
  background: var(--color-surface-soft);
}

.occlusion-frame {
  position: relative;
  display: inline-block;
  max-width: 100%;
}

/* A imagem inteira cabe no cartão (sem rolagem interna); o SVG acompanha o tamanho dela. */
.occlusion-frame img {
  display: block;
  max-width: 100%;
  max-height: 60vh;
  width: auto;
  height: auto;
  user-select: none;
}

.occlusion-layer {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.occlusion-cover {
  fill: var(--color-surface-inset);
  stroke: var(--color-text-secondary);
  stroke-width: 1.5;
}

.occlusion-target {
  fill: var(--color-accent);
  stroke: var(--color-text);
  stroke-width: 3;
}

.occlusion-open {
  fill: transparent;
  stroke: var(--color-accent);
  stroke-width: 3;
  stroke-dasharray: 6 4;
}

.occlusion-caption {
  color: var(--color-text-secondary);
  font-size: 0.95rem;
}

.occlusion-caption .answer-label {
  font-weight: 600;
  color: var(--color-text);
}
</style>
