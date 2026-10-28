# Contrato: API de Mídia, Espaço e Cotas

**Feature**: `090-armazenamento-hd-cofre-cotas` (fatias B e C) | Router: `backend/app/routers/media.py` | Prefixo:
`/api/media`

**Regras gerais**:
- todas as rotas exigem sessão (`CurrentUser`);
- mídia que o usuário não pode ver responde **`404`**, nunca `403`;
- nenhuma rota registra em log nomes, títulos ou bytes de imagem.

---

## `GET /api/media/usage`

```json
{
  "user": { "used_bytes": 52428800, "quota_bytes": 1073741824, "count": 131, "percent": 4.9, "level": "normal" },
  "server": { "level": "normal" },
  "vault": { "state": "ready" }
}
```

**Só para o administrador** (decisão C-Q4), `server` traz também `used_bytes`, `quota_bytes`, `disk_free_bytes`,
`margin_bytes` e `percent`. Os demais usuários veem só o nível, para não deduzirem o uso dos outros.

| Campo | Valores |
| :--- | :--- |
| `level` | `normal` (< 85 %), `high` (85–99 %), `full` (≥ 100 % ou sem espaço livre real) |
| `vault.state` | `ready`, `key_missing`, `key_mismatch`, `storage_unavailable` |

## `GET /api/media`

Lista as mídias **do próprio usuário**.

**Query**:

| Parâmetro | Valores |
| :--- | :--- |
| `kind` | `notebook_page` \| `avatar` \| `cover` (opcional) |
| `book_id` | opcional |
| `sort` | `created_desc` (padrão) \| `size_desc` \| `expires_asc` |
| `offset` | paginação (como entregue na fatia B; a resposta traz `next_offset`) |
| `limit` | ≤ 100 (padrão 50) |

`expires_at` e `days_left` são a validade **efetiva**: a menor entre a idade (30 dias) e o fim da espera depois de
o estudo ser visto concluído (7 dias). Capas, avatares e fotos mantidas têm os dois nulos.

```json
{
  "items": [
    {
      "id": "6f1c…", "kind": "notebook_page", "status": "active",
      "study": { "id": 31, "title": "Página digitalizada de teste", "reading_status": "revisado", "in_trash": false },
      "book": { "id": 2, "title": "Livro de Teste", "in_trash": false },
      "created_at": "2026-10-27T12:00:00Z", "expires_at": "2026-11-26T12:00:00Z", "days_left": 30,
      "keep_forever": false, "byte_size": 356000, "width": 1500, "height": 2000
    }
  ],
  "next_offset": null
}
```

## `GET /api/media/{id}/content` e `GET /api/media/{id}/thumbnail`

- **Resposta `200`:** bytes `image/webp`, decifrados em memória. A miniatura tem até 320 px.
- **Cabeçalhos:**
  - `Cache-Control: private, no-store, no-cache, max-age=0`;
  - `Pragma: no-cache`;
  - `X-Content-Type-Options: nosniff`;
  - `Content-Disposition: inline`.
- **Acesso por tipo:**
  - `notebook_page`: só o dono;
  - `avatar`: segue a visibilidade do perfil;
  - `cover`: o dono do livro e quem recebeu o livro por compartilhamento.
- **Erros:**

  | Status | `code` | Quando |
  | :--- | :--- | :--- |
  | 404 | — | sem permissão ou mídia inexistente |
  | 409 | `missing` | o arquivo sumiu do cofre |
  | 422 | `integrity_failed` | tag GCM inválida (arquivo adulterado ou corrompido) |
  | 503 | `vault_locked` | chave ausente ou errada |

## `PATCH /api/media/{id}`

Corpo: `{"keep_forever": true}`. Só para `notebook_page` do dono (`404` para os demais). Com `true`, limpa
`expires_at` e a marca de conclusão; com `false`, recalcula `expires_at = agora + retenção`. Responde `200` com o
item.

## `DELETE /api/media/{id}`

Apaga uma mídia do dono, em duas fases. Responde `200` com `{ "freed_bytes": 356000 }`.

**Garantia:** nenhuma coluna de `studies` é tocada.

## `POST /api/media/bulk-delete`

| Corpo | Efeito |
| :--- | :--- |
| `{"filter": "completed_studies", "dry_run": true}` | conta as fotos de estudos com `reading_status = 'concluido'` |
| `{"filter": "older_than_days", "days": 30, "dry_run": true}` | conta as fotos com mais de N dias (1–3650) |
| `{"ids": ["…", "…"], "dry_run": false}` | apaga os itens escolhidos (≤ 500) |

- **Escopo:** só `notebook_page` do próprio usuário; fotos com `keep_forever` ficam fora dos filtros (não da lista
  de `ids`).
- **`completed_studies`:** apaga na hora, sem a espera de 7 dias do job (decisão C-Q3).
- **Validação:** um filtro **ou** `ids`, nunca os dois; `older_than_days` exige `days`; `dry_run` vale `true` se
  omitido. Fora disso, `422`.
- **Resposta:** `{ "matched": 12, "freed_bytes": 4200000, "deleted": 12 }`, com `deleted = 0` em `dry_run`.

## `POST /api/studies/{id}/media` (fatia C; substitui o `attach` previsto)

Multipart `file` (JPEG, PNG ou WebP, até 20 MB e 40 MP). Guarda a foto da página com o estudo, para conferência.
É chamada pelo navegador **depois** de salvar o estudo, só com a caixa marcada (decisão C-Q1).
- só o dono, com o estudo fora da lixeira; senão, `404`;
- a foto é reduzida a até 2000 px em WebP, sem metadados, e cifrada;
- `expires_at = agora + retenção`;
- **resposta `201`:** `{ "item": { …item… }, "usage": { …como em /usage… } }`;
- **erros:** `413`, `415` e `422` (arquivo), `503 vault_locked` e `507` (cota). Uma falha aqui nunca altera o
  estudo.

## `GET /api/studies/{id}/media` (fatia C)

Lista as páginas `active` e `missing` vinculadas ao estudo, no mesmo formato de item. Só para o dono do estudo.

## Mudanças em rotas existentes

| Rota | Mudança |
| :--- | :--- |
| `POST /api/digitize/preview` | **sem mudança** (decisão C-Q1): lê e apaga a foto, como na 086. Guardar a foto é um envio separado, ao salvar |
| `POST /api/profile/avatar` e upload/URL de capa | gravam no cofre; `avatar_url` passa a `/api/avatars/<media_id>` e `cover_image` passa a `<media_id>`, ou seja, as **mesmas rotas de hoje**, e o frontend não muda |
| `GET /api/avatars/{nome}` e `GET /api/covers/{nome}` | passam a **exigir sessão**. Se `nome` é um `media_id`, decifram do cofre; se é um arquivo legado, servem enquanto ele existir. As duas usam a regra de acesso do tipo e devolvem `404` sem permissão |

**Erros de cota** (qualquer gravação: página, capa por arquivo ou link, avatar): `507` com `code` `user_quota` ou
`server_quota`, mais `detail` em português e `usage` (o mesmo objeto de `/usage`, na visão de usuário comum).
