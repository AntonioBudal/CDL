import test from 'node:test'
import assert from 'node:assert/strict'
import { normalizeCategoryText } from '../src/composables/useCategories.ts'

test('normalizeCategoryText normaliza diacríticos, pontuação e espaços em branco', () => {
  assert.equal(normalizeCategoryText('Ciências Humanas / Filosofia / Ética'), 'ciencias humanas / filosofia / etica')
  assert.equal(normalizeCategoryText('Lógica e Epistemologia'), 'logica e epistemologia')
  assert.equal(normalizeCategoryText('  Ficção   Científica  '), 'ficcao cientifica')
  assert.equal(normalizeCategoryText(''), '')
})

test('pesquisa e resolução de descendentes hierárquicos', () => {
  const sampleCategories = [
    { id: 'ciencias-humanas', name: 'Ciências Humanas', parent_id: null, path: 'Ciências Humanas' },
    { id: 'filosofia', name: 'Filosofia', parent_id: 'ciencias-humanas', path: 'Ciências Humanas / Filosofia' },
    { id: 'filosofia-etica', name: 'Ética', parent_id: 'filosofia', path: 'Ciências Humanas / Filosofia / Ética' },
    { id: 'filosofia-logica', name: 'Lógica', parent_id: 'filosofia', path: 'Ciências Humanas / Filosofia / Lógica' },
    { id: 'literatura', name: 'Literatura', parent_id: null, path: 'Literatura' },
    { id: 'literatura-brasileira', name: 'Literatura Brasileira', parent_id: 'literatura', path: 'Literatura / Literatura Brasileira' },
  ]

  // Testar busca por texto
  function search(query) {
    const term = normalizeCategoryText(query)
    const tokens = term.split(' ').filter(Boolean)
    return sampleCategories.filter(cat => {
      const normName = normalizeCategoryText(cat.name)
      const normPath = normalizeCategoryText(cat.path)
      return tokens.every(tok => normName.includes(tok) || normPath.includes(tok))
    })
  }

  // 1. Busca sem acento encontra categoria com acento
  const resEtica = search('etica')
  assert.equal(resEtica.length, 1)
  assert.equal(resEtica[0].id, 'filosofia-etica')

  // 2. Busca por palavra na trilha encontra as subcategorias
  const resFilosofia = search('filosofia')
  assert.equal(resFilosofia.length, 3)

  // 3. Testar resolução recursiva de descendentes
  const childrenMap = new Map()
  for (const cat of sampleCategories) {
    if (cat.parent_id) {
      const list = childrenMap.get(cat.parent_id) || []
      list.push(cat)
      childrenMap.set(cat.parent_id, list)
    }
  }

  function getDescendants(rootId) {
    const result = new Set([rootId])
    const queue = [rootId]
    while (queue.length > 0) {
      const curr = queue.shift()
      const children = childrenMap.get(curr)
      if (children) {
        for (const child of children) {
          if (!result.has(child.id)) {
            result.add(child.id)
            queue.push(child.id)
          }
        }
      }
    }
    return result
  }

  const humanDescendants = getDescendants('ciencias-humanas')
  assert.equal(humanDescendants.has('ciencias-humanas'), true)
  assert.equal(humanDescendants.has('filosofia'), true)
  assert.equal(humanDescendants.has('filosofia-etica'), true)
  assert.equal(humanDescendants.has('filosofia-logica'), true)
  assert.equal(humanDescendants.has('literatura'), false)

  const leafDescendants = getDescendants('filosofia-etica')
  assert.equal(leafDescendants.size, 1)
  assert.equal(leafDescendants.has('filosofia-etica'), true)
})
