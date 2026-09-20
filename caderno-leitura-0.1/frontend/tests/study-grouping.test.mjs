import test from 'node:test'
import assert from 'node:assert/strict'
import { ref } from 'vue'

import {
  useStudyGrouping,
  getDateBucket,
  READING_STATUS_LABELS,
} from '../src/composables/useStudyGrouping.ts'

test('getDateBucket particiona datas cronológicas relativas corretamente', () => {
  const now = new Date()
  const todayIso = now.toISOString()

  const threeDaysAgo = new Date(now.getTime() - 3 * 24 * 60 * 60 * 1000).toISOString()
  const twentyDaysAgo = new Date(now.getTime() - 20 * 24 * 60 * 60 * 1000).toISOString()
  const ninetyDaysAgo = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000).toISOString()

  assert.equal(getDateBucket(todayIso).id, 'hoje')
  assert.equal(getDateBucket(todayIso).title, 'Hoje')

  assert.equal(getDateBucket(threeDaysAgo).id, 'esta_semana')
  assert.equal(getDateBucket(threeDaysAgo).title, 'Esta Semana')

  assert.equal(getDateBucket(twentyDaysAgo).id, 'este_mes')
  assert.equal(getDateBucket(twentyDaysAgo).title, 'Este Mês')

  assert.equal(getDateBucket(ninetyDaysAgo).id, 'antigos')
  assert.equal(getDateBucket(ninetyDaysAgo).title, 'Mais Antigos')

  // Data inválida ou vazia vai para 'antigos'
  assert.equal(getDateBucket(null).id, 'antigos')
  assert.equal(getDateBucket('data_invalida').id, 'antigos')
})

test('READING_STATUS_LABELS cobre os 4 estados canônicos com metadados corretos', () => {
  const statuses = ['rascunho', 'em_estudo', 'revisado', 'concluido']
  for (const st of statuses) {
    assert.ok(READING_STATUS_LABELS[st], `Status ${st} deve estar definido`)
    assert.ok(READING_STATUS_LABELS[st].label, `Status ${st} deve ter label`)
    assert.ok(READING_STATUS_LABELS[st].badgeClass, `Status ${st} deve ter classe CSS`)
  }
  assert.equal(READING_STATUS_LABELS.rascunho.label, 'Rascunho')
  assert.equal(READING_STATUS_LABELS.em_estudo.label, 'Em Estudo')
  assert.equal(READING_STATUS_LABELS.revisado.label, 'Revisado')
  assert.equal(READING_STATUS_LABELS.concluido.label, 'Concluído')
})

test('useStudyGrouping agrupa por capítulo usando nomes canônicos e preserva integridade', () => {
  const studies = [
    { id: 1, title: 'Estudo 1', chapter_id: 10 },
    { id: 2, title: 'Estudo 2', chapter_id: 10 },
    { id: 3, title: 'Estudo 3', chapter_id: 20 },
  ]
  const chapters = [
    { id: 10, name: 'Capítulo 1: Fundamentos' },
    { id: 20, name: 'Capítulo 2: Aplicações' },
  ]

  const { groups, totalStudies } = useStudyGrouping({
    studies,
    chapters,
    initialCriteria: 'chapter',
  })

  assert.equal(totalStudies.value, 3)
  assert.equal(groups.value.length, 2)

  const g1 = groups.value.find(g => g.id === 'chapter-10')
  assert.ok(g1)
  assert.equal(g1.title, 'Capítulo 1: Fundamentos')
  assert.equal(g1.count, 2)
  assert.equal(g1.studies.length, 2)

  const g2 = groups.value.find(g => g.id === 'chapter-20')
  assert.ok(g2)
  assert.equal(g2.title, 'Capítulo 2: Aplicações')
  assert.equal(g2.count, 1)

  // Preservação de todos os estudos (SC-002)
  const totalInGroups = groups.value.reduce((acc, g) => acc + g.count, 0)
  assert.equal(totalInGroups, 3)
})

test('useStudyGrouping agrupa por categoria em ordem alfabética e trata sem categoria', () => {
  const studies = [
    { id: 1, title: 'Estudo Metafísica', category: 'Filosofia' },
    { id: 2, title: 'Estudo Mecânica', category: 'Física' },
    { id: 3, title: 'Estudo Ética', category: 'Filosofia' },
    { id: 4, title: 'Estudo Avulso' }, // sem categoria
  ]

  const { groups, totalStudies } = useStudyGrouping({
    studies,
    initialCriteria: 'category',
  })

  assert.equal(totalStudies.value, 4)
  assert.equal(groups.value.length, 3)

  // Ordem alfabética: Filosofia, Física, Sem Categoria
  assert.equal(groups.value[0].title, 'Filosofia')
  assert.equal(groups.value[0].count, 2)

  assert.equal(groups.value[1].title, 'Física')
  assert.equal(groups.value[1].count, 1)

  assert.equal(groups.value[2].title, 'Sem Categoria')
  assert.equal(groups.value[2].count, 1)
  assert.equal(groups.value[2].id, 'cat-sem-categoria')

  // Total preservado
  const totalInGroups = groups.value.reduce((acc, g) => acc + g.count, 0)
  assert.equal(totalInGroups, 4)
})

test('useStudyGrouping agrupa por data cronológica relativa', () => {
  const now = new Date()
  const today = now.toISOString()
  const threeDaysAgo = new Date(now.getTime() - 3 * 24 * 60 * 60 * 1000).toISOString()
  const pastYear = new Date(now.getTime() - 120 * 24 * 60 * 60 * 1000).toISOString()

  const studies = [
    { id: 1, title: 'Nota Recente', created_at: today },
    { id: 2, title: 'Nota da Semana', created_at: threeDaysAgo },
    { id: 3, title: 'Nota Histórica', created_at: pastYear },
  ]

  const { groups } = useStudyGrouping({
    studies,
    initialCriteria: 'date',
  })

  assert.equal(groups.value.length, 3)
  assert.equal(groups.value[0].title, 'Hoje')
  assert.equal(groups.value[0].count, 1)
  assert.equal(groups.value[1].title, 'Esta Semana')
  assert.equal(groups.value[1].count, 1)
  assert.equal(groups.value[2].title, 'Mais Antigos')
  assert.equal(groups.value[2].count, 1)
})

test('useStudyGrouping agrupa por status de leitura com as 4 raias canônicas', () => {
  const studies = [
    { id: 1, title: 'Rascunho A', reading_status: 'rascunho' },
    { id: 2, title: 'Em Estudo B', reading_status: 'em_estudo' },
    { id: 3, title: 'Revisado C', reading_status: 'revisado' },
    { id: 4, title: 'Concluído D', reading_status: 'concluido' },
    { id: 5, title: 'Padrão E' }, // sem status -> cai em rascunho
  ]

  const { groups } = useStudyGrouping({
    studies,
    initialCriteria: 'status',
  })

  assert.equal(groups.value.length, 4)

  const rascunhoGroup = groups.value.find(g => g.id === 'status-rascunho')
  assert.ok(rascunhoGroup)
  assert.equal(rascunhoGroup.count, 2)
  assert.equal(rascunhoGroup.badgeLabel, 'Rascunho')

  const emEstudoGroup = groups.value.find(g => g.id === 'status-em_estudo')
  assert.ok(emEstudoGroup)
  assert.equal(emEstudoGroup.count, 1)

  const revisadoGroup = groups.value.find(g => g.id === 'status-revisado')
  assert.ok(revisadoGroup)
  assert.equal(revisadoGroup.count, 1)

  const concluidoGroup = groups.value.find(g => g.id === 'status-concluido')
  assert.ok(concluidoGroup)
  assert.equal(concluidoGroup.count, 1)
})

test('useStudyGrouping gerencia colapso individual e alternância de critério', () => {
  const studies = ref([
    { id: 1, title: 'E1', chapter_id: 10 },
    { id: 2, title: 'E2', chapter_id: 10 },
  ])

  const { groups, currentCriteria, setCriteria, toggleGroup } = useStudyGrouping({
    studies,
    initialCriteria: 'chapter',
  })

  assert.equal(currentCriteria.value, 'chapter')
  assert.equal(groups.value[0].isCollapsed, false)

  // Colapsar grupo
  toggleGroup(groups.value[0].id)
  assert.equal(groups.value[0].isCollapsed, true)

  // Alternar critério
  setCriteria('status')
  assert.equal(currentCriteria.value, 'status')
  assert.equal(groups.value[0].id, 'status-rascunho')
  assert.equal(groups.value[0].isCollapsed, false) // novo grupo não colapsado
})
