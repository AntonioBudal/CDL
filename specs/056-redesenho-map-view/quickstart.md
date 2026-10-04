# Quickstart: Validação da Feature F 0.7.7 (Redesenho da Map View)

**Feature**: F 0.7.7 — Redesenho da Map View: Criação e Edição de Grafo Semântico  
**Artifact**: `quickstart.md`  

---

## 1. Pré-requisitos
- Frontend em execução em `http://localhost:5173` ou suíte de testes unitários (`npm test`).
- Backend em execução em `http://localhost:8000` ou suíte de integração (`pytest`).

---

## 2. Cenários de Validação Fim a Fim

### Cenário 1: Visualização Radial Concêntrica e Estudo Núcleo Destacado (US1 - MVP)
1. Acesse um capítulo contendo múltiplos estudos com relações semânticas cadastradas.
2. Alterne para a aba **"Mapa" (Map View)**.
3. **Resultado esperado**:
   - O estudo ativo ou foco principal aparece posicionado no centro focal com tamanho superior, halo dimensional e contraste evidente (`isCore`).
   - Os estudos com relações diretas orbitam no anel interno ($R_1$) e estudos secundários no anel externo ($R_2$).
   - Arestas curvas direcionadas unem os estudos com setas visíveis e badges com o tipo da relação (*fundamenta*, *desdobra*, etc.).
   - Pan (arrasto) e zoom operam de forma suave mantendo nitidez.

### Cenário 2: Traçado Interativo de Conexão com Linha Elástica (US2)
1. Passe o cursor sobre um nó de estudo periférico.
2. Observe o surgimento da alça de conexão interativa (`.node-connect-handle`).
3. Clique e arraste a partir da alça.
4. **Resultado esperado**:
   - Uma linha elástica dinâmica acompanha o cursor em tempo real.
   - Ao passar sobre outro nó elegível, o nó de destino recebe aura magnética indicando receptividade.
   - Ao passar sobre o próprio nó de origem, o cursor sinaliza bloqueio (`not-allowed`), impedindo auto-relação.

### Cenário 3: Seleção e Persistência no Popover de Relações com Inversão `⇄` (US2)
1. Solte a linha elástica sobre o nó de destino válido.
2. **Resultado esperado**:
   - Abre-se o mini-popover contextual `MapRelationPopover` ancorado no nó de destino.
   - O popover exibe a oração semântica: *"Estudo A [tipo de relação] Estudo B"*.
   - Ao clicar no botão de inversão rápida `⇄`, a oração se inverte instantaneamente para *"Estudo B [tipo de relação] Estudo A"*.
3. Selecione o tipo de relação "fundamenta", digite uma breve nota opcional e confirme ("Salvar Relação").
4. **Resultado esperado**:
   - A relação é salva no backend via API.
   - A nova aresta com seu rótulo e sentido direcional é desenhada imediatamente no mapa.

### Cenário 4: Criação Rápida de Novo Estudo Inline no Mapa (US3)
1. Em qualquer área vazia do fundo do mapa, dê um **duplo clique** (ou clique no botão flutuante `+`).
2. **Resultado esperado**:
   - Surge o mini-card de criação in-place no local exato do clique.
   - O campo de título recebe foco automático.
3. Digite o título do novo estudo (ex.: "Nova Síntese Conceitual"), selecione a seção "Resumo" e digite um breve texto. Pressione `Enter`.
4. **Resultado esperado**:
   - O estudo é salvo no capítulo via `POST /api/studies` e um novo nó surge posicionado no mapa sem recarregar a tela.

### Cenário 5: Modo Assistido de Toque e Ergonomia Mobile (US3)
1. Reduza a janela para modo mobile (< 768px).
2. Toque em um nó de estudo.
3. **Resultado esperado**:
   - Surge barra inferior de ações táteis com botões de dimensão mínima 44×44px: "Conectar a...", "Ver Estudo", "Novo Estudo Conectado".
4. Toque em "Conectar a..." e em seguida toque em outro nó de estudo.
5. **Resultado esperado**:
   - O popover de relação abre-se perfeitamente adaptado para o toque, permitindo estabelecer a conexão com conforto no celular.
