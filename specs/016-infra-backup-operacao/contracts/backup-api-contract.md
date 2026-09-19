# API Contract: Operações de Backup e Restauração

**Feature**: `016-infra-backup-operacao`  
**Base URL**: `/api`  
**Tags**: `Backup`  

---

## 1. Download do Pacote Completo de Backup

Gera e transmite um pacote ZIP contendo a base SQLite consistente (`caderno.db`), pasta de capas (`covers/`) e manifesto de autenticidade criptográfica (`manifest.json`) com somas SHA-256.

- **Endpoint**: `GET /api/backup/bundle`
- **Headers**:
  - `Accept`: `application/zip` ou `application/octet-stream`
- **Query Parameters**: Nenhum

### Respostas

#### `200 OK`
- **Content-Type**: `application/zip`
- **Headers**:
  - `Content-Disposition`: `attachment; filename="caderno-backup-YYYYMMDD-HHMMSS.zip"`
  - `Cache-Control`: `no-store`
  - `X-Content-Type-Options`: `nosniff`
- **Body**: Stream binário do arquivo ZIP compactado.

#### `503 Service Unavailable`
- **Condição**: O banco de dados SQLite está temporariamente bloqueado ou ocupado por transação longa.
- **Body**:
  ```json
  {
    "detail": "O banco está ocupado. Aguarde alguns segundos e tente novamente."
  }
  ```

---

## 2. Download do Banco Isolado (Legado / Retrocompatibilidade)

Mantido para retrocompatibilidade com rotinas automatizadas e scripts que consomem diretamente o `.db`.

- **Endpoint**: `GET /api/backup`
- **Headers**:
  - `Accept`: `application/octet-stream`
- **Respostas**:
  - `200 OK`: Arquivo `caderno-YYYYMMDD-HHMMSS.db`
  - `503 Service Unavailable`: Banco ocupado

---

## 3. Restauração de Pacote de Backup

Recebe um arquivo compactado `.zip` (ou alternativamente um `.db` isolado), extrai em sandbox transitória, valida os hashes SHA-256, executa `PRAGMA quick_check` e `PRAGMA foreign_key_check`, gera um snapshot de salvaguarda do acervo ativo e substitui atomicamente o banco e as capas.

- **Endpoint**: `POST /api/backup/restore`
- **Content-Type**: `multipart/form-data`
- **Form Body**:
  - `file`: Arquivo binário enviado (`.zip` ou `.db`).

### Respostas

#### `200 OK`
- **Content-Type**: `application/json`
- **Body**:
  ```json
  {
    "success": true,
    "message": "Acervo restaurado com sucesso! A base e as capas foram atualizadas.",
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

#### `400 Bad Request`
- **Condição**: Arquivo corrompido, formato inválido, tentativa de Zip Slip, ou falha de integridade criptográfica/física.
- **Body**:
  ```json
  {
    "detail": "O arquivo enviado falhou na verificação de integridade: soma SHA-256 divergente em 'caderno.db'."
  }
  ```

#### `422 Unprocessable Entity`
- **Condição**: Nenhum arquivo enviado ou arquivo com tamanho zero.
- **Body**:
  ```json
  {
    "detail": "O arquivo de backup está vazio ou inválido."
  }
  ```

#### `500 Internal Server Error`
- **Condição**: Erro inesperado durante a substituição física. O sistema aciona o rollback imediato para o snapshot prévio.
- **Body**:
  ```json
  {
    "detail": "Falha na substituição dos dados. O acervo anterior foi restaurado automaticamente via rollback seguro."
  }
  ```

---

## 4. Concorrência Otimista (HTTP 409)

Ao atualizar um livro, capítulo ou estudo via `PATCH`:

- **Endpoint**: `PATCH /api/studies/{study_id}` (e `/api/books/{id}`, `/api/chapters/{id}`)
- **Body**:
  ```json
  {
    "title": "Novo título editado",
    "notes": "Anotação revisada",
    "expected_updated_at": "2026-09-19T10:00:00Z"
  }
  ```

### Resposta de Conflito Concorrente

#### `409 Conflict`
- **Condição**: `current_updated_at > expected_updated_at + 1s`
- **Body**:
  ```json
  {
    "detail": "Conflito de concorrência: este estudo foi modificado em outro dispositivo. Seus dados foram preservados no formulário."
  }
  ```
