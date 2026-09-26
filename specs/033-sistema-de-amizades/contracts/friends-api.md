# API Contracts: F06 — Sistema de Amizades

Este documento especifica formalmente as rotas HTTP, parâmetros, códigos de status e contratos de dados para o módulo de amizades e interações sociais.

---

## 1. Ciclo de Vida de Amizades (`/api/friends`)

### 1.1 Enviar Solicitação de Amizade
- **Rota**: `POST /api/friends/request/{username}`
- **Autenticação**: Obrigatória (`caderno_session` ou `X-User-Id`).
- **Respostas**:
  - `200 OK`: Solicitação enviada com sucesso ou convertida automaticamente para amizade (caso houvesse solicitação inversa prévia).
    ```json
    {
      "ok": true,
      "message": "Solicitação de amizade enviada com sucesso.",
      "status": "pending"
    }
    ```
  - `400 Bad Request`: Tentativa de solicitar amizade a si mesmo.
  - `404 Not Found`: Usuário não encontrado ou usuário bloqueador (blindagem anti-enumeração).
  - `409 Conflict`: Já existe solicitação pendente ativa ou ambos já são amigos.

---

### 1.2 Aceitar Solicitação de Amizade
- **Rota**: `POST /api/friends/accept/{request_id}`
- **Autenticação**: Obrigatória.
- **Parâmetros**: `request_id` (inteiro) — Identificador único da solicitação.
- **Respostas**:
  - `200 OK`: Amizade aceita e estabelecida com sucesso.
    ```json
    {
      "ok": true,
      "message": "Solicitação de amizade aceita.",
      "status": "accepted"
    }
    ```
  - `403 Forbidden`: Usuário atual é o autor original da solicitação (`action_user_id`), não podendo aceitar a própria solicitação.
  - `404 Not Found`: Solicitação não encontrada ou não pertencente ao usuário.

---

### 1.3 Recusar Solicitação de Amizade
- **Rota**: `POST /api/friends/reject/{request_id}`
- **Autenticação**: Obrigatória.
- **Respostas**:
  - `200 OK`: Solicitação recusada e vínculo removido.
    ```json
    {
      "ok": true,
      "message": "Solicitação de amizade recusada.",
      "status": "none"
    }
    ```
  - `403 Forbidden`: Usuário atual não é o destinatário da solicitação.
  - `404 Not Found`: Solicitação inexistente.

---

### 1.4 Cancelar Solicitação Enviada
- **Rota**: `DELETE /api/friends/cancel/{request_id}`
- **Autenticação**: Obrigatória.
- **Respostas**:
  - `200 OK`: Solicitação cancelada pelo remetente.
    ```json
    {
      "ok": true,
      "message": "Solicitação de amizade cancelada.",
      "status": "none"
    }
    ```
  - `403 Forbidden`: Usuário atual não é o autor da solicitação enviada.
  - `404 Not Found`: Solicitação inexistente.

---

### 1.5 Desfazer Amizade Ativa
- **Rota**: `DELETE /api/friends/{username}`
- **Autenticação**: Obrigatória.
- **Respostas**:
  - `200 OK`: Amizade encerrada.
    ```json
    {
      "ok": true,
      "message": "Vínculo de amizade desfeito.",
      "status": "none"
    }
    ```
  - `404 Not Found`: Usuário não encontrado ou não há vínculo de amizade aceito ativo entre as partes.

---

### 1.6 Bloquear Usuário
- **Rota**: `POST /api/friends/block/{username}`
- **Autenticação**: Obrigatória.
- **Respostas**:
  - `200 OK`: Usuário bloqueado com sucesso (amizade prévia ou solicitações desfeitas).
    ```json
    {
      "ok": true,
      "message": "Usuário bloqueado com sucesso.",
      "status": "blocked"
    }
    ```
  - `400 Bad Request`: Tentativa de bloquear a si mesmo.
  - `404 Not Found`: Usuário alvo inexistente.

---

### 1.7 Desbloquear Usuário
- **Rota**: `POST /api/friends/unblock/{username}`
- **Autenticação**: Obrigatória.
- **Respostas**:
  - `200 OK`: Usuário desbloqueado (relação retorna a neutra).
    ```json
    {
      "ok": true,
      "message": "Usuário desbloqueado.",
      "status": "none"
    }
    ```
  - `403 Forbidden`: O usuário atual não foi o autor do bloqueio.
  - `404 Not Found`: Não há bloqueio ativo contra o usuário indicado.

---

## 2. Listagens e Consultas Sociais

### 2.1 Listar Amigos Ativos
- **Rota**: `GET /api/friends`
- **Autenticação**: Obrigatória.
- **Respostas**:
  - `200 OK`:
    ```json
    [
      {
        "friendship_id": 1,
        "user": {
          "id": "uuid-...",
          "username": "mariasilva",
          "display_name": "Maria Silva",
          "avatar_url": "/api/avatars/maria.webp",
          "bio": "Estudiosa de Filosofia e Literatura."
        },
        "since": "2026-09-25T14:30:00Z"
      }
    ]
    ```

---

### 2.2 Listar Solicitações Pendentes
- **Rota**: `GET /api/friends/requests`
- **Autenticação**: Obrigatória.
- **Respostas**:
  - `200 OK`:
    ```json
    {
      "received": [
        {
          "request_id": 4,
          "user": {
            "id": "uuid-...",
            "username": "joaoleitor",
            "display_name": "João",
            "avatar_url": null,
            "bio": null
          },
          "direction": "received",
          "created_at": "2026-09-25T16:00:00Z"
        }
      ],
      "sent": [
        {
          "request_id": 5,
          "user": {
            "id": "uuid-...",
            "username": "claramar",
            "display_name": "Clara",
            "avatar_url": null,
            "bio": null
          },
          "direction": "sent",
          "created_at": "2026-09-25T17:15:00Z"
        }
      ]
    }
    ```

---

### 2.3 Listar Usuários Bloqueados
- **Rota**: `GET /api/friends/blocked`
- **Autenticação**: Obrigatória.
- **Respostas**:
  - `200 OK`:
    ```json
    [
      {
        "friendship_id": 9,
        "user": {
          "id": "uuid-...",
          "username": "usuariochato",
          "display_name": "Usuário Chato",
          "avatar_url": null,
          "bio": null
        },
        "blocked_at": "2026-09-25T18:00:00Z"
      }
    ]
    ```

---

### 2.4 Resumo Social (Contadores para UI)
- **Rota**: `GET /api/friends/summary`
- **Autenticação**: Obrigatória.
- **Respostas**:
  - `200 OK`:
    ```json
    {
      "friends_count": 5,
      "pending_received_count": 2,
      "pending_sent_count": 1
    }
    ```

---

### 2.5 Consultar Status com Usuário Específico
- **Rota**: `GET /api/friends/status/{username}`
- **Autenticação**: Obrigatória.
- **Respostas**:
  - `200 OK`:
    ```json
    {
      "relation_status": "pending_received",
      "request_id": 4,
      "since": "2026-09-25T16:00:00Z"
    }
    ```
