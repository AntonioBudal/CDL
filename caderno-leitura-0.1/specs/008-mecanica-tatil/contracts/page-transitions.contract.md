# Contract: Vue Router Page Transitions under Mecânica

**Date**: 2026-09-19  
**Feature**: 008 — Mecânica: Superclasse Tátil & Responsiva  
**Status**: Ready  

---

## 1. Overview & Propósito

Sob a Superclasse Mecânica, a navegação entre telas/rotas do aplicativo deve abandonar transições lentas, fades graduais ou deslizes elásticos. Em vez disso, emula o corte seco rápido de consoles e instrumentos de medição.

---

## 2. Contrato de Transição Vue Router

A transição global do Vue Router `<Transition name="page" mode="out-in">` em `App.vue` responde às seguintes classes sob o seletor da Mecânica:

```css
:is(:root[data-superclass="mecanica"], .superclass-mecanica) .page-enter-active,
:is(:root[data-superclass="mecanica"], .superclass-mecanica) .page-leave-active {
  transition: opacity 100ms linear !important;
}

:is(:root[data-superclass="mecanica"], .superclass-mecanica) .page-enter-from,
:is(:root[data-superclass="mecanica"], .superclass-mecanica) .page-leave-to {
  opacity: 0;
  transform: none !important; /* Sem translacao em Y para evitar desfoque ou atraso */
}
```

---

## 3. Comportamento com Movimento Reduzido

Quando `prefers-reduced-motion: reduce` ou `data-motion="off"` estiverem ativos:
```css
@media (prefers-reduced-motion: reduce) {
  :is(:root[data-superclass="mecanica"], .superclass-mecanica) .page-enter-active,
  :is(:root[data-superclass="mecanica"], .superclass-mecanica) .page-leave-active {
    transition: none !important;
  }
}

:root[data-motion="off"] .page-enter-active,
:root[data-motion="off"] .page-leave-active {
  transition: none !important;
}
```
A troca de rota ocorre de forma instantânea sem interpolação.
