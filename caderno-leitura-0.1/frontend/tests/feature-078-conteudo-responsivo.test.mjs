import { describe, it } from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const srcDir = path.resolve(__dirname, '../src')

describe('Feature 078: Leitor e Disposicao de Conteudo Responsivo', () => {
  it('US1: useSplitPanes.ts inicializa leftCollapsed como true em mobile sem stored', () => {
    const splitPanesPath = path.join(srcDir, 'composables/useSplitPanes.ts')
    const content = fs.readFileSync(splitPanesPath, 'utf-8')
    assert.match(
      content,
      /layoutMode|windowWidth|isMobile|mobile/i,
      'useSplitPanes deve considerar viewport mobile na definicao'
    )
    assert.match(
      content,
      /leftCollapsed.*(?:stored|\?|mobile)/s,
      'leftCollapsed deve iniciar recolhido em modo mobile quando nao houver dimensao salva'
    )
  })

  it('US1: BookView.vue reorganiza acoes do cabecalho e alvos táteis mínimos', () => {
    const bookViewPath = path.join(srcDir, 'views/BookView.vue')
    const content = fs.readFileSync(bookViewPath, 'utf-8')
    assert.match(
      content,
      /splitLayoutRef\?\.leftCollapsed/s,
      'BookView deve manter controle de recolhimento da gaveta de capitulos'
    )
    assert.match(
      content,
      /(?:header-actions|book-header-actions|header-actions-menu)/s,
      'BookView deve organizar as acoes do cabecalho'
    )
    assert.match(
      content,
      /min-height:\s*44px|min-width:\s*44px|min-height:\s*2\.75rem|min-height:\s*var\(--space-touch\)|padding:\s*12px/s,
      'BookView deve ter alvos tateis ergonomicos para mobile'
    )
  })

  it('US2: AdminUsersTable.vue suporta modo de cartoes adaptativos em telas estreitas', () => {
    const adminTablePath = path.join(srcDir, 'components/admin/AdminUsersTable.vue')
    const content = fs.readFileSync(adminTablePath, 'utf-8')
    assert.match(
      content,
      /@media\s*\(\s*max-width:\s*767px\s*\)|@media\s*\(\s*max-width:\s*768px\s*\)/,
      'AdminUsersTable deve possuir media query para adaptacao em telas pequenas'
    )
    assert.match(
      content,
      /user-card|card-view|display:\s*(?:flex|grid|block)/,
      'AdminUsersTable deve estilizar apresentacao em cartoes ou blocos no mobile'
    )
    assert.match(
      content,
      /min-height:\s*44px|min-height:\s*2\.75rem|height:\s*44px|min-width:\s*44px/,
      'Acoes de administracao devem possuir altura/alvo tátil de pelo menos 44px'
    )
  })

  it('US3: FriendsView, AdminView e SovereigntySection suportam viewports de 320px sem overflow', () => {
    const friendsPath = path.join(srcDir, 'views/FriendsView.vue')
    const adminPath = path.join(srcDir, 'views/AdminView.vue')
    const sovereigntyPath = path.join(srcDir, 'components/landing/SovereigntySection.vue')

    const friendsContent = fs.readFileSync(friendsPath, 'utf-8')
    const adminContent = fs.readFileSync(adminPath, 'utf-8')
    const sovereigntyContent = fs.readFileSync(sovereigntyPath, 'utf-8')

    assert.doesNotMatch(
      friendsContent,
      /minmax\(280px,\s*1fr\)/,
      'FriendsView nao deve ter minmax rigido de 280px sem adaptacao fluida'
    )
    assert.doesNotMatch(
      adminContent,
      /minmax\(280px,\s*1fr\)/,
      'AdminView nao deve ter minmax rigido de 280px sem adaptacao fluida'
    )
    assert.doesNotMatch(
      sovereigntyContent,
      /minmax\(280px,\s*1fr\)/,
      'SovereigntySection nao deve ter minmax rigido de 280px sem adaptacao fluida'
    )
  })

  it('US4: Modais adotam declaracao com dvh para compatibilidade dinamica', () => {
    const bookEditPath = path.join(srcDir, 'components/BookEditModal.vue')
    const historyPath = path.join(srcDir, 'components/StudyHistoryModal.vue')
    const exportPath = path.join(srcDir, 'components/ExportModal.vue')

    const bookEditContent = fs.readFileSync(bookEditPath, 'utf-8')
    const historyContent = fs.readFileSync(historyPath, 'utf-8')
    const exportContent = fs.readFileSync(exportPath, 'utf-8')

    assert.match(bookEditContent, /90dvh/, 'BookEditModal deve ter declaracao com dvh')
    assert.match(historyContent, /85dvh/, 'StudyHistoryModal deve ter declaracao com dvh')
    assert.match(exportContent, /85dvh/, 'ExportModal deve ter declaracao com dvh')
  })

  it('US4: Regras de hover com elevacao estao protegidas por hover: hover e pointer: fine', () => {
    const stylePath = path.join(srcDir, 'style.css')
    const styleContent = fs.readFileSync(stylePath, 'utf-8')

    assert.match(
      styleContent,
      /@media\s*\(\s*hover:\s*hover\s*\)\s*and\s*\(\s*pointer:\s*fine\s*\)/,
      'style.css deve proteger transforms em :hover contra dispositivos capacitivos'
    )
  })

  it('Conformidade de estilo: Zero presenca de emojis nos arquivos modificados', () => {
    const filesToCheck = [
      'composables/useSplitPanes.ts',
      'views/BookView.vue',
      'components/admin/AdminUsersTable.vue',
      'views/FriendsView.vue',
      'views/AdminView.vue',
      'components/landing/SovereigntySection.vue',
      'components/BookEditModal.vue',
      'components/ExportModal.vue',
      'components/StudyHistoryModal.vue',
      'style.css'
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
