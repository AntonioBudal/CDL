import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const studyGridViewPath = path.resolve('src/components/views/StudyGridView.vue')

// ============================================================================
// User Story 1: Identidade Editorial & Reconhecimento Cromático de Status (P1 - MVP)
// ============================================================================

test('US1: StudyGridView.vue aplica friso vertical cromático de 4px na borda esquerda vinculado ao status', () => {
  const content = fs.readFileSync(studyGridViewPath, 'utf-8')

  // Classes de status no cartão
  assert.match(content, /status-rascunho/)
  assert.match(content, /status-em_andamento/)
  assert.match(content, /status-revisado/)
  assert.match(content, /status-concluido/)

  // Friso vertical lateral esquerdo de 4px no CSS
  assert.match(content, /border-left:\s*4px solid/s)
})

test('US1: StudyGridView.vue transforma o cartão em superfície integral de clique e acessibilidade de teclado', () => {
  const content = fs.readFileSync(studyGridViewPath, 'utf-8')

  // Artigo semântico com foco e evento de teclado
  assert.match(content, /<article[^>]*tabindex="0"/)
  assert.match(content, /@keydown\.enter/)
  assert.match(content, /@click="emit\('select-study',\s*study\.id\)"/)

  // Ação de lixeira isolada com @click.stop e aria-label
  assert.match(content, /@click\.stop="emit\('trash-study',\s*study\)"/)
  assert.match(content, /aria-label="Mover estudo para a lixeira"/)
})

// ============================================================================
// User Story 2: Cartografia de Densidade Analítica & Prévia do Resumo (P2)
// ============================================================================

test('US2: StudyGridView.vue renderiza prévia tipográfica de 2 a 3 linhas com corte suave', () => {
  const content = fs.readFileSync(studyGridViewPath, 'utf-8')

  // Prévia analítica baseada em summary_preview
  assert.match(content, /card-summary-preview/)
  assert.match(content, /study\.summary_preview/)

  // Estilização com line-clamp e overflow
  assert.match(content, /-webkit-line-clamp:\s*(2|3)/)
  assert.match(content, /display:\s*-webkit-box/)
})

test('US2: StudyGridView.vue exibe micro-badges de densidade no rodapé quando contagens > 0', () => {
  const content = fs.readFileSync(studyGridViewPath, 'utf-8')

  // Indicadores de destaques e relações
  assert.match(content, /study\.highlights_count/)
  assert.match(content, /study\.relations_count/)
  assert.match(content, /card-metrics/)
  assert.match(content, /metric-badge/)
})

// ============================================================================
// User Story 3: Grid Responsivo, Estados de Carregamento e Ergonomia Mobile (P3)
// ============================================================================

test('US3: StudyGridView.vue renderiza Skeleton Screens animados durante loading', () => {
  const content = fs.readFileSync(studyGridViewPath, 'utf-8')

  // Estado de loading e blocos de esqueleto
  assert.match(content, /skeleton-card/)
  assert.match(content, /loading/)
  assert.match(content, /skeleton-pulse|shimmer|skeleton-animation/)
})

test('US3: StudyGridView.vue adapta colunas (3, 2, 1) e garante alvos táteis mínimos de 44px', () => {
  const content = fs.readFileSync(studyGridViewPath, 'utf-8')

  // Media queries para colunas responsivas
  assert.match(content, /@media\s*\([^)]*max-width:\s*1024px\)/)
  assert.match(content, /@media\s*\([^)]*max-width:\s*(768px|640px)\)/)

  // Botões de ação no cartão com dimensões táteis mínimas de 44x44px
  assert.match(content, /min-width:\s*44px/)
  assert.match(content, /min-height:\s*44px/)
})
