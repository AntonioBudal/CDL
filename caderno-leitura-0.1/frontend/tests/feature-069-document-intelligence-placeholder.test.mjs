import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { DOCUMENT_INTELLIGENCE_STAGES, DIGITIZE_EXIT_SHORTCUTS } from '../src/types/digitize.ts'

const srcDir = path.resolve(process.cwd(), 'src')

test('US1: Rota /digitalizar registrada no router com alias /scan e componente correto', () => {
  const routerPath = path.resolve(srcDir, 'router/index.ts')
  assert.ok(fs.existsSync(routerPath), 'router/index.ts deve existir')

  const content = fs.readFileSync(routerPath, 'utf-8')

  assert.ok(content.includes('import DigitizeNotebookView from \'../views/DigitizeNotebookView.vue\''), 'Deve importar DigitizeNotebookView')
  assert.ok(content.includes("path: '/digitalizar'"), 'Deve registrar caminho /digitalizar')
  assert.ok(content.includes("alias: ['/scan']"), 'Deve conter alias /scan')
  assert.ok(content.includes("name: 'digitize-notebook'"), 'Deve nomear rota como digitize-notebook')
  assert.ok(content.includes("component: DigitizeNotebookView"), 'Deve associar o componente correto')
  assert.ok(content.includes("title: 'Digitalizar Caderno'"), 'Deve definir título da rota nos metadados')
})

test('US1: DigitizeNotebookView apresenta cabeçalho editorial e manifesto de privacidade 100% local', () => {
  const viewPath = path.resolve(srcDir, 'views/DigitizeNotebookView.vue')
  assert.ok(fs.existsSync(viewPath), 'DigitizeNotebookView.vue deve existir')

  const content = fs.readFileSync(viewPath, 'utf-8')

  // Cabeçalho e Título
  assert.ok(content.includes('Digitalizar Caderno'), 'Deve conter título principal Digitalizar Caderno')
  assert.ok(content.includes('role="main"'), 'Deve conter tag com role main')
  assert.ok(content.includes('Pesquisa Experimental'), 'Deve comunicar status de pesquisa experimental')

  // Manifesto de Soberania de Dados e Processamento Local
  assert.ok(content.includes('Processamento Estritamente Local no seu Computador'), 'Deve conter título de processamento local')
  assert.ok(content.includes('localmente, na sua própria máquina'), 'Deve garantir execução local na máquina do leitor')
  assert.ok(content.includes('Nenhuma foto, rascunho ou texto será transmitido a servidores em nuvem'), 'Deve conter garantia de não envio externo')
  assert.ok(content.includes('não há promessa de data de lançamento'), 'Deve explicitar ausência de promessa de data')

  // Banimento estrito de uploads, periféricos de câmera e chamadas de rede
  assert.ok(!content.includes('<input type="file"'), 'Não deve conter input de arquivo')
  assert.ok(!content.includes('type="file"'), 'Não deve conter atributo type file')
  assert.ok(!content.includes('mediaDevices'), 'Não deve acessar APIs de câmera')
  assert.ok(!content.includes('getUserMedia'), 'Não deve acessar getUserMedia')
  assert.ok(!content.includes('fetch('), 'Não deve efetuar chamadas fetch')
  assert.ok(!content.includes('axios'), 'Não deve conter chamadas axios')

  // Zero emojis
  const emojiRegex = /[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u
  assert.ok(!emojiRegex.test(content), 'DigitizeNotebookView.vue não deve conter emojis')
})

test('US2: Matriz de Maturidade contém exatamente os 4 marcos canônicos com notas transparentes', () => {
  assert.equal(DOCUMENT_INTELLIGENCE_STAGES.length, 4, 'Devem existir exatamente 4 estágios de maturidade')

  const [stage1, stage2, stage3, stage4] = DOCUMENT_INTELLIGENCE_STAGES

  assert.equal(stage1.title, 'Localizar linhas e blocos na página')
  assert.equal(stage1.status, 'validating')
  assert.equal(stage1.statusLabel, 'Em validação')
  assert.ok(stage1.technicalNote.includes('páginas sintéticas'))

  assert.equal(stage2.title, 'Ordem de leitura')
  assert.equal(stage2.status, 'validating')
  assert.equal(stage2.statusLabel, 'Em validação')

  assert.equal(stage3.title, 'Transcrição do texto manuscrito em português')
  assert.equal(stage3.status, 'researching')
  assert.equal(stage3.statusLabel, 'Em pesquisa')
  assert.ok(stage3.technicalNote.includes('português'))

  assert.equal(stage4.title, 'Classificação do conteúdo e diagramas')
  assert.equal(stage4.status, 'not_started')
  assert.equal(stage4.statusLabel, 'Não iniciado')

  // Validação no template
  const viewPath = path.resolve(srcDir, 'views/DigitizeNotebookView.vue')
  const content = fs.readFileSync(viewPath, 'utf-8')
  assert.ok(content.includes('DOCUMENT_INTELLIGENCE_STAGES'), 'Componente deve consumir DOCUMENT_INTELLIGENCE_STAGES')
  assert.ok(content.includes('badge-validating'), 'Deve conter classe CSS para status em validação')
  assert.ok(content.includes('badge-researching'), 'Deve conter classe CSS para status em pesquisa')
  assert.ok(content.includes('badge-not-started'), 'Deve conter classe CSS para status não iniciado')
})

test('US2: Ilustração Conceitual exibe rótulo explícito e dados fictícios sem tocar no acervo do leitor', () => {
  const viewPath = path.resolve(srcDir, 'views/DigitizeNotebookView.vue')
  const content = fs.readFileSync(viewPath, 'utf-8')

  assert.ok(content.includes('Ilustração Conceitual'), 'Deve conter tag destacada Ilustração Conceitual')
  assert.ok(content.includes('Visualização da Segmentação Geométrica'), 'Deve conter título explicativo da ilustração')
  assert.ok(content.includes('mockup-page-canvas'), 'Deve renderizar contêiner vetorial de exemplo')
  assert.ok(content.includes('Capítulo I — Do Hábito da Leitura Ativa'), 'Deve conter texto fictício neutro')
  assert.ok(content.includes('aria-hidden="true"'), 'A ilustração decorativa deve ser aria-hidden')
})

test('US3: Caminhos de saída para /importar e /inbox e card integrado no Ateliê de Fichamento', () => {
  assert.equal(DIGITIZE_EXIT_SHORTCUTS.length, 2, 'Devem existir 2 atalhos de saída')
  assert.equal(DIGITIZE_EXIT_SHORTCUTS[0].routePath, '/importar')
  assert.equal(DIGITIZE_EXIT_SHORTCUTS[1].routePath, '/inbox')

  // Validação na view DigitizeNotebookView
  const viewPath = path.resolve(srcDir, 'views/DigitizeNotebookView.vue')
  const viewContent = fs.readFileSync(viewPath, 'utf-8')
  assert.ok(viewContent.includes('DIGITIZE_EXIT_SHORTCUTS'), 'Deve renderizar atalhos de saída')
  assert.ok(viewContent.includes('btn-exit-action'), 'Deve conter botão de ação para saída')

  // Validação no ImportView.vue
  const importViewPath = path.resolve(srcDir, 'views/ImportView.vue')
  assert.ok(fs.existsSync(importViewPath), 'ImportView.vue deve existir')
  const importContent = fs.readFileSync(importViewPath, 'utf-8')

  assert.ok(importContent.includes('digitize-invitation-card'), 'ImportView deve conter o card de convite para digitalizar')
  assert.ok(importContent.includes('Caderno Manuscrito'), 'Deve conter título Caderno Manuscrito')
  assert.ok(importContent.includes('Em Pesquisa'), 'Deve exibir badge Em Pesquisa')
  assert.ok(importContent.includes('to="/digitalizar"'), 'Deve direcionar para /digitalizar')
  assert.ok(importContent.includes('Conhecer a proposta'), 'Deve conter ação Conhecer a proposta')

  const emojiRegex = /[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u
  assert.ok(!emojiRegex.test(importContent), 'ImportView.vue não deve conter emojis')
})

test('US4: Acessibilidade WAI-ARIA, touch targets mínimos (>= 44px) e imunidade cromática', () => {
  const viewPath = path.resolve(srcDir, 'views/DigitizeNotebookView.vue')
  const content = fs.readFileSync(viewPath, 'utf-8')

  // Acessibilidade e hierarquia
  assert.ok(content.includes('aria-labelledby="digitize-main-title"'), 'Deve ter aria-labelledby no main')
  assert.ok(content.includes('<h1'), 'Deve conter título H1')
  assert.ok(content.includes('<h2'), 'Deve conter subtítulos H2')
  assert.ok(content.includes('<h3'), 'Deve conter blocos H3')

  // Ergonomia tátil mobile
  assert.ok(content.includes('min-height: 44px'), 'Botões de ação devem ter no mínimo 44px de altura')

  // Imunidade cromática: consumo de tokens semânticos
  assert.ok(content.includes('var(--color-surface'), 'Deve consumir tokens de superfície')
  assert.ok(content.includes('var(--color-text'), 'Deve consumir tokens de texto')
  assert.ok(content.includes('var(--color-accent'), 'Deve consumir tokens de destaque')
  assert.ok(content.includes('var(--color-border-subtle'), 'Deve consumir tokens de borda')
})
