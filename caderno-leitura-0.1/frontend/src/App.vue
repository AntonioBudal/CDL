<script setup lang="ts">
import { RouterLink, RouterView, useRoute } from 'vue-router'
const route = useRoute()
</script>

<template>
  <a class="skip-link" href="#conteudo">Pular para o conteúdo</a>
  <header class="app-header">
    <div class="header-inner">
      <RouterLink class="brand" to="/">Caderno de Leitura</RouterLink>
      <nav aria-label="Navegação principal">
        <RouterLink to="/" :class="{ selected: ['books', 'book', 'study', 'study-edit'].includes(String(route.name)) }">Livros</RouterLink>
        <RouterLink to="/importar" active-class="selected">Importar estudo</RouterLink>
        <RouterLink to="/conexao" active-class="selected">Conexão</RouterLink>
      </nav>
    </div>
  </header>
  <main id="conteudo" class="workspace" tabindex="-1">
    <RouterView />
  </main>
  <footer class="app-footer">Caderno pessoal · Alpha 0.1</footer>
</template>
