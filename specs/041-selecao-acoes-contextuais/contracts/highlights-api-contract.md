# API Contract: Gerenciamento de Destaques de Estudos

**Endpoints**: `/api/studies/{study_id}/highlights`  
**Tags**: `["Destaques e Anotações de Estudos"]`  
**Autenticação**: Sessão ou Bearer Token (ou usuário padrão se `REQUIRE_AUTH=false`)  

---

## 1. Listar Destaques do Estudo

### Requisição
`GET /api/studies/{study_id}/highlights`

*Parâmetros de Rota*:
- `study_id` (int, obrigatório): Identificador do estudo.

*Parâmetros de Consulta (Query)*:
- `section` (string, opcional): Filtrar por seção (`summary`, `explanation`, `concepts`, `references`).

### Resposta de Sucesso
`200 OK`

```json
[
  {
    "id": 1,
    "study_id": 42,
    "user_id": "00000000-0000-0000-0000-000000000001",
    "section": "summary",
    "start_offset": 12,
    "end_offset": 64,
    "selected_text": "A revolução industrial transformou o modo de produção",
    "prefix": "No século XVIII, ",
    "suffix": " em escala global.",
    "color": "yellow",
    "kind": "highlight",
    "note": "",
    "created_at": "2026-09-27T01:30:00Z",
    "updated_at": "2026-09-27T01:30:00Z"
  }
]
```

### Respostas de Erro
- `404 Not Found`: Estudo inexistente ou excluído.
- `403 Forbidden`: Usuário não possui permissão para ler o estudo.

---

## 2. Criar Destaque / Anotação

### Requisição
`POST /api/studies/{study_id}/highlights`

*Headers*:
- `Content-Type: application/json`

*Corpo da Requisição*:
```json
{
  "section": "summary",
  "start_offset": 12,
  "end_offset": 64,
  "selected_text": "A revolução industrial transformou o modo de produção",
  "prefix": "No século XVIII, ",
  "suffix": " em escala global.",
  "color": "yellow",
  "kind": "highlight",
  "note": ""
}
```

### Resposta de Sucesso
`201 Created`

Retorna o objeto `StudyHighlightRead` criado.

### Respostas de Erro
- `422 Unprocessable Entity`: Validação falhou (texto selecionado vazio, offsets inválidos ou cor/tipo não reconhecidos).
- `404 Not Found`: Estudo inexistente.
- `403 Forbidden`: Usuário sem permissão de edição do estudo.

---

## 3. Atualizar Destaque / Nota

### Requisição
`PATCH /api/studies/{study_id}/highlights/{highlight_id}`

*Corpo da Requisição*:
```json
{
  "color": "green",
  "note": "Ponto fundamental para o ensaio comparativo.",
  "kind": "note"
}
```

### Resposta de Sucesso
`200 OK`

Retorna o objeto `StudyHighlightRead` atualizado.

---

## 4. Remover Destaque

### Requisição
`DELETE /api/studies/{study_id}/highlights/{highlight_id}`

### Resposta de Sucesso
`204 No Content`

### Respostas de Erro
- `404 Not Found`: Destaque inexistente.
- `403 Forbidden`: Destaque pertence a outro usuário ou estudo em modo somente leitura.
