<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import Icon from './ui/Icon.vue'

const props = withDefaults(
  defineProps<{
    coverImage?: string | null
    title: string
    author?: string | null
    size?: 'sm' | 'md' | 'lg'
  }>(),
  {
    coverImage: null,
    author: null,
    size: 'md',
  },
)

const imageError = ref(false)

watch(
  () => props.coverImage,
  () => {
    imageError.value = false
  },
)

const hasValidImage = computed(() => !!props.coverImage && !imageError.value)

// Gera um tom de cor único e determinístico baseado no título
const backgroundStyle = computed(() => {
  let hash = 0
  const text = props.title || 'Livro'
  for (let i = 0; i < text.length; i++) {
    hash = (hash << 5) - hash + text.charCodeAt(i)
    hash |= 0
  }
  const hue = Math.abs(hash) % 360
  return {
    background: `linear-gradient(145deg, hsl(${hue}, 38%, 24%) 0%, hsl(${hue}, 48%, 14%) 100%)`,
  }
})

const initials = computed(() => {
  if (!props.title) return ''
  const words = props.title.trim().split(/\s+/).filter(Boolean)
  if (words.length === 0) return ''
  if (words.length === 1) return words[0].slice(0, 2).toUpperCase()
  return (words[0][0] + words[1][0]).toUpperCase()
})
</script>

<template>
  <div
    class="book-cover-container"
    :class="[`cover-${size}`, { 'has-image': hasValidImage }]"
    :aria-label="`Capa de ${title}`"
  >
    <img
      v-if="hasValidImage"
      :src="`/api/covers/${coverImage}`"
      :alt="`Capa do livro ${title}`"
      class="book-cover-img"
      loading="lazy"
      @error="imageError = true"
    />
    <div
      v-else
      class="book-cover-placeholder"
      :style="backgroundStyle"
      role="img"
      :aria-label="`Marcador tipográfico: ${title}`"
    >
      <div class="spine-line" aria-hidden="true"></div>
      <div class="placeholder-content">
        <span class="placeholder-monogram" aria-hidden="true">
          <Icon v-if="!initials" name="book" :size="size === 'sm' ? 20 : size === 'lg' ? 36 : 28" />
          <template v-else>{{ initials }}</template>
        </span>
        <span class="placeholder-title">{{ title }}</span>
        <span v-if="author && size !== 'sm'" class="placeholder-author">{{ author }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.book-cover-container {
  aspect-ratio: 2 / 3;
  position: relative;
  overflow: hidden;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15), 0 1px 3px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: stretch;
  justify-content: stretch;
  background-color: var(--color-surface-inset, #edf2f7);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  user-select: none;
  flex-shrink: 0;
}

.cover-sm {
  width: 64px;
}

.cover-md {
  width: 140px;
}

.cover-lg {
  width: 200px;
}

.book-cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.book-cover-placeholder {
  width: 100%;
  height: 100%;
  position: relative;
  display: flex;
  flex-direction: column;
  padding: 8px 10px;
  color: #fff;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.spine-line {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  width: 6px;
  background: linear-gradient(to right, rgba(0, 0, 0, 0.35), rgba(255, 255, 255, 0.15), rgba(0, 0, 0, 0.2));
  border-right: 1px solid rgba(0, 0, 0, 0.25);
}

.placeholder-content {
  margin-left: 6px;
  display: flex;
  flex-direction: column;
  height: 100%;
  justify-content: space-between;
  text-align: left;
}

.placeholder-monogram {
  font-family: var(--font-family-serif, 'EB Garamond', serif);
  font-size: 1.1rem;
  font-weight: 700;
  opacity: 0.8;
  letter-spacing: 0.05em;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding-bottom: 4px;
  margin-bottom: 4px;
}

.cover-sm .placeholder-monogram {
  font-size: 0.85rem;
  padding-bottom: 2px;
}

.placeholder-title {
  font-family: var(--font-family-serif, 'EB Garamond', serif);
  font-size: 0.95rem;
  font-weight: 600;
  line-height: 1.25;
  color: #fff;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  word-break: break-word;
}

.cover-sm .placeholder-title {
  font-size: 0.75rem;
  -webkit-line-clamp: 3;
}

.cover-lg .placeholder-title {
  font-size: 1.2rem;
  -webkit-line-clamp: 5;
}

.placeholder-author {
  font-size: 0.75rem;
  opacity: 0.85;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-top: auto;
  padding-top: 4px;
}

.cover-lg .placeholder-author {
  font-size: 0.85rem;
}
</style>
