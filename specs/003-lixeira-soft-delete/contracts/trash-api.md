# API Contract: Lixeira e Restauração de Itens (Soft Delete)

**Feature**: `003-lixeira-soft-delete`  
**Date**: 2026-09-18  
**Format**: Markdown / REST JSON  

---

## 1. Operações de Livro (`/api/books`)

### `POST /api/books/{id}/trash`
Envia o livro e todos os seus estudos subordinados para a lixeira.

- **Parâmetros de Rota**: `id: int`
- **Respostas**:
  - `200 OK`:
    ```json
    {
      "id": 1,
      "title": "Dom Casmurro",
      "deleted_at": "2026-09-18T19:30:00Z"
    }
    ```
  - `404 Not Found`: Livro não encontrado ou já excluído permanentemente.

---

### `POST /api/books/{id}/restore`
Restaura o livro da lixeira, trazendo de volta seus estudos (exceto aqueles descartados individualmente antes do livro).

- **Parâmetros de Rota**: `id: int`
- **Respostas**:
  - `200 OK`:
    ```json
    {
      "id": 1,
      "title": "Dom Casmurro",
      "deleted_at": null
    }
    ```
  - `404 Not Found`: Livro não encontrado.

---

### `DELETE /api/books/{id}/permanent`
Exclui definitivamente o livro, seus capítulos e estudos subordinados em uma transação atômica.

- **Parâmetros de Rota**: `id: int`
- **Respostas**:
  - `204 No Content`: Excluído com sucesso.
  - `404 Not Found`: Livro não encontrado.

---

## 2. Operações de Estudo (`/api/studies`)

### `POST /api/studies/{id}/trash`
Envia um estudo individual para a lixeira.

- **Parâmetros de Rota**: `id: int`
- **Respostas**:
  - `200 OK`:
    ```json
    {
      "id": 10,
      "title": "Capítulo 1 - Análise do Olhar de Ressaca",
      "deleted_at": "2026-09-18T19:30:00Z"
    }
    ```
  - `404 Not Found`: Estudo não encontrado.

---

### `POST /api/studies/{id}/restore`
Restaura um estudo da lixeira. Caso o livro ou capítulo pai esteja na lixeira, reativa automaticamente o livro e capítulo em cascata ascendente.

- **Parâmetros de Rota**: `id: int`
- **Respostas**:
  - `200 OK`:
    ```json
    {
      "id": 10,
      "title": "Capítulo 1 - Análise do Olhar de Ressaca",
      "deleted_at": null,
      "book_restored": true
    }
    ```
  - `404 Not Found`: Estudo não encontrado.

---

### `DELETE /api/studies/{id}/permanent`
Exclui definitivamente o estudo em transação atômica.

- **Parâmetros de Rota**: `id: int`
- **Respostas**:
  - `204 No Content`: Excluído com sucesso.
  - `404 Not Found`: Estudo não encontrado.

---

## 3. Painel da Lixeira (`/api/trash`)

### `GET /api/trash`
Retorna todos os livros na lixeira e todos os estudos individualmente descartados, com cálculo de dias restantes até o expurgo automático de 30 dias.

- **Respostas**:
  - `200 OK`:
    ```json
    {
      "books": [
        {
          "id": 1,
          "title": "Dom Casmurro",
          "author": "Machado de Assis",
          "deleted_at": "2026-09-18T10:00:00Z",
          "days_until_purge": 30,
          "chapters_count": 5,
          "studies_count": 12
        }
      ],
      "studies": [
        {
          "id": 10,
          "title": "Nota sobre narrador não confiável",
          "book_id": 2,
          "book_title": "Memórias Póstumas",
          "chapter_name": "Óbito do autor",
          "deleted_at": "2026-09-17T15:00:00Z",
          "days_until_purge": 29
        }
      ],
      "total_items": 2
    }
    ```

---

### `POST /api/trash/empty`
Expurga permanentemente todos os livros e estudos atualmente na lixeira.

- **Respostas**:
  - `200 OK`:
    ```json
    {
      "purged_books": 1,
      "purged_studies": 1,
      "message": "Lixeira esvaziada com sucesso."
    }
    ```

---

### `POST /api/trash/purge-expired`
Executa a rotina de limpeza de registros com `deleted_at` anterior a 30 dias.

- **Respostas**:
  - `200 OK`:
    ```json
    {
      "purged_books": 0,
      "purged_studies": 0
    }
    ```
