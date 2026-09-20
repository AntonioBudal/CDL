# Contract: Search REST API

**Feature Branch**: `025-busca-global-contextual`  
**Date**: 2026-09-19  
**Base URL**: `/api/search`  

---

## 1. `GET /api/search`

Executa a busca transversal de estudos e anotações com suporte a múltiplos termos, normalização de acentos, geração de snippets contextuais com realce seguro e filtros por livro ou categoria.

### Parâmetros de Consulta (Query String)

| Parâmetro | Tipo | Obrigatório | Padrão | Descrição |
| :--- | :--- | :---: | :---: | :--- |
| `q` | `string` | **Sim** | — | Termo ou expressão de busca (mínimo de 2 caracteres). |
| `mode` | `string` | Não | `"and"` | Modo de combinação de múltiplos termos: `"and"` (todos presentes) ou `"or"` (qualquer um presente). |
| `book_id` | `integer` | Não | `null` | Restringe a busca aos estudos pertencentes ao livro indicado. |
| `category_id` | `integer` | Não | `null` | Restringe a busca aos estudos de livros associados à categoria informada. |
| `limit` | `integer` | Não | `20` | Quantidade máxima de resultados retornados (máximo: 100). |

### Resposta de Sucesso (`HTTP 200 OK`)

```json
{
  "query": "dialética",
  "mode": "and",
  "total": 2,
  "suggest_or": false,
  "results": [
    {
      "study_id": 14,
      "study_title": "A Contradição como Motor",
      "book_id": 3,
      "book_title": "Ciência da Lógica",
      "chapter_id": 7,
      "chapter_name": "Doutrina do Ser",
      "reading_status": "revisado",
      "matched_field": "Resumo",
      "snippet": "…o desdobramento da ideia através da <mark class=\"search-highlight\">dialética</mark> imanente ao próprio pensamento puro…",
      "updated_at": "2026-09-19T20:15:00Z"
    },
    {
      "study_id": 22,
      "study_title": "Materialismo e Método",
      "book_id": 5,
      "book_title": "O Capital",
      "chapter_id": 11,
      "chapter_name": "O Método da Economia Política",
      "reading_status": "concluido",
      "matched_field": "Conceitos",
      "snippet": "…inversão materialista da <mark class=\"search-highlight\">dialética</mark> hegeliana aplicada às relações de produção…",
      "updated_at": "2026-09-18T14:30:00Z"
    }
  ]
}
```

### Respostas de Erro

- **`HTTP 422 Unprocessable Entity`**: Parâmetro `q` ausente ou com comprimento inferior a 2 caracteres.
  ```json
  {
    "detail": [
      {
        "loc": ["query", "q"],
        "msg": "O termo de busca deve conter no mínimo 2 caracteres.",
        "type": "value_error"
      }
    ]
  }
  ```

---

## 2. `GET /api/search/history`

Retorna a lista dos termos pesquisados recentemente, ordenados do mais recente para o mais antigo (limite de 10 registros).

### Resposta de Sucesso (`HTTP 200 OK`)

```json
{
  "items": [
    {
      "id": 8,
      "query": "dialética",
      "created_at": "2026-09-19T21:00:00Z",
      "updated_at": "2026-09-19T22:10:00Z"
    },
    {
      "id": 5,
      "query": "ontologia hermenêutica",
      "created_at": "2026-09-19T18:40:00Z",
      "updated_at": "2026-09-19T18:40:00Z"
    }
  ]
}
```

---

## 3. `DELETE /api/search/history/{id}`

Exclui atomicamente um termo específico do histórico de pesquisas.

### Resposta de Sucesso (`HTTP 204 No Content`)

Corpo de resposta vazio.

### Respostas de Erro

- **`HTTP 404 Not Found`**: Registro com o `id` informado não encontrado.

---

## 4. `DELETE /api/search/history`

Limpa integralmente todo o histórico de pesquisas recentes da aplicação.

### Resposta de Sucesso (`HTTP 204 No Content`)

Corpo de resposta vazio.
