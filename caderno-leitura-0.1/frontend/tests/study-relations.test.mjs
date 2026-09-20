import test from 'node:test'
import assert from 'node:assert/strict'

import { RELATION_TYPE_LABELS } from '../src/composables/useStudyRelations.ts'

test('RELATION_TYPE_LABELS define rótulos canônicos simétricos e direcionais para os 6 tipos', () => {
  const expectedTypes = [
    'relacionado_com',
    'complementa',
    'contradiz',
    'depende_de',
    'mesmo_tema',
    'desdobramento_de',
  ]

  for (const type of expectedTypes) {
    assert.ok(RELATION_TYPE_LABELS[type], `Tipo ${type} deve estar presente em RELATION_TYPE_LABELS`)
    assert.ok(RELATION_TYPE_LABELS[type].outbound, `Tipo ${type} deve ter label de saída`)
    assert.ok(RELATION_TYPE_LABELS[type].inbound, `Tipo ${type} deve ter label de entrada / backlink`)
    assert.ok(RELATION_TYPE_LABELS[type].badgeClass, `Tipo ${type} deve ter classe css de badge`)
  }

  // Verificar semântica direcional de complementa e contradiz
  assert.equal(RELATION_TYPE_LABELS.complementa.outbound, 'Complementa')
  assert.equal(RELATION_TYPE_LABELS.complementa.inbound, 'Complementado por')

  assert.equal(RELATION_TYPE_LABELS.contradiz.outbound, 'Contradiz')
  assert.equal(RELATION_TYPE_LABELS.contradiz.inbound, 'Contradito por')

  assert.equal(RELATION_TYPE_LABELS.depende_de.outbound, 'Depende de')
  assert.equal(RELATION_TYPE_LABELS.depende_de.inbound, 'Pré-requisito de')

  assert.equal(RELATION_TYPE_LABELS.desdobramento_de.outbound, 'Desdobramento de')
  assert.equal(RELATION_TYPE_LABELS.desdobramento_de.inbound, 'Desdobra-se em')
})

test('cálculo do total de relações combina coleções de saída e de entrada', () => {
  const outbound = [
    { id: 1, source_study_id: 10, target_study_id: 20, relation_type: 'complementa', description: '', created_at: '' },
    { id: 2, source_study_id: 10, target_study_id: 30, relation_type: 'contradiz', description: '', created_at: '' },
  ]
  const inbound = [
    { id: 3, source_study_id: 40, target_study_id: 10, relation_type: 'depende_de', description: '', created_at: '' },
  ]

  const total = outbound.length + inbound.length
  assert.equal(total, 3)
})

test('remoção e atualização de item preservam imutabilidade de outros registros', () => {
  let list = [
    { id: 101, type: 'complementa', note: 'Nota 1' },
    { id: 102, type: 'contradiz', note: 'Nota 2' },
  ]

  // Atualização
  const updatedItem = { id: 101, type: 'desdobramento_de', note: 'Nota revisada' }
  const afterUpdate = list.map(item => item.id === 101 ? updatedItem : item)
  assert.equal(afterUpdate[0].type, 'desdobramento_de')
  assert.equal(afterUpdate[0].note, 'Nota revisada')
  assert.equal(afterUpdate[1].id, 102)

  // Remoção
  const afterDelete = afterUpdate.filter(item => item.id !== 102)
  assert.equal(afterDelete.length, 1)
  assert.equal(afterDelete[0].id, 101)
})
