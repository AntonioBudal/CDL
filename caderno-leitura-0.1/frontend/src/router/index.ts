import { createRouter, createWebHistory } from 'vue-router'
import BooksView from '../views/BooksView.vue'
import BookView from '../views/BookView.vue'
import DashboardView from '../views/DashboardView.vue'
import ImportView from '../views/ImportView.vue'
import ConnectionView from '../views/ConnectionView.vue'
import NotFoundView from '../views/NotFoundView.vue'
import StudyView from '../views/StudyView.vue'
import StudyEditView from '../views/StudyEditView.vue'
import SettingsView from '../views/SettingsView.vue'
import TrashView from '../views/TrashView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import SetupOwnerView from '../views/SetupOwnerView.vue'
import UserProfileView from '../views/UserProfileView.vue'
import FriendsView from '../views/FriendsView.vue'
import AdminView from '../views/AdminView.vue'
import SupportView from '../views/SupportView.vue'
import LandingView from '../views/LandingView.vue'
import AboutView from '../views/AboutView.vue'
import ReviewHubView from '../views/ReviewHubView.vue'
import HighlightsLibraryView from '../views/HighlightsLibraryView.vue'
import { updateSeoMeta } from '../composables/useSeoMeta'
import { useAuthStore } from '../stores/auth.ts'
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
    { path: '/dashboard', name: 'dashboard', component: DashboardView, meta: { title: 'Dashboard' } },
    { path: '/books', alias: ['/livros'], name: 'books', component: BooksView, meta: { title: 'Livros' } },
    { path: '/highlights', alias: ['/destaques', '/anotacoes'], name: 'highlights', component: HighlightsLibraryView, meta: { title: 'Destaques e Anotações' } },
    { path: '/review', alias: ['/revisao'], name: 'review', component: ReviewHubView, meta: { title: 'Central de Revisão' } },
    { path: '/livros/:bookId', alias: ['/books/:bookId'], name: 'book', component: BookView, meta: { title: 'Livro' } },
    { path: '/livros/:bookId/estudos/:studyId', alias: ['/books/:bookId/estudos/:studyId'], name: 'study', component: StudyView, meta: { title: 'Ler estudo' } },
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
      component: StudyView,
    },
    { path: '/livros/:bookId/estudos/:studyId/editar', alias: ['/books/:bookId/estudos/:studyId/editar'], name: 'study-edit', component: StudyEditView, meta: { title: 'Editar estudo' } },
    { path: '/importar', name: 'import', component: ImportView, meta: { title: 'Importar estudo' } },
    { path: '/amigos', alias: ['/friends'], name: 'friends', component: FriendsView, meta: { title: 'Amigos e Leitores' } },
    { path: '/conexao', name: 'connection', component: ConnectionView, meta: { title: 'Conexão' } },
    { path: '/ajustes', name: 'settings', component: SettingsView, meta: { title: 'Ajustes' } },
    { path: '/lixeira', name: 'trash', component: TrashView, meta: { title: 'Lixeira' } },
    { path: '/@:username', alias: ['/u/:username'], name: 'user-profile', component: UserProfileView, meta: { title: 'Perfil do Leitor' } },
    { path: '/admin', name: 'admin', component: AdminView, meta: { title: 'Administração', requiresAdmin: true } },
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

  // Se o proprietário ainda não cadastrou a senha mestra inicial
  if (auth.ownerSetupRequired.value && to.path !== '/primeiro-acesso') {
    return next('/primeiro-acesso')
  }

  const isPublicRoute = to.meta.public === true || ['/login', '/registro', '/primeiro-acesso'].includes(to.path)

  // Se não estiver autenticado e tentar acessar rota protegida
  if (!auth.isAuthenticated.value && !isPublicRoute) {
    return next({ path: '/login', query: to.fullPath !== '/' ? { redirect: to.fullPath } : undefined })
  }

  // Se usuário autenticado tentar acessar raiz (Landing Page) ou telas de login/registro
  if (auth.isAuthenticated.value) {
    if (to.path === '/' || ['/login', '/registro', '/primeiro-acesso'].includes(to.path)) {
      let target = '/livros'
      try {
        const pref = typeof window !== 'undefined' && window.localStorage
          ? window.localStorage.getItem('caderno_home_view')
          : null
        if (pref === 'dashboard') {
          target = '/dashboard'
        }
      } catch {
        // ignore
      }
      return next(target)
    }
  }

  // Se rota requer privilégios de administrador (RBAC)
  if (to.meta.requiresAdmin === true || to.path === '/admin') {
    if (!auth.isAdmin.value) {
      return next({ path: '/livros', query: { aviso: 'acesso-restrito' } })
    }
  }

  next()
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
