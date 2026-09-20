<script setup lang="ts">
import { computed } from 'vue'
import type { Component } from 'vue'
import type { IconProps } from '../../types'
import {
  BookOpen,
  Book,
  LayoutDashboard,
  Plus,
  Sliders,
  Trash2,
  RotateCcw,
  Pencil,
  X,
  Search,
  AlertTriangle,
  CheckCircle,
  Check,
  Flame,
  Folder,
  Calendar,
  Download,
  Upload,
  ExternalLink,
  ChevronRight,
  ChevronDown,
  Grid,
  List,
  Network,
  Maximize2,
  Minimize2,
  GripVertical,
  MoreHorizontal,
  ArrowUp,
  ArrowDown,
  CornerDownRight,
  CornerUpLeft,
  Link,
  ArrowRight,
} from 'lucide-vue-next'

const props = withDefaults(defineProps<IconProps>(), {
  size: 20,
  strokeWidth: 2,
  ariaLabel: undefined,
  class: '',
})

const iconMap: Record<string, Component> = {
  'book-open': BookOpen,
  'book': Book,
  'layout-dashboard': LayoutDashboard,
  'plus': Plus,
  'sliders': Sliders,
  'trash': Trash2,
  'trash-restore': RotateCcw,
  'pencil': Pencil,
  'x': X,
  'search': Search,
  'alert-triangle': AlertTriangle,
  'check-circle': CheckCircle,
  'check': Check,
  'flame': Flame,
  'folder': Folder,
  'calendar': Calendar,
  'download': Download,
  'upload': Upload,
  'external-link': ExternalLink,
  'chevron-right': ChevronRight,
  'chevron-down': ChevronDown,
  'grid': Grid,
  'list': List,
  'network': Network,
  'canvas': Maximize2,
  'maximize-2': Maximize2,
  'minimize-2': Minimize2,
  'grip-vertical': GripVertical,
  'more-horizontal': MoreHorizontal,
  'arrow-up': ArrowUp,
  'arrow-down': ArrowDown,
  'corner-down-right': CornerDownRight,
  'corner-up-left': CornerUpLeft,
  'link': Link,
  'arrow-right': ArrowRight,
}

const currentComponent = computed(() => iconMap[props.name] || BookOpen)
</script>

<template>
  <component
    :is="currentComponent"
    :size="size"
    :stroke-width="strokeWidth"
    :class="['ui-icon', props.class]"
    :role="ariaLabel ? 'img' : undefined"
    :aria-label="ariaLabel"
    :aria-hidden="ariaLabel ? undefined : 'true'"
    focusable="false"
  />
</template>

<style scoped>
.ui-icon {
  display: inline-block;
  vertical-align: middle;
  flex-shrink: 0;
  color: currentColor;
}
</style>
