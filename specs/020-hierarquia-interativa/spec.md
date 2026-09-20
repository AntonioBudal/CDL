# Feature Specification: F02 — Hierarquia Interativa

**Feature Branch**: `020-hierarquia-interativa`  
**Created**: 2026-09-19  
**Status**: Approved  
**Input**: User description: "F02 Hierarquia Interativa com estudos pais/filhos e drag-and-drop"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Estruturação e Visualização Hierárquica em Árvore (Priority: P1) 🎯 MVP

Como leitor e pesquisador que analisa obras densas,  
quero organizar meus estudos em relações de parentesco (estudos pais e estudos filhos),  
para que teses fundamentais, argumentos de apoio e notas secundárias tenham representação visual clara e estruturada.

**Why this priority**: É o alicerce fundamental do pensamento complexo e da síntese intelectual no Caderno. Transforma a listagem achatada em uma autêntica árvore de conhecimento navegável.

**Independent Test**: Criar estudos com relações de dependência, visualizar a hierarquia na visão de Árvore com indentação progressiva e expandir/recolher nós para leitura focada.

**Acceptance Scenarios**:
1. **Given** um capítulo com múltiplos estudos cadastrados, **When** o leitor acessa a visualização em Árvore, **Then** os estudos são apresentados organizados em ramos hierárquicos com indicadores de expansão/colapso (`chevrons`).
2. **Given** um ramo de estudo com sub-estudos filhos, **When** o leitor clica no indicador de colapso, **Then** os estudos subordinados são ocultados suavemente, exibindo a contagem de itens contidos.
3. **Given** nós expandidos ou recolhidos pelo leitor, **When** a página é recarregada, **Then** o estado de expansão/colapso de cada nó é preservado.
4. **Given** um estudo pai que é enviado para a lixeira, **When** a ação é confirmada, **Then** o sistema aplica cascata lógica: todos os estudos filhos e descendentes são movidos conjuntamente para a lixeira (preservando suas relações de parentesco), e ao restaurar o estudo pai, seus descendentes são restaurados juntos.

---

### User Story 2 - Reorganização por Drag-and-Drop e Prevenção Matemática de Ciclos (Priority: P2)

Como leitor que refina ativamente a estrutura de seus argumentos,  
quero arrastar e soltar estudos para reposicioná-los ou aninhá-los dentro de outros estudos,  
com a garantia de que o sistema impeça qualquer criação acidental de referências circulares ou inconsistências.

**Why this priority**: Permite reorganizar o raciocínio em tempo real conforme a leitura amadurece, garantindo integridade estrutural inviolável.

**Independent Test**: Arrastar um estudo para dentro de outro (transformando-o em filho) e verificar o aninhamento; tentar arrastar um nó pai para dentro de um nó filho e constatar o bloqueio preventivo.

**Acceptance Scenarios**:
1. **Given** dois estudos no mesmo nível, **When** o leitor arrasta o Estudo B e solta sobre o Estudo A, **Then** o Estudo B torna-se filho do Estudo A e a árvore é atualizada instantaneamente.
2. **Given** dois estudos no mesmo nível, **When** o leitor arrasta um estudo entre outros dois nós (zona intermediária), **Then** a ordem de exibição entre irmãos é reordenada na posição indicada.
3. **Given** um estudo pai que possui descendentes (filhos e netos), **When** o usuário tenta soltar o estudo pai dentro de si mesmo ou de qualquer um dos seus descendentes, **Then** a interface bloqueia o drop, exibe indicador de proibição e o sistema rejeita a operação com mensagem explicativa.
4. **Given** a árvore de estudos de um capítulo, **When** um estudo é aninhado em níveis sucessivos, **Then** o sistema impõe um limite máximo seguro de 5 níveis de profundidade hierárquica (raiz + até 4 subníveis), bloqueando tentativas de aninhamento além desse patamar e orientando o usuário.

---

### User Story 3 - Ergonomia Móvel e Ações Acessíveis de Hierarquia (Priority: P3)

Como leitor em smartphones ou dispositivos móveis,  
quero ajustar a hierarquia e reordenar estudos com controles táteis confortáveis,  
mesmo quando o arrasto contínuo com precisão de ponteiro for difícil na tela de toque.

**Why this priority**: Garante que o leitor no celular desfrute da mesma capacidade de organização e rigor estrutural do desktop, com áreas de toque acessíveis (mínimo de 44x44px).

**Independent Test**: Emular um smartphone (largura < 768px), acessar a Árvore de estudos e reorganizar a hierarquia utilizando controles táteis alternativos.

**Acceptance Scenarios**:
1. **Given** um leitor acessando a Árvore em dispositivo móvel, **When** interage com um estudo, **Then** dispõe de um menu de ações rápidas no card do nó ("Promover nó", "Recuar nó", "Mover para cima", "Mover para baixo") com alvos de toque mínimos de 44x44px.
2. **Given** a navegação por tecnologias assistivas ou teclado, **When** o leitor foca em um nó da árvore, **Then** as teclas direcionais (Seta Direita para expandir, Seta Esquerda para recolher, Setas Cima/Baixo para navegar) operam conforme o padrão WAI-ARIA Treeview.

---

### Edge Cases

- **O que acontece ao tentar mover um nó para dentro de seu próprio neto?** A validação preventiva do sistema detecta a violação de grafo acíclico e impede a ação tanto antes do envio quanto na validação de persistência, evitando loops infinitos de renderização.
- **O que acontece se dois dispositivos reordenarem a árvore simultaneamente?** O controle de concorrência detecta que o estado do registro foi modificado por outra sessão e orienta o recarregamento seguro sem perda de dados.
- **O que acontece se o leitor arrastar um estudo para a extremidade superior ou inferior da tela?** O contêiner da árvore realiza auto-scroll suave para permitir mover itens ao longo de capítulos longos.
- **O que acontece se um estudo filho for desvinculado (promovido)?** Ele sobe de nível tornando-se irmão do seu antigo pai, mantendo todo o seu conteúdo, anotações e datas originais intactos.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE permitir que cada estudo possua uma vinculação opcional a um estudo pai (`parent_study_id`) pertencente ao mesmo capítulo.
- **FR-002**: O sistema DEVE manter uma ordem de posição estável (`position`) entre estudos irmãos do mesmo nível hierárquico.
- **FR-003**: O sistema DEVE exibir os estudos na visualização em Árvore com indentação visual proporcional e marcadores de ramo.
- **FR-004**: O sistema DEVE disponibilizar indicadores de expansão/colapso para nós que contenham sub-estudos, exibindo contadores de filhos quando recolhidos.
- **FR-005**: O sistema DEVE suportar reorganização por arrastar e soltar (*drag-and-drop*) permitindo:
  - Aninhar um estudo tornando-o filho de outro nó.
  - Reordenar a sequência de estudos na mesma camada de parentesco.
  - Promover um estudo filho para a raiz ou camada imediatamente superior.
- **FR-006**: O sistema DEVE validar ativamente a integridade da árvore como um grafo acíclico dirigido (DAG), impedindo estritamente que um nó se torne descendente de si próprio.
- **FR-007**: O sistema DEVE aplicar cascata lógica ao mover um estudo pai para a lixeira (soft delete), movendo todos os seus descendentes conjuntamente e restaurando-os em conjunto caso o pai seja restaurado.
- **FR-008**: O sistema DEVE limitar a profundidade máxima de aninhamento em até 5 níveis (nível raiz + 4 subníveis), impedindo operações que ultrapassem essa barreira estrutural.
- **FR-009**: O sistema DEVE fornecer menu de ações rápidas acessíveis no card/nó ("Promover nó", "Recuar nó", "Mover para cima", "Mover para baixo") com área tátil mínima de 44x44px para telas de toque e suporte a teclado.
- **FR-010**: O sistema DEVE preservar o estado de expansão/colapso dos ramos no dispositivo do leitor entre recarregamentos de página.
- **FR-011**: O sistema DEVE preservar todas as datas originais, chaves primárias, texto importado e integridade do banco SQLite, operando migrações idempotentes e seguras.

---

### Key Entities

- **Estudo Hierárquico (Study)**: Registro de reflexão e análise que além de pertencer a um capítulo, agora possui referência opcional a um estudo ascendente (`parent_study_id`), índice de ordenação ordinal (`position`) e lista de sub-estudos descendentes (`children`).
- **Nó da Árvore (TreeNode)**: Projeção visual reativa do estudo na interface que encapsula estado de expansão local, profundidade de nível (*depth*), linhas conectoras de ramo e manipuladores táteis de arrasto.
- **Árvore de Capítulo (ChapterTree)**: Coleção hierarquicamente ordenada de todos os nós de estudo pertencentes a um capítulo específico.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O leitor consegue aninhar ou reordenar qualquer estudo via arrasto e soltura em menos de 2 segundos.
- **SC-002**: 100% das tentativas de criar referências circulares (nó pai dentro de nó descendente) são bloqueadas antes de corromper o banco.
- **SC-003**: A renderização da árvore completa de um capítulo com até 100 estudos carrega e responde a interações de expansão/colapso em menos de 100ms a 60fps.
- **SC-004**: O estado expandido/colapsado da árvore persiste integralmente após recarregar o navegador ou alternar entre visualizações.
- **SC-005**: Todas as ações de toque em dispositivos móveis atendem à diretriz ergonômica mínima de 44x44px.

---

## Assumptions

- Estudos pais e filhos pertencem sempre ao mesmo capítulo e obra. A vinculação transversal entre diferentes capítulos ou obras é tratada pelo Grafo de Relações Semânticas (F04).
- A hierarquia não altera o conteúdo do texto do fichamento (`source_response`), metadados de localização ou análises registradas.
- O leitor mantém autonomia total: capítulos que não demandam estrutura aninhada continuam funcionando como listas simples de nível único.
