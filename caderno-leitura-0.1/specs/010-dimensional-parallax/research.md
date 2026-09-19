# Research & Technical Decisions: 010 — Dimensional: Superclasse Cinemática & Profunda

**Feature**: 010 — Dimensional: Superclasse Cinemática & Profunda (3D Parallax Espacial)  
**Date**: 2026-09-19  
**Status**: Completed  

---

## 1. Pesquisa & Decisões Arquiteturais

### Decisão 1: Aproveitamento do Motor de Interação Existente (`useMagneticHover`) para o Tilt 3D
- **Contexto**: Para calcular a inclinação angular dos cartões nos eixos X e Y (*tilt 3D*), é necessário conhecer a posição normalizada do cursor em relação ao centro do elemento interativo.
- **Decisão**: Reutilizar diretamente os valores normalizados `--sc-magnetic-x` e `--sc-magnetic-y` calculados em tempo real pelo composable [`useMagneticHover.ts`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/composables/useMagneticHover.ts), já vinculado a todos os `.book-card` do acervo.
- **Rationale**: 
  - Evita duplicação de listeners e composables desnecessários.
  - As variáveis locais são normalizadas em `[-1.0, 1.0]`, permitindo que o CSS compute `rotateX` e `rotateY` via `calc()` puro sem overhead de runtime.
  - Ao retirar o cursor (`pointerleave`), `useMagneticHover` redefine automaticamente as variáveis para `0`, restaurando a posição neutra com desaceleração inercial suave.
- **Alternativas consideradas**:
  - *Biblioteca externa de tilt (VanillaTilt / Tilt.js)*: Rejeitada. Violaria a proibição de dependências externas pesadas e impactaria a performance de carregamento.
  - *Diretiva personalizada Vue*: Desnecessária, pois o composable existente já atende com perfeição.

### Decisão 2: Limites Estritos de Segurança Física para Ângulos de Rotação
- **Contexto**: Efeitos 3D mal dosados em páginas web frequentemente causam desconforto visual, cansaço ou sensação de "vitrine comercial".
- **Decisão**: Fixar limites angulares máximos de rotação em:
  - Eixo X (inclinação vertical): **±1.5°** (`--sc-tilt-max-x: calc(1.5deg * var(--sc-intensity))`).
  - Eixo Y (inclinação horizontal): **±2.0°** (`--sc-tilt-max-y: calc(2.0deg * var(--sc-intensity))`).
  - Perspectiva ótica: **1000px** (`perspective: 1000px`).
- **Rationale**: 
  - Os valores produzem uma sensação tátil refinada e discreta de relevo arquitetural sem deformar a legibilidade dos títulos ou causar fadiga visual.
- **Alternativas consideradas**:
  - *Rotação ampla (±10° a ±15°)*: Rejeitada categoricamente por violar a identidade sóbria e focada em leitura do Caderno.

### Decisão 3: Parallax Multicamada Interno Baseado em Offsets Relativos
- **Contexto**: A ilusão de profundidade tridimensional completa requer que diferentes planos visuais se movam com velocidades distintas sob o mesmo vetor de cursor.
- **Decisão**: Mapear as subcamadas dos cartões com deslocamentos defasados via GPU:
  - Miniatura da Capa (`.book-card-cover-wrapper`): `1px * var(--sc-intensity)`.
  - Título da Obra (`.book-card h2`): `2px * var(--sc-intensity)`.
  - Marcadores e Ações (`.book-number`, `.card-action`, badges): `3px * var(--sc-intensity)`.
- **Rationale**:
  - Camadas internas não exigem nós DOM extras, operando diretamente nos seletores existentes com `translate3d`.
- **Alternativas consideradas**:
  - *Uso de `transform-style: preserve-3d` com `translateZ` elevado*: Testes em navegadores móveis mostraram potencial risco de aliasing e blur em fontes. O uso de `translate3d(X, Y, 0)` proporcional mantém a nitidez do texto no padrão Retina/HiDPI.

### Decisão 4: Transição de Rota Cinemática por Aproximação Z
- **Contexto**: Na Superclasse Mecânica, as rotas usam corte seco linear (100ms); na Invisível, usam cascata temporal de 240ms. A Dimensional deve expressar profundidade espacial cinematográfica.
- **Decisão**: Implementar transição de rota com aproximação suave de profundidade (`scale(0.985) → scale(1.0)` com leve subida `translateY(4px → 0)`) em `300ms–320ms` acelerada por GPU com `cubic-bezier(0.16, 1, 0.3, 1)`.
- **Rationale**:
  - Conecta a experiência de tela cheia à linguagem física de profundidade dos cartões.

### Decisão 5: Blindagem do Leitor e Acessibilidade Universal
- **Contexto**: O modo de leitura de capítulos e estudos requer foco e conforto absoluto.
- **Decisão**:
  - `.markdown-content` e derivados recebem `transform: none !important; animation: none !important;`.
  - `prefers-reduced-motion: reduce` e `data-motion="off"` forçam `--sc-intensity: 0.0 !important;` e suprimem todas as rotações angulares, tilts e aproximações de escala.

---

## 2. Matriz de Compatibilidade e Tecnologias
- **Folha de Estilos**: `frontend/src/styles/superclasses/dimensional.css`.
- **Import Global**: `frontend/src/style.css`.
- **Suporte a Navegadores**: Chrome/Edge 105+, Firefox 110+, Safari 16.4+ (suporte integral a CSS nesting, `calc()`, `perspective` e `color-mix()`).
