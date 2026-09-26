# Research & Architectural Decisions: F07 — Compartilhamento e Permissões por Recurso (ACL)

Este documento consolida as decisões técnicas, padrões de modelagem, arquitetura de autorização e contratos de interface para a implementação da Feature 07 (Compartilhamento e Permissões por Recurso - ACL) no Caderno de Leitura.

---

## Decisão 1: Modelo Relacional de Visibilidade e ACL Multinível

- **Decisão**: 
  1. Adicionar coluna `visibility` nas tabelas `books` (`VARCHAR(20)`, padrão `'private'`) e `studies` (`VARCHAR(20)`, padrão `'inherit'`).
  2. Criar a tabela relacional `resource_permissions` para gerenciar concessões nominais (modo `custom`).
- **Rationale**:
  - A abordagem híbrida (coluna de visibilidade para regras gerais + tabela de ACL para concessões granulares nominais) é o padrão da indústria (similar ao Google Drive / GitHub) para sistemas de permissão eficientes.
  - No caso de `books`, os valores canônicos são `'private'`, `'friends'` e `'public'`.
  - No caso de `studies`, o valor padrão `'inherit'` cumpre a decisão alinhada (Q1: A), herdando a visibilidade do livro ao qual o estudo pertence, enquanto permite ao leitor definir sobrescritas (`override`) específicas: `'private'`, `'friends'`, `'custom'` ou `'public'`.
  - A tabela `resource_permissions` armazena `(resource_type, resource_id, granted_to_user_id, can_view, created_at)` com restrição `UNIQUE` composta e índices de busca rápida.
- **Alternativas consideradas**:
  - *Tabela de ACL para todos os acessos*: Rejeitado por demandar criação e atualização de milhares de linhas individuais de permissão sempre que uma obra for compartilhada com amigos ou publicamente, degradando o desempenho no SQLite local.
  - *Visibilidade puramente binária (público/privado)*: Rejeitado por não atender à granularidade requerida no Roadmap 0.5 (amigos, customizado e público).

---

## Decisão 2: Resolução de Acesso, Herança e Blindagem Anti-Enumeração

- **Decisão**: 
  - Centralizar a avaliação de permissão de leitura em `sharing_service.py` via funções puras e determinísticas `can_read_study(session, user_id, study)` e `can_read_book(session, user_id, book)`.
  - Qualquer tentativa de consulta a recurso privado, não compartilhado ou de autor bloqueado retorna estritamente `HTTP 404 Not Found`.
- **Rationale**:
  - Se o usuário solicitante for o proprietário (`resource.user_id == user_id`), o acesso é concedido imediatamente.
  - Se houver relação de bloqueio mútuo ou unilateral entre os usuários (F06), o acesso é negado incondicionalmente.
  - Para estudos com `visibility == 'inherit'`, a resolução consulta a visibilidade do livro correspondente.
  - Retornar `HTTP 404 Not Found` em vez de `403 Forbidden` quando o recurso não estiver visível impede que atacantes ou terceiros descubram a existência de títulos, notas confidenciais ou IDs de outros leitores ("Deny by Default" / OWASP Anti-Enumeration).
  - Em conformidade com a decisão Q3: A, recursos configurados como `public` exigem que o requisitante seja um usuário autenticado no sistema.
- **Alternativas consideradas**:
  - *Permitir visitantes anônimos nos links públicos*: Descartado por escolha explícita do usuário (Q3: A) para preservar a governança do servidor local e auditoria de acesso.
  - *Lógica de autorização dispersa dentro dos routers*: Rejeitado por gerar duplicação de regras e risco de brechas de segurança.

---

## Decisão 3: Blindagem Irrestrita de Somente-Leitura (Read-Only) em Camada Dupla

- **Decisão**: Garantir que convidados possuam acesso exclusivamente de leitura, tanto no backend quanto no frontend:
  1. **No Backend**: Todos os endpoints de mutação (`POST /api/studies`, `PATCH /api/studies/{id}`, `DELETE /api/studies/{id}`, adição de notas, tags, conexões no canvas ou relações entre estudos) validam rigidamente que `current_user.id == study.user_id`. Se não for o proprietário, a mutação é abortada com `HTTP 403 Forbidden` (ou `404`).
  2. **No Frontend**: A visualização de estudo compartilhado (`StudyView.vue`) detecta se o leitor ativo não é o proprietário, exibindo cabeçalho de modo leitura ("Estudo compartilhado por @autor"), ocultando todos os botões de ação destrutiva/edição e bloqueando atalhos de teclado.
- **Rationale**:
  - O Roadmap 0.5 define categoricamente que o compartilhamento é estritamente Read-Only.
  - Previne qualquer risco de corrupção ou conflito de concorrência em anotações alheias.
- **Alternativas consideradas**:
  - *Permissão de comentários ou anotações conjuntas*: Fora de escopo para a versão 0.5.

---

## Decisão 4: Localização e Experiência do Leitor na Interface (Aba "Compartilhados Comigo")

- **Decisão**: 
  - Adicionar na tela da Biblioteca (`LibraryView.vue`) um seletor de visualização com abas: **"Meu Acervo"** e **"Compartilhados Comigo"**, em consonância com a resposta do usuário (Q2: A).
  - Em "Compartilhados Comigo", exibir cartões dos estudos/livros aos quais o leitor tem acesso, agrupados ou filtráveis por autor (`@username`), livro e data de compartilhamento.
  - No leitor de estudos e nas listagens, disponibilizar o botão de ação rápida "Compartilhar", que abre o componente `ShareModal.vue`.
- **Rationale**:
  - Mantém a ergonomia unificada no ambiente do Acervo, onde o leitor já realiza suas buscas e filtragens habituais.
  - O `ShareModal.vue` fornece alternância fluida entre os modos (`Privado`, `Herdar do Livro`, `Amigos`, `Personalizado`, `Público`), permitindo copiar link com 1 clique e gerenciar permissões nominais com alvos táteis mínimos de 44px.
- **Alternativas consideradas**:
  - *Criar página separada no menu superior*: Rejeitado para não poluir a barra de navegação global.
  - *Colocar no Hub Social (/amigos)*: Descartado na clarificação (Q2: B preterida em favor de Q2: A).

---

## Decisão 5: Estrutura de Endpoints REST e Módulo `sharing.py`

- **Decisão**: 
  - Criar o router `backend/app/routers/sharing.py` sob o prefixo `/api/shared` para consultas de recursos compartilhados, e endpoints em `/api/studies/{id}/permissions` e `/api/books/{id}/permissions` para gestão da ACL pelo proprietário.
  - Rotas canônicas:
    - `GET /api/shared/studies`: Lista estudos compartilhados com o usuário atual (paginado e filtrável).
    - `GET /api/shared/books`: Lista livros compartilhados com o usuário atual.
    - `GET /api/studies/{id}/permissions`: Retorna a configuração de visibilidade e lista de permissões ativas (apenas proprietário).
    - `PUT /api/studies/{id}/visibility`: Altera o modo de visibilidade do estudo (apenas proprietário).
    - `POST /api/studies/{id}/permissions`: Concede acesso nominal para `@username` (apenas proprietário).
    - `DELETE /api/studies/{id}/permissions/{user_id}`: Revoga acesso nominal de um usuário (apenas proprietário).
- **Rationale**:
  - Desacopla as responsabilidades de autorização e compartilhamento social do núcleo CRUD de estudos, facilitando testes e manutenção.
