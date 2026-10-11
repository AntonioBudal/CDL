import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const srcDir = path.resolve(process.cwd(), 'src')

test('US1: ReviewStatsHeader implementa a Barra Unificada de Prontidão Intelectual sem os 5 cards legados', () => {
  const headerPath = path.resolve(srcDir, 'components/review/ReviewStatsHeader.vue')
  assert.ok(fs.existsSync(headerPath), 'ReviewStatsHeader.vue deve existir')

  const content = fs.readFileSync(headerPath, 'utf-8')

  // Estrutura unificada de prontidão
  assert.ok(content.includes('readiness-banner'), 'Deve conter a classe readiness-banner')
  assert.ok(content.includes('readiness-headline'), 'Deve conter o bloco readiness-headline')
  assert.ok(content.includes('readiness-breakdown'), 'Deve conter a decomposição semântica em linha')
  assert.ok(content.includes('estimated-time'), 'Deve conter estimativa de tempo de sessão')
  assert.ok(content.includes('estimatedMinutes'), 'Deve computar estimatedMinutes')

  // Disparador de prática evidente
  assert.ok(content.includes('btn-start-practice'), 'Deve conter botão primário btn-start-practice')
  assert.ok(content.includes('data-testid="start-practice-btn"'), 'Deve conter data-testid para start-practice-btn')
  assert.ok(content.includes('Praticar Revisão Agora'), 'Deve conter texto imperativo do botão')
  assert.ok(content.includes("emit('start-practice')"), 'Deve emitir evento start-practice')

  // Banimento dos 5 cards dispersos de SaaS
  assert.ok(!content.includes('review-stat-card'), 'Não deve conter classes legadas de review-stat-card')

  // Imunidade cromática: banimento de cores rígidas
  assert.ok(!content.includes('#2563eb'), 'Não deve conter azul hex rígido #2563eb')
  assert.ok(!content.includes('#16a34a'), 'Não deve conter verde hex rígido #16a34a')
  assert.ok(!content.includes('#dc2626'), 'Não deve conter vermelho hex rígido #dc2626')

  // Banimento de emojis
  const emojiRegex = /[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u
  assert.ok(!emojiRegex.test(content), 'ReviewStatsHeader.vue não deve conter emojis')
})

test('US3: ReviewPedagogicalEmpty fornece demonstração viva de termo oculto e guia de 3 passos', () => {
  const emptyPath = path.resolve(srcDir, 'components/review/ReviewPedagogicalEmpty.vue')
  assert.ok(fs.existsSync(emptyPath), 'ReviewPedagogicalEmpty.vue deve existir')

  const content = fs.readFileSync(emptyPath, 'utf-8')

  // Acessibilidade e cabeçalho acolhedor
  assert.ok(content.includes('role="region"'), 'Deve definir região semântica acessível')
  assert.ok(content.includes('aria-label="Guia Pedagógico de Revisão e Estudo Ativo"'), 'Deve ter rótulo acessível')
  assert.ok(content.includes('hero-title'), 'Deve conter título do hero')

  // Demonstração interativa de termo oculto
  assert.ok(content.includes('interactive-demo-card'), 'Deve conter o card de demonstração interativa')
  assert.ok(content.includes('demo-gap-btn'), 'Deve conter o botão de termo oculto interativo')
  assert.ok(content.includes('isDemoRevealed'), 'Deve gerenciar estado reativo de revelação')
  assert.ok(content.includes('[ termo oculto ]'), 'Deve exibir placeholder de termo oculto')
  assert.ok(content.includes('recuperar'), 'Deve revelar a palavra da demonstração didática')
  assert.ok(content.includes('toggleDemo'), 'Deve alternar visibilidade ao clique')

  // Guia de 3 passos instrucionais
  assert.ok(content.includes('guide-steps-grid'), 'Deve conter grade de passos didáticos')
  assert.ok(content.includes('guide-step-card'), 'Deve conter cartões de passos')
  assert.ok(content.includes('handleGoToBooks'), 'Deve permitir navegação direta para o acervo de livros')

  // Banimento de cores hex saturadas
  assert.ok(!content.includes('#2563eb'), 'Não deve conter azul hex rígido #2563eb')
  assert.ok(!content.includes('#16a34a'), 'Não deve conter verde hex rígido #16a34a')

  // Banimento de emojis
  const emojiRegex = /[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u
  assert.ok(!emojiRegex.test(content), 'ReviewPedagogicalEmpty.vue não deve conter emojis')
})

test('US1/US3: ReviewHubView integra a Barra de Prontidão e o Estado Vazio Pedagógico', () => {
  const viewPath = path.resolve(srcDir, 'views/ReviewHubView.vue')
  assert.ok(fs.existsSync(viewPath), 'ReviewHubView.vue deve existir')

  const content = fs.readFileSync(viewPath, 'utf-8')

  // Integração com os novos componentes
  assert.ok(content.includes('ReviewStatsHeader'), 'Deve importar e utilizar ReviewStatsHeader')
  assert.ok(content.includes('ReviewPedagogicalEmpty'), 'Deve importar e utilizar ReviewPedagogicalEmpty')
  assert.ok(content.includes('@start-practice="startReview"'), 'Deve conectar o evento @start-practice')

  // Banimento de emojis
  const emojiRegex = /[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u
  assert.ok(!emojiRegex.test(content), 'ReviewHubView.vue não deve conter emojis')
})
