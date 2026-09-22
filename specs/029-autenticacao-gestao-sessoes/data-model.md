# Data Model: Autenticação e Gestão de Sessões (F02)

**Feature**: `029-autenticacao-gestao-sessoes`  
**Date**: 2026-09-21  
**Status**: Completed  

---

## 1. Diagrama de Relacionamento de Entidades (ERD)

```
┌─────────────────────────────────────────────────────────────┐
│                            User                             │
├─────────────────────────────────────────────────────────────┤
│ id: String(36) [PK, UUID]                                   │
│ username: String(50) [Unique, Indexed]                      │
│ email: String(255) [Unique, Indexed, Nullable]              │
│ display_name: Text                                          │
│ role: String(20) [admin | user, default='user']             │
│ status: String(20) [ativo | suspenso | inativo]             │
│ created_at: UTCDateTime                                     │
│ updated_at: UTCDateTime                                     │
└──────────────┬───────────────────────────────┬──────────────┘
               │ 1                             │ 1
               │                               │
               ▼ 0..1                          ▼ *
┌──────────────────────────────┐ ┌──────────────────────────────┐
│       LocalCredential        │ │         UserSession          │
├──────────────────────────────┤ ├──────────────────────────────┤
│ user_id: String(36) [PK, FK] │ │ id: String(36) [PK, UUID]    │
│ password_hash: Text          │ │ user_id: String(36) [FK, Idx]│
│ password_updated_at: DateTime│ │ session_token_hash: Str(64)  │
└──────────────────────────────┘ │   [Unique, Indexed]          │
                                 │ device_name: String(100)     │
                                 │ ip_address: String(45)       │
                                 │ user_agent: Text             │
                                 │ created_at: UTCDateTime      │
                                 │ last_activity: UTCDateTime   │
                                 │ expires_at: UTCDateTime [Idx]│
                                 └──────────────────────────────┘
```

---

## 2. Especificação das Tabelas e Entidades

### 2.1. Entidade `User` (Atualização no modelo existente)

Adiciona atributos de credencial pública e autorização:
- **`email`**: `String(255)`, único, indexado, opcional (permite cadastro com ou sem e-mail em ambientes locais restritos).
- **`role`**: `String(20)`, obrigatório, padrão `'user'` (o proprietário canônico recebe `'admin'`).
- **Relacionamentos**:
  - `credential`: `LocalCredential` (1 para 0..1, `uselist=False`, cascade delete).
  - `sessions`: `list[UserSession]` (1 para N, cascade delete).

### 2.2. Entidade `LocalCredential` (Nova)

Armazena as informações de senha local protegidas com chave derivada:
- **`user_id`**: `String(36)`, chave primária e chave estrangeira apontando para `users.id` com `ondelete="CASCADE"`.
- **`password_hash`**: `Text`, não anulável. Armazena a string formatada padrão Argon2id (`$argon2id$v=19$m=65536,t=2,p=1$...`).
- **`password_updated_at`**: `UTCDateTime`, não anulável, padrão horário UTC atual.

### 2.3. Entidade `UserSession` (Nova)

Registra cada dispositivo/navegador ativo conectado à conta:
- **`id`**: `String(36)`, chave primária com UUID v4.
- **`user_id`**: `String(36)`, chave estrangeira para `users.id` com `ondelete="CASCADE"`, indexada para consultas rápidas de sessões por usuário.
- **`session_token_hash`**: `String(64)`, string hexadecimal do hash SHA-256 do token opaco entregue ao cookie do cliente. Único e indexado.
- **`device_name`**: `String(100)`, descrição amigável formatada a partir do User-Agent (ex.: "Chrome no Windows", "Safari no iPhone").
- **`ip_address`**: `String(45)`, endereço IP do cliente (compatível com IPv4 e IPv6).
- **`user_agent`**: `Text`, cabeçalho original bruto recebido na criação ou atualização.
- **`created_at`**: `UTCDateTime`, data e hora de emissão da sessão.
- **`last_activity`**: `UTCDateTime`, data e hora da última requisição com atividade processada.
- **`expires_at`**: `UTCDateTime`, carimbo de expiração calculado (geralmente `last_activity + 30 dias`), indexado para limpeza periódica de sessões expiradas.

---

## 3. Regras de Validação e Integridade

1. **Unicidade de Identificadores**:
   - `username`: Deve ser alfanumérico com hífens ou sublinhados (`^[a-zA-Z0-9_.-]{3,50}$`), único em toda a base.
   - `email`: Caso fornecido, deve atender ao formato padrão de e-mail e ser único em toda a base.
2. **Requisitos Mínimos de Senha**:
   - Mínimo de 8 caracteres.
   - Proibição de caracteres nulos ou espaços exclusivamente em branco.
3. **Integridade Referencial em Cascata**:
   - Exclusão ou purga de um usuário remove automaticamente sua credencial local (`LocalCredential`) e todas as suas sessões ativas (`UserSession`).
4. **Ciclo de Vida de Sessões e Transição de Estados**:
   - **Ativa**: `expires_at > now()` e `user.status == 'ativo'`.
   - **Expirada**: `expires_at <= now()`. Rejeitada com `HTTP 401 Unauthorized` e passível de purga automática.
   - **Revogada**: Deletada fisicamente do banco de dados na ação de logout, revogação remota ou encerramento coletivo (*logout-all*).

---

## 4. Migração Alembic (Versão 0012)

- Adição de colunas `email` e `role` na tabela `users` via `batch_alter_table`.
- Atribuição de `role='admin'` para o proprietário canônico (`00000000-0000-0000-0000-000000000001`).
- Criação da tabela `local_credentials` com chave primária e estrangeira `user_id`.
- Criação da tabela `user_sessions` com índices em `user_id`, `session_token_hash` e `expires_at`.
- Suporte total a `downgrade()` com remoção segura de tabelas e reversão de colunas em SQLite.
