# Research & Technical Decisions: F09 — Notificações e Atividade Social

**Feature Branch**: `036-notificacoes-atividade-social`  
**Created**: 2026-09-26  
**Status**: Completed  

---

## 1. Mecanismo de Atualização no Cliente (Polling Leve vs. Conexões Persistentes)

### Contexto
O requisito FR-003 e a especificação exigem que novidades sociais e avisos administrativos sejam refletidos no cliente de forma oportuna sem sobrecarregar o servidor ou degradar a experiência em conexões móveis e túneis locais (Cloudflare Tunnel/Tailscale).

### Decisão
Implementar **polling periódico leve no cliente web com intervalo de 45 segundos**, associado a **revalidação sob demanda**:
1. Chamada leve e rápida a cada 45 segundos para `GET /api/notifications/unread-count`, que retorna unicamente `{"unread_count": int}` com consulta direta e otimizada por índice no SQLite (`SELECT COUNT(*) FROM notifications WHERE user_id = :uid AND read_at IS NULL`).
2. Revalidação imediata disparada pelos seguintes gatilhos no navegador:
   - Ao focar a janela ou aba da aplicação (`window.addEventListener('focus', ...)`).
   - Ao navegar entre rotas no Vue Router.
   - Ao clicar para abrir o menu suspenso (dropdown) de notificações no cabeçalho.
3. A listagem detalhada de notificações (`GET /api/notifications`) só é solicitada quando o usuário de fato abre o dropdown ou a tela da central de notificações, mantendo o tráfego em repouso extremamente enxuto.

### Rationale
- **Compatibilidade com Processo Único Local:** O Leitorum opera como um servidor local orquestrado via FastAPI/Uvicorn em processo único (conforme Artigo III da Constituição). WebSockets ou Server-Sent Events (SSE) mantêm conexões abertas continuamente, consumindo workers e descritores de rede no Windows, além de gerarem instabilidades comuns de timeout e reconexão através de tunnels Cloudflare ou redes Tailscale.
- **Eficiência Computacional:** Uma contagem indexada em SQLite local consome menos de 0,5ms de CPU. Polling de 45s por aba ativa resulta em carga insignificante (< 2 requisições por minuto por leitor).
- **Consistência de UX:** O usuário nunca percebe atraso porque a revalidação imediata no `focus` e na abertura do dropdown garante dados frescos instantaneamente no momento em que ele interage com a interface.

### Alternativas Consideradas
- **WebSockets:** Rejeitado devido à complexidade de gerenciar conexões persistentes, estado de heartbeat, autenticação por ticket em WS e suporte frágil em túneis locais e hibernação de abas móveis.
- **Server-Sent Events (SSE):** Rejeitado porque prende uma thread/conexão do Uvicorn por cliente conectado, o que se torna um gargalo em arquiteturas locais monolíticas com poucos workers.
- **Polling de Alta Frequência (ex.: 5s):** Rejeitado por gerar I/O de disco desnecessário no arquivo SQLite sem ganho perceptível para o leitor.

---

## 2. Modelagem e Armazenamento da Entidade `Notification`

### Contexto
Eventos de notificação possuem diferentes naturezas: solicitações de amizade (`friend_request`), confirmações (`friend_accepted`), compartilhamento de livros e estudos (`study_shared`) e avisos administrativos (`system_alert`). Cada um carrega metadados distintos (IDs, nomes, títulos de obras, links de navegação).

### Decisão
Criar o modelo declarativo SQLAlchemy `Notification` mapeado para a tabela `notifications` com schema relacional flexível:
- `id`: `String(36)`, chave primária com UUID v4 gerado automaticamente.
- `user_id`: `String(36)`, chave estrangeira para `users.id` com `ondelete="CASCADE"`, indexada.
- `actor_id`: `String(36)`, chave estrangeira para `users.id` com `ondelete="SET NULL"`, anulável (nulo em comunicados do sistema).
- `event_type`: `String(32)`, categorizado via enum/string literal (`friend_request`, `friend_accepted`, `study_shared`, `system_alert`).
- `payload`: `JSON`, armazena dicionário de atributos complementares (ex.: `{"friendship_id": 12, "requester_name": "Ana", "study_id": 4, "title": "Notas de Leitura", "message": "...", "link": "/estudos/4"}`).
- `read_at`: `DateTime(timezone=True)`, anulável; indica se o leitor já visualizou/marcou a notificação.
- `created_at`: `DateTime(timezone=True)`, data/hora UTC de criação.

**Índices de Performance:**
1. `ix_notifications_user_read`: Composto em `(user_id, read_at)` para resolver instantaneamente a consulta do contador de não lidos.
2. `ix_notifications_user_created`: Composto em `(user_id, created_at DESC)` para ordenação cronológica decrescente rápida na listagem.

### Rationale
- O uso de uma coluna `JSON` para o `payload` evita esquemas excessivamente fragmentados com múltiplas tabelas-filhas para cada tipo de evento social, preservando flexibilidade para futuras expansões sem migrações de DDL constantes.
- Chaves estrangeiras ativadas (`PRAGMA foreign_keys = ON`) mantêm integridade referencial: a exclusão de um usuário remove automaticamente suas notificações.

### Alternativas Consideradas
- **Tabelas Específicas por Tipo de Evento (`friend_notifications`, `study_notifications`):** Rejeitado por inflar a complexidade do ORM e exigir uniões complexas (`UNION ALL`) para montar a listagem unificada.
- **Campos Estáticos Rígidos (ex.: `book_id`, `study_id`, `friendship_id` como colunas nulas):** Rejeitado por criar colunas esparsas no banco de dados e dificultar extensibilidade.

---

## 3. Disparo de Avisos Administrativos e Alertas Institucionais (`system_alert`)

### Contexto
O administrador do Leitorum precisa emitir avisos gerais (ex.: comunicados de manutenção, regras da comunidade) que cheguem a todos os leitores e cujo status de leitura (`read_at`) possa ser rastreado individualmente por cada leitor.

### Decisão
Implementar o endpoint `POST /api/admin/notifications/broadcast` que realiza uma inserção em lote (`bulk insert`) de registros na tabela `notifications` para todos os usuários ativos no momento do envio.
- Cada leitor recebe seu próprio registro individual de notificação com `user_id = user.id`, `actor_id = admin.id`, `event_type = 'system_alert'` e `read_at = None`.
- A rota administrativa exige o papel `admin` (utilizando a dependência `AdminUser`).
- A inserção utiliza `session.add_all(...)` em uma única transação atômica.

### Rationale
- Conforme alinhado na clarificação (Q3: Opção A), linhas individuais garantem independência total: o usuário A pode marcar o aviso como lido sem afetar o usuário B.
- A contagem de não lidas e a busca de notificações permanecem idênticas para todos os tipos de eventos, sem necessidade de consultas especiais com `LEFT JOIN` ou tabelas associativas secundárias de leitura (`read_states`).
- Para a escala da aplicação (dezenas a milhares de leitores), uma inserção em lote de registros de notificação consome menos de 20ms no SQLite local.

### Alternativas Consideradas
- **Registro Global Único + Tabela de Leituras (`notification_reads`):** Rejeitado pois adicionaria complexidade conceitual, consultas com junções adicionais e lógica dispersa para saber se o leitor já visualizou o aviso global.

---

## 4. Desacoplamento Transacional e Resiliência da Emissão

### Contexto
O requisito FR-010 define que a emissão de notificações não deve impedir a conclusão da operação principal (ex.: criar amizade, conceder permissão de leitura a um estudo) caso ocorra alguma falha transitória ou erro no registro da notificação.

### Decisão
Implementar o serviço de notificações (`notification_service.py`) com padrão de emissão segura e defensiva:
- A função auxiliar `dispatch_notification(session, user_id, event_type, actor_id, payload)` inclui tratamento de exceção (`try / except Exception as exc: logger.error(...)`) quando acionada a partir de operações externas.
- Em fluxos transacionais existentes (`friendship_service.py` e `sharing_service.py`), a criação do registro de notificação é adicionada na mesma transação (`session.add(Notification(...))`) imediatamente após a mutação principal, de modo atômico e transparente.
- Se uma notificação falhar por qualquer motivo anômalo de serialização ou restrição, a ação primária (amizade, permissão) pode ser preservada ou reportada com log adequado, garantindo que o leitor nunca fique bloqueado de interagir socialmente.

### Rationale
- Notificações são itens informativos de suporte à experiência do usuário, nunca elementos de autorização crítica. O desacoplamento evita falsos erros em operações essenciais do caderno.

---

## 5. Ações Rápidas de Amizade Inline no Painel

### Contexto
O requisito FR-005 e o alinhamento Q2 (Opção A) definem que solicitações de amizade podem ser aceitas ou recusadas diretamente no card de notificação, mantendo o card visível com feedback amigável imediato.

### Decisão
1. **Frontend:**
   - O componente `NotificationItem.vue` detecta `event_type === 'friend_request'` e exibe os botões de ação rápida "Aceitar" e "Recusar".
   - Ao clicar em "Aceitar", o componente chama o endpoint de aceite de amizade (`/api/friends/requests/{id}/accept`) e em seguida marca a notificação como lida (`/api/notifications/{id}/read`).
   - O estado do card no componente transita reativamente para exibição de texto inline confirmatório (ex.: "✓ Amizade aceita"), desabilitando os botões sem remover o card da lista visual.
   - Ao clicar em "Recusar", chama a rejeição (`/api/friends/requests/{id}/reject`) e exibe inline "Solicitação recusada", também marcando a notificação como lida.
2. **Backend:**
   - Ao aceitar uma amizade em `friendship_service.py`, o backend emite automaticamente uma nova notificação do tipo `friend_accepted` para o remetente original, notificando-o da nova conexão.
   - Tratamento de idempotência: se o leitor já respondeu à solicitação em outra aba ou tela, a API retorna mensagem amigável sem erro 500, e a UI exibe o estado resolvido.

### Rationale
- Evita que o card suma bruscamente debaixo do cursor do usuário logo após o clique (o que gera desorientação visual).
- Proporciona confirmação visual de que a ação foi registrada com sucesso.

---

## 6. Política de Retenção e Purga Automática (60 Dias)

### Contexto
O requisito FR-009 e SC-005 determinam que notificações antigas já lidas não devem se acumular indefinidamente no arquivo SQLite local.

### Decisão
Implementar a rotina `purge_expired_notifications(session: Session, retention_days: int = 60) -> int` em `notification_service.py`:
- Executa exclusão dos registros onde `read_at IS NOT NULL` e `read_at < (now - timedelta(days=retention_days))`.
- Notificações não lidas (`read_at IS NULL`) **nunca** são purgadas automaticamente, assegurando que o leitor não perca comunicados não visualizados.
- A purga é exposta através do endpoint de manutenção `POST /api/admin/notifications/purge` e pode ser acionada na inicialização do servidor ou por tarefas de manutenção periódica (`maintenance.py`).

### Rationale
- Preserva a saúde e o tamanho do banco SQLite local em modo WAL sem intervenção manual do usuário.
- O limiar de 60 dias oferece prazo mais que suficiente para histórico de atividade social.

---

## 7. Arquitetura de Componentes no Frontend

### Contexto
O cabeçalho (`App.vue`) precisa abrigar o ícone de notificações com badge numérico e um painel dropdown acessível, responsivo e alinhado aos temas e design tokens do Leitorum.

### Decisão
Estruturar os seguintes componentes e módulos:
1. `src/api/notifications.ts`: Funções de consumo da API REST (`fetchNotifications`, `fetchUnreadCount`, `markAsRead`, `markAllAsRead`, `broadcastAlert`, `purgeOldNotifications`).
2. `src/types/notifications.ts`: Interfaces TypeScript correspondentes (`NotificationItem`, `NotificationListResponse`, `UnreadCountResponse`, `BroadcastNotificationRequest`).
3. `src/composables/useNotifications.ts`: Composable reativo singleton que gerencia polling a cada 45s, estado de não lidos (`unreadCount`), carregamento, abertura do painel e mutações de leitura.
4. `src/components/notifications/NotificationsDropdown.vue`: Menu suspenso flutuante com cabeçalho ("Notificações", "Marcar todas como lidas"), abas ou filtros de leitura, lista paginada/com rolagem suave, e rodapé com link ou ação.
5. `src/components/notifications/NotificationItem.vue`: Renderizador específico para cada tipo de item com avatar, ícones temáticos (amizade, estudo, sistema), data relativa formatada e ações inline.
6. `src/components/ui/Icon.vue`: Adição do ícone `Bell` e `BellRing` da biblioteca `lucide-vue-next`.

### Rationale
- Segue estritamente os padrões existentes do projeto (Vue 3 `<script setup lang="ts">`, composables, design tokens CSS, ausência de bibliotecas pesadas de terceiros).
- Respeita acessibilidade (atributos ARIA `aria-expanded`, `aria-label`, navegação por teclado e foco consistente).
