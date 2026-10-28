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
  "server": { "used_bytes": 21474836480, "quota_bytes": 966367641600, "disk_free_bytes": 820000000000, "percent": 2.2, "level": "normal" },
  "vault": { "state": "ready" }
}
```

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
| `cursor` | paginação |
| `limit` | ≤ 100 |

```json
{
  "items": [
    {
      "id": "6f1c…", "kind": "notebook_page", "status": "active",
      "study": { "id": 31, "title": "Página digitalizada de teste", "reading_status": "revisado" },
      "book": { "id": 2, "title": "Livro de Teste" },
      "created_at": "2026-10-27T12:00:00Z", "expires_at": "2026-11-26T12:00:00Z", "days_left": 30,
      "keep_forever": false, "byte_size": 356000, "width": 1500, "height": 2000
    }
  ],
  "next_cursor": null
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

Corpo: `{"keep_forever": true}`. Só para `notebook_page` do dono. Com `true`, limpa `expires_at`; com `false`,
recalcula `expires_at = agora + retenção`. Responde `200` com o item.

## `DELETE /api/media/{id}`

Apaga uma mídia do dono, em duas fases. Responde `200` com `{ "freed_bytes": 356000 }`.

**Garantia:** nenhuma coluna de `studies` é tocada.

## `POST /api/media/bulk-delete`

| Corpo | Efeito |
| :--- | :--- |
| `{"filter": "completed_studies", "dry_run": true}` | conta as fotos de estudos com `reading_status = 'concluido'` |
| `{"filter": "older_than_days", "days": 30, "dry_run": true}` | conta as fotos com mais de N dias (1–3650) |
| `{"ids": ["…", "…"], "dry_run": false}` | apaga os itens escolhidos (≤ 500) |

- **Escopo:** só `notebook_page` do próprio usuário; fotos com `keep_forever` ficam fora dos filtros.
- **Resposta:** `{ "matched": 12, "freed_bytes": 4200000, "deleted": 12 }`, com `deleted = 0` em `dry_run`.

## `POST /api/media/{id}/attach` (fatia C)

Corpo: `{"study_id": 31}`. Vincula uma página `pending` do próprio usuário a um estudo do próprio usuário.
- muda o estado de `pending` para `active`;
- define `expires_at` e `book_id`.

**Erros:**

| Status | Quando |
| :--- | :--- |
| 404 | mídia ou estudo de outro dono |
| 409 | a mídia não está `pending` |

## `GET /api/studies/{id}/media` (fatia C)

Lista as páginas vinculadas ao estudo, no mesmo formato de item. Só para o dono do estudo.

## Mudanças em rotas existentes

| Rota | Mudança |
| :--- | :--- |
| `POST /api/digitize/preview` | campo de formulário opcional `keep_photo=true`; a resposta ganha `stored_media: {id, byte_size, pending_until} \| null` e `storage_warning` (cota cheia, chave ausente). Sem `keep_photo`, tudo segue como na 086 |
| `POST /api/profile/avatar` e upload/URL de capa | gravam no cofre; `avatar_url` passa a `/api/avatars/<media_id>` e `cover_image` passa a `<media_id>`, ou seja, as **mesmas rotas de hoje**, e o frontend não muda |
| `GET /api/avatars/{nome}` e `GET /api/covers/{nome}` | passam a **exigir sessão**. Se `nome` é um `media_id`, decifram do cofre; se é um arquivo legado, servem enquanto ele existir. As duas usam a regra de acesso do tipo e devolvem `404` sem permissão |

**Erros de cota** (qualquer gravação): `507` com `code` `user_quota` ou `server_quota`, mais `detail` em
português e `usage` (o mesmo objeto de `/usage`).
