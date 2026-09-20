# Research & Technical Decisions: F02 — Hierarquia Interativa

**Feature Branch**: `020-hierarquia-interativa`  
**Date**: 2026-09-19  
**Status**: Completed  

---

## 1. Modelagem Relacional da Árvore e Adjacência no SQLite

### Contexto
O modelo `Study` atualmente é achatado: pertence diretamente a um `chapter_id`, sem vínculos de parentesco entre estudos. A funcionalidade requer relacionamentos pai-filho e ordenação ordinal entre irmãos.

### Decisão
- Adotar o padrão **Lista de Adjacência** adicionando:
  - `parent_study_id`: `INTEGER NULL REFERENCES studies(id) ON DELETE SET NULL`
  - `position`: `INTEGER NOT NULL DEFAULT 0`
  - Índices: `ix_studies_parent_study_id` e `ix_studies_chapter_parent_position` (`chapter_id`, `parent_study_id`, `position`).

### Rationale
- O escopo de estudos é naturalmente particionado por capítulo (`chapter_id`), raramente ultrapassando 50 a 100 itens por capítulo.
- A profundidade é limitada a 5 níveis (decisão ratificada na clarificação Q2: Opção A).
- A lista de adjacência é a modelagem mais limpa, auditável e simples para SQLite, permitindo reordenação local com mínima escrita e sem locks abrangentes.
- A migração Alembic (`0006_add_study_hierarchy_and_position.py`) adiciona as colunas de forma segura com valores padrão para dados legados existentes (`parent_study_id = NULL`, `position = id` ou índice sequencial).

### Alternativas Consideradas
- **Nested Sets (Conjuntos Aninhados - lft/rgt)**: Rejeitado. Exige reescrever todos os nós da árvore a cada inserção ou movimentação, introduzindo alto risco de corrupção concorrente.
- **Materialized Path (Caminho Materializado - ex: '/1/4/12/')**: Rejeitado. Introduz redundância textual e requer atualização em cascata de strings de caminho para toda a subárvore quando um nó é movido.
- **Closure Table (Tabela de Fechamento)**: Rejeitado. Cria uma tabela auxiliar com $O(N^2)$ linhas, desnecessária para árvores pequenas delimitadas por capítulo e com profundidade máxima de 5 níveis.

---

## 2. Algoritmo de Prevenção de Ciclos (DAG) e Limite de Profundidade

### Contexto
Permitir que o usuário arraste ou mova nós pode acidentalmente criar loops infinitos (ex.: tornar um nó pai filho de seu próprio descendente), corrompendo a renderização da árvore e os algoritmos de travessia.

### Decisão
- Implementar verificação rigorosa de Grafo Acíclico Dirigido (DAG) em duas frentes:
  1. **Frontend (Prevenção Proativa)**: Durante o `dragover` e na montagem do menu de ações, desabilitar alvos de drop ou comandos que levariam a ciclos ou excederiam a profundidade de 5 níveis.
  2. **Backend (Validação Autoritativa)**: No serviço de persistência (`study_service.py`), antes de aplicar a movimentação de um estudo $S$ para um novo pai $P$:
     - Se $P == S \rightarrow$ Erro 422: auto-referência inválida.
     - Se $P$ pertencer a outro capítulo $\rightarrow$ Erro 422: estudos pais e filhos devem pertencer ao mesmo capítulo.
     - Subida recursiva (ou CTE): percorrer os ancestrais de $P$. Se $S$ for encontrado na cadeia ascendente de $P$, rejeitar com HTTP 422 ("Ciclo detectado: um estudo não pode se tornar filho de seu próprio descendente").
     - Verificação de profundidade: calcular a profundidade do pai $P$ na árvore ($depth_P$) somada à altura da subárvore de $S$ ($height_S$). Se $depth_P + 1 + height_S > 5$, rejeitar com HTTP 422 ("Profundidade máxima de 5 níveis excedida").

### Rationale
- Com limite de 5 níveis e <= 100 nós por capítulo, a travessia em memória leva uma fração de milissegundo (< 0.5ms).
- A rejeição determinística com HTTP 422 protege a integridade do banco mesmo contra requisições anômalas ou de rede.

---

## 3. Reorganização por Drag-and-Drop no Frontend (Vue 3 / HTML5 Nativo)

### Contexto
A reorganização visual de estudos na visão de Árvore precisa ser fluida, responsiva e alinhada com as diretrizes do projeto (sem bibliotecas pesadas de terceiros).

### Decisão
- Utilizar a **HTML5 Drag and Drop API nativa** integrada a manipuladores Vue 3:
  - Drag Source: nós possuem `draggable="true"` em seu manipulador de arrasto (*drag handle*).
  - No `dragstart`, o ID do estudo e sua subárvore são registrados no payload de transferência e no estado reativo local.
  - Drop Target: as zonas de soltura detectam três intenções com base na posição vertical do cursor:
    - **Topo do card (25% superior)**: soltar como irmão imediatamente acima (`reorder: before`).
    - **Centro do card (50% central)**: soltar como filho do nó alvo (`nest: as child`).
    - **Base do card (25% inferior)**: soltar como irmão imediatamente abaixo (`reorder: after`).
  - Indicadores visuais claros (linhas azuis para irmãos, contorno azul tracejado para adoção como filho).
  - Nós descendentes do item sendo arrastado recebem classe `is-drop-forbidden` e eventos de drop são cancelados (`dropEffect = 'none'`).

### Rationale
- Zero dependências npm adicionais, mantendo o bundle leve e sem vulnerabilidades.
- Máxima flexibilidade para desenhar os indicadores de ramo e conectores SVG da árvore.
- Respeito a `prefers-reduced-motion` desativando transições de arraste quando solicitado pelo sistema operacional.

---

## 4. Ergonomia Móvel e Ações Rápidas Acessíveis (WAI-ARIA & 44x44px)

### Contexto
Em telas de toque (< 768px), o arrastar e soltar contínuo pode ser impreciso e cansativo. A clarificação Q3 ratificou a Opção A: menu de ações rápidas no card com alvo mínimo de 44x44px.

### Decisão
- Cada card de estudo na árvore disponibiliza um botão de ações estruturais que abre um menu tátil com 4 ações determinísticas:
  1. **Promover nó (Outdent)**: Move o nó para o nível do seu pai atual (se desvincula do pai, subindo um nível hierárquico).
  2. **Recuar nó (Indent)**: Transforma o nó em filho do seu irmão anterior imediato (aninhando-o).
  3. **Mover para cima**: Troca de posição com o irmão imediatamente acima.
  4. **Mover para baixo**: Troca de posição com o irmão imediatamente abaixo.
- Todos os botões e gatilhos possuem dimensão mínima de 44x44px em resoluções móveis (`@media (max-width: 768px)`).
- Suporte a teclado via WAI-ARIA Treeview:
  - Foco com `Tab` e setas `Up` / `Down` para navegar entre os nós.
  - Seta `Right` para expandir ramo colapsado.
  - Seta `Left` para recolher ramo expandido ou subir para o pai.
  - Atalhos de teclado acessíveis (`Alt+Up`, `Alt+Down`, `Alt+Right`, `Alt+Left`) para reorganização sem mouse.

---

## 5. Política de Cascata na Lixeira (Soft Delete) e Concorrência Otimista

### Contexto
A clarificação Q1 ratificou a Opção A: ao mover um nó pai para a lixeira, todos os seus filhos e descendentes o acompanham; ao restaurar o pai, os filhos são restaurados juntos.

### Decisão
- **Exclusão Lógica (`trash_study`)**:
  - Busca recursiva (DFS) de todos os IDs de descendentes ativos sob o estudo pai.
  - Atualização em lote de `deleted_at = utc_now()` para o pai e todos os descendentes em uma única transação atômica.
- **Restauração (`restore_study`)**:
  - Busca recursiva de todos os descendentes marcados como deletados sob o estudo pai.
  - Restauração atômica (`deleted_at = None`) do estudo pai e de seus descendentes subordinados.
- **Concorrência Otimista**:
  - Qualquer alteração hierárquica ou de posição exige `expected_updated_at`.
  - Se outro dispositivo/aba moveu o estudo paralelamente, o backend retorna HTTP 409 Conflict, e a interface exibe o `ConcurrencyConflictModal` existente solicitando recarga da árvore.
