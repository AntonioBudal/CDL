# Pesquisa e Decisões de Arquitetura: F08 — Administração e RBAC

Este documento consolida as decisões técnicas, alternativas analisadas e padrões arquiteturais adotados para a implementação da **Feature 08 — Administração e RBAC** no Caderno de Leitura.

---

## 1. Controle de Acesso Baseado em Papéis (RBAC) no FastAPI

### Decisão
Implementar uma dependência reutilizável `require_admin` em `backend/app/dependencies.py` que resolve o `current_user` (via sessão/cookie ou `X-User-Id` em testes) e valida estritamente se `current_user.role == "admin"`. Caso contrário, levanta `HTTPException(status_code=403, detail="Acesso restrito a administradores.")`.

### Racional
- O FastAPI permite composição elegante de dependências: `AdminUser = Annotated[User, Depends(require_admin)]`.
- O modelo `User` já possui a coluna `role` com valor padrão `'user'` e `status` com valor padrão `'ativo'`.
- A verificação de `user.status == "ativo"` já é realizada na raiz por `get_current_user`.
- O código HTTP 403 Forbidden é semanticamente o correto para requisições autenticadas cujo papel não possui permissão para o recurso solicitado (diferente de 401 Unauthorized para visitantes sem sessão válida).

### Alternativas Consideradas
- **Sistema de permissões matricial com escopos OAuth2 (scopes)**: Desnecessariamente complexo para a escala da aplicação; o modelo canônico de dois papéis (`admin` vs `user`) atende com clareza e alta manutenibilidade.
- **Middleware interceptor global para rotas `/api/admin/*`**: Menos explícito e dificulta testes unitários diretos nos routers; dependências FastAPI oferecem injeção tipada e contratos claros no Swagger/OpenAPI.

---

## 2. Suspensão Atômica e Revogação Imediata de Sessões

### Decisão
A operação de suspensão (`POST /api/admin/users/{id}/suspend` executada por admin):
1. Altera `user.status = "suspenso"`.
2. Invoca `session_service.revoke_user_all_sessions(session, user.id)`, deletando/revogando todas as sessões ativas do usuário no banco SQLite.
3. Executa `commit_changes(session)` para assegurar durabilidade imediata no modo WAL.

### Racional
- Cumpre a escolha deliberada na especificação (Q1: A).
- A invalidação atômica impede que um usuário com token ativo continue operando em abas abertas ou no aplicativo móvel.
- Mesmo se houvesse qualquer cache em memória, a próxima requisição falha tanto pela ausência do token na tabela `user_sessions` quanto pela checagem de `user.status != 'ativo'` em `get_current_user`.

### Alternativas Consideradas
- **Apenas alterar status sem revogar sessões**: Deixaria janelas de vulnerabilidade até a expiração natural da sessão (de até 30 dias).
- **Lista negra em memória (Redis/in-memory blocklist)**: Viola o princípio de arquitetura local sem dependências externas adicionais. O SQLite é rápido o suficiente para revogação em banco.

---

## 3. Proteção contra Auto-Bloqueio e Extinção do Papel Admin

### Decisão
Criar regras estritas de integridade na camada de serviço (`admin_service.py`):
1. **Auto-Suspensão Proibida**: Um admin não pode suspender sua própria conta (`target_user.id == current_user.id` -> `HTTP 400 Bad Request` com mensagem explicativa).
2. **Auto-Rebaixamento Condicional**: Um admin só pode alterar o próprio papel para `user` se houver pelo menos um outro administrador ativo no sistema (`active_admin_count > 1`). Se `active_admin_count <= 1`, a operação é terminantemente recusada (`HTTP 400 Bad Request`).
3. **Suspensão de Outro Admin**: Só permitida se restar pelo menos um administrador ativo além daquele que está sendo suspenso.

### Racional
- Previne lockout permanente acidental ou malicioso no sistema ("a chave trancada dentro de casa").
- Mantém a governança soberana do servidor local.

### Alternativas Consideradas
- **Permitir auto-rebaixamento com confirmação dupla**: Arriscado caso seja o único admin, pois exigiria intervenção no banco via terminal para recuperação.
- **Conta admin raiz imutável**: Inflexível; permitir múltiplos admins promove colaboração familiar ou de grupos de estudo, desde que a contagem mínima de 1 seja preservada.

---

## 4. Utilitário CLI para Provisionamento do Administrador Inicial

### Decisão
Implementar um script autônomo e executável `backend/scripts/create_admin.py` (e registrá-lo também como subcomando em `python -m app.cli create-admin`):
- Modo 1 (Criação Nova): Solicita `@username`, `email` e `senha` (com confirmação e máscara via `getpass.getpass`), valida complexidade mínima (mínimo 8 caracteres) e salva a conta com `role='admin'` e senha com hash Argon2id / bcrypt compatível com `LocalCredential`.
- Modo 2 (Promoção): Se o `@username` informado já existir na base, pergunta ao operador se deseja promovê-lo a administrador (`role='admin'`), atualizando o registro imediatamente.

### Racional
- Atende à decisão Q3: A.
- Não expõe a senha em argumentos de linha de comando ou histórico de shell (`bash_history` / `PSReadLine`).
- Funciona tanto para novas instalações quanto para sistemas existentes onde o usuário já se cadastrou como leitor e deseja se tornar administrador.

### Alternativas Consideradas
- **Variáveis no `.env`**: Risco de deixar credenciais permanentes em texto plano no arquivo de configuração do sistema.
- **Inserção via SQL manual**: Propenso a erros na geração do hash criptográfico e IDs UUID.

---

## 5. Interface do Painel Administrativo no Frontend (Vue 3 / TypeScript)

### Decisão
- Criar a view principal `frontend/src/views/AdminView.vue` acessível na rota `/admin`.
- Proteger a rota no Vue Router via `beforeEnter` / navigation guard: se `!authStore.isAuthenticated || authStore.currentUser?.role !== 'admin'`, redireciona para a home (`/`) com feedback discreto.
- Exibir o link "Administração" na barra de navegação superior (`App.vue`), visível somente se `currentUser?.role === 'admin'`.
- Componentes organizados:
  - `AdminUsersTable.vue`: Listagem tabular com colunas ID, Usuário, E-mail, Provedor, Criação, Último Acesso, Status, Role, Estudos e Ações.
  - `AdminConfirmModal.vue`: Modal de confirmação acessível (WAI-ARIA `role="dialog"`, alvos de toque >= 44px) para suspender, reativar, promover/rebaixar ou revogar sessões.
  - Barra de busca e filtros rápidos de status (`Todos`, `Ativos`, `Suspensos`).
  - Sem emojis informais, seguindo a diretriz editorial rígida do Caderno de Leitura.

### Racional
- Atende à decisão Q2: A.
- Ergonomia consistente com o restante da plataforma (alvos táteis, acessibilidade WCAG 2.1 AA).
- Separação clara de responsabilidades no frontend.
