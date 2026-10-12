# Feature Specification: Correções Visuais, de Cor e de Disposição

**Feature Branch**: `075-correcoes-visuais-disposicao`  
**Created**: 2026-10-11  
**Status**: Draft  
**Input**: Resolução de 14 pendências de layout, alinhamento, contraste e herança de tema no frontend, eliminando a causa raiz das variáveis CSS indefinidas e refinando a experiência visual de leitura.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Toda tela legível e consistente em qualquer um dos dez temas (Priority: P1)

Como leitor do Caderno de Leitura, eu desejo alternar livremente entre qualquer um dos dez temas visuais (incluindo temas escuros como Noite Suave, Grafite, Fiorde e Voltagem, ou temas quentes como Pergaminho e Solário) e ter a garantia de que todas as telas, cartões, formulários, modais e controles acompanham o tema selecionado, sem caixas brancas fixas, sem textos escuros sobre fundos escuros e com contraste visual nítido.

**Why this priority**: É a causa raiz sistêmica de 10 dos 14 problemas relatados. Atualmente, 104 variáveis CSS usadas em componentes não estão declaradas no sistema de temas e recorrem a fallbacks fixos (como `#ffffff` e `#6b7280`), quebrando a imersão do leitor e a acessibilidade visual em múltiplos temas.

**Independent Test**: Alternar para o tema escuro Grafite ou Fiorde e navegar pelas telas de Destaques, Revisão, Biblioteca, Lixeira e Apoie. Verificar visualmente e via testes automatizados que nenhum elemento apresenta fundo branco fixo e que os contrastes atendem às diretrizes de acessibilidade.

**Acceptance Scenarios**:

1. **Dado** um tema escuro ativo (ex.: Noite Suave, Grafite, Fiorde ou Voltagem), **quando** o leitor navega pelas telas de Destaques, Hub de Revisão, Lixeira, Livros ou Apoie, **então** nenhum contêiner, painel, cabeçalho ou cartão apresenta fundo branco fixo ou borda clara destoante.
2. **Dado** qualquer um dos dez temas ativos, **quando** o leitor visualiza textos de interface, rótulos e ícones, **então** a taxa de contraste é igual ou superior a 4,5:1 para textos informativos e 3:1 para ícones de ação e bordas interativas.
3. **Dado** o tema Pergaminho, **quando** o leitor acessa a tela de Destaques ou Apoie, **então** as superfícies dos cartões utilizam as variáveis tonais do papel (`--color-surface`, `--color-page`), sem conflito visual com o fundo.
4. **Dado** a suíte de testes do frontend, **quando** executada a validação automática de estilos, **então** zero variáveis CSS utilizadas nos componentes `.vue` estão indefinidas no sistema de tokens.

---

### User Story 2 - Navegação e organização de livros e capas (Priority: P2)

Como leitor organizando meu acervo, eu desejo que a grade de livros permaneça alinhada e harmônica mesmo quando há poucos livros cadastrados, que as miniaturas na visualização em lista não exibam textos cortados desnecessários, que os selos de categoria sejam discretos e transparentes, e que os botões de ação e busca estejam visualmente balanceados.

**Why this priority**: A tela de Livros (`/livros`) é a porta de entrada principal da biblioteca do leitor. Problemas de alinhamento em grades pequenas, textos truncados em capas miniaturas e botões com duplicações visuais prejudicam a clareza e a ergonomia de uso.

**Independent Test**: Acessar `/livros` com apenas 1 ou 2 livros cadastrados nos modos de exibição em Grade e em Lista, verificar a disposição, alternar temas e inspecionar os botões da barra de ferramentas.

**Acceptance Scenarios**:

1. **Dado** a biblioteca com poucos livros cadastrados (ex.: 1 a 3 itens), **quando** visualizada no modo grade em telas largas, **então** os livros ficam alinhados à esquerda da grade, sem espaçamentos inflados que desloquem o primeiro livro do alinhamento natural da página.
2. **Dado** a visualização de livros no modo lista, **quando** um livro não possui imagem de capa cadastrada, **então** a miniatura lateral (`size="sm"`) exibe apenas a cor sólida configurada e a textura/lombada estilizada, sem tentar renderizar o título em tipografia ilegível ou cortada.
3. **Dado** qualquer livro com categoria atribuída, **quando** exibido seu selo de categoria (`CategoryBadge`), **então** o fundo do selo é transparente e a cor da borda e do texto acompanha harmoniosamente as variáveis do tema ativo.
4. **Dado** a barra de ferramentas da biblioteca (`LibraryToolbar`), **quando** visualizado o botão de adicionar livro, **então** há apenas um único sinal de adição (o ícone semântico) acompanhado do texto limpo "Adicionar Livro", sem o caractere literal `+` antes do rótulo.
5. **Dado** a barra de ferramentas da biblioteca, **quando** visualizado o seletor de visualização Grade/Lista, **então** o contêiner do seletor possui fundo neutro/transparente com separação nítida e espaçamento visível entre os dois botões, e o campo de busca utiliza cores integradas ao tema corrente.

---

### User Story 3 - Gestão e visualização de estudos do livro (Priority: P2)

Como leitor acompanhando capítulos e notas de um livro específico (`/livros/:id`), eu desejo alternar entre as visões em Grade, Lista, Árvore e Mapa com indicadores de status legíveis, cabeçalhos de tabela perfeitamente alinhados com suas colunas, botões com contraste e dimensões táteis adequadas e controles móveis responsivos.

**Why this priority**: A página de detalhes do livro concentra o trabalho reflexivo e o estudo aprofundado dos capítulos. Erros de contraste em ícones da árvore, desalinhamentos na tabela e menus de status com caixas brancas afetam diretamente a leitura analítica.

**Independent Test**: Acessar `/livros/:id` com múltiplos estudos em diferentes estados (Rascunho, Em Estudo, Revisado, Concluído), testar a ordenação e seleção na lista, inspecionar a árvore e o mapa em tema escuro.

**Acceptance Scenarios**:

1. **Dado** o menu e o selo de estado do estudo (`StudyStatusBadge`), **quando** exibidas as opções (Rascunho, Em Estudo, Revisado, Concluído), **então** os selos apresentam fundo transparente com borda e texto respeitando o tema, além de um indicador visual semântico que não dependa exclusivamente de cor para distinguir o estado.
2. **Dado** a visão em lista de estudos (`StudyListView`), **quando** renderizada a tabela, **então** os títulos dos cabeçalhos ficam perfeitamente alinhados com os conteúdos de cada coluna correspondente, compartilham a mesma hierarquia tipográfica e o indicador de ordenação ativa utiliza um componente de ícone padronizado sem caracteres ASCII soltos.
3. **Dado** um ou mais estudos selecionados na visão em lista, **quando** o botão de desmarcar seleção é exibido, **então** sua área tátil de clique possui dimensão mínima de 44 por 44 pixels.
4. **Dado** a visão em árvore de estudos (`StudyTreeNodeItem`), **quando** visualizados os botões e ícones de ação em repouso, sob cursor (*hover*) ou sob foco (*focus*), **então** os ícones mantêm contraste mínimo de 3:1 sobre o fundo imediato em todos os dez temas, sem utilizar variáveis de fundo como cor de texto.
5. **Dado** a visão em mapa (`StudyMapView`), **quando** examinados os botões de controle de zoom e centralização, **então** os ícones possuem contraste adequado com o mapa em todos os temas.
6. **Dado** a visão em mapa em telas desktop, **quando** um estudo está selecionado, **então** a barra móvel de resumo do estudo permanece restrita a dispositivos móveis e não obstrui a interface em telas amplas.

---

### User Story 4 - Cabeçalho, rodapé e estados vazios da aplicação (Priority: P3)

Como leitor autenticado na aplicação, eu desejo que o cabeçalho superior e o rodapé das páginas internas apresentem espaçamento equilibrado, sem elementos soltos ou redundantes, e que telas ou abas sem conteúdo exibam estados vazios visualmente integrados e centralizados.

**Why this priority**: Garante polimento estético contínuo, eliminação de caixas brancas residuais em temas escuros e consistência visual entre todas as telas internas do sistema.

**Independent Test**: Navegar pelo cabeçalho superior inspecionando o gatilho do usuário, verificar o rodapé em telas desktop e mobile, e acessar telas com coleções vazias (ex.: abas de amigos, lixeira vazia).

**Acceptance Scenarios**:

1. **Dado** o rodapé interno da aplicação (`AppFooter`), **quando** exibido em resolução desktop, **então** seus blocos distribuem-se nas extremidades laterais com alinhamento equilibrado; em telas móveis, quebra de linha suave sem pontuações ou traços órfãos isolados.
2. **Dado** o gatilho do menu de perfil do usuário no cabeçalho (`UserDropdown`), **quando** exibido em qualquer tela autenticada, **então** apresenta unicamente o avatar com foto ou iniciais, com área de toque mínima de 44 por 44 pixels, rótulo acessível `aria-label`, sem duplicação de nome fora do avatar, sem setas decorativas soltas e sem fundo cinza fixo em temas escuros.
3. **Dado** um estado vazio em qualquer tela (componente `EmptyState`), **quando** renderizado em um tema escuro, **então** a caixa de destaque do ícone utiliza fundo sutil do tema (`--color-surface-soft`) ou fundo transparente, sem criar um quadrado branco opaco ao redor do ícone.
4. **Dado** a aba de usuários bloqueados na tela de Amigos (`FriendsView`), **quando** não houver usuários bloqueados, **então** o estado vazio é renderizado centralizado no contêiner da aba, utilizando a mesma estrutura padronizada das demais abas.

---

### User Story 5 - Páginas públicas, links externos e persistência do tema da visita (Priority: P3)

Como visitante ou leitor explorando as páginas públicas do Caderno de Leitura (`/`, `/sobre`, `/apoie`), eu desejo encontrar links externos corretos para o código-fonte do projeto, explicações transparentes sobre as formas de apoio ao software e a persistência do tema visual escolhido durante toda a minha sessão de navegação anônima.

**Why this priority**: Reforça a transparência do projeto comunitário de código aberto e garante conforto visual contínuo para novos visitantes antes do login.

**Independent Test**: Acessar a página inicial pública, selecionar um tema na vitrine de temas, navegar para `/sobre` e `/apoie`, verificar que o tema permanece ativo na sessão do navegador, clicar no link de código aberto e conferir o destino.

**Acceptance Scenarios**:

1. **Dado** o rodapé público (`PublicFooter`) ou links de código aberto em qualquer tela, **quando** o visitante clica em "Código Aberto", **então** o link aponta precisamente para o repositório público oficial `https://github.com/AntonioBudal/CDL`.
2. **Dado** a página `/apoie` (`SupportView`), **quando** o visitante ou usuário a lê, **então** o texto esclarece de forma transparente que a fase atual é de desenvolvimento e o apoio buscado consiste em uso do aplicativo, reporte de falhas e contribuições técnicas de código aberto, sem exibir caixas com dados bancários vazios ou botões inoperantes de doação.
3. **Dado** um visitante que selecionou um tema visual na vitrine da página inicial pública, **quando** ele navega entre as páginas públicas (`/`, `/sobre`, `/apoie`), **então** o tema escolhido é mantido na sessão de navegação, sem retroceder ao tema padrão a cada mudança de rota.
4. **Dado** a persistência do tema da visita, **quando** um usuário autenticado acessa o sistema, **então** sua preferência individual salva de tema tem precedência e não é corrompida pela visita anônima prévia.

---

### Edge Cases

- **Troca rápida de temas em telas complexas**: Ao alternar sucessivamente entre temas claros, quentes e escuros com modais abertos, nenhum elemento deve reter estilos *inline* ou classes herdadas que impeçam a atualização imediata das variáveis CSS.
- **Redimensionamento de janela entre desktop e mobile**: Transições de tela entre 320px e 1920px não devem quebrar alinhamentos de grade nem empilhar botões de ação sobrepostos.
- **Livros com títulos muito longos sem imagem de capa**: A miniatura pequena da capa não deve estourar o contêiner nem gerar rolagem horizontal na tabela de livros.
- **Visitante em modo de navegação anônima restrita**: Se o armazenamento local (*localStorage*) estiver desativado pelo navegador, o seletor de tema público deve degradar graciosamente em memória de sessão sem lançar exceções não tratadas.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema de estilos do frontend DEVE fornecer uma camada de compatibilidade em `tokens.css` declarando como apelidos para as variáveis canônicas oficiais todas as 104 variáveis CSS legadas utilizadas em componentes `.vue` (incluindo `--color-text-muted`, `--color-primary`, `--color-border-subtle`, `--color-text-secondary`, `--color-danger`, `--color-text-primary`, `--color-bg`, entre outras).
- **FR-002**: A suíte de testes automatizados (`npm test`) DEVE incluir uma validação automatizada que verifique todos os arquivos `.vue` em `frontend/src/` e garanta que nenhuma variável CSS de cor utilizada esteja ausente do conjunto de tokens declarados em `tokens.css` e `palettes.css`.
- **FR-003**: O sistema de tokens DEVE mapear variáveis de raio legadas (`--radius-sm`, `--radius-md`, `--radius-lg`) e de elevação/sombra para as variáveis canônicas (`--radius-control`, `--radius-card`, `--radius-panel`, `--shadow-sm`, `--shadow-md`).
- **FR-004**: Os estilos dos componentes NÃO DEVEM utilizar variáveis de fundo como cor de texto (como a ocorrência de `color: var(--color-inverse-bg)` em botões), substituindo-as por variáveis semânticas de texto (`--color-text`, `--color-on-inverse` ou `--color-muted`).
- **FR-005**: Todos os dez temas visuais suportados DEVEM garantir razão de contraste mínima de 4,5:1 para textos informativos de interface e 3:1 para ícones e bordas interativas.
- **FR-010**: O componente `BooksView.vue` DEVE alinhar os cartões de livro à esquerda no modo grade quando a quantidade de itens na linha for menor que a capacidade máxima da grade.
- **FR-011**: O componente `BookCover.vue` DEVE ocultar o texto de título na miniatura pequena (`size="sm"`) quando o livro não possuir imagem de capa, exibindo unicamente a cor base configurada e detalhes estilizados de lombada.
- **FR-012**: O componente `CategoryBadge.vue` DEVE utilizar fundo transparente e aplicar borda e cor de texto orientadas pelas variáveis semânticas do tema ativo.
- **FR-013**: O componente `LibraryToolbar.vue` DEVE exibir no botão de adicionar livro um único ícone de adição sem prefixação de caractere `+` no texto, apresentar o contêiner do seletor Grade/Lista com fundo transparente e espaçamento visível entre opções, e integrar o campo de pesquisa às cores do tema.
- **FR-020**: O componente `StudyStatusBadge.vue` DEVE exibir as opções de estado do estudo com fundo transparente, borda e texto do tema e um indicador visual acessível não dependente exclusivamente de cor.
- **FR-021**: O componente `StudyListView.vue` DEVE alinhar vertical e horizontalmente os cabeçalhos de coluna com as respectivas células de dados, padronizar a tipografia dos cabeçalhos, indicar ordenação ativa via componente `<Icon>` e prover área tátil mínima de 44x44px no botão de desmarcar seleção.
- **FR-022**: O componente `StudyTreeNodeItem.vue` DEVE manter visíveis os ícones de ação em repouso, sob cursor e sob foco em todos os dez temas, eliminando cores de texto derivadas de variáveis de fundo.
- **FR-023**: O componente `StudyMapView.vue` DEVE assegurar contraste adequado nos botões de controle e ocultar a barra móvel de resumo do estudo em resoluções de desktop.
- **FR-030**: O componente `AppFooter.vue` DEVE distribuir seus elementos de extremidade a extremidade em desktop (`justify-content: space-between`) e quebrar suavemente em telas móveis sem pontuações isoladas.
- **FR-031**: O componente `UserDropdown.vue` DEVE exibir no botão-gatilho unicamente o avatar do usuário com dimensão mínima de 44x44px e rótulo acessível, removendo textos externos duplicados, setas isoladas e fundos cinzas fixos.
- **FR-032**: O componente `EmptyState.vue` DEVE utilizar fundo sutil (`--color-surface-soft`) ou transparente na moldura do ícone, evitando fundos brancos opacos em temas escuros.
- **FR-033**: A aba de bloqueados em `FriendsView.vue` DEVE centralizar visualmente seu estado vazio utilizando o componente padronizado `EmptyState.vue`.
- **FR-034**: Os links para o código-fonte em rodapés públicos e na documentação DEVEM apontar para o repositório oficial `https://github.com/AntonioBudal/CDL`.
- **FR-035**: A página `/apoie` (`SupportView.vue`) DEVE apresentar texto claro e sóbrio sobre apoio comunitário e técnico, sem formulários ou botões inoperantes de doação financeira.
- **FR-036**: O composable de tema da visita (`useVisitorTheme.ts` ou equivalente) DEVE preservar o tema selecionado durante a sessão de navegação pública nas rotas `/`, `/sobre` e `/apoie`.
- **FR-040**: A implementação desta feature DEVE se restringir estritamente ao código de frontend em `frontend/src/`, sem nenhuma alteração de schema, migração de banco de dados ou alteração de rotas da API backend.
- **FR-041**: O código e os textos DEVEM cumprir rigorosamente a proibição constitucional de emojis em 100% dos arquivos.
- **FR-042**: O código DEVE manter a proteção absoluta da privacidade do acervo do usuário, sem expor dados privados em testes ou interfaces públicas.

---

### Key Entities *(include if feature involves data)*

- **Tema da Visita (VisitorTheme)**: Preferência volátil de tema ativo selecionado por visitante não autenticado, mantida durante a navegação entre rotas públicas e descartada ou substituída quando o usuário se autentica.
- **Tokens de Compatibilidade (CompatibilityTokens)**: Mapeamento de variáveis CSS legadas de design tokens para as variáveis semânticas canônicas de cores, raios e sombras da aplicação.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% dos arquivos de componentes `.vue` passam no teste automatizado de ausência de variáveis CSS de cor indefinidas (`0` ocorrências de variáveis não mapeadas).
- **SC-002**: 10 dos 10 temas visuais do Caderno de Leitura atingem conformidade com razão de contraste $\ge 4,5:1$ para textos de interface e $\ge 3:1$ para ícones de controle em todas as telas auditadas.
- **SC-003**: 0 caixas ou contêineres com fundo branco fixo são exibidos em temas escuros (Noite Suave, Grafite, Fiorde e Voltagem) nas telas de Destaques, Revisão, Biblioteca, Lixeira e Apoie.
- **SC-004**: 100% dos botões de ação e controles táteis especificados (gatilho de perfil, desmarcar na lista de estudos, seletores de modo) possuem alvo de interação tátil $\ge 44 \times 44$ pixels.
- **SC-005**: A suíte de testes completa do frontend (`npm test`) e a compilação de produção (`npm run build`) concluem com 0 erros e 0 alertas críticos.
- **SC-006**: A persistência do tema público opera fluidamente entre `/`, `/sobre` e `/apoie` sem piscar (*flash of unstyled theme*) e sem alterar o tema persistido de contas de usuários locais.

---

## Assumptions

- O repositório oficial de código aberto do projeto é mantido em `https://github.com/AntonioBudal/CDL`.
- As 127 variáveis canônicas já declaradas em `tokens.css` e `palettes.css` são a fonte oficial de verdade estilística do projeto, devendo as variáveis legadas ser mapeadas para elas.
- O apoio ao projeto na versão atual é comunitário e baseado em código aberto, reporte de problemas e feedback de uso, sem necessidade de integração com intermediários de pagamento.
- Os navegadores suportados mantêm suporte nativo a CSS Custom Properties e `localStorage` / `sessionStorage`.
- Nenhuma funcionalidade de backend, modelo de banco de dados SQLite ou contrato de API REST necessita de modificação para atender a estas correções visuais.
