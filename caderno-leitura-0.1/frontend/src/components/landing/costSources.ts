/**
 * Quanto custa (F0.10.08, spec 101). Regra do roadmap: preço só com fonte e data de consulta.
 * Preços em dólar, como nas fontes, sem conversão de câmbio. Para atualizar, conferir a fonte e trocar `checkedAt`.
 * O teste `feature-101-landing-confianca` recusa linha de preço sem `sourceUrl` https ou sem `checkedAt` ISO.
 */

export interface CostPlan {
  name: string
  /** Preço por mês no plano anual, em US$. */
  yearlyMonthly: number
  /** Preço no plano mensal, em US$ (null quando o plano não tem cobrança mensal). */
  monthly: number | null
}

export interface CostRow {
  product: string
  kind: string
  plans: CostPlan[]
  note?: string
  sourceUrl: string
  sourceLabel: string
  /** Data da consulta (AAAA-MM-DD). */
  checkedAt: string
}

export const LEITORUM_COST = {
  license: 0,
  note: 'Código público. Roda no computador ou servidor que você já tem; energia e máquina não são estimadas, porque dependem do seu caso.',
  sourceUrl: 'https://github.com/AntonioBudal/CDL',
  sourceLabel: 'github.com/AntonioBudal/CDL',
}

export const COST_ROWS: CostRow[] = [
  {
    product: 'Readwise',
    kind: 'Serviço de destaques e revisão diária (o mais parecido)',
    plans: [
      { name: 'Full', yearlyMonthly: 9.99, monthly: 12.99 },
      { name: 'Highlights', yearlyMonthly: 7.99, monthly: 8.99 },
      { name: 'Highlights Lite', yearlyMonthly: 5.59, monthly: 6.99 },
    ],
    sourceUrl: 'https://readwise.io/pricing',
    sourceLabel: 'readwise.io/pricing',
    checkedAt: '2026-11-07',
  },
  {
    product: 'Notion',
    kind: 'Caderno geral, não específico de leitura',
    plans: [
      { name: 'Free', yearlyMonthly: 0, monthly: 0 },
      { name: 'Plus', yearlyMonthly: 10, monthly: 12 },
    ],
    note: 'Preço por vaga.',
    sourceUrl: 'https://www.notion.com/pricing',
    sourceLabel: 'notion.com/pricing',
    checkedAt: '2026-11-07',
  },
]

/** "US$ 9,99" (vírgula decimal; inteiro sem casas). */
export function formatUsd(value: number): string {
  const text = Number.isInteger(value) ? String(value) : value.toFixed(2).replace('.', ',')
  return `US$ ${text}`
}

/** "07/11/2026" a partir de "2026-11-07". */
export function formatCheckedAt(iso: string): string {
  const [year, month, day] = iso.split('-')
  return `${day}/${month}/${year}`
}

/** Preço anual total arredondado em centavos ("US$ 119,88"). */
export function yearlyTotal(plan: CostPlan): string {
  return formatUsd(Math.round(plan.yearlyMonthly * 12 * 100) / 100)
}
