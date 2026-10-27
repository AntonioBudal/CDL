# Contrato: API de Digitalização

**Feature**: `086-digitalizar-caderno-estudo` | Router: `backend/app/routers/digitize.py` | Prefixo: `/api/digitize`

As duas rotas exigem usuário autenticado (`CurrentUser`), nenhuma acessa o banco além da autenticação, e as duas
respondem com `Cache-Control: no-store`.

---

## `GET /api/digitize/status`

Informa se a digitalização está disponível nesta instalação.

**200**
```json
{ "available": true, "reason": null }
```
```json
{ "available": false, "reason": "not_installed" }
```

`reason` ∈ `null`, `not_installed`, `integrity_failed`. Nunca contém caminhos.

## `POST /api/digitize/preview`

Lê uma foto de página e devolve o texto para revisão. **Não grava nada no banco.** Para salvar, o cliente usa
`POST /api/studies`, como na importação.

**Requisição**: `multipart/form-data` com um campo `file` (JPEG, PNG ou WebP, até 20 MB e 40 MP).

**200**
```json
{
  "text": "Capítulo 1\nLinha de exemplo fictícia",
  "lines": [
    { "index": 0, "text": "Capítulo 1", "confidence": 0.93, "low_confidence": false },
    { "index": 1, "text": "Linha de exemplo fictícia", "confidence": 0.61, "low_confidence": true }
  ],
  "low_confidence_count": 1,
  "warnings": [
    { "code": "draft", "message": "Texto lido automaticamente. Pode conter erros: revise antes de salvar." }
  ],
  "engine": { "name": "leitorum-motor", "version": "0.1.0", "reader": "PP-OCRv6 small", "license_status": "VERIFIED" },
  "elapsed_ms": 8421
}
```

**Erros**: o corpo é `{"detail": "<mensagem em português>", "code": "<código>"}`.

| Status | `code` | Quando |
| :--- | :--- | :--- |
| 401 | — | sem sessão (comportamento padrão de `CurrentUser`) |
| 413 | `too_large` | arquivo > 20 MB ou imagem > 40 MP |
| 415 | `unsupported_format` | formato fora de JPEG, PNG ou WebP (inclui HEIC e PDF) |
| 422 | `invalid_image` | arquivo corrompido, truncado ou ausente |
| 503 | `unavailable` | motor não instalado ou com integridade falha |
| 503 | `busy` | outro pedido em andamento; inclui `Retry-After: 15` |
| 503 | `low_memory` | memória livre abaixo do mínimo (padrão 2 GiB) |
| 504 | `timeout` | o motor passou de 120 s e foi encerrado |
| 500 | `engine_failed` | o motor terminou com erro ou com saída inválida (detalhe só no log local, sem texto) |

**Garantias**:
- A imagem e a pasta temporária são apagadas antes da resposta, em qualquer desfecho, inclusive na desconexão do
  cliente.
- Nenhum texto lido aparece em logs.
- Nenhuma requisição sai da máquina.
