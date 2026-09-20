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

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'dashboard', component: DashboardView, meta: { title: 'Dashboard' } },
    { path: '/dashboard', redirect: '/' },
    { path: '/books', alias: ['/livros'], name: 'books', component: BooksView, meta: { title: 'Livros' } },
    { path: '/livros/:bookId', alias: ['/books/:bookId'], name: 'book', component: BookView, meta: { title: 'Livro' } },
    { path: '/livros/:bookId/estudos/:studyId', alias: ['/books/:bookId/estudos/:studyId'], name: 'study', component: StudyView, meta: { title: 'Ler estudo' } },
    { path: '/livros/:bookId/estudos/:studyId/editar', alias: ['/books/:bookId/estudos/:studyId/editar'], name: 'study-edit', component: StudyEditView, meta: { title: 'Editar estudo' } },
    { path: '/importar', name: 'import', component: ImportView, meta: { title: 'Importar estudo' } },
    { path: '/conexao', name: 'connection', component: ConnectionView, meta: { title: 'Conexão' } },
    { path: '/ajustes', name: 'settings', component: SettingsView, meta: { title: 'Ajustes' } },
    { path: '/lixeira', name: 'trash', component: TrashView, meta: { title: 'Lixeira' } },
    { path: '/:pathMatch(.*)*', component: NotFoundView, meta: { title: 'Página não encontrada' } },
  ],
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    if (to.path === from.path) return false
    return { top: 0 }
  },
})

router.beforeEach((to, _from, next) => {
  if (to.path === '/') {
    try {
      const pref = typeof window !== 'undefined' && window.localStorage
        ? window.localStorage.getItem('caderno_home_view')
        : null
      if (pref === 'books') {
        return next('/books')
      }
    } catch {
      // ignore
    }
  }
  next()
})

router.afterEach((to) => { document.title = `${String(to.meta.title)} · Caderno de Leitura` })
