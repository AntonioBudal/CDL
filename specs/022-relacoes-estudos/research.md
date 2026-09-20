# Technical Research & Architecture Decisions: F04 — Relações entre Estudos

**Feature**: `022-relacoes-estudos`  
**Date**: 2026-09-19  
**Status**: Completed  

---

## 1. Decisões Arquiteturais e Rationales

### Decisão 1: Modelo Relacional e Integridade de Dados (`study_relations`)
- **Decisão**: Criar a tabela `study_relations` com chaves estrangeiras duplas referenciando `studies(id)` com `ON DELETE CASCADE`.
- **Campos**:
  - `id`: Chave primária inteira autoincrementável.
  - `source_study_id`: Inteiro não-nulo com chave estrangeira para `studies.id`.
  - `target_study_id`: Inteiro não-nulo com chave estrangeira para `studies.id`.
  - `relation_type`: Texto não-nulo com `CheckConstraint` limitando aos 6 tipos canônicos:
    - `relacionado_com` (associação temática neutra)
    - `complementa` (origem fornece argumentos/suporte ao destino)
    - `contradiz` (origem refuta/problematiza a tese do destino)
    - `depende_de` (origem pressupõe o entendimento prévio do destino)
    - `mesmo_tema` (afinidade conceitual direta)
    - `desdobramento_de` (origem é consequência ou derivação do destino)
  - `description`: Texto não-nulo com default `''` e limite de 500 caracteres para notas explicativas.
  - `created_at`: Data e hora de criação com default `CURRENT_TIMESTAMP`.
- **Restrições & Índices**:
  - `CheckConstraint("source_study_id != target_study_id", name="ck_study_relations_no_self")`: Proíbe no nível do banco de dados que um estudo se auto-relacione.
  - `UniqueConstraint("source_study_id", "target_study_id", "relation_type", name="uq_study_relations_src_tgt_type")`: Impede duplicatas do mesmo vínculo semântico.
  - `Index("ix_study_relations_source", "source_study_id")`: Otimiza a busca de relações de saída.
  - `Index("ix_study_relations_target", "target_study_id")`: Otimiza a busca reversa de backlinks.
- **Rationale**: Garante integridade referencial estrita no SQLite com `PRAGMA foreign_keys = ON`, impedindo estados inválidos ou referências corrompidas.
- **Alternativas Rejeitadas**:
  - *Armazenar relações como array JSON dentro da tabela `studies`:* Rejeitado porque quebra a primeira forma normal, impede consultas de backlinks reversos eficientes e inviabiliza constraints de integridade referencial nativas.

---

### Decisão 2: Escopo Transversal e Busca Rápida de Candidatos
- **Decisão**: As relações podem conectar estudos entre quaisquer livros cadastrados no acervo pessoal. A API fornecerá um endpoint otimizado `GET /api/studies/search-candidates?query=...&exclude_study_id=...` que pesquisa estudos por título ou nome de capítulo em todo o acervo.
- **Formato do Resultado**: Retorna `id`, `title`, `book_id`, `book_title`, `chapter_id`, `chapter_title` com limite de 20 itens.
- **Filtragem Preventiva**: O frontend e o backend filtram automaticamente o próprio estudo selecionado (`exclude_study_id`) e estudos já vinculados com a mesma direção e tipo de relação.
- **Rationale**: Permite cruzar hipóteses e teses entre autores e obras distintas da biblioteca pessoal do leitor, preservando contexto claro sobre a origem de cada estudo através da exibição do livro e capítulo.
- **Alternativas Rejeitadas**:
  - *Restringir ao mesmo livro:* Rejeitado conforme alinhamento com o usuário na Questão 1 (Opção A).

---

### Decisão 3: Consulta Unificada de Backlinks e Prevenção de Consultas N+1
- **Decisão**: A rota `GET /api/studies/{id}/relations` executa uma consulta composta unificada com junções (`JOIN` com `studies` e `books`), retornando um payload estruturado com duas coleções:
  - `outbound`: Relações onde o estudo atual é a origem (`source`), trazendo os metadados do estudo de destino (`target`).
  - `inbound`: Backlinks onde o estudo atual é o destino (`target`), trazendo os metadados do estudo de origem (`source`).
- **Filtragem de Soft Delete**: A query aplica explicitamente `studies.is_deleted == False` para ambos os lados da relação, garantindo que conexões envolvendo estudos temporariamente na lixeira não poluam a interface.
- **Rationale**: Elimina o problema clássico de queries N+1, reduzindo a latência da visualização de estudo a um único ciclo de I/O no SQLite.
- **Alternativas Rejeitadas**:
  - *Fazer duas chamadas HTTP separadas (uma para saída e outra para entrada):* Rejeitado por duplicar o overhead de rede e complicar o gerenciamento de estado no frontend.

---

### Decisão 4: Projeção Visual Vetorial no Canvas e Mapa (Curvas Bézier SVG)
- **Decisão**: O componente de Canvas renderizará uma camada vetorial SVG sobreposta (`<svg class="canvas-connections-layer">`) contendo as arestas semânticas entre os cards posicionados no espaço bidimensional.
- **Cálculo Geométrico**:
  - Algoritmo de ancoragem nas bordas mais próximas: identifica os centros de cada card $(x_1, y_1)$ e $(x_2, y_2)$ e calcula a interseção com o retângulo delimitador de cada nó para definir os pontos de início e fim $(P_{start}, P_{end})$.
  - Traçado em curva Bézier cúbica suave: calcula pontos de controle $C_1$ e $C_2$ baseados na distância e orientação relativa para produzir arcos elegantes sem pontas duras.
  - Marcador direcional: elemento `<marker id="arrow" ...>` com ponta de flecha SVG na extremidade final da linha.
  - Badge compacto flutuante: elemento `<g class="relation-badge">` com fundo semi-opaco e texto estilizado contendo o tipo da relação no ponto médio paramétrico da curva $(t = 0.5)$.
- **Desempenho**: As arestas são desenhadas no espaço de coordenadas do mundo e transformadas conjuntamente com o contêiner do Canvas (`transform: translate3d(...) scale(...)`), garantindo que o navegador aproveite aceleração GPU nativa a 60fps sem recalcular coordenadas durante simples operações de pan e zoom.
- **Rationale**: Máxima fluidez e legibilidade espacial, sem sobrecarregar a CPU com cálculos manuais a cada frame de pan/zoom.
- **Alternativas Rejeitadas**:
  - *Desenhar em `<canvas>` 2D nativo via CanvasRenderingContext2D:* Rejeitado porque elementos SVG integram-se diretamente ao modelo reativo do Vue 3, suportam CSS styling, eventos de ponteiro nativos e animações declarativas com facilidade incomparável.

---

### Decisão 5: Ciclo de Vida Latente sob Soft Delete (Lixeira)
- **Decisão**: O envio de um estudo para a lixeira (`services/trash_service.py`) não altera as linhas da tabela `study_relations`. Apenas as consultas ativas filtram estudos com `is_deleted = False`.
- **Restauração**: Quando o estudo é restaurado da lixeira, seus vínculos reaparecem imediatamente no estudo e no Canvas, sem necessidade de recadastro.
- **Expurgo Definitivo**: Quando um estudo é expurgado definitivamente da lixeira (`DELETE FROM studies WHERE id = ...`), as chaves estrangeiras com `ON DELETE CASCADE` garantem a remoção atômica e limpa de todas as suas relações na tabela `study_relations`.
- **Rationale**: Alinhado com a Questão 3 (Opção A) e com a Constituição (artigo I - Preservação Absoluta de Registros).
- **Alternativas Rejeitadas**:
  - *Destruir as relações imediatamente no envio à lixeira:* Rejeitado por causar perda destrutiva irrecuperável caso o usuário tenha enviado o estudo à lixeira por engano.

---

### Decisão 6: Ergonomia Tátil Móvel e Acessibilidade WAI-ARIA
- **Decisão**:
  - O modal de criação de relação e a listagem de backlinks utilizam componentes modais/gavetas com alvos de toque mínimos de 44x44px.
  - Relações na tela de leitura de um estudo utilizam tags semânticas navegáveis com rótulos `aria-label="Relação: [tipo] com [estudo]"`.
  - No modo móvel, clicar em uma relação abre o estudo conectado em uma gaveta sobreposta (*bottom sheet*) ou navega diretamente, mantendo o histórico de navegação estável.
- **Rationale**: Cumpre os requisitos inegociáveis de ergonomia móvel e acessibilidade da Constituição.
