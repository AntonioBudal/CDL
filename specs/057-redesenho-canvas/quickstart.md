# Quickstart: Validação da Feature F 0.7.8 (Redesenho do Canvas)

**Feature**: F 0.7.8 — Redesenho do Canvas: Espaço Livre de Pensamento e Criação Espacial  
**Artifact**: `quickstart.md`  

---

## 1. Pré-requisitos
- Frontend em execução em `http://localhost:5173` ou suíte de testes unitários (`npm test`).
- Backend em execução em `http://localhost:8000` ou suíte de integração (`pytest`).

---

## 2. Cenários de Validação Fim a Fim

### Cenário 1: Criação Rápida In-Place no Canvas via Duplo Clique (US1 - MVP)
1. Acesse um livro/capítulo e abra a aba **"Canvas" (Canvas View)**.
2. Dê um **duplo clique** em qualquer coordenada vazia do espaço 2D.
3. **Resultado esperado**:
   - Um mini-card inline de criação rápida surge exatamente nas coordenadas do clique.
   - O campo de título recebe foco automático.
4. Preencha o título (ex.: "Nova Síntese Espacial"), escolha a seção inicial "Resumo" e pressione `Enter`.
5. **Resultado esperado**:
   - O estudo é criado e persistido no capítulo via `POST /api/studies`.
   - Um novo cartão cartesiano surge posicionado na coordenada do clique e permanece no local após recarregar a tela.

---

### Cenário 2: Movimentação Cartesiana Livre e Persistência Debounced (US1)
1. Clique e arraste um cartão de estudo para uma nova posição na mesa de trabalho.
2. Observe o movimento suave com aceleração de hardware.
3. Solte o cartão.
4. **Resultado esperado**:
   - As novas coordenadas `(x, y)` são sincronizadas via `POST /api/canvas/batch` com debounce transparente de 500ms.
   - Ao recarregar a página ou alternar de view e voltar, o cartão permanece na mesma coordenada exata.

---

### Cenário 3: Criação de Moldura Temática e Movimento Solidário (US2)
1. Na barra de ferramentas (`CanvasToolbar`), selecione a ferramenta **Moldura** (`frame`) ou clique em "+ Moldura".
2. Clique e arraste no canvas desenhando um retângulo que envolva dois ou mais cartões de estudo.
3. **Resultado esperado**:
   - Uma moldura colorida é criada no fundo, com título padrão editável e alças de redimensionamento nos 4 cantos e bordas.
4. Clique no cabeçalho da moldura e arraste-a para outra região do canvas.
5. **Resultado esperado**:
   - Todos os cartões contidos no interior da moldura movem-se solidariamente com ela, mantendo suas posições relativas milimetricamente intactas.

---

### Cenário 4: Traçado de Conexões Direcionadas e Relações Semânticas (US3)
1. Selecione a ferramenta de conexão (`connect`) ou clique na alça conectora de um cartão de estudo.
2. Arraste a linha elástica até outro cartão vizinho.
3. **Resultado esperado**:
   - Abre-se o mini-popover contextual de relações semânticas ancorado no destino.
   - O usuário escolhe o tipo (*fundamenta*, *desdobra*, etc.) e confirma.
   - Uma aresta curva direcionada com seta indicativa e badge semântico é desenhada entre os dois cartões.

---

### Cenário 5: Alinhamento Magnético (Smart Guides), Minimapa e Mobile (US3)
1. Ao arrastar um cartão de estudo, aproxime-o lentamente da borda ou centro de outro cartão vizinho (dentro de $\pm 10$px).
2. **Resultado esperado**:
   - O cartão encaixa suavemente com atração magnética e projeta linhas guias pontilhadas temporárias na cor de acento.
3. Clique em uma região distante no mini-mapa no canto inferior direito.
4. **Resultado esperado**:
   - A câmera centraliza instantaneamente no quadrante clicado.
5. Reduza a viewport para resolução mobile (< 768px).
6. **Resultado esperado**:
   - A barra tátil de rodapé exibe ferramentas com alvos mínimos de 44×44px e suporta gestos nativos de toque e pinça.

---
