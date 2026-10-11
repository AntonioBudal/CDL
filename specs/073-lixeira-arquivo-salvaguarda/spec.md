# Feature Specification: Lixeira — Arquivo de Salvaguarda e Segurança

**Feature Branch**: `073-lixeira-arquivo-salvaguarda`

**Created**: 2026-10-11

**Status**: Draft

**Input**: User description: "F0.8.8"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Visão de Custódia e Contagem Regressiva Temporal (Priority: P1)

Como leitor do sistema,
quero visualizar claramente os livros e estudos mantidos na custódia temporária da lixeira, acompanhados por indicadores visuais dos dias restantes antes do expurgo automático,
para que eu tenha tranquilidade sobre o que foi descartado e saiba exatamente quanto tempo resta para decidir sobre a recuperação de cada item.

**Why this priority**:
Constitui a fundação da salvaguarda de dados. O usuário precisa de visibilidade imediata sobre o conteúdo da lixeira, sua proveniência (livro ancestral e capítulo) e o prazo de expurgo de 30 dias para não correr risco de perda inadvertida de anotações.

**Independent Test**:
Pode ser testado de forma isolada acessando a visualização da lixeira com livros e estudos descartados em diferentes estágios de retenção, verificando a apresentação dos cartões, a identificação nítida de tipo e a contagem regressiva temporal com destaque de urgência.

**Acceptance Scenarios**:

1. **Given** que existem livros e estudos individuais na lixeira, **When** o usuário acessa a página da lixeira, **Then** o sistema exibe os itens agrupados ou filtrados por abas ("Todos", "Livros" e "Estudos individuais") com seus respectivos contadores numéricos atualizados.
2. **Given** um item descartado na lixeira, **When** ele é renderizado na lista, **Then** o cartão apresenta seu tipo ("Livro" ou "Estudo"), o título, a data de descarte e um indicador visual de retenção temporal evidenciando os dias restantes antes do expurgo permanente de 30 dias.
3. **Given** um estudo descartado pertencente a uma obra do acervo, **When** o cartão é exibido, **Then** o sistema apresenta a hierarquia de proveniência de forma clara (Título do Livro ancestral > Nome do Capítulo).
4. **Given** um item com prazo de expurgo iminente (5 dias ou menos restantes), **When** o cartão é renderizado, **Then** o indicador temporal recebe ênfase visual de urgência diferenciada dos itens recém-descartados.

---

### User Story 2 - Seleção em Lote e Barra Flutuante de Ações Múltiplas (Priority: P2)

Como leitor organizando meu acervo,
quero poder marcar múltiplos livros e estudos na lixeira simultaneamente e acionar comandos em lote a partir de uma barra flutuante de ações,
para que eu possa restaurar ou descartar definitivamente vários itens em uma única operação sem repetições cansativas.

**Why this priority**:
Ações em lote elevam drasticamente a produtividade e a ergonomia de limpeza do acervo, eliminando a fricção de clicar em botões individuais para dezenas de estudos ou livros.

**Independent Test**:
Pode ser testado marcando uma ou mais caixas de seleção, verificando o surgimento animado da barra flutuante com a contagem de itens selecionados e executando a restauração múltipla com feedback imediato.

**Acceptance Scenarios**:

1. **Given** a lista de itens da lixeira, **When** o usuário marca a caixa de seleção de um ou mais itens, **Then** uma barra de ações em lote surge na parte inferior da tela informando a quantidade exata de itens selecionados.
2. **Given** a barra de ações em lote visível, **When** o usuário clica na opção de selecionar todos da aba ativa, **Then** todos os itens visíveis ficam marcados e a barra reflete a contagem total.
3. **Given** itens selecionados na barra de lote, **When** o usuário aciona o comando "Restaurar selecionados", **Then** todos os itens selecionados são restaurados para o acervo ativo, removidos da lista e uma notificação de sucesso consolida a quantidade restaurada.
4. **Given** itens selecionados na barra de lote, **When** o usuário desmarca todos os itens ou clica em cancelar seleção, **Then** a barra de ações em lote é recolhida suavemente.

---

### User Story 3 - Proteção Reforçada e Barreira Contra Expurgo Acidental (Priority: P3)

Como leitor zeloso pelas minhas notas de estudo,
quero que as ações destrutivas irreversíveis (esvaziar toda a lixeira ou excluir definitivamente itens em lote/individuais) possuam confirmação explícita com barreiras deliberadas,
para que um clique involuntário jamais destrua dados preciosos sem minha autorização consciente.

**Why this priority**:
Segurança contra perda acidental de dados é um princípio constitucional inviolável do projeto. Ações de destruição permanente exigem fricção intencional e clara comunicação das consequências irreversíveis.

**Independent Test**:
Pode ser testado acionando o botão "Esvaziar lixeira" ou "Excluir definitivamente" e verificando que a ação nunca ocorre de imediato, exigindo confirmação explícita em diálogo modal protegido com suporte a cancelamento por teclado.

**Acceptance Scenarios**:

1. **Given** que o usuário clica no botão "Esvaziar lixeira", **When** a ação é disparada, **Then** o sistema exibe um diálogo modal de alerta com foco retido, explicando que todos os livros e estudos serão permanentemente destruídos e solicitando confirmação explícita.
2. **Given** o diálogo modal de esvaziamento aberto, **When** o usuário pressiona a tecla Escape ou clica em "Cancelar", **Then** o diálogo é fechado sem realizar nenhuma exclusão e nenhum dado é alterado.
3. **Given** o diálogo modal de esvaziamento aberto, **When** o usuário confirma explicitamente o esvaziamento, **Then** todos os itens da lixeira são permanentemente destruídos, a visualização transita para o estado vazio acolhedor e uma notificação confirma o expurgo total.
4. **Given** itens marcados na seleção em lote, **When** o usuário escolhe "Excluir definitivamente" na barra de ações, **Then** um diálogo de confirmação reforçada é apresentado detalhando o número de itens a serem destruídos antes de qualquer remoção irreversível.

---

### User Story 4 - Restauração Fluida e Resolução de Dependências (Priority: P4)

Como leitor recuperando anotações descartadas,
quero que a restauração individual aconteça com animação suave e resolução transparente da dependência do livro ancestral,
para que eu veja imediatamente o resultado da recuperação e saiba exatamente onde o estudo foi realocado.

**Why this priority**:
Garante continuidade cognitiva e feedback sensorial polido, além de tratar com clareza o caso em que um estudo é restaurado enquanto seu livro de origem também estava descartado.

**Independent Test**:
Pode ser testado restaurando um estudo avulso cujo livro ancestral também está na lixeira, confirmando a animação de saída do cartão, a reativação coerente do livro e a mensagem explicativa no toast de notificação.

**Acceptance Scenarios**:

1. **Given** um item na lista da lixeira, **When** o usuário clica em "Restaurar", **Then** o cartão correspondente anima suavemente sua saída com transição de elevação e desvanecimento, sendo removido da tela e decrementando os contadores da página.
2. **Given** um estudo cujo livro ancestral também se encontrava na lixeira, **When** o usuário restaura o estudo, **Then** o sistema reativa o livro de origem no acervo ativo e notifica claramente o leitor sobre a recuperação conjunta do livro e do estudo.
3. **Given** a lixeira sem itens restantes após operações de restauração ou esvaziamento, **When** o último item é removido, **Then** a página exibe um estado vazio informativo com link de retorno ao acervo principal.

---

### Edge Cases

- **Tentativa de restaurar estudo com livro ancestral também na lixeira**: O sistema deve reativar automaticamente o livro ancestral ou alertar o usuário de forma clara que o livro foi restaurado para acomodar o estudo, sem gerar erros de integridade referencial.
- **Expurgo temporal de itens durante a sessão aberta**: Caso um item atinja 0 dias e seja purgado pelo ciclo automático do sistema enquanto a tela está aberta, a interface deve tratar respostas de item não encontrado com aviso amigável e recarregamento gracioso.
- **Seleção mista de livros e estudos para exclusão em lote**: Ao selecionar múltiplos livros e estudos simultaneamente para expurgo permanente, o diálogo de confirmação deve quantificar separadamente quantos livros e quantos estudos serão destruídos.
- **Cancelamento rápido com foco acessível**: Pressionar a tecla Escape em qualquer diálogo de confirmação deve fechar o diálogo imediatamente e restaurar o foco para o elemento disparador original.
- **Navegação com teclado na grade de seleção**: Cada caixa de seleção deve ser operável via tecla Espaço e navegável via Tab/Shift+Tab, com alvos de toque adequados a dispositivos móveis.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE exibir todos os itens em custódia temporária na lixeira divididos em abas de filtro: "Todos", "Livros" e "Estudos individuais", com contadores numéricos dinâmicos para cada categoria.
- **FR-002**: O sistema DEVE exibir em cada cartão de item descartado seu tipo (Livro ou Estudo), título, autor/origem, data de descarte e um indicador visual de dias restantes antes do expurgo automático de 30 dias.
- **FR-003**: O sistema DEVE aplicar destaque visual de urgência quando a contagem regressiva de um item for menor ou igual a 5 dias restantes.
- **FR-004**: Para estudos individuais na lixeira, o cartão DEVE exibir claramente a hierarquia da obra de proveniência (Livro ancestral > Capítulo associado).
- **FR-005**: Cada cartão de item descartado DEVE possuir uma caixa de seleção (*checkbox*) acessível permitindo marcação individual para operações em lote.
- **FR-006**: O sistema DEVE exibir uma barra flutuante de ações em lote fixada na parte inferior da tela sempre que um ou mais itens estiverem selecionados.
- **FR-007**: A barra de ações em lote DEVE apresentar o contador de itens selecionados, atalho para selecionar/desmarcar todos os itens da aba ativa, botão de "Restaurar selecionados" e botão de "Excluir selecionados".
- **FR-008**: O botão de "Esvaziar lixeira" no cabeçalho e a ação de "Excluir selecionados" na barra de lote DEVEM exigir confirmação explícita por meio de diálogo modal de alerta com barreira deliberada contra destruição acidental.
- **FR-009**: O diálogo de confirmação de exclusão permanente DEVE implementar semântica acessível de alerta (`role="alertdialog"`), retenção de foco (*focus trap*), suporte à tecla Escape para cancelamento e fechamento sem efeitos colaterais ao cancelar.
- **FR-010**: Ao acionar a restauração individual de um item, o cartão correspondente DEVE executar uma animação suave de saída (desvanecimento e elevação), decrementando os contadores e emitindo notificação de confirmação.
- **FR-011**: Ao restaurar um estudo cujo livro de origem também esteja descartado na lixeira, o sistema DEVE reativar o livro ancestral no acervo ativo e informar expressamente essa ação na notificação ao usuário.
- **FR-012**: Quando a lixeira estiver sem nenhum item em custódia, o sistema DEVE exibir uma tela de estado vazio acolhedora, com ícone semântico, mensagem explicativa e botão de navegação para o acervo principal.
- **FR-013**: Todas as ações de seleção, restauração e exclusão DEVEM suportar operação completa por teclado e possuir alvos de toque mínimos de 44x44 pixels em telas sensíveis ao toque.

---

### Key Entities

- **Item Descartado (Livro)**: Registro de uma obra literária em custódia temporária na lixeira, contendo título, autor, quantidade de capítulos, quantidade de estudos vinculados, data de descarte (`deleted_at`) e dias restantes até o expurgo (calculado com base na janela de 30 dias).
- **Item Descartado (Estudo)**: Registro de uma anotação ou estudo individual em custódia temporária, contendo título, livro de origem, capítulo de origem, data de descarte e dias restantes até o expurgo.
- **Lote de Seleção**: Conjunto volátil de identificadores de itens selecionados pelo usuário para execução atômica ou sequenciada de ações em massa (restauração ou exclusão definitiva).
- **Diálogo de Confirmação Reforçada**: Componente modal de salvaguarda que intercepta intenções de destruição irreversível, exigindo clique deliberado do usuário em botão com estilo de perigo e permitindo abortar com Escape.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O usuário consegue identificar os dias restantes para o expurgo permanente de qualquer item na lixeira em menos de 2 segundos de visualização.
- **SC-002**: 100% das ações de destruição definitiva (esvaziar lixeira ou expurgo individual/em lote) exigem confirmação deliberada em diálogo de alerta, impedindo perdas acidentais por clique único.
- **SC-003**: A barra flutuante de ações em lote é exibida em menos de 300 milissegundos após a marcação da primeira caixa de seleção.
- **SC-004**: Usuários conseguem restaurar múltiplos itens selecionados em uma única ação combinada, reduzindo o tempo de recuperação de 5 itens em pelo menos 60% em comparação com restaurações individuais sucessivas.
- **SC-005**: 100% dos fluxos de seleção, confirmação e cancelamento podem ser operados exclusivamente via teclado (teclas Tab, Espaço, Enter e Escape) sem perda ou armadilha de foco.

---

## Assumptions

- O período canônico de custódia temporária da lixeira é de 30 dias corridos a partir da data de descarte (`deleted_at`).
- Quando um livro é descartado, seus estudos subordinados também são mantidos na lixeira sob custódia do livro.
- A restauração de um estudo individual cujo livro ancestral também está na lixeira prioriza a preservação da integridade do acervo reativando o livro automaticamente ou notificando a restauração conjunta.
- Dispositivos móveis e navegadores em tela estreita acomodam a barra flutuante na parte inferior sem sobrepor elementos interativos essenciais do rodapé.
- Todos os testes automatizados da funcionalidade operam exclusivamente com dados fictícios e bancos descartáveis em conformidade com as regras constitucionais de isolamento.
