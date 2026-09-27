# Feature Specification: F09.5.2 — Contraste Dinâmico, Estudos Compartilhados e Responsividade Mobile

**Feature Branch**: `038-contraste-compartilhados-mobile`

**Created**: 2026-09-26

**Status**: Draft

**Input**: User description: "F09.5.2 — Contraste Dinâmico, Estudos Compartilhados e Responsividade Mobile: Implementar cálculo automático e consistente das cores de texto a partir da cor de fundo (luminância relativa WCAG, estados default, hover, focus, active, selected, disabled); corrigir e reformular a tela de Estudos Compartilhados investigando a causa estrutural de SVGs gigantes; e realizar auditoria completa da experiência em dispositivos móveis, principalmente da navegação por abas e cabeçalhos em telas pequenas."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Contraste Dinâmico Centralizado e Acessível para Estados de Interface (Priority: P1)

Como leitor utilizando qualquer um dos temas do sistema (claros, escuros, solarizados ou sépias), quero que todas as cores de texto, ícones (`currentColor`) e elementos de primeiro plano tenham contraste legível calculado automaticamente a partir da cor do seu fundo em qualquer estado de interação (`default`, `hover`, `focus`, `active`, `selected`, `disabled`), para que eu nunca me depare com textos invisíveis, cinzas apagados sobre fundos escuros ou contrastes insuficientes ao passar o mouse ou selecionar itens.

**Why this priority**: É a fundação crítica de acessibilidade e legibilidade visual de toda a aplicação. A presença de cores fixas hard-coded (`#fff`, `#18181b`, `text-white`, `text-black`) quebra a interface assim que o fundo muda de estado ou de tema.

**Independent Test**: Alternar entre temas claros (ex.: "Papel Fosco", "Solarized") e escuros (ex.: "Noite Suave", "Grafite", "Cyber"); inspecionar elementos com variação de fundo — especialmente abas de navegação, botões primários/secundários, badges de categorias e cards — verificando que em repouso e durante `hover`, `active` e `selected` o contraste da fonte atinge a taxa mínima de 4.5:1 para texto normal e 3.0:1 para elementos de interface e textos grandes conforme a norma WCAG 2.1.

**Acceptance Scenarios**:

1. **Given** um elemento de interface com fundo dinâmico ou variável, **When** o algoritmo de contraste centralizado avalia a cor efetiva de fundo, **Then** ele calcula a luminância relativa $L = 0.2126R + 0.7152G + 0.0722B$ (com linearização sRGB) e seleciona a cor de primeiro plano que maximiza a razão de contraste $((L_1 + 0.05) / (L_2 + 0.05))$, superando o limiar de 4.5:1.
2. **Given** uma aba de navegação (em `SettingsView`, `BooksView`, `StudyTabs`, `FriendsView` ou `DashboardView`), **When** o usuário interage passando o mouse (`hover`) ou selecionando a aba (`selected`), alterando a cor de fundo da aba, **Then** a cor do texto e dos ícones associados é imediatamente recalculada para o novo fundo, impedindo texto escuro em fundo escuro ou texto claro em fundo claro.
3. **Given** ícones embutidos em botões, abas ou badges que utilizam `stroke="currentColor"` ou `fill="currentColor"`, **When** a cor de texto do componente é atualizada pelo cálculo de contraste, **Then** o ícone acompanha com fidelidade milimétrica a mesma cor de contraste sem regras discrepantes.
4. **Given** os campos de seleção (`<select>`) e botões secundários descritos em `style.css`, **When** renderizados em qualquer tema, **Then** as regras de texto com `!important` hard-coded são substituídas pelo mecanismo semântico de contraste dinâmico sem regressão visual.

---

### User Story 2 - Diagnóstico Estrutural e Reformulação Integral de Estudos Compartilhados (Priority: P2)

Como leitor consultando estudos compartilhados por outros usuários ou amigos, quero que a tela de Estudos Compartilhados (`SharedStudiesList.vue`) tenha uma diagramação equilibrada, componentes padronizados, ícones proporcionais e estados informativos consistentes, para que eu possa localizar, filtrar e abrir estudos com clareza em qualquer tamanho de monitor ou dispositivo móvel.

**Why this priority**: A tela de Estudos Compartilhados sofre de desagregação estética e dimensional severa devido ao uso indevido de classes utilitárias não suportadas e ausência de contenção nos elementos gráficos, transmitindo impressão de sistema inacabado.

**Independent Test**: Acessar a tela de Estudos Compartilhados (`/books` na aba "Compartilhados Comigo") em desktop e em celular; verificar que o ícone da barra de pesquisa e todos os demais ícones mantêm dimensões exatas de 16px a 20px, que os cards respeitam as variáveis semânticas do tema atual, que a busca e filtros por `@autor` respondem fluidamente e que o estado vazio e de carregamento são harmoniosos.

**Acceptance Scenarios**:

1. **Given** a barra de busca e filtro de autor em `SharedStudiesList.vue`, **When** inspecionada visualmente e no código, **Then** os ícones de busca e arroba não utilizam classes utilitárias externas inexistentes (como `w-4 h-4 text-zinc-400`), sendo substituídos pelo componente padronizado do sistema `<Icon name="search" :size="16" />` ou por SVG com atributos explícitos `width="16" height="16"`, impedindo qualquer expansão desproporcional.
2. **Given** os cartões de estudo da lista compartilhada, **When** exibidos em qualquer um dos 10 temas ativos, **Then** utilizam exclusivamente as variáveis semânticas do sistema (`--color-surface`, `--color-border`, `--color-text`, `--color-muted`, `--color-accent`) em vez de classes arbitrárias de frameworks inexistentes (`dark:bg-zinc-900`, `border-zinc-200`, etc.).
3. **Given** a tela de estudos compartilhados sem resultados (busca sem correspondência ou ausência de compartilhamentos), **When** o estado vazio é renderizado, **Then** o container do estado vazio exibe ilustração/ícone contido, título claro, mensagem explicativa acolhedora e botão de redefinição de filtros quando houver consulta ativa.
4. **Given** o carregamento assíncrono dos dados da API de compartilhamento, **When** a requisição está em trânsito, **Then** o estado de carregamento exibe esqueletos estruturados com animação suave (*shimmer*) respeitando o formato dos cards reais.

---

### User Story 3 - Auditoria de Arquitetura de Navegação e Responsividade Mobile (Priority: P3)

Como leitor utilizando o Leitorum em smartphone ou tablet, quero que a navegação principal da aplicação, os sistemas de abas segmentadas e os cabeçalhos de ações se ajustem ergonomicamente ao espaço reduzido da tela, para que eu tenha alvos de toque confortáveis (mínimo de 44x44px), acesso a todas as seções sem cortes e visibilidade limpa do conteúdo de leitura.

**Why this priority**: Com a expansão de seções da aplicação (Amigos, Administração, Lixeira, Ajustes segmentados em 5 abas), a grade rígida mobile de 3 colunas em `mobile-navigation.css` e as abas horizontais sem contenção transbordam ou comprimem a interface em telas pequenas.

**Independent Test**: Reduzir a viewport para larguras comuns de smartphones (360px, 390px, 412px); verificar que a barra de navegação principal exibe todas as opções essenciais sem estourar altura nem sobrepor conteúdo, que abas secundárias permitem navegação tátil fluida e que os cabeçalhos das telas não apresentam overflow horizontal.

**Acceptance Scenarios**:

1. **Given** a barra de navegação principal no rodapé mobile (`.main-nav` sob `mobile-navigation.css`), **When** visualizada em smartphones com até 6 rotas ativas (`Livros/Dashboard`, `Importar`, `Amigos`, `Ajustes`, `Lixeira` e opcionalmente `Administração`), **Then** a barra organiza os itens de forma ergonômica, garantindo alvos de toque mínimos de 44x44px e sem empilhar linhas de forma desordenada fora da área visível.
2. **Given** telas com navegação por abas segmentadas (`SettingsView` com 5 abas, `FriendsView` com 4 abas, `StudyTabs` com 6 abas, `BooksView` com 2 abas), **When** visualizadas em viewports móveis, **Then** as abas mantêm rolagem horizontal suave com contenção (*overflow-x: auto*), suporte a toque com *momentum*, indicador visual de scroll e foco WAI-ARIA intacto.
3. **Given** o cabeçalho superior (`app-header`) em telas estreitas (< 380px), **When** o título da aplicação, badge de sincronização, botão de busca e sino de notificações são renderizados, **Then** eles se organizam de maneira compacta sem quebrar a barra em alturas excessivas e sem causar barra de rolagem horizontal na página.
4. **Given** formulários e painéis de filtros em telas menores que 720px, **When** exibidos, **Then** campos de busca, seletores de categoria e botões secundários se adaptam para empilhamento vertical com largura de 100% e espaçamento ergonômico.

---

## Edge Cases

- **Cores sem formato hexadecimal puro**: Como o algoritmo trata cores de fundo expressas em `rgb()`, `rgba()`, `hsl()`, nomes CSS nomeados ou referências a variáveis CSS como `var(--color-surface)`? O utilitário deve normalizar strings de cores e resolver referências computadas via DOM (`getComputedStyle`) quando executado no navegador.
- **Fundo semi-transparente ou com opacidade**: O que ocorre quando um elemento possui fundo com canal alfa (ex.: `rgba(0, 0, 0, 0.05)`)? O algoritmo deve compor a cor sobre a cor de fundo do elemento ancestral mais próximo para determinar a luminância efetiva percebida pelo olho humano.
- **Preferência de contraste elevado do sistema operacional**: Quando a mídia `prefers-contrast: more` está ativada, como o sistema se comporta? O limiar de contraste dinâmico é elevado para a norma WCAG AAA (mínimo de 7.0:1 para texto normal e 4.5:1 para elementos de interface).
- **Abas ativas com nomes longos no mobile**: Como o sistema evita que abas como "Conta & Dispositivos" ou "Solicitações Recebidas" ocupem a tela inteira em celulares? As abas devem utilizar `white-space: nowrap`, espaçamento proporcional e rolagem horizontal elástica com indicador de corte sutil (gradiente de desvanecimento nas bordas).
- **SVGs sem viewBox**: O que ocorre se um ícone SVG legado não possuir nem `viewBox` nem `width`/`height`? O componente de ícone do sistema deve impor dimensões padrão via propriedades CSS e atributos XML padrão para prevenir explosão visual.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE disponibilizar um utilitário centralizado de cálculo de contraste (`getAccessibleTextColor(backgroundColor, options)`) que receba uma cor de fundo, calcule sua luminância relativa conforme as fórmulas canônicas da WCAG 2.1 e retorne a cor de primeiro plano de maior legibilidade.
- **FR-002**: O algoritmo de contraste centralizado DEVE aplicar um limiar mínimo de 4.5:1 para textos regulares e 3.0:1 para textos em destaque/componentes de UI, suportando customização de opções por contexto.
- **FR-003**: O cálculo de contraste DEVE obrigatoriamente suportar a avaliação dos estados interativos do componente (`default`, `hover`, `focus`, `active`, `selected`, `disabled`), garantindo que a cor de texto seja recalculada sempre que a cor de fundo for alterada por um desses estados.
- **FR-004**: O sistema DEVE aplicar a cor de primeiro plano calculada tanto ao texto quanto aos elementos de traço e preenchimento de ícones associados via `currentColor` ou variáveis semânticas dedicadas.
- **FR-005**: O sistema NÃO DEVE utilizar funções dispersas ou duplicadas de contraste por tipo de componente (como `getTabTextColor`, `getButtonTextColor`, etc.), mantendo a lógica de contraste estritamente unificada e reutilizável.
- **FR-006**: O sistema DEVE eliminar regras com valores de cor hard-coded (`white`, `black`, `#fff`, `#18181b`, `text-white`, etc.) em classes ou folhas de estilo quando a cor depender do plano de fundo dinâmico.
- **FR-007**: A especificação DEVE identificar formalmente a causa raiz dos SVGs desproporcionais em `SharedStudiesList.vue`: o emprego de classes utilitárias do Tailwind (`w-4 h-4`, `text-zinc-400`) em um ambiente que não possui o Tailwind CSS instalado nem compilado, resultando em tags `<svg>` sem atributos dimensionais `width` e `height` que expandem para o tamanho total do container.
- **FR-008**: A tela de Estudos Compartilhados DEVE ser integralmente refatorada para utilizar os componentes e tokens oficiais do Leitorum: substituição de SVGs inline pelo componente `<Icon />`, substituição de classes `zinc` por variáveis semânticas (`--color-surface`, `--color-text`, `--color-border`), e estruturação de cards harmonizados com a identidade visual da plataforma.
- **FR-009**: A tela de Estudos Compartilhados DEVE implementar estados robustos e acessíveis para: carregamento (esqueleto animado/skeleton com tokens de shimmer), erro (alerta com botão de nova tentativa) e ausência de dados (empty state proporcional e contextualizado para busca vazia e acervo vazio).
- **FR-010**: A arquitetura de navegação móvel DEVE reformular a regra rígida de `grid-template-columns: repeat(3, minmax(0, 1fr))` em `mobile-navigation.css`, implementando uma barra inferior prioritária que exibe os destinos primários e um botão de ação 'Mais' que aciona um painel inferior (*bottom sheet* / gaveta) com as rotas secundárias (`Lixeira`, `Administração`, `Conexão`), garantindo alvos de toque mínimos de 44x44px e layout contido em uma única linha horizontal.
- **FR-011**: Todos os componentes de abas segmentadas (`SettingsView`, `BooksView`, `StudyTabs`, `FriendsView`, `DashboardView`) DEVEM garantir conformidade ergonômica em telas pequenas: rolagem horizontal contida, alvos de toque mínimos de 44x44px, preservação da semântica WAI-ARIA (`role="tablist"`, `role="tab"`, `aria-selected`) e indicação clara de foco e seleção.
- **FR-012**: O cabeçalho da aplicação (`app-header`) DEVE implementar leiaute responsivo adaptado para viewports estreitas (< 380px), preservando a visibilidade da marca Leitorum, busca, notificações e estado de sincronização sem quebra destrutiva de linhas.
- **FR-013**: O mecanismo de aplicação de contraste dinâmico no frontend DEVE operar via composable Vue que calcula a luminância e injeta variáveis CSS customizadas locais no elemento (ex.: `--dynamic-fg`, `--dynamic-hover-fg`, `--dynamic-border`), permitindo que transições de estado (`hover`, `focus`, `active`) sejam executadas diretamente pelo motor de estilos do navegador com máxima performance.
- **FR-014**: O overflow de abas segmentadas em dispositivos móveis DEVE ser indicado visualmente por meio de gradientes suaves de máscara (*fade mask*) nas extremidades laterais do container com rolagem horizontal, garantindo pista visual clara de continuidade sem poluição visual ou dependência de scrollbars intrusivas.

---

### Clarifications Resolved

- **Clarification 1 (Barra de Navegação Mobile)**: Adotada a **Opção A (Barra prioritária com botão 'Mais')**. A barra inferior do celular exibe os destinos primários com alvos de toque ergonômicos e um 5º botão "Mais" que expande uma gaveta inferior (*bottom sheet*) contendo as rotas de suporte e administração (`Lixeira`, `Administração`, `Conexão`).
- **Clarification 2 (Aplicação do Contraste Dinâmico)**: Adotada a **Opção A (Variáveis CSS Injetadas no DOM + Composable Vue)**. Um composable centralizado avalia o background efetivo e projeta variáveis CSS locais no elemento alvo (`--dynamic-fg`, `--dynamic-hover-fg`, etc.), desfrutando da aceleração e pseudoclasses do CSS nativo.
- **Clarification 3 (Indicador de Overflow em Abas Móveis)**: Adotada a **Opção A (Gradientes sutis de máscara/fade)**. Fitas de abas com transbordamento horizontal utilizam máscara gradiente suave nas laterais, indicando de forma elegante que há itens navegáveis através de rolagem tátil.

---

### Key Entities *(include if feature involves data)*

- **ContrastCalculationOptions**: Entidade de configuração do cálculo de contraste contendo: `targetContrastRatio` (padrão 4.5 ou 3.0), `lightCandidate` (cor clara de fallback, ex.: `#ffffff`), `darkCandidate` (cor escura de fallback, ex.: `#111827`), `strictAA` (booleano), `highContrastMode` (booleano).
- **ElementInteractionState**: Enumeração dos estados visuais avaliados para contraste: `default`, `hover`, `focus`, `active`, `selected`, `disabled`.
- **SharedStudyCardItem**: Entidade visual representativa do estudo compartilhado exibido na lista, compreendendo: `id`, `title`, `book_title`, `chapter_name`, `owner_username`, `owner_display_name`, `owner_avatar_url`, `visibility`, `updated_at`, `can_read`.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% dos textos e ícones com background dinâmico ou variável em abas, botões e badges atingem índice de contraste medido $\ge 4.5:1$ (texto normal) e $\ge 3.0:1$ (texto grande / controles de interface) em todos os 10 temas do sistema e em todos os seus estados interativos (`default`, `hover`, `focus`, `active`, `selected`).
- **SC-002**: Redução a zero (0) de regras CSS hard-coded com `!important` para cor de texto em seletores de tema escuro e claro em `style.css`.
- **SC-003**: 100% dos ícones renderizados na tela de Estudos Compartilhados mantêm proporções fiéis ao padrão do sistema (entre 16px e 20px para ícones de controle, e máximo de 120px para ilustração de estado vazio), sem nenhum elemento gráfico estourando a viewport em nenhuma resolução de tela.
- **SC-004**: A tela de Estudos Compartilhados atinge conformidade total com os tokens de design do Leitorum, eliminando 100% das classes utilitárias externas inexistentes (`zinc`, `dark:`, etc.).
- **SC-005**: A navegação móvel (`mobile-navigation.css` e abas secundárias) é plenamente operável em telas a partir de 320px de largura sem rolagem horizontal indesejada da página inteira e com alvos de toque com dimensão mínima de 44x44px em 100% dos links e botões navegáveis.
- **SC-006**: A suíte de testes de acessibilidade visual e testes unitários do frontend (`npm test`) e checagem de tipos (`vue-tsc -b`) passam com 100% de sucesso e zero erros de tipagem.

---

## Assumptions

- O projeto não utiliza nem pretende instalar o framework Tailwind CSS; todo o sistema visual é fundamentado em CSS nativo modular com variáveis e tokens de design customizados (`tokens.css`, `palettes.css`, `style.css`).
- O componente `<Icon />` baseado em `lucide-vue-next` é a biblioteca padrão e canônica de ícones do Leitorum e deve ser preferido em substituição a SVGs embutidos manualmente com código cru.
- A persistência síncrona do tema e a estrutura dos 10 temas consolidados na versão 0.5 (F09.5) são estáveis e constituem o alicerce onde o contraste dinâmico atuará.
- A aplicação atende primordialmente leitores em computadores de mesa, laptops, tablets e smartphones conectados ao servidor local ou via rede privada.
