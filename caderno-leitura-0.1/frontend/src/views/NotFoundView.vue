<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>
<template>
  <section class="empty-state">
    <p class="eyebrow">Página não encontrada</p>
    <h1>Este endereço não existe.</h1>
    <p>Volte ao acervo para continuar.</p>
    <RouterLink class="button primary" to="/">Ir para meus livros</RouterLink>
  </section>
</template>
