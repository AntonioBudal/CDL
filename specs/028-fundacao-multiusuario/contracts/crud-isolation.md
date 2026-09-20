# Contract: Isolamento e Autorização no CRUD Geral (F01)

**Protocol**: HTTP / REST  
**Base Path**: `/api`  

---

## 1. Livros (`/api/books`)

### `GET /api/books`
- **Filtro Aplicado**: `Book.user_id == current_user.id AND Book.deleted_at IS NULL`
- **Retorno**: Apenas livros do usuário ativo.

### `POST /api/books`
- **Comportamento**: O campo `user_id` é injetado automaticamente como `current_user.id`.
- **Payload de Entrada**:
  ```json
  {
    "title": "A Ética Demonstrada à Maneira dos Geômetras",
    "author": "Baruch Spinoza",
    "subtitle": "Tratado Filosófico",
    "year": 1677
  }
  ```
- **Response 201 Created**:
  ```json
  {
    "id": 1,
    "user_id": "00000000-0000-0000-0000-000000000001",
    "title": "A Ética Demonstrada à Maneira dos Geômetras",
    "author": "Baruch Spinoza",
    "subtitle": "Tratado Filosófico",
    "year": 1677,
    "created_at": "2026-09-20T12:00:00Z",
    "updated_at": "2026-09-20T12:00:00Z",
    "deleted_at": null,
    "cover_image": null
  }
  ```

### `GET /api/books/{id}`
- **Comportamento**: Busca por `id`.
  - Se `book.user_id == current_user.id`: Retorna 200 OK com o livro.
  - Se `book` não existe OU `book.user_id != current_user.id`:
    ```json
    HTTP/1.1 404 Not Found
    Content-Type: application/json

    {
      "detail": "Livro não encontrado."
    }
    ```

### `PATCH /api/books/{id}`
- **Comportamento**: Apenas o proprietário pode alterar. Se pertencer a outro usuário, retorna `HTTP 404 Not Found`.

### `DELETE /api/books/{id}` (Mover para Lixeira)
- **Comportamento**: Define `deleted_at = UTC now` para o livro e todos os seus estudos/capítulos. Se pertencer a outro usuário, retorna `HTTP 404 Not Found`.

---

## 2. Estudos (`/api/studies`)

### `GET /api/studies`
- **Filtro Aplicado**: `Study.user_id == current_user.id AND Study.deleted_at IS NULL`
- **Retorno**: Apenas estudos de autoria do usuário autenticado.

### `POST /api/studies`
- **Validação Cruzada**: O capítulo informado em `chapter_id` deve pertencer a um livro cujo `user_id == current_user.id`. Se o capítulo for de outro leitor, retorna `HTTP 404 Not Found`.
- **Injeção**: `study.user_id = current_user.id`.

### `GET /api/studies/{id}`
- **Comportamento**:
  - Se `study.user_id == current_user.id`: Retorna 200 OK.
  - Se `study` for de outro leitor: Retorna `HTTP 404 Not Found` (proteção anti-enumeração IDOR).

### `PATCH /api/studies/{id}`
- **Comportamento**: Se pertencer a outro leitor, retorna `HTTP 404 Not Found`.

---

## 3. Categorias Taxonômicas (`/api/categories`)

### `GET /api/categories`
- **Filtro Aplicado**: `Category.user_id IS NULL OR Category.user_id == current_user.id`
- **Retorno**: Todas as categorias padrão do sistema combinadas com as categorias pessoais criadas pelo usuário ativo.

### `POST /api/categories`
- **Comportamento**: Registra a nova categoria atribuindo `user_id = current_user.id`.

### `DELETE /api/categories/{id}`
- **Comportamento**:
  - Se a categoria for do sistema (`user_id IS NULL`): Retorna `HTTP 403 Forbidden` (`"Categorias padrão do sistema não podem ser excluídas."`).
  - Se a categoria for de outro usuário: Retorna `HTTP 404 Not Found`.
  - Se for do usuário ativo: Exclui a categoria personalizada (204 No Content).

---

## 4. Lixeira (`/api/trash`)

### `GET /api/trash`
- **Filtro Aplicado**: Itens excluídos com `deleted_at IS NOT NULL AND user_id == current_user.id`.
- **Retorno**: Apenas recursos descartados pelo usuário atual.

### `POST /api/trash/books/{id}/restore` & `POST /api/trash/studies/{id}/restore`
- **Comportamento**: Se o item pertencer a outro usuário, retorna `HTTP 404 Not Found`.
