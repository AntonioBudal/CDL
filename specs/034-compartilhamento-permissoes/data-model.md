# Data Model: F07 — Compartilhamento e Permissões por Recurso (ACL)

Este documento especifica o modelo de dados relacional, migrações e entidades necessárias para implementar o controle de visibilidade e compartilhamento granular de recursos no Caderno de Leitura.

---

## 1. Entidades e Esquema Relacional

```
┌─────────────────────────┐               ┌──────────────────────────────┐
│          books          │               │           studies            │
├─────────────────────────┤               ├──────────────────────────────┤
│ id: Integer (PK)        │ 1           N │ id: Integer (PK)             │
│ user_id: String(36)(FK) │──────────────▶│ book_id: Integer (FK)        │
│ title: String           │               │ user_id: String(36)(FK)      │
│ visibility: String(20)  │               │ visibility: String(20)       │
└─────────────────────────┘               └──────────────────────────────┘
             │                                           │
             │                                           │
             │ 1                                         │ 1
             ▼                                           ▼
┌────────────────────────────────────────────────────────────────────────┐
│                          resource_permissions                          │
├────────────────────────────────────────────────────────────────────────┤
│ id: Integer (PK, Autoincrement)                                        │
│ resource_type: String(20) ('study' ou 'book')                          │
│ resource_id: Integer (ID do recurso)                                   │
│ granted_to_user_id: String(36) (FK users.id ON DELETE CASCADE)          │
│ can_view: Boolean (Default: True)                                      │
│ created_at: UTCDateTime (Default: CURRENT_TIMESTAMP)                   │
├────────────────────────────────────────────────────────────────────────┤
│ UNIQUE(resource_type, resource_id, granted_to_user_id)                 │
│ CHECK(resource_type IN ('study', 'book'))                              │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Modificações em Tabelas Existentes

### 2.1. Tabela `books`
- **Nova Coluna**:
  - `visibility`: `VARCHAR(20) NOT NULL DEFAULT 'private'`
- **Valores Aceitos**:
  - `'private'`: Visível exclusivamente pelo proprietário.
  - `'friends'`: Visível por todos os usuários com amizade aceita (`friendships.status == 'accepted'`).
  - `'public'`: Visível por qualquer usuário autenticado no sistema.
- **Constraint**:
  - `CheckConstraint("visibility IN ('private', 'friends', 'public')", name="chk_book_visibility")`

### 2.2. Tabela `studies`
- **Nova Coluna**:
  - `visibility`: `VARCHAR(20) NOT NULL DEFAULT 'inherit'`
- **Valores Aceitos**:
  - `'inherit'`: Herda a visibilidade definida no livro correspondente (`book.visibility`).
  - `'private'`: Visível exclusivamente pelo proprietário (ignora se o livro for público/amigos).
  - `'friends'`: Visível para todos os amigos mútuos aceitos.
  - `'custom'`: Visível apenas para os usuários cadastrados nominalmente em `resource_permissions`.
  - `'public'`: Visível para qualquer usuário autenticado no sistema com o link.
- **Constraint**:
  - `CheckConstraint("visibility IN ('inherit', 'private', 'friends', 'custom', 'public')", name="chk_study_visibility")`

---

## 3. Nova Tabela: `resource_permissions`

Armazena concessões de acesso nominais direcionadas (ACL) para a granularidade `custom`.

| Coluna | Tipo | Nulável | Descrição |
|---|---|---|---|
| `id` | `INTEGER` | NÃO | Chave primária autoincrement |
| `resource_type` | `VARCHAR(20)` | NÃO | Tipo de recurso: `'study'` ou `'book'` |
| `resource_id` | `INTEGER` | NÃO | Identificador do recurso associado |
| `granted_to_user_id` | `VARCHAR(36)` | NÃO | Chave estrangeira para `users.id` (ON DELETE CASCADE) |
| `can_view` | `BOOLEAN` | NÃO | Flag de permissão de leitura (padrão: `True`) |
| `created_at` | `DATETIME` | NÃO | Data/hora da concessão em UTC |

### Índices e Restrições
- `uq_resource_permission`: `UNIQUE(resource_type, resource_id, granted_to_user_id)`
- `chk_resource_permission_type`: `CHECK(resource_type IN ('study', 'book'))`
- `ix_resource_permissions_target`: Índice sobre `(resource_type, resource_id)` para consultas de listagem e verificação rápida de acesso.
- `ix_resource_permissions_granted`: Índice sobre `(granted_to_user_id)` para alimentar a aba "Compartilhados Comigo".

---

## 4. Schemas Pydantic (Entrada e Saída)

### 4.1. Schemas de Permissão e Compartilhamento
```python
class VisibilityUpdateRequest(BaseModel):
    visibility: str = Field(description="Nível de visibilidade ('inherit', 'private', 'friends', 'custom', 'public')")

class GrantPermissionRequest(BaseModel):
    username: str = Field(description="Handle do usuário (@username) a receber acesso")

class ResourcePermissionItem(BaseModel):
    user_id: str
    username: str
    display_name: str
    avatar_url: str | None
    created_at: datetime

class ResourcePermissionsRead(BaseModel):
    resource_type: str
    resource_id: int
    visibility: str
    effective_visibility: str
    is_owner: bool
    permissions: list[ResourcePermissionItem]
```

### 4.2. Schemas de Recursos Compartilhados
```python
class SharedStudySummary(BaseModel):
    id: int
    title: str
    book_id: int
    book_title: str
    chapter_id: int | None
    chapter_name: str | None
    owner_id: str
    owner_username: str
    owner_display_name: str
    owner_avatar_url: str | None
    visibility: str
    updated_at: datetime

class SharedStudiesResponse(BaseModel):
    items: list[SharedStudySummary]
    total: int
```

---

## 5. Migração Alembic (`0017_add_sharing_and_permissions.py`)

- **Operação de Upgrade**:
  1. `add_column('books', sa.Column('visibility', sa.String(length=20), server_default='private', nullable=False))`
  2. `add_column('studies', sa.Column('visibility', sa.String(length=20), server_default='inherit', nullable=False))`
  3. Criar tabela `resource_permissions` com constraints e índices.
- **Operação de Downgrade**:
  1. `drop_table('resource_permissions')`
  2. `drop_column('studies', 'visibility')`
  3. `drop_column('books', 'visibility')`
- **Isolamento e Segurança**:
  - Dados existentes preservados integralmente: obras existentes recebem `visibility = 'private'` e estudos recebem `visibility = 'inherit'`.
  - Zero impacto em acervos legados.
