# Research: Decisões Técnicas e Arquiteturais da Feature F 0.7.6

**Feature**: F 0.7.6 — Redesenho da Tree View: Hierarquia Cognitiva e Estruturação de Tópicos  
**Branch**: `055-redesenho-tree-view`  
**Date**: 2026-10-04  

---

## 1. Contexto e Motivação

A `StudyTreeView.vue` tem como propósito primário expressar a **subordinação hierárquica e a desagregação conceitual** dos estudos de um livro/capítulo. A implementação atual organiza os nós com recuo à esquerda, mas carece de percepção imediata de progresso agregado por ramo, controle de colapso/expansão em lote, linhas guias visuais contínuas e ergonomia de drag-and-drop refinada.

---

## 2. Decisões Arquiteturais e de Design

### D1: Conectores e Linhas Guias em CSS Estrutural Puro

- **Decisão**: Utilizar pseudo-elementos (`::before` e `::after`) nas listas `ul.tree-branch` e itens `li.tree-node-item` para desenhar conectores em "L" contínuos conectando pais a filhos.
- **Rationale**:
  - Elimina a sobrecarga computacional de SVGs ou canvas dinâmicos.
  - Reage automaticamente ao redimensionamento de nós e títulos longos.
  - Conecta-se às variáveis canônicas de cores dos 10 temas do sistema (`var(--color-border)` / `var(--color-border-divider)`).
- **Alternativas Rejeitadas**:
  - *SVG inline absoluto*: Complexo para recalcular posições durante expansão/colapso animado.
  - *Apenas recuo com margem esquerda*: Não transmite conexão topológica nem profundidade para árvores com 3 ou 4 níveis.

---

### D2: Modelo de Agregação de Progresso do Ramo (`BranchProgress`)

- **Decisão**: Calcular métricas de completude em tempo $O(N)$ durante a composição da árvore em `useStudyHierarchy.ts`.
- **Regras Conforme Clarificação**:
  - Considera todos os descendentes recursivos (filhos + netos + bisnetos).
  - Estudos com status `concluido` ou `revisado` contam como completude consolidada.
  - Métricas calculadas para cada nó:
    ```typescript
    export interface BranchProgress {
      total: number
      completed: number
      percent: number
      label: string // Ex: "2/4 concluídos"
      details: {
        rascunho: number
        em_andamento: number
        revisado: number
        concluido: number
      }
    }
    ```
- **Rationale**:
  - Garante atualização reativa instantânea ao alterar status de qualquer subestudo sem requisições adicionais à rede.
  - Apresenta fração clara (`2/4 concluídos`) em micro-badge com tooltip detalhando os status.
  - Nós folha (sem filhos) não exibem badge, preservando silêncio visual.

---

### D3: Estratégia de Abertura Inicial e Persistência no `localStorage`

- **Decisão**: Adotar a estratégia de **conjunto de nós colapsados** (`collapsedNodeIds`) persistida sob a chave `caderno_tree_collapsed_${bookId}`.
- **Rationale**:
  - Como a clarificação definiu **"Totalmente expandida por padrão"**, o conjunto vazio `[]` representa todos os nós abertos.
  - Quando a pessoa clica para recolher um nó específico, o ID desse nó é adicionado a `collapsedNodeIds`.
  - "Expandir Todos" esvazia o conjunto instantaneamente (`collapsedNodeIds.clear()`).
  - "Recolher Todos" inclui todos os IDs com filhos no conjunto.
  - Novos nós criados surgem automaticamente abertos sem quebrar a preferência do usuário.

---

### D4: Drag-and-Drop Magnético com Distinção Visual e Bloqueio Rigoroso de Ciclos

- **Decisão**: Dividir a área do card alvo em 3 zonas táteis distintas durante `dragover`:
  - Superior (0% a 25% da altura): `dropPosition = 'before'` (linha horizontal superior de inserção linear).
  - Inferior (75% a 100% da altura): `dropPosition = 'after'` (linha horizontal inferior de inserção linear).
  - Central (25% a 75% da altura): `dropPosition = 'inside'` (moldura magnética de absorção cobrindo o card destino com borda de destaque e fundo suave).
- **Proteção contra Ciclos e Profundidade**:
  - `canNestUnder(sourceId, targetId)` valida que:
    1. `sourceId !== targetId` (não aninhar sobre si mesmo).
    2. `targetId` não é descendente de `sourceId` (evita ciclos infinitos).
    3. Profundidade resultante não excede 5 níveis (índices 0 a 4).
  - Se proibido, o estilo `is-drop-forbidden` é aplicado imediatamente com cursor de bloqueio.

---

### D5: Ergonomia Mobile e Acessibilidade WAI-ARIA 1.2

- **Decisão**: Alvos táteis de 44×44px nos botões de chevron e no menu de ações rápidas contextuais.
- **Padrão WAI-ARIA**:
  - Contêiner: `role="tree"` com `tabindex="0"`.
  - Nós: `role="treeitem"`, `aria-expanded` (apenas quando tem filhos), `aria-level="depth + 1"`, `aria-selected`.
  - Navegação por teclado: Setas Direita/Esquerda para expandir/recolher e Cima/Baixo para navegar na ordem linear de nós visíveis.
  - Atalhos Alt + Setas para reordenação tátil acessível.

---

## 3. Resumo de Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|
| Lentidão em árvores grandes com dezenas de nós | Baixa | Médio | Computação plana de métricas em passo único com mapa memoizado em `useStudyHierarchy.ts`. |
| Conflitos de edição concorrente no endpoint `/move` | Baixa | Baixo | Interceptação de HTTP 409 com mensagem acolhedora e recarregamento automático da árvore. |
| Dificuldade no toque de smartphones | Média | Médio | Menu touch de 44px com ações expressas ("Mover para cima", "Mover para baixo", "Promover", "Recuar"). |
