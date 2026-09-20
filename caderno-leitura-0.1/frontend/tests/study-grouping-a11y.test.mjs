import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

// =============================================================================
// User Story 4: Ergonomia Móvel, Cabeçalhos Aderentes e Acessibilidade (T023 - T025)
// =============================================================================

test('GroupSection.vue implementa cabeçalhos aderentes (sticky headers) e semântica WAI-ARIA', () => {
  const componentPath = path.resolve('src/components/views/GroupSection.vue')
  const content = fs.readFileSync(componentPath, 'utf-8')

  // Semântica de marco WAI-ARIA
  assert.ok(content.includes('role="region"'), 'A seção deve ter role="region"')
  assert.ok(content.includes(':aria-labelledby="headingId"'), 'A seção deve estar vinculada ao seu título por aria-labelledby')
  assert.ok(content.includes('role="group"'), 'O contêiner de conteúdo deve ter role="group"')

  // Controle de alternância de colapso
  assert.ok(content.includes(':aria-expanded="!isCollapsed"'), 'Botão deve expor estado de expansão via aria-expanded')
  assert.ok(content.includes(':aria-controls="contentId"'), 'Botão deve controlar a área de conteúdo via aria-controls')
  assert.ok(content.includes(':aria-label='), 'Contador numérico de itens deve ter aria-label para tecnologias assistivas')

  // Cabeçalho aderente (Sticky positioning)
  assert.ok(content.includes('position: sticky;'), 'Header do grupo deve ter position: sticky')
  assert.ok(content.includes('top: 0;'), 'Header do grupo deve aderir ao topo (top: 0)')
  assert.ok(content.includes('z-index: 10;'), 'Header do grupo deve ter z-index para sobreposição na rolagem')
})

test('GroupSection.vue e GroupBySelector.vue cumprem requisitos de alvos táteis mínimos de 44px', () => {
  const sectionPath = path.resolve('src/components/views/GroupSection.vue')
  const sectionContent = fs.readFileSync(sectionPath, 'utf-8')

  // GroupSection toggle button
  assert.ok(sectionContent.includes('min-height: 44px;'), 'Botão de expansão do grupo deve ter min-height de 44px')

  const selectorPath = path.resolve('src/components/views/GroupBySelector.vue')
  const selectorContent = fs.readFileSync(selectorPath, 'utf-8')

  // GroupBySelector alvos táteis
  assert.ok(selectorContent.includes('min-height: 44px;'), 'Seletor nativo ou label deve garantir min-height de 44px')
  assert.ok(selectorContent.includes('.group-by-native-select'), 'Deve conter seletor nativo acessível')
  assert.ok(selectorContent.includes('for="study-group-by-select"'), 'Label deve estar associada ao select via atributo for')
  assert.ok(selectorContent.includes('id="study-group-by-select"'), 'Select deve ter id correspondente à label')
})

test('StudyStatusBadge.vue cumpre semântica de menu WAI-ARIA e alvos táteis mínimos de 44px', () => {
  const badgePath = path.resolve('src/components/StudyStatusBadge.vue')
  const content = fs.readFileSync(badgePath, 'utf-8')

  // Semântica de menu
  assert.ok(content.includes('role="menu"'), 'Menu de status deve ter role="menu"')
  assert.ok(content.includes('role="menuitem"'), 'Itens de status devem ter role="menuitem"')
  assert.ok(content.includes(':aria-expanded="isOpen"'), 'Gatilho interativo deve ter aria-expanded')
  assert.ok(content.includes('aria-haspopup="true"'), 'Gatilho interativo deve ter aria-haspopup="true"')

  // Alvo tátil das opções
  assert.ok(content.includes('min-height: 44px;'), 'Opções do menu dropdown de status devem ter min-height de 44px')
})
