import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const heatmapVuePath = resolve(__dirname, '../src/components/HeatmapCalendar.vue')
const heatmapSource = readFileSync(heatmapVuePath, 'utf-8')

test('US4: HeatmapCalendar define tokens de opacidade atenuada para dias vazios (.level-0)', () => {
  // Verifica se o token de opacidade vazia é definido no root padrão
  assert.ok(
    heatmapSource.includes('--heatmap-cell-empty-opacity: 0.6'),
    'Deve definir --heatmap-cell-empty-opacity padrão de 0.6 para o tema clássico'
  )

  // Verifica temas escuros (breu, vinil, vespera, fiorde, dark)
  assert.ok(
    heatmapSource.includes('--heatmap-cell-empty-opacity: 0.45'),
    'Deve atenuar a opacidade das células vazias para 0.45 nos temas escuros'
  )

  // Verifica temas sépia (pergaminho, sequoia, sepia)
  assert.ok(
    heatmapSource.includes('--heatmap-cell-empty-opacity: 0.5'),
    'Deve atenuar a opacidade das células vazias para 0.5 nos temas sépia e e-ink'
  )

  // Verifica temas solarizados (solario, voltagem, solarized)
  assert.ok(
    heatmapSource.includes('--heatmap-cell-empty-opacity: 0.55'),
    'Deve atenuar a opacidade das células vazias para 0.55 nos temas solarizados'
  )
})

test('US4: Células com atividade (.level-1 a .level-3) possuem opacidade plena (1.0)', () => {
  assert.ok(
    heatmapSource.includes('.level-1,\n.level-2,\n.level-3 {\n  opacity: 1;\n}'),
    'Células com atividade devem ter opacidade 1.0 plena para contraste inequívoco'
  )
})

test('US4: Modo E-Ink utiliza borda tracejada para level-0 e sólida para dias com atividade', () => {
  assert.ok(
    heatmapSource.includes(':root[data-theme="e-ink"] .level-0') &&
    heatmapSource.includes('border-style: dashed;'),
    'Tema E-Ink deve usar borda tracejada para células sem atividade'
  )

  assert.ok(
    heatmapSource.includes(':root[data-theme="e-ink"] .level-1') &&
    heatmapSource.includes('border-style: solid;'),
    'Tema E-Ink deve usar borda sólida para células com atividade'
  )
})
