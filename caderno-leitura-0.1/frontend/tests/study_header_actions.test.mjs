import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const studyViewPath = path.resolve('src/views/StudyView.vue')
const dropdownComponentPath = path.resolve('src/components/ui/DropdownMenu.vue')

test('StudyView.vue - Header Actions como Ícones Puros de 44x44px', () => {
  const content = fs.readFileSync(studyViewPath, 'utf-8')

  // Ações em header-actions formatadas como botões de ícone com SVG e acessibilidade
  assert.match(content, /class="secondary share-action header-icon-btn"/)
  assert.match(content, /class="secondary export-action header-icon-btn"/)
  assert.match(content, /class="secondary history-action header-icon-btn"/)
  assert.match(content, /class="button primary edit-action header-icon-btn"/)
  assert.match(content, /class="secondary danger-action header-icon-btn"/)

  // Atributos de acessibilidade WAI-ARIA e tooltips
  assert.match(content, /aria-label="Compartilhar estudo e gerenciar permissões"/)
  assert.match(content, /aria-label="Exportar estudo"/)
  assert.match(content, /aria-label="Abrir histórico de versões do estudo"/)
  assert.match(content, /aria-label="Editar estudo"/)
  assert.match(content, /aria-label="Mover para a lixeira"/)
})

test('StudyView.vue - Responsividade Mobile, Linha Única e Breadcrumb Inteligente', () => {
  const content = fs.readFileSync(studyViewPath, 'utf-8')
  // Breadcrumb com transição inteligente desktop x mobile
  assert.match(content, /breadcrumb-desktop/)
  assert.match(content, /breadcrumb-mobile/)
  assert.match(content, /back-chapter-btn/)
  assert.match(content, /Voltar a \{\{\s*state\.context\.chapter\.name\s*\}\}/)

  // Header actions com flex-wrap: nowrap para impedir quebras de linha
  assert.match(content, /\.header-actions\s*\{[^}]*flex-wrap:\s*nowrap/s)

  // Alvos táteis mínimos de 44x44px garantidos no CSS
  assert.match(content, /min-width:\s*44px/)
  assert.match(content, /min-height:\s*44px/)
})

test('StudyView.vue - Blindagem no Modo Somente Leitura', () => {
  const content = fs.readFileSync(studyViewPath, 'utf-8')
  // Ações mutáveis condicionadas estritamente a canEdit
  assert.match(content, /v-if="canEdit"[^>]*class="secondary share-action header-icon-btn"/)
  assert.match(content, /v-if="canEdit"[^>]*class="button primary edit-action header-icon-btn"/)
  assert.match(content, /v-if="canEdit"[^>]*class="secondary danger-action header-icon-btn"/)

  // Ações de exportar e histórico permanecem livres para consulta de visitantes
  assert.match(content, /class="secondary export-action header-icon-btn"[^>]*@click="exportModalOpen = true"/)
  assert.match(content, /class="secondary history-action header-icon-btn"[^>]*@click="historyModalOpen = true"/)
})

test('DropdownMenu.vue - Acessibilidade WAI-ARIA e Isolamento de Teclas', () => {
  const content = fs.readFileSync(dropdownComponentPath, 'utf-8')
  // WAI-ARIA Menu semantics
  assert.match(content, /aria-haspopup="menu"/)
  assert.match(content, /:aria-expanded="isOpen"/)
  assert.match(content, /role="menu"/)
  assert.match(content, /aria-orientation="vertical"/)

  // Teclas tratadas e contenção de propagação (Active Recall protection)
  assert.match(content, /shouldStopPropagation|\['Escape',\s*'ArrowDown',\s*'ArrowUp',\s*'Home',\s*'End'\]\.includes/)
  assert.match(content, /event\.stopPropagation\(\)/)
})
