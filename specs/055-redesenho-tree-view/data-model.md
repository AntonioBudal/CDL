# Data Model: Modelagem de Dados e Tipos da Tree View

**Feature**: F 0.7.6 — Redesenho da Tree View: Hierarquia Cognitiva e Estruturação de Tópicos  
**Status**: Completed  
**Artifact**: `data-model.md`  

---

## 1. Entidades Principais e Extensões

### 1.1 `BranchProgress` (Métricas de Progresso Agregado do Ramo)

```typescript
export interface BranchProgressDetails {
  rascunho: number
  em_andamento: number
  revisado: number
  concluido: number
}

export interface BranchProgress {
  total: number               // Total de descendentes (filhos + netos + bisnetos)
  completed: number           // Quantidade em status consolidado (concluido + revisado)
  percent: number             // 0 a 100
  label: string               // Ex: "2/4 concluídos"
  details: BranchProgressDetails
}
```

### 1.2 `StudyTreeNode` (Extensão do Nó de Árvore)

```typescript
export interface StudyTreeNode extends StudySummary {
  parent_study_id: number | null
  position: number
  depth: number
  children: StudyTreeNode[]
  progress?: BranchProgress | null  // Presente se children.length > 0
}
```

### 1.3 `TreeExpansionState` (Estado de Expansão/Colapso)

```typescript
export interface TreeExpansionState {
  collapsedNodeIds: Set<number>
  isTreeRootExpanded: boolean
}
```

---

## 2. Regras de Cálculo e Algoritmo de Agregação

### 2.1 Função de Cálculo Pós-Ordem (`calculateBranchProgress`)

Para cada nó na árvore:
1. Se o nó não possui filhos (`children.length === 0`), `progress = null`.
2. Se possui filhos, percorre recursivamente todos os nós descendentes acumulando:
   - `total = contagem de todos os nós descendentes`.
   - `details.rascunho = contagem com status 'rascunho'`.
   - `details.em_andamento = contagem com status 'em_andamento' ou 'em_estudo'`.
   - `details.revisado = contagem com status 'revisado'`.
   - `details.concluido = contagem com status 'concluido'`.
3. `completed = details.concluido + details.revisado`.
4. `percent = total > 0 ? Math.round((completed / total) * 100) : 0`.
5. `label = `${completed}/${total} concluídos``.

---

## 3. Limites Estruturais e Restrições de Integridade

1. **Profundidade Máxima**:
   - `MAX_TREE_DEPTH = 5` (níveis 0 a 4).
   - Um nó com `depth >= 4` não pode receber filhos (`canNestUnder` retorna `false`).
2. **Prevenção de Ciclos**:
   - `sourceId !== targetId`.
   - Se `targetNode` é descendente de `sourceNode`, a operação é proibida.
3. **Persistência**:
   - Chave `caderno_tree_collapsed_${bookId}` armazena `number[]` no `localStorage`.
