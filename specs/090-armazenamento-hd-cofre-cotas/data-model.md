# Data Model: Armazenamento no HD, Cofre de Imagens e Cotas

**Feature**: `090-armazenamento-hd-cofre-cotas` | **Plan**: [plan.md](plan.md)

Duas tabelas novas, em migrações Alembic de fatias diferentes. Cada migração só roda depois do snapshot
pré-migração verificado (`AGENTS.md` §2, Constituição V.1). Nenhuma coluna das tabelas existentes muda de tipo.

---

## 1. `storage_settings` (fatia 090-A; uma linha)

| Coluna | Tipo | Regra |
| :--- | :--- | :--- |
| `id` | INTEGER PK | sempre `1` (`CHECK (id = 1)`) |
| `storage_id` | TEXT(36) NOT NULL | UUID do marcador `.leitorum-storage.json` da raiz |
| `media_key_fingerprint` | TEXT(16) NULL | impressão digital da chave mestra (fatia B); nunca a chave |
| `media_key_epoch` | INTEGER NOT NULL DEFAULT 0 | época atual da chave |
| `created_at` / `updated_at` | DATETIME | UTC |

**Na partida:** se `LEITORUM_STORAGE_ROOT` estiver definido, os três `storage_id` precisam bater: o do marcador,
o desta tabela e o do banco aberto. Se não baterem, o app não inicia (research R1).

## 2. `encrypted_media` (fatia 090-B)

| Coluna | Tipo | Regra |
| :--- | :--- | :--- |
| `id` | TEXT(36) PK | UUID v4; também é o nome do arquivo `vault/<aa>/<id>.enc` e o `media_id` do cabeçalho |
| `user_id` | TEXT(36) NOT NULL FK `users.id` | dono e cota; `ON DELETE RESTRICT` (a exclusão de conta apaga as mídias antes) |
| `kind` | TEXT(20) NOT NULL | `notebook_page` \| `avatar` \| `cover` (`CHECK`) |
| `status` | TEXT(12) NOT NULL | `pending` \| `active` \| `deleting` \| `missing` (`CHECK`) |
| `study_id` | INTEGER NULL FK `studies.id` | `ON DELETE SET NULL`; **apagar a mídia nunca toca no estudo** |
| `book_id` | INTEGER NULL FK `books.id` | `ON DELETE SET NULL`; capas e páginas (para listar por livro) |
| `byte_size` | INTEGER NOT NULL | tamanho do `.enc` em disco; é o que conta na cota |
| `plain_size` | INTEGER NOT NULL | tamanho do WebP antes de cifrar (informativo) |
| `width` / `height` | INTEGER NOT NULL | dimensões depois da otimização |
| `content_type` | TEXT(32) NOT NULL | `image/webp` |
| `format_version` | INTEGER NOT NULL | `1` |
| `key_epoch` | INTEGER NOT NULL | época da chave usada |
| `sha256` | TEXT(64) NOT NULL | do arquivo `.enc` inteiro (backup e migração sem chave) |
| `keep_forever` | BOOLEAN NOT NULL DEFAULT 0 | "Manter permanentemente" (só `notebook_page`) |
| `expires_at` | DATETIME NULL | `created_at + retenção` para páginas; `NULL` para avatar e capa |
| `pending_until` | DATETIME NULL | validade do vínculo pendente (24 h) |
| `created_at` / `updated_at` | DATETIME NOT NULL | UTC |

**Índices**:
- `(user_id, status)`, para a cota do usuário e a lista;
- `(status, expires_at)`, para o job;
- `(study_id)`;
- `(kind, user_id)`.

**Restrições**:
- `CHECK (kind = 'notebook_page' OR keep_forever = 0)`;
- `CHECK (kind <> 'notebook_page' OR expires_at IS NOT NULL OR keep_forever = 1)`.

**Referências existentes** (sem mudança de tipo):
- `user_profiles.avatar_url` passa a guardar `/api/media/<id>/content`;
- `books.cover_image` passa a guardar `media:<id>`.

As rotas antigas `/api/avatars/{arquivo}` e `/api/covers/{arquivo}` resolvem os valores antigos durante a
transição (research R5 e R10).

## 3. Estados e transições de uma mídia

```text
(upload) ──reserva de cota──▶ pending ──arquivo gravado + vínculo──▶ active ──apagar / expirar──▶ deleting ──arquivo removido──▶ (linha apagada)
             │                   │ 24 h sem vínculo (páginas)                     ▲
             │                   └──────────────────────────────────▶ deleting ─┘
             └─ falha na gravação ─▶ (linha removida)
active ──arquivo sumiu (reconciliação)──▶ missing ──usuário apaga──▶ (linha apagada)
```

## 4. Uso de espaço (calculado, sem tabela)

| Valor | Cálculo |
| :--- | :--- |
| `user.used_bytes` | `SUM(byte_size)` de `encrypted_media` do usuário com `status IN ('pending','active','deleting')` |
| `user.count` | quantidade de mídias `active` do usuário |
| `server.used_bytes` | a mesma soma, para todos os usuários |
| `server.disk_free_bytes` | `shutil.disk_usage(raiz).free` |
| `can_write(n)` | `user.used + n ≤ cota_usuário` **e** `server.used + n ≤ cota_global` **e** `disk_free - n ≥ margem` |

## 5. Configuração (`.env` do sistema principal)

| Variável | Padrão | Fatia |
| :--- | :--- | :--- |
| `LEITORUM_STORAGE_ROOT` | — (sem ela, vale o comportamento atual) | A |
| `LEITORUM_SECONDARY_BACKUP_DIR` | — | A |
| `LEITORUM_MEDIA_MASTER_KEY` | — (preferência: arquivo protegido por DPAPI) | B |
| `LEITORUM_MEDIA_KEY_FILE` | `%LOCALAPPDATA%\Leitorum\media-master.key` | B |
| `LEITORUM_USER_STORAGE_QUOTA_BYTES` | `1073741824` | C |
| `LEITORUM_GLOBAL_STORAGE_QUOTA_BYTES` | `966367641600` | C |
| `LEITORUM_STORAGE_FREE_MARGIN_BYTES` | `2147483648` | C |
| `LEITORUM_MEDIA_RETENTION_DAYS` | `30` | C |
| `LEITORUM_MEDIA_DELETE_ON_COMPLETED` | `true` | C |
| `LEITORUM_MEDIA_COMPLETED_GRACE_DAYS` | `7` | C |
| `LEITORUM_MEDIA_JOB_INTERVAL_HOURS` | `6` | C |

**Precedência**: `CADERNO_DATABASE_PATH`, `CADERNO_COVERS_DIR` e `CADERNO_AVATARS_DIR` explícitos vencem
`LEITORUM_STORAGE_ROOT`.
