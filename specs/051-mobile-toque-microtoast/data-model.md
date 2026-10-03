# Data Model: Responsividade Mobile, Toque Nativo e Micro-Toast de Ferramentas

**Feature**: `051-mobile-toque-microtoast`  
**Data**: 2026-10-03  
**Status**: Concluído

Este documento descreve as estruturas de dados, tipagens TypeScript e estados reativos da interface envolvidos no suporte a toque nativo e no micro-toast de ferramentas.

---

## 1. Tipagens TypeScript

### `FloatingToastPayload`
Representa os parâmetros de emissão de um micro-toast flutuante de feedback de ferramenta.

```typescript
export interface FloatingToastPayload {
  /** Mensagem textual concisa (ex: "Destaque aplicado", "Trecho ocultado") */
  message: string
  /** Ponto cromático opcional para representar a cor do marca-texto ativo */
  colorDot?: string
  /** Duração em milissegundos antes do desaparecimento (padrão: 1800ms) */
  duration?: number
}
```

---

### `TouchTapContext`
Rastreia as coordenadas espaciais e temporais de toques táteis para discriminar entre toque simples, duplo toque e rolagem de página.

```typescript
export interface TouchTapContext {
  /** Timestamp em ms do último toque concluído (touchend) */
  lastTapTimestamp: number
  /** Coordenada X na viewport do último toque */
  lastTapX: number
  /** Coordenada Y na viewport do último toque */
  lastTapY: number
  /** Coordenada X de início do toque corrente (touchstart) */
  touchStartX: number
  /** Coordenada Y de início do toque corrente (touchstart) */
  touchStartY: number
  /** Flag indicando se o gesto em andamento excedeu a tolerância e virou scroll */
  isScrolling: boolean
}
```

---

## 2. Máquina de Estados do Micro-Toast

```
              [Inativo (visible=false)]
                         │
                 showToast(payload)
                         ▼
        ┌────── [Ativo (visible=true)] ──────┐
        │                                    │
    Novo showToast()                   1800ms expirados
        │                                    │
        ▼                                    ▼
[Substituição Atômica]               [Fade-out 250ms]
  (Reinicia timer)                           │
        │                                    ▼
        └───────────────────────────> [Inativo]
```

### Regras de Transição:
1. Ao invocar `showToast(...)`:
   - Se já houver um timer ativo, ele é cancelado imediatamente com `clearTimeout`.
   - `message` e `colorDot` são atualizados de forma síncrona.
   - `visible` passa para `true`.
   - Um novo timer de 1800ms é agendado.
2. Ao expirar o timer:
   - `visible` passa para `false`, ativando a transição CSS `toast-fade` (duração 250ms).
