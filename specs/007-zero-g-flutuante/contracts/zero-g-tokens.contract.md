# Contract: Zero-G CSS Tokens & Motion Behaviors

**Date**: 2026-09-19  
**Feature**: 007 — Zero-G: Superclasse Flutuante & Magnética  
**Status**: Ready  

---

## 1. CSS Variable Mapping & Formula Contracts

### Root Intensity Scoping
```css
:root {
  --sc-intensity: 1.0;
}

:root[data-superclass-intensity="subtle"] {
  --sc-intensity: 0.5;
}

:root[data-superclass-intensity="standard"] {
  --sc-intensity: 1.0;
}

:root[data-superclass-intensity="high"] {
  --sc-intensity: 1.5;
}

:root[data-superclass-intensity="off"] {
  --sc-intensity: 0.0;
}

@media (prefers-reduced-motion: reduce) {
  :root {
    --sc-intensity: 0.0 !important;
  }
}

:root[data-motion="off"] {
  --sc-intensity: 0.0 !important;
}
```

---

## 2. Geometry & Depth Elevation Contract

Quando `data-superclass="zero-g"` está ativo:

### Borda e Elevação de Cartões
```css
:root[data-superclass="zero-g"] .book-card {
  border-width: 1px;
  border-style: solid;
  border-color: color-mix(in srgb, var(--color-border) 45%, transparent);
  border-left-width: 1px; /* Remove marcadores duros na borda esquerda */
  box-shadow:
    0 4px 14px -2px rgba(0, 0, 0, 0.04),
    0 10px 28px -4px rgba(0, 0, 0, 0.06);
}

:root[data-superclass="zero-g"] .book-card:hover {
  box-shadow:
    0 12px 36px -4px rgba(0, 0, 0, 0.12),
    0 24px 60px -8px rgba(0, 0, 0, 0.08);
}
```

---

## 3. Motion & Physics Easing Contract

### Idle Breathing (Repouso)
- **Target**: `.book-grid > li`
- **Ciclo**: `5.4s` contínuo, `ease-in-out` infinito.
- **Fase**: `animation-delay: calc(var(--card-index, 0) * 240ms)`.
- **Amplitude**: `0` a `calc(-1px * var(--sc-intensity))`.

```css
@keyframes sc-zero-g-float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(calc(-1px * var(--sc-intensity)));
  }
}

:root[data-superclass="zero-g"] .book-grid > li {
  animation: sc-zero-g-float 5.4s ease-in-out infinite;
  animation-delay: calc(var(--card-index, 0) * 240ms);
  will-change: transform;
}
```

### Hover Magnético e Retorno Elástico
- **Target**: `.book-card`
- **Cálculo de Deslocamento**:
  $$\text{dx} = \text{calc}(\text{var}(--sc\text{-magnetic-x}, 0) \times 4\text{px} \times \text{var}(--sc\text{-intensity}))$$
  $$\text{dy} = \text{calc}(\text{var}(--sc\text{-magnetic-y}, 0) \times 4\text{px} \times \text{var}(--sc\text{-intensity}))$$
- **Curva de Retorno**: `cubic-bezier(0.16, 1, 0.3, 1)` com duração de `650ms`.

```css
:root[data-superclass="zero-g"] .book-card {
  transform: translate3d(
    calc(var(--sc-magnetic-x, 0) * 4px * var(--sc-intensity)),
    calc(var(--sc-magnetic-y, 0) * 4px * var(--sc-intensity)),
    0
  );
  transition:
    transform 650ms cubic-bezier(0.16, 1, 0.3, 1),
    box-shadow 650ms cubic-bezier(0.16, 1, 0.3, 1),
    border-color 300ms ease;
  will-change: transform, box-shadow;
}
```

---

## 4. Reading Mode Absolute Immobility Guarantee

Sob nenhuma circunstância os seguintes elementos ou seletores podem receber animações de oscilação, translações magnéticas ou alterações de posicionamento decorrentes da Superclasse:
- `.markdown-content` e todos os seus descendentes (`p`, `h1`-`h6`, `blockquote`, `ul`, `ol`, `code`, `pre`)
- `.reader-tools`
- `.study-view` e `.study-section`
- Campos de formulário e inputs (`input`, `textarea`, `select`)
