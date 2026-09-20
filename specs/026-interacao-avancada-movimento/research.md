# Technical Research: F10 — Interação Avançada, Movimento e Experiências Visuais

**Feature Branch**: `026-interacao-avancada-movimento`  
**Date**: 2026-09-19  
**Status**: Completed  

---

## 1. Arquitetura Gráfica e Motor de Aceleração para Grafos Densos

### Decisão
Adotar uma **arquitetura híbrida de renderização** baseada exclusivamente na API padrão **HTML5 Canvas 2D**:
- **Plano de Fundo Acelerado (`CanvasAcceleratedLayer.vue`)**: Um elemento `<canvas>` posicionado como camada inferior, responsável por desenhar conexões, curvas de Bézier e setas direcionais em lote (*path batching*) via `requestAnimationFrame` quando a contagem de nós visíveis atingir ou superar 60 elementos.
- **Plano de Interatividade e Cartões (DOM/HTML/Vue 3)**: Os nós e cartões permanecem como componentes Vue ricos em DOM (`CanvasNode.vue`, `CanvasFrameNode.vue`), usufruindo da estilização por classes Tailwind, seleção de texto, formulários e acessibilidade nativa sem a complexidade de reconstruir eventos de ponteiro em WebGL.
- **Camada Alternativa SVG (< 60 nós)**: Para grafos pequenos/moderados (< 60 nós), mantém-se a camada SVG existente (`CanvasConnectionsLayer.vue`), assegurando fidelidade vetorial perfeita e transição sem atrito.

### Justificativa
- **Zero Dependências Externas**: Dispensa a inclusão de bibliotecas pesadas (como Pixi.js ou Three.js), evitando sobrecarregar o pacote empacotado (`dist/`) e eliminando riscos de incompatibilidade ou vazamento de contexto WebGL (`WebGLContextLost`).
- **Performance a 60fps**: O Canvas 2D com hardware acceleration nativa dos navegadores modernos desenha mais de 1.000 curvas simultâneas em menos de 2ms por quadro, superando com folga o orçamento de 16.6ms para 60fps.
- **Desalocação Limpa**: O contexto 2D não retém texturas pesadas na VRAM; no hook `onUnmounted`, basta cancelar o `cancelAnimationFrame` e limpar a referência do canvas.

### Alternativas Consideradas
- *Pixi.js v8 / Three.js (WebGL)*: Rejeitado por adicionar centenas de kilobytes ao bundle final e trazer complexidade desnecessária para curvas 2D em um caderno de leitura.
- *Manter 100% SVG mesmo com centenas de nós*: Rejeitado porque o DOM do SVG sofre engasgos de reflow e repaint (*jank*) quando centenas de elementos `<path>` são transladados e redimensionados simultaneamente em pan/zoom.

---

## 2. Física Inercial e Modelagem Matemática das 5 Superclasses

### Decisão
Implementar um composable unificado e leve `useSuperclassPhysics.ts` que parametriza constantes cinemáticas de acordo com a Superclasse ativa e a intensidade configurada pelo usuário (0% a 100%):

| Superclasse | Comportamento Cinemático | Constantes Físicas Principais | Micro-resposta Tátil |
|---|---|---|---|
| **Zero-G** | Flutuação inercial contínua sem atrito estático; conexões ondulatórias fluidas | Fricção baixa (\(k_f \approx 0.96\)), mola suave (\(k_s \approx 0.05\)), deriva temporal (\(t_{decay} \approx 600ms\)) | Desaceleração suave, ondulação senoidal na aresta ao soltar |
| **Mecânica** | Movimento indexado em grade (*snap-to-grid* de 20px) com retenção rígida | Fricção de parada alta (\(k_f \approx 0.82\)), mola rápida (\(k_s \approx 0.28\)), acomodação seca (\(t_{decay} \approx 120ms\)) | Micro-pulso visual tátil (`pulse-snap`) de 80ms no ponto de ancoragem |
| **Invisível** | Calmaria visual absoluta; molduras e conexões latentes | Fricção moderada (\(k_f \approx 0.90\)), fade progressivo por distância do cursor (\(d_{threshold} \approx 140px\)) | Revelação etérea e dissolução suave sem choque mecânico |
| **Dimensional** | Profundidade espacial 2.5D com paralaxe multi-camada e elevação sombreada | Fator de paralaxe Z (\(p_z \in [0.4, 1.6]\)), sombra dinâmica proporcional à velocidade | Inclinação (*tilt*) e projeção de sombra amplificada durante arrasto |
| **Monolítica** | Estabilidade brutalista; nós ancorados sem qualquer inércia ou oscilação | Fricção instantânea (\(k_f = 0\)), transição linear estrita, sem overshoot de mola | Borda de alto contraste instantânea, parada seca imediata |

### Justificativa
- A matemática de interpolação por amortecimento exponencial e molas simples (*critically damped spring*) não requer bibliotecas de física complexas, executando em menos de 0.05ms por iteração.
- A intensidade (`caderno_superclass_intensity`, 0 a 1) atua como multiplicador paramétrico direto: em 0, os coeficientes de inércia e oscilação colapsam para 0 (imobilidade estática imediata).

### Alternativas Consideradas
- *Biblioteca de física externa (Matter.js / Popmotion)*: Descartada por peso desnecessário e risco de simulações caóticas não condizentes com um software sóbrio de leitura.

---

## 3. Feedback Háptico Visual e Acessibilidade (`prefers-reduced-motion`)

### Decisão
1. **Feedback Háptico Visual**:
   - Criação de utilitário CSS/JS leve que aplica temporariamente o atributo `data-haptic-pulse="snap | connect | step"` ao elemento alvo, disparando uma micro-interação visual discreta de 80ms (pulso de escala de 1.02x ou brilho de contorno sutil), com efeito auditivo/tátil virtualizado.
   - Aplicação em: ancoragem de nós no Canvas, união de arestas no Mapa, reordenação de itens na Árvore Hierárquica (`StudyTreeView`) e detecção de passos nos sliders de `SettingsView`.
2. **Respeito a `prefers-reduced-motion: reduce`**:
   - Detecção reativa via `window.matchMedia('(prefers-reduced-motion: reduce)')`.
   - Quando ativado, desliga instantaneamente todos os laços de interpolação inercial, amortecimento elástico e paralaxe multi-camada. Os nós acompanham o ponteiro de forma 1:1 e cessam o movimento imediatamente ao soltar o mouse/touch.
3. **Ergonomia Móvel e Sobriedade em Leitura**:
   - Em telas sensíveis ao toque (`window.matchMedia('(pointer: coarse)')`), a translação de viewport no Canvas/Mapa é delegada ao gesto tátil do navegador, evitando simulações redundantes em JavaScript para economizar bateria e evitar aquecimento térmico.
   - Nas visualizações de leitura e fichamento (`StudyView.vue`, `StudyEditView.vue`), a física e os shaders espaciais são 100% inativos.
