# Research & Technical Decisions: F03 — Canvas de Estudos

**Feature Branch**: `021-canvas-estudos`  
**Date**: 2026-09-19  
**Status**: Completed  

---

## 1. Modelo Relacional e Persistência de Coordenadas Espaciais no SQLite

### Contexto
O Canvas de Estudos exige que as posições físicas dos cards (x, y, largura, altura, z-index e tag de cor) sejam persistidas de forma duradoura. Contudo, em conformidade com o Princípio 3 do Roadmap 0.4 ("Desacoplamento entre Espaço e Semântica") e a Constituição do Caderno, a movimentação de nós no Canvas não pode alterar a hierarquia canônica (`parent_study_id`, `position`) nem a ordenação de capítulos na tabela `studies`.

### Decisão
- Criar a tabela dedicada `study_canvas_nodes` via migração Alembic `0007_add_study_canvas_nodes.py`:
  - `id`: `INTEGER PRIMARY KEY AUTOINCREMENT`
  - `study_id`: `INTEGER NOT NULL REFERENCES studies(id) ON DELETE CASCADE`
  - `book_id`: `INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE`
  - `pos_x`: `REAL NOT NULL DEFAULT 0.0` (coordenada horizontal contínua no mundo 2D)
  - `pos_y`: `REAL NOT NULL DEFAULT 0.0` (coordenada vertical contínua no mundo 2D)
  - `width`: `REAL NULL` (largura customizada opcional do card, default 280px)
  - `height`: `REAL NULL` (altura customizada opcional do card, default automático)
  - `z_index`: `INTEGER NOT NULL DEFAULT 0` (ordem de profundidade no empilhamento)
  - `color_tag`: `TEXT NULL` (etiqueta cromática opcional do card para agrupamento visual)
  - `updated_at`: `DATETIME NOT NULL` (controle de concorrência e timestamp)
  - Restrição única e índice: `UNIQUE(study_id, book_id)` e índice `ix_canvas_nodes_book_study`.

### Rationale
- Isolamento total entre metadados de visualização espacial e o modelo semântico `Study`.
- Deleção em cascata (`ON DELETE CASCADE`): se um estudo for removido definitivamente ou expurgado da lixeira, suas coordenadas no canvas são limpas automaticamente sem deixar orfandade.
- A restrição única `(study_id, book_id)` garante que cada estudo possua exatamente uma coordenada espacial estável no contexto de sua obra (decisão ratificada na clarificação Q2: Opção A — Canvas por Livro).

### Alternativas Consideradas
- **Adicionar `pos_x` e `pos_y` diretamente na tabela `studies`**: Rejeitado. Poluiria a tabela principal com metadados opcionais de visualização e violaria o princípio de desacoplamento do Roadmap 0.4.
- **Salvar coordenadas exclusivamente no `localStorage`**: Rejeitado. As coordenadas do layout intelectual do leitor são um trabalho de síntese autêntico e devem ser preservadas no banco e incluídas em backups e restaurações do acervo.

---

## 2. Motor de Viewport 2D: Matemática de Transformação e Renderização a 60fps

### Contexto
O leitor precisa de navegação espacial contínua por deslocamento livre (pan) e aproximação/afastamento (zoom). A manipulação de dezenas de elementos no DOM pode causar travamentos (*jank*) caso haja repaints ou reflows excessivos.

### Decisão
- Utilizar um modelo matemático formal de **Espaço do Mundo (*World Space*) vs Espaço da Tela (*Screen Space*)**:
  $$\text{Screen}_X = \text{World}_X \times \text{Zoom} + \text{Pan}_X$$
  $$\text{Screen}_Y = \text{World}_Y \times \text{Zoom} + \text{Pan}_Y$$
  $$\text{World}_X = \frac{\text{Screen}_X - \text{Pan}_X}{\text{Zoom}}$$
  $$\text{World}_Y = \frac{\text{Screen}_Y - \text{Pan}_Y}{\text{Zoom}}$$
- Aceleração por GPU via CSS Transforms no contêiner do palco:
  `transform: translate3d(panX px, panY px, 0) scale(zoomLevel)` e `transform-origin: 0 0; will-change: transform;`.
- Zoom com ponto focal ancorado no cursor do mouse / centro da pinça:
  Ao alterar o zoom em $\Delta$, o novo pan é recalculado para manter invariante o ponto do mundo sob o cursor:
  $$\text{Pan}_{novo} = \text{Screen}_{cursor} - (\text{Screen}_{cursor} - \text{Pan}_{anterior}) \times \frac{\text{Zoom}_{novo}}{\text{Zoom}_{anterior}}$$
- Limites estritos de zoom (*clamping*): mínimo 0.25x (25%) e máximo 2.0x (200%).
- Persistência do estado do observador no navegador (`localStorage`) sob a chave `caderno_canvas_viewport_{bookId}` contendo `{ panX, panY, zoomLevel }`.

### Rationale
- Zero dependências de bibliotecas externas pesadas (sem D3, PixiJS ou Three.js). Matemática pura em TypeScript nativo via composable `useCanvasViewport.ts`.
- `translate3d` aciona a camada de composição da GPU, mantendo 60fps contínuos sem disparar reflows dos cards internos.
- Respeito a `prefers-reduced-motion`: transições animadas (como o "Ajustar à Tela") tornam-se imediatas se a preferência de acessibilidade estiver ativada no sistema.

---

## 3. Algoritmo de Auto-Grid para Estudos sem Coordenadas Prévias (Q1: Opção A)

### Contexto
Quando o leitor abre o Canvas de um livro pela primeira vez, ou adiciona novos estudos que ainda não foram manipulados no espaço 2D, esses cards chegam do banco sem registro na tabela `study_canvas_nodes`.

### Decisão
- Implementar o algoritmo determinístico de **Auto-Grid Ordenado por Capítulo**:
  - Parâmetros da grade:
    - Largura estimada do card: $W_{card} = 280\text{px}$
    - Altura estimada do card: $H_{card} = 220\text{px}$
    - Espaçamento horizontal e vertical: $G = 24\text{px}$
    - Número de colunas por capítulo: $C = 3$
  - Agrupamento: estudos são ordenados por `chapter.order_index`, `parent_study_id` e `position`.
  - Cada capítulo ocupa um quadrante horizontal ou bloco de colunas:
    $$X = \text{coluna} \times (W_{card} + G) + \text{offsetCapitulo}_X$$
    $$Y = \text{linha} \times (H_{card} + G)$$
  - Detecção de colisão simples: se a coordenada computada colidir com um card já persistido pelo usuário, o novo card é deslocado para a próxima posição livre na grade.
- Quando o usuário move um card pela primeira vez, a posição é persistida na API (`study_canvas_nodes`).

### Rationale
- Elimina o problema de cartões sobrepostos ou amontoados na origem (0, 0).
- Proporciona uma visão inicial imediata, limpa e esteticamente agradável do livro logo no primeiro clique no modo Canvas.

---

## 4. Seleção Simples, Marquee Selection e Arraste em Bloco

### Contexto
O leitor precisa de flexibilidade para organizar grandes seções do canvas: mover um único card ou selecionar dezenas de anotações relacionadas para movê-las em conjunto sem perder a disposição relativa.

### Decisão
- Composable dedicado `useCanvasSelection.ts`:
  - **Seleção Simples**: Clique em um card seleciona exclusivamente aquele card. `Ctrl+Clique` ou `Cmd+Clique` alterna a seleção do card sem desmarcar os demais.
  - **Marquee Selection (Caixa Retangular)**: Ao clicar e arrastar no fundo com a tecla `Shift` pressionada (ou através da ferramenta de seleção na barra de ferramentas), projeta-se um retângulo semi-transparente no espaço de tela:
    $$\text{Box}_{screen} = [\min(x_1, x_2), \min(y_1, y_2), |x_2 - x_1|, |y_2 - y_1|]$$
    Convertido para coordenadas do mundo, qualquer card cujo retângulo intersecte a caixa é incluído na seleção ativa.
  - **Arraste em Bloco**:
    Quando um card pertencente à seleção múltipla é arrastado por um vetor $(\Delta x, \Delta y)$, todos os outros cards selecionados recebem exatamente o mesmo deslocamento relativo:
    $$x_{i, novo} = x_{i, original} + \Delta x$$
    $$y_{i, novo} = y_{i, original} + \Delta y$$
  - **Elevação de Z-Index**: O card clicado ou arrastado recebe o maior `z_index` atual $+ 1$, trazendo-o ao primeiro plano visual.

---

## 5. Mini-mapa de Navegação (Radar View) e "Ajustar à Tela" (Fit to View)

### Contexto
Em pranchas com muitos estudos, o usuário pode rolar para áreas vazias e perder os cards de vista (*lost in space*). O mini-mapa fornece consciência topológica instantânea.

### Decisão
- Componente `CanvasMinimap.vue`:
  - Dimensão padrão do radar: $180 \times 120\text{px}$ no canto inferior direito.
  - Cálculo do Retângulo Delimitador (*Bounding Box*) de todos os nós:
    $$X_{min} = \min(x_i), \quad X_{max} = \max(x_i + w_i)$$
    $$Y_{min} = \min(y_i), \quad Y_{max} = \max(y_i + h_i)$$
  - Projeção de nós: cada card é renderizado como uma pequena pastilha na cor de sua tag ou neutra.
  - Projeção do Viewport: renderização de um retângulo translúcido representando a porção do mundo visível na tela:
    $$\text{View}_{world} = \left[-\frac{\text{Pan}_X}{\text{Zoom}}, -\frac{\text{Pan}_Y}{\text{Zoom}}, \frac{\text{Width}_{tela}}{\text{Zoom}}, \frac{\text{Height}_{tela}}{\text{Zoom}}\right]$$
  - Interação: clicar ou arrastar a janela no mini-mapa recentraliza o viewport imediatamente na coordenada desejada.
- **Função Fit to View**:
  Calcula a escala necessária para conter todo o Bounding Box com margem de segurança de 60px:
  $$\text{Scale} = \min\left(\frac{\text{Width}_{tela} - 120}{X_{max} - X_{min}}, \frac{\text{Height}_{tela} - 120}{Y_{max} - Y_{min}}, 1.0\right)$$
  E centraliza o ponto médio $(\frac{X_{min}+X_{max}}{2}, \frac{Y_{min}+Y_{max}}{2})$ no meio da tela.

---

## 6. Ergonomia Tátil Móvel e Acessibilidade (Q3: Opção A & WAI-ARIA)

### Contexto
O sistema roda em navegadores de smartphones e tablets conectados pela rede local ou Tailscale. Gestos táteis não podem colidir com a rolagem vertical nativa da página nem exigir precisão cirúrgica de ponteiro.

### Decisão
- **Toque Direto Inteligente (Pointer Events)**:
  - Cards possuem manipuladores claros e `touch-action: none` para impedir que o navegador tente rolar a página enquanto o usuário move o card.
  - O contêiner de fundo possui `touch-action: none` e gerencia:
    - 1 ponteiro tocando no fundo $\rightarrow$ Pan do canvas.
    - 2 ponteiros simultâneos $\rightarrow$ Cálculo contínuo de distância euclidiana para Pinch-to-Zoom e translação do ponto central.
- **Botões Táteis Flutuantes Acessíveis**:
  - Barra de controle flutuante com botões de tamanho mínimo $44 \times 44\text{px}$ para Zoom In, Zoom Out, 100% e Ajustar à Tela.
- **Navegação por Teclado e Foco Consistente**:
  - `Tab` / `Shift+Tab` navega entre os cards de estudo em ordem de leitura.
  - Card focado pode ser movido no espaço com `Shift + Setas Direcionais` (passos de 10px ou 50px com `Shift+Ctrl`).
  - Atributos semânticos: `role="region"`, `aria-label="Canvas de Estudos"`, `aria-roledescription="Espaço bidimensional interativo"`.

---

## 7. Sincronização e Concorrência Otimista com a API

### Contexto
Arrastar múltiplos cards pode gerar dezenas de eventos por segundo. O envio indiscriminado de requisições causaria gargalo de rede e sobrecarga no SQLite.

### Decisão
- Implementar **Atualização em Lote com Debounce**:
  - No frontend, as coordenadas dos cards são atualizadas a 60fps no estado reativo local durante o arrasto.
  - Ao soltar o card (`pointerup`), dispara-se um debounce de 300ms.
  - A requisição `PUT /api/books/{id}/canvas` envia a lista de nós alterados:
    `[{ "study_id": 12, "pos_x": 350.5, "pos_y": 120.0, "z_index": 4 }]`.
  - O backend processa em uma única transação atômica no SQLite utilizando `INSERT INTO ... ON CONFLICT(study_id, book_id) DO UPDATE`.
  - Tratamento de HTTP 409: caso outro dispositivo tenha atualizado as coordenadas concorrentemente, o frontend faz merge seguro sem perda de dados locais.
