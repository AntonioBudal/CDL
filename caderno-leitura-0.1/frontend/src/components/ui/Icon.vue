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
  Copy,
  Heart,
  Pencil,
  X,
  Search,
  AlertTriangle,
  CheckCircle,
  Check,
  Flame,
  Folder,
  FolderPlus,
  Minus,
  Calendar,
  Download,
  Upload,
  ExternalLink,
  ChevronRight,
  ChevronDown,
  ChevronUp,
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
  User,
  Smartphone,
  Monitor,
  Shield,
  Lock,
  Globe,
  Users,
  Camera,
  Image,
  Eye,
  EyeOff,
  UserPlus,
  UserMinus,
  Ban,
  Clock,
  Unlock,
  Mail,
  ChevronLeft,
  LogOut,
  RefreshCw,
  UserCheck,
  UserX,
  Bell,
  BellRing,
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
  'rotate-ccw': RotateCcw,
  'copy': Copy,
  'heart': Heart,
  'pencil': Pencil,
  'x': X,
  'search': Search,
  'alert-triangle': AlertTriangle,
  'check-circle': CheckCircle,
  'check': Check,
  'flame': Flame,
  'folder': Folder,
  'folder-plus': FolderPlus,
  'minus': Minus,
  'calendar': Calendar,
  'download': Download,
  'upload': Upload,
  'external-link': ExternalLink,
  'chevron-right': ChevronRight,
  'chevron-down': ChevronDown,
  'chevron-up': ChevronUp,
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
  'user': User,
  'smartphone': Smartphone,
  'monitor': Monitor,
  'shield': Shield,
  'lock': Lock,
  'globe': Globe,
  'users': Users,
  'camera': Camera,
  'image': Image,
  'eye': Eye,
  'eye-off': EyeOff,
  'user-plus': UserPlus,
  'user-minus': UserMinus,
  'ban': Ban,
  'clock': Clock,
  'unlock': Unlock,
  'mail': Mail,
  'chevron-left': ChevronLeft,
  'log-out': LogOut,
  'refresh-cw': RefreshCw,
  'user-check': UserCheck,
  'user-x': UserX,
  'bell': Bell,
  'bell-ring': BellRing,
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
