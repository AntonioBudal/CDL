# Contract: Invisível CSS Tokens & Editorial Physics

**Date**: 2026-09-19  
**Feature**: 009 — Invisível: Superclasse Silenciosa & Editorial e Limpeza de Ajustes  
**Status**: Ready  

---

## 1. CSS Variable Mapping & Formula Contracts

### Escopo e Raiz
A Superclasse Invisível é ativada via classe ou atributo no `:root` ou elemento ancestral:
```css
:is(:root[data-superclass="invisivel"], .superclass-invisivel) {
  --sc-border-radius: 0px;
  --sc-shadow-idle: none;
  --sc-shadow-hover: none;
  --sc-shadow-active: none;
  --sc-reading-shift-x: calc(4px * var(--sc-intensity));
  --sc-transition-duration: 200ms;
  --sc-transition-easing: cubic-bezier(0.2, 0, 0, 1);
}
```

### Escalonamento de Intensidade (`--sc-intensity`)
- `off` / `prefers-reduced-motion: reduce` / `data-motion="off"`: `--sc-intensity: 0.0 !important;`
- `subtle`: `--sc-intensity: 0.5;`
- `standard`: `--sc-intensity: 1.0;`
- `high`: `--sc-intensity: 1.5;`

---

## 2. Contrato de Desmaterialização de Caixas

Cartões do acervo e itens de lista (`.book-card`, `.book-list-item`, `.panel`, `.appearance-group`):
- Sem bordas laterais ou caixas fechadas.
- Fundo transparente ou plano, integrado ao background da página.
- Divisores suaves baseados em margens e linhas tênues editoriais:
```css
:is(:root[data-superclass="invisivel"], .superclass-invisivel) :is(.book-card, .book-list-item) {
  background: transparent !important;
  border: none !important;
  border-bottom: 1px solid color-mix(in srgb, var(--color-border) 30%, transparent) !important;
  border-radius: 0 !important;
  box-shadow: none !important;
  transition: transform var(--sc-transition-duration) var(--sc-transition-easing);
}
```

---

## 3. Contrato de Microinterações Editoriais

### Deslocamento Horizontal de Leitura (Shift Lateral)
Ao passar o mouse sobre itens do acervo, botões editoriais ou títulos:
```css
:is(:root[data-superclass="invisivel"], .superclass-invisivel) :is(.book-card, .book-list-item):hover {
  transform: translateX(var(--sc-reading-shift-x));
}
```

### Sublinhado Progressivo em Links e Títulos
Linha sutil desenhada da esquerda para a direita:
```css
:is(:root[data-superclass="invisivel"], .superclass-invisivel) .text-link,
:is(:root[data-superclass="invisivel"], .superclass-invisivel) .book-card h2 a,
:is(:root[data-superclass="invisivel"], .superclass-invisivel) .chapter-list a {
  position: relative;
  text-decoration: none;
}

:is(:root[data-superclass="invisivel"], .superclass-invisivel) .text-link::after,
:is(:root[data-superclass="invisivel"], .superclass-invisivel) .book-card h2 a::after,
:is(:root[data-superclass="invisivel"], .superclass-invisivel) .chapter-list a::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: -2px;
  width: 100%;
  height: 1.5px;
  background-color: var(--color-accent);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform var(--sc-transition-duration) var(--sc-transition-easing);
}

:is(:root[data-superclass="invisivel"], .superclass-invisivel) :is(.text-link, .book-card:hover h2 a, .chapter-list a:hover)::after {
  transform: scaleX(1);
}
```

---

## 4. Contrato de Botões Editoriais

Botões globais (`button`, `.button`, `.btn`):
- Desprovidos de relevo plástico; comportam-se como botões tipográficos elegantes:
```css
:is(:root[data-superclass="invisivel"], .superclass-invisivel) :is(button, .button, .btn) {
  border-radius: 0;
  box-shadow: none !important;
  border-width: 1px;
  transition:
    transform var(--sc-transition-duration) var(--sc-transition-easing),
    background-color var(--sc-transition-duration) ease,
    border-color var(--sc-transition-duration) ease;
}

:is(:root[data-superclass="invisivel"], .superclass-invisivel) :is(button, .button, .btn):hover:not(:disabled) {
  transform: translateX(calc(2px * var(--sc-intensity)));
}
```

---

## 5. Contrato de Transição em Cascata (*Staggered Fade-Up*)

```css
@keyframes sc-invisivel-fade-up {
  from {
    opacity: 0;
    transform: translateY(calc(6px * var(--sc-intensity)));
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

:is(:root[data-superclass="invisivel"], .superclass-invisivel) .page-enter-active .page-header {
  animation: sc-invisivel-fade-up 240ms cubic-bezier(0.2, 0, 0, 1) 0ms both;
}

:is(:root[data-superclass="invisivel"], .superclass-invisivel) .page-enter-active :is(.reader-heading, .breadcrumb, .intro) {
  animation: sc-invisivel-fade-up 240ms cubic-bezier(0.2, 0, 0, 1) 40ms both;
}

:is(:root[data-superclass="invisivel"], .superclass-invisivel) .page-enter-active :is(.reader-analysis, .book-grid, .chapter-layout) {
  animation: sc-invisivel-fade-up 240ms cubic-bezier(0.2, 0, 0, 1) 80ms both;
}
```

---

## 6. Blindagem de Leitura

```css
:is(:root[data-superclass="invisivel"], .superclass-invisivel) :is(
  .markdown-content,
  .markdown-content *,
  .study-section,
  .reader-tools
) {
  transform: none !important;
  animation: none !important;
}
```
