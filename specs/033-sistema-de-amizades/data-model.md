# Data Model: F06 — Sistema de Amizades

Este documento especifica as estruturas de dados relacionais, entidades de domínio, restrições de integridade e esquemas de validação para o Sistema de Amizades.

---

## 1. Esquema Relacional (SQL / SQLAlchemy 2.0)

### Tabela `friendships`

A tabela armazena a relação normalizada entre dois usuários, garantindo um único registro por par através da ordenação dos identificadores (`user_id_a < user_id_b`).

| Coluna | Tipo | Nulável | Descrição / Restrições |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | Não | Chave primária autoincremento. |
| `user_id_a` | `VARCHAR(36)` | Não | Chave estrangeira para `users.id` (ON DELETE CASCADE). Menor UUID do par. |
| `user_id_b` | `VARCHAR(36)` | Não | Chave estrangeira para `users.id` (ON DELETE CASCADE). Maior UUID do par. |
| `status` | `VARCHAR(20)` | Não | Estado canônico: `'pending'`, `'accepted'`, `'blocked'`. |
| `action_user_id` | `VARCHAR(36)` | Não | Chave estrangeira para `users.id`. Usuário que provocou a última alteração. |
| `created_at` | `DATETIME` | Não | Timestamp em UTC de criação do registro. |
| `updated_at` | `DATETIME` | Não | Timestamp em UTC da última modificação. |

### Restrições e Índices

- **`uq_friendships_pair`**: `UNIQUE(user_id_a, user_id_b)` — Garante unicidade estrita por par ordenado.
- **`ck_friendships_ordered_pair`**: `CHECK(user_id_a < user_id_b)` — Assegura consistência física e elimina duplicações espelhadas.
- **`ck_friendships_no_self`**: `CHECK(user_id_a != user_id_b)` — Impede relacionamentos reflexivos (auto-amizade).
- **`ix_friendships_user_a`**: Índice em `user_id_a`.
- **`ix_friendships_user_b`**: Índice em `user_id_b`.
- **`ix_friendships_status`**: Índice composto em `(status, action_user_id)`.

---

## 2. Máquina de Estados e Transições

```
        ┌────────────────────────────────────────────────────────┐
        │                                                        │
        ▼ (solicitar / request)                                  │ (desbloquear)
┌───────────────┐                  ┌───────────────┐             │
│    PENDING    │──(aceitar)──────▶│   ACCEPTED    │             │
└───────────────┘                  └───────────────┘             │
  │            │                     │                           │
  │ (recusar)  │ (cancelar)          │ (desfazer)                │
  ▼            ▼                     ▼                           │
┌──────────────────────────────────────────────────┐             │
│                   SEM VÍNCULO                    │             │
└──────────────────────────────────────────────────┘             │
        │                                                        │
        │ (bloquear a partir de qualquer estado)                 │
        ▼                                                        │
┌───────────────┐                                                │
│    BLOCKED    │────────────────────────────────────────────────┘
└───────────────┘
```

### Regras de Transição

1. **Sem Vínculo ➔ PENDING**:
   - `action_user_id` = solicitante.
   - Par ordenado gravado com `user_id_a < user_id_b`.
   - Se já existia pendência inversa, avança diretamente para `ACCEPTED`.
2. **PENDING ➔ ACCEPTED**:
   - Permitido exclusivamente para o usuário que **não** é o `action_user_id` (o destinatário).
   - `action_user_id` atualizado para o destinatário que aceitou.
3. **PENDING ➔ SEM VÍNCULO (Recusa ou Cancelamento)**:
   - Recusa: acionada pelo destinatário (`current_user != action_user_id`).
   - Cancelamento: acionado pelo remetente (`current_user == action_user_id`).
   - O registro é removido fisicamente do banco de dados (`session.delete`).
4. **ACCEPTED ➔ SEM VÍNCULO (Desfazer Amizade)**:
   - Acionado por qualquer um dos dois participantes.
   - O registro é removido fisicamente do banco.
5. **Qualquer Estado ➔ BLOCKED**:
   - Acionado por qualquer um dos usuários contra o outro.
   - Atualiza `status = 'blocked'` e `action_user_id = bloqueador`.
   - Se já existia registro (amigos ou pendente), sobrepõe o estado. Se não existia, cria novo registro `BLOCKED`.
6. **BLOCKED ➔ SEM VÍNCULO (Desbloquear)**:
   - Permitido exclusivamente para o autor do bloqueio (`current_user == action_user_id`).
   - O registro é removido fisicamente do banco.

---

## 3. Schemas de Dados (Pydantic v2)

```python
class FriendUserRead(BaseModel):
    id: str
    username: str
    display_name: str
    avatar_url: str | None = None
    bio: str | None = None

class FriendItem(BaseModel):
    friendship_id: int
    user: FriendUserRead
    since: datetime

class FriendRequestItem(BaseModel):
    request_id: int
    user: FriendUserRead
    direction: Literal["sent", "received"]
    created_at: datetime

class FriendBlockedItem(BaseModel):
    friendship_id: int
    user: FriendUserRead
    blocked_at: datetime

class FriendsSummaryResponse(BaseModel):
    friends_count: int
    pending_received_count: int
    pending_sent_count: int

class FriendshipStatusResponse(BaseModel):
    relation_status: Literal[
        "none",
        "pending_sent",
        "pending_received",
        "friends",
        "blocked_by_me",
        "blocked_by_them"
    ]
    request_id: int | None = None
    since: datetime | None = None
```
