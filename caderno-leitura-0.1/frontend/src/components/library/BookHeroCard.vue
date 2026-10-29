<script setup lang="ts">
import { RouterLink } from 'vue-router'
import type { Book } from '../../types'
import BookCover from '../BookCover.vue'
import CategoryBadge from '../CategoryBadge.vue'
import Icon from '../ui/Icon.vue'

defineProps<{
  book: Book
}>()

const emit = defineEmits<{
  (e: 'select-category', categoryId: string): void
}>()
</script>

<template>
  <section class="book-hero-card" aria-label="Leitura ativa em andamento">
    <div class="hero-cover-container">
      <BookCover
        :cover-image="book.cover_image"
        :title="book.title"
        :author="book.author"
        size="md"
      />
    </div>

    <div class="hero-content">
      <div class="hero-eyebrow-container">
        <span class="hero-eyebrow">
          <Icon name="flame" :size="14" :stroke-width="2" class="hero-eyebrow-icon" />
          Em Andamento
        </span>
        <span v-if="book.year" class="hero-year">({{ book.year }})</span>
      </div>

      <h2 class="hero-title">{{ book.title }}</h2>
      <p v-if="book.subtitle" class="hero-subtitle">{{ book.subtitle }}</p>
      <p class="hero-author">{{ book.author || 'Autor não informado' }}</p>

      <div
        v-if="book.categories && book.categories.length > 0"
        class="hero-categories"
      >
        <CategoryBadge
          v-for="cat in book.categories"
          :key="cat.id"
          :category="cat"
          clickable
          size="sm"
          title="Filtrar por esta categoria"
          @click="emit('select-category', cat.id)"
        />
      </div>

      <div class="hero-actions">
        <RouterLink
          class="hero-continue-btn"
          :to="{ name: 'book', params: { bookId: book.id } }"
        >
          <Icon name="book-open" :size="16" :stroke-width="2" />
          <span>Continuar Leitura</span>
        </RouterLink>
      </div>
    </div>
  </section>
</template>

<style scoped>
.book-hero-card {
  display: flex;
  align-items: center;
  gap: 1.75rem;
  padding: 1.5rem 1.75rem;
  margin-bottom: 2rem;
  background-color: var(--color-surface);
  border: var(--border-width, 1px) solid var(--color-border);
  border-left: var(--edge-strong, 0.3rem) solid var(--color-accent);
  border-radius: var(--radius-panel, 0.65rem);
  box-shadow: 0 4px 16px -4px color-mix(in srgb, var(--color-inverse-bg, #000) 8%, transparent);
  transition: transform 150ms ease, box-shadow 150ms ease, border-color 150ms ease;
}

.book-hero-card:hover {
  border-color: var(--color-border-hover, var(--color-border));
  box-shadow: 0 8px 24px -4px color-mix(in srgb, var(--color-inverse-bg, #000) 12%, transparent);
  transform: translateY(-2px);
}

.hero-cover-container {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hero-content {
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  min-width: 0;
}

.hero-eyebrow-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.hero-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-link);
}

.hero-eyebrow-icon {
  color: var(--color-link);
}

.hero-year {
  font-size: 0.8125rem;
  color: var(--color-muted);
}

.hero-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 750;
  line-height: 1.25;
  color: var(--color-text);
  letter-spacing: -0.02em;
}

.hero-subtitle {
  margin: 0;
  font-size: 0.9375rem;
  color: var(--color-muted);
  line-height: 1.4;
}

.hero-author {
  margin: 0;
  font-size: 0.9375rem;
  color: var(--color-subtle, var(--color-muted));
  font-weight: 500;
}

.hero-categories {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-top: 0.35rem;
}

.hero-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 0.75rem;
}

.hero-continue-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  min-height: 44px;
  background-color: var(--color-accent);
  color: var(--color-on-accent, #fff);
  border-radius: var(--radius-button, 0.4rem);
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 650;
  cursor: pointer;
  transition: background-color 150ms ease, transform 150ms ease;
}

.hero-continue-btn:hover {
  background-color: var(--color-accent-hover);
  transform: translateY(-1px);
}

.hero-continue-btn:focus-visible {
  outline: var(--focus-width, 3px) solid var(--color-accent);
  outline-offset: 2px;
}

@media (prefers-reduced-motion: reduce) {
  .book-hero-card,
  .hero-continue-btn {
    transition: none !important;
    transform: none !important;
  }
}

@media (max-width: 640px) {
  .book-hero-card {
    flex-direction: column;
    align-items: flex-start;
    padding: 1.25rem;
    gap: 1.25rem;
  }

  .hero-cover-container {
    width: 100%;
    justify-content: center;
  }
}
</style>
