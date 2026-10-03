import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const studyViewPath = path.resolve('src/views/StudyView.vue')
const dropdownComponentPath = path.resolve('src/components/ui/DropdownMenu.vue')

test('StudyView.vue - Contrato de Importação do DropdownMenu', () => {
  const content = fs.readFileSync(studyViewPath, 'utf-8')
  assert.match(content, /import\s+DropdownMenu\s+from\s+['"]\.\.\/components\/ui\/DropdownMenu\.vue['"]/)
})

test('StudyView.vue - Hierarquia Desktop e Ação Primária de Edição (US1)', () => {
  const content = fs.readFileSync(studyViewPath, 'utf-8')
  // Botão primário de destaque para Editar Estudo
  assert.match(content, /class="button primary edit-action"/)
  assert.match(content, /Editar estudo/)

  // Botão secundário Compartilhar visível no Desktop
  assert.match(content, /class="secondary share-action desktop-only"/)

  // Menu suspenso agrupando utilitários secundários
  assert.match(content, /<DropdownMenu\s+aria-label="Mais opções do estudo">/)
  assert.match(content, /Histórico de versões/)
  assert.match(content, /Exportar estudo/)
  assert.match(content, /Mover para a lixeira/)
})

test('StudyView.vue - Responsividade Mobile, Linha Única e Breadcrumb Inteligente (US2)', () => {
  const content = fs.readFileSync(studyViewPath, 'utf-8')
  // Breadcrumb com transição inteligente desktop x mobile
  assert.match(content, /breadcrumb-desktop/)
  assert.match(content, /breadcrumb-mobile/)
  assert.match(content, /back-chapter-btn/)
  assert.match(content, /Voltar a \{\{\s*state\.context\.chapter\.name\s*\}\}/)

  // Header actions com flex-wrap: nowrap para impedir quebras de linha
  assert.match(content, /\.header-actions\s*\{[^}]*flex-wrap:\s*nowrap/s)

  // Compartilhar agrupado no menu para visualização mobile
  assert.match(content, /class="dropdown-action-btn mobile-only"/)

  // Alvos táteis mínimos de 44x44px garantidos no CSS
  assert.match(content, /min-width:\s*44px/)
  assert.match(content, /min-height:\s*44px/)
})

test('StudyView.vue - Blindagem no Modo Somente Leitura (US4)', () => {
  const content = fs.readFileSync(studyViewPath, 'utf-8')
  // Ações mutáveis condicionadas estritamente a canEdit
  assert.match(content, /v-if="canEdit"[^>]*class="button primary edit-action"/)
  assert.match(content, /v-if="canEdit"[^>]*class="secondary share-action desktop-only"/)
  assert.match(content, /v-if="canEdit"[^>]*class="dropdown-action-btn mobile-only"/)
  assert.match(content, /v-if="canEdit"[^>]*class="dropdown-action-btn danger-item"/)

  // Ação de exportar permanece livre para leitores convidados
  assert.match(content, /class="dropdown-action-btn"[^>]*role="menuitem"[^>]*@click="close\(\);\s*exportModalOpen = true"/)
})

test('DropdownMenu.vue - Acessibilidade WAI-ARIA e Isolamento de Teclas (US3)', () => {
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
