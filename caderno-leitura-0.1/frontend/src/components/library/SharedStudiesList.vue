<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { sharingApi } from '../../api/sharing.ts'
import type { SharedStudySummary } from '../../types.ts'

const loading = ref(true)
const loadError = ref<string | null>(null)
const items = ref<SharedStudySummary[]>([])
const total = ref(0)

const searchQuery = ref('')
const authorFilter = ref('')
let debounceTimer: ReturnType<typeof setTimeout> | null = null

async function fetchSharedStudies() {
  loading.value = true
  loadError.value = null
  try {
    const res = await sharingApi.getSharedStudies({
      q: searchQuery.value.trim() || undefined,
      author: authorFilter.value.trim().replace(/^@/, '') || undefined,
      limit: 50,
    })
    items.value = res.items
    total.value = res.total
  } catch (err: unknown) {
    loadError.value = err instanceof Error ? err.message : 'Falha ao carregar estudos compartilhados.'
  } finally {
    loading.value = false
  }
}

function onSearchInput() {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    fetchSharedStudies()
  }, 300)
}

function clearFilters() {
  searchQuery.value = ''
  authorFilter.value = ''
  fetchSharedStudies()
}

function formatDate(iso: string): string {
  try {
    const d = new Date(iso)
    return new Intl.DateTimeFormat('pt-BR', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    }).format(d)
  } catch {
    return iso
  }
}

function getVisibilityLabel(vis: string): { label: string } {
  switch (vis) {
    case 'public':
      return { label: 'Público' }
    case 'friends':
      return { label: 'Amigos' }
    case 'custom':
      return { label: 'Nominal' }
    default:
      return { label: 'Compartilhado' }
  }
}

onMounted(fetchSharedStudies)
</script>

<template>
  <div class="shared-studies-container space-y-6">
    <!-- Barra de Filtros e Busca -->
    <div class="flex flex-col sm:flex-row gap-3 items-stretch sm:items-center justify-between">
      <div class="flex-1 flex flex-col sm:flex-row gap-2.5">
        <!-- Input de busca textual -->
        <div class="relative flex-1">
          <svg class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            v-model="searchQuery"
            type="search"
            placeholder="Buscar por título ou tema..."
            class="w-full pl-9 pr-4 py-2.5 text-sm rounded-xl bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-zinc-900 dark:text-zinc-100 placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500 shadow-sm"
            aria-label="Buscar estudos compartilhados por texto"
            @input="onSearchInput"
          />
        </div>

        <!-- Input de busca por autor -->
        <div class="relative w-full sm:w-56">
          <span class="absolute left-3.5 top-1/2 -translate-y-1/2 text-zinc-400 text-sm font-mono" aria-hidden="true">@</span>
          <input
            v-model="authorFilter"
            type="search"
            placeholder="autor (username)"
            class="w-full pl-8 pr-4 py-2.5 text-sm rounded-xl bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-zinc-900 dark:text-zinc-100 placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500 shadow-sm"
            aria-label="Filtrar estudos compartilhados por autor"
            @input="onSearchInput"
          />
        </div>
      </div>

      <div v-if="searchQuery || authorFilter" class="flex items-center gap-2">
        <button
          type="button"
          class="min-h-[44px] px-3.5 py-2 text-xs font-medium text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-200 bg-zinc-100 dark:bg-zinc-800 rounded-xl hover:bg-zinc-200 dark:hover:bg-zinc-700 transition-colors"
          @click="clearFilters"
        >
          Limpar filtros
        </button>
      </div>
    </div>

    <!-- Indicador de Carregamento -->
    <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 gap-4" role="status" aria-label="Carregando estudos compartilhados">
      <div
        v-for="i in 4"
        :key="i"
        class="p-5 rounded-2xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 animate-pulse space-y-3"
      >
        <div class="flex items-center gap-2.5">
          <div class="w-8 h-8 rounded-full bg-zinc-200 dark:bg-zinc-800" />
          <div class="space-y-1 flex-1">
            <div class="h-3 w-28 bg-zinc-200 dark:bg-zinc-800 rounded" />
            <div class="h-2.5 w-16 bg-zinc-200 dark:bg-zinc-800 rounded" />
          </div>
        </div>
        <div class="h-4 w-3/4 bg-zinc-200 dark:bg-zinc-800 rounded" />
        <div class="h-3 w-1/2 bg-zinc-200 dark:bg-zinc-800 rounded" />
      </div>
    </div>

    <!-- Mensagem de Erro -->
    <div
      v-else-if="loadError"
      class="p-4 rounded-2xl bg-red-50 dark:bg-red-950/40 text-red-700 dark:text-red-300 border border-red-200 dark:border-red-900/50 flex items-center justify-between gap-3"
      role="alert"
    >
      <div class="flex items-center gap-2">
        <svg class="w-4 h-4 text-red-600 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <span class="text-sm">{{ loadError }}</span>
      </div>
      <button
        type="button"
        class="min-h-[44px] px-3 py-1.5 text-xs font-medium rounded-lg bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 hover:bg-red-200"
        @click="fetchSharedStudies"
      >
        Tentar novamente
      </button>
    </div>

    <!-- Lista Vazia -->
    <div
      v-else-if="items.length === 0"
      class="p-12 text-center rounded-2xl border border-dashed border-zinc-200 dark:border-zinc-800 bg-white/50 dark:bg-zinc-900/30 space-y-3"
    >
      <div class="flex justify-center" aria-hidden="true">
        <svg class="w-12 h-12 text-zinc-300 dark:text-zinc-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      </div>
      <h3 class="text-base font-semibold text-zinc-900 dark:text-zinc-100">
        {{ searchQuery || authorFilter ? 'Nenhum estudo corresponde à busca' : 'Nenhum estudo compartilhado com você' }}
      </h3>
      <p class="text-xs text-zinc-500 dark:text-zinc-400 max-w-md mx-auto leading-relaxed">
        {{
          searchQuery || authorFilter
            ? 'Tente ajustar os termos de busca ou limpar os filtros para encontrar outros estudos.'
            : 'Quando seus amigos no Leitorum ou outros leitores compartilharem estudos e livros, eles aparecerão aqui para você ler e consultar.'
        }}
      </p>
      <div v-if="searchQuery || authorFilter" class="pt-2">
        <button
          type="button"
          class="min-h-[44px] px-4 py-2 text-xs font-medium rounded-xl bg-amber-600 hover:bg-amber-500 text-white transition-colors"
          @click="clearFilters"
        >
          Ver todos os compartilhados
        </button>
      </div>
    </div>

    <!-- Grid de Estudos Compartilhados -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <article
        v-for="item in items"
        :key="item.id"
        class="group p-5 rounded-2xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/80 hover:border-amber-400/60 dark:hover:border-amber-500/50 shadow-sm hover:shadow-md transition-all flex flex-col justify-between"
      >
        <div class="space-y-3">
          <!-- Cabeçalho do Card: Autor + Badge de Visibilidade -->
          <div class="flex items-center justify-between gap-3">
            <div class="flex items-center gap-2.5 min-w-0">
              <div
                class="w-8 h-8 rounded-full bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300 flex items-center justify-center text-xs font-semibold overflow-hidden shrink-0"
              >
                <img
                  v-if="item.owner_avatar_url"
                  :src="item.owner_avatar_url"
                  :alt="item.owner_display_name"
                  class="w-full h-full object-cover"
                />
                <span v-else>{{ item.owner_display_name.charAt(0).toUpperCase() }}</span>
              </div>
              <div class="min-w-0">
                <p class="text-xs font-semibold text-zinc-900 dark:text-zinc-100 truncate">
                  {{ item.owner_display_name }}
                </p>
                <p class="text-[11px] text-zinc-400 dark:text-zinc-500 font-mono truncate">
                  @{{ item.owner_username }}
                </p>
              </div>
            </div>

            <span
              class="inline-flex items-center text-[11px] font-medium px-2 py-0.5 rounded-full bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400 shrink-0"
              :title="`Visibilidade: ${item.visibility}`"
            >
              <span>{{ getVisibilityLabel(item.visibility).label }}</span>
            </span>
          </div>

          <!-- Título do Estudo -->
          <div>
            <h3 class="text-base font-semibold text-zinc-900 dark:text-zinc-100 group-hover:text-amber-600 dark:group-hover:text-amber-400 transition-colors line-clamp-2">
              <RouterLink :to="{ name: 'study', params: { bookId: item.book_id, studyId: item.id } }">
                {{ item.title }}
              </RouterLink>
            </h3>
            <p class="text-xs text-zinc-500 dark:text-zinc-400 mt-1 line-clamp-1">
              <span class="font-medium text-zinc-700 dark:text-zinc-300">{{ item.book_title }}</span>
              <span v-if="item.chapter_name"> · {{ item.chapter_name }}</span>
            </p>
          </div>
        </div>

        <!-- Rodapé do Card -->
        <div class="mt-4 pt-3 border-t border-zinc-100 dark:border-zinc-800/80 flex items-center justify-between text-xs text-zinc-400 dark:text-zinc-500">
          <span>Atualizado em {{ formatDate(item.updated_at) }}</span>
          <RouterLink
            :to="{ name: 'study', params: { bookId: item.book_id, studyId: item.id } }"
            class="min-h-[44px] inline-flex items-center px-3 py-1.5 font-medium text-amber-700 dark:text-amber-400 hover:text-amber-600 rounded-lg hover:bg-amber-50 dark:hover:bg-amber-950/30 transition-colors"
            aria-label="Abrir estudo em modo somente leitura"
          >
            Abrir leitura →
          </RouterLink>
        </div>
      </article>
    </div>
  </div>
</template>

<style scoped>
.shared-studies-container {
  width: 100%;
}
</style>
