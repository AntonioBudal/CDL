<script setup lang="ts">
import { RouterLink } from 'vue-router'
import type { BreadcrumbItem } from '../../types/navigation'

interface Props {
  items: BreadcrumbItem[]
}

defineProps<Props>()
</script>

<template>
  <nav class="app-breadcrumb" aria-label="Trilha de navegação">
    <ol class="breadcrumb-list">
      <li
        v-for="(item, idx) in items"
        :key="idx"
        class="breadcrumb-item"
      >
        <RouterLink
          v-if="item.to && !item.current"
          :to="item.to"
          class="breadcrumb-link"
        >
          <span class="breadcrumb-text">{{ item.label }}</span>
        </RouterLink>
        <span
          v-else
          class="breadcrumb-current"
          aria-current="page"
        >
          <span class="breadcrumb-text">{{ item.label }}</span>
        </span>
        <span
          v-if="idx < items.length - 1"
          class="breadcrumb-separator"
          aria-hidden="true"
        >/</span>
      </li>
    </ol>
  </nav>
</template>

<style scoped>
.app-breadcrumb {
  margin-bottom: calc(var(--space-unit, 1rem) * 1.25);
  font-size: 0.875rem;
  line-height: 1.4;
  color: var(--color-muted);
}

.breadcrumb-list {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.375rem 0.5rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.breadcrumb-item {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 0;
  max-width: 100%;
}

.breadcrumb-link {
  color: var(--color-muted);
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  min-width: 0;
  padding: 0.25rem 0;
  border-radius: var(--radius-sm, 4px);
  transition: color 0.15s ease-in-out;
}

.breadcrumb-link:hover {
  color: var(--color-text);
  text-decoration: underline;
  text-underline-offset: 0.2em;
}

.breadcrumb-link:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

.breadcrumb-current {
  color: var(--color-text);
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  min-width: 0;
}

.breadcrumb-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 260px;
}

.breadcrumb-separator {
  color: var(--color-muted);
  opacity: 0.65;
  user-select: none;
  font-weight: 400;
}

@media (pointer: coarse) {
  .breadcrumb-link {
    min-height: 36px;
  }
}

@media (max-width: 640px) {
  .breadcrumb-text {
    max-width: 180px;
  }
}
</style>
