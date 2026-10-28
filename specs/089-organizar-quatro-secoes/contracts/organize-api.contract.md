# Contrato: Organização nas 4 Seções

**Feature**: `089-organizar-quatro-secoes` | Router: `backend/app/routers/imports.py` | Prefixo: `/api/imports`

As duas rotas:
- exigem usuário autenticado (`CurrentUser`);
- respondem com `Cache-Control: no-store`;
- não acessam o banco nem leem estudos.

---

## `GET /api/imports/organize/status`

**200**
```json
{ "available": true, "reason": null, "version": "1" }
```
```json
{ "available": false, "reason": "integrity_failed", "version": null }
```

`reason` ∈ `null`, `not_installed`, `integrity_failed`. Nunca contém caminhos.

## `POST /api/imports/organize`

Sugere a distribuição do texto entre as 4 seções. **Não grava nada.** Para salvar, o cliente usa
`POST /api/studies`.

**Requisição**:

```json
{
  "text": "O capítulo trata de um tema de teste.\nTermo de teste: definição fictícia.\nSOBRENOME, Nome. Livro de Teste. Cidade: Editora, 2020.",
  "lines": [
    { "text": "O capítulo trata de um tema de teste.", "bbox": [120, 140, 1480, 200], "confidence": 0.91 }
  ]
}
```

| Campo | Regra |
| :--- | :--- |
| `text` | obrigatório; não pode ser só espaços (`422`); até 50 000 caracteres (`413`) |
| `lines` | opcional; até 2 000 itens; cada um com `text` obrigatório, `bbox` com 4 números ou `null`, e `confidence` entre 0 e 1 ou `null` |

**200**:

```json
{
  "sections": {
    "summary": "O capítulo trata de um tema de teste.",
    "explanation": "",
    "concepts": "Termo de teste: definição fictícia.",
    "references": "SOBRENOME, Nome. Livro de Teste. Cidade: Editora, 2020."
  },
  "segments": [
    { "index": 0, "start": 0, "end": 37, "text": "O capítulo trata de um tema de teste.", "section": "summary", "confidence": 0.81, "review": false },
    { "index": 1, "start": 38, "end": 73, "text": "Termo de teste: definição fictícia.", "section": "concepts", "confidence": 0.94, "review": false },
    { "index": 2, "start": 74, "end": 129, "text": "SOBRENOME, Nome. Livro de Teste. Cidade: Editora, 2020.", "section": "references", "confidence": 0.99, "review": false }
  ],
  "explicit_headings": false,
  "review_count": 0,
  "engine": { "name": "leitorum-organizer", "version": "1", "sha256": "60d6538d…" },
  "elapsed_ms": 4,
  "warnings": [{ "code": "suggestion", "message": "Distribuição automática: confira as seções antes de salvar." }]
}
```

**Garantias**:
- **Posições e texto:** `start` e `end` são posições no `text` recebido, em pontos de código (Python). Cada
  trecho traz também o próprio `text`, igual a `text[start:end]`, e **o cliente usa esse campo**. Ele nunca
  recorta por posição, porque o JavaScript conta em unidades UTF-16 e as posições divergiriam com caracteres fora
  do plano básico.
- **Seções:** `sections[s]` é a junção por `\n` dos `text[start:end]` dos trechos de `s`, na ordem.
- **Cobertura:** todo caractere não branco de `text` está em exatamente um trecho.

**Avisos**:

| `code` | Quando |
| :--- | :--- |
| `suggestion` | sempre |
| `single_section` | todos os trechos ficaram numa só seção |

**Erros**: o corpo é `{"detail": "<português>", "code": "<código>"}`.

| Status | `code` | Quando |
| :--- | :--- | :--- |
| 401 | — | sem sessão |
| 413 | `too_large` | texto > 50 000 caracteres ou > 400 trechos |
| 422 | `empty_text` / validação | texto vazio ou campo inválido |
| 503 | `unavailable` | artefato ausente ou com integridade falha |

## Mudança aditiva no contrato da 086

`POST /api/digitize/preview` → cada item de `lines` ganha `bbox: [x0, y0, x1, y1] | null`, em pixels da imagem
recebida. Os outros campos não mudam.
