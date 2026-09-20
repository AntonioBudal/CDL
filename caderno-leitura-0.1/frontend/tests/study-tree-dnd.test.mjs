import test from 'node:test'
import assert from 'node:assert/strict'

const {
  calculateDropIntent,
} = await import('../src/composables/useStudyHierarchy.ts')

// ==========================================
// User Story 2: Reorganização por Drag-and-Drop e Prevenção de Ciclos
// ==========================================

test('calculateDropIntent identifica topo do card como inserção antes (before)', () => {
  const result = calculateDropIntent(10, 100, 1, 2)
  assert.equal(result.position, 'before')
  assert.equal(result.allowed, true)
})

test('calculateDropIntent identifica base do card como inserção depois (after)', () => {
  const result = calculateDropIntent(85, 100, 1, 2)
  assert.equal(result.position, 'after')
  assert.equal(result.allowed, true)
})

test('calculateDropIntent identifica centro do card como aninhamento (inside)', () => {
  const result = calculateDropIntent(50, 100, 1, 2, () => true)
  assert.equal(result.position, 'inside')
  assert.equal(result.allowed, true)
})

test('calculateDropIntent bloqueia aninhamento quando canNestUnder proíbe ciclo', () => {
  // Simula que canNestUnder detectou ciclo e retornou false
  const result = calculateDropIntent(50, 100, 1, 2, () => false)
  assert.equal(result.position, null)
  assert.equal(result.allowed, false)
})

test('calculateDropIntent bloqueia soltar sobre si mesmo', () => {
  const result = calculateDropIntent(50, 100, 1, 1)
  assert.equal(result.position, null)
  assert.equal(result.allowed, false)
})
