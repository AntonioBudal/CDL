# Guia Rápido de Validação: F08 — Administração e RBAC

Este guia descreve os passos práticos e comandos reproduzíveis para validar de ponta a ponta as funcionalidades de Administração e RBAC.

---

## 1. Pré-Requisitos e Ambiente de Testes

1. Servidor e dependências instaladas (`backend/.venv` ativo).
2. Para validação manual isolada, use uma variável de ambiente apontando para um banco temporário ou execute os testes automatizados herméticos.

---

## 2. Cenários de Validação

### Cenário 1: Provisionamento do Administrador Inicial via CLI

Execute o script de criação de administrador pelo terminal:

```powershell
cd backend
.venv\Scripts\python.exe scripts/create_admin.py --username admin_teste --email admin@teste.local --password "SenhaForte123!"
```

**Resultado Esperado**:
- O comando confirma: `Administrador 'admin_teste' criado com sucesso com papel 'admin'.`
- Se for executado novamente com o mesmo username, ele informa que o usuário já existe e confirma que ele já possui privilégios de administrador.

---

### Cenário 2: Verificação de Acesso e Indicadores no Painel Web (`/admin`)

1. Inicie a aplicação com `python iniciar.py` (ou `npm run dev` no frontend).
2. Faça login com a conta de administrador criada (`admin_teste`).
3. Observe a barra superior de navegação (`App.vue`): o link "Administração" é exibido com destaque.
4. Clique no link ou navegue até `http://localhost:8000/admin` (ou `http://localhost:5173/admin`).
5. Observe os cards de topo com contagem total de usuários, usuários ativos, suspensos e total de estudos.
6. A tabela lista todas as contas do sistema com colunas de Username, E-mail, Provedor, Data de Criação, Último Acesso, Status e Role.

---

### Cenário 3: Blindagem 403 Forbidden para Leitores Convencionais

1. Abra uma janela anônima no navegador.
2. Crie uma conta comum de leitor (`leitor_comum`).
3. Tente acessar diretamente a rota `/admin`.
4. **Resultado Esperado**: O Vue Router intercepta a navegação no Navigation Guard e redireciona o usuário para a página inicial com aviso de permissão insuficiente.
5. Se for feita uma requisição direta à API via curl ou PowerShell:
   ```powershell
   curl http://localhost:8000/api/admin/users -H "X-User-Id: <ID_DO_LEITOR_COMUM>"
   ```
   **Resultado Esperado**: HTTP `403 Forbidden` com payload `{"detail": "Acesso restrito a administradores."}`.

---

### Cenário 4: Suspensão de Conta e Encerramento Imediato de Sessões

1. Mantenha a conta `leitor_comum` logada na janela anônima.
2. Na janela do administrador em `/admin`, localize a linha de `leitor_comum`.
3. Clique na ação "Suspender Conta" e confirme no modal.
4. Na janela do `leitor_comum`, tente navegar ou clicar em qualquer recurso (ex.: abrir um livro).
5. **Resultado Esperado**:
   - Todas as sessões do usuário foram excluídas no banco.
   - A chamada de API falha com HTTP `401 Unauthorized` ("Usuário não autenticado ou inativo").
   - O leitor é desconectado e enviado para a tela de login.
   - Qualquer tentativa de novo login é recusada informando que a conta está suspensa.

---

### Cenário 5: Proteção contra Auto-Bloqueio e Extinção do Admin

1. Na tabela do painel administrativo, localize a linha da própria conta de administrador conectada (`admin_teste`).
2. O botão de "Suspender" deve estar desabilitado ou, se acionado via API direta, deve retornar `HTTP 400 Bad Request` ("Você não pode suspender sua própria conta de administrador.").
3. Tente alterar o papel de `admin_teste` para `user`:
4. **Resultado Esperado**: Como ele é o único admin ativo, a operação é terminantemente recusada com `HTTP 400 Bad Request` ("Não é possível rebaixar o único administrador ativo do sistema.").

---

### Cenário 6: Reativação de Conta

1. No painel administrativo, localize o `leitor_comum` suspenso.
2. Clique na ação "Reativar Conta" e confirme.
3. O status volta para "ativo".
4. Na janela anônima, o leitor volta a conseguir efetuar login normalmente.

---

## 3. Validação Automatizada de Regressão

Execute a suíte hermética completa:

```powershell
# Backend
cd backend
.venv\Scripts\python.exe -m pytest tests/test_admin_and_rbac.py

# Frontend
cd ../frontend
npm test
npm run build
```
