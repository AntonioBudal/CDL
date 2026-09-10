import { createRouter, createWebHistory } from 'vue-router'
import BooksView from '../views/BooksView.vue'
import BookView from '../views/BookView.vue'
import ImportView from '../views/ImportView.vue'
import ConnectionView from '../views/ConnectionView.vue'
import NotFoundView from '../views/NotFoundView.vue'
import StudyView from '../views/StudyView.vue'
import StudyEditView from '../views/StudyEditView.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'books', component: BooksView, meta: { title: 'Livros' } },
    { path: '/livros/:bookId', name: 'book', component: BookView, meta: { title: 'Livro' } },
    { path: '/livros/:bookId/estudos/:studyId', name: 'study', component: StudyView, meta: { title: 'Ler estudo' } },
    { path: '/livros/:bookId/estudos/:studyId/editar', name: 'study-edit', component: StudyEditView, meta: { title: 'Editar estudo' } },
    { path: '/importar', name: 'import', component: ImportView, meta: { title: 'Importar estudo' } },
    { path: '/conexao', name: 'connection', component: ConnectionView, meta: { title: 'Conexão' } },
    { path: '/:pathMatch(.*)*', component: NotFoundView, meta: { title: 'Página não encontrada' } },
  ],
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    if (to.path === from.path) return false
    return { top: 0 }
  },
})

router.afterEach((to) => { document.title = `${String(to.meta.title)} · Caderno de Leitura` })
