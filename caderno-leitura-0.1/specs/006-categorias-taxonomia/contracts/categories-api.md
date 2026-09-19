# API & Interface Contracts: Categorias e Taxonomia de Livros (T05)

**Feature**: `006-categorias-taxonomia`  
**Date**: 2026-09-18  
**Status**: Ready

---

## 1. Endpoints de Categorias

### 1.1 Listar Categorias da Taxonomia
Retorna todas as categorias ativas do catálogo canônico com seus caminhos hierárquicos formatados.

- **Método / Rota**: `GET /api/categories`
- **Parâmetros de Consulta**:
  - `q` (*string, opcional*): Termo de busca para filtragem rápida no servidor (insensível a caixa e acentos).
- **Respostas**:
  - `200 OK`:
    ```json
    [
      {
        "id": "ciencias-humanas",
        "name": "Ciências Humanas",
        "parent_id": null,
        "path": "Ciências Humanas"
      },
      {
        "id": "filosofia",
        "name": "Filosofia",
        "parent_id": "ciencias-humanas",
        "path": "Ciências Humanas / Filosofia"
      },
      {
        "id": "filosofia-etica",
        "name": "Ética",
        "parent_id": "filosofia",
        "path": "Ciências Humanas / Filosofia / Ética"
      }
    ]
    ```

---

## 2. Endpoints de Livros com Categorias

### 2.1 Listar Livros com Filtro Recursivo de Categoria
- **Método / Rota**: `GET /api/books`
- **Parâmetros de Consulta**:
  - `category` (*string, opcional*): ID da categoria a ser filtrada (ex.: `filosofia`).
  - `q` (*string, opcional*): Busca textual em título, autor e subtítulo.
  - `sort` (*string, opcional*): Campo de ordenação (`title`, `author`, `created_at`, `updated_at`, `year`).
  - `order` (*string, opcional*): Direção (`asc` ou `desc`).
- **Comportamento do Filtro**:
  - Se `category` for fornecido, a consulta localiza a categoria e todas as suas subcategorias descendentes via CTE recursiva, retornando todos os livros que possuem ao menos uma dessas categorias associadas.
  - Livros com `deleted_at IS NOT NULL` permanecem 100% excluídos.
- **Respostas**:
  - `200 OK`:
    ```json
    [
      {
        "id": 1,
        "title": "Ética a Nicômaco",
        "author": "Aristóteles",
        "subtitle": "",
        "year": -350,
        "cover_image": null,
        "created_at": "2026-09-18T12:00:00Z",
        "updated_at": "2026-09-18T12:00:00Z",
        "deleted_at": null,
        "categories": [
          {
            "id": "filosofia-etica",
            "name": "Ética",
            "parent_id": "filosofia",
            "path": "Ciências Humanas / Filosofia / Ética"
          }
        ]
      }
    ]
    ```

### 2.2 Consultar Livro por ID
- **Método / Rota**: `GET /api/books/{book_id}`
- **Respostas**:
  - `200 OK`: `BookRead` completo com lista de objetos `categories: list[CategoryRead]`.
  - `404 Not Found`: Quando o livro não existe ou está excluído.

### 2.3 Criar Livro com Categorias
- **Método / Rota**: `POST /api/books`
- **Corpo da Requisição (`BookCreate`)**:
  ```json
  {
    "title": "Memórias Póstumas de Brás Cubas",
    "author": "Machado de Assis",
    "subtitle": "",
    "year": 1881,
    "category_ids": ["literatura-brasileira", "literatura-ficcao"]
  }
  ```
- **Respostas**:
  - `201 Created`: Livro criado com categorias vinculadas.
  - `400 Bad Request`: Se algum `category_id` não existir no catálogo ou o título for inválido.

### 2.4 Atualizar Livro Parcialmente
- **Método / Rota**: `PATCH /api/books/{book_id}`
- **Corpo da Requisição (`BookPatch`)**:
  ```json
  {
    "category_ids": ["literatura-brasileira"]
  }
  ```
- **Regras de Preservação e Sincronização**:
  - Se `category_ids` não for enviado no JSON, as categorias existentes do livro são **preservadas**.
  - Se `category_ids` for enviado como `[]`, todas as categorias são removidas do livro.
  - Se `category_ids` contiver identificadores inválidos, a requisição é rejeitada com `400 Bad Request` antes de persistir qualquer alteração.
- **Respostas**:
  - `200 OK`: Livro atualizado com a nova lista de categorias.
  - `400 Bad Request`: Categoria inexistente ou payload sem alterações.
  - `404 Not Found`: Livro inexistente.

---

## 3. Contratos de Tipos no Frontend (`frontend/src/types.ts`)

```typescript
export interface Category {
  id: string
  name: string
  parent_id: string | null
  path: string
}

export interface Book {
  id: number
  title: string
  author: string | null
  subtitle?: string | null
  year?: number | null
  cover_image?: string | null
  created_at?: string | null
  updated_at?: string | null
  deleted_at?: string | null
  categories?: Category[]
}

export interface BookCreatePayload {
  title: string
  author?: string | null
  subtitle?: string | null
  year?: number | null
  category_ids?: string[]
}

export interface BookPatch {
  title?: string
  author?: string | null
  subtitle?: string | null
  year?: number | null
  cover_image?: string | null
  expected_updated_at?: string | null
  category_ids?: string[]
}

export interface LibraryFilterState {
  searchQuery: string
  selectedCategory: string | null
  viewMode: LibraryViewMode
  sortBy: BookSortOption
}
```
