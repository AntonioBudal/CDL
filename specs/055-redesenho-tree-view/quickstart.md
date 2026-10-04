# Quickstart: Validação da Feature F 0.7.6 (Redesenho da Tree View)

**Feature**: F 0.7.6 — Redesenho da Tree View: Hierarquia Cognitiva e Estruturação de Tópicos  
**Artifact**: `quickstart.md`  

---

## 1. Pré-requisitos
- Frontend em execução em `http://localhost:5173` ou suíte de testes unitários (`npm test`).
- Backend em execução ou suíte de integração (`pytest`).

---

## 2. Cenários de Validação Fim a Fim

### Cenário 1: Linhas Guias e Visualização Conectada Elegante (P1 - MVP)
1. Acesse um capítulo que contenha estudos estruturados com estudos pais e subestudos.
2. Alterne para a visualização em **Árvore (Tree View)**.
3. **Resultado esperado**:
   - Cada nó filho exibe linhas guias finas e semânticas conectando-o vertical e horizontalmente ao nó ancestral.
   - Os títulos e metadados alinham-se proporcionalmente ao nível de profundidade.

### Cenário 2: Controles Globais de Expansão e Persistência no LocalStorage (P1 - MVP)
1. Na barra superior da Tree View, clique em **"Recolher Todos"**.
2. **Resultado esperado**:
   - Todos os ramos filhos são colapsados instantaneamente (< 100ms), restando apenas os estudos de nível raiz visíveis com seus chevrons apontando para a direita (`chevron-right`).
3. Clique em **"Expandir Todos"**.
4. **Resultado esperado**:
   - Todos os nós e subestudos voltam a ficar visíveis.
5. Recolha manualmente um nó específico e recarregue a página.
6. **Resultado esperado**:
   - Apenas o nó manualmente recolhido permanece fechado; os demais continuam abertos conforme salvo no `localStorage`.

### Cenário 3: Micro-Badge de Progresso Agregado por Ramo (P2)
1. Observe um nó pai com subestudos em múltiplos estados (ex.: 1 concluído, 1 revisado, 2 rascunhos).
2. **Resultado esperado**:
   - O card do nó pai exibe micro-badge compacto com fração textual `2/4 concluídos` e mini-barra de preenchimento em 50%.
   - Ao passar o cursor ou focar, um tooltip contextual detalha a contagem de cada status.
3. Atualize o status de um dos subestudos de rascunho para concluído.
4. **Resultado esperado**:
   - O indicador do pai atualiza instantaneamente para `3/4 concluídos` (75%).

### Cenário 4: Drag-and-Drop Magnético e Bloqueio Determinístico de Ciclos (P3)
1. Inicie o arrasto de um nó de estudo sobre outro card.
2. **Resultado esperado**:
   - Ao posicionar o cursor no topo/base: linha indicadora horizontal fina sinaliza inserção linear antes ou depois.
   - Ao posicionar o cursor no centro do card: moldura magnética sutil indica aninhamento subordinado como filho.
3. Tente arrastar um nó pai para dentro de um de seus próprios descendentes ou subestudos.
4. **Resultado esperado**:
   - O cursor bloqueia a ação (`not-allowed`) e o drop é completamente ignorado, impedindo a criação de ciclos infinitos.

### Cenário 5: Ergonomia Mobile e Alvos Táteis de 44px (P3)
1. Reduza a janela para largura móvel (< 768px).
2. **Resultado esperado**:
   - Os botões de chevron para expandir e recolher possuem dimensões de toque confortáveis (mínimo 44×44px).
   - O menu de ações rápidas táteis permite "Mover para cima", "Mover para baixo", "Promover" e "Recuar" com botões de 44px sem depender de arrasto touch instável.
