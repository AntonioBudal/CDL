# Sync Flow & Concurrency Lifecycle

**Feature**: `031-sincronizacao-multidispositivo`  
**Date**: 2026-09-22  
**Status**: Completed  

Este documento descreve os fluxos de mensagens, transições de estado e protocolos de interação entre clientes desktop/móveis e o servidor central FastAPI.

---

## 1. Fluxo de Atualização com Controle Otimista de Concorrência (OCC)

### Cenário A: Atualização Sequencial Bem-Sucedida
Quando não há edições concorrentes, a gravação procede sem atrito e avança a versão.

```mermaid
sequenceDiagram
    autonumber
    actor Leitor
    participant Frontend as Cliente Web (Vue 3)
    participant API as FastAPI Central
    participant DB as SQLite WAL

    Leitor->>Frontend: Digita reflexões e clica "Salvar"
    Frontend->>API: PATCH /api/studies/10 { title, notes, expected_version: 3 }
    API->>DB: SELECT version FROM studies WHERE id = 10 AND user_id = :uid
    DB-->>API: version = 3
    API->>API: Valida: expected_version (3) == current_version (3) -> OK
    API->>DB: UPDATE studies SET title = :t, notes = :n, version = 4, updated_at = :now WHERE id = 10
    DB-->>API: 1 row affected
    API-->>Frontend: HTTP 200 OK { id: 10, version: 4, updated_at: :now, ... }
    Frontend->>Frontend: Atualiza versão local para 4 e limpa indicador de pendência
    Frontend-->>Leitor: Exibe estado "Salvo"
```

---

### Cenário B: Detecção de Conflito Concorrente e Diálogo de Resolução
Quando outro terminal salvou uma alteração prévia e o cliente tenta enviar versão defasada.

```mermaid
sequenceDiagram
    autonumber
    actor Leitor
    participant Celular as Smartphone (Tailscale)
    participant Desktop as PC Desktop
    participant API as FastAPI Central
    participant DB as SQLite WAL

    Note over Celular, Desktop: Ambos os terminais possuem Estudo 10 na versão 1
    Desktop->>API: PATCH /api/studies/10 { notes: "Nota do PC", expected_version: 1 }
    API->>DB: UPDATE studies SET version = 2 WHERE id = 10 AND version = 1
    API-->>Desktop: HTTP 200 OK (versão 2)

    Note over Celular: Leitor edita no celular e clica "Salvar"
    Celular->>API: PATCH /api/studies/10 { notes: "Nota do Celular", expected_version: 1 }
    API->>DB: SELECT version FROM studies WHERE id = 10
    DB-->>API: version = 2
    API->>API: Valida: expected_version (1) != current_version (2) -> CONFLITO!
    API-->>Celular: HTTP 409 Conflict { server_version: 2, server_updated_at, server_data: { notes: "Nota do PC" } }
    
    Note over Celular: Frontend NÃO apaga o rascunho local
    Celular->>Celular: Renderiza ConflictResolutionModal com comparação
    Leitor->>Celular: Escolhe "Sobrescrever com Rascunho Local"
    
    Celular->>API: PATCH /api/studies/10 { notes: "Nota do Celular", expected_version: 2 }
    API->>DB: UPDATE studies SET notes = "Nota do Celular", version = 3 WHERE id = 10 AND version = 2
    API-->>Celular: HTTP 200 OK (versão 3)
    Celular-->>Leitor: Confirmação de salvamento e fechamento do modal
```

---

## 2. Fluxo de Reconciliação Pós-Reconexão / Standby

Quando um celular volta de suspensão ou recupera sinal Wi-Fi/Tailscale:

```mermaid
sequenceDiagram
    autonumber
    participant SistemaOperacional as Dispositivo Móvel (OS)
    participant Composable as useSync.ts
    participant Cache as Repositório Local
    participant API as FastAPI Central

    SistemaOperacional->>Composable: Evento visibilitychange (visible) ou online
    Composable->>Composable: Verifica cooldown (mínimo 5s desde última requisição)
    Composable->>API: GET /api/sync/changes?since=2026-09-22T21:45:00Z
    
    API->>API: Consulta entidades do usuário com updated_at >= since ou deleted_at >= since
    API-->>Composable: HTTP 200 OK { server_time, updated: { books, studies, canvas_nodes, preferences }, deleted: { book_ids, study_ids } }
    
    Composable->>Cache: Aplica remoção de itens em deleted
    Composable->>Cache: Atualiza entidades em updated (se formulário ativo não estiver em edição)
    Composable->>Composable: Armazena server_time como novo ponteiro since
    Composable->>Composable: Transiciona status para "Sincronizado"
```

---

## 3. Matriz de Estados do Indicador de Sincronização

| Estado | Significado | Ação do Usuário | Ícone / Feedback Visual |
| :--- | :--- | :--- | :--- |
| `IDLE_SYNCED` | Todos os dados locais estão persistidos e idênticos ao servidor. | Nenhuma ação necessária. | Nuvem neutra estática ou discreto "Sincronizado". |
| `SYNCING` | Requisição de envio ou reconciliação ativa em andamento. | Aguardar brevemente. | Ícone de atualização em rotação suave. |
| `OFFLINE` | Dispositivo sem rede ou servidor local do PC inacessível. | Leitura liberada; edições são retidas localmente. | Nuvem cortada "Offline — dados retidos". |
| `CONFLICT` | Resposta `HTTP 409` recebida; divergência detectada. | Decidir no modal de resolução. | Alerta visual chamando atenção ao formulário. |
