# Arquitetura de Compartilhamento e Permissões por Recurso (ACL)

Este documento consolida a arquitetura técnica, as regras de segurança, o modelo de dados e as decisões de design implementadas na **Feature 07 — Compartilhamento e Permissões por Recurso (ACL)** (versão 0.5) do Caderno de Leitura.

---

## 1. Visão Geral e Princípios Fundamentais

A funcionalidade de Compartilhamento e ACL por Recurso permite que o leitor decida com quem deseja compartilhar suas produções intelectuais, notas e estudos de livros, garantindo segurança de ponta a ponta e respeito à intimidade editorial:

1. **Compartilhamento Estritamente Read-Only para Convidados**:
   - Convidados e leitores autorizados recebem permissão exclusiva de leitura e navegação (`read`).
   - Mutações de escrita (`PATCH`, `DELETE`, reordenação, inserção de nós no canvas, anotações de leitura e mudanças de status) são estritamente proibidas para convidados, retornando incondicionalmente `403 Forbidden` ("Acesso somente leitura").

2. **Blindagem Anti-Enumeração Rigorosa (OWASP "Deny by Default" / HTTP 404)**:
   - Recursos privados ou estudos para os quais o leitor não possua concessão válida retornam invariavelmente `404 Not Found` (simulando a inexistência do registro).
   - Isso impede que usuários mal-intencionados descubram títulos de estudos, livros ou a existência de IDs por enumeração.

3. **Herança de Visibilidade com Sobrescrita Explícita (Decisão Q1: A)**:
   - Estudos adotam por padrão a visibilidade `'inherit'`, herdando a visibilidade configurada no livro associado ao capítulo.
   - O leitor proprietário pode sobrescrever a visibilidade de qualquer estudo individualmente para `'private'`, `'friends'`, `'custom'` ou `'public'`.

4. **Acesso Restrito a Usuários Autenticados (Decisão Q3: A)**:
   - Mesmo para estudos e livros marcados como `'public'`, o acesso requer sessão autenticada ativa. Usuários anônimos recebem `401 Unauthorized`, resguardando o ambiente de scraping indiscriminado.

5. **Integração e Supressão Soberana de Bloqueios (F06)**:
   - Se existir uma relação de bloqueio bilateral ativa entre o proprietário e outro usuário, o sistema bloqueia qualquer visualização de estudos (mesmo públicos), retornando invariavelmente `404 Not Found`.
   - Usuários bloqueados são excluídos de qualquer concessão nominal de ACL (`400 Bad Request`) e suprimidos de todos os feeds de busca e listagem compartilhada.

6. **Central de Estudos Compartilhados na Biblioteca (Decisão Q2: A)**:
   - A Biblioteca (`BooksView.vue`) possui um alternador de abas semântico `[ Meu Acervo | Compartilhados Comigo ]`, permitindo explorar estudos de outros leitores sem poluir a visão do acervo pessoal.

---

## 2. Modelo de Dados Relacional

A arquitetura de permissões é suportada pela adição de colunas de visibilidade e pela tabela relacional `resource_permissions`:

```sql
-- Coluna de visibilidade em livros ('private', 'friends', 'public')
ALTER TABLE books ADD COLUMN visibility VARCHAR(20) NOT NULL DEFAULT 'private';

-- Coluna de visibilidade em estudos ('inherit', 'private', 'friends', 'custom', 'public')
ALTER TABLE studies ADD COLUMN visibility VARCHAR(20) NOT NULL DEFAULT 'inherit';

-- Tabela de concessões nominais (ACL Granular)
CREATE TABLE resource_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_type VARCHAR(20) NOT NULL, -- 'study' ou 'book'
    resource_id INTEGER NOT NULL,
    granted_to_user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    permission_level VARCHAR(20) NOT NULL DEFAULT 'read',
    granted_by_user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_resource_permission UNIQUE (resource_type, resource_id, granted_to_user_id),
    CONSTRAINT chk_resource_type CHECK (resource_type IN ('study', 'book')),
    CONSTRAINT chk_permission_level CHECK (permission_level IN ('read'))
);

CREATE INDEX ix_resource_permissions_resource ON resource_permissions (resource_type, resource_id);
CREATE INDEX ix_resource_permissions_granted ON resource_permissions (granted_to_user_id);
```

### Migração Alembic
A migração `0017_add_sharing_and_permissions.py` aplica as alterações de forma declarativa e com verificação de compatibilidade bidirecional com o SQLite local.

---

## 3. Matriz de Níveis de Visibilidade

| Modo | Escopo de Leitura | Requisitos de Acesso | Herança |
|---|---|---|---|
| `inherit` (Estudos) | Adota a visibilidade do livro associado | Depende do `visibility` do livro | Sim |
| `private` | Apenas o leitor proprietário | `user_id == owner_id` | Não |
| `friends` | Proprietário + Amigos com vínculo aceito (F06) | Amizade mútua ativa (`accepted`) | Não |
| `custom` | Proprietário + Leitores nominados na ACL | Concessão expressa em `resource_permissions` | Não |
| `public` | Qualquer leitor autenticado na plataforma | Sessão autenticada ativa | Não |

---

## 4. Núcleo de Autorização e Serviço (`sharing_service.py`)

O serviço centralizado encapsula as regras de verificação e concessão de acesso:

- `resolve_effective_visibility(session, study)`: Avalia a visibilidade efetiva do estudo, resolvendo a herança através do livro pai se o estudo estiver como `'inherit'`.
- `can_read_study(session, study, user_id)`:
  1. Retorna `True` imediatamente se `user_id == study.user_id`.
  2. Verifica relação de bloqueio bilateral; se bloqueado, retorna `False`.
  3. Resolve a visibilidade efetiva:
     - `public`: Retorna `True` para qualquer usuário autenticado.
     - `friends`: Consulta `friendship_service.are_friends(owner_id, user_id)`.
     - `custom`: Consulta se existe registro em `resource_permissions`.
     - `private`: Retorna `False`.
- `grant_permission(session, resource_type, resource_id, owner_id, target_username)`:
  - Valida soberania do proprietário.
  - Verifica inexistência de bloqueio bilateral.
  - Insere ou atualiza atomicamente a concessão nominal na tabela de permissões.
- `revoke_permission(session, resource_type, resource_id, owner_id, target_user_id)`:
  - Remove a concessão nominal da tabela de permissões.
- `get_shared_studies_for_user(session, user_id, q, author, limit, offset)`:
  - Consulta unificada que agrega:
    1. Estudos públicos de terceiros.
    2. Estudos de amigos configurados com visibilidade `'friends'`.
    3. Estudos com concessão nominal individual na tabela `resource_permissions`.
  - Exclui estudos descartados na lixeira (`discarded_at IS NOT NULL`).
  - Suprime incondicionalmente qualquer estudo de autores que estejam em relação de bloqueio com o usuário solicitante.

---

## 5. Endpoints REST da API

### Modificação de Visibilidade (Proprietário)
- `PUT /api/studies/{id}/visibility`: Altera o nível de visibilidade do estudo (`inherit`, `private`, `friends`, `custom`, `public`).
- `PUT /api/books/{id}/visibility`: Altera o nível de visibilidade do livro (`private`, `friends`, `public`).

### ACL Granular Nominal (Modo Custom)
- `GET /api/studies/{id}/permissions`: Retorna a visibilidade efetiva e a lista de leitores autorizados.
- `POST /api/studies/{id}/permissions`: Concede permissão de leitura nominal via `username` (ex: `{"username": "leitor_amigo"}`).
- `DELETE /api/studies/{id}/permissions/{user_id}`: Revoga a permissão nominal de um leitor.

### Feeds de Recursos Compartilhados
- `GET /api/shared/studies?q=...&author=...&limit=50&offset=0`: Retorna estudos compartilhados com o leitor conectado com paginação e filtros.
- `GET /api/shared/books`: Retorna livros que contenham estudos compartilhados acessíveis ao leitor.

---

## 6. Camada de Apresentação e Ergonomia Visual

### 1. `ShareModal.vue`
- Modal flutuante centrado com acessibilidade completa (`role="dialog"`, `aria-modal="true"`, `aria-labelledby`).
- Radiogroup acessível para seleção instantânea de visibilidade.
- Bloco de cópia de link direto com feedback visual ("Copiado!").
- No modo `'custom'`, expõe campo de concessão nominal por `@username` e lista de leitores convidados com ação de revogação imediata em 1 clique.
- Cumpre os parâmetros ergonômicos com alvos táteis mínimos de 44x44px.

### 2. `StudyView.vue`
- Quando acessado pelo proprietário: exibe botão "Compartilhar", acionando `ShareModal.vue`, e atalhos completos de edição e lixeira.
- Quando acessado por convidado (`can_edit == false`):
  - Exibe **Banner de Somente Leitura** informando o autor do estudo com crachá e `@username`.
  - Oculta os botões "Editar estudo", "Mover para a lixeira" e "Compartilhar".
  - Desativa o seletor interativo de status de leitura (`StudyStatusBadge`).
  - Torna a lista de conexões e relações somente-leitura (`StudyRelationsList`).

### 3. `BooksView.vue` & `SharedStudiesList.vue`
- Alternador de abas WAI-ARIA no topo do acervo (`[ Meu Acervo | Compartilhados Comigo ]`).
- Cartões ricos de estudo com avatar do autor, nome de exibição, `@username`, título do livro, capítulo e data da última atualização.
- Busca textual integrada e filtro específico por autor.
- Estados vazios, esqueletos de carregamento (`animate-pulse`) e mensagens de erro sem emojis informais, respeitando as regras tipográficas do Caderno de Leitura.

---

## 7. Garantias de Qualidade e Conformidade

- **Backend**: Suíte hermética em `backend/tests/test_sharing_and_permissions.py` cobrindo as 4 User Stories (MVP, ACL customizada, feed compartilhado e blindagem anti-bloqueio) com 100% de sucesso.
- **Frontend**: Suíte `frontend/tests/sharing.test.mjs` validando contratos de tipos, métodos de API, conformidade WAI-ARIA, alvos de toque de 44px e ausência de emojis informais.
- **Ecossistema**: Integração completa aprovada com 293 testes de backend (`pytest`), 240 testes de frontend (`npm test`) e tipagem estrita via `vue-tsc -b && vite build`.
