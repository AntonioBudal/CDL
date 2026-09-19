# Architecture & Design Research: 011 — Monolítica: Superclasse Pesada & Solene

**Feature**: 011 — Monolítica: Superclasse Pesada & Solene (Brutalista & Arquitetura em Pedra)  
**Date**: 2026-09-19  
**Status**: Completed  

---

## 1. Problema & Filosofia de Design

A interface do Caderno de Leitura já conta com quatro superclasses de movimento:
- **Zero-G**: flutuante, elástica e magnética.
- **Mecânica**: tátil, imediata, switches rápidos e corte seco.
- **Invisível**: silenciosa, editorial, sem caixas e com fluxo progressivo.
- **Dimensional**: perspectiva 3D, tilt angular delimitado e relevo em camadas.

A quinta e última superclasse, **Monolítica**, fecha o espectro de sensações físicas introduzindo a estética de **arquitetura brutalista, arquivos perpétuos, pedras lapidares e bibliotecas monumentais**. A interface deve transmitir permanência, solidez deliberada, austeridade e peso físico.

---

## 2. Decisões Arquiteturais e Técnicas

### Decisão 1: Geometria Brutalista e Cantos Rigorosamente Retos (`border-radius: 0px`)
- **Escolha**: Declarar `--sc-border-radius: 0px !important;` e aplicar nos recipientes estruturais: `.book-card`, `.panel`, `button`, `.button`, `.btn`, `input`, `textarea`, `select`, `.appearance-group`, `.category-badge`.
- **Racional**: Cantos arredondados suavizam interfaces e transmitem maleabilidade de plástico. A estética brutalista apoia-se em ângulos retos puros, prismas sólidos e cortes lapidares sem qualquer chanfro ou suavização circular.
- **Alternativas descartadas**: Manter raio de 2px (isso colidiria com a Superclasse Mecânica, que já adota cantos de 2px com switches). A Monolítica exige zero absoluto (`0px`).

### Decisão 2: Supressão Total de Sombras Flutuantes e Realce por Bordas Estruturais
- **Escolha**:
  - `--sc-shadow-idle: none;`
  - `--sc-shadow-hover: none;`
  - `--sc-shadow-active: none;`
  - Bordas estruturais sólidas: `--sc-border-width: calc(var(--border-width, 1px) + 1px);` com cor forte (`border-color: var(--color-border-strong)` ou `var(--color-text)` em destaque).
- **Racional**: Sombras difusas e gaussianas sugerem que os elementos estão pairando sobre uma superfície. Na arquitetura brutalista, a estrutura **é** a própria superfície: os blocos repousam com peso pleno sobre a fundação. O relevo visual emerge das demarcações de linha espessa e contraste maciço.
- **Alternativas descartadas**: Sombras sólidas duras com offset (já utilizadas na Superclasse Mecânica). A Monolítica prescinde de sombras projetadas, confiando no peso geométrico puro.

### Decisão 3: Microinterações Ponderadas e Inversão de Alto Contraste
- **Escolha**:
  - No hover (`:hover`), o elemento não sobe nem flutua (`transform: none !important;`). Ele transita lentamente em tom de contraste (`background-color`, `border-color`) com curva ponderada e solene em ~380ms (`cubic-bezier(0.25, 1, 0.5, 1)`).
  - No clique (`:active`), os botões respondem com inversão brutalista de alto contraste (fundo com a cor do texto e texto com a cor de fundo, ou realce denso de borda), sem deslocamento vertical.
- **Racional**: A resposta tátil da pedra não é elástica nem compressiva; ela é uma presença estática imutável. A transição estendida e a inversão tonal direta transmitem monumentalidade e seriedade funcional.
- **Alternativas descartadas**: Efeito de afundamento push-down (pertence à Mecânica) ou atração magnética (pertence à Zero-G).

### Decisão 4: Transição de Rota Solene e Ponderada (Dissolução Lapidar)
- **Escolha**:
  - `.page-enter-active`: `opacity 380ms cubic-bezier(0.25, 1, 0.5, 1) !important; transform: none !important;`
  - `.page-leave-active`: `opacity 220ms ease !important; transform: none !important;`
  - `.page-enter-from`: `opacity: 0; transform: none !important;`
  - `.page-leave-to`: `opacity: 0; transform: none !important;`
- **Racional**: Navegar entre salas de um arquivo monumental não causa empurrões de câmera nem saltos espaciais. A dissolução ponderada em opacidade sem deslocamentos de viewport confere tranquilidade e solenidade à leitura.
- **Alternativas descartadas**: Cortes secos de 100ms (Mecânica), aproximações Z de 300ms (Dimensional) ou cascatas temporais verticais (Invisível).

### Decisão 5: Blindagem do Leitor e Acessibilidade Universal
- **Escolha**:
  - `.markdown-content`, `.markdown-content *`, `.study-section`, `.reader-tools` e `.reading-page` permanecem com `transform: none !important; animation: none !important;`.
  - Sob `prefers-reduced-motion: reduce` e `data-motion="off"`, `--sc-intensity: 0.0 !important;` e todas as durações tornam-se `0ms` imediatas (`transition: none !important; animation: none !important;`).
- **Racional**: Garante conformidade com o Artigo I e IV da Constituição do Projeto e atende leitores com sensibilidade vestibular.

---

## 3. Matriz Comparativa Final (As 5 Superclasses)

| Dimensão | Zero-G | Mecânica | Invisível | Dimensional | Monolítica |
|---|---|---|---|---|---|
| **Bordas / Raio** | Raio médio (`10px`), borda tênue | Raio curto (`2px`), facetado | Sem bordas laterais (`0px`), linha tênue inferior | Raio médio (`8px`), refinado | Estritamente reto (`0px`), bordas espessas |
| **Sombras** | Ampla, difusa, multicamada | Sólida, dura, offset sem blur | Nenhuma sombra de caixa | Dinâmica projetada em perspectiva | Nenhuma sombra (`box-shadow: none`) |
| **Hover** | Atração magnética + levitação | Elevação rápida (`-1px`) | Deslocamento lateral + sublinhado | Tilt 3D (±1.5°/±2.0°) + paralaxe | Preenchimento ponderado (~380ms), imóvel |
| **Clique (Active)** | Amortecimento elástico | Push-down (`+3px`), colapso | Realce tipográfico | Retração Z sutil | Inversão brutalista de alto contraste |
| **Transição de Rota**| Amortecimento elástico (400ms) | Corte seco rápido (100ms) | Cascata temporal (*staggered fade-up*) | Aproximação Z (300ms) | Dissolução solene e lapidar (380ms) |
