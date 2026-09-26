# Modelo de Dados: F08 — Administração e RBAC

Este documento descreve os modelos de dados relacionais, estados, projeções e agregações utilizados na **Feature 08 — Administração e RBAC**.

---

## 1. Entidades Principais

### `User` (Tabela `users`)
A tabela de usuários é a entidade central do controle de acesso:

```sql
-- Schema existente no SQLite (modelo Base)
CREATE TABLE users (
    id VARCHAR(36) NOT NULL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) UNIQUE,
    display_name TEXT NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    status VARCHAR(20) NOT NULL DEFAULT 'ativo',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT username_not_blank CHECK (length(trim(username)) > 0),
    CONSTRAINT display_name_not_blank CHECK (length(trim(display_name)) > 0),
    CONSTRAINT chk_user_role CHECK (role IN ('user', 'admin')),
    CONSTRAINT chk_user_status CHECK (status IN ('ativo', 'suspenso'))
);

CREATE INDEX ix_users_username ON users (username);
CREATE INDEX ix_users_email ON users (email);
CREATE INDEX ix_users_role ON users (role);
CREATE INDEX ix_users_status ON users (status);
```

#### Atributos de Governança
- `role`: Define os privilégios do usuário na plataforma.
  - `'user'`: Leitor convencional.
  - `'admin'`: Administrador do sistema com acesso ao painel `/admin` e às rotas `/api/admin/*`.
- `status`: Define se a conta está autorizada a operar.
  - `'ativo'`: Conta em situação regular.
  - `'suspenso'`: Conta com acesso bloqueado administrativamente.

---

### `UserSession` (Tabela `user_sessions`)
Representa os dispositivos e conexões ativas do usuário:

```sql
CREATE TABLE user_sessions (
    id VARCHAR(36) NOT NULL PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token_hash VARCHAR(64) NOT NULL UNIQUE,
    device_name VARCHAR(100) NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    user_agent TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_activity DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL
);

CREATE INDEX ix_user_sessions_user_id ON user_sessions (user_id);
CREATE INDEX ix_user_sessions_expires_at ON user_sessions (expires_at);
```

---

## 2. Máquinas de Estados e Transições

### Máquina de Estados de `status` da Conta

```
                  ┌─────────────────┐
                  │      ativo      │
                  │ (padrão inicial)│
                  └────────┬────────┘
                           │
            Admin suspende │ Admin reativa
            conta          │ conta
            (FR-004/005)   │ (FR-004)
                           ▼
                  ┌─────────────────┐
                  │    suspenso     │
                  │ (sessões purgadas│
                  │  acesso 401/403) │
                  └─────────────────┘
```

#### Regras de Transição de Status:
1. **Ativo -> Suspenso**:
   - Válido se o usuário solicitante for `admin` e `target_user.id != current_user.id`.
   - Se o alvo for outro `admin`, a transição só é permitida se houver pelo menos mais um admin ativo remanescente no sistema.
   - Ação colateral obrigatória: todas as sessões ativas do usuário alvo são excluídas de `user_sessions`.
2. **Suspenso -> Ativo**:
   - Válido se o solicitante for `admin`.
   - O usuário pode voltar a realizar login; nenhuma sessão prévia é restaurada (deve autenticar-se novamente).

---

### Máquina de Estados de `role` do Usuário

```
                  ┌─────────────────┐
                  │      user       │
                  │ (padrão leitor) │
                  └────────┬────────┘
                           │
             Admin promove │ Admin rebaixa
             a admin       │ a user
             (FR-006)      │ (FR-006)
                           ▼
                  ┌─────────────────┐
                  │      admin      │
                  │(acesso /admin)  │
                  └─────────────────┘
```

#### Regras de Transição de Papel:
1. **User -> Admin**:
   - Promove o leitor a administrador.
2. **Admin -> User**:
   - Rebaixa o administrador a leitor comum.
   - **Regra de Proteção de Lockout**: A contagem de administradores com status `'ativo'` após a alteração deve ser de no mínimo 1. Se for o único admin ativo, a operação é bloqueada com HTTP 400 Bad Request.

---

## 3. Schemas de Apresentação e Agregação (Pydantic / TypeScript)

### `AdminUserItem`
Objeto detalhado de usuário retornado na listagem administrativa:

| Campo | Tipo | Descrição |
|---|---|---|
| `id` | `string (UUID)` | Identificador imutável da conta |
| `username` | `string` | Handle do usuário (@username) |
| `display_name` | `string` | Nome exibido publicamente |
| `email` | `string \| null` | E-mail da conta (exclusivo para admins) |
| `role` | `'user' \| 'admin'` | Papel no sistema |
| `status` | `'ativo' \| 'suspenso'` | Situação da conta |
| `provider` | `'local' \| 'google' \| 'ambos'` | Provedores vinculados |
| `created_at` | `string (ISO 8601)` | Data de cadastro |
| `last_access` | `string (ISO 8601) \| null` | Data da atividade mais recente |
| `studies_count` | `number` | Total de estudos criados pelo usuário |
| `books_count` | `number` | Total de livros no acervo do usuário |
| `active_sessions_count` | `number` | Quantidade de sessões ativas no momento |

### `AdminStatsSummary`
Indicadores executivos do topo do painel:

| Campo | Tipo | Descrição |
|---|---|---|
| `total_users` | `number` | Total de contas cadastradas |
| `active_users` | `number` | Contas ativas |
| `suspended_users` | `number` | Contas suspensas |
| `admin_users` | `number` | Total de administradores ativos |
| `total_studies` | `number` | Total de estudos produzidos na plataforma |
