import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { EDITOR_SECTION_TABS } from '../src/types.ts'

test('EDITOR_SECTION_TABS possui as 5 seções canônicas em português', () => {
  assert.equal(EDITOR_SECTION_TABS.length, 5)
  const keys = EDITOR_SECTION_TABS.map((t) => t.key)
  assert.deepEqual(keys, ['summary', 'explanation', 'concepts', 'references', 'notes'])

  const labels = EDITOR_SECTION_TABS.map((t) => t.label)
  assert.deepEqual(labels, ['Resumo', 'Explicação', 'Conceitos', 'Referências', 'Notas'])
})

test('StudyEditorFields.vue possui abas de navegação acessíveis com role="tablist" e role="tab"', () => {
  const filePath = path.resolve('src/components/StudyEditorFields.vue')
  const content = fs.readFileSync(filePath, 'utf-8')

  assert.ok(content.includes('role="tablist"'), 'Deve conter container com role="tablist"')
  assert.ok(content.includes('role="tab"'), 'Cada aba deve possuir role="tab"')
  assert.ok(content.includes('aria-selected'), 'Deve gerenciar aria-selected para a aba ativa')
  assert.ok(content.includes('activeTab'), 'Deve gerenciar a aba ativa')
})

test('StudyEditorFields.vue suporta modo focado e botão toggle para "todas as seções"', () => {
  const filePath = path.resolve('src/components/StudyEditorFields.vue')
  const content = fs.readFileSync(filePath, 'utf-8')

  assert.ok(content.includes('viewMode'), 'Deve gerenciar viewMode (focado vs all)')
  assert.ok(
    content.includes('Ver todas as seções') || content.includes('viewMode === \'all\''),
    'Deve prover toggle para ver todas as seções'
  )
  assert.ok(
    content.includes('has-content') || content.includes('hasContent') || content.includes('indicator'),
    'Deve indicar visualmente abas com conteúdo preenchido'
  )
})

test('StudyEditorFields.vue preserva campos de metadados quando showMetadata for true', () => {
  const filePath = path.resolve('src/components/StudyEditorFields.vue')
  const content = fs.readFileSync(filePath, 'utf-8')

  assert.ok(content.includes('v-if="showMetadata"'), 'Deve renderizar título e localização condicionalmente')
  assert.ok(content.includes('v-model="title"'), 'Deve fazer bind de title')
  assert.ok(content.includes('v-model="location"'), 'Deve fazer bind de location')
})
