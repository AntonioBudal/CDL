<script setup lang="ts">
import { RouterLink, RouterView, useRoute } from 'vue-router'
import type { IconName } from './types'
import Icon from './components/ui/Icon.vue'
import GlobalSearchModal from './components/search/GlobalSearchModal.vue'
import { useGlobalSearch } from './composables/useGlobalSearch.ts'

const route = useRoute()
const { openSearch } = useGlobalSearch()

interface NavLinkItem {
  to: string
  label: string
  routes: string[]
  icon: IconName
}

const mainLinks: NavLinkItem[] = [
  {
    to: '/',
    label: 'Livros',
    routes: ['books', 'book', 'study', 'study-edit'],
    icon: 'book-open',
  },
  {
    to: '/dashboard',
    label: 'Dashboard',
    routes: ['dashboard'],
    icon: 'layout-dashboard',
  },
  {
    to: '/importar',
    label: 'Importar',
    routes: ['import'],
    icon: 'plus',
  },
  {
    to: '/ajustes',
    label: 'Ajustes',
    routes: ['settings', 'connection'],
    icon: 'sliders',
  },
  {
    to: '/lixeira',
    label: 'Lixeira',
    routes: ['trash'],
    icon: 'trash',
  },
]
</script>

<template>
  <a class="skip-link" href="#conteudo">Pular para o conteúdo</a>
  <header class="app-header">
    <div class="header-inner">
      <RouterLink class="brand" to="/">Caderno de Leitura</RouterLink>
      <nav class="main-nav" aria-label="Navegação principal">
        <RouterLink
          v-for="item in mainLinks"
          :key="item.to"
          :to="item.to"
          :class="{
            selected: item.routes.includes(String(route.name))
          }"
          :aria-current="
            item.routes.includes(String(route.name))
              ? (route.name === item.routes[0] ? 'page' : 'true')
              : undefined
          "
        >
          <Icon :name="item.icon" :size="18" :stroke-width="1.8" class="nav-icon" />
          <span>{{ item.label }}</span>
        </RouterLink>
      </nav>
      <div class="header-actions flex items-center gap-2">
        <button
          type="button"
          class="search-trigger-btn flex items-center gap-2 px-3 py-1.5 rounded-lg border border-border/70 bg-muted/40 hover:bg-muted/80 text-muted-foreground hover:text-foreground text-xs font-medium transition-colors cursor-pointer min-h-[38px]"
          aria-label="Abrir busca global de estudos (Ctrl+K)"
          @click="openSearch"
        >
          <Icon name="search" :size="15" />
          <span class="hidden sm:inline">Buscar</span>
          <kbd class="hidden md:inline-block px-1.5 py-0.5 rounded border border-border bg-card text-[10px] font-mono text-muted-foreground">Ctrl K</kbd>
        </button>
      </div>
    </div>
  </header>
  <main id="conteudo" class="workspace" tabindex="-1">
    <RouterView v-slot="{ Component }">
      <Transition name="page" mode="out-in">
        <component :is="Component" :key="$route.fullPath" />
      </Transition>
    </RouterView>
  </main>
  <footer class="app-footer">Caderno de Leitura · Versão 0.4</footer>
  <GlobalSearchModal />
</template>
