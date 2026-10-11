# Feature Specification: Ajustes — Ateliê de Preferências e Leitura Viva

**Feature Branch**: `072-ajustes-atelie-preferencias`

**Created**: 2026-10-11

**Status**: Draft

**Input**: User description: "F0.8.08, adicione a especificação dos ajustes a melhora das previsualizações tipo no windows 11 que tem previews dos temas com boxes mostrando as cores, não apeans um nome crie um box de prévisualização para cada tema com as cores do tema"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ateliê de Temas com Pré-Visualização Visual Estilo Windows 11 (Priority: P1)

Como leitor do Caderno de Leitura,
Quero visualizar cada um dos temas disponíveis através de um cartão de pré-visualização gráfica com as cores reais da paleta (fundo, superfície, texto e acento) — de forma análoga à tela de personalização do Windows 11 —,
Para que eu possa comparar imediatamente a estética e o contraste das opções antes de escolher, sem depender de adivinhar o efeito por um mero menu suspenso de texto.

**Why this priority**: A identidade visual e o conforto dos olhos são o núcleo da experiência de um caderno digital. Substituir uma lista crua suspensa por uma galeria visual com amostras de cor ricas e interativas eleva imediatamente a percepção de qualidade do sistema e reduz a fricção de escolha.

**Independent Test**: Pode ser testado de forma isolada ao acessar a seção de Aparência em `/ajustes`, verificando se cada um dos 10 temas canônicos exibe um cartão com miniatura colorida da sua paleta real, com seleção visual destacada ao clique ou navegação por teclado.

**Acceptance Scenarios**:

1. **Given** que o leitor acessa a seção de Aparência nas preferências, **When** visualiza a área de seleção de tema, **Then** o sistema exibe uma grade de cartões visuais para cada um dos 10 temas canônicos contendo amostras nítidas de suas cores principais (cor de fundo, cor da superfície/cartão, cor da tipografia e cor de destaque/acento), acompanhadas pelo nome do tema.
2. **Given** que um tema específico está ativo, **When** a grade de temas é renderizada, **Then** o cartão do tema ativo apresenta um indicador visual evidente de seleção (borda em relevo e marca de seleção ou anel iluminado), diferenciando-se com clareza dos temas não selecionados.
3. **Given** que o leitor clica ou pressiona a tecla Enter/Espaço sobre um cartão de tema diferente, **When** a seleção é confirmada, **Then** o tema é aplicado imediatamente em toda a aplicação e o novo cartão passa a exibir o estado selecionado.
4. **Given** o tema de alto contraste E-Ink, **When** exibido na grade de pré-visualizações, **Then** seu cartão reflete com fidelidade a composição estritamente monocromática (fundo branco, borda preta e texto preto puro), sem simulação de gradientes ou cores coloridas inexistentes.

---

### User Story 2 - Bancada de Leitura Viva e Sincronia Imediata (Priority: P2)

Como estudioso que ajusta suas preferências de leitura,
Quero uma bancada viva de demonstração literária que responda instantaneamente a qualquer alteração de tamanho de fonte, entrelinha, alinhamento de texto e família tipográfica,
Para que eu encontre minha ergonomia de estudo ideal em tempo real sem precisar abrir um livro real para verificar se o ajuste ficou confortável.

**Why this priority**: Ajustar parâmetros de leitura às cegas gera frustração. A bancada viva garante feedback imediato e segurança ao leitor.

**Independent Test**: Pode ser testado ao alterar sliders ou seletores de tamanho de fonte e espaçamento na seção de Leitura, verificando que o parágrafo de exemplo da amostra ao vivo reage no mesmo instante sem travamento ou atraso perceptível.

**Acceptance Scenarios**:

1. **Given** que o leitor está na tela de preferências no computador desktop, **When** a página é carregada, **Then** o simulador de leitura permanece visível em uma coluna dedicada ao lado dos controles, exibindo um fragmento literário estruturado e cartões de amostra.
2. **Given** que o leitor modifica o tamanho da fonte, entrelinha ou família tipográfica, **When** o controle é manipulado, **Then** o fragmento do simulador reflete as novas dimensões e fontes de forma contínua e suave, sem necessidade de recarregar a página.
3. **Given** que o leitor navega em um dispositivo móvel (smartphone ou tablet), **When** visualiza as opções de leitura, **Then** o simulador de leitura fica acessível através de um painel retrátil inferior expansível, permitindo testar a legibilidade sem cobrir os controles de ajuste.

---

### User Story 3 - Navegação Contínua por Menu Lateral Vertical (Priority: P3)

Como usuário gerenciando múltiplos aspectos da sua conta e do sistema,
Quero navegar pelos 5 grupos temáticos de ajustes (Perfil & Privacidade, Aparência, Leitura, Sistema, Conta & Dispositivos) através de um menu lateral vertical fluido e integrado,
Para que eu tenha clareza de contexto e encontre qualquer configuração rapidamente, substituindo abas horizontais empilhadas no topo.

**Why this priority**: A navegação lateral moderna organiza a densidade de opções com hierarquia clara e mantém o padrão de usabilidade de grandes sistemas operacionais e ferramentas de produtividade.

**Independent Test**: Pode ser testado ao alternar entre os itens do menu lateral vertical, confirmando a transição suave de conteúdo, o destaque do item ativo e a preservação do parâmetro na URL para compartilhamento ou recarga.

**Acceptance Scenarios**:

1. **Given** a tela de ajustes em desktop, **When** o leitor visualiza o menu de navegação, **Then** os 5 grupos aparecem dispostos verticalmente à esquerda com títulos claros e ícones contextuais semânticos.
2. **Given** que o usuário clica em uma seção do menu lateral (por exemplo, "Sistema"), **When** a seção é selecionada, **Then** o formulário correspondente é exibido sem recarga da página, o indicador visual do menu é atualizado e o endereço na barra do navegador reflete a seção ativa.
3. **Given** que o leitor acessa a página com um parâmetro de seção na URL (exemplo: `/ajustes?tab=aparencia`), **When** a página inicializa, **Then** a seção correta abre diretamente com foco e realce adequados.

---

### User Story 4 - Ateliê de Perfil e Curadoria de Avatar (Priority: P4)

Como leitor membro da comunidade literária,
Quero atualizar minha foto de avatar, nome de exibição e biografia literária com validação transparente e recorte visual centralizado,
Para que minha presença pública e correspondência literária no Salão de Amigos reflitam minha identidade autêntica.

**Why this priority**: Personalizar a identidade do perfil dá vida ao aspecto social e de amizade construído no ecossistema literário.

**Independent Test**: Pode ser testado ao enviar uma imagem válida para o avatar, verificando a pré-visualização recortada em formato circular/quadrado suavizado e o salvamento das informações do perfil.

**Acceptance Scenarios**:

1. **Given** a seção de Perfil & Privacidade, **When** o usuário escolhe um arquivo de imagem para o avatar (WebP, PNG ou JPEG de até 2MB), **Then** o sistema gera uma pré-visualização instantânea e recorta a imagem para proporção quadrada nítida.
2. **Given** que o usuário tenta enviar um arquivo com tamanho superior a 2MB ou formato não suportado, **When** o arquivo é selecionado, **Then** o sistema impede o envio e apresenta uma mensagem explicativa em português claro, mantendo o avatar anterior intacto.
3. **Given** o perfil configurado, **When** o usuário aciona a ação "Ver perfil público", **Then** é direcionado para a visualização externa pública do seu próprio perfil de leitor.

---

### User Story 5 - Gestão de Conta, Segurança e Diagnóstico do Sistema (Priority: P5)

Como leitor zeloso pelos seus dados e pela integridade das suas anotações,
Quero gerenciar a segurança da minha conta (troca de senha, encerramento de outras sessões ativas) e consultar métricas de armazenamento local e cópia de segurança,
Para que eu tenha controle e tranquilidade absoluta sobre a privacidade e longevidade do meu caderno de estudos.

**Why this priority**: Preservar a soberania e a segurança dos dados do usuário é um pilar constitucional inviolável do projeto.

**Independent Test**: Pode ser testado ao consultar a aba do Sistema, confirmando a exibição das métricas de diagnósticos e os controles de backup e restauração.

**Acceptance Scenarios**:

1. **Given** a seção Conta & Dispositivos, **When** o usuário altera sua senha com confirmação correta, **Then** a credencial é atualizada com proteção e feedback amigável.
2. **Given** a lista de dispositivos e sessões conectadas, **When** o usuário solicita revogar o acesso de uma sessão secundária, **Then** a sessão é finalizada imediatamente e a lista é atualizada.
3. **Given** a seção de Sistema, **When** o leitor consulta o diagnóstico de integridade, **Then** são exibidas informações precisas sobre volume de armazenamento local, status do banco de dados e ações de backup seguro.

---

### Edge Cases

- **Tema Monocromático E-Ink sob Seleção Visual**: No tema E-Ink, cores de acento são suprimidas intencionalmente; os cartões de pré-visualização devem apresentar alto contraste em preto e branco puro, sem quebrar os anéis de foco ou estados selecionados.
- **Telas Estreitas e Dispositivos Móveis**: A grade de cartões de temas deve reorganizar suas colunas de forma fluida (de 3 a 4 colunas em telas amplas para 2 colunas em telas médias e 1 a 2 colunas em telas compactas), garantindo alvos táteis mínimos de $44 \times 44\text{px}$ para toques em smartphones.
- **Navegação por Teclado na Galeria de Temas**: O grupo de cartões de temas deve operar com semântica de grupo de opções (`role="radiogroup"`), permitindo transição contínua via teclas de seta (`ArrowLeft`, `ArrowRight`, `ArrowUp`, `ArrowDown`), mantendo o leitor de tela informado via atributos `aria-checked`.
- **Sobrescrita de Preferências em Abas Paralelas**: Se as preferências forem alteradas em outra aba do mesmo navegador, os cartões de pré-visualização e a bancada viva devem sincronizar o estado ativo sem recarga forçada.
- **Falha no Carregamento de Imagem de Avatar**: Caso a imagem enviada seja corrompida ou abortada no meio da leitura, o componente deve restaurar graciosamente o avatar tipográfico padrão sem travar a interface.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE fornecer uma galeria visual de pré-visualização de temas na seção de Aparência, composta por cartões individuais para cada um dos 10 temas oficiais do sistema.
- **FR-002**: Cada cartão de pré-visualização de tema DEVE conter um box de amostra que exiba graficamente as cores reais da respectiva paleta: a cor do plano de fundo da página, a cor da superfície do cartão, uma linha representativa da cor do texto e um bloco ou indicador da cor de destaque/acento.
- **FR-003**: Cada cartão de pré-visualização DEVE exibir o nome canônico em português do tema e indicar de forma destacada e evidente quando aquele tema é o atualmente selecionado pelo leitor.
- **FR-004**: O acionamento de qualquer cartão de pré-visualização de tema (por clique, toque ou ativação via teclado) DEVE aplicar o tema correspondente imediatamente em toda a aplicação.
- **FR-005**: A galeria de cartões de temas DEVE ser acessível por teclado, estruturada com semântica acessível de seleção exclusiva (`role="radiogroup"` e `role="radio"` com `aria-checked`), permitindo navegação pelas setas direcionais.
- **FR-006**: O sistema DEVE disponibilizar uma bancada de leitura viva permanente no computador desktop que exiba em tempo real o impacto visual das configurações de tipografia, tamanho de texto, alinhamento, espaçamento e tema.
- **FR-007**: A bancada de leitura viva DEVE atualizar sua renderização instantaneamente a cada movimento de ajuste nos controles de leitura e aparência, sem requerer recarga de página.
- **FR-008**: Em telas móveis e tablets, a bancada de leitura viva DEVE se comportar como um painel inferior retrátil e expansível para possibilitar a conferência visual sem bloquear a manipulação dos controles.
- **FR-009**: O layout principal da tela de preferências DEVE organizar os controles através de um menu lateral vertical com 5 seções temáticas claramente demarcadas: "Perfil & Privacidade", "Aparência", "Leitura", "Sistema" e "Conta & Dispositivos".
- **FR-010**: O menu lateral vertical DEVE sincronizar o estado da seção ativa com a URL da aplicação (parâmetro de busca), garantindo que a recarga da página preserve a seção corrente.
- **FR-011**: O sistema DEVE oferecer upload de imagem para o avatar do leitor com suporte aos formatos WebP, PNG e JPEG, limitando o tamanho a 2MB e fornecendo corte quadrado nítido.
- **FR-012**: O sistema DEVE fornecer validação defensiva para o avatar, recusando arquivos acima de 2MB ou tipos incompatíveis com mensagens explicativas em português.
- **FR-013**: O sistema DEVE preservar as opções de segurança da conta, incluindo alteração de senha autenticada e encerramento seletivo de sessões em outros dispositivos.
- **FR-014**: O sistema DEVE disponibilizar painel de diagnóstico e salvaguarda com métricas de memória e persistência local, além de ferramentas de backup e restauração atômica.
- **FR-015**: Todos os elementos interativos, cartões de temas e botões de ação DEVEM respeitar a área de toque mínima de $44 \times 44\text{px}$ em dispositivos móveis, sem o uso de emojis na interface.

---

### Key Entities

- **Tema Visual**: Representa uma paleta de apresentação do sistema. Composto por identificador único, nome amigável de exibição e valores cromáticos canônicos (fundo da página, superfície, texto e acento).
- **Preferências do Leitor**: Conjunto de configurações personalizadas do leitor, abrangendo tema visual, família tipográfica, tamanho de leitura percentual, entrelinha, alinhamento de parágrafo e preferências de privacidade.
- **Perfil do Leitor**: Registro dos dados de identidade do usuário, incluindo identificador único (`@username`), nome de exibição, biografia de estudo, arquivo de avatar e visibilidade do perfil (público ou restrito).
- **Sessão Ativa de Acesso**: Instância de conexão ativa de um dispositivo, contendo data do último acesso, endereço de rede mascarado e identificador de sessão para revogação.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O leitor consegue visualizar e identificar a paleta cromática de todos os 10 temas em menos de 3 segundos na seção de Aparência graças aos cartões de pré-visualização gráfica.
- **SC-002**: A troca de tema visual a partir da galeria de cartões tem resposta visual imediata no simulador e na interface global (sem latência ou travamento de interface).
- **SC-003**: 100% dos cartões de pré-visualização de temas e controles de formulário são plenamente navegáveis e acionáveis via teclado (teclas Tab, Setas, Espaço e Enter).
- **SC-004**: A validação de arquivos de avatar bloqueia 100% dos arquivos que excedam 2MB antes de qualquer processamento pesado, emitindo aviso legível.
- **SC-005**: A alternância entre as 5 seções temáticas pelo menu lateral vertical ocorre instantaneamente, sem desmontagem abrupta de estado não salvo.
- **SC-006**: 100% dos testes da suíte automatizada do frontend e do backend permanecem aprovados com zero regressões em conformidade com a Constituição do projeto.

---

## Assumptions

- O sistema mantém os 10 temas canônicos oficiais já consolidados no ecossistema (`papel-fosco`, `noite-suave`, `cinza-neutro`, `grafite`, `monocromatico`, `pergaminho`, `e-ink`, `solario`, `fiorde`, `voltagem`).
- As preferências de leitura e aparência do usuário continuarão salvas no armazenamento local do navegador (`localStorage`) com sincronização de perfil no banco de dados quando autenticado.
- A aplicação adota exclusivamente ícones vetoriais padronizados e tipografia editorial, sem uso de emojis no código-fonte ou na interface.
- A pré-visualização viva utiliza fragmentos literários fictícios pré-definidos para demonstração, sem ler anotações privadas ou acervo real do usuário, em conformidade com as regras de privacidade.
