# Contrato de Serviço: Backup, Snapshot e Manutenção

**Módulo**: `app.services.maintenance` / `app.services.backups`  
**Consumidores**: `migrations/env.py`, `iniciar.py`, ferramentas CLI de manutenção e testes unitários.

---

## 1. Funções de Configuração e Localização

### `get_database_path() -> Path`
- **Descrição**: Retorna o caminho absoluto canônico do banco de dados ativo.
- **Entrada**: Nenhuma (lê `os.environ.get("CADERNO_DATABASE_PATH")`).
- **Saída**: Objeto `pathlib.Path` absoluto e resolvido.
- **Exceções**: `ValueError` se `CADERNO_DATABASE_PATH` for definido como caminho relativo.

### `get_backup_dir() -> Path`
- **Descrição**: Retorna o diretório dedicado a snapshots e backups (`<db_dir>/backups`). Cria o diretório se não existir.
- **Saída**: Objeto `pathlib.Path` absoluto.

---

## 2. Funções de Ciclo de Vida do Snapshot

### `create_pre_upgrade_snapshot(database_path: Path | None = None) -> Path | None`
- **Descrição**: Cria um snapshot consistente do banco informado (ou do banco ativo se omitido) antes de uma migração.
- **Comportamento**:
  - Se a base não existir ou tiver tamanho 0, retorna `None` (não há dados a preservar em base virgem).
  - Gera o arquivo com nome padronizado: `caderno-pre-migracao-YYYYMMDD-HHMMSS.db` no diretório de backups.
  - Utiliza SQLite Online Backup API com cópia atômica.
  - Altera `PRAGMA journal_mode=DELETE` na cópia gerada.
  - Valida a cópia com `PRAGMA quick_check` e `PRAGMA foreign_key_check`.
  - Dispara a rotação automática dos 5 snapshots mais recentes (`rotate_pre_upgrade_snapshots`).
  - Retorna o caminho do snapshot gerado.
- **Exceções**:
  - `TimeoutError`: Se o banco ativo permanecer bloqueado por mais de 30 segundos.
  - `sqlite3.DatabaseError`: Se a cópia falhar na verificação de integridade ou chaves estrangeiras.
  - `RuntimeError`: Em caso de erro de permissão ou espaço em disco.

### `rotate_pre_upgrade_snapshots(backup_dir: Path, keep: int = 5) -> list[Path]`
- **Descrição**: Aplica a política de retenção aos snapshots automáticos pré-migração.
- **Comportamento**:
  - Localiza apenas arquivos correspondentes ao padrão `caderno-pre-migracao-*.db`.
  - Ordena os arquivos por timestamp decrescente (mais recentes primeiro).
  - Remove com segurança os arquivos que excederem o limite `keep`.
  - Retorna a lista de arquivos removidos.
  - **Inviolabilidade**: Backups sob demanda (`caderno-*.db`) ou arquivos manuais nunca são tocados.

### `inspect_snapshot(snapshot_path: Path) -> dict`
- **Descrição**: Inspeciona a integridade e quantitativos de um snapshot sem ler ou exibir o conteúdo confidencial das anotações.
- **Saída**: Dicionário serializável com o formato:
  ```json
  {
    "snapshot_path": "C:\\...\\caderno-pre-migracao-20260917-210000.db",
    "created_at": "2026-09-17T21:00:00Z",
    "file_size_bytes": 32768,
    "schema_revision": "0001_initial",
    "integrity_ok": true,
    "counts": {
      "books": 3,
      "chapters": 12,
      "studies": 45
    }
  }
  ```
- **Exceções**: `FileNotFoundError`, `sqlite3.DatabaseError` se o arquivo estiver corrompido.
