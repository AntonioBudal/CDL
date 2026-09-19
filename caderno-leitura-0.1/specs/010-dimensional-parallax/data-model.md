# Data Model & Physical State Specification: 010 — Dimensional

**Feature**: 010 — Dimensional: Superclasse Cinemática & Profunda (3D Parallax Espacial)  
**Date**: 2026-09-19  
**Status**: Completed  

---

## 1. Modelo de Tokens e Variáveis CSS da Dimensional

A Superclasse Dimensional introduz variáveis de perspectiva, inclinação angular e camadas de relevo sem criar entidades no banco de dados (100% no cliente frontend).

### Mapeamento de Tokens Físicos

| Token CSS | Escopo | Valor Padrão (1.0x) | Finalidade / Papel Físico |
|---|---|---|---|
| `--sc-border-radius` | `:is(:root[data-superclass="dimensional"], .superclass-dimensional)` | `calc(var(--radius-card, 8px))` | Cantos harmonizados com o tema ativo |
| `--sc-perspective` | `:is(:root[data-superclass="dimensional"], .superclass-dimensional)` | `1000px` | Ponto de fuga e profundidade de câmera |
| `--sc-tilt-max-x` | `:is(:root[data-superclass="dimensional"], .superclass-dimensional)` | `calc(1.5deg * var(--sc-intensity))` | Limite estrito de rotação vertical (tilt X) |
| `--sc-tilt-max-y` | `:is(:root[data-superclass="dimensional"], .superclass-dimensional)` | `calc(2.0deg * var(--sc-intensity))` | Limite estrito de rotação horizontal (tilt Y) |
| `--sc-shadow-idle` | `:is(:root[data-superclass="dimensional"], .superclass-dimensional)` | `0 6px 16px -2px rgba(0,0,0,0.08), 0 16px 36px -6px rgba(0,0,0,0.06)` | Sombra volumétrica de repouso |
| `--sc-shadow-hover` | `:is(:root[data-superclass="dimensional"], .superclass-dimensional)` | Dinâmica orientada pelo cursor com iluminação direcional | Sombra projetada no plano oposto ao tilt |
| `--sc-transition-duration` | `:is(:root[data-superclass="dimensional"], .superclass-dimensional)` | `320ms` | Duração de restauração inercial suave |
| `--sc-transition-easing` | `:is(:root[data-superclass="dimensional"], .superclass-dimensional)` | `cubic-bezier(0.16, 1, 0.3, 1)` | Desaceleração inercial cinemática |

---

## 2. Diagrama de Estados de Interação do Cartão 3D

```mermaid
stateDiagram-v2
    [*] --> Neutro: Montagem do componente

    state Neutro {
        desc: rotateX(0deg) rotateY(0deg) translateZ(0)
        shadow: --sc-shadow-idle
    }

    state Inclinado3D {
        desc: perspective(1000px) rotateX(calculado) rotateY(calculado)
        shadow: Sombra projetada oposta ao cursor
        camadas: Parallax interno (Capa 1px, Título 2px, Marcador 3px)
    }

    state Pressionado {
        desc: scale(0.98) translateZ(-4px)
        shadow: Sombra comprimida
    }

    Neutro --> Inclinado3D: pointermove (cursor sobre o cartão)
    Inclinado3D --> Inclinado3D: pointermove (atualização de coordenadas)
    Inclinado3D --> Neutro: pointerleave (desaceleração 320ms cubic-bezier)
    Inclinado3D --> Pressionado: :active (clique / toque inicial)
    Pressionado --> Inclinado3D: :active release
    Pressionado --> Neutro: pointerleave
```

---

## 3. Composição de Subcamadas de Parallax

```
┌─────────────────────────────────────────────────────────────┐
│  Plano 3: Marcadores e Badges (Deslocamento 3px)            │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Plano 2: Título e Autoria (Deslocamento 2px)          │  │
│  │ ┌───────────────────────────────────────────────────┐ │  │
│  │ │ Plano 1: Miniatura da Capa (Deslocamento 1px)     │ │  │
│  │ │                                                   │ │  │
│  │ └───────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────┘  │
│  Plano 0: Superfície do Cartão (Tilt base ±1.5° / ±2.0°)    │
└─────────────────────────────────────────────────────────────┘
```
