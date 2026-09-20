import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = dirname(fileURLToPath(import.meta.url))

const modalSource = readFileSync(
  resolve(__dirname, '../src/components/search/GlobalSearchModal.vue'),
  'utf-8'
)
const resultItemSource = readFileSync(
  resolve(__dirname, '../src/components/search/SearchResultItem.vue'),
  'utf-8'
)
const appSource = readFileSync(
  resolve(__dirname, '../src/App.vue'),
  'utf-8'
)

test('FR-010 e SC-006: Modal possui contenção estrita contra overflow horizontal', () => {
  assert.ok(
    modalSource.includes('overflow-x-hidden'),
    'GlobalSearchModal deve possuir overflow-x-hidden para blindagem contra rolagem lateral'
  )
})

test('FR-010 e SC-006: Controles interativos respeitam área tátil mínima de 44px no mobile', () => {
  assert.ok(
    modalSource.includes('min-h-[44px]'),
    'Input, seletores e botões devem ter altura mínima de 44px'
  )
  assert.ok(
    modalSource.includes('min-w-[44px]'),
    'Botão de fechar e ações principais devem ter largura mínima de 44px'
  )
})

test('FR-010: Modal implementa atributos semânticos de diálogo e acessibilidade WAI-ARIA', () => {
  assert.ok(
    modalSource.includes('role="dialog"'),
    'Modal deve possuir role="dialog"'
  )
  assert.ok(
    modalSource.includes('aria-modal="true"'),
    'Modal deve possuir aria-modal="true"'
  )
  assert.ok(
    modalSource.includes('aria-label="Busca global de estudos"'),
    'Modal deve possuir rótulo acessível aria-label'
  )
  assert.ok(
    modalSource.includes('aria-live="polite"'),
    'Contagem de resultados deve ser anunciada para leitores de tela com aria-live="polite"'
  )
})

test('FR-010: Suporte a atalhos de teclado (Ctrl+K, /, Esc, setas cima e baixo)', () => {
  assert.ok(
    modalSource.includes("e.key.toLowerCase() === 'k'") && modalSource.includes('e.ctrlKey'),
    'Deve capturar atalho Ctrl+K'
  )
  assert.ok(
    modalSource.includes("e.key === 'Escape'"),
    'Deve fechar o modal com a tecla Escape'
  )
  assert.ok(
    modalSource.includes("e.key === 'ArrowDown'") && modalSource.includes("e.key === 'ArrowUp'"),
    'Deve permitir navegar nos resultados com as setas do teclado'
  )
})

test('FR-001: Botão de busca está integrado na barra superior em App.vue com rótulo acessível', () => {
  assert.ok(
    appSource.includes('search-trigger-btn'),
    'App.vue deve conter o botão disparador de busca'
  )
  assert.ok(
    appSource.includes('aria-label="Abrir busca global de estudos (Ctrl+K)"'),
    'Botão de busca deve ter aria-label claro'
  )
})
