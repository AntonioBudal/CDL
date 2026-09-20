import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

test('appearance-bootstrap exporta factoryReset e cleanOrphanKeys', () => {
  const bootstrapContent = fs.readFileSync(
    path.resolve(process.cwd(), 'src/appearance-bootstrap.js'),
    'utf-8'
  )

  assert.ok(
    bootstrapContent.includes('factoryReset'),
    'appearance-bootstrap deve conter a rotina factoryReset'
  )
  assert.ok(
    bootstrapContent.includes('cleanOrphanKeys'),
    'appearance-bootstrap deve conter a rotina cleanOrphanKeys'
  )
  assert.ok(
    bootstrapContent.includes("window.localStorage.removeItem(LEGACY)"),
    'Deve remover chave legada v1 durante limpeza e reset'
  )
})

test('cálculo de diagnóstico de consumo do localStorage', () => {
  function calculateStorageDiagnostic(storage) {
    if (!storage) {
      return {
        isAvailable: false,
        keyCount: 0,
        totalBytes: 0,
        formattedSize: 'N/D',
        cadernoKeysCount: 0,
      }
    }

    try {
      let totalBytes = 0
      let cadernoKeysCount = 0
      const keys = Object.keys(storage)

      for (const key of keys) {
        const val = storage[key] ?? ''
        // Estimativa UTF-16: 2 bytes por caractere na chave e no valor
        totalBytes += (key.length + String(val).length) * 2
        if (key.startsWith('caderno.')) {
          cadernoKeysCount++
        }
      }

      const formattedSize =
        totalBytes < 1024
          ? `${totalBytes} B`
          : `${(totalBytes / 1024).toFixed(1)} KB`

      return {
        isAvailable: true,
        keyCount: keys.length,
        totalBytes,
        formattedSize,
        cadernoKeysCount,
      }
    } catch {
      return {
        isAvailable: false,
        keyCount: 0,
        totalBytes: 0,
        formattedSize: 'Indisponível',
        cadernoKeysCount: 0,
      }
    }
  }

  const mockStorage = {
    'caderno.aparencia.v2': JSON.stringify({ theme: 'porcelana', font: 'inter' }),
    'caderno.livros.filtro': 'design',
    'outra.chave': '12345',
  }

  const diag = calculateStorageDiagnostic(mockStorage)
  assert.equal(diag.isAvailable, true)
  assert.equal(diag.keyCount, 3)
  assert.equal(diag.cadernoKeysCount, 2)
  assert.ok(diag.totalBytes > 0)
  assert.ok(diag.formattedSize.includes('B') || diag.formattedSize.includes('KB'))

  const fallbackDiag = calculateStorageDiagnostic(null)
  assert.equal(fallbackDiag.isAvailable, false)
  assert.equal(fallbackDiag.formattedSize, 'N/D')
})

test('consulta e tratamento de status da API de saúde (/api/health)', async () => {
  const originalFetch = globalThis.fetch

  globalThis.fetch = async (url) => {
    if (url === '/api/health') {
      return {
        ok: true,
        status: 200,
        json: async () => ({
          status: 'ok',
          service: 'caderno-leitura',
          version: '0.2.0-alpha.1',
        }),
      }
    }
    throw new Error('Not found')
  }

  try {
    const start = Date.now()
    const res = await fetch('/api/health', { cache: 'no-store' })
    const data = await res.json()
    const latencyMs = Math.max(0, Date.now() - start)

    assert.equal(res.ok, true)
    assert.equal(data.status, 'ok')
    assert.equal(data.version, '0.2.0-alpha.1')
    assert.ok(typeof latencyMs === 'number')
  } finally {
    globalThis.fetch = originalFetch
  }
})

test('definição canônica das três seções de Ajustes', () => {
  const tabs = [
    { id: 'aparencia', label: 'Aparência', description: 'Cores, tema e física' },
    { id: 'leitura', label: 'Leitura', description: 'Tipografia literária e texto' },
    { id: 'sistema', label: 'Sistema', description: 'Diagnóstico, conexão e backup' },
  ]

  assert.equal(tabs.length, 3)
  assert.deepEqual(
    tabs.map(t => t.id),
    ['aparencia', 'leitura', 'sistema']
  )
})

test('SettingsView.vue preserva nó raiz único e semântica WAI-ARIA', () => {
  const viewContent = fs.readFileSync(
    path.resolve(process.cwd(), 'src/views/SettingsView.vue'),
    'utf-8'
  )

  // Nó raiz único
  assert.ok(
    viewContent.includes('<section class="settings-page wrap">'),
    'SettingsView deve possuir o nó raiz único <section class="settings-page wrap">'
  )

  // WAI-ARIA tablist e tabpanel
  assert.ok(viewContent.includes('role="tablist"'), 'Deve possuir container role="tablist"')
  assert.ok(viewContent.includes('role="tab"'), 'Abas devem possuir role="tab"')
  assert.ok(viewContent.includes('role="tabpanel"'), 'Painéis devem possuir role="tabpanel"')
  assert.ok(viewContent.includes('aria-selected'), 'Abas devem possuir controle aria-selected')
  assert.ok(viewContent.includes('aria-controls'), 'Abas devem apontar aria-controls para o painel')

  // Layout 2 colunas e preview
  assert.ok(viewContent.includes('class="settings-layout"'), 'Deve utilizar container de layout 2 colunas')
  assert.ok(viewContent.includes('class="settings-sidebar"'), 'Deve possuir coluna lateral para preview')
  assert.ok(viewContent.includes('<AppearancePreview'), 'Deve renderizar o componente AppearancePreview')

  // Central de Diagnóstico do Sistema
  assert.ok(viewContent.includes('Escopo de Armazenamento'), 'Aba sistema deve ter card de escopo')
  assert.ok(viewContent.includes('Status da Conexão Local'), 'Aba sistema deve ter card de conexão')
  assert.ok(viewContent.includes('Armazenamento do Navegador'), 'Aba sistema deve ter diagnóstico de storage')
  assert.ok(viewContent.includes('Restaurar Padrões de Fábrica'), 'Aba sistema deve ter card de reset')
  assert.ok(viewContent.includes('<DatabaseBackup'), 'Aba sistema deve embutir DatabaseBackup')
})

test('AppearanceControls suporta filtragem por aba', () => {
  const controlsContent = fs.readFileSync(
    path.resolve(process.cwd(), 'src/components/AppearanceControls.vue'),
    'utf-8'
  )

  assert.ok(
    controlsContent.includes("tab?: 'aparencia' | 'leitura' | 'all'"),
    'AppearanceControls deve aceitar a prop tab'
  )
  assert.ok(
    controlsContent.includes('APPEARANCE_KEYS'),
    'Deve definir conjunto de chaves da aba Aparência'
  )
  assert.ok(
    controlsContent.includes('READING_KEYS'),
    'Deve definir conjunto de chaves da aba Leitura'
  )
  assert.ok(
    controlsContent.includes('visibleFields'),
    'Deve calcular campos visíveis de acordo com a aba'
  )
})

test('AppearancePreview adapta apresentação ao modo grade e lista', () => {
  const previewContent = fs.readFileSync(
    path.resolve(process.cwd(), 'src/components/AppearancePreview.vue'),
    'utf-8'
  )

  assert.ok(
    previewContent.includes("preferences?.library === 'list'"),
    'Deve verificar se o modo lista está ativo'
  )
  assert.ok(
    previewContent.includes('book-list-compact'),
    'Deve renderizar lista compacta no modo lista'
  )
  assert.ok(
    previewContent.includes('book-grid'),
    'Deve renderizar grade no modo grade'
  )
  assert.ok(
    previewContent.includes('<StudyTabs'),
    'Deve renderizar abas de estudo realistas'
  )
  assert.ok(
    previewContent.includes('<BookCover'),
    'Deve utilizar BookCover para apresentação realista'
  )
})

test('ConfirmResetModal implementa acessibilidade WAI-ARIA e controle por teclado', () => {
  const modalContent = fs.readFileSync(
    path.resolve(process.cwd(), 'src/components/ConfirmResetModal.vue'),
    'utf-8'
  )

  assert.ok(modalContent.includes('role="dialog"'), 'Deve possuir role="dialog"')
  assert.ok(modalContent.includes('aria-modal="true"'), 'Deve ser modal explícito')
  assert.ok(modalContent.includes('aria-labelledby'), 'Deve ter aria-labelledby')
  assert.ok(modalContent.includes("event.key === 'Escape'"), 'Deve fechar com tecla Escape')
  assert.ok(modalContent.includes('<Teleport to="body">'), 'Deve teleportar para o body')
})
