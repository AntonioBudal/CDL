# Research & Architectural Decisions: F06 — Sistema de Amizades

Este documento consolida as decisões técnicas, padrões de modelagem e arquitetura de segurança para a implementação da Feature 06 (Sistema de Amizades) no Caderno de Leitura.

---

## Decisão 1: Modelagem Relacional de Amizade (Par Ordenado Único Normalizado)

- **Decisão**: Utilizar uma única linha na tabela `friendships` para representar a conexão entre dois usuários, normalizando a ordem dos identificadores no momento da gravação (`user_id_a < user_id_b`).
- **Rationale**:
  - Em um banco de dados relacional (SQLite), armazenar duas linhas para uma mesma amizade (ex.: A->B e B->A) gera risco de inconsistência transacional, descompasso de status e duplicação desnecessária de índices.
  - A normalização com ordenação léxica de UUIDs garante que `(user_id_a, user_id_b)` seja sempre único através de uma restrição `UNIQUE(user_id_a, user_id_b)` e `CHECK(user_id_a != user_id_b)`.
  - A coluna `action_user_id` registra qual dos dois usuários originou o estado atual:
    - Se `status == 'pending'` e `action_user_id == user_id_a`: significa que `user_id_a` enviou a solicitação para `user_id_b`.
    - Se `status == 'pending'` e `action_user_id == user_id_b`: significa que `user_id_b` enviou a solicitação para `user_id_a`.
    - Se `status == 'accepted'`: ambos são amigos mútuos.
    - Se `status == 'blocked'`: o usuário identificado em `action_user_id` bloqueou o outro membro do par.
- **Alternativas consideradas**:
  - *Grafo Direcionado Duplo (duas linhas por amizade)*: Rejeitado por aumentar a complexidade de manutenção atômica no SQLite, duplicar registros e exigir lógica de sincronização contínua.
  - *Tabelas Separadas para Solicitações e Amizades*: Rejeitado por fragmentar o histórico e exigir migrações destrutivas de dados entre tabelas ao aceitar/rejeitar.

---

## Decisão 2: Blindagem Anti-Enumeração e Bloqueio Efetivo Bilateral

- **Decisão**: Toda consulta a perfil público (`GET /api/users/{username}`) e endpoints de recursos retorna `HTTP 404 Not Found` quando houver bloqueio entre as partes, e consultas de busca (`GET /api/users?q=...`) filtram sumariamente qualquer usuário com relação de bloqueio ativa.
- **Rationale**:
  - Retornar `HTTP 403 Forbidden` quando um usuário visita o perfil de quem o bloqueou confirma a existência do perfil e a presença do bloqueio, gerando atrito e incentivando tentativas de evasão.
  - O retorno `HTTP 404 Not Found` segue os padrões OWASP de blindagem anti-IDOR/anti-enumeração ("Deny by Default"), fazendo com que o bloqueador pareça simplesmente inexistente para o bloqueado.
  - Na busca de descobríveis, uma subconsulta `WHERE NOT EXISTS (SELECT 1 FROM friendships WHERE status = 'blocked' AND ...)` garante que o usuário bloqueado nunca apareça nos resultados.
- **Alternativas consideradas**:
  - *Retornar mensagem explícita "Você foi bloqueado"*: Rejeitado por violar privacidade e boas práticas de segurança defensiva.
  - *Bloqueio apenas na UI*: Rejeitado; a Constituição e as regras do projeto exigem autorização e blindagem rigorosamente no servidor.

---

## Decisão 3: Tratamento Atômico de Solicitações Cruzadas e Reenvio Pós-Recusa

- **Decisão**: 
  1. Se o usuário A enviar solicitação para B e já existir uma solicitação pendente inversa de B para A, o sistema converte a relação automaticamente para `accepted` em uma única transação atômica.
  2. Quando uma solicitação for recusada pelo destinatário ou cancelada pelo remetente, o registro é excluído fisicamente do banco (`DELETE`), retornando a relação ao estado neutro ("sem vínculo"), em conformidade com a decisão alinhada (Q1: A).
- **Rationale**:
  - A conversão atômica de solicitações cruzadas elimina conflitos de chave única e melhora a experiência do usuário (ambos queriam ser amigos simultaneamente).
  - A exclusão física de pendências canceladas/recusadas mantém o banco enxuto e elimina acúmulo de registros orfãos no SQLite.
  - O bloqueio permanece persistido para impedir reenvios abusivos quando necessário.
- **Alternativas consideradas**:
  - *Soft delete para pendências canceladas*: Rejeitado por onerar consultas com filtros adicionais sem benefício prático para os usuários.

---

## Decisão 4: Estrutura de Endpoints e Contratos REST (`/api/friends`)

- **Decisão**: Criar um módulo de rotas dedicado em `backend/app/routers/friends.py` sob o prefixo `/api/friends`.
- **Rationale**:
  - Mantém a modularidade do backend, isolando a lógica de relacionamentos de `users.py` (focado em contas/perfis) e `auth.py` (focado em credenciais e sessões).
  - Rotas canônicas:
    - `POST /api/friends/request/{username}` (envio de solicitação)
    - `POST /api/friends/accept/{request_id}` (aceite de solicitação)
    - `POST /api/friends/reject/{request_id}` (recusa de solicitação)
    - `DELETE /api/friends/cancel/{request_id}` (cancelamento de solicitação enviada)
    - `DELETE /api/friends/{username}` (encerramento de amizade ativa)
    - `POST /api/friends/block/{username}` (bloqueio de usuário)
    - `POST /api/friends/unblock/{username}` (desbloqueio de usuário)
    - `GET /api/friends` (lista de amigos aceitos)
    - `GET /api/friends/requests` (solicitações pendentes recebidas e enviadas)
    - `GET /api/friends/blocked` (lista de bloqueados)
- **Alternativas consideradas**:
  - *Incorporar no router `users.py`*: Rejeitado para evitar sobrecarga de responsabilidades em um único arquivo de rotas.

---

## Decisão 5: Interface do Usuário e Hub Social no Frontend

- **Decisão**: 
  1. Criação de rota dedicada `/amigos` em `frontend/src/views/FriendsView.vue` com 4 abas estruturadas: "Meus Amigos", "Solicitações", "Bloqueados" e "Descobrir Leitores".
  2. Inserção de link de primeiro nível na barra superior global em `frontend/src/App.vue` (visível para usuários autenticados).
  3. Adição de crachá numérico no menu indicando solicitações pendentes recebidas não respondidas.
  4. Integração de botão contextual no perfil público (`UserProfileCard.vue` e `UserProfileView.vue`) e nos cartões de busca para interagir diretamente ("Conectar", "Pendente", "Amigo", "Bloquear").
- **Rationale**:
  - Atende diretamente à deliberação do usuário (Q2: A).
  - Proporciona centralização ergonômica com foco em acessibilidade (alvos táteis de 44px e atributos WAI-ARIA para navegação por abas).
- **Alternativas consideradas**:
  - *Inserir dentro de Ajustes*: Descartado pela escolha do usuário na fase de especificação.
