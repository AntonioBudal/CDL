# Research & Architectural Decisions: F0.7.14 — Sessões Estruturadas de Estudo e Auditoria de Aprendizado

**Feature**: F0.7.14 — Sessões Estruturadas de Estudo e Auditoria de Aprendizado  
**Branch**: `063-sessoes-estudo`  
**Date**: 2026-10-10  

---

## 1. Contexto e Objetivos

O Caderno de Leitura já conta com a **Central de Revisão** (F0.7.10) e a **Biblioteca de Highlights e Anotações** (F0.7.11), nas quais o leitor pode revisar destaques e cartões de active recall isoladamente. No entanto, o ato de estudar ainda era atomizado: o leitor não possuía uma delimitação de bloco de estudo (com começo, meio, fim, ritmo e contagem de tempo), nem um histórico auditável de sessões cumpridas.

A feature **F0.7.14** preenche essa lacuna com:
1. **Configuração de Escopo**: Escolha flexível entre Sessão Rápida (10 itens), Sessão por Livro/Capítulo ou Todos os Pendentes.
2. **Ambiente Imersivo de Foco**: Modo de tela limpa sem menus laterais ou cabeçalhos globais dispersivos, com barra de progresso horizontal (`Item 3 de 10`) e atalhos táteis/teclado.
3. **Persistência Atômica e Resiliente**: Registro individual de cada cartão avaliado no banco, garantindo que interrupções não causem perda de trabalho cognitivo.
4. **Encerramento Triunfante e Auditoria**: Painel de encerramento com métricas consolidadas (tempo, acertos/dificuldades, retenção) e histórico retrospectivo solene.

---

## 2. Decisões Arquiteturais

### D1: Modelagem de Dados e Migração Alembic `0028_add_study_sessions_tables.py`
- **Problema**: Como estruturar a persistência de sessões sem sobrecarregar a tabela de destaques nem criar concorrência indesejada?
- **Decisão**: Criar duas tabelas dedicadas:
  - `study_sessions`:
    - `id` (INTEGER, PK, autoincrement)
    - `user_id` (VARCHAR(36), FK para `users.id`, indexado, obrigatório)
    - `book_id` (INTEGER, FK para `books.id`, nullable, indexado — quando filtrado por obra específica)
    - `scope_type` (VARCHAR(30), ex.: `'quick'`, `'book'`, `'all'`)
    - `status` (VARCHAR(20), default `'in_progress'`: `'in_progress'`, `'completed'`, `'interrupted'`)
    - `started_at` (DATETIME UTC, obrigatório)
    - `completed_at` (DATETIME UTC, nullable)
    - `total_items` (INTEGER, total de itens configurados no lote)
    - `completed_items` (INTEGER, total de itens efetivamente avaliados)
    - `easy_count` (INTEGER, default 0)
    - `medium_count` (INTEGER, default 0)
    - `hard_count` (INTEGER, default 0)
    - `duration_seconds` (INTEGER, tempo de estudo acumulado)
    - `created_at`, `updated_at` (DATETIME UTC)
  - `study_session_items`:
    - `id` (INTEGER, PK, autoincrement)
    - `session_id` (INTEGER, FK para `study_sessions.id`, cascade delete, indexado)
    - `highlight_id` (INTEGER, FK para `study_highlights.id`, indexado)
    - `rating` (VARCHAR(20), `'easy'`, `'medium'`, `'hard'`)
    - `time_spent_seconds` (INTEGER, default 0)
    - `answered_at` (DATETIME UTC)
- **Justificativa**: Garante normalização limpa, auditoria item a item e integridade relacional.

---

### D2: Atualização Atômica de Repetição Espaçada e Resiliência
- **Problema**: O que acontece quando o leitor avalia um cartão durante a sessão?
- **Decisão**: 
  1. Cada avaliação chama `POST /api/study-sessions/{id}/items` imediatamente.
  2. O backend registra a resposta em `study_session_items` e simultaneamente atualiza o destaque em `study_highlights` (novo carimbo `last_reviewed_at`, próximo agendamento `next_review_at` e avanço do estágio de revisão).
  3. Se o leitor fechar a janela, o que já foi respondido não precisa ser repetido.
  4. Se a sessão for cancelada pelo leitor, a rota `POST /api/study-sessions/{id}/interrupt` fecha a sessão como `'interrupted'`.

---

### D3: Ajuste de Escopo Dinâmico (Q2: A)
- **Problema**: O leitor solicita lote rápido de 10 itens para um livro que possui apenas 4 itens pendentes.
- **Decisão**:
  - O endpoint de início `POST /api/study-sessions/start` consulta os destaques pendentes para o livro.
  - Se a quantidade pendente for menor que 10, o sistema inicia a sessão imediatamente com o número de itens disponíveis (ex.: 4 itens), configurando `total_items = 4`.
  - O frontend exibe no cabeçalho de progresso: *"Item 1 de 4 (todos os pendentes deste livro)"*.
  - Elimina diálogos de bloqueio e atritos na experiência.

---

### D4: Interface Imersiva e Ergonomia Visual
- **Problema**: Manter o leitor imerso sem quebrar a identidade visual nem perder atalhos de acessibilidade.
- **Decisão**:
  - Nova rota `/estudo/sessao/:sessionId` montada em `frontend/src/views/StudySessionView.vue`.
  - Cabeçalho minimalista `SessionProgressHeader.vue` contendo apenas:
    - Indicador de item (`Item X de Y`) e barra de progresso horizontal suave.
    - Cronômetro sutil em formato `MM:SS`.
    - Botão de saída segura com confirmação tátil/teclado (`Esc`).
  - Cartão de estudo centralizado com foco no texto, resposta oculta/revelada e opções táteis amplas:
    - Fácil (`1` ou tecla `F`)
    - Médio (`2` ou tecla `M`)
    - Difícil (`3` ou tecla `D`)
    - Espaço para revelar resposta.
  - Modal de resumo final triunfante `SessionSummaryModal.vue`.

---

### D5: Filosofia Editorial e Sem Gamificação Infantil
- **Problema**: Evitar sons espalhafatosos, confetes ou placares competitivos.
- **Decisão**:
  - O encerramento adota estética solene: métricas tipográficas limpas, elogio sutil à constância intelectual, resumo de tempo e retorno convidativo ao acervo.
  - Alinhamento pleno à Constituição do Leitorum (Zero Emojis, privacidade absoluta, foco no texto).
