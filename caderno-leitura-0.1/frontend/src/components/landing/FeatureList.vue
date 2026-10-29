<script setup lang="ts">
interface FeatureItem {
  title: string
  description: string
}

// Cada item descreve um recurso existente; ver routers de books, studies, study_highlights, review, imports,
// study_versions, search e sharing no backend.
const features: FeatureItem[] = [
  {
    title: 'Livros, capítulos e estudos',
    description:
      'Cadastre os livros, divida-os em capítulos e crie um estudo para cada trecho, com a página ou o local de referência.',
  },
  {
    title: 'Quatro partes por estudo',
    description: 'Resumo, explicação, conceitos e referências, além de um campo livre para notas.',
  },
  {
    title: 'Marcações',
    description:
      'Marque partes do estudo como destaque, citação, nota, pergunta ou trecho oculto, em cinco cores, e consulte todas as marcações em uma única lista.',
  },
  {
    title: 'Revisão',
    description:
      'Perguntas e trechos ocultos viram itens de revisão. Você avalia cada um como fácil, médio ou difícil, e os difíceis aparecem primeiro.',
  },
  {
    title: 'Importação de fichamentos',
    description:
      'Cole um fichamento já escrito e o Leitorum separa o texto nas quatro partes para você conferir antes de salvar.',
  },
  {
    title: 'Histórico e busca',
    description:
      'Cada estudo guarda as versões anteriores, que podem ser comparadas e restauradas. A busca encontra estudos e anotações em todo o acervo.',
  },
  {
    title: 'Compartilhamento',
    description:
      'Livros e estudos começam privados. Você pode abri-los para amigos ou publicá-los com um link.',
  },
]
</script>

<template>
  <section id="recursos" class="features-section" aria-labelledby="features-heading">
    <h2 id="features-heading" class="section-title">O que dá para fazer</h2>
    <dl class="features-list">
      <div v-for="item in features" :key="item.title" class="feature-item">
        <dt class="feature-title">{{ item.title }}</dt>
        <dd class="feature-desc">{{ item.description }}</dd>
      </div>
    </dl>
  </section>
</template>

<style scoped>
.features-section {
  padding-block: clamp(2.5rem, 6vw, 4.5rem);
  border-bottom: 1px solid var(--color-border-divider, var(--color-border));
}

.section-title {
  font-family: var(--font-reading, "Caderno EB Garamond", serif);
  font-size: clamp(1.75rem, 3vw, 2.4rem);
  font-weight: 600;
  line-height: 1.2;
  margin: 0 0 1.75rem 0;
  color: var(--color-text);
}

.features-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 22rem), 1fr));
  gap: 1.5rem 3rem;
  margin: 0;
}

.feature-item {
  min-width: 0;
}

.feature-title {
  font-size: 1.05rem;
  font-weight: 700;
  line-height: 1.35;
  margin: 0 0 0.35rem 0;
  color: var(--color-text);
}

.feature-desc {
  font-size: 1rem;
  line-height: 1.6;
  margin: 0;
  color: var(--color-text);
}
</style>
