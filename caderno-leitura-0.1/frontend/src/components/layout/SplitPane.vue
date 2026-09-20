<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  id: 'left' | 'right' | 'main'
  width?: number
  collapsed?: boolean
  minWidth?: number
  maxWidth?: number
  isResizing?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  width: undefined,
  collapsed: false,
  minWidth: undefined,
  maxWidth: undefined,
  isResizing: false
})

const paneStyle = computed(() => {
  if (props.id === 'main') {
    return {
      minWidth: 'var(--pane-main-min-width, 360px)'
    }
  }

  if (props.collapsed) {
    return {
      width: '0px',
      minWidth: '0px',
      maxWidth: '0px',
      padding: '0px',
      margin: '0px',
      border: 'none',
      visibility: 'hidden' as const,
      opacity: 0,
      pointerEvents: 'none' as const
    }
  }

  const effectiveWidth = props.width ? `${props.width}px` : undefined
  return {
    width: effectiveWidth,
    minWidth: props.minWidth ? `${props.minWidth}px` : undefined,
    maxWidth: props.maxWidth ? `${props.maxWidth}px` : undefined
  }
})
</script>

<template>
  <div
    class="split-pane"
    :class="[
      `split-pane-${id}`,
      {
        'is-collapsed': collapsed,
        'is-resizing': isResizing,
        'split-pane-side': id !== 'main'
      }
    ]"
    :style="paneStyle"
  >
    <div class="split-pane-inner">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.split-pane {
  position: relative;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-sizing: border-box;
}

.split-pane-side {
  flex-shrink: 0;
  transition: width 0.24s cubic-bezier(0.16, 1, 0.3, 1),
              opacity 0.18s ease,
              visibility 0.24s ease;
}

.split-pane.is-resizing {
  transition: none !important;
}

.split-pane-main {
  flex: 1 1 0%;
  min-width: var(--pane-main-min-width, 360px);
  z-index: 1;
}

.split-pane-inner {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  box-sizing: border-box;
}

.split-pane.is-collapsed {
  border: none !important;
  visibility: hidden;
  pointer-events: none;
}

@media (prefers-reduced-motion: reduce) {
  .split-pane-side {
    transition: none !important;
  }
}
</style>
