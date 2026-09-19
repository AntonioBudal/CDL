# API Contract: Exportação de Anotações

**Feature Branch**: `015-exportacao-anotacoes`  
**Date**: 2026-09-19  

---

## 1. Exportar Livro Completo

Gera e faz download do arquivo consolidado de um livro com todos os seus capítulos e estudos ativos.

### Endpoint
`GET /api/books/{book_id}/export`

### Parâmetros de Consulta (Query Params)
| Parâmetro | Tipo | Padrão | Descrição |
|:---|:---|:---|:---|
| `format` | `string` | `"markdown"` | Formato de exportação: `"markdown"` ou `"text"` |
| `include_notes` | `boolean` | `true` | Incluir anotações pessoais |
| `include_sections` | `boolean` | `true` | Incluir as 4 seções de análise |
| `include_source` | `boolean` | `false` | Incluir resposta bruta da IA |
| `include_metadata` | `boolean` | `true` | Incluir metadados de cabeçalho |

### Respostas

#### Sucesso: HTTP 200 OK (Markdown)
- **Headers**:
  - `Content-Type: text/markdown; charset=utf-8`
  - `Content-Disposition: attachment; filename="memorias-postumas-de-bras-cubas.md"`
- **Corpo**: Conteúdo textual codificado em UTF-8 com Frontmatter YAML e capítulos/estudos hierárquicos.

#### Sucesso: HTTP 200 OK (Texto Puro)
- **Headers**:
  - `Content-Type: text/plain; charset=utf-8`
  - `Content-Disposition: attachment; filename="memorias-postumas-de-bras-cubas.txt"`
- **Corpo**: Conteúdo em texto puro codificado em UTF-8 com divisores ASCII.

#### Erros:
- `HTTP 404 Not Found`: Livro inexistente ou que esteja na lixeira (`deleted_at IS NOT NULL`).
  ```json
  { "detail": "Livro não encontrado." }
  ```

---

## 2. Exportar Estudo Individual

Gera e faz download do arquivo contendo exclusivamente os dados de um único estudo.

### Endpoint
`GET /api/studies/{study_id}/export`

### Parâmetros de Consulta (Query Params)
Mesmos parâmetros descritos acima (`format`, `include_notes`, `include_sections`, `include_source`, `include_metadata`).

### Respostas

#### Sucesso: HTTP 200 OK
- **Headers**:
  - `Content-Type: text/markdown; charset=utf-8` (ou `text/plain; charset=utf-8`)
  - `Content-Disposition: attachment; filename="memorias-postumas-cap-01-estudo-01.md"`
- **Corpo**: Conteúdo do estudo codificado em UTF-8.

#### Erros:
- `HTTP 404 Not Found`: Estudo inexistente ou que esteja na lixeira (`deleted_at IS NOT NULL`).
  ```json
  { "detail": "Estudo não encontrado." }
  ```
