# Contracts: F07 — API de Compartilhamento e Recursos Compartilhados

Este documento formaliza as assinaturas, contratos de requisição/resposta e regras de erro para a Feature 07.

---

## 1. Gestão de Permissões e Visibilidade (Proprietário)

### `GET /api/studies/{id}/permissions`
Retorna a visibilidade atual do estudo e a listagem de concessões nominais (quando em modo `custom`).

- **Autenticação**: Obrigatória (Cookie de Sessão ou `X-User-Id`).
- **Autorização**: Apenas o proprietário do estudo pode consultar. Não-proprietários recebem `404 Not Found`.
- **Response 200 OK**:
  ```json
  {
    "resource_type": "study",
    "resource_id": 42,
    "visibility": "custom",
    "effective_visibility": "custom",
    "is_owner": true,
    "permissions": [
      {
        "user_id": "77e382d6-419b-449e-b715-cf64e7c7a331",
        "username": "joao_leitor",
        "display_name": "João Silva",
        "avatar_url": "/api/profile/avatar/joao_leitor",
        "created_at": "2026-09-26T14:00:00Z"
      }
    ]
  }
  ```

---

### `PUT /api/studies/{id}/visibility`
Altera o nível de visibilidade de um estudo.

- **Autenticação**: Obrigatória.
- **Autorização**: Apenas o proprietário.
- **Request Body**:
  ```json
  {
    "visibility": "friends"
  }
  ```
  *(Valores válidos: `'inherit'`, `'private'`, `'friends'`, `'custom'`, `'public'`)*
- **Response 200 OK**: Retorna o objeto de permissões atualizado.
- **Response 422**: Nível de visibilidade inválido.

---

### `POST /api/studies/{id}/permissions`
Concede permissão nominal de leitura a um leitor específico para o estudo.

- **Autenticação**: Obrigatória.
- **Autorização**: Apenas o proprietário.
- **Request Body**:
  ```json
  {
    "username": "joao_leitor"
  }
  ```
- **Response 201 Created**:
  ```json
  {
    "user_id": "77e382d6-419b-449e-b715-cf64e7c7a331",
    "username": "joao_leitor",
    "display_name": "João Silva",
    "avatar_url": null,
    "created_at": "2026-09-26T14:05:00Z"
  }
  ```
- **Response 404**: Usuário com o `@username` não encontrado ou bloqueado.
- **Response 409**: Usuário já possui permissão concedida para este recurso.
- **Response 400**: Tentativa de conceder permissão a si próprio.

---

### `DELETE /api/studies/{id}/permissions/{user_id}`
Revoga a permissão nominal de um leitor específico.

- **Autenticação**: Obrigatória.
- **Autorização**: Apenas o proprietário.
- **Response 200 OK**:
  ```json
  {
    "ok": true
  }
  ```
- **Response 404**: Permissão não encontrada.

---

## 2. Acesso e Descoberta de Recursos Compartilhados

### `GET /api/shared/studies`
Lista estudos de outros leitores que foram compartilhados com o leitor autenticado (via `friends`, `custom` ou `public` de amigos/seguidos).

- **Autenticação**: Obrigatória.
- **Query Parameters**:
  - `q`: Termo de busca textual opcional (título do estudo, livro ou `@username`).
  - `author`: Filtrar por `@username` do autor.
  - `limit`: Inteiro (padrão: 50, máx: 100).
  - `offset`: Inteiro (padrão: 0).
- **Response 200 OK**:
  ```json
  {
    "items": [
      {
        "id": 42,
        "title": "Síntese Epistemológica do Capítulo 3",
        "book_id": 5,
        "book_title": "Crítica da Razão Pura",
        "chapter_id": 12,
        "chapter_name": "Analítica Transcendental",
        "owner_id": "99f482d6-119b-449e-b715-cf64e7c7a999",
        "owner_username": "immanuel_k",
        "owner_display_name": "Immanuel Kant",
        "owner_avatar_url": "/api/profile/avatar/immanuel_k",
        "visibility": "friends",
        "updated_at": "2026-09-26T12:00:00Z"
      }
    ],
    "total": 1
  }
  ```

---

### `GET /api/studies/{id}` (Contrato Estendido com Regras de Compartilhamento)
Consulta um estudo individual. Se o solicitante for o proprietário, entrega com direitos de edição (`can_edit: true`). Se for um convidado autorizado (amigo, ACL custom ou link público autenticado), entrega em modo somente-leitura (`can_edit: false`). Se não for autorizado ou se houver bloqueio, retorna `404 Not Found`.

- **Response 200 OK (para convidado)**:
  ```json
  {
    "id": 42,
    "book_id": 5,
    "chapter_id": 12,
    "title": "Síntese Epistemológica do Capítulo 3",
    "location": "Página 45",
    "notes": "Reflexão sobre a síntese a priori...",
    "summary": "Resumo analítico...",
    "explanation": "Explicação dos conceitos fundamentais...",
    "concepts": "A priori, Intuição pura",
    "references": "B130-B140",
    "source_response": null,
    "created_at": "2026-09-26T10:00:00Z",
    "updated_at": "2026-09-26T12:00:00Z",
    "can_edit": false,
    "owner": {
      "id": "99f482d6-119b-449e-b715-cf64e7c7a999",
      "username": "immanuel_k",
      "display_name": "Immanuel Kant",
      "avatar_url": "/api/profile/avatar/immanuel_k"
    }
  }
  ```
- **Response 404**: Se o estudo for privado, se a permissão não foi concedida ou se os usuários estiverem em relação de bloqueio mútuo/unilateral.
