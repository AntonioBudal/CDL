# Contrato de API: F08 — Administração e RBAC

Todos os endpoints descritos neste contrato exigem autenticação ativa e papel de administrador (`role === 'admin'`). Usuários com papel `user` recebem `HTTP 403 Forbidden`. Visitantes não autenticados recebem `HTTP 401 Unauthorized`.

---

## 1. Listagem e Filtro de Usuários

### `GET /api/admin/users`

Retorna a lista paginada de contas cadastradas com agregações operacionais.

#### Parâmetros de Query

| Parâmetro | Tipo | Padrão | Descrição |
|---|---|---|---|
| `q` | `string` | — | Busca textual por `@username`, nome de exibição ou e-mail |
| `status` | `string` | `all` | Filtro por status: `all`, `ativo`, `suspenso` |
| `role` | `string` | `all` | Filtro por papel: `all`, `user`, `admin` |
| `limit` | `integer` | `50` | Limite de registros por página (1..100) |
| `offset` | `integer` | `0` | Deslocamento para paginação |

#### Resposta de Sucesso (`200 OK`)

```json
{
  "items": [
    {
      "id": "a0000000-0000-0000-0000-000000000001",
      "username": "admin_principal",
      "display_name": "Administrador Principal",
      "email": "admin@caderno.local",
      "role": "admin",
      "status": "ativo",
      "provider": "local",
      "created_at": "2026-09-20T10:00:00Z",
      "last_access": "2026-09-26T14:00:00Z",
      "studies_count": 14,
      "books_count": 3,
      "active_sessions_count": 2
    },
    {
      "id": "b1111111-1111-1111-1111-111111111111",
      "username": "leitor_amigo",
      "display_name": "Amigo Leitor",
      "email": "amigo@email.com",
      "role": "user",
      "status": "ativo",
      "provider": "google",
      "created_at": "2026-09-22T15:30:00Z",
      "last_access": "2026-09-26T12:00:00Z",
      "studies_count": 8,
      "books_count": 2,
      "active_sessions_count": 1
    }
  ],
  "total": 2
}
```

---

## 2. Indicadores da Aplicação

### `GET /api/admin/stats`

Retorna estatísticas consolidadas para os cards do topo do painel administrativo.

#### Resposta de Sucesso (`200 OK`)

```json
{
  "total_users": 15,
  "active_users": 14,
  "suspended_users": 1,
  "admin_users": 2,
  "total_studies": 142
}
```

---

## 3. Moderação de Conta

### `POST /api/admin/users/{id}/suspend`

Suspende a conta indicada e invalida imediatamente todas as suas sessões ativas no banco de dados.

#### Payload de Requisição (Opcional)

```json
{
  "reason": "Comportamento ofensivo recorrente nos compartilhamentos"
}
```

#### Resposta de Sucesso (`200 OK`)

```json
{
  "id": "b1111111-1111-1111-1111-111111111111",
  "status": "suspenso",
  "sessions_revoked": 2,
  "message": "Conta suspensa com sucesso. 2 sessões ativas foram revogadas."
}
```

#### Códigos de Erro
- `400 Bad Request`:
  - `{"detail": "Você não pode suspender sua própria conta de administrador."}`
  - `{"detail": "Não é possível suspender o único administrador ativo do sistema."}`
- `404 Not Found`: Usuário não encontrado.

---

### `POST /api/admin/users/{id}/reactivate`

Restaura o status da conta para `ativo`, permitindo novos logins.

#### Resposta de Sucesso (`200 OK`)

```json
{
  "id": "b1111111-1111-1111-1111-111111111111",
  "status": "ativo",
  "message": "Conta reativada com sucesso."
}
```

#### Códigos de Erro
- `404 Not Found`: Usuário não encontrado.

---

### `POST /api/admin/users/{id}/sessions/revoke-all`

Encerra forçadamente todas as sessões ativas de um usuário sem alterar seu status de conta.

#### Resposta de Sucesso (`200 OK`)

```json
{
  "id": "b1111111-1111-1111-1111-111111111111",
  "sessions_revoked": 3,
  "message": "Todas as 3 sessões do usuário foram revogadas."
}
```

---

## 4. Gestão de Papéis (RBAC)

### `PUT /api/admin/users/{id}/role`

Altera o papel do usuário entre `user` e `admin`.

#### Payload de Requisição

```json
{
  "role": "admin"
}
```

#### Resposta de Sucesso (`200 OK`)

```json
{
  "id": "b1111111-1111-1111-1111-111111111111",
  "role": "admin",
  "message": "Papel do usuário atualizado para admin com sucesso."
}
```

#### Códigos de Erro
- `400 Bad Request`:
  - `{"detail": "Não é possível rebaixar o único administrador ativo do sistema."}`
  - `{"detail": "Papel inválido. Valores aceitos: 'user', 'admin'."}`
- `404 Not Found`: Usuário não encontrado.
