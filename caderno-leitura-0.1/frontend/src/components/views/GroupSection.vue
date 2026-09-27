<script setup lang="ts">
import { computed } from 'vue'
import Icon from '../ui/Icon.vue'

interface Props {
  id: string
  title: string
  count: number
  isCollapsed?: boolean
  badgeLabel?: string
  badgeClass?: string
}

const props = withDefaults(defineProps<Props>(), {
  isCollapsed: false,
  badgeLabel: undefined,
  badgeClass: undefined,
})

const emit = defineEmits<{
  (e: 'toggle', id: string): void
}>()

const headingId = computed(() => `group-heading-${props.id}`)
const contentId = computed(() => `group-content-${props.id}`)
</script>

<template>
  <section
    :id="`group-section-${id}`"
    class="group-section"
    :class="{ 'is-collapsed': isCollapsed }"
    role="region"
    :aria-labelledby="headingId"
  >
    <header class="group-header">
      <button
        type="button"
        class="group-toggle-btn"
        :aria-expanded="!isCollapsed"
        :aria-controls="contentId"
        @click="emit('toggle', id)"
      >
        <span class="group-chevron-wrap" :class="{ 'is-rotated': isCollapsed }" aria-hidden="true">
          <Icon
            name="chevron-down"
            :size="16"
            class="group-chevron-icon"
          />
        </span>
        <h3 :id="headingId" class="group-title">{{ title }}</h3>
        <span v-if="badgeLabel" class="group-status-tag" :class="badgeClass">{{ badgeLabel }}</span>
        <span class="group-count-badge" :aria-label="`${count} estudos`">{{ count }}</span>
      </button>
    </header>

    <div
      v-show="!isCollapsed"
      :id="contentId"
      class="group-content"
      role="group"
      :aria-labelledby="headingId"
    >
      <slot />
    </div>
  </section>
</template>

<style scoped>
.group-section {
  margin-bottom: 24px;
  background: transparent;
  transition: all 0.2s ease;
}

.group-header {
  position: sticky;
  top: 0;
  z-index: 10;
  background: var(--color-surface, #ffffff);
  border-bottom: 1px solid var(--color-border, #e2e8f0);
  border-radius: 6px 6px 0 0;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.group-toggle-btn {
  display: flex;
  align-items: center;
  width: 100%;
  min-height: 44px;
  padding: 8px 12px;
  background: transparent;
  border: none;
  cursor: pointer;
  text-align: left;
  font-family: inherit;
  color: var(--color-text, #1a202c);
  border-radius: 6px;
  transition: background-color 0.15s ease, color 0.15s ease;
}

.group-toggle-btn:hover {
  background-color: var(--color-surface-hover, #f8fafc);
  color: var(--color-hover-text);
}

.group-toggle-btn:hover .group-title {
  color: var(--color-hover-text);
}

.group-toggle-btn:hover .group-chevron-wrap {
  color: var(--color-hover-text);
}

.group-toggle-btn:hover .group-count-badge {
  color: var(--color-hover-text);
  border-color: var(--color-border-hover);
}

:root .group-header .group-toggle-btn {
  background: transparent;
  border: none;
  color: var(--color-text, #1a202c);
}

:root .group-header .group-toggle-btn:hover {
  background-color: var(--color-surface-hover, #f8fafc);
  color: var(--color-hover-text);
}

:root .group-header .group-toggle-btn:hover .group-title,
:root .group-header .group-toggle-btn:hover .group-chevron-wrap,
:root .group-header .group-toggle-btn:hover .group-count-badge {
  color: var(--color-hover-text);
}

.group-toggle-btn:focus-visible {
  outline: 2px solid var(--color-accent, #3b82f6);
  outline-offset: -2px;
}

.group-chevron-wrap {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  margin-right: 8px;
  color: var(--color-muted, #718096);
  flex-shrink: 0;
}

.group-chevron-icon {
  transition: transform 0.2s ease;
}

.group-chevron-icon.is-rotated {
  transform: rotate(-90deg);
}

.group-title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: var(--color-text, #1a202c);
  flex-grow: 1;
}

.group-status-tag {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 9999px;
  margin-right: 8px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.badge-rascunho {
  background-color: var(--badge-draft-bg, #f1f5f9);
  color: var(--badge-draft-text, #475569);
  border: 1px solid #cbd5e1;
}

.badge-em-estudo {
  background-color: var(--badge-study-bg, #eff6ff);
  color: var(--badge-study-text, #1d4ed8);
  border: 1px solid #bfdbfe;
}

.badge-revisado {
  background-color: var(--badge-reviewed-bg, #fef3c7);
  color: var(--badge-reviewed-text, #b45309);
  border: 1px solid #fde68a;
}

.badge-concluido {
  background-color: var(--badge-done-bg, #ecfdf5);
  color: var(--badge-done-text, #047857);
  border: 1px solid #a7f3d0;
}

:root:is([data-theme='noite-suave'], [data-theme='grafite'], [data-theme='fiorde'], [data-theme='voltagem']) .group-header {
  background: var(--color-surface);
  border-bottom-color: var(--color-border);
}

:root:is([data-theme='noite-suave'], [data-theme='grafite'], [data-theme='fiorde'], [data-theme='voltagem']) .group-title {
  color: #ffffff;
}

:root:is([data-theme='noite-suave'], [data-theme='grafite'], [data-theme='fiorde'], [data-theme='voltagem']) .group-chevron-wrap {
  color: #d4d4d4;
}

:root:is([data-theme='noite-suave'], [data-theme='grafite'], [data-theme='fiorde'], [data-theme='voltagem']) .group-toggle-btn:hover .group-title {
  color: var(--color-hover-text);
}

:root:is([data-theme='noite-suave'], [data-theme='grafite'], [data-theme='fiorde'], [data-theme='voltagem']) .group-toggle-btn:hover .group-chevron-wrap {
  color: var(--color-hover-text);
}

:root:is([data-theme='noite-suave'], [data-theme='grafite'], [data-theme='fiorde'], [data-theme='voltagem']) .badge-rascunho {
  background-color: rgba(148, 163, 184, 0.18);
  color: #e2e8f0;
  border-color: rgba(148, 163, 184, 0.35);
}

:root:is([data-theme='noite-suave'], [data-theme='grafite'], [data-theme='fiorde'], [data-theme='voltagem']) .badge-em-estudo {
  background-color: rgba(59, 130, 246, 0.2);
  color: #93c5fd;
  border-color: rgba(59, 130, 246, 0.4);
}

:root:is([data-theme='noite-suave'], [data-theme='grafite'], [data-theme='fiorde'], [data-theme='voltagem']) .badge-revisado {
  background-color: rgba(245, 158, 11, 0.2);
  color: #fde68a;
  border-color: rgba(245, 158, 11, 0.4);
}

:root:is([data-theme='noite-suave'], [data-theme='grafite'], [data-theme='fiorde'], [data-theme='voltagem']) .badge-concluido {
  background-color: rgba(16, 185, 129, 0.2);
  color: #6ee7b7;
  border-color: rgba(16, 185, 129, 0.4);
}

.group-count-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 24px;
  height: 24px;
  padding: 0 8px;
  font-size: 0.8rem;
  font-weight: 600;
  border-radius: 12px;
  background-color: var(--color-surface-soft, #e2e8f0);
  color: var(--color-muted, #4a5568);
  border: 1px solid var(--color-border, transparent);
}

.group-content {
  padding-top: 14px;
  padding-bottom: 6px;
}

@media (max-width: 768px) {
  .group-header {
    position: sticky;
    top: 0;
    z-index: 20;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.06);
  }

  .group-toggle-btn {
    min-height: 48px;
    padding: 10px 12px;
  }
}
</style>
