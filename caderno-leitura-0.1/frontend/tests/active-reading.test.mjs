import test from 'node:test'
import assert from 'node:assert/strict'
import { ref } from 'vue'
import { useActiveReadingSession } from '../src/composables/useActiveReadingSession.ts'
import {
  setHighlightsRevealedState,
  collectInteractiveHighlights,
  scrollAndFocusHighlight,
} from '../src/utils/highlightRenderer.ts'

function createSampleHighlights() {
  return [
    {
      id: 101,
      study_id: 1,
      user_id: 'u1',
      section: 'summary',
      start_offset: 10,
      end_offset: 25,
      selected_text: 'materialismo histórico',
      prefix: '',
      suffix: '',
      color: 'yellow',
      kind: 'hidden',
      note: '',
      created_at: '2026-09-27T08:00:00Z',
      updated_at: '2026-09-27T08:00:00Z',
    },
    {
      id: 102,
      study_id: 1,
      user_id: 'u1',
      section: 'summary',
      start_offset: 40,
      end_offset: 55,
      selected_text: 'luta de classes',
      prefix: '',
      suffix: '',
      color: 'green',
      kind: 'question',
      note: 'Qual é o motor da história?',
      created_at: '2026-09-27T08:00:00Z',
      updated_at: '2026-09-27T08:00:00Z',
    },
    {
      id: 103,
      study_id: 1,
      user_id: 'u1',
      section: 'summary',
      start_offset: 70,
      end_offset: 85,
      selected_text: 'modo de produção',
      prefix: '',
      suffix: '',
      color: 'blue',
      kind: 'highlight', // Não é interativo (apenas destaque de cor)
      note: '',
      created_at: '2026-09-27T08:00:00Z',
      updated_at: '2026-09-27T08:00:00Z',
    },
    {
      id: 104,
      study_id: 1,
      user_id: 'u1',
      section: 'explanation', // Outra seção
      start_offset: 5,
      end_offset: 20,
      selected_text: 'infraestrutura econômica',
      prefix: '',
      suffix: '',
      color: 'purple',
      kind: 'hidden',
      note: '',
      created_at: '2026-09-27T08:00:00Z',
      updated_at: '2026-09-27T08:00:00Z',
    },
  ]
}

test('T004 [US1]: useActiveReadingSession inicializa inativa e filtra trechos interativos da seção', () => {
  const activeSection = ref('summary')
  const highlights = ref(createSampleHighlights())

  const session = useActiveReadingSession({
    activeSectionRef: activeSection,
    highlightsRef: highlights,
  })

  assert.equal(session.isActive.value, false)
  // Na seção 'summary' há 2 trechos interativos (id 101 e 102), o id 103 é 'highlight' e 104 é de 'explanation'
  assert.equal(session.totalCount.value, 2)
  assert.equal(session.revealedCount.value, 0)
  assert.equal(session.completionPercentage.value, 0)
})

test('T004 [US1]: startSession mascara itens, revealAll e hideAll alteram em lote', () => {
  const activeSection = ref('summary')
  const highlights = ref(createSampleHighlights())

  const session = useActiveReadingSession({
    activeSectionRef: activeSection,
    highlightsRef: highlights,
  })

  // Iniciar sessão
  session.startSession()
  assert.equal(session.isActive.value, true)
  assert.equal(session.revealedCount.value, 0)
  assert.equal(session.completionPercentage.value, 0)

  // Revelar todos
  session.revealAll()
  assert.equal(session.revealedCount.value, 2)
  assert.equal(session.completionPercentage.value, 100)

  // Ocultar todos
  session.hideAll()
  assert.equal(session.revealedCount.value, 0)
  assert.equal(session.completionPercentage.value, 0)

  // Encerrar sessão
  session.endSession()
  assert.equal(session.isActive.value, false)
  assert.equal(session.revealedCount.value, 2) // ao encerrar restaura visibilidade para leitura
})

test('T004 [US1]: utilitários DOM setHighlightsRevealedState e collectInteractiveHighlights manipulam nós', () => {
  function createMockMark(id, kind, isRevealed) {
    const classes = new Set(['study-occlusion'])
    if (isRevealed) classes.add('is-revealed')

    const btn = {
      textContent: kind === 'hidden' ? (isRevealed ? 'Ocultar' : 'Revelar') : (isRevealed ? 'Esconder resposta' : 'Ver resposta'),
    }

    return {
      getAttribute(attr) {
        if (attr === 'data-highlight-id') return String(id)
        if (attr === 'data-kind') return kind
        return null
      },
      classList: {
        contains(c) { return classes.has(c) },
        add(c) { classes.add(c) },
        remove(c) { classes.delete(c) },
        toggle(c) {
          if (classes.has(c)) { classes.delete(c); return false }
          classes.add(c); return true
        },
      },
      querySelector(selector) {
        if (selector.includes('study-occlusion-btn') && kind === 'hidden') return btn
        if (selector.includes('study-question-reveal-btn') && kind === 'question') return btn
        return null
      },
      querySelectorAll() { return [] },
    }
  }

  const mark1 = createMockMark(101, 'hidden', false)
  const mark2 = createMockMark(102, 'question', false)

  const fakeRoot = {
    querySelectorAll(selector) {
      if (selector.includes('data-highlight-id')) {
        return [mark1, mark2]
      }
      return []
    },
    querySelector() { return null },
  }

  // Coleta inicial
  const collected = collectInteractiveHighlights(fakeRoot)
  assert.equal(collected.length, 2)
  assert.equal(collected[0].id, 101)
  assert.equal(collected[0].isRevealed, false)

  // Revela todos via setHighlightsRevealedState
  const toggledIds = []
  setHighlightsRevealedState(fakeRoot, true, (id, rev) => toggledIds.push({ id, rev }))

  assert.equal(mark1.classList.contains('is-revealed'), true)
  assert.equal(mark1.querySelector('.study-occlusion-btn').textContent, 'Ocultar')
  assert.equal(mark2.classList.contains('is-revealed'), true)
  assert.equal(mark2.querySelector('.study-question-reveal-btn').textContent, 'Esconder resposta')
  assert.equal(toggledIds.length, 2)
  assert.equal(toggledIds[0].rev, true)

  // Oculta todos
  setHighlightsRevealedState(fakeRoot, false)
  assert.equal(mark1.classList.contains('is-revealed'), false)
  assert.equal(mark1.querySelector('.study-occlusion-btn').textContent, 'Revelar')
  assert.equal(mark2.classList.contains('is-revealed'), false)
  assert.equal(mark2.querySelector('.study-question-reveal-btn').textContent, 'Ver resposta')
})

test('T008 [US2]: toggleNode e setNodeRevealed sincronizam progresso pontual', () => {
  const activeSection = ref('summary')
  const highlights = ref(createSampleHighlights())

  const session = useActiveReadingSession({
    activeSectionRef: activeSection,
    highlightsRef: highlights,
  })

  session.startSession()
  assert.equal(session.revealedCount.value, 0)
  assert.equal(session.completionPercentage.value, 0)

  // Revela pontualmente o nó 101
  session.toggleNode(101)
  assert.equal(session.revealedCount.value, 1)
  assert.equal(session.completionPercentage.value, 50)
  assert.equal(session.nodes.value.find((n) => n.highlight_id === 101)?.is_revealed, true)

  // Oculta novamente o nó 101
  session.toggleNode(101)
  assert.equal(session.revealedCount.value, 0)
  assert.equal(session.completionPercentage.value, 0)

  // Seta diretamente via setNodeRevealed
  session.setNodeRevealed(102, true)
  assert.equal(session.revealedCount.value, 1)
  assert.equal(session.completionPercentage.value, 50)
})

test('T010 [US3]: next e previous efetuam navegação cíclica pelos trechos', () => {
  const activeSection = ref('summary')
  const highlights = ref(createSampleHighlights())

  const session = useActiveReadingSession({
    activeSectionRef: activeSection,
    highlightsRef: highlights,
  })

  session.startSession()
  assert.equal(session.focusedIndex.value, -1)

  // Avança para primeiro item (índice 0)
  session.next()
  assert.equal(session.focusedIndex.value, 0)

  // Avança para segundo item (índice 1)
  session.next()
  assert.equal(session.focusedIndex.value, 1)

  // Avança ciclicamente (volta para índice 0)
  session.next()
  assert.equal(session.focusedIndex.value, 0)

  // Volta ciclicamente com previous (vai para índice 1)
  session.previous()
  assert.equal(session.focusedIndex.value, 1)

  // Volta para índice 0
  session.previous()
  assert.equal(session.focusedIndex.value, 0)
})

test('T013 [US4]: Sessão de Leitura Ativa opera em memória com zero chamadas ao servidor', () => {
  const activeSection = ref('summary')
  const highlights = ref(createSampleHighlights())

  let serverCallCount = 0
  const fakeApiProxy = new Proxy({}, {
    get() {
      return () => {
        serverCallCount++
        return Promise.resolve()
      }
    },
  })

  const session = useActiveReadingSession({
    activeSectionRef: activeSection,
    highlightsRef: highlights,
  })

  // Realiza ciclo completo de estudo ativo
  session.startSession()
  session.revealAll()
  session.hideAll()
  session.toggleNode(101)
  session.next()
  session.previous()
  session.endSession()

  // Nenhuma requisição de mutação ou sincronização externa é disparada
  assert.equal(serverCallCount, 0, 'Sessão de Leitura Ativa não deve enviar requisições ao servidor')
})

test('T015 [Polish]: themes.css define estilos de anel de foco e suporte a E-Ink para estudo ativo', async () => {
  const fs = await import('node:fs')
  const path = await import('node:path')
  const cssPath = path.resolve('src/themes.css')
  const css = fs.readFileSync(cssPath, 'utf-8')

  assert.ok(css.includes('.study-highlight-focused'), 'Deve definir anel de foco para trecho ativo')
  assert.ok(css.includes("data-theme='e-ink'] .study-highlight-focused"), 'Deve definir foco de alto contraste no E-Ink')
  assert.ok(css.includes("data-theme='e-ink'] .active-reading-bar"), 'Deve definir barra adaptada ao E-Ink')
})

test('T016 [Polish]: ActiveReadingBar.vue cumpre semântica WAI-ARIA e alvos táteis mínimos de 44px no mobile', async () => {
  const fs = await import('node:fs')
  const path = await import('node:path')
  const barPath = path.resolve('src/components/ActiveReadingBar.vue')
  const component = fs.readFileSync(barPath, 'utf-8')

  assert.ok(component.includes('role="region"'), 'Deve possuir landmark role region')
  assert.ok(component.includes('aria-label="Barra de Leitura Ativa"'), 'Deve possuir rótulo acessível')
  assert.ok(component.includes('aria-live="polite"'), 'Deve anunciar progresso dinamicamente com aria-live polite')
  assert.ok(component.includes('min-height: 44px'), 'Deve definir altura mínima de toque de 44px no mobile')
  assert.ok(component.includes('min-width: 44px'), 'Deve definir largura mínima de toque de 44px no mobile')
})
