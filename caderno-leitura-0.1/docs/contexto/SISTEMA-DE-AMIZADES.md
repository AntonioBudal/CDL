# Arquitetura do Sistema de Amizades e Interações Sociais

Este documento consolida a arquitetura técnica, as decisões de design e as regras de governança social implementadas na **Feature 06 — Sistema de Amizades (F06)** (versão 0.5) do Caderno de Leitura.

---

## 1. Visão Geral e Princípios Fundamentais

A funcionalidade de Amizades introduz o tecido social e relacional entre leitores da plataforma, preservando a intimidade reflexiva, a privacidade rigorosa e a segurança contra enumeração ou assédio:

1. **Par Ordenado Normalizado (`user_id_a < user_id_b`)**:
   - Cada relacionamento entre dois usuários é estritamente único no banco de dados, independentemente de quem disparou a ação primeiro.
   - Os identificadores UUID são normalizados alfabeticamente na persistência via `Friendship.normalize_pair()`.
   - Uma constraint de chave única `uq_friendships_pair` e constraints `CHECK` garantem no próprio motor SQLite que não possam coexistir registros duplicados nem auto-amizades reflexivas.

2. **Blindagem Bilateral Anti-Enumeração (HTTP 404)**:
   - Quando o usuário A bloqueia o usuário B, qualquer tentativa de B de acessar o perfil público de A (`GET /api/users/{username}`) ou de enviar solicitações retorna `404 Not Found` (simulando a inexistência da conta).
   - Usuários bloqueados são excluídos imediatamente dos resultados de buscas descobríveis (`GET /api/users?q=...`) em ambas as direções.
   - O bloqueador não revela a existência do bloqueio, impedindo vazamento de dados de moderação e proteção pessoal.

3. **Neutralidade da Recusa e Soberania do Bloqueio (Decisão Q1: A)**:
   - A recusa de uma solicitação de amizade (`POST /api/friends/reject/{request_id}`) encerra a pendência e restaura a relação ao estado neutro ("sem vínculo"), permitindo novo envio futuro pelo remetente.
   - Caso o leitor deseje impedir novos envios e interações de forma definitiva, deve acionar a função soberana de **Bloqueio** (`POST /api/friends/block/{username}`).

4. **Confidencialidade da Lista Nominal de Amigos (Decisão Q3: A)**:
   - No perfil público de um leitor (`/@username`), é exposto unicamente o contador quantitativo consolidado (`friends_count`, ex.: "5 amigos").
   - A listagem nominal detalhada de amigos é estritamente privada, visível exclusivamente ao próprio titular através do Hub Social.

5. **Resolução Atômica de Solicitações Cruzadas Simultâneas**:
   - Se o usuário A solicita amizade a B e, antes de aceitar, o usuário B também solicita amizade a A, o sistema detecta a intenção mútua e converte a relação atomicamente para `accepted` ("Vocês agora são amigos!"), evitando exceções de duplicidade.

---

## 2. Modelo de Dados Relacional (`Friendship`)

A tabela `friendships` modela os relacionamentos entre usuários do sistema:

```sql
CREATE TABLE friendships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id_a VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    user_id_b VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    action_user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_friendships_pair UNIQUE (user_id_a, user_id_b),
    CONSTRAINT ck_friendships_ordered_pair CHECK (user_id_a < user_id_b),
    CONSTRAINT ck_friendships_no_self CHECK (user_id_a != user_id_b)
);

CREATE INDEX ix_friendships_user_id_a ON friendships (user_id_a);
CREATE INDEX ix_friendships_user_id_b ON friendships (user_id_b);
CREATE INDEX ix_friendships_action_user_id ON friendships (action_user_id);
CREATE INDEX ix_friendships_status_action ON friendships (status, action_user_id);
```

### Papéis das Colunas
- `user_id_a`, `user_id_b`: Identificadores únicos dos usuários, normalizados (`user_id_a < user_id_b`).
- `status`: Estado canônico do vínculo relacional (`pending`, `accepted`, `blocked`).
- `action_user_id`: Usuário que disparou a transição de estado mais recente (essencial para desambiguar quem enviou a solicitação ou quem efetuou o bloqueio).

---

## 3. Máquina de Estados e Perspectiva Relacional

Do ponto de vista da persistência, o estado do registro é um dos valores canônicos: `pending`, `accepted` ou `blocked` (ou inexistente, indicando `none`).
Do ponto de vista da interface com o usuário conectado (`CurrentUser`), o status é projetado em uma perspectiva orientada à ação:

| Estado Canônico | Autor da Ação (`action_user_id`) | Perspectiva do Usuário Conectado | Ação Disponível na UI |
|---|---|---|---|
| Inexistente | — | `none` | Botão "Conectar" / "Bloquear" |
| `pending` | Usuário conectado | `pending_sent` | "Solicitação enviada" / Botão "Cancelar" |
| `pending` | Outro usuário | `pending_received` | Botões "Aceitar" / "Recusar" |
| `accepted` | Qualquer parte | `friends` | Indicador "Amigos" / "Desfazer amizade" |
| `blocked` | Usuário conectado | `blocked_by_me` | Indicador "Bloqueado" / "Desbloquear" |
| `blocked` | Outro usuário | `blocked_by_them` | Blindagem 404 (oculto / inexistente) |

---

## 4. Endpoints da API REST (`/api/friends` e `/api/users`)

Todas as rotas de mutação executam `commit_changes(session)` para garantir durabilidade no banco local SQLite (modo WAL).

### Gestão do Ciclo de Vida
- `POST /api/friends/request/{username}`: Envia solicitação ou resolve solicitação cruzada.
- `POST /api/friends/accept/{request_id}`: Aceita solicitação pendente recebida.
- `POST /api/friends/reject/{request_id}`: Recusa solicitação recebida (remove registro, retorna a `none`).
- `DELETE /api/friends/cancel/{request_id}`: Cancela solicitação pendente enviada.
- `DELETE /api/friends/{username}`: Desfaz amizade ativa de forma soberana para ambas as partes.
- `POST /api/friends/block/{username}`: Bloqueia leitor a partir de qualquer estado.
- `POST /api/friends/unblock/{username}`: Remove bloqueio prévio, retornando a `none`.

### Consultas e Listagens Sociais
- `GET /api/friends`: Lista amizades aceitas do usuário conectado com data `since`.
- `GET /api/friends/requests`: Lista solicitações pendentes separadas em `received` e `sent`.
- `GET /api/friends/blocked`: Lista usuários bloqueados pelo titular.
- `GET /api/friends/summary`: Retorna contadores consolidados (`friends_count`, `pending_received_count`, `pending_sent_count`) para badges de navegação em tempo real.
- `GET /api/friends/status/{username}`: Consulta status relacional pontual sob a perspectiva do usuário conectado.
- `GET /api/users?q=...`: Busca de usuários descobríveis, excluindo usuários bloqueados em qualquer direção.
- `GET /api/users/{username}`: Retorna perfil público com `friends_count` e aplica blindagem 404 se bloqueado.

---

## 5. Interface com o Usuário e Hub Social (`/amigos`)

O frontend oferece um espaço centralizado para comunidade leitora, estruturado em 4 abas acessíveis (conforme decisão Q2: A):

1. **Aba "Meus Amigos"**:
   - Grid de cartões de leitores amigos com avatar, nome, handle, data de amizade e botões contextuais compactos.
   - Estado vazio acolhedor incentivando a busca por novos leitores.

2. **Aba "Solicitações"**:
   - Seção de solicitações recebidas com botões primários táteis para "Aceitar" ou "Recusar".
   - Seção de solicitações enviadas com opção de "Cancelar".

3. **Aba "Descobrir Leitores"**:
   - Barra de pesquisa integrada com debounce de 300ms conectada a `searchUsers`.
   - Exibição de bio, dados públicos e botão dinâmico "Conectar".

4. **Aba "Bloqueados"**:
   - Lista de usuários bloqueados pelo titular com data do bloqueio e botão acessível de "Desbloquear".

### Acessibilidade e Ergonomia Móvel
- **Alvos Táteis de 44px**: Todos os botões e elementos interativos respeitam a altura mínima de 44px em conformidade com as diretrizes WAI-ARIA para telas sensíveis ao toque.
- **WAI-ARIA Completo**: Atributos `role="tablist"`, `role="tab"`, `role="tabpanel"`, `aria-selected` e `aria-controls` garantem navegação fluida por teclado e leitores de tela.
- **Zero Emojis**: Todo o vocabulário visual e textual adota iconografia vetorial Lucide SVG e linguagem sóbria.
- **Crachá de Pendências**: Notificação numérica visual no cabeçalho global quando há solicitações pendentes recebidas.

---

## 6. Cobertura de Testes Automatizados

A funcionalidade foi homologada com cobertura exaustiva ponta a ponta:
- **Backend (`pytest backend/tests`)**: 284 testes aprovados sem falhas, incluindo 8 cenários específicos de isolamento relacional, concorrência, recusa neutra, solicitações cruzadas, desfazimento, auto-bloqueio proibido, blindagem anti-enumeração (404) e persistência de migrações Alembic.
- **Frontend (`npm test`)**: 230 testes unitários e de integração aprovados, validando conformidade de tipos, composable reativo `useFriends`, integridade do router, semântica WAI-ARIA e ausência de emojis.
- **Compilação de Produção**: `vue-tsc -b && vite build` concluído com sucesso sem erros de tipagem.
