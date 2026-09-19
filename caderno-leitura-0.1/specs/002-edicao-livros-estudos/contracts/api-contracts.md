# Contratos de API: Edição e Concorrência

**Feature**: `002-edicao-livros-estudos`  
**Base URL**: `/api`  

---

## 1. Endpoints de Livros (`/books`)

### `PATCH /books/{book_id}`
Atualiza os metadados de um livro existente.

- **Parâmetros de Rota**:
  - `book_id`: ID numérico inteiro do livro.
- **Corpo da Requisição (`application/json`)**:
  ```json
  {
    "title": "A Arte da Guerra",
    "author": "Sun Tzu",
    "subtitle": "Tratado Estratégico",
    "year": 2020,
    "expected_updated_at": "2026-09-17T20:00:00Z"
  }
  ```
  *Todos os campos são opcionais no envio, mas ao menos um campo modificador deve ser fornecido.*
- **Respostas**:
  - **`200 OK`**:
    ```json
    {
      "id": 1,
      "title": "A Arte da Guerra",
      "author": "Sun Tzu",
      "subtitle": "Tratado Estratégico",
      "year": 2020,
      "created_at": "2026-09-10T12:00:00Z",
      "updated_at": "2026-09-17T21:30:00Z"
    }
    ```
  - **`404 Not Found`**: Livro não encontrado.
  - **`409 Conflict`**: O livro foi modificado em outro dispositivo após `expected_updated_at`.
  - **`422 Unprocessable Entity`**: Título em branco ou ano inválido (fora de 1000..2100).

---

## 2. Endpoints de Capítulos (`/books/{book_id}/chapters`)

### `PATCH /books/{book_id}/chapters/{chapter_id}`
Renomeia um capítulo existente.

- **Parâmetros de Rota**:
  - `book_id`: ID do livro pai.
  - `chapter_id`: ID do capítulo.
- **Corpo da Requisição**:
  ```json
  {
    "name": "Capítulo 1 — Avaliações Iniciais",
    "expected_updated_at": "2026-09-17T20:00:00Z"
  }
  ```
- **Respostas**:
  - **`200 OK`**: Retorna o objeto `ChapterRead` atualizado.
  - **`404 Not Found`**: Livro ou capítulo não encontrado.
  - **`409 Conflict`**: Conflito de concorrência.
  - **`422 Unprocessable Entity`**: Nome vazio ou composto apenas por espaços.

### `POST /books/{book_id}/chapters/{chapter_id}/move`
Troca a posição do capítulo com o adjacente (subir ou descer).

- **Corpo da Requisição**:
  ```json
  {
    "direction": "up"
  }
  ```
  *Valores aceitos para `direction`: `"up"` (subir para índice menor) ou `"down"` (descer para índice maior).*
- **Respostas**:
  - **`200 OK`**: Retorna a lista completa ordenada `list[ChapterRead]` do livro.
  - **`400 Bad Request`**: Capítulo já está no topo ou no final da lista.
  - **`404 Not Found`**: Livro ou capítulo inexistente.

---

## 3. Endpoints de Estudos (`/studies`)

### `PATCH /studies/{study_id}`
Atualiza os campos editáveis de um estudo, com proteção de versão.

- **Parâmetros de Rota**:
  - `study_id`: ID do estudo.
- **Corpo da Requisição**:
  ```json
  {
    "title": "Nova perspectiva sobre estratégia",
    "location": "p. 45–48",
    "summary": "Resumo atualizado.",
    "explanation": "Explicação revisada.",
    "concepts": "Conceito A.",
    "references": "Ref 1.",
    "notes": "Minha reflexão aprofundada.",
    "expected_updated_at": "2026-09-17T20:00:00Z"
  }
  ```
  *(O campo `source_response` nunca é aceito para edição)*
- **Respostas**:
  - **`200 OK`**: Retorna `StudyRead` com novo `updated_at`.
  - **`404 Not Found`**: Estudo inexistente.
  - **`409 Conflict`**: Conflito de versão (modificado em outro dispositivo).
  - **`422 Unprocessable Entity`**: Todas as 4 seções de análise em branco.
