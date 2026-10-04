# Technical Research: F 0.7.7 — Redesenho da Map View (Criação e Edição de Grafo Semântico)

**Feature**: F 0.7.7 — Redesenho da Map View  
**Created**: 2026-10-04  
**Status**: Completed  

---

## Decision Log

### D1: Algoritmo de Distribuição Radial Concêntrica e Repulsão Suave
- **Decisão**: Implementar layout determinístico através de função pura em `useMapLayout.ts`. O Estudo Núcleo (estudo ativo ou primeiro estudo focal do capítulo) fica ancorado ao centro da área visual `(cx, cy)`. Estudos com relação direta de 1º grau orbitam no anel interno $R_1 \approx 160\text{px}$. Estudos secundários (2º grau ou isolados) orbitam no anel externo $R_2 \approx 280\text{px}$. Um passe de relaxamento angular com força repulsiva suave $\Delta \theta = \frac{k}{d^2}$ evita sobreposição de cartões quando muitos estudos compartilham o mesmo quadrante.
- **Racional**: Garante estabilidade visual reproduzível (sem jittering de simulações físicas que flutuam eternamente), permite ao leitor memorizar a localização espacial de cada ideia e mantém a hierarquia cognitiva evidente.
- **Alternativas consideradas**:
  - *Force-directed orgânico contínuo (D3-force)*: Descartado por causar deslocamento constante de nós, tornando cliques e conexões difíceis e cansativos.
  - *Grade matricial em colunas*: Descartada por não valorizar a centralidade do argumento principal.

---

### D2: Traçado Interativo de Arestas com Linha Elástica SVG
- **Decisão**: Criar manipulador de conexão no componente `StudyMapView.vue`. Cada nó possui uma alça conectora visível (`.node-connect-handle`). Ao iniciar o arrasto nessa alça, o mapa entra no modo `isConnecting = true` e desenha em tempo real uma linha elástica curva (`<path class="elastic-draft-line">`) unindo o nó de origem à coordenada do ponteiro do mouse `(clientX, clientY)`. Ao sobrevoar um nó candidato válido, ele recebe classe `.is-drop-target`. Auto-conexões são bloqueadas na raiz (`sourceId === targetId`).
- **Racional**: Oferece feedback visual imediato e tátil, similar a ferramentas modernas de pensamento visual (Figma, Miro, Obsidian Canvas), sem adicionar bibliotecas pesadas de terceiros.
- **Alternativas consideradas**:
  - *Apenas seleção por formulário suspenso*: Descartada por ser passiva e lenta.
  - *Canvas 2D com WebGL puro para arrasto*: Descartado por complexidade desnecessária; SVG nativo atende a 60fps com aceleração CSS por GPU já existente no `CanvasAcceleratedLayer`.

---

### D3: Popover Contextual Ancorado (`MapRelationPopover.vue`)
- **Decisão**: Desenvolver componente dedicado `MapRelationPopover.vue` ancorado nas coordenadas da conexão. Exibe oração semântica orientada ativa (*"Estudo Origem [relação] Estudo Destino"*), dropdown estilizado com os 6 tipos canônicos de relação (`fundamenta`, `desdobra`, `contradiz`, `sintetiza`, `cita`, `complementa`), botão de inversão rápida `⇄` para inverter a direção do argumento em 1 clique, campo opcional de justificativa e botões "Salvar Relação" / "Cancelar".
- **Racional**: Elimina atrito cognitivo. O usuário define o sentido da relação no calor do pensamento, sem perder o contexto visual do grafo.
- **Alternativas consideradas**:
  - *Modal central de tela cheia*: Descartado por cobrir o mapa e desorientar a percepção relacional.
  - *Menu de clique com botão direito*: Descartado por ser pouco intuitivo e inacessível no mobile.

---

### D4: Mini-card Inline de Criação Rápida no Mapa (`MapQuickCreateCard.vue`)
- **Decisão**: Ao acionar duplo clique em coordenada livre do mapa ou tocar no botão flutuante "+ Novo Estudo", renderiza-se um mini-card compacto in-place nas coordenadas exatas. O leitor preenche Título e escolhe a Seção Inicial (*Resumo*, *Conceito* ou *Explicação* com texto breve). Ao pressionar `Enter` ou clicar em "Criar", a requisição `POST /api/studies` é disparada. Se a criação foi originada a partir de uma alça conectora, a relação semântica é criada simultaneamente, inserindo o novo estudo e a aresta no grafo.
- **Racional**: Atende ao requisito do usuário de não quebrar a imersão de estudo. Permite registrar pensamentos emergentes e ramificações conceituais em menos de 5 segundos.
- **Alternativas consideradas**:
  - *Redirecionar para `/import`*: Descartado por exigir navegação de página e destruir o fluxo visual.

---

### D5: Ergonomia Móvel Assistida e Alvos de Toque (WCAG 2.2)
- **Decisão**: Para telas móveis (< 768px), onde arrastar com um dedo enquanto segura o celular pode conflitar com o pan do navegador, fornecer modo assistido de toque:
  1. Toque no nó de origem seleciona o estudo e abre barra de ações táteis de rodapé.
  2. Toque no botão "Conectar a..." (mínimo 44×44px) ativa o modo de mira.
  3. Toque no nó de destino abre o popover de relação.
  4. Todos os botões táteis (seleção, fechamento, inverter direção) possuem dimensões mínimas de 44×44px.
- **Racional**: Garante total acessibilidade e conforto operacional em celulares e tablets sem depender de arrasto touch contínuo.
- **Alternativas consideradas**:
  - *Apenas arrasto touch*: Rejeitado por taxa alta de erros e cancelamento acidental por scroll do navegador.
