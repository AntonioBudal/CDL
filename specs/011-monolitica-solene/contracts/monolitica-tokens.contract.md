# Contract: Monolítica CSS Tokens & Brutalist Architectural Physics

**Feature**: 011 — Monolítica: Superclasse Pesada & Solene (Brutalista & Arquitetura em Pedra)  
**Date**: 2026-09-19  
**Status**: Ready  

---

## 1. Escopo e Mapeamento de Variáveis

A Superclasse Monolítica é ativada pelo atributo ou classe no elemento ancestral:
```css
:is(:root[data-superclass="monolitica"], .superclass-monolitica) {
  --sc-border-radius: 0px !important;
  --sc-border-width: calc(var(--border-width, 1px) + 1px);
  --sc-shadow-idle: none !important;
  --sc-shadow-hover: none !important;
  --sc-shadow-active: none !important;
  --sc-transition-duration: 380ms;
  --sc-transition-easing: cubic-bezier(0.25, 1, 0.5, 1);
}
```

### Escalonamento de Intensidade (`--sc-intensity`)
- `off` / `prefers-reduced-motion: reduce` / `data-motion="off"`: `--sc-intensity: 0.0 !important;`
- `subtle`: `--sc-intensity: 0.5;`
- `standard`: `--sc-intensity: 1.0;`
- `high`: `--sc-intensity: 1.5;`

---

## 2. Contrato dos Cartões do Acervo (`.book-card`)

Os cartões assumem a forma de blocos sólidos retangulares sem cantos curvos e sem sombras flutuantes:

```css
:is(:root[data-superclass="monolitica"], .superclass-monolitica) .book-card {
  border-radius: var(--sc-border-radius);
  border: var(--sc-border-width) solid var(--color-border-strong);
  box-shadow: var(--sc-shadow-idle);
  transform: none !important;
  transition:
    background-color var(--sc-transition-duration) var(--sc-transition-easing),
    border-color var(--sc-transition-duration) var(--sc-transition-easing);
  will-change: background-color, border-color;
}

:is(:root[data-superclass="monolitica"], .superclass-monolitica) .book-card:hover {
  background-color: var(--color-surface-hover);
  border-color: var(--color-text);
  box-shadow: var(--sc-shadow-hover);
}

:is(:root[data-superclass="monolitica"], .superclass-monolitica) .book-card:active {
  background-color: var(--color-surface-soft);
  border-color: var(--color-text);
}
```

---

## 3. Contrato de Botões e Controles Globais

Botões representam blocos geométricos monolíticos maciços:

```css
:is(:root[data-superclass="monolitica"], .superclass-monolitica) :is(
  button,
  .button,
  .btn
) {
  border-radius: var(--sc-border-radius);
  border: var(--sc-border-width) solid currentColor;
  box-shadow: var(--sc-shadow-idle);
  transform: none !important;
  transition:
    background-color var(--sc-transition-duration) var(--sc-transition-easing),
    color var(--sc-transition-duration) var(--sc-transition-easing),
    border-color var(--sc-transition-duration) var(--sc-transition-easing);
}

:is(:root[data-superclass="monolitica"], .superclass-monolitica) :is(
  button,
  .button,
  .btn
):hover:not(:disabled) {
  transform: none !important;
  box-shadow: none !important;
  border-color: var(--color-text);
}

:is(:root[data-superclass="monolitica"], .superclass-monolitica) :is(
  button,
  .button,
  .btn
):active:not(:disabled) {
  transform: none !important;
  box-shadow: none !important;
  background-color: var(--color-text);
  color: var(--color-page);
}
```

---

## 4. Contrato de Campos de Formulário e Painéis

```css
:is(:root[data-superclass="monolitica"], .superclass-monolitica) :is(
  input[type="text"],
  input[type="number"],
  textarea,
  select,
  .panel,
  .appearance-group
) {
  border-radius: var(--sc-border-radius);
  border: var(--sc-border-width) solid var(--color-border-strong);
  box-shadow: none !important;
  transform: none !important;
  transition: border-color var(--sc-transition-duration) var(--sc-transition-easing);
}

:is(:root[data-superclass="monolitica"], .superclass-monolitica) :is(
  input:focus,
  textarea:focus,
  select:focus
) {
  outline: calc(var(--focus-width, 2px) + 1px) solid var(--color-text);
  outline-offset: 1px;
  border-color: var(--color-text);
}
```

---

## 5. Contrato de Transição de Rota Solene (Dissolução Lapidar)

```css
:is(:root[data-superclass="monolitica"], .superclass-monolitica) .page-enter-active {
  transition: opacity 380ms cubic-bezier(0.25, 1, 0.5, 1) !important;
  transform: none !important;
}

:is(:root[data-superclass="monolitica"], .superclass-monolitica) .page-leave-active {
  transition: opacity 220ms ease !important;
  transform: none !important;
}

:is(:root[data-superclass="monolitica"], .superclass-monolitica) .page-enter-from,
:is(:root[data-superclass="monolitica"], .superclass-monolitica) .page-leave-to {
  opacity: 0 !important;
  transform: none !important;
}
```

---

## 6. Blindagem de Leitura

```css
:is(:root[data-superclass="monolitica"], .superclass-monolitica) :is(
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

---

## 7. Neutralização sob Acessibilidade

```css
@media (prefers-reduced-motion: reduce) {
  :is(:root[data-superclass="monolitica"], .superclass-monolitica) {
    --sc-intensity: 0.0 !important;
  }

  :is(:root[data-superclass="monolitica"], .superclass-monolitica) * {
    transition: none !important;
    animation: none !important;
  }
}

:root[data-motion="off"][data-superclass="monolitica"],
:root[data-motion="off"] .superclass-monolitica {
  --sc-intensity: 0.0 !important;
}

:is(
  :root[data-motion="off"][data-superclass="monolitica"],
  :root[data-motion="off"] .superclass-monolitica
) * {
  transition: none !important;
  animation: none !important;
}
```
