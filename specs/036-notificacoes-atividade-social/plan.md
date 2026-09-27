# Implementation Plan: F09 — Notificações e Atividade Social

**Branch**: `036-notificacoes-atividade-social` | **Date**: 2026-09-26 | **Spec**: [specs/036-notificacoes-atividade-social/spec.md](specs/036-notificacoes-atividade-social/spec.md)

**Input**: Feature specification from `specs/036-notificacoes-atividade-social/spec.md`

---

## Summary

Implementar a Central de Notificações e Atividade Social (F09) do Leitorum, integrando um centro de eventos unificado que conecta solicitações de amizade (`friend_request`), confirmações (`friend_accepted`), concessões de compartilhamento de estudos/livros (`study_shared`) e avisos administrativos institucionais (`system_alert`) diretamente à interface do leitor.

A solução técnica baseia-se em:
1. Modelo relacional `Notification` com payload flexível JSON e índices compostos de contagem e data no SQLite local.
2. Polling leve de contagem a cada 45 segundos (`GET /api/notifications/unread-count`) com revalidação sob demanda ao focar a janela, navegar ou abrir o painel.
3. Ações rápidas de amizade diretamente no card com feedback inline imediato ("✓ Amizade aceita" / "Solicitação recusada") sem remoção abrupta da lista.
4. Desacoplamento transacional via `notification_service.py` para garantir que falhas em notificações nunca impeçam a conclusão da ação principal.
5. Emissão em lote de alertas administrativos para usuários ativos e rotina de purga periódica para notificações lidas com mais de 60 dias.

---

## Technical Context

**Language/Version**: Python 3.13 (64-bit) no Windows (Backend) / TypeScript 5.3 + Vue 3 (Frontend)  
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0, Alembic, Uvicorn, Pydantic v2 (Backend); Vue 3 (Composition API), Vite, Lucide Vue Next, Pinia (Frontend)  
**Storage**: SQLite 3 local em modo Write-Ahead Logging (WAL) com chaves estrangeiras ativas (`PRAGMA foreign_keys = ON`)  
**Testing**: Pytest com bancos SQLite efêmeros em diretórios temporários (`tmp_path`) e portas de rede efêmeras (Backend); Vitest + @vue/test-utils (Frontend)  
**Target Platform**: Windows 10/11 local (processo único orquestrado via `iniciar.py`), servindo redes locais/Tailscale e acesso web responsivo (PC e dispositivos móveis)  
**Project Type**: Aplicação Web Full-Stack com API REST e SPA empacotada  
**Performance Goals**: Obtenção do contador de não lidos em menos de 10ms no SQLite; renderização da central de notificações em menos de 300ms no cliente  
**Constraints**: Não utilizar bibliotecas pesadas de mensageria externa (RabbitMQ, Redis, Celery); isolamento estrito contra o banco de dados de produção (`backend/data/caderno.db`) durante testes; respeitar contratos de caminhos e charset UTF-8  
**Scale/Scope**: Centenas a milhares de notificações por usuário com purga automática a cada 60 dias; escala típica de leitor individual, famílias e círculos de leitura  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Artigo Constitucional | Conformidade | Justificativa / Mecanismo de Garantia |
| :--- | :--- | :--- |
| **I. Proteção do Acervo e Privacidade** | **PASS** | As notificações contêm apenas metadados relacionais e identificadores sintéticos. Textos completos de anotações e conteúdos privados nunca são expostos. A autorização é checada por `current_user.id` em todas as rotas (anti-enumeração com 404). |
| **II. Isolamento Estrito de Testes** | **PASS** | Todas as suítes de testes (`test_notifications.py`) utilizam fixtures com `tmp_path` e bancos SQLite em memória/temporários. O banco de produção `backend/data/caderno.db` não é tocado sob nenhuma hipótese. |
| **III. Fidelidade Arquitetural** | **PASS** | Utiliza estritamente a stack ratificada: FastAPI, SQLAlchemy 2.0, Alembic, Vue 3, Vite, Lucide Vue Next, sem adição de servidores externos de fila ou bancos adicionais. |
| **IV. Governança por SDD** | **PASS** | Ciclo formal respeitado: `speckit.specify` concluído com checklist 100%, `speckit.clarify` alinhado (Q1: Polling 45s, Q2: Ação rápida inline, Q3: Linhas individuais para alertas de sistema), avançando agora no `speckit.plan`. |
| **V. Resiliência Operacional e Migrações** | **PASS** | Nova migração Alembic para a tabela `notifications` sem alterações destrutivas em tabelas existentes. Emissão desacoplada com proteção `try/except` para não interromper a transação principal. |

---

## Project Structure

### Documentation (this feature)

```text
specs/036-notificacoes-atividade-social/
├── plan.md              # Este plano de implementação técnica
├── research.md          # Decisões de pesquisa da Fase 0 (polling 45s, JSON payload, desacoplamento)
├── data-model.md        # Especificação da entidade Notification, índices e schemas Pydantic
├── quickstart.md        # Roteiro de validação ponta a ponta e testes automatizados
├── contracts/           # Contratos de interface OpenAPI
│   └── notifications-api.yaml
└── tasks.md             # Tarefas atômicas geradas na Fase 2 (/speckit-tasks)
```

### Source Code

```text
caderno-leitura-0.1/
├── backend/
│   ├── alembic/
│   │   └── versions/
│   │       └── xxxx_create_notifications_table.py
│   ├── app/
│   │   ├── models/
│   │   │   ├── notification.py               # Novo modelo SQLAlchemy Notification
│   │   │   └── __init__.py                   # Registro do modelo Notification
│   │   ├── schemas/
│   │   │   ├── notification.py               # Schemas Pydantic v2 de entrada e saída
│   │   │   └── __init__.py
│   │   ├── services/
│   │   │   ├── notification_service.py       # Lógica de negócio, contagem, emissão e purga
│   │   │   ├── friendship_service.py         # Disparo de friend_request e friend_accepted
│   │   │   ├── sharing_service.py            # Disparo de study_shared ao conceder permissão
│   │   │   └── admin_service.py              # Integração de avisos institucionais em massa
│   │   ├── routers/
│   │   │   ├── notifications.py              # Endpoints /api/notifications/*
│   │   │   ├── admin.py                      # Endpoint /api/admin/notifications/broadcast e purge
│   │   │   └── __init__.py
│   │   └── main.py                           # Registro do router de notificações na aplicação FastAPI
│   └── tests/
│       └── test_notifications.py             # Testes de integração do ciclo de vida de notificações
│
└── frontend/
    └── src/
        ├── types/
        │   ├── notifications.ts              # Tipos TypeScript para notificações e respostas da API
        │   └── types.ts                      # Atualização do mapa de ícones (adição de bell)
        ├── api/
        │   └── notifications.ts              # Funções de integração HTTP com /api/notifications
        ├── composables/
        │   └── useNotifications.ts           # Composable reativo: polling 45s, estado, badge, leitura
        ├── components/
        │   ├── ui/
        │   │   └── Icon.vue                  # Adição do ícone Bell de lucide-vue-next
        │   └── notifications/
        │       ├── NotificationsDropdown.vue # Dropdown de notificações com cabeçalho, abas e rodapé
        │       └── NotificationItem.vue      # Card individual com avatar, ícones e ações inline
        ├── App.vue                           # Inclusão do sino de notificações com badge no cabeçalho
        └── __tests__/
            ├── useNotifications.spec.ts      # Testes unitários do composable de notificações
            └── NotificationsDropdown.spec.ts # Testes de montagem e interação do componente dropdown
```

**Structure Decision**: Web application padrão do repositório, dividida em `backend/` (FastAPI/SQLAlchemy) e `frontend/` (Vue 3/Vite), respeitando integralmente a árvore de arquivos e padrões arquiteturais vigentes do Leitorum.

---

## Complexity Tracking

> **Não foram identificadas violações ou desvios constitucionais que requeiram justificativa.** Todas as decisões técnicas adotam as abordagens mais simples e canônicas recomendadas para o projeto (SQLite local, polling leve, processos integrados sem filas externas).
