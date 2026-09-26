# Administração e Controle de Acesso Baseado em Papéis (RBAC)

Este documento descreve a arquitetura, regras de autorização, operações de moderação, proteção contra bloqueios acidentais e ferramentas CLI implementadas na funcionalidade **F08 — Administração e RBAC** do Caderno de Leitura.

---

## 1. Visão Geral da Arquitetura RBAC

O Caderno de Leitura adota um modelo de **Controle de Acesso Baseado em Papéis (Role-Based Access Control - RBAC)** com dois papéis canônicos de usuário:

| Papel (`role`) | Descrição | Permissões |
|---|---|---|
| **`user`** (Padrão) | Leitor convencional do sistema | Acesso ao próprio acervo (livros, estudos, canvas), perfil pessoal, amizades e recursos explicitamente compartilhados com ele. Bloqueado de qualquer operação administrativa com `HTTP 403 Forbidden`. |
| **`admin`** | Administrador do sistema | Acesso irrestrito ao painel administrativo (`/admin`), visão consolidada de todas as contas da plataforma, métricas globais, moderação (suspensão/reativação), desconexão forçada de sessões e alteração de papéis. |

### Dependência de Autorização no FastAPI

A autorização é aplicada de forma declarativa e rigorosa através da dependência `require_admin` em `backend/app/dependencies.py`:

```python
def require_admin(current_user: CurrentUser) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores.",
        )
    return current_user

AdminUser = Annotated[User, Depends(require_admin)]
```

Todas as rotas sob o prefixo `/api/admin/*` injetam `current_admin: AdminUser`, garantindo rejeição imediata de qualquer requisição que não provenha de uma conta administrativa autenticada.

---

## 2. Máquina de Estados da Conta e Transições

O modelo `User` gerencia dois eixos ortogonais de estado:

```
  [user] <==== (update_user_role) ====> [admin]
                  (anti-lockout)

  [ativo] <==== (suspend / reactivate) ====> [suspenso]
                  (purga de sessões)
```

### Regras de Transição

1. **Suspensão (`ativo` → `suspenso`)**:
   - Marca o status do usuário como `suspenso`.
   - **Revogação Atômica de Sessões**: Todas as sessões ativas do usuário em `user_sessions` são imediatamente excluídas do banco de dados (`revoke_user_all_sessions`).
   - Todos os dispositivos conectados do usuário (PC e mobile) perdem acesso instantaneamente, recebendo `HTTP 401 Unauthorized` ou `HTTP 403 Forbidden` na chamada seguinte.
2. **Reativação (`suspenso` → `ativo`)**:
   - Restaura o status do usuário para `ativo`.
   - Permite que o usuário volte a realizar login normalmente com suas credenciais.
3. **Promoção (`user` → `admin`)**:
   - Concede prerrogativas administrativas à conta.
4. **Rebaixamento (`admin` → `user`)**:
   - Remove prerrogativas administrativas, sujeito à salvaguarda do último administrador.

---

## 3. Salvaguardas Anti-Lockout

Para prevenir estados irrecuperáveis onde o sistema ficaria sem administradores ativos:

1. **Proteção contra Auto-Suspensão**:
   - O administrador autenticado está estritamente proibido de suspender sua própria conta através da interface ou API (`HTTP 400 Bad Request`).
2. **Proteção do Último Administrador Ativo**:
   - É terminantemente proibido suspender ou rebaixar (`admin` → `user`) uma conta se não houver pelo menos **outro administrador ativo** cadastrado no banco de dados (`HTTP 400 Bad Request`).

---

## 4. Endpoints REST Administrativos

Todas as rotas respondem sob o prefixo `/api/admin`:

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/admin/users` | Listagem paginada de contas com métricas agregadas (estudos, livros, sessões ativas), busca textual (`q`) e filtros (`status`, `role`). |
| `GET` | `/api/admin/stats` | Indicadores globais da plataforma (total de contas, ativas, suspensas, administradores, total de estudos). |
| `POST` | `/api/admin/users/{id}/suspend` | Suspende conta e revoga atomicamente todas as sessões ativas. Aceita motivo opcional (`reason`). |
| `POST` | `/api/admin/users/{id}/reactivate` | Reativa conta suspensa. |
| `PUT` | `/api/admin/users/{id}/role` | Altera papel entre `user` e `admin`, validando proteção do último admin. |
| `POST` | `/api/admin/users/{id}/sessions/revoke-all` | Desconecta forçadamente todos os dispositivos ativos do usuário sem alterar status da conta. |

---

## 5. Utilitário CLI para Terminal

Para provisionar o primeiro administrador ou promover contas locais de forma direta e segura sem tocar no banco de dados SQLite:

```powershell
# Na raiz da aplicação (caderno-leitura-0.1):

# 1. Modo interativo com senha oculta via getpass:
.\backend\.venv\Scripts\python.exe backend/scripts/create_admin.py

# 2. Modo com parâmetros completos de linha de comando:
.\backend\.venv\Scripts\python.exe backend/scripts/create_admin.py --username admin --email admin@caderno.local --password "SenhaForte123!" --display-name "Administrador"

# 3. Promoção determinística de usuário existente:
.\backend\.venv\Scripts\python.exe backend/scripts/create_admin.py --promote @usuario_leitor
```

---

## 6. Frontend: Painel Administrativo e Guardas de Rota

### Componentes e Telas

- **`AdminView.vue` (`/admin`)**:
  - Cards de topo com indicadores numéricos agregados.
  - Barra de busca com debounce e filtros combinados por Status e Papel.
  - Tabela semântica `<AdminUsersTable />` com métricas operacionais por conta.
  - Diálogo modal acessível `<AdminConfirmModal />` com suporte WAI-ARIA, foco automático e alvos táteis mínimos de 44px.
- **Navegação no `App.vue`**:
  - O link "Administração" na barra superior é condicionado a `auth.isAdmin.value`, permanecendo invisível para usuários convencionais.
- **Navigation Guard no Vue Router (`router/index.ts`)**:
  - Qualquer tentativa de navegação direta para `/admin` por usuário sem papel de administrador é interceptada e redirecionada para a página inicial com query parameter explicativo (`?aviso=acesso-restrito`).

---

## 7. Governança e Isolamento de Dados

- **Privacidade Estrita**: E-mails de usuários são visíveis única e exclusivamente no painel administrativo para contas autenticadas como admin.
- **Isolamento em Testes**: Todos os testes automatizados (`test_admin_and_rbac.py` e `admin.test.mjs`) operam sobre bancos de dados temporários e efêmeros gerados via `tmp_path`. O banco de produção `backend/data/caderno.db` nunca é acessado durante testes.
