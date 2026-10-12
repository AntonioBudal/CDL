# Feature Specification: Página Inicial sem Login (SEO) — Manifesto do Leitor Reflexivo

**Feature Branch**: `074-manifesto-leitor-reflexivo`

**Created**: 2026-10-11

**Status**: Draft

**Input**: User description: "Planejamento — Página Inicial sem Login: Manifesto do Leitor Reflexivo (F0.8.09)"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Hero Editorial Assimétrico e Manifesto do Leitor (Priority: P1)

Como leitor ou pesquisador que chega à página inicial sem cadastro,
quero encontrar uma abertura tipográfica marcante, elegante e reflexiva com mensagem clara sobre o método de leitura em camadas,
para que eu compreenda imediatamente o propósito do Leitorum como um refúgio de concentração e estudo profundo contra a dispersão da leitura rasa na internet.

**Why this priority**:
Representa o primeiro contato e a principal declaração de valor do produto. Define a atmosfera editorial do sistema, estabelece a primeira impressão estética e oferece as vias primárias de conversão e entrada.

**Independent Test**:
Pode ser testado acessando a rota pública inicial (`/`) em qualquer dispositivo, verificando a composição assimétrica com tipografia clássica, sobrelinha, título editorial ("Ler devagar é uma forma de pensar"), subtítulo manifesto, ficha de leitura conceitual e botões claros de ação.

**Acceptance Scenarios**:

1. **Given** um visitante não autenticado acessando a raiz (`/`), **When** a página carrega, **Then** o sistema exibe o Hero com composição tipográfica assimétrica, sobrelinha em versalete ("Caderno de leitura e estudo em camadas"), título principal e subtítulo ensaístico.
2. **Given** a seção Hero em exibição, **When** o usuário observa a coluna lateral (desktop) ou abaixo do texto (mobile), **Then** é exibida uma Ficha de Leitura conceitual detalhando as quatro perguntas do método (Resumo, Explicação, Conceitos, Referências).
3. **Given** os controles de ação no Hero, **When** o visitante clica em "Criar Conta Gratuita", **Then** é direcionado para a rota de registro (`/registro`); se clica em "Já possuo conta (Entrar)", é direcionado para a tela de identificação (`/login`).
4. **Given** o cabeçalho público da página, **When** visualizado em desktop, **Then** exibe a marca em tipografia editorial, links-âncora ("Método", "Temas", "Princípios") e ação de "Entrar"; no mobile, exibe a marca e ação de "Entrar", otimizando espaço.

---

### User Story 2 - Bancada Interativa do Simulador em 4 Dimensões (Priority: P2)

Como visitante interessado no método,
quero experimentar na prática como funciona o fichamento em 4 camadas através de um simulador interativo na própria página inicial,
para que eu comprove o valor intelectual da ferramenta antes de decidir criar uma conta, sem depender de cadastros prévios ou chamadas de rede.

**Why this priority**:
A melhor forma de demonstrar um método cognitivo é permitindo que o leitor o experimente diretamente. O simulador in-place remove qualquer barreira de adoção e prova a utilidade do Leitorum em menos de um minuto de navegação.

**Independent Test**:
Pode ser testado interagindo com o simulador literário na seção `#metodo`, alternando entre as abas (Resumo analítico, Explicação aprofundada, Conceitos-chave, Referências e conexões), verificando a transição suave de texto e a sincronização com as marcas do trecho de Machado de Assis.

**Acceptance Scenarios**:

1. **Given** a seção da bancada do simulador (`#metodo`), **When** o visitante visualiza o componente, **Then** é apresentada uma metáfora visual de livro aberto: à esquerda, o trecho literário clássico de Machado de Assis (*Memórias Póstumas de Brás Cubas*, prólogo "Ao leitor") com marcas e nota marginal; à direita, o caderno analítico com abas para as 4 dimensões.
2. **Given** a aba "Resumo analítico" ativa por padrão, **When** o visitante clica em "Explicação aprofundada", "Conceitos-chave" ou "Referências e conexões", **Then** o painel de texto transita suavemente (esmaecimento em 150ms) exibindo a respectiva análise metodológica, sem salto de layout (CLS zero).
3. **Given** uma dimensão selecionada no simulador, **When** o visitante observa o trecho literário da obra, **Then** as marcas no texto correspondentes àquela dimensão recebem destaque visual simultâneo (realce de fundo e sublinhado duplo), mantendo as demais com sublinhado simples.
4. **Given** um dispositivo móvel com tela estreita, **When** a bancada é visualizada, **Then** o trecho é exibido em formato compacto com botão para expandir ("Ler o trecho inteiro"), e as abas das dimensões são dispostas em faixa horizontal com rolagem e alinhamento (*scroll-snap*).

---

### User Story 3 - Ateliê Vitrine dos 10 Temas Canônicos (Priority: P3)

Como leitor cuidadoso com a fadiga visual,
quero explorar os 10 temas oficiais do Leitorum e ver a paleta de cores ser aplicada instantaneamente na página,
para que eu comprove o conforto estético e a ergonomia de leitura em diferentes iluminações e superfícies antes de me cadastrar.

**Why this priority**:
O conforto ocular é um dos maiores diferenciais do produto. Permitir a troca de paleta ao vivo transforma a visita numa experiência sensorial tangível e demonstra o cuidado editorial com a tipografia e o contraste.

**Independent Test**:
Pode ser testado selecionando qualquer um dos 10 temas na grade de paletas da seção `#temas`, verificando a repintura imediata da página e o anúncio acessível do tema selecionado, sem perda de estado e sem persistência indesejada no armazenamento local da visita anônima.

**Acceptance Scenarios**:

1. **Given** a seção de temas (`#temas`), **When** o visitante visualiza a vitrine, **Then** o sistema exibe uma grade com os 10 temas canônicos oficiais (`papel-fosco`, `noite-suave`, `cinza-neutro`, `grafite`, `monocromatico`, `pergaminho`, `e-ink`, `solario`, `fiorde`, `voltagem`), cada um representado por um cartão de amostra com suas quatro cores reais (`page`, `surface`, `text`, `accent`).
2. **Given** a grade de temas, **When** o visitante clica em um tema (ex.: `pergaminho`), **Then** a página inteira é repintada instantaneamente com a nova paleta e o cartão selecionado exibe anel de foco luminoso e indicador de marcação.
3. **Given** um tema selecionado na vitrine, **When** a mudança ocorre, **Then** uma linha de estado acessível informa: "Tema aplicado: [Nome do Tema]. A página inteira foi repintada."
4. **Given** que o visitante navega por teclado na grade de temas, **When** utiliza as setas direcionais, **Then** a seleção e a repintura acompanham o foco, respeitando o padrão de grupo de seleção com tecla única de tabulação.
5. **Given** que o visitante sai da página inicial para outra rota, **When** a página desmonta, **Then** as variáveis temporárias de cor são restauradas ao estado original sem poluir as preferências definitivas do navegador.

---

### User Story 4 - Soberania de Dados e Tradição Histórica do Método (Priority: P4)

Como leitor que valoriza a integridade dos seus pensamentos,
quero ler com total clareza os compromissos de soberania de dados do Leitorum e a linhagem histórica do método de estudo em camadas,
para que eu confie no produto como uma ferramenta sustentável, transparente e livre de exploração comercial.

**Why this priority**:
A confiança é o pilar fundamental de um caderno de notas. Em vez de depoimentos inventados de marketing, a página ancora sua autoridade na tradição centenária dos *commonplace books* e na garantia explícita de soberania.

**Independent Test**:
Pode ser testado inspecionando a seção `#principios` e a linha do tempo histórica, verificando a clareza das 4 garantias de soberania, a ausência de alegações enganosas e os links institucionais para `/apoie` e `/sobre`.

**Acceptance Scenarios**:

1. **Given** a seção de soberania (`#principios`), **When** o leitor lê as diretrizes, **Then** o sistema apresenta 4 compromissos inequívocos:
   - *Sem anúncios nem rastreadores* (zero telemetria, zero pixels de rastreamento);
   - *Suas notas não alimentam modelos* (nenhum dado enviado a terceiros ou usado para treinar IA);
   - *Você pode levar tudo embora* (exportação aberta e possibilidade de execução local-first);
   - *Software livre sustentado por leitores* (código aberto e sustentação comunitária).
2. **Given** a seção da tradição histórica, **When** o leitor percorre a linha do tempo, **Then** são apresentados três marcos temporais verificáveis:
   - Século XVI (os cadernos de lugares-comuns e a memória do leitor);
   - 1706 (o método de índice de John Locke);
   - Hoje (o fichamento em camadas digital com conexões cruzadas e revisão).
3. **Given** a seção de fecho da página, **When** o leitor atinge o final da leitura, **Then** encontra uma chamada reflexiva de conversão ("Comece pelo próximo livro que você pretende ler devagar") e o rodapé institucional com links para Sobre, Apoie, licença e repositório.

---

### User Story 5 - Infraestrutura de SEO, Acessibilidade e Performance (Priority: P5)

Como motor de busca, leitor de tela ou usuário em conexão lenta,
quero acessar uma página rápida, totalmente indexável, acessível segundo padrões WCAG AAA e semanticamente rica,
para que o conteúdo seja encontrado organicamente na web e utilizável por qualquer pessoa sem barreiras técnicas.

**Why this priority**:
Garante que o manifesto cumpra seu propósito de descoberta orgânica (SEO) e atenda aos mais altos padrões de qualidade técnica da web aberta.

**Independent Test**:
Pode ser testado validando a presença do JSON-LD Schema.org estruturado, metatags Open Graph/Twitter completas, contraste visual mínimo de 7:1 em textos de leitura contínua, acessibilidade ARIA e desempenho avaliado no Google Lighthouse com meta de 95+ em todas as categorias.

**Acceptance Scenarios**:

1. **Given** o HTML entregue na rota `/`, **When** inspecionado por um rastreador ou leitor, **Then** o documento contém título descritivo (`Leitorum — caderno de leitura e estudo em camadas`), meta description precisa, tags canônicas, Open Graph com imagem e texto alternativo, e marcação Schema.org em JSON-LD (`SoftwareApplication` / `WebApplication` com `applicationCategory: "EducationalApplication"`).
2. **Given** o conteúdo vital da página (h1, manifesto, trecho literário, painéis do simulador e princípios), **When** avaliado sem execução prévia de JavaScript dinâmico, **Then** os textos essenciais estão presentes no documento para indexação direta.
3. **Given** os textos de leitura contínua, **When** avaliados em qualquer um dos temas oficiais, **Then** mantêm taxa de contraste de pelo menos 7:1 (WCAG AAA) nos corpos de texto e 4,5:1 em elementos de suporte.
4. **Given** o carregamento de fontes e scripts na página pública, **When** medido em ambiente de produção, **Then** as fontes essenciais utilizam `font-display: swap` com pré-carregamento restrito, as rotas autenticadas pesadas são carregadas sob demanda e a pontuação Lighthouse atinge 95 ou superior em Performance, Acessibilidade, Melhores Práticas e SEO.

---

### Edge Cases

- **Navegação com preferências de movimento reduzido (`prefers-reduced-motion`)**: Ao alternar entre as 4 dimensões no simulador ou trocar temas na vitrine, todas as transições visuais de esmaecimento e cor tornam-se instantâneas, sem disparar efeitos de movimento.
- **Visualização sob o tema e-ink**: No tema monocromático e-ink, todas as marcas de texto contam com sublinhados duplos e formas geométricas de alto contraste, sem depender de pigmentação cromática para identificar dimensões.
- **Telas ultraestreitas (320px) e zoom de 200%**: A página mantém integridade de leitura completa, empilhando o livro e o caderno do simulador sem provocar rolagem horizontal indesejada.
- **Teclado sem mouse**: O simulador de abas implementa foco itinerante com suporte completo a setas esquerda/direita, Home, End e tecla Tab para avançar diretamente ao painel analítico com `tabindex="0"`.
- **Restauração de tema ao navegar para login ou registro**: A seleção de tema da vitrine permanece restrita ao ciclo de vida da página inicial em memória, restaurando a preferência original do usuário caso ele navegue para fora da landing page.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE disponibilizar na raiz pública (`/`) um Hero editorial assimétrico com sobrelinha em versalete, título de manifesto ("Ler devagar é uma forma de pensar"), subtítulo reflexivo e cartão informativo da Ficha de Leitura em 4 partes.
- **FR-002**: O Hero DEVE conter botões de conversão claros e contrastantes: "Criar Conta Gratuita" direcionando para `/registro` e "Já possuo conta (Entrar)" direcionando para `/login`.
- **FR-003**: O cabeçalho público DEVE conter a marca do produto, links-âncora de salto para as seções da página (`#metodo`, `#temas`, `#principios`) e ação direta de entrada, adaptando-se em telas estreitas com um link inicial acessível de "Pular para o conteúdo".
- **FR-004**: O sistema DEVE incorporar uma bancada interativa do Simulador em 4 Dimensões na seção `#metodo`, com metáfora visual de livro aberto (trecho da obra à esquerda e caderno analítico à direita no desktop).
- **FR-005**: O simulador DEVE conter o trecho clássico do prólogo "Ao leitor" de *Memórias Póstumas de Brás Cubas* (Machado de Assis, 1881), apresentando citação, marcas analíticas de texto e nota marginal.
- **FR-006**: O simulador DEVE conter quatro abas acessíveis no topo do caderno: "Resumo analítico", "Explicação aprofundada", "Conceitos-chave" e "Referências e conexões", com transição de opacidade de 150ms ao alternar entre os conteúdos.
- **FR-007**: Ao alternar uma aba no simulador, o sistema DEVE sincronizar o realce visual das marcas do trecho correspondentes àquela dimensão (fundo preenchido e sublinhado duplo), mantendo as demais com sublinhado simples.
- **FR-008**: O simulador DEVE funcionar 100% no cliente com textos pré-carregados e altura mínima fixa no painel analítico, garantindo ausência de requisições de rede e prevenção de desvios de layout (CLS zero).
- **FR-009**: O sistema DEVE apresentar uma vitrine interativa dos 10 temas oficiais na seção `#temas`, com cartões de paleta exibindo as quatro cores reais de cada tema (`page`, `surface`, `text`, `accent`).
- **FR-010**: Ao clicar ou selecionar um tema na vitrine, o sistema DEVE repintar a página imediatamente em memória definindo `data-theme` no elemento raiz, anunciando a mudança em região acessível `aria-live="polite"`.
- **FR-011**: A seleção de tema da vitrine DEVE ser efêmera para a visita anônima, restaurando o tema original ao desmontar o componente na navegação para outra rota.
- **FR-012**: O sistema DEVE apresentar uma seção de soberania de dados (`#principios`) declarando ausência de anúncios, ausência de rastreadores, garantia de que notas não treinam IA externa, exportação livre e natureza de software livre.
- **FR-013**: O sistema DEVE apresentar a linhagem histórica do método de estudo substituindo depoimentos fictícios, abrangendo os cadernos de lugares-comuns do século XVI, o método de índice de Locke (1706) e o fichamento digital em camadas contemporâneo.
- **FR-014**: O sistema DEVE incluir no cabeçalho do documento metatags completas de SEO, Open Graph com imagem e texto alternativo, Twitter Card e dados estruturados Schema.org em JSON-LD (`SoftwareApplication` e `WebApplication` com `applicationCategory: "EducationalApplication"`).
- **FR-015**: O sistema DEVE garantir que o conteúdo vital da página inicial esteja presente no HTML inicial indexável por mecanismos de busca e leitores automatizados.
- **FR-016**: Toda a interface da página inicial DEVE ser construída com estrita conformidade constitucional de Zero Emojis, utilizando exclusivamente ícones semânticos da biblioteca oficial de ícones.

---

### Key Entities

- **Manifesto Editorial**: Conjunto de declarações filosóficas e tipográficas sobre a prática da leitura atenta, estruturadas em sobrelinha, título de impacto, subtítulo reflexivo e ficha analítica de 4 perguntas.
- **Simulador das 4 Dimensões**: Entidade de demonstração cognitiva in-place, composta por uma obra literária clássica em domínio público (autor, obra, ano, prólogo, texto e marcas) associada a quatro painéis metodológicos de análise (Resumo, Explicação, Conceitos, Referências).
- **Mostruário dos 10 Temas**: Coleção das dez paletas canônicas do ecossistema visual do Leitorum, parametrizadas com amostras das quatro cores fundamentais e chave estável de seleção.
- **Declaração de Soberania & Tradição**: Coleção de quatro princípios inegociáveis de preservação de dados e três marcos históricos de linhagem da prática de fichamento intelectual.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O visitante consegue experimentar todas as 4 dimensões do método no simulador em menos de 10 segundos, com zero requisições de rede adicionais.
- **SC-002**: A alternância entre os temas oficiais na vitrine pública reflete a nova paleta na interface em menos de 100 milissegundos.
- **SC-003**: 100% dos textos de leitura contínua da landing page atingem taxa de contraste mínima de 7:1 (WCAG AAA) sobre a cor de fundo nos temas suportados.
- **SC-004**: A página inicial atinge pontuação de 95 ou superior no Google Lighthouse nas quatro categorias fundamentais: Performance, Acessibilidade, Melhores Práticas e SEO.
- **SC-005**: 100% dos controles interativos (abas, paletas de tema, botões de ação e links) são totalmente operáveis por teclado com foco visível e alvos de toque mínimos de 44x44 pixels.

---

## Assumptions

- O trecho literário oficial de demonstração é o prólogo "Ao leitor" de *Memórias Póstumas de Brás Cubas* (Machado de Assis, 1881), em domínio público no Brasil e internacionalmente.
- O simulador opera exclusivamente com dados estáticos embutidos no cliente, eliminando qualquer latência ou dependência de banco de dados ativo.
- A troca de temas na vitrine atua na sessão em memória do navegador sem sobregravar as configurações definitivas do usuário, garantindo uma demonstração não intrusiva.
- A preservação da indexação orgânica apoia-se em conteúdo textual semântico disponível no documento HTML inicial, assegurando indexabilidade mesmo por rastreadores que não executam JavaScript complexo.
- A modularização dos componentes segue a divisão por responsabilidade em `components/landing/`, facilitando a manutenção e a reutilização de elementos como o `ThemePreviewGrid`.
