<script setup lang="ts">
import { computed } from 'vue'
import { renderMarkdown } from '../services/markdown'
const props = defineProps<{ content: string }>()
const rendered = computed(() => renderMarkdown(props.content))
</script>

<template><div class="markdown-content" v-html="rendered"></div></template>
