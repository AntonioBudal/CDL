# Data Model: F0.9.01 — Arquitetura de Navegação Global e Shell Responsivo

**Feature**: `specs/082-navegacao-global-shell-responsivo`  
**Date**: 2026-10-20  

---

## 1. Tipos de Navegação e Breadcrumb

A tipagem da navegação é isolada no módulo de tipos de navegação do frontend:

```typescript
// frontend/src/types/navigation.ts

import type { RouteLocationRaw } from 'vue-router'
import type { IconName } from './index'

/**
 * Item individual de trilha de navegação (Breadcrumb).
 */
export interface BreadcrumbItem {
  /** Rótulo legível exibido no item */
  label: string
  /** Destino da rota. Se omitido ou current = true, renderizado como texto/página atual */
  to?: RouteLocationRaw
  /** Indica se é a página ativa/atual */
  current?: boolean
}

/**
 * Item primário da barra de navegação desktop.
 */
export interface PrimaryNavItem {
  to: string
  label: string
  routes: string[]
  icon: IconName
  badgeCount?: () => number
}

/**
 * Item secundário exibido no dropdown "Mais".
 */
export interface SecondaryNavItem {
  to: string
  label: string
  routes: string[]
  icon: IconName
  requiresAdmin?: boolean
  badgeCount?: () => number
}
```

---

## 2. Matriz de Mapeamento de Rotas no Desktop

| Rótulo | Rota Alvo | Rotas Ativas Correlatas | Ícone | Posição |
| :--- | :--- | :--- | :--- | :--- |
| **Dashboard** | `/dashboard` | `['dashboard']` | `layout-dashboard` | Item Primário 1 |
| **Livros** | `/livros` | `['books', 'book', 'study', 'study-edit']` | `book-open` | Item Primário 2 |
| **Destaques** | `/highlights` | `['highlights']` | `pencil` | Item Primário 3 |
| **Revisão** | `/review` | `['review', 'study-session']` | `rotate-ccw` | Item Primário 4 |
| **Inbox** | `/inbox` | `['inbox']` | `inbox` | Item Primário 5 |
| **Mais ▾** | Dropdown | `['import', 'friends', 'settings', 'connection', 'trash', 'admin']` | `more-horizontal` | Menu Retrátil |

---

## 3. Matriz de Breadcrumb por Visão

| Visão / Arquivo | Estrutura de Itens do Breadcrumb | Destinos dos Links |
| :--- | :--- | :--- |
| **BookView** | `[Livros, Título do Livro]` | `[{ label: 'Livros', to: '/livros' }, { label: book.title, current: true }]` |
| **StudyView** | `[Livros, Título do Livro · Capítulo, Título do Estudo]` | `[{ label: 'Livros', to: '/livros' }, { label: `${book.title} · ${chapter.name}`, to: { name: 'book', params: { bookId }, query: { chapter: chapterId } } }, { label: study.title, current: true }]` |
| **StudyEditView** | `[Livros, Título do Livro · Capítulo, Editar estudo]` | `[{ label: 'Livros', to: '/livros' }, { label: `${book.title} · ${chapter.name}`, to: { name: 'book', ... } }, { label: 'Editar estudo', current: true }]` |
| **UserProfileView** | `[Livros, Perfil de @username]` | `[{ label: 'Livros', to: '/livros' }, { label: `@${username}`, current: true }]` |
