# API Contract: Importação e Prévia de Estudos

**Feature**: `040-importacao-inteligente`  
**Endpoint**: `POST /api/imports/preview`

---

## 1. Requisição de Prévia

### `POST /api/imports/preview`
Recebe o texto bruto colado pelo usuário e retorna as seções identificadas sem persistir nada no banco de dados.

#### Headers
```http
Content-Type: application/json
```

#### Request Body
```json
{
  "source_response": "# 1. Visão Geral\nEste capítulo aborda os fundamentos...\n\n**Aprofundamento:**\nO autor explora detalhadamente...\n\n## Termos-chave\n- Paradigma: modelo conceitual.\n\n### Fontes Consultadas\n- Livro X, 2024."
}
```

#### JSON Schema da Requisição
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ImportPreviewRequest",
  "type": "object",
  "properties": {
    "source_response": {
      "type": "string",
      "description": "Texto integral colado pelo usuário para extração estruturada"
    }
  },
  "required": ["source_response"]
}
```

---

## 2. Resposta da Prévia

#### Status Codes
- `200 OK`: Análise realizada com sucesso (com ou sem avisos).
- `422 Unprocessable Entity`: Payload malformatado.

#### Response Body (`200 OK`)
```json
{
  "source_response": "# 1. Visão Geral\nEste capítulo aborda os fundamentos...\n\n**Aprofundamento:**\nO autor explora detalhadamente...\n\n## Termos-chave\n- Paradigma: modelo conceitual.\n\n### Fontes Consultadas\n- Livro X, 2024.",
  "summary": "Este capítulo aborda os fundamentos...\n\n",
  "explanation": "O autor explora detalhadamente...\n\n",
  "concepts": "- Paradigma: modelo conceitual.\n\n",
  "references": "- Livro X, 2024.",
  "unassigned_text": "",
  "warnings": []
}
```

#### Exemplo de Resposta com Texto Não Classificado e Avisos
```json
{
  "source_response": "Aqui está a síntese que você pediu:\n\n## Resumo\nTexto do resumo...\n",
  "summary": "Texto do resumo...\n",
  "explanation": "",
  "concepts": "",
  "references": "",
  "unassigned_text": "Aqui está a síntese que você pediu:\n\n",
  "warnings": [
    {
      "code": "unassigned_text",
      "message": "Há texto antes da primeira seção. Revise 'Texto não associado' antes de salvar.",
      "section": null,
      "line": 1
    },
    {
      "code": "missing_section",
      "message": "Seção 'Explicação' não encontrada.",
      "section": "explanation",
      "line": null
    },
    {
      "code": "missing_section",
      "message": "Seção 'Conceitos' não encontrada.",
      "section": "concepts",
      "line": null
    },
    {
      "code": "missing_section",
      "message": "Seção 'Referências' não encontrada.",
      "section": "references",
      "line": null
    }
  ]
}
```

---

## 3. Criação do Estudo (`POST /api/studies`)

Endpoint padrão de persistência do estudo no acervo após a conferência da prévia.

#### Request Body
```json
{
  "chapter_id": 12,
  "title": "Fundamentos do Capítulo 1",
  "location": "p. 15-20",
  "source_response": "# 1. Visão Geral\nEste capítulo aborda...",
  "summary": "Este capítulo aborda os fundamentos...",
  "explanation": "O autor explora detalhadamente...",
  "concepts": "- Paradigma: modelo conceitual.",
  "references": "- Livro X, 2024.",
  "notes": "Minhas notas pessoais..."
}
```

#### Status Codes
- `201 Created`: Estudo criado e persistido no banco com sucesso.
- `400 Bad Request` / `422 Unprocessable Entity`: Dados inválidos.
- `401 Unauthorized`: Usuário não autenticado.
