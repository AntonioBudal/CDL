# Data Model & Schemas: Infraestrutura e Backup/Restauração (T09-T10)

**Feature**: `016-infra-backup-operacao`  
**Date**: 2026-09-19  
**Status**: Completed  

---

## 1. Estrutura do Pacote de Backup (.zip)

O pacote de backup universal gerado possui a seguinte organização interna:

```text
caderno-backup-20260919-143000.zip
├── manifest.json              # Metadados de integridade e tabela de hashes SHA-256
├── caderno.db                 # Base de dados SQLite (journal_mode=DELETE, consistente)
└── covers/                    # Diretório com arquivos de imagem das capas cadastradas
    ├── capa-livro-1.jpg
    └── capa-livro-2.png
```

---

## 2. Entidade: `BackupManifest`

Estrutura JSON armazenada em `manifest.json` e serializada pelo Pydantic:

### Campos

| Campo | Tipo | Obrigatório | Descrição |
| :--- | :--- | :--- | :--- |
| `app_version` | `string` | Sim | Versão da aplicação no momento da geração (ex.: `"0.3.0"`). |
| `schema_version` | `string` ou `null` | Não | Identificador da revisão Alembic do banco (ex.: `"0005_trash_and_covers"`). |
| `created_at` | `string` (ISO 8601 UTC) | Sim | Timestamp exato de criação (ex.: `"2026-09-19T14:30:00Z"`). |
| `generator` | `string` | Sim | Identificador do motor de backup (ex.: `"Caderno de Leitura Backup Engine"`). |
| `counts` | `object` | Sim | Contagens agregadas de itens no banco e no pacote (livros, capítulos, estudos, capas). |
| `files` | `map[string, string]` | Sim | Mapa de caminho relativo do arquivo no ZIP para seu hash SHA-256 (64 caracteres hexadecimais em minúsculo). |

### Exemplo JSON
```json
{
  "app_version": "0.3.0",
  "schema_version": "0005_trash_and_covers",
  "created_at": "2026-09-19T14:30:00Z",
  "generator": "Caderno de Leitura Backup Engine",
  "counts": {
    "books": 12,
    "chapters": 45,
    "studies": 150,
    "covers": 2
  },
  "files": {
    "caderno.db": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "covers/capa-livro-1.jpg": "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e",
    "covers/capa-livro-2.png": "b8a5d7c92ef61b12480ad9163274b591823d6a45fc9e1a83701bf4e8590c2134"
  }
}
```

---

## 3. Entidade: `RestoreResult`

Resposta retornada pelo endpoint de restauração `POST /api/backup/restore` e pela CLI:

### Campos

| Campo | Tipo | Obrigatório | Descrição |
| :--- | :--- | :--- | :--- |
| `success` | `boolean` | Sim | `true` se o acervo foi validado e restaurado com sucesso. |
| `message` | `string` | Sim | Mensagem descritiva em português para exibição na interface. |
| `backup_created_at` | `string` ou `null` | Não | Data/hora do backup restaurado (extraída do manifesto ou do arquivo). |
| `pre_restore_snapshot` | `string` | Sim | Nome do arquivo de snapshot de salvaguarda gerado antes da troca. |
| `schema_revision` | `string` ou `null` | Não | Revisão do banco restaurado. |
| `counts` | `object` | Sim | Contagens agregadas do acervo restaurado (`books`, `chapters`, `studies`). |
| `covers_restored` | `integer` | Sim | Quantidade de arquivos de imagem de capa restaurados. |

### Exemplo JSON
```json
{
  "success": true,
  "message": "Acervo restaurado com sucesso! O sistema foi atualizado.",
  "backup_created_at": "2026-09-19T14:30:00Z",
  "pre_restore_snapshot": "caderno-pre-restauracao-20260919-150210.db",
  "schema_revision": "0005_trash_and_covers",
  "counts": {
    "books": 12,
    "chapters": 45,
    "studies": 150
  },
  "covers_restored": 2
}
```

---

## 4. Schemas Pydantic (`app/schemas/backups.py`)

```python
from pydantic import BaseModel, Field


class BackupCounts(BaseModel):
    books: int = 0
    chapters: int = 0
    studies: int = 0
    covers: int = 0


class BackupManifestSchema(BaseModel):
    app_version: str
    schema_version: str | None = None
    created_at: str
    generator: str = "Caderno de Leitura Backup Engine"
    counts: BackupCounts
    files: dict[str, str]


class RestoreResultResponse(BaseModel):
    success: bool = True
    message: str
    backup_created_at: str | None = None
    pre_restore_snapshot: str
    schema_revision: str | None = None
    counts: dict[str, int]
    covers_restored: int = 0


class SnapshotInspectionResponse(BaseModel):
    snapshot_path: str
    created_at: str
    file_size_bytes: int
    schema_revision: str | None = None
    integrity_ok: bool
    counts: dict[str, int]
```

---

## 5. DTOs de Concorrência Otimista (Frontend e Composable)

```typescript
export interface ConcurrencyConflictState {
  hasConflict: boolean
  message: string
  clientUpdatedAt: string | null
  serverUpdatedAt?: string | null
}

export type ConcurrencyResolutionAction = 'overwrite' | 'reload'
```
