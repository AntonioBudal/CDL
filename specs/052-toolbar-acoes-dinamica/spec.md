# Feature Specification: F 0.7.3 — Refatoração Dinâmica da Floating Actions Toolbar

**Feature Branch**: `052-toolbar-acoes-dinamica`

**Created**: 2026-10-03

**Status**: Draft

**Input**: User description: "/speckit-specify F0.7.3" (F 0.7.3 — Refatoração Dinâmica da Floating Actions Toolbar: transformar a régua flutuante de ações em uma experiência ágil, contextual e elegante em duas camadas, eliminando o comportamento engessado ao anotar ou criar perguntas)

## Clarifications

### Session 2026-10-03
- Q: Como o botão de marca-texto na barra flutuante deve diferenciar o grifo imediato de 1 clique da abertura da paleta para trocar de cor? → A: Split Button: O corpo do botão/ícone grifa imediatamente com a última cor memorizada, enquanto uma seta sutil adjacente expande a paleta com as 5 cores canônicas.
- Q: Como as teclas de atalho devem se comportar na caixa de texto de anotações e perguntas para equilibrar agilidade e suporte a múltiplas linhas? → A: Tecla Enter salva imediatamente o formulário, enquanto Shift+Enter insere quebras de linha adicionais (estilo notas rápidas), e Escape cancela.
- Q: Como a régua flutuante de ações deve se comportar visualmente enquanto o popover de anotação ou pergunta estiver aberto na tela? → A: A régua principal de botões se recolhe temporariamente enquanto o popover de anotação ou pergunta estiver aberto, eliminando poluição visual e mantendo o foco total no formulário ancorado.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Destaque em 1 Clique com Memorização de Cor e Ações Imediatas (Priority: P1)

Como uma pessoa leitora que sublinha ativamente seus textos, quero aplicar marca-texto imediatamente com um único clique (usando a última cor utilizada) e acionar oclusões de revisão ou cópia de citação sem atritos, para que meu fluxo cognitivo de leitura não seja interrompido por menus intermediários obrigatórios.

**Why this priority**: É a interação mais frequente no estudo (90%+ dos usos da barra flutuante). Eliminar cliques redundantes para grifar é o maior ganho de fluidez e ergonomia.

**Independent Test**: Pode ser testado selecionando qualquer trecho no leitor e clicando no botão principal de marca-texto: o destaque deve ser aplicado instantaneamente com a cor memorizada sem exigir abertura da paleta.

**Acceptance Scenarios**:

1. **Given** que o leitor selecionou um trecho de texto no estudo, **When** ele clica no botão principal de marca-texto, **Then** o destaque é criado imediatamente com a cor memorizada no dispositivo (padrão amarelo), emitindo notificação de confirmação e limpando a seleção.
2. **Given** que o leitor selecionou um trecho e deseja alternar a cor, **When** ele abre a paleta de cores rápida e escolhe uma nova cor (ex.: verde), **Then** o trecho é destacado com a nova cor e essa opção passa a ser a nova cor padrão memorizada para os próximos cliques diretos.
3. **Given** que um trecho foi selecionado, **When** o usuário clica em "Ocultar trecho" ou "Copiar citação", **Then** a ação é executada em 1 único clique, sem expandir ou distorcer a barra.

---

### User Story 2 - Camada Desacoplada de Anotação e Pergunta com Foco Ágil (Priority: P2)

Como uma pessoa que registra reflexões e formula perguntas ativas sobre a obra, quero que os formulários de anotação e pergunta abram em um popover contextual independente e focado, para que a régua principal de botões não se estique bruscamente sobre o texto e eu possa salvar rapidamente via teclado (`Enter`) ou cancelar (`Esc`).

**Why this priority**: Evita a experiência desajeitada (*clumsy*) atual, onde a régua dobra de tamanho e encobre as linhas de leitura que o usuário está anotando.

**Independent Test**: Selecionar um trecho, clicar em "Anotar" ou "Pergunta": verificar que a régua de botões não se deforma, o campo de texto recebe foco automático imediatamente e `Enter` salva o registro.

**Acceptance Scenarios**:

1. **Given** que um trecho está selecionado e a barra flutuante está visível, **When** o usuário clica em "Anotar", **Then** a régua de botões permanece intacta e abre-se um popover leve ancorado logo abaixo da seleção com campo de texto em foco automático (`autofocus`).
2. **Given** que o popover de anotação está aberto com texto digitado, **When** o usuário pressiona a tecla `Enter` (ou clica no botão de confirmação), **Then** a anotação é salva, o popover se fecha e uma notificação de sucesso é exibida.
3. **Given** que o popover de anotação ou pergunta está aberto, **When** o usuário pressiona `Escape` ou clica fora da área, **Then** a operação é cancelada e o popover se fecha sem salvar alterações.

---

### User Story 3 - Ergonomia Mobile com Gaveta Inferior e Proteção de Teclado Virtual (Priority: P3)

Como uma pessoa leitora que utiliza o smartphone, quero que a inserção de anotações ou perguntas se adapte confortavelmente em uma gaveta inferior móvel (*bottom sheet*), para que o teclado virtual do celular não cubra o campo de digitação nem desloque a página de forma descontrolada.

**Why this priority**: Garante uma experiência tátil impecável em telas sensíveis ao toque, onde o teclado virtual ocupa mais de 40% da área útil da tela.

**Independent Test**: Em viewport móvel (< 768px), selecionar uma palavra e abrir "Anotar": a interface deve ancorar o campo na base da viewport visível (`visualViewport`), garantindo visibilidade total durante a digitação.

**Acceptance Scenarios**:

1. **Given** um dispositivo móvel com texto selecionado, **When** o leitor clica em "Anotar" ou "Pergunta", **Then** abre-se uma gaveta inferior com alvo de toque touch-friendly (botões ≥ 44px) e espaçamento superior ao teclado virtual.
2. **Given** que o teclado virtual do celular é exibido, **When** a viewport visível é reduzida, **Then** o formulário de anotação se reposiciona dinamicamente para permanecer acima do teclado sem cobrir o botão de salvar.
3. **Given** que a gaveta móvel está aberta, **When** o leitor arrasta para baixo ou toca no botão de fechar, **Then** o formulário é descartado e o leitor retorna ao texto.

---

### Edge Cases

- **Seleção no topo extremo ou base extrema da página**: A régua e o popover devem detectar as bordas do viewport e inverter sua orientação (aparecer abaixo quando não houver espaço acima e vice-versa), nunca ultrapassando os limites da janela.
- **Teclado virtual abrindo/fechando no celular**: A ancoragem deve escutar alterações na API `window.visualViewport` para recalcular a altura máxima utilizável sem perda de foco.
- **Seleção desfeita enquanto formulário está aberto**: Se o usuário desselecionar acidentalmente o texto pelo navegador com o popover já aberto, o popover mantém a referência da seleção até o usuário cancelar explicitamente ou salvar.
- **LocalStorage indisponível ou corrompido**: Se `localStorage` falhar ou contiver valor inválido de cor, o sistema utiliza o amarelo (`yellow`) como fallback seguro sem interromper o funcionamento.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE implementar o controle de marca-texto como um botão bipartido (*Split Button*), onde o clique no ícone principal aplica instantaneamente a cor memorizada em 1 clique direto.
- **FR-002**: O sistema DEVE persistir a última cor de marca-texto utilizada pelo leitor no armazenamento local (`localStorage`), restaurando-a automaticamente em novas sessões de estudo.
- **FR-003**: O sistema DEVE disponibilizar uma seta/indicador expansor adjacente no Split Button que abre a paleta rápida para alternância entre as 5 cores canônicas (amarelo, verde, azul, rosa, roxo).
- **FR-004**: O sistema DEVE executar as ações imediatas de "Ocultar trecho" (Active Recall) e "Copiar citação" em 1 clique direto a partir da régua flutuante.
- **FR-005**: O formulário de "Anotar" e "Pergunta" DEVE ser desacoplado da régua flutuante, abrindo em camada de popover ancorado independente que recolhe temporariamente a régua de ações principal, mantendo foco exclusivo no formulário sem distorcer dimensões visuais.
- **FR-006**: O campo de entrada do formulário de anotação/pergunta DEVE receber foco automático imediato ao abrir e responder à tecla `Enter` para salvar diretamente, permitindo `Shift+Enter` para novas linhas, e `Escape` para cancelamento.
- **FR-007**: Em visualizações móveis, o formulário de anotação/pergunta DEVE adotar formato de gaveta inferior (*bottom sheet*) ajustada dinamicamente à área visível do teclado (`window.visualViewport`).
- **FR-008**: Ao concluir qualquer ação (destaque, anotação, oclusão ou cópia), o sistema DEVE emitir o micro-toast informativo correspondente e limpar a seleção ativa.

### Key Entities

- **SelectionContext**: Representa o trecho de texto capturado no estudo (`section`, `start_offset`, `end_offset`, `selected_text`, `prefix`, `suffix`).
- **ToolbarMode**: Estado operacional da barra flutuante (`idle`, `color_palette`, `note_popover`, `question_popover`).
- **HighlightColorPreference**: Cor memorizada para ação rápida de grifar (`yellow` | `green` | `blue` | `pink` | `purple`).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O leitor consegue aplicar um destaque de texto com a cor padrão em **1 único clique**, reduzindo o tempo médio de marcação em pelo menos 50% em comparação ao fluxo anterior.
- **SC-002**: A régua flutuante de ações mantém largura dimensional estável ao acionar notas ou perguntas, com **0 deformações estruturais** nos botões principais.
- **SC-003**: O fluxo completo de criar uma anotação pode ser executado **100% via teclado** (`Atalho/Clique → Digitação imediata → Enter`), sem necessidade de reposicionar o cursor com o mouse.
- **SC-004**: Em dispositivos móveis com largura a partir de 320px e teclado virtual ativo, o campo de digitação e o botão de confirmação permanecem **100% visíveis** sem rolagem forçada da página.

---

## Assumptions

- A infraestrutura de endpoints `/api/studies/{id}/highlights` existente é reutilizada integralmente, sem alterações de backend ou migrações de schema de banco.
- O navegador do usuário suporta `window.visualViewport` e `localStorage` (com fallbacks limpos caso estejam indisponíveis).
- Os padrões de acessibilidade WCAG 2.1 AA (alvos de toque mínimos de 44x44px no mobile, navegação por teclado e semântica de formulário) são rigorosamente cumpridos.
