# Modelo de Dados e Estados: Lixeira — Arquivo de Salvaguarda e Segurança

Este documento descreve as entidades de dados, tipos TypeScript, estruturas de estado reativo e transições de ciclo de vida para a Feature F0.8.8.

---

## 1. Tipos e Entidades da Lixeira

### 1.1 Entidades Existentes (Consumidas da API)

```typescript
export interface TrashBookItem {
  id: number
  title: string
  author: string | null
  deleted_at: string
  days_until_purge: number
  chapters_count: number
  studies_count: number
}

export interface TrashStudyItem {
  id: number
  title: string
  book_id: number
  book_title: string
  chapter_id: number | null
  chapter_name: string
  deleted_at: string
  days_until_purge: number
}

export interface TrashSummary {
  books: TrashBookItem[]
  studies: TrashStudyItem[]
  total_items: number
}
```

---

## 2. Modelos de Estado do Frontend

### 2.1 Identificador Unificado de Seleção

Para suportar a seleção mista de livros e estudos na mesma lista de lote, utiliza-se a chave composta ou tupla:

```typescript
export type TrashItemType = 'book' | 'study'

export interface SelectedTrashItemKey {
  type: TrashItemType
  id: number
}

export type SelectedItemKeyString = `${TrashItemType}-${number}`
```

Funções auxiliares de serialização:
- `toKeyString(type: TrashItemType, id: number): SelectedItemKeyString` $\rightarrow$ `"${type}-${id}"`
- `parseKeyString(key: SelectedItemKeyString): { type: TrashItemType; id: number }`

### 2.2 Estado da Barra de Ações em Lote

```typescript
export interface BatchActionProgress {
  isActive: boolean
  totalCount: number
  completedCount: number
  currentAction: 'restoring' | 'deleting' | null
  errors: string[]
}
```

### 2.3 Cálculo de Retenção e Urgência

Para cada item descartado na lixeira:

```typescript
export interface RetentionMetrics {
  daysRemaining: number
  totalRetentionDays: number // Sempre 30 dias
  elapsedPercentage: number  // clamp(((30 - daysRemaining) / 30) * 100, 0, 100)
  isUrgent: boolean          // daysRemaining <= 5
  urgencyLabel: string       // "Expurgo em X dias" ou "Expurgo em 1 dia"
}
```

Regras de Validação:
- `daysRemaining`: Inteiro no intervalo $[0, 30]$.
- `isUrgent`: Verdadeiro se `daysRemaining <= 5`, acionando estilização com variáveis semânticas de atenção/perigo.
- `elapsedPercentage`: Normalizado entre 0% e 100% para desenhar a barra de progresso visual de tempo decorrido.

---

## 3. Máquina de Estados e Ciclo de Vida do Item

### Transições de Estado

```
                 [ Descartado no Acervo ]
                           │
                           ▼
                    ┌──────────────┐
                    │   IN_TRASH   │
                    └──────┬───────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   (Restaurar)        (Selecionar)       (Excluir Definitivo)
        │                  │                  │
        ▼                  ▼                  ▼
┌───────────────┐   ┌──────────────┐   ┌──────────────┐
│   RESTORING   │   │   SELECTED   │   │  CONFIRMING  │
│  (Anim 180ms) │   └──────┬───────┘   │   (Modal)    │
└───────┬───────┘          │           └──────┬───────┘
        │            (Ação em Lote)           │
        │                  ▼                  │
        │           ┌──────────────┐          │
        │           │  BATCH_PROC  │          │
        │           └──────┬───────┘          │
        │                  │                  │
        ▼                  ▼                  ▼
┌───────────────┐   ┌──────────────┐   ┌──────────────┐
│    RESTORED   │   │  FINALIZED   │   │ PURGED_DB    │
│ (Acervo Ativo)│   │(Atualiza UI) │   │(Destruído DB)│
└───────────────┘   └──────────────┘   └──────────────┘
```

1. **`IN_TRASH`**: Estado padrão do item ao carregar a lixeira.
2. **`SELECTED`**: Usuário marcou a caixa de seleção. Adicionado ao conjunto `selectedKeys`.
3. **`RESTORING`**: Requisição de restauração em andamento. Aplica `.is-restoring` (saída suave de 180ms).
4. **`RESTORED`**: Item removido da lista no frontend e reativado no banco de dados ativo.
5. **`CONFIRMING`**: Modal de alerta aberto aguardando confirmação deliberada do usuário.
6. **`PURGED_DB`**: Item expurgado fisicamente do banco de dados (SQLite `DELETE`).
