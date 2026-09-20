# Technical Research: F05 — Agrupamento Visual

**Feature Branch**: `023-agrupamento-visual`  
**Date**: 2026-09-19  
**Specification**: [spec.md](./spec.md)  
**Status**: Completed  

---

## 1. Decisões Técnicas Consolidadas

### Decisão 1: Atributo `reading_status` no Modelo de Estudos
- **Decisão**: Adicionar a coluna `reading_status` à tabela `studies` via migração Alembic, tipada como `VARCHAR(20) NOT NULL DEFAULT 'rascunho'` com restrição `CheckConstraint("reading_status IN ('rascunho', 'em_estudo', 'revisado', 'concluido')", name="ck_studies_reading_status")` e índice de performance `ix_studies_reading_status`.
- **Rationale**:
  - Responde diretamente à decisão aprovada no esclarecimento Q1: ciclo editorial canônico de 4 estados.
  - O valor padrão `'rascunho'` garante retrocompatibilidade total com todos os estudos existentes no banco sem deixar valores nulos.
  - A restrição a nível de banco previne inconsistências semânticas e garante integridade referencial estrita.
- **Alternativas consideradas**:
  - *Tabela separada de status / workflow*: Rejeitada por excesso de complexidade e overhead de junções relacionais para um atributo intrínseco de cada estudo.
  - *Campos booleanos dispersos (`is_reviewed`, `is_draft`)*: Rejeitada por inviabilizar ordenação, transição finita e agrupamento direto em raias.

---

### Decisão 2: Modelo Relacional e Persistência de Molduras no Canvas (`CanvasFrame`)
- **Decisão**: Criar a tabela `canvas_frames` com os campos:
  - `id`: `INTEGER PRIMARY KEY AUTOINCREMENT`
  - `book_id`: `INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE`
  - `title`: `VARCHAR(100) NOT NULL`
  - `color`: `VARCHAR(32) NOT NULL DEFAULT 'neutral'`
  - `pos_x`: `FLOAT NOT NULL DEFAULT 0.0`
  - `pos_y`: `FLOAT NOT NULL DEFAULT 0.0`
  - `width`: `FLOAT NOT NULL DEFAULT 400.0`
  - `height`: `FLOAT NOT NULL DEFAULT 300.0`
  - `created_at`: `DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP`
  - `updated_at`: `DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP`
  - Índice: `ix_canvas_frames_book_id`
- **Rationale**:
  - As molduras são vinculadas exclusivamente ao Canvas do livro específico (`book_id`), respeitando o mesmo isolamento espacial de `study_canvas_nodes` (F03).
  - Chave estrangeira com `ON DELETE CASCADE` garante que a exclusão definitiva do livro expurgue suas molduras associadas sem deixar registros órfãos.
- **Alternativas consideradas**:
  - *Armazenar frames apenas no `localStorage`*: Rejeitada porque a topologia e o zoneamento espacial do leitor são artefatos intelectuais persistentes que devem ser preservados e incluídos nos backups ZIP universais.

---

### Decisão 3: Arquitetura Reativa de Particionamento (`useStudyGrouping`)
- **Decisão**: Implementar o composable `useStudyGrouping` no frontend como um motor de ordenação e projeção puramente em memória sobre a coleção reativa de estudos, emitindo uma lista de `StudyGroup` com `{ id, title, count, isCollapsed, studies }`.
- **Critérios suportados**:
  1. `chapter`: Agrupa por `chapter_id` respeitando a ordem canônica do livro.
  2. `status`: Agrupa pelas 4 raias do ciclo de maturação (`rascunho`, `em_estudo`, `revisado`, `concluido`).
  3. `category`: Agrupa pela categoria atribuída ao estudo ou ao livro, com seção fallback "Sem Categoria".
  4. `date`: Agrupa cronologicamente por faixas relativas baseadas em `created_at` / `updated_at`: "Hoje", "Esta Semana", "Este Mês", "Mais Antigos".
  5. `manual`: Agrupamento espacial livre exclusivo do Canvas 2D (F03).
- **Rationale**:
  - O particionamento puramente em memória é instantâneo (<5ms para centenas de estudos) e não onera a CPU nem dispara requisições HTTP redundantes.
  - Zero mutação nos dados estruturais; alternar entre visões é uma operação não-destrutiva de projeção.
- **Alternativas consideradas**:
  - *Endpoints de agrupamento dedicados no backend para cada critério*: Rejeitada por gerar latência de rede desnecessária e consultas repetidas sobre dados já carregados no cliente.

---

### Decisão 4: Interação e Contenção Espacial de Molduras no Canvas 2D
- **Decisão**:
  - Uma moldura envolve um cartão de estudo quando o centro geométrico do cartão $(card.x + card.width/2, card.y + card.height/2)$ ou suas coordenadas principais estão contidas no retângulo da moldura:
    $$frame.x \le center.x \le frame.x + frame.width \quad \land \quad frame.y \le center.y \le frame.y + frame.height$$
  - Ao arrastar a moldura, o deslocamento $(\Delta x, \Delta y)$ é aplicado em tempo real tanto às coordenadas do frame quanto a todos os cartões de estudo contidos nele (agrupamento em bloco solidário aprovado em Q2: A).
  - Mover um cartão individual no interior da moldura altera apenas as coordenadas daquele cartão.
- **Rationale**:
  - Oferece ergonomia idêntica aos principais softwares profissionais de canvas espacial (Figma, Miro, Obsidian Canvas), mantendo a fidelidade tátil esperada.
- **Alternativas consideradas**:
  - *Tabela relacional de associação `frame_studies`*: Rejeitada por introduzir acoplamento rígido no banco de dados para um conceito puramente geométrico espacial.

---

### Decisão 5: Projeção Espacial Reversível no Canvas 2D
- **Decisão**:
  - Quando o usuário ativa um agrupador automático (por Categoria, por Status ou por Data) no Canvas 2D, as coordenadas $(x, y)$ dos cartões são recalculadas dinamicamente em memória em raias/colunas ordenadas com espaçamento regular.
  - As posições originais manuais salvas no banco de dados (`study_canvas_nodes`) permanecem intocadas.
  - Ao selecionar novamente o agrupador "Livre / Manual", os nós retornam instantaneamente às suas coordenadas exatas salvas.
- **Rationale**:
  - Cumpre integralmente o esclarecimento Q3: A (projeção reversível não-destrutiva), eliminando qualquer risco de perda de arranjos visuais construídos com esmero pelo usuário.

---

### Decisão 6: Ergonomia Móvel, Sticky Headers e Acessibilidade WAI-ARIA
- **Decisão**:
  - Cabeçalhos de grupos utilizam CSS `position: sticky; top: 0; z-index: 10` com fundo opaco adaptado ao tema e sombra de descolamento sutil durante a rolagem vertical em telas móveis.
  - Cada grupo é contido em elemento semântico `<section>` com botão de colapso portando `aria-expanded="true|false"` e alvos táteis mínimos de 44x44px.
  - Suporte a controle total por teclado (Enter e Barra de Espaço alternam a expansão do grupo focado).
