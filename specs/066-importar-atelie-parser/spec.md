# Feature Specification: F0.8.05 — Ateliê de Fichamento e Parser Estruturado

**Feature Branch**: `066-importar-atelie-parser`

**Created**: 2026-10-10

**Status**: Draft

**Input**: User description: "Feature 05: Importar — Ateliê de Fichamento e Parser Estruturado (Roadmap 0.8 — Redesign Estrutural e Arquitetura Visual)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ateliê em Duas Colunas Sincronizadas (Two-Pane Studio) e Faixa Superior Compacta (Priority: P1) [MVP]

O leitor acessa a rota `/importar` para fichar uma leitura e encontra um ateliê de transformação textual em duas colunas sincronizadas (*Two-Pane Studio*), substituindo o longo e burocrático formulário vertical antigo:

1. **Faixa Superior Compacta de Metadados:**
   - Barra horizontal unificada e compacta posicionada no topo com seletores de **Livro** e **Capítulo**, além dos campos opcionais de **Página/Localização** e **Título do estudo**.
   - Libera quase 100% da altura vertical da tela para o trabalho cognitivo de escrita e conferência.
   - Preserva carregamento assíncrono de livros e capítulos, validações de obrigatoriedade e aviso contextual quando um livro não possui capítulos.

2. **Painel Esquerdo (Editor da Fonte Bruta):**
   - Área de edição ampla, confortável e imersiva para o texto-base da fonte colada ou digitada.
   - Contador dinâmico de palavras e caracteres no rodapé do editor.
   - Suporte a colar texto (`Ctrl+V`) com processamento imediato sem travar o navegador.
   - Indicador de estado desatualizado (*stale*) discreto quando o texto for modificado após a análise preliminar.

3. **Painel Direito (Prévia Estruturada Viva das Seções):**
   - Exibição em tempo real ou sob demanda das quatro seções semânticas do fichamento: **Resumo**, **Explicação**, **Conceitos-chave** e **Referências/Citações**.
   - Cartões estruturados elegantes que indicam claramente o conteúdo parseado e status vazio (*Vazia*) para seções ainda não detectadas.
   - Bloco de **Conteúdo Não Classificado** com botões rápidos de 1 clique para atribuir trechos residuais a qualquer uma das quatro seções.
   - Painel de avisos da análise (`warnings`) formatado de maneira acolhedora e integrada ao tema.

**Why this priority**: Substitui um formulário transacional monótono por um ambiente de ateliê imersivo, fornecendo feedback visual imediato de como o texto da fonte se organiza no modelo de estudo de quatro dimensões do Leitorum.

**Independent Test**: Acessar `/importar`, selecionar livro e capítulo na barra superior compacta, colar um texto de estudo no editor esquerdo, verificar a renderização estruturada instantânea das 4 seções no painel direito e realizar o salvamento com sucesso.

**Acceptance Scenarios**:

1. **Given** a página `/importar` carregada, **When** o usuário examina o layout, **Then** os campos de Livro, Capítulo, Localização e Título ocupam uma barra superior compacta e a área principal é dividida em dois painéis verticais lado a lado (*Two-Pane Studio*).
2. **Given** um texto colado no editor do painel esquerdo, **When** o parser é executado (automaticamente ao colar ou via botão 'Analisar texto'), **Then** o painel direito exibe as quatro seções estruturadas com seus respectivos conteúdos categorizados sem recarga de página.
3. **Given** texto residual não categorizado pelo parser, **When** exibido no card de conteúdo não classificado, **Then** o leitor pode clicar em qualquer um dos botões de 1 clique ('Resumo', 'Explicação', 'Conceitos', 'Referências') e o texto é imediatamente movido para a seção escolhida.
4. **Given** os metadados válidos e as seções conferidas, **When** o leitor aciona 'Salvar estudo', **Then** o estudo é persistido no banco de dados e a tela de confirmação de salvamento é exibida com links de direcionamento.

---

### User Story 2 - Barra de Ferramentas Flutuante Contextual e Modos de Foco (Priority: P1) [MVP]

Para manter a área de escrita desobstruída e zen, a antiga barra estática de botões cinzas fixada acima do textarea é substituída por:

1. **Barra de Ferramentas Contextual Flutuante:**
   - Aparece suavemente suspensa sobre o texto quando o usuário faz uma seleção no editor.
   - Disponibiliza ações essenciais de formatação Markdown: Negrito (`Ctrl+B`), Itálico (`Ctrl+I`), Título H3, Tabela, Bloco de Código e Link (`Ctrl+K`).
   - Posiciona-se dinamicamente próxima à seleção sem obstruir a visão do texto selecionado.
   - Desaparece automaticamente ao desselecionar ou ao pressionar `Esc`.
   - Um botão discreto e acessível na barra de rodapé do editor permite acionar as mesmas ferramentas caso o leitor prefira interação por clique sem seleção.

2. **Alternância entre Modos de Visualização (*View Mode Toggle*):**
   - Controle segmentado elegante permitindo alternar entre:
     - **Dividido (50/50):** Edição e prévia lado a lado (modo padrão em telas amplas).
     - **Apenas Fonte (100% Editor):** Modo de foco total na escrita ou leitura da fonte bruta.
     - **Apenas Prévia (100% Prévia):** Foco na conferência da nota sintetizada e refinamento das 4 seções.
   - Transição suave entre modos em 180ms acelerada por GPU.

**Why this priority**: Reduz a poluição visual na digitação, garantindo ergonomia moderna similar a editores reflexivos e concedendo controle total sobre a divisão de espaço visual.

**Independent Test**: Selecionar um trecho de texto no editor, verificar o surgimento da barra flutuante, aplicar negrito e link, alternar para o modo 'Apenas Fonte' e 'Apenas Prévia' e constatar a animação suave e a persistência do conteúdo editado.

**Acceptance Scenarios**:

1. **Given** texto digitado no editor esquerdo, **When** o usuário seleciona um trecho com o mouse ou teclado, **Then** a barra de ferramentas flutuante surge suavemente acima ou abaixo da seleção com botões táteis de formatação.
2. **Given** uma palavra selecionada e a barra flutuante visível, **When** o botão 'Negrito' é acionado (ou atalho `Ctrl+B`), **Then** a marcação `**palavra**` é aplicada e a barra atualiza o estado.
3. **Given** o ateliê no modo dividido (50/50), **When** o usuário clica no modo 'Apenas Fonte', **Then** o painel esquerdo expande suavemente para 100% da largura útil sem perda de foco.
4. **Given** o ateliê no modo 'Apenas Prévia', **When** o usuário volta para o modo dividido, **Then** a grade de 50/50 é restaurada instantaneamente.

---

### User Story 3 - Pulso de Detecção Estrutural, Tratamento Térmico e Debounce (Priority: P2)

O leitor que manipula fontes densas (artigos, capítulos extensos, transcripts de mais de 2.000 palavras) precisa de uma resposta ágil e tátil sem congelamentos:

1. **Pulso Luminoso de Detecção Estrutural:**
   - Quando o parser identifica automaticamente uma quebra de seção ou título na fonte colada, os cartões de seção do painel de prévia emitem um pulso visual discreto (`animation: section-pulse 400ms ease-out`), comunicando que a estrutura foi reconhecida.
2. **Debounce e Rendimento com Textos Densos:**
   - Análise automática e renderização da prévia utilizam debounce otimizado (300ms) para não travar a digitação contínua nem bloquear o thread principal do navegador.
3. **Avisos da Análise e Estados Térmicos:**
   - Seções vazias exibem marcadores discretos e amigáveis sem tom punitivo.
   - Avisos sobre linhas ambíguas ou ausência de fontes são apresentados com cartões de alerta acolhedores integrados ao tema visual selecionado.

**Why this priority**: Garante fluidez técnica para textos extensos e fornece feedback visual tangível durante a transformação do texto bruto.

**Independent Test**: Colar um texto de 2.500 palavras com títulos variados, verificar a ausência de quedas de frames ou travamento de digitação, e conferir o pulso sutil nos cartões do preview quando a análise é concluída.

**Acceptance Scenarios**:

1. **Given** um texto estruturado colado no editor, **When** a detecção automática identifica as seções, **Then** os cartões de seção no painel direito recebem uma indicação luminosa suave respeitando as variáveis de `--color-accent` e `--radius-card`.
2. **Given** digitação rápida em fluxo contínuo de texto longo, **When** o usuário digita no editor, **Then** a interface permanece fluida a 60 FPS sem engasgos graças ao debounce de prévia.
3. **Given** preferência de sistema `prefers-reduced-motion: reduce`, **When** o pulso de detecção é acionado, **Then** a animação é suprimida instantaneamente.

---

### User Story 4 - Integração com Promoção do Inbox, Responsividade e Acessibilidade (Priority: P3)

O ateliê se integra perfeitamente com o fluxo de triagem e adapta-se a dispositivos móveis e acessibilidade universal:

1. **Promoção de Capturas do Inbox (`promote_inbox_id`):**
   - Ao receber o parâmetro `promote_inbox_id` via query string, exibe o banner acolhedor de promoção no topo, carrega o conteúdo da captura no editor e vincula a conclusão com `promoteInboxCapture`.
2. **Responsividade em Telas Intermediárias e Móveis (< 1024px):**
   - O layout de duas colunas colapsa harmoniosamente em abas segmentadas no topo: **[Texto da Fonte]** e **[Prévia Estruturada]**.
   - No mobile (< 768px), os seletores compactos organizam-se em duas linhas empilhadas e a área de toque dos botões mantém no mínimo 44x44px.
3. **Acessibilidade por Teclado e Zero Emojis:**
   - Navegação completa por teclado com estados `:focus-visible` evidentes (`--ring-focus`).
   - Ausência absoluta de emojis literais em favor do catálogo vetorial SVG `Icon.vue`.
   - Compatibilidade total com os 10 temas nativos (imunidade cromática absoluta).

**Why this priority**: Preserva 100% das integrações do produto e garante que o ateliê seja utilizável em laptops compactos, tablets e smartphones.

**Independent Test**: Abrir `/importar?promote_inbox_id=...`, verificar banner de promoção, redimensionar a janela para 800px e 375px conferindo as abas responsivas, navegar exclusivamente com teclado e salvar.

**Acceptance Scenarios**:

1. **Given** navegação iniciada a partir do Inbox via 'Promover a Estudo', **When** a tela `/importar` carrega, **Then** o banner de promoção é exibido e o texto da captura preenche automaticamente o editor e a seção de resumo.
2. **Given** largura de tela menor que 1024px, **When** o ateliê é renderizado, **Then** o layout exibe abas segmentadas ('Texto da Fonte' e 'Prévia Estruturada') para alternância confortável sem quebra de scroll.
3. **Given** navegação puramente via teclado (`Tab`, `Shift+Tab`, atalhos de formatação), **When** o leitor navega pelos controles, **Then** todos os botões e campos possuem anéis de foco nítidos sem bloqueios ou armadilhas de foco.

---

## Functional Requirements

- **FR-001**: O cabeçalho de metadados deve ser uma barra horizontal compacta no topo contendo seleção de Livro (obrigatório), Capítulo (obrigatório), Página/Localização (opcional) e Título do estudo (opcional).
- **FR-002**: A área principal de trabalho deve adotar a arquitetura *Two-Pane Studio*, dividida em painel de edição da fonte (à esquerda) e painel de prévia estruturada viva (à direita).
- **FR-003**: O painel esquerdo deve conter contador dinâmico de palavras e caracteres, suporte a `paste` automático e botão manual para acionar a análise de texto.
- **FR-004**: O painel direito deve exibir os cartões estruturados das 4 seções: Resumo, Explicação, Conceitos-chave e Referências/Citações, indicando visualmente seções preenchidas e seções vazias.
- **FR-005**: O painel direito deve exibir o bloco de Conteúdo Não Classificado com botões de 1 clique para atribuir texto a qualquer uma das quatro seções sem perda de dados.
- **FR-006**: A barra de ferramentas de formatação Markdown deve operar de forma flutuante contextual sobre o texto selecionado, com fallback de botões acessíveis no rodapé do editor.
- **FR-007**: A barra de ferramentas flutuante deve suportar Negrito, Itálico, Título H3, Tabela, Bloco de Código e Link, integrando-se aos atalhos `Ctrl+B`, `Ctrl+I`, `Ctrl+K`.
- **FR-008**: O ateliê deve disponibilizar alternância de modos de visualização (*Split 50/50*, *Apenas Fonte 100%*, *Apenas Prévia 100%*) com transição em até 180ms.
- **FR-009**: O parser de preview deve incluir pulso luminoso sutil de confirmação de detecção estrutural e aplicar debounce de no mínimo 300ms para digitação contínua.
- **FR-010**: Em viewports abaixo de 1024px, o painel duplo deve colapsar automaticamente em abas segmentadas ('Texto da Fonte' vs 'Prévia Estruturada').
- **FR-011**: O fluxo de promoção de capturas do Inbox (`promote_inbox_id`) deve ser plenamente suportado e acionar `promoteInboxCapture` ao salvar com sucesso.
- **FR-012**: Todos os elementos estilizados devem consumir estritamente as variáveis semânticas dos 10 temas nativos, com zero emojis literais em templates e código.

---

## Success Criteria

- **SC-001**: O formulário vertical monolítico é 100% substituído pelo ateliê *Two-Pane Studio*, liberando a área de trabalho para foco de leitura e escrita.
- **SC-002**: A barra estática cinza de formatação Markdown é substituída pela barra contextual flutuante com suporte a seleção de texto e atalhos universais.
- **SC-003**: Testes com textos longos (> 2.000 palavras) ocorrem sem travamentos de digitação (latência de input < 50ms) e a prévia é atualizada de forma suave.
- **SC-004**: 100% dos testes unitários e de integração de `/importar` passam com sucesso (`npm test` e `pytest`), sem quebras de build (`npm run build`).
- **SC-005**: A interface mantém conformidade total com os 10 temas cromáticos e atende a `prefers-reduced-motion` com fallbacks imediatos.
