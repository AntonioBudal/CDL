<script setup lang="ts">
interface DataFact {
  title: string
  description: string
}

// Afirmações conferidas no código: export_service (Markdown, texto e .zip da conta), ausência de scripts de
// análise no frontend e de clientes de IA no backend; as únicas saídas de rede são google_auth_service e
// cover_service (e o script de login do Google no navegador, quando o login com Google está ativado).
const facts: DataFact[] = [
  {
    title: 'Onde ficam',
    description: 'No servidor em que este Leitorum está instalado, em um banco de dados SQLite.',
  },
  {
    title: 'Exportação',
    description:
      'Um livro ou um estudo pode ser exportado em Markdown ou texto simples. A exportação da conta gera um arquivo .zip com os estudos em Markdown, os dados em JSON e as imagens enviadas.',
  },
  {
    title: 'Sem anúncios nem análise de uso',
    description:
      'O Leitorum não tem anúncios nem ferramentas de análise de terceiros, e os textos não são enviados a serviços de inteligência artificial.',
  },
  {
    title: 'Conexões externas',
    description:
      'Só acontecem no login com Google, quando ele está ativado nesta instalação, e ao buscar uma capa pelo endereço que você informar.',
  },
]
</script>

<template>
  <section id="dados" class="sovereignty-section" aria-labelledby="data-heading">
    <h2 id="data-heading" class="section-title">Seus dados</h2>

    <dl class="facts-list">
      <div v-for="fact in facts" :key="fact.title" class="fact-item">
        <dt class="fact-title">{{ fact.title }}</dt>
        <dd class="fact-desc">{{ fact.description }}</dd>
      </div>
    </dl>

    <p class="source-note">
      O código-fonte está publicado no
      <a href="https://github.com/AntonioBudal/CDL" target="_blank" rel="noopener noreferrer">GitHub</a>.
    </p>
  </section>
</template>

<style scoped>
.sovereignty-section {
  padding-block: clamp(2.5rem, 6vw, 4.5rem);
}

.section-title {
  font-family: var(--font-reading, "Caderno EB Garamond", serif);
  font-size: clamp(1.75rem, 3vw, 2.4rem);
  font-weight: 600;
  line-height: 1.2;
  margin: 0 0 1.75rem 0;
  color: var(--color-text);
}

.facts-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 22rem), 1fr));
  gap: 1.5rem 3rem;
  margin: 0;
}

.fact-item {
  min-width: 0;
}

.fact-title {
  font-size: 1.05rem;
  font-weight: 700;
  line-height: 1.35;
  margin: 0 0 0.35rem 0;
  color: var(--color-text);
}

.fact-desc {
  font-size: 1rem;
  line-height: 1.6;
  margin: 0;
  color: var(--color-text);
}

.source-note {
  margin: 2rem 0 0 0;
  font-size: 1rem;
  line-height: 1.6;
  color: var(--color-text);
}

.source-note a {
  color: var(--color-link);
  text-decoration: underline;
  text-underline-offset: 3px;
}

.source-note a:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}
</style>
