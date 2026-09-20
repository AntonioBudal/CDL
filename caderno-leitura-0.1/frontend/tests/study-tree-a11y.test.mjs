import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

// ==========================================
// User Story 3: Ergonomia Móvel e Acessibilidade (WAI-ARIA & 44x44px)
// ==========================================

test('StudyTreeNodeItem.vue define alvos de toque minimos de 44x44px para resolucoes moveis', () => {
  const componentPath = path.resolve('src/components/views/StudyTreeNodeItem.vue')
  const content = fs.readFileSync(componentPath, 'utf-8')

  // Verifica se o seletor de media query para mobile define min-width e min-height de 44px
  assert.ok(content.includes('@media (max-width: 768px)'), 'Deve conter media query para mobile <= 768px')
  assert.ok(content.includes('min-width: 44px;'), 'Deve conter min-width: 44px para touch-target')
  assert.ok(content.includes('min-height: 44px;'), 'Deve conter min-height: 44px para touch-target')
  assert.ok(content.includes('touch-target'), 'Deve aplicar classe touch-target nos botões')
})

test('StudyTreeNodeItem.vue inclui as 4 acoes rapidas de reorganizacao tatil', () => {
  const componentPath = path.resolve('src/components/views/StudyTreeNodeItem.vue')
  const content = fs.readFileSync(componentPath, 'utf-8')

  assert.ok(content.includes("triggerMove('up'"), 'Deve conter ação de mover para cima')
  assert.ok(content.includes("triggerMove('down'"), 'Deve conter ação de mover para baixo')
  assert.ok(content.includes("triggerMove('demote'"), 'Deve conter ação de recuar nó (aninhar)')
  assert.ok(content.includes("triggerMove('promote'"), 'Deve conter ação de promover nó')
})

test('StudyTreeView.vue possui navegacao por teclado acessivel WAI-ARIA Treeview', () => {
  const componentPath = path.resolve('src/components/views/StudyTreeView.vue')
  const content = fs.readFileSync(componentPath, 'utf-8')

  assert.ok(content.includes('role="tree"'), 'Contêiner deve ter role="tree"')
  assert.ok(content.includes('tabindex="0"'), 'Contêiner deve ser focável via teclado (tabindex="0")')
  assert.ok(content.includes('@keydown="handleTreeKeydown"'), 'Deve manipular eventos de teclado')
  assert.ok(content.includes('ArrowDown'), 'Deve suportar ArrowDown')
  assert.ok(content.includes('ArrowUp'), 'Deve suportar ArrowUp')
  assert.ok(content.includes('ArrowRight'), 'Deve suportar ArrowRight')
  assert.ok(content.includes('ArrowLeft'), 'Deve suportar ArrowLeft')
  assert.ok(content.includes('event.altKey'), 'Deve suportar atalhos estruturais com Alt')
})

test('Componentes respeitam prefers-reduced-motion', () => {
  const itemPath = path.resolve('src/components/views/StudyTreeNodeItem.vue')
  const itemContent = fs.readFileSync(itemPath, 'utf-8')
  assert.ok(itemContent.includes('@media (prefers-reduced-motion: reduce)'), 'StudyTreeNodeItem deve respeitar prefers-reduced-motion')

  const treePath = path.resolve('src/components/views/StudyTreeView.vue')
  const treeContent = fs.readFileSync(treePath, 'utf-8')
  assert.ok(treeContent.includes('@media (prefers-reduced-motion: reduce)'), 'StudyTreeView deve respeitar prefers-reduced-motion')
})
