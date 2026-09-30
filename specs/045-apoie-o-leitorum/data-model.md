# Data Model: F0.6.6 — Apoie o Leitorum

**Feature Branch**: `045-apoie-o-leitorum`  
**Date**: 2026-09-29  
**Status**: Ready  

---

## 1. Relational Entities (SQLAlchemy 2.0 / SQLite)

### Tabela `support_settings`

Armazena os parâmetros configurados pelo administrador para exibição na página de apoio. Opera como padrão singleton (registro único de configuração geral do sistema).

```sql
CREATE TABLE support_settings (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    pix_enabled BOOLEAN NOT NULL DEFAULT 0,
    pix_key VARCHAR(255) NULL,
    pix_recipient_name VARCHAR(255) NULL,
    pix_qr_code_url TEXT NULL,
    alternative_enabled BOOLEAN NOT NULL DEFAULT 0,
    alternative_label VARCHAR(100) NULL,
    alternative_url TEXT NULL,
    custom_message TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by_user_id VARCHAR(36) NULL REFERENCES users(id) ON DELETE SET NULL
);
```

#### Campos e Tipagem:

| Coluna | Tipo | Nulo | Padrão | Descrição |
|---|---|---|---|---|
| `id` | `INTEGER` | Não | `1` | Chave primária singleton (garante apenas 1 linha de configuração global) |
| `pix_enabled` | `BOOLEAN` | Não | `False` | Indica se o método de contribuição PIX está ativo |
| `pix_key` | `VARCHAR(255)` | Sim | `NULL` | Chave PIX (e-mail, chave aleatória, telefone ou CPF/CNPJ) |
| `pix_recipient_name`| `VARCHAR(255)` | Sim | `NULL` | Nome do titular/beneficiário cadastrado na instituição financeira |
| `pix_qr_code_url` | `TEXT` | Sim | `NULL` | URL estática, caminho de imagem ou payload base64 do QR Code |
| `alternative_enabled`| `BOOLEAN` | Não | `False` | Indica se o meio alternativo (Google Pay/link externo) está ativo |
| `alternative_label` | `VARCHAR(100)` | Sim | `NULL` | Rótulo do botão de apoio alternativo (ex.: "Google Pay") |
| `alternative_url` | `TEXT` | Sim | `NULL` | URL completa e válida para redirecionamento externo |
| `custom_message` | `TEXT` | Sim | `NULL` | Texto opcional complementar institucional redigido pelo administrador |
| `created_at` | `DATETIME` | Não | `now()` | Carimbo de data/hora de criação do registro |
| `updated_at` | `DATETIME` | Não | `now()` | Carimbo de data/hora da última alteração |
| `updated_by_user_id`| `VARCHAR(36)` | Sim | `NULL` | Identificador UUID do administrador que realizou a última modificação |

---

## 2. Pydantic Schemas

### `SupportPublicResponse`
Esquema serializado retornado pelo endpoint público `GET /api/support`:

```python
class SupportPublicResponse(BaseModel):
    pix_enabled: bool
    pix_key: str | None = None
    pix_recipient_name: str | None = None
    pix_qr_code_url: str | None = None
    alternative_enabled: bool
    alternative_label: str | None = None
    alternative_url: str | None = None
    custom_message: str | None = None
    has_any_method_active: bool
```

### `SupportAdminResponse`
Esquema completo retornado para o painel de administração em `GET /api/admin/support`:

```python
class SupportAdminResponse(SupportPublicResponse):
    source: str  # "database" | "environment" | "default"
    updated_at: datetime | None = None
    updated_by_user_id: str | None = None
    updated_by_name: str | None = None
```

### `SupportConfigUpdate`
Esquema de validação para payload enviado pelo administrador em `PUT /api/admin/support`:

```python
class SupportConfigUpdate(BaseModel):
    pix_enabled: bool
    pix_key: str | None = Field(default=None, max_length=255)
    pix_recipient_name: str | None = Field(default=None, max_length=255)
    pix_qr_code_url: str | None = None
    alternative_enabled: bool
    alternative_label: str | None = Field(default=None, max_length=100)
    alternative_url: str | None = None
    custom_message: str | None = Field(default=None, max_length=1000)
```

---

## 3. Fallback Hierarchy (Regras de Resolução)

Quando uma requisição consulta as configurações de apoio:

```text
1. Verifica se existe registro persistido na tabela support_settings.
   ├── Se existir: utiliza os valores gravados no banco de dados.
   └── Se não existir:
       ├── Consulta as variáveis de ambiente:
       │   ├── SUPPORT_PIX_ENABLED
       │   ├── SUPPORT_PIX_KEY
       │   ├── SUPPORT_PIX_RECIPIENT
       │   ├── SUPPORT_PIX_QR_CODE_URL
       │   ├── SUPPORT_ALTERNATIVE_ENABLED
       │   ├── SUPPORT_ALTERNATIVE_LABEL
       │   └── SUPPORT_ALTERNATIVE_URL
       └── Se não houver variáveis definidas:
           Retorna valores padrão seguros (todos os meios inativos, has_any_method_active = False).
```

---

## 4. Auditoria de Segurança

Toda alteração de configuração realizada via endpoint `PUT /api/admin/support` registrará uma entrada na tabela `audit_logs` existente com:
- `user_id`: ID do administrador autenticado;
- `action`: `"admin.support_settings_updated"`;
- `resource_type`: `"support_settings"`;
- `details`: Resumo das alterações de estado (ex.: `{"pix_enabled": true, "alternative_enabled": false}`).
