import { describe, it } from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const srcDir = path.resolve(__dirname, '../src')

describe('Feature 079: Rótulos de Botões e Linhas Texto + Botão em Telas Estreitas', () => {
  it('US4: style.css define white-space: nowrap e flex-shrink: 0 na regra-base de botoes', () => {
    const stylePath = path.join(srcDir, 'style.css')
    const content = fs.readFileSync(stylePath, 'utf-8')
    assert.match(
      content,
      /button,\s*\.button\s*\{[^}]*white-space:\s*nowrap/s,
      'Regra base button, .button deve definir white-space: nowrap'
    )
    assert.match(
      content,
      /button,\s*\.button\s*\{[^}]*flex-shrink:\s*0/s,
      'Regra base button, .button deve definir flex-shrink: 0'
    )
  })

  it('US4: Controles Tipo C declaram white-space: normal nominalmente', () => {
    const conflictModalPath = path.join(srcDir, 'components/sync/ConflictResolutionModal.vue')
    const searchModalPath = path.join(srcDir, 'components/search/GlobalSearchModal.vue')
    const studySessionPath = path.join(srcDir, 'views/StudySessionView.vue')

    const conflictContent = fs.readFileSync(conflictModalPath, 'utf-8')
    const searchContent = fs.readFileSync(searchModalPath, 'utf-8')
    const sessionContent = fs.readFileSync(studySessionPath, 'utf-8')

    assert.match(
      conflictContent,
      /white-space:\s*normal/,
      'ConflictResolutionModal deve isentar cartoes-opcao com white-space: normal'
    )
    assert.match(
      searchContent,
      /white-space:\s*normal/,
      'GlobalSearchModal deve isentar banner/botao de modo com white-space: normal'
    )
    assert.match(
      sessionContent,
      /white-space:\s*normal/,
      'StudySessionView deve isentar botoes de avaliacao com white-space: normal'
    )
  })

  it('US2: TrashView.vue organiza barra de lote com flex-wrap e variantes de rotulo curto', () => {
    const trashPath = path.join(srcDir, 'views/TrashView.vue')
    const content = fs.readFileSync(trashPath, 'utf-8')
    assert.match(
      content,
      /trash-batch-bar|batch-actions/s,
      'TrashView deve conter estilos para a barra de acoes em lote'
    )
    assert.match(
      content,
      /flex-wrap:\s*wrap/,
      'Barra de lote ou grupo de botoes da lixeira deve permitir flex-wrap'
    )
  })

  it('US2: ReviewPedagogicalEmpty e modais de resumo reorganizam botoes para telas estreitas', () => {
    const emptyPath = path.join(srcDir, 'components/review/ReviewPedagogicalEmpty.vue')
    const summaryPath = path.join(srcDir, 'components/review/ReviewSummaryModal.vue')

    const emptyContent = fs.readFileSync(emptyPath, 'utf-8')
    const summaryContent = fs.readFileSync(summaryPath, 'utf-8')

    assert.match(
      emptyContent,
      /btn-text-short|btn-text-full|max-width|flex-wrap/,
      'ReviewPedagogicalEmpty deve conter adaptacao para telas estreitas'
    )
    assert.match(
      summaryContent,
      /flex-wrap:\s*wrap/,
      'ReviewSummaryModal deve suportar flex-wrap nas acoes de rodape'
    )
  })

  it('US2: HeroSection e PublicFooter flexibilizam botoes sem corte por altura rigida', () => {
    const heroPath = path.join(srcDir, 'components/landing/HeroSection.vue')
    const footerPath = path.join(srcDir, 'components/landing/PublicFooter.vue')

    const heroContent = fs.readFileSync(heroPath, 'utf-8')
    const footerContent = fs.readFileSync(footerPath, 'utf-8')

    assert.doesNotMatch(
      heroContent,
      /height:\s*48px;\s*overflow:\s*hidden/,
      'HeroSection nao deve cortar texto de botao com height fixa e overflow hidden'
    )
    assert.doesNotMatch(
      footerContent,
      /height:\s*48px;\s*overflow:\s*hidden/,
      'PublicFooter nao deve cortar texto de botao com height fixa e overflow hidden'
    )
  })

  it('US2: SessionsManager e SettingsView reorganizam acoes para telas estreitas com alvos minimos', () => {
    const sessionsPath = path.join(srcDir, 'components/auth/SessionsManager.vue')
    const settingsPath = path.join(srcDir, 'views/SettingsView.vue')

    const sessionsContent = fs.readFileSync(sessionsPath, 'utf-8')
    const settingsContent = fs.readFileSync(settingsPath, 'utf-8')

    assert.match(
      sessionsContent,
      /min-height:\s*44px/,
      'SessionsManager deve definir min-height de 44px nos botoes de acao'
    )
    assert.match(
      sessionsContent,
      /@media\s*\(max-width:\s*640px\)/,
      'SessionsManager deve conter adaptacao de empilhamento para telas estreitas'
    )
    assert.match(
      settingsContent,
      /@media\s*\(max-width:\s*640px\)/,
      'SettingsView deve conter adaptacao de empilhamento para acoes'
    )
  })

  it('US3: style.css padroniza .section-heading e .save-bar com flex-wrap e protecao de estrangulamento', () => {
    const stylePath = path.join(srcDir, 'style.css')
    const content = fs.readFileSync(stylePath, 'utf-8')

    assert.match(
      content,
      /\.section-heading\s*\{[^}]*flex-wrap:\s*wrap/s,
      '.section-heading deve possuir flex-wrap: wrap para permitir empilhamento'
    )
    assert.match(
      content,
      /\.save-bar\s*\{[^}]*flex-wrap:\s*wrap/s,
      '.save-bar deve possuir flex-wrap: wrap'
    )
    assert.match(
      content,
      /\.save-bar\s+p\s*\{[^}]*flex:\s*1\s+1\s+12rem/s,
      '.save-bar p deve possuir base flexivel de 12rem para evitar estrangulamento'
    )
  })

  it('Conformidade de estilo: Zero presenca de emojis nos arquivos modificados', () => {
    const filesToCheck = [
      'style.css',
      'views/TrashView.vue',
      'views/ReviewHubView.vue',
      'components/review/ReviewPedagogicalEmpty.vue',
      'components/review/ReviewSummaryModal.vue',
      'components/session/SessionSummaryModal.vue',
      'components/landing/HeroSection.vue',
      'components/landing/PublicFooter.vue',
      'components/auth/SessionsManager.vue',
      'views/SettingsView.vue',
      'components/sync/ConflictResolutionModal.vue',
      'components/search/GlobalSearchModal.vue',
      'views/StudySessionView.vue'
    ]

    const emojiRegex = /[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u

    for (const file of filesToCheck) {
      const fullPath = path.join(srcDir, file)
      if (fs.existsSync(fullPath)) {
        const content = fs.readFileSync(fullPath, 'utf-8')
        assert.doesNotMatch(
          content,
          emojiRegex,
          `Arquivo ${file} nao deve conter nenhum caractere emoji`
        )
      }
    }
  })
})
