# Notificações e Atividade Social — Arquitetura e Decisões Técnicas

## 1. Visão Geral

A feature **F09 — Notificações e Atividade Social** implementa a central unificada de eventos assíncronos e atividade social da plataforma Leitorum. Através de um indicador visual no cabeçalho com polling adaptativo leve (45s) e um painel dropdown acessível, os leitores recebem e respondem instantaneamente a interações sociais, permissões de compartilhamento e alertas institucionais.

---

## 2. Decisões Arquiteturais e de Produto

1. **Estratégia de Atualização (Polling Leve + Revalidação no Foco)**:
   - Polling a cada 45s consultando o endpoint ultraleve `GET /api/notifications/unread-count` (executa apenas `SELECT count(id)` indexado).
   - Revalidação imediata disparada ao focar na janela/aba (`window.focus`), navegar entre rotas ou clicar para abrir o dropdown de notificações.
   - Preservação da simplicidade da aplicação local/processo único sem complexidade de WebSockets persistentes ou Redis.

2. **Ações Rápidas de Amizade com Feedback Inline**:
   - Os cards de notificação do tipo `friend_request` incluem botões "Aceitar" e "Recusar" diretamente no dropdown.
   - Ao clicar, o card exibe confirmação inline imediata ("Amizade aceita" / "Solicitação recusada") e persiste a ação sem fechar ou fazer sumir o card de forma abrupta, garantindo clareza e previsibilidade cognitiva.
   - O aceite de amizade gera automaticamente uma notificação reversa `friend_accepted` para o solicitante.

3. **Compartilhamento Transparente**:
   - Concessões nominais de acesso a estudos e livros (F07) geram notificações automáticas `study_shared` com títulos canônicos e links diretos para leitura imediata.

4. **Alertas Institucionais e Manutenção Preventiva**:
   - Administradores autenticados podem disparar comunicados em massa (`system_alert`) via `POST /api/admin/notifications/broadcast`, criando registros individuais para todos os usuários ativos com severidade configurável (`info`, `warning`, `critical`).
   - Política de retenção automática: notificações lidas com mais de 60 dias são purgadas periodicamente no ciclo de vida (`lifespan`), por endpoint administrativo e pelo CLI de manutenção (`python -m app.services.maintenance purgar-notificacoes`).

---

## 3. Modelo de Dados

Tabela: `notifications`

| Coluna | Tipo | Descrição |
|---|---|---|
| `id` | VARCHAR(36) | Chave primária UUIDv4 |
| `user_id` | VARCHAR(36) | Destinatário da notificação (FK `users.id` CASCADE) |
| `actor_id` | VARCHAR(36) | Autor que originou o evento (FK `users.id` SET NULL, opcional) |
| `event_type` | VARCHAR(32) | Tipo de evento (`friend_request`, `friend_accepted`, `study_shared`, `system_alert`) |
| `payload` | JSON | Metadados contextuais (título, mensagem, link, severidade, IDs de recurso) |
| `read_at` | DATETIME | Data/hora UTC de leitura (`NULL` indica não lida) |
| `created_at` | DATETIME | Data/hora UTC de emissão do evento |

### Índices de Alta Performance:
- `ix_notifications_user_read`: `(user_id, read_at)` — viabiliza contagem de não lidos em sub-milissegundos.
- `ix_notifications_user_created`: `(user_id, created_at DESC)` — otimiza listagem paginada e ordenação cronológica.

---

## 4. Endpoints da API

- `GET /api/notifications` — Listagem paginada de notificações do usuário autenticado (suporta filtro `unread_only=true`).
- `GET /api/notifications/unread-count` — Retorna apenas a contagem numérica `{ "unread_count": N }`.
- `PATCH /api/notifications/{notification_id}/read` — Marcação individual idempotente como lida.
- `POST /api/notifications/read-all` — Marca todas as notificações pendentes como lidas em lote.
- `POST /api/admin/notifications/broadcast` — Emissão em massa de aviso do sistema (exclusivo para administradores).
- `POST /api/admin/notifications/purge` — Purga administrativa de notificações lidas antigas (exclusivo para administradores).

---

## 5. Acessibilidade e Interface

- O botão disparador do cabeçalho implementa `aria-haspopup="dialog"`, `:aria-expanded="open"` e `:aria-label` dinâmico.
- O painel dropdown possui `role="region"`, `tabindex="-1"`, fecha com a tecla `Escape` ou clique externo, e estrutura a lista em `role="feed"`.
- As abas de filtro ("Todas" / "Não lidas") seguem o padrão WAI-ARIA `role="tablist"` e `role="tab"`.
- Alvos de clique de botões de ação e marcação de leitura respeitam o mínimo de 44x44px.
- Zero uso de emojis informais, respeitando as diretrizes estéticas e o teste `visual_system.test.mjs`.
