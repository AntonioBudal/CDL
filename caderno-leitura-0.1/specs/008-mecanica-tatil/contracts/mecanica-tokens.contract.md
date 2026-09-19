# Contract: Mecânica CSS Tokens & Tactile Physics

**Date**: 2026-09-19  
**Feature**: 008 — Mecânica: Superclasse Tátil & Responsiva  
**Status**: Ready  

---

## 1. CSS Variable Mapping & Formula Contracts

### Escopo e Raiz
A Superclasse Mecânica é ativada via classe ou atributo no `:root` ou elemento ancestral:
```css
:is(:root[data-superclass="mecanica"], .superclass-mecanica) {
  --sc-border-radius: 2px;
  --sc-shadow-idle: 0 calc(3px * var(--sc-intensity)) 0 var(--color-shadow, rgba(0, 0, 0, 0.35));
  --sc-shadow-hover: 0 calc(4px * var(--sc-intensity)) 0 var(--color-shadow, rgba(0, 0, 0, 0.45));
  --sc-shadow-active: 0 0 0 transparent;
  --sc-transition-duration: 100ms;
  --sc-transition-easing: linear;
}
```

### Escalonamento de Intensidade (`--sc-intensity`)
Herdado do subsistema base de Superclasses:
- `off` / `prefers-reduced-motion: reduce` / `data-motion="off"`: `--sc-intensity: 0.0 !important;`
- `subtle`: `--sc-intensity: 0.5;`
- `standard`: `--sc-intensity: 1.0;`
- `high`: `--sc-intensity: 1.5;`

---

## 2. Push-Down & Solid Shadow Contracts (Botões e Cartões)

Para qualquer elemento interativo (`button`, `.button`, `.btn`, `.book-card`, `.book-list-item`, `.tag-chip`, `.filter-chip`):

### Repouso (Idle)
```css
:is(:root[data-superclass="mecanica"], .superclass-mecanica) :is(button, .button, .btn, .book-card, .book-list-item) {
  border-radius: var(--sc-border-radius);
  box-shadow: var(--sc-shadow-idle);
  transform: translateY(0);
  transition:
    transform var(--sc-transition-duration) var(--sc-transition-easing),
    box-shadow var(--sc-transition-duration) var(--sc-transition-easing),
    border-color var(--sc-transition-duration) var(--sc-transition-easing);
  will-change: transform, box-shadow;
}
```

### Sobretela (Hover)
Elevação leve de 1px com expansão da sombra dura:
```css
:is(:root[data-superclass="mecanica"], .superclass-mecanica) :is(button, .button, .btn, .book-card, .book-list-item):hover {
  transform: translateY(calc(-1px * var(--sc-intensity)));
  box-shadow: var(--sc-shadow-hover);
}
```

### Clique / Ativação (Active / Push-Down)
Afundamento de 3px com anulação da sombra projetada (batente mecânico exato):
```css
:is(:root[data-superclass="mecanica"], .superclass-mecanica) :is(button, .button, .btn, .book-card, .book-list-item):active {
  transform: translateY(calc(3px * var(--sc-intensity)));
  box-shadow: var(--sc-shadow-active);
  transition-duration: calc(var(--sc-transition-duration) * 0.5); /* Resposta de descida em 50ms */
}
```

---

## 3. Contrato para Campos de Formulário e Entradas

Campos de texto (`input[type="text"]`, `input[type="number"]`, `input[type="search"]`, `textarea`, `select`):

### Repouso (Idle)
- Cantos secos: `border-radius: var(--sc-border-radius);`
- Sombra interna tipo cavidade (entrincheirado na chapa):
```css
:is(:root[data-superclass="mecanica"], .superclass-mecanica) :is(input[type="text"], input[type="number"], input[type="search"], textarea, select) {
  border-radius: var(--sc-border-radius);
  border: 1px solid var(--color-border);
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.12);
  transition: border-color var(--sc-transition-duration) var(--sc-transition-easing);
}
```

### Foco (Focus)
- Sem deslocamento vertical (`transform: none`).
- Borda instantaneamente contrastada e reforçada:
```css
:is(:root[data-superclass="mecanica"], .superclass-mecanica) :is(input[type="text"], input[type="number"], input[type="search"], textarea, select):focus {
  outline: none;
  border-color: var(--color-accent);
  box-shadow:
    inset 0 1px 3px rgba(0, 0, 0, 0.12),
    0 0 0 1px var(--color-accent);
}
```

---

## 4. Contrato de Switches / Toggles

Controles deslizantes de ativação (`[role="switch"]`, `.switch`, `.toggle`, `.toggle-indicator`):
- O pino/chave comuta de estado em velocidade ultrarrápida: `50ms` a `80ms` linear.
- Borda e fundo sem transições lentas ou elásticas.

```css
:is(:root[data-superclass="mecanica"], .superclass-mecanica) :is([role="switch"], .switch-handle, .toggle-knob) {
  transition: transform 60ms linear, background-color 60ms linear;
  border-radius: var(--sc-border-radius);
}
```

---

## 5. Contrato de Painéis, Caixas de Ajustes e Modais

Superfícies de contenção (`.appearance-group`, `.panel`, `.form-panel`, `.modal-content`):
- Cantos com acabamento quase reto (`2px`).
- Sombra de montagem dura sem blur:
```css
:is(:root[data-superclass="mecanica"], .superclass-mecanica) :is(.appearance-group, .panel, .form-panel, .modal-content) {
  border-radius: var(--sc-border-radius);
  border: 1px solid var(--color-border);
  box-shadow: 0 calc(2px * var(--sc-intensity)) 0 var(--color-shadow, rgba(0, 0, 0, 0.25));
}
```

---

## 6. Cláusula Pétrea de Imobilidade e Modo Leitura

Sob nenhuma hipótese os seguintes seletores recebem animação, afundamento ou deslocamento:
```css
:is(:root[data-superclass="mecanica"], .superclass-mecanica) :is(
  .markdown-content,
  .markdown-content *,
  .reader-tools,
  .reader-tools *,
  .study-view,
  .study-section
) {
  transform: none !important;
  animation: none !important;
}
```
Também não são permitidos keyframes de oscilação contínua (zero idle breathing) em cartões ou botões.
