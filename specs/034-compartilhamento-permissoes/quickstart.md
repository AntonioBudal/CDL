# Quickstart & Guia de Validação: F07 — Compartilhamento e Permissões por Recurso (ACL)

Este guia orienta a validação end-to-end dos cenários de teste da Feature 07 utilizando bancos descartáveis temporários e o cliente de testes da aplicação.

---

## 1. Pré-Requisitos e Ambiente de Teste

- Python 3.13 com o ambiente virtual ativo (`backend/.venv`).
- Node.js 24+ para a suíte de testes de frontend e build.
- **Banco de Produção Blindado**: O banco ativo `backend/data/caderno.db` **NUNCA** é tocado. Todos os comandos abaixo utilizam bancos efêmeros (`tmp_path`).

---

## 2. Cenários Automatizados de Teste (Backend)

Os testes automatizados de backend são implementados em `backend/tests/test_sharing_and_permissions.py`:

```bash
# Execução da suíte dedicada da Feature 07:
.\backend\.venv\Scripts\python -m pytest backend/tests/test_sharing_and_permissions.py -v
```

### Casos de Teste Validados:
1. **`test_visibility_defaults`**: Livros são criados com `private` e estudos com `inherit`.
2. **`test_friends_visibility_access`**:
   - Estudo com visibilidade `friends` é acessível para amigos aceitos (200 OK com `can_edit=False`).
   - Usuários estranhos recebem 404.
3. **`test_custom_visibility_and_acl`**:
   - Proprietário define `custom` e concede acesso a `@amigo_b`.
   - `@amigo_b` lê com sucesso (200 OK).
   - `@amigo_c` (amigo, mas fora da ACL) recebe 404.
   - Proprietário revoga `@amigo_b`; `@amigo_b` passa a receber 404 imediatamente.
4. **`test_blocked_user_cannot_access_public_or_friends`**:
   - Bloqueio unilateral entre leitor A e B garante que B recebe 404 ao tentar ler qualquer estudo de A, mesmo que público.
5. **`test_read_only_mutations_blocked`**:
   - Convidado tenta fazer `PATCH /api/studies/{id}` ou `DELETE` e recebe `403 Forbidden` ou `404`.
6. **`test_shared_studies_feed`**:
   - `GET /api/shared/studies` retorna a lista paginada dos estudos que foram compartilhados com o usuário atual.

---

## 3. Validação do Frontend (Vue 3 / TypeScript)

```bash
# Testes unitários do frontend (node:test):
npm test

# Verificação estrita de tipos e compilação do bundle:
npm run build
```

### Casos de Teste de Frontend (`frontend/tests/sharing.test.mjs`):
1. **`ShareModal.vue`**:
   - Abertura com foco correto e atributos acessíveis WAI-ARIA (`role="dialog"`).
   - Alternância entre visibilidades e exibição do campo de busca de `@username` quando `custom`.
   - Botão de cópia de link com confirmação visual.
2. **Aba "Compartilhados Comigo" na Biblioteca (`LibraryView.vue`)**:
   - Alternância fluida entre "Meu Acervo" e "Compartilhados Comigo".
   - Cartões com visualização clara do autor (`@username`), livro e capítulo.
3. **Modo Leitura Convidado (`StudyView.vue`)**:
   - Ocultação rigorosa dos botões de edição, salvar e exclusão para estudos de terceiros.
   - Presença do banner informativo de modo somente-leitura.

---

## 4. Roteiro de Verificação Manual (Navegador PC e Celular)

1. Inicie o servidor: `.\INICIAR-REDE.cmd`.
2. **Conta A (PC)**:
   - Abra um estudo qualquer e clique no botão **"Compartilhar"**.
   - Defina a visibilidade como **"Amigos"** ou **"Personalizado"** (adicionando `@leitor_b`).
   - Copie o link do estudo.
3. **Conta B (Celular / Janela Anônima)**:
   - Acesse a Biblioteca e clique na aba **"Compartilhados Comigo"**. O estudo de A deve estar listado com o crachá do autor.
   - Clique para abrir: confirme que o texto está perfeito, com a superclasse visual do leitor, banner de somente-leitura ativo e sem opções de edição.
