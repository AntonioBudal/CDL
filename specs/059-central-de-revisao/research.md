# Research & Technical Decisions: F 0.7.10 — Central de Revisão de Perguntas e Clozes

**Feature**: F 0.7.10 — Central de Revisão de Perguntas e Clozes  
**Branch**: `059-central-de-revisao`  
**Date**: 2026-10-04  

---

## Decisões Técnicas Principais

### D1: Reutilização da Tabela `study_highlights` vs Nova Tabela de Flashcards

- **Decisão**: Estender a tabela existente `study_highlights` adicionando colunas leves (`last_reviewed_at`, `review_count`, `last_rating`), sem criar tabelas paralelas de cartões ou perguntas.
- **Racional**:
  1. No Leitorum, perguntas e termos ocultos (clozes) já são instâncias consolidadas de `study_highlights` (`kind='question'` e `kind='hidden'`).
  2. Criar uma tabela intermediária redundante de flashcards geraria descompasso de sincronização caso o leitor edite o texto ou apague um destaque no estudo original.
  3. Com colunas adicionais em `study_highlights`, qualquer alteração no estudo reflete imediatamente no acervo de revisão com integridade referencial nativa via chave estrangeira `study_id`.
- **Alternativas Consideradas**:
  - *Tabela independente `review_cards`*: Rejeitada por duplicação de dados, necessidade de sincronização bidirecional complexa e risco de orfandade de dados.
  - *Armazenar metadados de revisão em JSON nos metadados do estudo*: Rejeitada por inviabilizar indexação eficiente em banco relacional e consultas agregadas rápidas.

---

### D2: Algoritmo de Fila de Revisão: Prioridade Inteligente Simples vs SRS Prematuro

- **Decisão**: Adotar ordenação heurística relacional simples no banco de dados SQLite baseada em `last_reviewed_at`, `review_count` e `last_rating`, sem implementar algoritmos matemáticos densos (SuperMemo SM-2, FSRS) nesta etapa.
- **Racional**:
  1. A priorização obedece à regra aprovada (Q1 = A):
     - Prioridade 1: Itens nunca revisados (`review_count = 0` ou `last_reviewed_at IS NULL`).
     - Prioridade 2: Itens classificados como "Difícil" (`last_rating = 'hard'`) com intervalo decorrido.
     - Prioridade 3: Itens revisados há mais tempo (`last_reviewed_at ASC`).
  2. Essa heurística é 100% resolvida via SQL simples (`ORDER BY CASE ...`), proporcionando performance instantânea (< 5ms) mesmo com milhares de destaques no SQLite local.
  3. Previne over-engineering e complexidade matemática antes que o leitor construa o hábito de revisão diária.
- **Alternativas Consideradas**:
  - *SuperMemo SM-2 / Anki SRS*: Rejeitada temporariamente. Requer campos como fator de facilidade (EF), intervalos calculados e máquina de estados densa, violando o princípio YAGNI para a v0.7.
  - *Ordem puramente cronológica ou aleatória*: Rejeitadas por não priorizarem as fragilidades cognitivas reais do leitor.

---

### D3: Tamanho da Rodada de Revisão e Ergonomia Cognitiva

- **Decisão**: Fila estruturada em blocos padrão de 10 itens por rodada com opção de continuar ("Revisar mais 10" ou "Revisar todos os itens").
- **Racional**:
  1. Conforme clarificação aprovada (Q2 = A), blocos de 10 itens reduzem a barreira de entrada psicológica (estudos rápidos de 3 a 5 minutos), evitando cansaço mental e fadiga por decisão.
  2. No mobile, sessões curtas são ideais para o uso no transporte ou pausas breves.
  3. Permite uma tela de encerramento de ciclo frequente que recompensa o esforço e consolida métricas parciais.
- **Alternativas Consideradas**:
  - *Fila infinita sem paradas*: Gera ansiedade de fila acumulada ("backlog infinito") e desestimula a volta ao aplicativo.
  - *Lote rígido de 20*: Pode ser excessivo para leituras diárias curtas.

---

### D4: Unificação de Formatos e Pílulas de Filtro Rápido

- **Decisão**: Apresentar na rota `/review` uma fila unificada de perguntas e termos ocultos (clozes) por padrão, com pílulas de filtro no topo para isolar tipos (`Todos`, `Perguntas`, `Termos Ocultos`).
- **Racional**:
  1. Conforme clarificação aprovada (Q3 = A), ambos os formatos compartilham o mesmo princípio neurocognitivo: recuperação ativa da memória (Active Recall).
  2. A experiência unificada oferece variedade dinâmica ao leitor, enquanto os seletores de tipo permitem sessões monotemáticas caso o leitor deseje apenas perguntas abertas.
- **Alternativas Consideradas**:
  - *Dois hubs completamente separados*: Fragmentaria a interface e exigiria navegações desnecessárias entre menus.

---

### D5: Atalhos de Teclado Universais e Alvos Móveis de 44px

- **Decisão**: Mapear atalhos globais de teclado no desktop (`Barra de Espaço` para alternar revelação; `1`, `2`, `3` para *Difícil*, *Médio*, *Fácil*) com proteção contra digitação acidental em inputs, e alvos táteis mínimos de $44 \times 44$px no mobile.
- **Racional**:
  1. No desktop, a velocidade de revisão com uma única mão sobre o teclado (`Espaço` com o polegar e `1`/`2`/`3` com os dedos indicadores) maximiza o estado de fluxo.
  2. Atributos WAI-ARIA com `aria-live="polite"` garantem que leitores de tela anunciem a resposta revelada e a mudança de card sem desorientação.
- **Alternativas Consideradas**:
  - *Apenas cliques de mouse*: Reduziria a velocidade média de revisão no desktop em mais de 50%.
