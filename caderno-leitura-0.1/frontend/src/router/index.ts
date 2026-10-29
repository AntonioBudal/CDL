import { createRouter, createWebHistory } from 'vue-router'
import LandingView from '../views/LandingView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import SetupOwnerView from '../views/SetupOwnerView.vue'
import AboutView from '../views/AboutView.vue'
import SupportView from '../views/SupportView.vue'
import NotFoundView from '../views/NotFoundView.vue'
import DigitizeNotebookView from '../views/DigitizeNotebookView.vue'
import { updateSeoMeta } from '../composables/useSeoMeta'
import { useAuthStore } from '../stores/auth.ts'
import { resolveNavigation } from './guard.ts'
import { api } from '../services/api'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'login', component: LoginView, meta: { title: 'Identificação', public: true } },
    { path: '/registro', name: 'register', component: RegisterView, meta: { title: 'Criar Conta', public: true } },
    { path: '/primeiro-acesso', name: 'setup-owner', component: SetupOwnerView, meta: { title: 'Primeiro Acesso', public: true } },
    {
      path: '/',
      name: 'landing',
      component: LandingView,
      meta: {
        title: 'Início',
        public: true,
        description: 'Caderno pessoal de leitura e estudos em camadas. Metodologia em 4 partes, privacidade total e zero anúncios.',
      },
    },
    {
      path: '/sobre',
      name: 'about',
      component: AboutView,
      meta: {
        title: 'Sobre o Leitorum',
        public: true,
        description: 'Conheça o Leitorum, sua metodologia de leitura em 4 partes, princípios de privacidade e arquitetura local-first.',
      },
    },
    { path: '/dashboard', name: 'dashboard', component: () => import('../views/DashboardView.vue'), meta: { title: 'Dashboard' } },
    { path: '/inbox', alias: ['/caixa-de-entrada'], name: 'inbox', component: () => import('../views/InboxView.vue'), meta: { title: 'Caixa de Entrada' } },
    { path: '/books', alias: ['/livros'], name: 'books', component: () => import('../views/BooksView.vue'), meta: { title: 'Livros' } },
    { path: '/highlights', alias: ['/destaques', '/anotacoes'], name: 'highlights', component: () => import('../views/HighlightsLibraryView.vue'), meta: { title: 'Destaques e Anotações' } },
    { path: '/review', alias: ['/revisao'], name: 'review', component: () => import('../views/ReviewHubView.vue'), meta: { title: 'Central de Revisão' } },
    {
      path: '/estudo/sessao/:sessionId',
      alias: ['/study/session/:sessionId'],
      name: 'study-session',
      component: () => import('../views/StudySessionView.vue'),
      meta: { title: 'Sessão de Estudo', cleanScreen: true },
    },
    { path: '/livros/:bookId', alias: ['/books/:bookId'], name: 'book', component: () => import('../views/BookView.vue'), meta: { title: 'Livro' } },
    { path: '/livros/:bookId/estudos/:studyId', alias: ['/books/:bookId/estudos/:studyId'], name: 'study', component: () => import('../views/StudyView.vue'), meta: { title: 'Ler estudo' } },
    {
      path: '/estudos/:studyId',
      name: 'study-direct',
      beforeEnter: async (to, _from, next) => {
        try {
          const studyId = Number(to.params.studyId)
          if (!studyId) return next('/livros')
          const study = await api.getStudy(studyId)
          const bookId = study.book_id || (study as any).chapter?.book_id
          if (bookId) {
            return next(`/livros/${bookId}/estudos/${studyId}`)
          }
        } catch {
          // ignore
        }
        next('/livros')
      },
      component: () => import('../views/StudyView.vue'),
    },
    { path: '/livros/:bookId/estudos/:studyId/editar', alias: ['/books/:bookId/estudos/:studyId/editar'], name: 'study-edit', component: () => import('../views/StudyEditView.vue'), meta: { title: 'Editar estudo' } },
    { path: '/importar', name: 'import', component: () => import('../views/ImportView.vue'), meta: { title: 'Importar estudo' } },
    {
      path: '/digitalizar',
      alias: ['/scan'],
      name: 'digitize-notebook',
      component: DigitizeNotebookView,
      meta: { title: 'Digitalizar Caderno' },
    },
    { path: '/amigos', alias: ['/friends'], name: 'friends', component: () => import('../views/FriendsView.vue'), meta: { title: 'Amigos e Leitores' } },
    { path: '/conexao', name: 'connection', component: () => import('../views/ConnectionView.vue'), meta: { title: 'Conexão' } },
    { path: '/ajustes', name: 'settings', component: () => import('../views/SettingsView.vue'), meta: { title: 'Ajustes' } },
    { path: '/minhas-imagens', name: 'media-space', component: () => import('../views/MediaSpaceView.vue'), meta: { title: 'Minhas Imagens e Espaço' } },
    { path: '/lixeira', name: 'trash', component: () => import('../views/TrashView.vue'), meta: { title: 'Lixeira' } },
    { path: '/@:username', alias: ['/u/:username'], name: 'user-profile', component: () => import('../views/UserProfileView.vue'), meta: { title: 'Perfil do Leitor' } },
    { path: '/admin', name: 'admin', component: () => import('../views/AdminView.vue'), meta: { title: 'Administração', requiresAdmin: true } },
    {
      path: '/apoie',
      alias: ['/apoiar'],
      name: 'support',
      component: SupportView,
      meta: {
        title: 'Apoie o Leitorum',
        public: true,
        description: 'Apoie o desenvolvimento contínuo e independente do Leitorum.',
      },
    },
    { path: '/:pathMatch(.*)*', component: NotFoundView, meta: { title: 'Página não encontrada' } },
  ],
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    if (to.hash) {
      return { el: to.hash, behavior: 'smooth' }
    }
    if (to.path === from.path) return false
    return { top: 0 }
  },
})

router.beforeEach(async (to, _from, next) => {
  const auth = useAuthStore()
  await auth.checkAuth()

  let homePreference: string | null = null
  try {
    homePreference = typeof window !== 'undefined' && window.localStorage
      ? window.localStorage.getItem('caderno_home_view')
      : null
  } catch {
    // ignore
  }

  const redirect = resolveNavigation({
    path: to.path,
    fullPath: to.fullPath,
    isPublicMeta: to.meta.public === true,
    requiresAdmin: to.meta.requiresAdmin === true,
    isAuthenticated: auth.isAuthenticated.value,
    isAdmin: auth.isAdmin.value,
    ownerSetupRequired: auth.ownerSetupRequired.value,
    homePreference,
  })
  return redirect === null ? next() : next(redirect)
})

router.afterEach((to) => {
  const isPublic = to.meta.public === true
  const title = String(to.meta.title || 'Caderno de Leitura')
  const description = typeof to.meta.description === 'string' ? to.meta.description : ''
  const origin = typeof window !== 'undefined' ? window.location.origin : 'https://leitorum.com'
  const canonicalUrl = `${origin}${to.path}`

  updateSeoMeta({
    title,
    description,
    canonicalUrl,
    robots: isPublic ? 'index, follow' : 'noindex, nofollow',
    ogType: 'website',
  })
})
