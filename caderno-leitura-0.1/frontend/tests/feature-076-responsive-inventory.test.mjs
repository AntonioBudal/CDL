import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const testDir = path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1'))
const frontendDir = path.resolve(testDir, '..')

function findRepoRoot(startDir) {
  let curr = startDir
  while (curr && curr !== path.dirname(curr)) {
    if (fs.existsSync(path.join(curr, 'specs', '076-estrategia-responsiva'))) {
      return curr
    }
    curr = path.dirname(curr)
  }
  return path.resolve(startDir, '../../..')
}

const repoRoot = findRepoRoot(testDir)

test('Feature 076: Toda rota nomeada em router/index.ts deve constar no contrato de decisões de responsividade', () => {
  const routerPath = path.join(frontendDir, 'src', 'router', 'index.ts')
  const contractPath = path.join(repoRoot, 'specs', '076-estrategia-responsiva', 'contracts', 'responsive-decisions.contract.md')

  assert.ok(fs.existsSync(routerPath), 'router/index.ts deve existir')
  assert.ok(fs.existsSync(contractPath), 'responsive-decisions.contract.md deve existir')

  const routerContent = fs.readFileSync(routerPath, 'utf8')
  const contractContent = fs.readFileSync(contractPath, 'utf8')

  // Extrair todos os identificadores de rota: name: '...' ou name: "..."
  const routeNameRegex = /name:\s*['"]([^'"]+)['"]/g
  const matchedRouteNames = []
  let match
  while ((match = routeNameRegex.exec(routerContent)) !== null) {
    matchedRouteNames.push(match[1])
  }

  assert.ok(matchedRouteNames.length > 0, 'Deve encontrar pelo menos 1 rota nomeada no roteador')

  // Desduplicar nomes de rotas
  const uniqueRouteNames = [...new Set(matchedRouteNames)]

  // Validar que cada rota está documentada na tabela de decisões
  const missingRoutes = []
  for (const routeName of uniqueRouteNames) {
    // Procura por `routeName` no formato de código de markdown: `routeName`
    const pattern = new RegExp(`\`${routeName}\``)
    if (!pattern.test(contractContent)) {
      missingRoutes.push(routeName)
    }
  }

  assert.deepEqual(
    missingRoutes,
    [],
    `As seguintes rotas nomeadas de router/index.ts não constam do contrato de decisões:\n${missingRoutes.join(', ')}`
  )
})

test('Feature 076: Contrato de decisões possui detalhamento das 3 visualizações complexas (Map, Canvas e Tree)', () => {
  const contractPath = path.join(repoRoot, 'specs', '076-estrategia-responsiva', 'contracts', 'responsive-decisions.contract.md')
  const contractContent = fs.readFileSync(contractPath, 'utf8')

  assert.ok(contractContent.includes('StudyMapView.vue'), 'Contrato deve detalhar Map View')
  assert.ok(contractContent.includes('StudyCanvasView.vue'), 'Contrato deve detalhar Canvas View')
  assert.ok(contractContent.includes('StudyTreeNodeItem.vue'), 'Contrato deve detalhar Tree View')
  assert.ok(contractContent.includes('Classificação 3'), 'Map View deve ser classificado como 3')
  assert.ok(contractContent.includes('Classificação 4'), 'Canvas View deve ser classificado como 4')
  assert.ok(contractContent.includes('Classificação 2'), 'Tree View deve ser classificado como 2')
})
