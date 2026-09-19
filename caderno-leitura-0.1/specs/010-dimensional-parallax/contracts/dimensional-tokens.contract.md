# Contract: Dimensional CSS Tokens & 3D Parallax Physics

**Feature**: 010 — Dimensional: Superclasse Cinemática & Profunda (3D Parallax Espacial)  
**Date**: 2026-09-19  
**Status**: Ready  

---

## 1. Escopo e Mapeamento de Variáveis

A Superclasse Dimensional é ativada pelo atributo ou classe no elemento ancestral:
```css
:is(:root[data-superclass="dimensional"], .superclass-dimensional) {
  --sc-border-radius: calc(var(--radius-card, 8px));
  --sc-perspective: 1000px;
  --sc-tilt-max-x: calc(1.5deg * var(--sc-intensity));
  --sc-tilt-max-y: calc(2.0deg * var(--sc-intensity));
  --sc-shadow-idle: 0 6px 16px -2px rgba(0, 0, 0, 0.08), 0 16px 36px -6px rgba(0, 0, 0, 0.06);
  --sc-transition-duration: 320ms;
  --sc-transition-easing: cubic-bezier(0.16, 1, 0.3, 1);
}
```

### Escalonamento de Intensidade (`--sc-intensity`)
- `off` / `prefers-reduced-motion: reduce` / `data-motion="off"`: `--sc-intensity: 0.0 !important;`
- `subtle`: `--sc-intensity: 0.5;`
- `standard`: `--sc-intensity: 1.0;`
- `high`: `--sc-intensity: 1.5;`

---

## 2. Contrato de Tilt 3D nos Cartões do Acervo

A inclinação angular utiliza as coordenadas normalizadas `--sc-magnetic-x` e `--sc-magnetic-y` (fornecidas por `useMagneticHover.ts`):

```css
:is(:root[data-superclass="dimensional"], .superclass-dimensional) .book-card {
  border-radius: var(--sc-border-radius);
  box-shadow: var(--sc-shadow-idle);
  transform-style: preserve-3d;
  transform:
    perspective(var(--sc-perspective))
    rotateX(calc(var(--sc-magnetic-y, 0) * -1.5deg * var(--sc-intensity)))
    rotateY(calc(var(--sc-magnetic-x, 0) * 2.0deg * var(--sc-intensity)))
    translateZ(0);
  transition:
    transform var(--sc-transition-duration) var(--sc-transition-easing),
    box-shadow var(--sc-transition-duration) var(--sc-transition-easing),
    border-color 200ms ease;
  will-change: transform, box-shadow;
}

:is(:root[data-superclass="dimensional"], .superclass-dimensional) .book-card:hover {
  box-shadow:
    calc(var(--sc-magnetic-x, 0) * -6px * var(--sc-intensity))
    calc(var(--sc-magnetic-y, 0) * -6px * var(--sc-intensity) + 14px)
    32px -4px rgba(0, 0, 0, 0.14),
    0 24px 56px -8px rgba(0, 0, 0, 0.08);
}
```

---

## 3. Contrato de Parallax Interno Multicamada

Elementos internos do cartão acompanham o vetor do cursor em proporções escalonadas:

```css
/* Camada 1: Miniatura da Capa */
:is(:root[data-superclass="dimensional"], .superclass-dimensional) .book-card .book-card-cover-wrapper {
  transform: translate3d(
    calc(var(--sc-magnetic-x, 0) * 1px * var(--sc-intensity)),
    calc(var(--sc-magnetic-y, 0) * 1px * var(--sc-intensity)),
    0
  );
  transition: transform var(--sc-transition-duration) var(--sc-transition-easing);
  will-change: transform;
}

/* Camada 2: Título da Obra */
:is(:root[data-superclass="dimensional"], .superclass-dimensional) .book-card h2 {
  transform: translate3d(
    calc(var(--sc-magnetic-x, 0) * 2px * var(--sc-intensity)),
    calc(var(--sc-magnetic-y, 0) * 2px * var(--sc-intensity)),
    0
  );
  transition: transform var(--sc-transition-duration) var(--sc-transition-easing);
  will-change: transform;
}

/* Camada 3: Marcador, Ação e Badges */
:is(:root[data-superclass="dimensional"], .superclass-dimensional) .book-card :is(
  .book-number,
  .card-action,
  .category-badge
) {
  transform: translate3d(
    calc(var(--sc-magnetic-x, 0) * 3px * var(--sc-intensity)),
    calc(var(--sc-magnetic-y, 0) * 3px * var(--sc-intensity)),
    0
  );
  transition: transform var(--sc-transition-duration) var(--sc-transition-easing);
  will-change: transform;
}
```

---

## 4. Contrato de Botões e Controles Globais

```css
:is(:root[data-superclass="dimensional"], .superclass-dimensional) :is(button, .button, .btn) {
  border-radius: var(--sc-border-radius);
  box-shadow: 0 3px 8px -1px rgba(0, 0, 0, 0.12);
  transform: translateZ(0);
  transition:
    transform var(--sc-transition-duration) var(--sc-transition-easing),
    box-shadow var(--sc-transition-duration) var(--sc-transition-easing);
}

:is(:root[data-superclass="dimensional"], .superclass-dimensional) :is(button, .button, .btn):hover:not(:disabled) {
  transform: translateY(calc(-2px * var(--sc-intensity))) scale(calc(1 + (0.005 * var(--sc-intensity))));
  box-shadow: 0 8px 20px -2px rgba(0, 0, 0, 0.18);
}

:is(:root[data-superclass="dimensional"], .superclass-dimensional) :is(button, .button, .btn):active:not(:disabled) {
  transform: translateY(calc(1px * var(--sc-intensity))) scale(0.99);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.10);
}
```

---

## 5. Contrato de Transição de Rota Cinemática

```css
:is(:root[data-superclass="dimensional"], .superclass-dimensional) .page-enter-active {
  transition:
    opacity 300ms cubic-bezier(0.16, 1, 0.3, 1),
    transform 300ms cubic-bezier(0.16, 1, 0.3, 1) !important;
}

:is(:root[data-superclass="dimensional"], .superclass-dimensional) .page-leave-active {
  transition:
    opacity 180ms ease,
    transform 180ms ease !important;
}

:is(:root[data-superclass="dimensional"], .superclass-dimensional) .page-enter-from {
  opacity: 0;
  transform: scale(calc(1 - (0.015 * var(--sc-intensity)))) translateY(calc(4px * var(--sc-intensity))) !important;
}

:is(:root[data-superclass="dimensional"], .superclass-dimensional) .page-leave-to {
  opacity: 0;
  transform: scale(calc(1 + (0.01 * var(--sc-intensity)))) !important;
}
```

---

## 6. Blindagem de Leitura

```css
:is(:root[data-superclass="dimensional"], .superclass-dimensional) :is(
  .markdown-content,
  .markdown-content *,
  .study-section,
  .reader-tools,
  .reading-page
) {
  transform: none !important;
  animation: none !important;
}
```
