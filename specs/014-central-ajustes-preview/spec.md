# Feature Specification: Central de Ajustes com Preview ao Vivo e Organização em Seções

**Feature Branch**: `014-central-ajustes-preview`  
**Created**: 2026-09-19  
**Status**: Ready for Planning (Clarifications Resolved)  
**Input**: User description: "T08 — Central de ajustes reorganizada em aparência, leitura e sistema com preview ao vivo"

---

## Resolved Clarifications (Session 19/09/2026)

- **Q1 (Navegação Estrutural)**: **Opção A — Abas segmentadas no topo**. A tela de Ajustes adota três abas principais (`Aparência`, `Leitura` e `Sistema`), permitindo transição imediata sem sobrecarregar a página com rolagens excessivas.
- **Q2 (Arranjo Visual da Amostra)**: **Opção A — Painel lateral fixo no desktop (layout de 2 colunas) e bloco adaptativo empilhado no mobile**. No desktop, a amostra permanece visível ao lado dos controles, refletindo imediatamente as escolhas de tema, fonte e superclasse em tempo real; no mobile, posiciona-se de forma compacta e fluida.
- **Q3 (Ações Operacionais de Sistema)**: **Opção C — Central completa de diagnóstico**. A aba "Sistema" reúne o informativo de persistência (navegador vs banco local), status da conexão local (`/conexao` e `/api/health`), estatísticas de armazenamento do `localStorage` (tamanho em bytes e contagem de chaves), botão "Restaurar Padrões de Aparência" com confirmação explícita, painel de backup manual (`DatabaseBackup.vue`) e limpeza de cache/chaves obsoletas.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Organização Estruturada em Três Seções (Aparência, Leitura e Sistema) (Priority: P1)

Como um leitor que estuda no computador e no celular, quero encontrar as configurações do aplicativo divididas claramente em três áreas lógicas — **Aparência**, **Leitura** e **Sistema** —, para que eu possa ajustar temas visuais, conforto tipográfico ou verificar a integridade da conexão sem me perder em uma lista interminável e desordenada de opções.

**Why this priority**: A usabilidade da tela de configurações é a base para a experiência personalizada de estudo. Sem uma categorização funcional intuitiva, o usuário tem dificuldade de encontrar ajustes cruciais como fontes, paletas e status da sincronização local.

**Independent Test**: Acessar a tela de Ajustes (`/ajustes`) e navegar entre as seções de Aparência, Leitura e Sistema, validando que os controles pertencentes a cada categoria estão agrupados e legendados com exatidão.

**Acceptance Scenarios**:

1. **Given** que o leitor acessa a tela de Ajustes, **When** ele seleciona a seção "Aparência", **Then** são exibidos os controles visuais globais (paleta/tema, Superclasse de interface, intensidade física, cor de destaque e largura de página).
2. **Given** que o leitor acessa a seção "Leitura", **When** ele altera o tamanho da fonte ou a família tipográfica, **Then** as opções refletem diretamente o catálogo literário seguro (EB Garamond, Source Sans 3, OpenDyslexic, etc.) e a escala de leitura.
3. **Given** que o leitor acessa a seção "Sistema", **When** a tela é exibida, **Then** ele visualiza um informativo explícito destacando que as preferências visuais são salvas no navegador local, enquanto as notas e o acervo residem no banco de dados, acompanhado do status da conexão e opções de restauração dos padrões visuais.

---

### User Story 2 - Amostra Dinâmica e Preview ao Vivo de Tokens e Estilos (Priority: P2)

Como um estudante ajustando a experiência visual do caderno, quero ver imediatamente uma amostra interativa composta por um cartão de livro realista e um trecho de texto com abas e marcações (`==destaque==`), para que eu possa avaliar o contraste, tamanho e comportamento físico antes de continuar meus estudos, sem precisar transitar entre telas.

**Why this priority**: Ajustar opções visuais "no escuro" força o usuário a trocar de página várias vezes para testar o resultado. O preview integrado ao vivo fecha o ciclo de feedback visual instantaneamente.

**Independent Test**: Modificar o tema para "Pergaminho", a fonte para "EB Garamond" e a Superclasse para "Mecânica", verificando que o painel de amostra atualiza suas cores, tipografia, bordas e microinterações no mesmo instante, sem recarregar a página.

**Acceptance Scenarios**:

1. **Given** a amostra visível na tela de Ajustes, **When** o leitor troca a paleta de cores (ex.: de Porcelana para Breu ou E-Ink), **Then** o cartão de amostra e o bloco de leitura atualizam suas cores de fundo, texto e realces conforme os tokens ativos.
2. **Given** a amostra com abas e marcação de estudo, **When** o usuário clica nas abas da amostra (Resumo, Explicação, Conceitos, Referências), **Then** a navegação funciona de forma idêntica ao leitor real e exibe o estilo de marcação selecionado.
3. **Given** o cartão de livro de exemplo na amostra, **When** a preferência de exibição do acervo é alterada (modo grade com capa vs modo lista compacto), **Then** a amostra de cartão reflete fielmente essa escolha estrutural.

---

### User Story 3 - Robustez de Persistência, Precedência de Acessibilidade e Prevenção de FOUC (Priority: P3)

Como um leitor que utiliza telas variadas (inclusive dispositivos com tela e-ink ou preferências de acessibilidade), quero que minhas escolhas sejam salvas com segurança no navegador, aplicadas sem nenhum clarão (*flash of unstyled content*) ao recarregar e que respeitem modos de alto contraste e redução de movimento.

**Why this priority**: A estabilidade operacional e a acessibilidade garantem que o sistema seja confiável em qualquer dispositivo, preservando preferências mesmo sob falhas temporárias de armazenamento local.

**Independent Test**: Configurar preferências personalizadas, recarregar a página forçadamente (Ctrl+F5) e verificar que o tema e a fonte já são aplicados no primeiro milissegundo de renderização, sem saltos de layout ou flashes visuais.

**Acceptance Scenarios**:

1. **Given** o tema configurado como "E-Ink", **When** o usuário tenta alterar a cor de destaque cromática ou intensidade de física, **Then** o sistema mantém a precedência monocromática rígida (preto/branco/cinza) para garantir legibilidade estrita.
2. **Given** a detecção de preferência do sistema por redução de movimento (`prefers-reduced-motion`), **When** uma Superclasse dinâmica estiver ativa, **Then** animações e transições cinemáticas são neutralizadas automaticamente.
3. **Given** preferências salvas previamente no navegador, **When** a página é carregada pela primeira vez, **Then** o script de inicialização precoce no cabeçalho aplica as classes e variáveis no elemento raiz antes da renderização do Vue.
4. **Given** a existência de valores corrompidos ou obsoletos no armazenamento local, **When** o aplicativo é iniciado, **Then** os valores inválidos são purgados e substituídos por padrões seguros sem apagar preferências válidas.

---

### Edge Cases

- **Armazenamento local (`localStorage`) bloqueado ou desativado**: O sistema deve aplicar as preferências na sessão ativa e exibir um aviso discreto explicando que as alterações não serão persistidas após fechar o navegador.
- **Telas muito estreitas (< 360px) em celulares**: O bloco de prévia e os controles de formulário devem empilhar verticalmente mantendo áreas de toque de no mínimo 44px para evitar toques acidentais.
- **Troca rápida e repetida de fontes e temas**: A renderização deve permanecer fluida e estável sem travamentos do navegador nem sobreposição de fontes locais não carregadas.
- **Redefinição total de preferências ("Restaurar Padrões")**: Deve solicitar confirmação explícita antes de purgar as configurações visuais salvas no navegador.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE organizar a tela de Ajustes em exatamente três seções lógicas: **Aparência**, **Leitura** e **Sistema**.
- **FR-002**: A navegação entre as três seções DEVE utilizar uma barra de abas segmentadas no topo da página de Ajustes (`role="tablist"`), permitindo alternância instantânea entre "Aparência", "Leitura" e "Sistema" com suporte total a navegação por teclado (setas horizontais, Enter e Espaço).
- **FR-003**: A seção **Aparência** DEVE conter os controles de: Tema Cromático (10 paletas oficiais), Superclasse de Interface (5 estilos físicos), Multiplicador de Intensidade da Superclasse, Cor de Destaque e Largura da Interface.
- **FR-004**: A seção **Leitura** DEVE conter os controles de: Fonte Tipográfica (seletor com catálogo de fontes literárias e fallback), Tamanho do Texto no Leitor (controle granular), Densidade Visual e Estilo de Marcação de Texto.
- **FR-005**: A seção **Sistema** DEVE exibir um painel informativo detalhando o escopo de persistência (preferências salvas localmente no navegador via `localStorage` versus acervo salvo no SQLite local `caderno.db`).
- **FR-006**: A seção **Sistema** DEVE fornecer uma Central Completa de Diagnóstico contendo:
  - Informativo visual sobre o escopo de persistência (armazenamento local no navegador vs banco de dados).
  - Teste de status da conexão local com atalho para `/conexao` e verificação de integridade via `/api/health`.
  - Diagnóstico de armazenamento do navegador (tamanho estimado em bytes e contagem de chaves ativas do `localStorage`).
  - Botão "Restaurar Padrões de Aparência", redefinindo todas as preferências visuais para os padrões de fábrica após confirmação explícita em modal/diálogo.
  - Painel de backup manual do banco de dados (reaproveitando o componente `DatabaseBackup.vue`).
  - Ação de limpeza de cache e purga atômica de chaves legadas e obsoletas do navegador.
- **FR-007**: A tela de Ajustes DEVE exibir uma **Amostra Interativa (Preview ao Vivo)** contendo:
  - Um cartão de livro funcional refletindo a preferência de exibição do acervo.
  - Um bloco de leitura com abas de estudo reais (Resumo, Explicação, Conceitos, Referências) contendo texto formatado e trechos marcados (`==exemplo==`).
  - Botões de ação e estados de controle demonstrativos.
- **FR-008**: O posicionamento da Amostra Interativa DEVE adotar um layout de duas colunas no desktop (> 1024px), com os controles na coluna principal à esquerda e o painel de amostra fixo/aderente (*sticky*) à direita, garantindo visibilidade contínua durante a edição; em telas menores ou móveis (<= 1024px), a amostra posiciona-se empilhada abaixo dos controles da aba ativa de forma fluida.
- **FR-009**: Qualquer alteração em qualquer controle de Aparência ou Leitura DEVE ser refletida instantaneamente na Amostra Interativa e na interface geral sem necessidade de recarregar a página.
- **FR-010**: O sistema DEVE aplicar o script de inicialização precoce (`appearance-bootstrap.js`) no cabeçalho do documento para garantir zero clarão (*FOUC*) durante o carregamento inicial.
- **FR-011**: O tema monocromático `e-ink` DEVE manter precedência estrita, suprimindo saturação cromática, sombras difusas e físicas cinemáticas.
- **FR-012**: O sistema DEVE respeitar a preferência de acessibilidade do usuário por redução de movimento (`prefers-reduced-motion`), neutralizando transições cinemáticas nas Superclasses.
- **FR-013**: O sistema DEVE fornecer um botão "Restaurar Padrões de Aparência", que redefine as preferências para as configurações originais de fábrica após confirmação do usuário.
- **FR-014**: Todas as opções legadas ou obsoletas do `localStorage` DEVEM ser automaticamente migradas ou purgadas de forma atômica na inicialização.
- **FR-015**: Todos os controles de seleção, botões e campos DEVEM ser 100% operáveis via teclado (Tab, setas, Enter, Espaço) com indicador visual de foco nítido e acessível.

---

### Key Entities *(include if feature involves data)*

- **`AppearancePreferences`**: Estrutura cliente (armazenada em `localStorage`) que persiste as escolhas do leitor:
  - `theme`: Identificador da paleta de cores (ex.: `porcelana`, `breu`, `pergaminho`, `e-ink`, etc.).
  - `accent`: Cor de destaque da interface.
  - `font`: Família tipográfica ativa para leitura e interface.
  - `reader-size`: Escala percentual de tamanho do texto do leitor (ex.: `100%`).
  - `density`: Nível de espaçamento e densidade de informação.
  - `mark-style`: Estilo visual de realce de texto marcado.
  - `library-view`: Modo preferencial de visualização do acervo (grade vs lista).
  - `layout-width`: Largura máxima do contêiner da página.
  - `superclass`: Estilo físico e comportamental ativo (`zero-g`, `mecanica`, `invisivel`, `dimensional`, `monolitica`).
  - `superclass-intensity`: Multiplicador numérico paramétrico da Superclasse.
- **`SystemScopeInfo`**: Entidade lógica exibida na interface para orientação do usuário:
  - Informações de escopo (navegador local vs servidor).
  - Status da conexão com a API local (`/api/health`).
  - Versão instalada da aplicação.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O leitor consegue alternar entre qualquer um dos 10 temas, 5 Superclasses e famílias tipográficas com reflexo visual instantâneo na Amostra Interativa em menos de 50ms.
- **SC-002**: 100% dos controles presentes na tela de Ajustes possuem rótulos descritivos, textos explicativos e impacto visual imediatamente visível na amostra.
- **SC-003**: O recarregamento forçado da página (F5) não apresenta nenhum clarão perceptível de tema incorreto (*FOUC* zero).
- **SC-004**: 100% dos controles e abas da tela de Ajustes são acessíveis e navegáveis exclusivamente através do teclado, com áreas de toque móveis de no mínimo 44px x 44px.
- **SC-005**: A separação das configurações nas três áreas lógicas reduz o tempo de localização de um ajuste em pelo menos 50% em comparação com uma listagem linear única.

---

## Assumptions

- As preferências visuais continuam sendo armazenadas no `localStorage` sob o namespace seguro `caderno.aparencia.v2`.
- O catálogo de 10 paletas cromáticas e as 5 Superclasses de Interface (Zero-G, Mecânica, Invisível, Dimensional, Monolítica) já homologadas são mantidos integralmente.
- O componente `AppearancePreview.vue` existente será aprimorado para refletir dinamicamente a preferência de exibição do acervo (grade/lista) e as abas reais de leitura.
- O banco de dados ativo `backend/data/caderno.db` não armazena preferências específicas de navegador de cada cliente, mantendo o isolamento entre dados do acervo e aparência pessoal de cada dispositivo.
