# Research: F 0.7.8 — Redesenho do Canvas: Espaço Livre de Pensamento e Criação Espacial

**Feature**: F 0.7.8 — Redesenho do Canvas  
**Date**: 2026-10-04  
**Status**: Completed  

---

## Decisões Técnicas e Arquiteturais

### D1: Mecânica de Criação Rápida In-Place no Canvas (Duplo Clique)

- **Decisão**: Capturar o evento de duplo clique (`@dblclick`) na superfície do canvas (quando não disparado sobre nós ou molduras existentes), convertendo as coordenadas de viewport `(clientX, clientY)` para o espaço de mundo `(worldX, worldY)` através da transformação inversa de pan e zoom, e abrindo o mini-card de criação rápida no ponto exato.
- **Racional**:
  - Elimina fricção cognitiva: o usuário não precisa alternar para formulários externos ou navegar para outra tela para registrar um pensamento emergente.
  - O mini-card solicita apenas Título e Seção Inicial (Resumo, Conceito ou Explicação), garantindo conformidade com a validação `require_analysis` do backend.
  - Ao salvar com `Enter`, o estudo é criado via `POST /api/studies` e imediatamente posicionado nas coordenadas `(worldX, worldY)` através de persistência em `study_canvas_nodes`.
- **Alternativas consideradas**:
  - *Modal central flutuante*: Rejeitado por interromper a continuidade espacial do pensamento.
  - *Criação de nó temporário rascunho sem título*: Rejeitado por violar as restrições de validação de modelo do backend.

---

### D2: Movimento Solidário Automático de Cartões em Molduras (Frames)

- **Decisão**: Implementar detecção geométrica em tempo real: cartões cujas caixas delimitadoras estejam contidas (ou com centro) no interior de uma moldura retangular são considerados membros dessa moldura durante a operação de arrasto. Ao arrastar a moldura pelo seu cabeçalho ou área de fundo, o deslocamento delta `(dx, dy)` é aplicado simultaneamente à moldura e a todos os cartões vinculados, persistindo as posições relativas com debounce de 500ms.
- **Racional**:
  - Alinhado com a Decisão de Clarificação Q1 (Opção A).
  - Garante a sensação natural de um "bloco de notas" ou "quadro temático": mover o grupo não desfaz a diagramação interna cuidadosamente construída pelo usuário.
  - Permite ainda mover cartões individualmente para dentro ou fora da moldura sem travamentos burocráticos.
- **Alternativas consideradas**:
  - *Vínculo relacional estrito em banco de dados*: Rejeitado por exigir alterações de schema e migrações SQL, violando a diretriz de zero impacto estrutural no banco de dados.
  - *Movimento independente (moldura solta no fundo)*: Rejeitado por gerar frustração ao ter que mover múltiplos cartões um a um.

---

### D3: Conexões Direcionadas e Integração com Relações Semânticas

- **Decisão**: As conexões direcionadas desenhadas no Canvas utilizam a infraestrutura existente de `useCanvasConnections` e a tabela canônica `study_relations`. Ao puxar uma aresta entre dois cartões pela alça conectora, abre-se o popover contextual de relações semânticas para seleção do tipo canônico (*fundamenta / depende_de*, *desdobra*, *contradiz*, *complementa*, etc.), traçando arestas curvas com setas indicativas de sentido e badges legíveis.
- **Racional**:
  - Alinhado com a Decisão de Clarificação Q2 (Opção A).
  - Mantém integridade referencial: as relações mapeadas no Canvas refletem-se na Map View e na aba de relações do leitor, evitando duplicação ou desconexão de dados.
  - Bloqueio imediato de auto-relações (`source_study_id === target_study_id`).
- **Alternativas consideradas**:
  - *Arestas exclusivamente visuais sem persistência*: Rejeitado por criar desconexão entre a organização visual e a base de conhecimento do acervo.

---

### D4: Alinhamento Magnético Inteligente (Smart Guides)

- **Decisão**: Durante o arrasto de cartões no Canvas, calcular em tempo de execução a proximidade das coordenadas dos eixos X e Y (bordas esquerda, direita, superior, inferior e centros) com os cartões vizinhos mais próximos. Quando a distância estiver dentro do limiar de atração (threshold de $\pm 10$px), aplicar encaixe suave (magnetic snap) e projetar temporariamente linhas guias pontilhadas na cor de acento (`var(--color-accent)`).
- **Racional**:
  - Alinhado com a Decisão de Clarificação Q3 (Opção A).
  - Confere acabamento gráfico profissional e sensação de precisão estética, inspirada nas melhores práticas de ferramentas de design espacial (Figma, Miro, Excalidraw).
  - O cálculo é puramente vetorial e leve ($O(N)$ sobre nós visíveis), rodando a 60 fps sem sobrecarregar a thread de UI.
- **Alternativas consideradas**:
  - *Snap to grid rígido*: Rejeitado por restringir a sensação de liberdade espacial do usuário.
  - *Sem qualquer auxílio de alinhamento*: Rejeitado por tornar difícil alinhar cartões simetricamente.

---

### D5: Ergonomia Mobile, Gestos Nativos e Acessibilidade

- **Decisão**:
  - Implementar suporte a gestos de pinça (pinch-to-zoom) e arrasto com dois dedos para pan no mobile, mantendo botões dedicados de zoom no rodapé.
  - Barra de ações táteis de rodapé para seleção rápida de ferramentas (`select`, `pan`, `frame`, `connect`).
  - Alvos táteis rigorosamente configurados para dimensão mínima de 44×44px (`.touch-target`, `.action-btn`).
  - Lista alternativa acessível em container `.sr-only` para leitura linear por softwares leitores de tela (WCAG 2.2).
- **Racional**:
  - Cumpre os critérios constitucionais de acessibilidade e os requisitos funcionais FR-011 e FR-012.

---
