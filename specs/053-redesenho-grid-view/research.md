# Research: F 0.7.4 — Redesenho da Grid View: Reconhecimento Visual e Cartografia de Leitura

**Feature**: F 0.7.4 — Redesenho da Grid View  
**Status**: Completed  
**Artifact**: `research.md`

---

## Decisões Técnicas e Arquiteturais

### D1: Agregação em Lote de Métricas Analíticas no Backend (`highlights_count` e `relations_count`)

- **Decisão**: Calcular as contagens de destaques e relações sem incorrer no problema de N+1 queries utilizando duas consultas agrupadas em lote (`GROUP BY`) com `IN (study_ids)`.
- **Racional**:
  - Para um capítulo com 20 estudos, realizar 20 subqueries individuais degradaria a latência da rota.
  - A abordagem em lote executa exatamente 2 consultas auxiliares (`StudyHighlight` agrupado por `study_id` e `StudyRelation` agrupado por `source_study_id` / `target_study_id`).
  - Ambas as tabelas possuem índices em suas chaves estrangeiras (`ix_study_highlights_study_id`, `ix_study_relations_source_target`).
  - No SQLite local, a execução combinada ocorre em menos de 1.5ms.
- **Alternativas consideradas**:
  - *Colunas desnormalizadas de contagem na tabela `studies`:* Rejeitada para evitar complexidade de sincronização e triggers em um modelo de dados simples.
  - *Subqueries correlacionadas em linha no SELECT principal:* Rejeitada porque a contagem de relações precisa avaliar tanto ponta de origem quanto destino, tornando o SELECT complexo.

---

### D2: Geração e Apresentação da Prévia Tipográfica Analítica (`summary_preview`)

- **Decisão**: O backend provê o campo `summary_preview: str` normalizado com até 240 caracteres, priorizando `summary` e caindo em fallback para `explanation`. O frontend renderiza o bloco com fonte serifada/editorial e controle estrito de quebra via CSS `-webkit-line-clamp: 2` (ou 3 em telas amplas).
- **Racional**:
  - Satisfaz a decisão de clarificação Q2: Opção A.
  - Corta espaços em branco e quebras de linha excessivas na origem, economizando payload JSON.
  - Se ambos os campos forem vazios, o campo retorna string vazia `""` e o frontend oculta a caixa de texto harmoniosamente sem deixar buracos verticais.
- **Alternativas consideradas**:
  - *Enviar o texto completo de `summary` e `explanation` para todos os estudos do capítulo:* Ineficiente para capítulos longos com fichamentos extensos.
  - *Truncamento exclusivo no frontend:* Rejeitada pois exigiria trafegar milhares de caracteres analíticos desnecessariamente na listagem de índice.

---

### D3: Identidade Cromática Editorial e Micro-Badges de Status

- **Decisão**: Cada cartão recebe um friso vertical de 4px na borda esquerda (`border-left: 4px solid var(--status-border)`), acompanhado do `StudyStatusBadge.vue` interativo no cabeçalho.
- **Racional**:
  - Satisfaz a decisão de clarificação Q1: Opção A.
  - Cria um ritmo visual agradável na varredura periférica dos olhos na grade: o leitor distingue imediatamente estudos concluídos (verde) de estudos em andamento (âmbar) ou rascunhos (cinza).
  - Alinha-se perfeitamente aos princípios das superclasses estéticas existentes no sistema (Invisível, Monolítica, Mecânica, Dimensional, Zero-G).
- **Alternativas consideradas**:
  - *Cabeçalho tonal com fundo preenchido:* Rejeitada por gerar ruído visual excessivo quando muitos cartões estão agrupados.

---

### D4: Estrutura dos Skeleton Screens para Transição Estável

- **Decisão**: Implementar templates de *Skeleton Screens* animados que reproduzem exatamente a geometria, margens e proporção dos cartões da grade (cabeçalho, 2 linhas de título, bloco de prévia analítica e rodapé com 2 micro-indicadores).
- **Racional**:
  - Elimina saltos de layout (*Cumulative Layout Shift - CLS*) durante o carregamento de capítulos com múltiplos estudos.
  - Transmite sensação de alta performance mesmo ao alternar rapidamente entre capítulos na barra lateral.
- **Alternativas consideradas**:
  - *Spinner central genérico:* Rejeitado por não fornecer pista geométrica de conteúdo e parecer engessado.

---

### D5: Ergonomia de Superfície de Clique Integral e Ação de Lixeira Isolada

- **Decisão**: O cartão inteiro é configurado como elemento interativo de navegação com `@click="openStudy"` e navegação por teclado (`tabindex="0"`, `@keydown.enter="openStudy"`). A ação de mover para a lixeira é posicionada no rodapé inferior com `@click.stop` e disparo do modal de confirmação.
- **Racional**:
  - Satisfaz a decisão de clarificação Q3: Opção A.
  - Máxima agilidade de uso: clicar em qualquer ponto do card abre a leitura imediatamente.
  - O `@click.stop` na lixeira garante que o evento de clique não propague para o card raiz, prevenindo navegações indesejadas no momento da exclusão.
- **Alternativas consideradas**:
  - *Navegação apenas no link do título:* Rejeitada por reduzir a área útil de clique no celular.
