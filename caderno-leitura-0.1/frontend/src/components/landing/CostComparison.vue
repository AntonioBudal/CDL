<script setup lang="ts">
/** Quanto custa (F0.10.08, spec 101): preços só com fonte e data de consulta, em dólar, como nas fontes. */
import { vReveal } from '../../composables/useReveal'
import { COST_ROWS, LEITORUM_COST, formatCheckedAt, formatUsd, yearlyTotal } from './costSources'
</script>

<template>
  <section id="custo" class="cost-section" aria-labelledby="cost-heading">
    <h2 v-reveal id="cost-heading" class="section-title">Quanto custa</h2>

    <div v-reveal class="cost-card cost-card-leitorum">
      <h3 class="cost-product">Leitorum</h3>
      <p class="cost-price">{{ formatUsd(LEITORUM_COST.license) }} <span class="cost-muted">de licença</span></p>
      <p class="cost-text">{{ LEITORUM_COST.note }}</p>
      <p class="cost-source">
        Fonte:
        <a :href="LEITORUM_COST.sourceUrl" target="_blank" rel="noopener noreferrer">{{ LEITORUM_COST.sourceLabel }}</a>
      </p>
    </div>

    <div v-for="row in COST_ROWS" :key="row.product" v-reveal class="cost-card">
      <h3 class="cost-product">{{ row.product }}</h3>
      <p class="cost-muted">{{ row.kind }}</p>
      <div class="cost-table-wrap" tabindex="0" role="region" :aria-label="`Tabela de preços do ${row.product}`">
        <table class="cost-table">
          <caption class="visually-hidden">Preços do {{ row.product }} em dólares</caption>
          <thead>
            <tr>
              <th scope="col">Plano</th>
              <th scope="col">Plano anual (por mês)</th>
              <th scope="col">Total por ano</th>
              <th scope="col">Plano mensal</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="plan in row.plans" :key="plan.name">
              <th scope="row">{{ plan.name }}</th>
              <td>{{ formatUsd(plan.yearlyMonthly) }}</td>
              <td>{{ yearlyTotal(plan) }}</td>
              <td>{{ plan.monthly === null ? '—' : formatUsd(plan.monthly) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-if="row.note" class="cost-muted">{{ row.note }}</p>
      <p class="cost-source">
        Fonte:
        <a :href="row.sourceUrl" target="_blank" rel="noopener noreferrer">{{ row.sourceLabel }}</a>,
        consultada em <time :datetime="row.checkedAt">{{ formatCheckedAt(row.checkedAt) }}</time>.
      </p>
    </div>

    <p v-reveal class="cost-note">
      Preços de terceiros mudam; confira na fonte. Comparamos custo, não recursos. Valores em dólar, como nas fontes,
      sem conversão.
    </p>
  </section>
</template>

<style scoped>
.cost-section {
  padding-block: clamp(2.5rem, 6vw, 4.5rem);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.section-title {
  font-family: var(--font-reading, "Caderno EB Garamond", serif);
  font-size: clamp(1.75rem, 3vw, 2.4rem);
  font-weight: 600;
  line-height: 1.2;
  margin: 0 0 0.75rem 0;
  color: var(--color-text);
}

.cost-card {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 1.25rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 14px;
  min-width: 0;
}

.cost-product {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--color-text);
}

.cost-price {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text);
}

.cost-text {
  margin: 0;
  line-height: 1.5;
  color: var(--color-text);
}

.cost-muted {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 400;
  color: var(--color-muted);
}

.cost-table-wrap {
  overflow-x: auto;
  max-width: 100%;
}

.cost-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
  color: var(--color-text);
}

.cost-table th,
.cost-table td {
  text-align: left;
  padding: 0.5rem 0.6rem;
  border-bottom: 1px solid var(--color-border);
  white-space: nowrap;
}

.cost-table thead th {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-muted);
}

.cost-table tbody th {
  font-weight: 600;
}

.cost-source {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-text);
}

.cost-source a {
  color: var(--color-link);
  text-decoration: underline;
  text-underline-offset: 3px;
  overflow-wrap: anywhere;
}

.cost-note {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-muted);
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
</style>
