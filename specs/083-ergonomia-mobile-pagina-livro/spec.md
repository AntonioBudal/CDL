# Feature Specification: F0.9.02 — Ergonomia Mobile e Descongestionamento da Página do Livro

**Feature Branch**: `083-ergonomia-mobile-pagina-livro`  
**Created**: 2026-10-21  
**Status**: Draft  
**Input**: User description: "F02 — Ergonomia Mobile e Descongestionamento da Página do Livro (Roadmap 0.9)"

---

## Contexto e Propósito

No contexto da versão **0.9 — Revisão Geral de UI/UX, Ergonomia e Estabilização**, a **Feature F0.9.02** foca na otimização ergonômica da página interna do livro (`/livros/:bookId`).

A auditoria de interface identificou que, em dispositivos móveis (`<= 767px`):
1. **Cabeçalho Verticalmente Inflado:** O cabeçalho empilha capa de dimensões médias (160x240px), título, subtítulo, autor, categorias e quatro botões de ação em formato de pílula expandida, ocupando mais de 450px da altura útil antes mesmo da barra de capítulos.
2. **Duplicação de Controles de Capítulos:** A faixa superior de capítulos exibe simultaneamente um seletor `<select>` nativo e a esteira de pílulas roláveis horizontais, gerando poluição visual, sobreposição de áreas de toque e rolagem vertical desnecessária.
3. **Inspetor Analítico Redundante e Rígido:** A faixa inferior do inspetor repete dados estáticos que consomem espaço de leitura na base da viewport, em vez de atuar como painel contextual recolhível sob demanda.

Esta especificação define o redesenho ergonômico da página do livro no mobile para garantir que o conteúdo principal (os estudos e notas da obra) seja imediatamente acessível na primeira dobra da tela, preservando a rica arquitetura horizontal já consolidada para telas maiores (desktop).

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Cabeçalho Condensado de Linha Dupla com Ações Agrupadas no Mobile (Priority: P1) - MVP

Como leitor acessando um livro pelo smartphone, quero um cabeçalho compacto e organizado que apresente capa em miniatura, título e autor em espaço vertical reduzido, mantendo todas as ações do livro agrupadas e fáceis de acionar, para que a tela não seja dominada por metadados antes de eu ver meus estudos.

**Why this priority**: É a alteração de maior impacto visual imediato, liberando mais de 250px de altura vertical no celular e permitindo que o leitor visualize os estudos da obra logo ao carregar a página.

**Independent Test**: Acessar `/livros/:bookId` em viewport móvel (390x844px e 360x740px); verificar que a altura do cabeçalho do livro é inferior a 160px e que o botão de ações agrupadas abre menu com Exportar, Editar, Mover para a lixeira e Modo Foco.

**Acceptance Scenarios**:
1. **Dado** um usuário em smartphone (`<= 767px`), **quando** a página do livro é aberta, **então** o cabeçalho exibe a miniatura da capa (48x72px), o título com truncamento elíptico se ultrapassar duas linhas, e o nome do autor na linha superior.
2. **Dado** o cabeçalho móvel condensado, **quando** visualizada a linha inferior, **então** são exibidos os marcadores compactos de categoria e um botão de menu agrupado ("Ações do livro").
3. **Dado** o acionamento do menu "Ações do livro", **quando** o leitor clica no botão, **então** é aberto um menu contextual acessível com as opções "Modo foco", "Exportar anotações", "Editar livro" e "Mover para a lixeira", cada uma com alvo tátil de no mínimo 44x44px.

---

### User Story 2 - Faixa de Capítulos Unificada sem Redundância no Celular (Priority: P1)

Como leitor navegando pelos capítulos de uma obra no celular, quero um seletor único, limpo e aderente que mostre o capítulo ativo e permita alternar de capítulo ou adicionar um novo com rapidez, sem esteiras de pílulas roláveis duplicadas.

**Why this priority**: Elimina a confusão visual causada pela exibição simultânea de dois controles de capítulo na mesma tela móvel e agiliza a troca de capítulos.

**Independent Test**: Abrir um livro com múltiplos capítulos no celular; constatar que a esteira de pílulas horizontais fica oculta no mobile, permanecendo apenas o seletor unificado de capítulos com acesso direto à criação de novo capítulo.

**Acceptance Scenarios**:
1. **Dado** um livro com capítulos cadastrados em tela móvel (`<= 767px`), **quando** a página é exibida, **então** o sistema apresenta exclusivamente o seletor unificado de capítulos contendo o nome e índice do capítulo atual e o total de estudos.
2. **Dado** o seletor móvel, **quando** o usuário seleciona outro capítulo na lista, **então** a rota é atualizada com `?chapter=:id` e os estudos correspondentes são carregados imediatamente sem salto brusco na interface.
3. **Dado** o botão de novo capítulo no mobile, **quando** acionado, **então** o campo de inserção inline é exibido de forma limpa com botão de salvar e cancelar com alvos táteis de no mínimo 44x44px.

---

### User Story 3 - Inspetor Analítico Recolhível por Padrão no Celular (Priority: P2)

Como leitor visualizando estudos no smartphone, quero que a barra inferior de métricas comece recolhida e possa ser expandida sob demanda, para que toda a área útil de rolagem seja dedicada à leitura e aos cards de estudo.

**Why this priority**: Evita que a barra inferior compita por espaço com a barra de navegação móvel e garante máxima imersão na leitura dos estudos.

**Independent Test**: Carregar um livro no mobile; constatar que a barra do inspetor inicia recolhida com o botão "Ver detalhes do livro", e que ao tocá-lo o painel expande suavemente exibindo as métricas contextuais completas.

**Acceptance Scenarios**:
1. **Dado** a visualização do livro no mobile (`<= 767px`), **quando** a página é renderizada, **então** a faixa inferior do inspetor inicia em estado colapsado, exibindo apenas um cabeçalho compacto com o botão "Ver detalhes do livro" e ícone indicador de estado.
2. **Dado** o inspetor colapsado, **quando** o usuário clica em "Ver detalhes do livro", **então** a grade de métricas (total de capítulos, estudos no capítulo, card de foco) é revelada com animação suave respeitando preferências de movimento.
3. **Dado** o inspetor expandido, **quando** o usuário toca novamente no botão (agora exibindo "Ocultar detalhes"), **então** o painel retorna ao estado recolhido.

---

## Edge Cases

- **Livro com título muito longo:** Títulos com mais de 60 caracteres no celular devem truncar graciosamente com reticências após 2 linhas (`-webkit-line-clamp: 2`), sem estourar o contêiner nem sobrepor a miniatura da capa.
- **Livro sem capa cadastrada:** O componente de capa em miniatura (48x72px) deve renderizar o tom determinístico de cor com as iniciais do título de forma legível e proporcional.
- **Livro com apenas um capítulo ou sem capítulos:** O seletor unificado deve tratar graciosamente o estado com um único capítulo (sem desabilitar a criação de novos) ou exibir indicação de nenhum capítulo cadastrado com CTA de inclusão.
- **Alternância de orientação (giro de tela móvel para desktop):** Ao girar o dispositivo para modo paisagem (`>= 768px`), o cabeçalho completo original e a esteira horizontal de pílulas roláveis devem reaparecer automaticamente sem necessidade de recarregar a página.
- **Modo Foco ativado no mobile:** O modo foco deve ocultar tanto a faixa de capítulos quanto o inspetor, garantindo imersão total mesmo em smartphones.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE reorganizar o cabeçalho do livro em formato condensado de linha dupla em dispositivos com largura de tela de até 767px.
- **FR-002**: A linha superior do cabeçalho móvel DEVE exibir a miniatura da capa em proporção reduzida (48x72px), o título do livro e o nome do autor.
- **FR-003**: A linha inferior do cabeçalho móvel DEVE apresentar os chips de categoria em formato compacto e um botão de menu agrupado ("Ações do livro").
- **FR-004**: O menu de ações agrupadas DEVE fornecer acesso com um toque às ações de "Modo foco", "Exportar anotações", "Editar livro" e "Mover para a lixeira", com alvos táteis mínimos de 44x44px.
- **FR-005**: O sistema DEVE ocultar a esteira horizontal de pílulas roláveis de capítulos no mobile, mantendo apenas o seletor unificado de capítulos com suporte à seleção e contagem de estudos.
- **FR-006**: O seletor de capítulos móvel DEVE integrar botão discreto para criação de novo capítulo com formulário inline acessível.
- **FR-007**: A faixa inferior do inspetor analítico DEVE inicializar recolhida por padrão em telas móveis (`<= 767px`), disponibilizando botão acessível para alternância de expansão ("Ver detalhes do livro" / "Ocultar detalhes").
- **FR-008**: Todas as modificações de estilo DEVEM respeitar os 10 temas oficiais do sistema por meio de variáveis CSS semânticas e cumprir a diretriz de acessibilidade para movimento reduzido (`prefers-reduced-motion`).

---

### Key Entities

- **Livro (`Book`)**: Obra literária ou científica cadastrada pelo leitor, contendo título, subtítulo, autor, ano, capa, categorias associadas e coleção de capítulos.
- **Capítulo (`Chapter`)**: Divisão contextual de uma obra, contendo nome, ordem sequencial e lista de estudos associados.
- **Inspetor de Livro (`BookInspector`)**: Conjunto de indicadores analíticos que sumarizam o contexto de leitura (total de capítulos, total de estudos, capítulo ativo e estudo em foco).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em viewport móvel padrão (390x844px), a altura combinada do cabeçalho e da barra de capítulos não ultrapassa 300px, assegurando que o primeiro estudo ou aviso inicial seja visível na primeira dobra da tela sem rolagem vertical prévia.
- **SC-002**: O leitor consegue alternar entre capítulos no smartphone com no máximo 2 toques e com tempo de resposta visual inferior a 100ms.
- **SC-003**: Todas as 4 ações de gerenciamento da obra (Editar, Exportar, Lixeira e Foco) permanecem acessíveis no celular através do menu unificado sem necessidade de rolagem horizontal.
- **SC-004**: 100% dos botões e controles interativos da página do livro possuem alvos táteis de no mínimo 44x44px em telas sensíveis ao toque.

---

## Assumptions

- A visualização em telas desktop (`>= 768px`) preserva a arquitetura horizontal consolidada em 3 faixas empilhadas sem qualquer regressão funcional.
- Os modelos de dados, endpoints de API e contratos de backend permanecem estritamente intactos, em conformidade com o escopo da versão 0.9.
- O componente `DropdownMenu.vue` existente ou elemento de menu contextual acessível será reaproveitado para as ações agrupadas do livro.
