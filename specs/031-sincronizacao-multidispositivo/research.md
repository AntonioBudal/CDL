# Research: Sincronização Multidispositivo

**Feature**: `031-sincronizacao-multidispositivo`  
**Date**: 2026-09-22  
**Status**: Completed  

---

## 1. Contexto e Problema

O Caderno de Leitura (CDL) evoluiu na versão 0.5 para suportar múltiplos usuários e autenticação robusta (local e Google GIS). Com a introdução do acesso móvel via Tailscale HTTPS, o leitor frequentemente intercala sessões de estudo entre o computador principal (desktop) e o smartphone (celular).

### Desafios Identificados
1. **Perda de Dados por Sobrescrita Cega (Lost Updates):** Se o usuário faz uma alteração no celular durante o trajeto e posteriormente edita o mesmo estudo no PC sem recarregar a tela, a escrita posterior do PC pode apagar inadvertidamente as anotações do celular se não houver controle de concorrência.
2. **Desconexão Intermitente e Standby Móvel:** Aparelhos celulares entram frequentemente em modo de economia de energia / standby, suspendendo conexões WebSocket ou timers de polling contínuo.
3. **Ergonomia Espacial Diferenciada:** O Canvas 2D foi projetado primariamente para monitores desktop ultrawide. Telas verticais de smartphone possuem proporções e resoluções radicalmente diferentes.
4. **Isolamento de Dados no SQLite WAL:** O banco opera localmente com leitor único/múltiplo e escritor serializado. O modelo de sincronização deve ser leve e transacional sem demandar servidores de mensageria adicionais (ex.: Redis/RabbitMQ).

---

## 2. Decisões Técnicas Principais

### Decisão 1: Controle de Concorrência Otimista (OCC) com Versão Numérica Monotônica
- **Abordagem:** Toda entidade mutável (`Study`, `Book`, etc.) recebe uma coluna `version: int` (iniciando em 1, incrementada a cada `UPDATE` bem-sucedido) e `updated_at: datetime` em UTC.
- **Protocolo de Atualização:**
  - Requisições `PATCH` ou `PUT` transmitem o campo `expected_version: int`.
  - O banco de dados realiza verificação atômica: se `entity.version != expected_version`, a transação é abortada e a API responde `HTTP 409 Conflict`.
  - O payload da resposta `HTTP 409` traz os dados completos da versão vigente no servidor (`server_version`, `updated_at`, campos de texto), permitindo ao cliente comparar as versões ou forçar a sobrescrita.
- **Mecânica de Sobrescrita:** Quando o usuário clica expressamente em "Sobrescrever com rascunho local", o frontend reenvia o payload informando `expected_version = server_version`. A transação grava os dados do usuário e avança o contador para `server_version + 1`.

### Decisão 2: Feed Incremental de Mudanças Baseado em Timestamps (`Change Feed`)
- **Abordagem:** Endpoint `GET /api/sync/changes?since=<iso_timestamp>`.
- **Rastreamento de Exclusões:** Utiliza a coluna `deleted_at` já existente em `studies` e `books` (implementada na Feature 003 — Lixeira e Soft Delete). Registros com `deleted_at IS NOT NULL` e `deleted_at >= since` são retornados no array de exclusões (`deleted: { study_ids: [...], book_ids: [...] }`).
- **Particionamento:** A resposta divide os dados em:
  - `updated`: entidades criadas ou modificadas após o instante `since` (`updated_at >= since` e `deleted_at IS NULL`).
  - `deleted`: identificadores de entidades excluídas após `since`.
  - `server_time`: carimbo temporal emitido pelo servidor no fuso UTC para ser usado na próxima consulta `since`.

### Decisão 3: Persistência e Sincronização Centralizada de Preferências do Leitor
- **Abordagem:** Criação da tabela `user_preferences` associada a `users.id` (`1:1`).
- **Campos Sincronizados:**
  - `active_superclass` (string: zero-g, mecanica, invisivel, dimensional, monolitica).
  - `superclass_intensity` (float: 0.0 a 2.0).
  - `preferred_view_mode` (string: grid, list, tree, canvas, cockpit).
  - `tree_collapsed_state` (JSON string de IDs de estudos recolhidos).
  - `font_family` (string: garamond, sans, dyslexic).
  - `font_scale` (float: 0.8 a 1.4).
  - `theme_mode` (string: dark, light, e-ink).
- **Desacoplamento de Zoom/Pan:** As coordenadas espaciais relativas dos cartões (`study_canvas_nodes` x, y) são sincronizadas no backend. Todavia, a câmera (zoom e deslocamento de pan da lousa) é armazenada exclusivamente no `localStorage` de cada dispositivo, respeitando a ergonomia física da tela local.

### Decisão 4: Ciclo de Vida Reativo e Gatilhos de Reconciliação no Frontend
- **Abordagem:** O composable `useSync.ts` orquestra as sincronizações de forma declarativa e econômica:
  - Evento `window.addEventListener('online')`: dispara reconciliação imediata quando a conectividade é restabelecida.
  - Evento `document.addEventListener('visibilitychange')`: quando `visibilityState === 'visible'` (o leitor desbloqueia o celular ou retorna à aba do navegador), agenda reconciliação suave.
  - Evento `window.addEventListener('focus')`: verifica se o último carimbo `server_time` possui mais de 30 segundos; em caso afirmativo, consulta o feed de alterações.
  - Prevenção de tempestade de requisições: mecanismo de debounce / cooldown mínimo de 5 segundos entre consultas de reconciliação automática.

---

## 3. Avaliação de Riscos e Mitigações

| Risco | Impacto | Mitigação |
| :--- | :--- | :--- |
| **Conflito de concorrência com perda de digitação** | Alto | O frontend intercepta `409` e preserva integralmente o rascunho em memória e no componente; nunca limpa campos do formulário na ocorrência de erro. |
| **Divergência de relógio (Clock Skew) entre PC e Celular** | Médio | O cliente nunca utiliza seu relógio local como parâmetro de consulta; utiliza sempre o `server_time` retornado pelo backend na resposta anterior. |
| **Vazamento de dados entre leitores** | Crítico | Todas as consultas a `studies`, `books`, `canvas_nodes` e `user_preferences` filtram estritamente por `user_id = current_user.id` no servidor. |
| **Trava de banco de dados SQLite sob escritas simultâneas** | Baixo | Modo WAL com `PRAGMA busy_timeout = 5000` (5 segundos) configurado em `session.py`, serializando transações sem bloquear leitores. |
