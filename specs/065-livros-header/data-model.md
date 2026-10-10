# Data Model: F0.8.01 — Curadoria Editorial, Biblioteca Ativa e Novo Header Global

## Entidades e Modelos de Dados

A feature F0.8.01 foca em reestruturação de layout, arquitetura do App Shell e componentes de interface, sem modificar esquemas relacionais no banco de dados SQLite. Os modelos e estados envolvidos são descritos a seguir:

---

### 1. Entidade de Domínio Existente: `Book`

A entidade `Book` é mantida integralmente compatível com o schema e contratos de API existentes.

| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | `int` | Identificador único do livro no acervo. |
| `title` | `str` | Título da obra (obrigatório, preenchido no Drawer). |
| `author` | `str \| null` | Autor da obra (opcional). |
| `subtitle` | `str \| null` | Subtítulo da obra (opcional). |
| `year` | `int \| null` | Ano de publicação (opcional). |
| `cover_image` | `str \| null` | Imagem da capa ou null para capa tipográfica nativa. |
| `categories` | `Category[]` | Lista de categorias atribuídas. |
| `created_at` | `str` | Timestamp ISO de cadastro. |
| `updated_at` | `str` | Timestamp ISO da última alteração (utilizado para ordenar o Hero Card). |

---

### 2. Estado de Interface do Header Global (`GlobalHeaderState`)

Estado local reativo para controle dos menus suspensos e zonas do cabeçalho:

```typescript
interface GlobalHeaderState {
  isMoreMenuOpen: boolean       // Estado do menu retrátil "Mais ▾"
  isUserDropdownOpen: boolean   // Estado do dropdown de perfil e logout
  primaryRoutes: NavLinkItem[]  // Rotas diretas: Livros, Destaques, Revisão, Inbox
  secondaryRoutes: NavLinkItem[] // Rotas no menu "Mais": Importar, Amigos, Ajustes, Lixeira, Admin
}
```

---

### 3. Contrato de Props e Eventos do Componente `Drawer`

```typescript
interface DrawerProps {
  open: boolean                 // Controla visibilidade da gaveta lateral
  title: string                 // Título do cabeçalho do Drawer (aria-labelledby)
  description?: string          // Descrição de apoio opcional
  width?: string                // Largura no desktop (padrão: "420px")
}

interface DrawerEmits {
  (e: 'close'): void            // Disparado no clique do fechar, Esc ou backdrop
}
```

---

### 4. Modelo de Leitura Ativa (`ActiveReadingHero`)

Calculado reativamente a partir do acervo de livros do leitor:

```typescript
interface ActiveReadingHero {
  book: Book                    // Obra em andamento selecionada (mais recente)
  hasRecentActivity: boolean    // Indica se possui estudos recentes
}
```
Regra de determinação:
- O livro com maior `updated_at` entre os livros ativos (`is_deleted == false`).
- Fallback para o primeiro livro da lista caso os timestamps sejam idênticos.
- Caso a biblioteca esteja vazia, a seção Hero é ocultada automaticamente.
