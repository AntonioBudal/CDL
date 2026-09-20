# Interface Contract: Cinemática e Aceleração Gráfica das Superclasses

**Feature Branch**: `026-interacao-avancada-movimento`  
**Date**: 2026-09-19  
**Contract Type**: Frontend Composable, CSS Tokens & Component Contracts  

---

## 1. Contrato do Composable `useSuperclassPhysics`

O composable centraliza os cálculos de física inercial, amortecimento elástico, snap-to-grid e detecção de acessibilidade.

### Assinatura e Interface Pública

```typescript
export interface UseSuperclassPhysicsOptions {
  activeSuperclass?: ComputedRef<string> | Ref<string>
  intensity?: ComputedRef<number> | Ref<number>
}

export interface UseSuperclassPhysicsReturn {
  // Perfil cinemático atual
  activeProfile: ComputedRef<KinematicProfile>
  
  // Sinalizações de acessibilidade e ambiente
  isReducedMotion: Ref<boolean>
  isTouchDevice: Ref<boolean>
  
  // Cálculo de amortecimento inercial pós-arrasto
  calculateInertialStep: (
    current: { x: number; y: number },
    velocity: { vx: number; vy: number },
    deltaTime: number
  ) => {
    nextPosition: { x: number; y: number }
    nextVelocity: { vx: number; vy: number }
    isFinished: boolean
  }
  
  // Cálculo de snap-to-grid calibrado
  calculateSnapPosition: (x: number, y: number, gridSize?: number) => {
    snappedX: number
    snappedY: number
    didSnap: boolean
  }
  
  // Gatilho de feedback háptico visual (80ms)
  triggerHapticPulse: (element: HTMLElement | null, style?: 'snap' | 'connect' | 'step') => void
  
  // Verificação de comutação para motor acelerado
  shouldAccelerate: (nodeCount: number) => boolean
}
```

---

## 2. Contrato do Componente `CanvasAcceleratedLayer.vue`

Camada acelerada em HTML5 Canvas 2D substituindo ou complementando o desenho de conexões em alta densidade de nós (≥ 60).

### Props

| Prop | Tipo | Obrigatório | Padrão | Descrição |
|---|---|---|---|---|
| `connections` | `ComputedConnection[]` | Sim | - | Lista de arestas e curvas de relacionamento calculadas |
| `activeStudyId` | `number \| null` | Não | `null` | Identificador do estudo em foco para realce de arestas conectadas |
| `viewport` | `{ x: number; y: number; scale: number }` | Sim | - | Coordenadas de translação (pan) e nível de zoom do Canvas/Mapa |
| `width` | `number` | Sim | - | Largura visível em pixels da viewport do canvas |
| `height` | `number` | Sim | - | Altura visível em pixels da viewport do canvas |

### Emits

| Evento | Payload | Descrição |
|---|---|---|
| `select-relation` | `ComputedConnection` | Disparado quando o usuário clica sobre a área de uma aresta/linha desenhada no canvas |

---

## 3. Contrato de Tokens CSS e Atributos DOM

### 3.1 Atributos DOM Reativos
- `data-haptic-pulse="snap | connect | step"`: Aplicado temporariamente ao elemento interativo durante 80ms para disparar transição de micro-vibração visual.
- `data-reduced-motion="active"`: Aplicado ao contêiner raiz quando `prefers-reduced-motion: reduce` for detectado no sistema operacional.

### 3.2 Variáveis CSS Cinemáticas Globais

| Token CSS | Intervalo Típico | Descrição |
|---|---|---|
| `--sc-physics-friction` | `0.0` a `0.98` | Fricção relativa da superclasse ponderada pela intensidade |
| `--sc-spring-stiffness` | `0.05` a `1.0` | Constante elástica de retorno para ancoragem |
| `--sc-parallax-depth` | `0.0` a `2.0` | Fator multiplicador de deslocamento 2.5D para camadas de profundidade |
| `--sc-proximity-reveal` | `0px` a `180px` | Distância do cursor para início de revelação suave na Superclasse Invisível |
