# API Contract: Dashboard de Leitura

**Feature**: `013-dashboard-calendario-timeline`  
**Endpoint**: `GET /api/dashboard`  
**Version**: 1.0  
**Status**: Approved  

---

## 1. Visão Geral
Fornece os dados consolidados de produtividade do leitor, incluindo cartões de resumo, mapa de calor anual/periódico e timeline cronológica reversa de atividades recentes.

---

## 2. Especificação do Endpoint

### `GET /api/dashboard`

Retorna as métricas agregadas, a lista de pontos do mapa de calor e a lista de atividades recentes.

#### Parâmetros de Consulta (Query Parameters)

| Parâmetro | Tipo | Obrigatório? | Padrão | Descrição |
|---|---|---|---|---|
| `tz_offset` | `integer` | Não | `0` | Deslocamento do fuso horário local do cliente em minutos em relação ao UTC (ex.: `-180` para UTC-3 / Horário de Brasília). |
| `days` | `integer` | Não | `365` | Quantidade de dias passados para projeção do mapa de calor (limite: 30 a 730). |
| `date` | `string` | Não | `null` | Filtro opcional de data (`YYYY-MM-DD`) para restringir a timeline aos eventos de um dia civil específico. |
| `limit` | `integer` | Não | `30` | Quantidade máxima de itens retornados na lista da timeline (limite: 1 a 100). |

---

### Exemplo de Requisição

```http
GET /api/dashboard?tz_offset=-180&days=365&limit=20 HTTP/1.1
Host: localhost:8000
Accept: application/json
```

---

### Resposta de Sucesso (HTTP 200 OK)

```json
{
  "summary": {
    "total_books": 12,
    "total_studies": 47,
    "total_reading_days": 28,
    "current_streak": 4,
    "avg_studies_per_book": 3.9
  },
  "heatmap": [
    {
      "date": "2025-09-20",
      "count": 0,
      "level": 0
    },
    {
      "date": "2026-09-18",
      "count": 2,
      "level": 2
    },
    {
      "date": "2026-09-19",
      "count": 5,
      "level": 3
    }
  ],
  "timeline": [
    {
      "id": "study-105-created",
      "entity_type": "study",
      "action": "study_created",
      "timestamp": "2026-09-19T11:45:00Z",
      "title": "Análise Estrutural do Capítulo 3",
      "book_id": 4,
      "book_title": "Memórias Póstumas de Brás Cubas",
      "chapter_id": 8,
      "chapter_title": "Capítulo III",
      "study_id": 105
    },
    {
      "id": "book-12-created",
      "entity_type": "book",
      "action": "book_created",
      "timestamp": "2026-09-18T16:20:00Z",
      "title": "Grande Sertão: Veredas",
      "book_id": 12,
      "book_title": "Grande Sertão: Veredas",
      "chapter_id": null,
      "chapter_title": null,
      "study_id": null
    }
  ]
}
```

---

### Resposta de Erro (HTTP 422 Unprocessable Entity)

Retornado caso os parâmetros violem os tipos ou limites estipulados:

```json
{
  "detail": [
    {
      "type": "string_pattern_mismatch",
      "loc": ["query", "date"],
      "msg": "Formato de data inválido. Use o padrão YYYY-MM-DD.",
      "input": "data-invalida"
    }
  ]
}
```

---

## 3. Contratos de Navegação no Frontend

1. **Rota Principal**: `/dashboard`
   - Componente associado: `DashboardView.vue`
   - Rótulo no cabeçalho: `Dashboard`
   - Meta title: `Dashboard · Caderno de Leitura`
   - Envoltório DOM: nó raiz único `<div class="dashboard-view">` sob transição `<Transition mode="out-in">`.
2. **Links de Ação na Timeline**:
   - Para estudos: navega para `/livros/:bookId/estudos/:studyId`.
   - Para livros: navega para `/livros/:bookId`.
