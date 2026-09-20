# Feature Specification: F04 — Relações entre Estudos

**Feature Branch**: `022-relacoes-estudos`  
**Created**: 2026-09-19  
**Status**: Draft  
**Input**: User description: "Definir o sistema de relações semânticas e conexões direcionadas entre estudos (F04 do Roadmap 0.4)"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Conexões Semânticas e Referências Cruzadas Bidirecionais (Priority: P1) [MVP]

Como leitor e pesquisador que analisa múltiplos textos, quero conectar dois estudos através de um vínculo conceitual explícito (ex.: *complementa*, *contradiz*, *depende de*, *mesmo tema*, *desdobramento de*) e visualizar automaticamente a referência cruzada (backlink) no estudo de destino, para que eu possa mapear pontes intelectuais e navegar pela malha de conhecimento sem me limitar à ordem linear de capítulos.

**Why this priority**: É o cerne ontológico e valor funcional primordial da F04. Sem a capacidade de vincular estudos com semântica explícita e navegar bidirecionalmente entre eles, nenhuma visualização de rede ou mapa tem utilidade.

**Independent Test**: Criar uma relação do tipo "contradiz" entre o Estudo A e o Estudo B com uma anotação explicativa; abrir o Estudo B e verificar que o vínculo reverso com o Estudo A é exibido com precisão e permite navegação de volta com um clique.

**Acceptance Scenarios**:
1. **Given** que o usuário está visualizando ou editando o Estudo A, **When** aciona a ação "Adicionar Relação", seleciona o Estudo B, escolhe o tipo "complementa" e confirma, **Then** o sistema registra a conexão e a exibe na lista de relações do Estudo A.
2. **Given** que a relação entre Estudo A e Estudo B foi criada, **When** o usuário abre o Estudo B, **Then** a seção de relações do Estudo B exibe o vínculo recebido de Estudo A indicando a direção ("complementado por Estudo A").
3. **Given** que o usuário tenta relacionar o Estudo A consigo mesmo, **When** tenta confirmar a seleção, **Then** o sistema bloqueia a ação preventivamente com alerta explicativo.

---

### User Story 2 - Visualização Gráfica com Setas Direcionadas no Canvas e Mapa (Priority: P2)

Como usuário que organiza estudos no espaço bidimensional (Canvas de Estudos ou Mapa de Rede), quero que as relações semânticas sejam renderizadas visualmente como arestas conectadas com pontas de flecha direcionadas e indicação do tipo de relação, para que eu compreenda visualmente a topologia e as linhas de raciocínio da obra.

**Why this priority**: Transforma as relações tabulares em síntese espacial intuitiva, aproveitando a infraestrutura recém-concluída do Canvas 2D (F03) e do modo Mapa (F01).

**Independent Test**: Abrir o Canvas de um livro contendo estudos previamente conectados; confirmar que as conexões entre os cards aparecem desenhadas graficamente com setas e acompanham o deslocamento dos cards em tempo real durante o arrasto.

**Acceptance Scenarios**:
1. **Given** dois cards posicionados no Canvas com uma relação direcional ativa, **When** a visualização do Canvas é carregada, **Then** uma linha de conexão é desenhada unindo as bordas mais próximas dos cards com uma ponta de seta apontando para o estudo de destino.
2. **Given** que um dos cards conectados é movido pelo usuário pelo Canvas, **When** o card é arrastado, **Then** a linha de conexão recalcula continuamente sua ancoragem e traçado em tempo real a 60fps.
3. **Given** que o usuário posiciona o cursor ou toca sobre a linha de conexão, **When** interage com a linha, **Then** o sistema destaca a aresta e exibe o rótulo do tipo de vínculo e sua nota explicativa.

---

### User Story 3 - Gestão, Anotação e Remoção Segura de Vínculos (Priority: P3)

Como pesquisador que refina suas hipóteses ao longo do tempo, quero editar a anotação explicativa de uma relação, alterar sua tipologia ou removê-la sem afetar o conteúdo dos estudos envolvidos, garantindo integridade e flexibilidade na manutenção da minha base de conhecimento.

**Why this priority**: Garante governança ao leitor, permitindo ajustes conforme seu entendimento evolui ou retificação de erros de catalogação.

**Independent Test**: Selecionar uma relação existente, alterar sua anotação de "tese oposta" para "crítica metodológica", salvar a alteração e, em seguida, remover o vínculo, constatando que os dois estudos permanecem íntegros e a conexão deixa de existir.

**Acceptance Scenarios**:
1. **Given** uma relação existente entre Estudo A e Estudo B, **When** o leitor edita o texto descritivo e confirma, **Then** a alteração é salva e refletida em ambos os estudos.
2. **Given** uma relação existente, **When** o leitor clica no comando de remover relação e confirma, **Then** o vínculo é desfeito de forma atômica e os estudos permanecem inalterados.
3. **Given** que um estudo que possui 3 relações ativas é excluído definitivamente pelo usuário, **When** a exclusão é processada, **Then** suas relações são limpas em cascata sem deixar órfãos ou inconsistências no sistema.

---

### User Story 4 - Ergonomia Móvel, Busca Rápida e Acessibilidade (Priority: P4)

Como usuário acessando o caderno em smartphone ou via teclado no desktop, quero localizar estudos para conexão através de uma busca rápida com digitação incremental e navegar pelas relações usando controles acessíveis e alvos de toque adequados, para ter uma experiência ágil em qualquer dispositivo.

**Why this priority**: Assegura a conformidade estrita com as regras da Constituição (alvos mínimos de 44x44px, acessibilidade WAI-ARIA e responsividade total em dispositivos móveis).

**Independent Test**: Emular tela de smartphone de 375px; acionar a criação de relação, buscar por trecho do título de um estudo, navegar na lista de resultados e selecionar o vínculo usando toque confortável; navegar pelas relações via teclado usando Tab e Enter.

**Acceptance Scenarios**:
1. **Given** o modal ou gaveta de criação de relação aberto, **When** o usuário digita no campo de busca, **Then** os estudos candidatos são filtrados incrementalmente exibindo título, capítulo e livro de origem.
2. **Given** a lista de relações na tela de um estudo em dispositivo móvel, **When** o leitor toca em uma relação, **Then** o estudo de destino é apresentado em visualização acessível com opção de navegação imediata.
3. **Given** um usuário utilizando navegação exclusivamente por teclado, **When** foca a lista de relações com Tab, **Then** consegue acionar e gerenciar os vínculos com teclas padrão (Enter/Espaço/Delete).

---

### Edge Cases

- **Auto-conexão Proibida**: O que acontece quando o usuário tenta relacionar um estudo consigo mesmo? O seletor exclui o próprio estudo da lista de busca e qualquer tentativa programática direta é rejeitada com erro de validação.
- **Relações Duplicadas**: O que acontece se o usuário tentar criar a mesma relação duas vezes entre os mesmos dois estudos com o mesmo tipo? O sistema detecta a duplicidade e avisa que o vínculo já existe, impedindo entradas redundantes.
- **Estudo Movido para Lixeira (Q3 - Opção A)**: O que acontece com as relações de um estudo quando ele é enviado para a lixeira (soft delete)? As relações são preservadas no banco de dados, mas ocultadas das consultas e visualizações ativas. Caso o estudo seja restaurado da lixeira, todos os vínculos reaparecem intactos. Caso seja expurgado em definitivo, as relações são excluídas em cascata.
- **Conexões Transversais entre Livros Diferentes (Q1 - Opção A)**: Estudos de livros diferentes podem ser relacionados entre si na malha de conhecimento? Sim. As relações semânticas operam de forma transversal a todo o acervo pessoal, permitindo cruzar teses entre diferentes livros, com identificação clara da obra de origem na busca e na exibição.
- **Representação Gráfica no Canvas e Mapa (Q2 - Opção A)**: Como representar visualmente conexões na exploração 2D? O traçado é renderizado através de curvas suaves (Bézier cúbicas ou quadráticas) unindo as bordas mais próximas dos cards, com ponta de seta direcional e badge compacto flutuante indicando o tipo de relação sobre a linha.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE permitir a criação de relações direcionadas entre dois estudos distintos, exigindo a seleção explícita de um estudo de origem, um estudo de destino e um tipo semântico formal.
- **FR-002**: O sistema DEVE suportar os seguintes tipos semânticos de relação canônicos:
  - `relacionado_com` (associação temática neutra)
  - `complementa` (origem fornece suporte, dados ou argumentos adicionais ao destino)
  - `contradiz` (origem contesta, refuta ou problematiza a tese do destino)
  - `depende_de` (origem pressupõe o entendimento prévio do destino como pré-requisito)
  - `mesmo_tema` (afinidade conceitual direta entre teses semelhantes)
  - `desdobramento_de` (origem é decorrência, consequência prática ou derivação lógica do destino)
- **FR-003**: O sistema DEVE permitir uma anotação textual opcional (`description`) de até 500 caracteres detalhando a justificativa intelectual do vínculo.
- **FR-004**: O sistema DEVE impedir rigorosamente a criação de auto-relações (onde o estudo de origem é idêntico ao de destino).
- **FR-005**: O sistema DEVE impedir a duplicidade de relações idênticas (mesma origem, mesmo destino e mesmo tipo de relação).
- **FR-006**: O sistema DEVE disponibilizar consulta bidirecional completa: ao consultar as relações de um estudo, devem ser retornadas tanto as relações de saída (*outbound relations*) quanto as relações recebidas (*inbound backlinks*).
- **FR-007**: O sistema DEVE permitir a exclusão individual de uma relação sem afetar a integridade ou o conteúdo de qualquer um dos estudos envolvidos.
- **FR-008**: O sistema DEVE excluir automaticamente as relações em cascata quando um estudo for permanentemente destruído da base de dados.
- **FR-009**: O sistema DEVE permitir que relações semânticas sejam estabelecidas transversalmente entre estudos de quaisquer livros do acervo, exibindo o livro e capítulo para desambiguação clara na busca e nos backlinks.
- **FR-010**: O sistema DEVE renderizar arestas vetoriais direcionadas em curvas Bézier suaves conectando as bordas mais próximas dos nós correspondentes no modo Canvas de Estudos e no modo Mapa, com ponta de seta direcional, badge compacto do tipo de relação e ancoragem dinâmica que recalcula em tempo real a 60fps durante arrasto de cards.
- **FR-011**: O sistema DEVE preservar latentes as relações quando um estudo participante for enviado para a lixeira (soft delete), ocultando-as das telas ativas e reativando-as intactas caso o estudo seja restaurado.
- **FR-012**: A interface móvel DEVE garantir áreas mínimas de toque de 44x44px em todos os controles de relação, busca e remoção.
- **FR-013**: Todos os elementos interativos de relações DEVEM seguir a especificação semântica WAI-ARIA para navegação acessível por teclado.

---

### Key Entities *(include if feature involves data)*

- **StudyRelation (Relação entre Estudos)**:
  - Representa o elo semântico e direcional entre dois estudos do caderno.
  - Atributos essenciais:
    - Identificador único (`id`).
    - Estudo de origem (`source_study_id`).
    - Estudo de destino (`target_study_id`).
    - Tipo formal da relação (`relation_type`): `relacionado_com`, `complementa`, `contradiz`, `depende_de`, `mesmo_tema`, `desdobramento_de`.
    - Justificativa textual / nota explicativa (`description`).
    - Data e hora de criação (`created_at`).
  - Restrições essenciais:
    - Proibição de auto-relacionamento (`source_study_id != target_study_id`).
    - Unicidade composta de vínculo (`source_study_id`, `target_study_id`, `relation_type`).
    - Cascata de exclusão na remoção permanente de qualquer um dos estudos participantes.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O usuário consegue vincular dois estudos através de busca rápida e seleção de tipo semântico em menos de 10 segundos.
- **SC-002**: 100% das relações criadas geram backlinks reversos automáticos e imediatos na visão do estudo de destino sem necessidade de recarregar a página.
- **SC-003**: 0% de auto-relações ou conexões duplicadas registradas no sistema sob qualquer circunstância.
- **SC-004**: No Canvas 2D, as arestas gráficas conectam os cards e recalculam suas coordenadas a 60fps durante operações de pan, zoom e movimentação contínua de nós.
- **SC-005**: 100% dos controles interativos de criação, navegação e remoção de relações operam com área de toque mínima de 44x44px em dispositivos móveis.
- **SC-006**: Todos os testes automatizados de backend e frontend executam de forma 100% isolada em ambientes descartáveis, com 0 leituras ou gravações no banco ativo de produção.

---

## Assumptions

- O usuário constrói sua rede semântica de forma deliberada e manual; inferências automáticas não supervisionadas via IA externa estão fora do escopo conforme diretrizes de privacidade.
- A visualização em modo Mapa reutilizará o grafo de nós e arestas derivado das entidades `Study` e `StudyRelation`.
- A remoção de relações é uma operação segura e reversível pelo usuário mediante nova criação, não exigindo confirmações com diálogos modais bloqueantes intrusivos, mas com feedback claro de desfecho.
- A busca rápida de estudos candidatos priorizará correspondência por título e capítulo de forma incremental no cliente ou via endpoint leve de busca.
