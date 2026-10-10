# Feature Specification: F0.8.01 — Curadoria Editorial, Biblioteca Ativa e Novo Header Global

**Feature Branch**: `065-livros-header`

**Created**: 2026-10-10

**Status**: Draft

**Input**: User description: "Feature 01: Livros — Curadoria Editorial, Biblioteca Ativa e Novo Header Global (Roadmap 0.8 — Redesign Estrutural e Arquitetura Visual)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Header Global em 3 Zonas Operacionais e Menu do Usuário (Priority: P1) [MVP]

O leitor acessa a aplicação e encontra um cabeçalho global reestruturado de forma limpa, desobstruída e hierarquizada em 3 blocos semânticos:
1. **Bloco Esquerdo (Marca):** Logotipo minimalista `Leitorum` com link para a raiz/acervo.
2. **Bloco Central (Navegação Primária + Menu 'Mais'):**
   - 4 abas diretas reservadas ao ciclo ativo de leitura diária: **Livros**, **Destaques**, **Revisão**, **Inbox**.
   - Menu suspenso retrátil **"Mais ▾"**: agrupa utilitários secundários e de ciclo estendido: **Importar**, **Amigos**, **Ajustes**, **Lixeira** (e **Administração** para administradores).
3. **Bloco Direito (Centro de Ferramentas e Identidade):**
   - Pílula de comando para **Busca Global** (`Ctrl+K`).
   - Botão de ação rápida de **Captura** (`Ctrl+Shift+C`).
   - Indicador discreto de **Sincronização** com pulso e tooltip contextual.
   - Centro de **Notificações** (sino com badge).
   - **Menu do Usuário (Avatar/Iniciais):** Dropdown unificado contendo o perfil do leitor, identificador, status da conta e, obrigatoriamente, a ação de **Sair** (`handleLogout`), removendo o botão solto de logout do topo do header.

**Why this priority**: O Header Global constitui a moldura mestre de navegação (*App Shell*) de todo o sistema. Sua consolidação em 3 zonas elimina a superlotação horizontal e serve de fundação estável para todas as rotas e features subsequentes do Roadmap 0.8.

**Independent Test**: Navegar por todas as rotas autenticadas verificando a presença e consistência dos 3 blocos, abertura e navegação pelo menu retrátil "Mais ▾", e acionamento de logout seguro de dentro do dropdown do usuário.

**Acceptance Scenarios**:

1. **Given** um usuário autenticado em qualquer página, **When** visualiza o header global, **Then** apenas as 4 abas de leitura ativa (`Livros`, `Destaques`, `Revisão`, `Inbox`) estão expostas diretamente, e as abas estendidas estão acessíveis no menu "Mais ▾".
2. **Given** o header global exibido, **When** o usuário inspeciona o topo direito, **Then** o botão solto "Sair" não existe no nível superior, residindo exclusivamente dentro do dropdown acionado pelo avatar/iniciais do leitor.
3. **Given** o menu suspenso do usuário aberto, **When** o leitor clica em "Sair", **Then** a confirmação é apresentada e a sessão é encerrada com redirecionamento para `/login`.

---

### User Story 2 - Biblioteca Ativa em Largura Total e Drawer Deslizante de Cadastro (Priority: P1) [MVP]

Ao acessar `/livros`, o usuário encontra a biblioteca ocupando a largura total do espaço de leitura, sem a coluna lateral estática de formulário (que anteriormente ocupava ~35% da tela).
No lugar do painel rígido fixo, a página disponibiliza um botão proeminente e tátil `+ Adicionar Livro` na barra de ações da biblioteca. Ao ser clicado:
- Abre um **Drawer lateral deslizante** acessível a partir da direita (420px de largura no desktop, 100% no mobile).
- O Drawer retém o foco do teclado no primeiro campo (`Título do livro`).
- O leitor pode preencher título, autor e categorias e salvar o livro, ou fechar o Drawer pressionando `Esc`, clicando no botão fechar ou clicando no backdrop escurecido suave.
- Ao salvar, o livro é criado via API existente e o leitor é conduzido ao livro recém-criado ou vê o acervo atualizado sem quebras de validação.

**Why this priority**: Devolve mais de um terço da tela à exploração dos livros e substitui uma experiência rígida de formulário CRUD por um fluxo focado, imersivo e livre de distrações visuais.

**Independent Test**: Acessar `/livros`, verificar ausência de formulário estático lateral, clicar em `+ Adicionar Livro`, validar abertura suave do Drawer em 220ms, preencher os campos, salvar com sucesso e testar fechamento via `Esc` e backdrop.

**Acceptance Scenarios**:

1. **Given** a página `/livros` carregada, **When** o usuário inspeciona o layout da página, **Then** o acervo de livros ocupa a largura útil total sem painel lateral estático permanente.
2. **Given** o botão `+ Adicionar Livro` acionado, **When** o Drawer é aberto, **Then** ele surge com deslizamento lateral suave da direita para a esquerda, exibe backdrop atenuado e direciona o foco para o campo de título.
3. **Given** o Drawer aberto, **When** o usuário pressiona a tecla `Esc` ou clica fora da gaveta no backdrop, **Then** o Drawer se fecha e o foco retorna ao botão que o disparou.
4. **Given** o formulário no Drawer preenchido com dados válidos, **When** o usuário clica em "Cadastrar livro", **Then** a requisição é submetida com estado de carregamento e o livro é criado sem erros.

---

### User Story 3 - Hero de Leitura Ativa ("Em Andamento") e Estante Fluida (Priority: P2)

No topo da página de livros (acima da grade geral), o sistema destaca a seção **"Em Andamento"** com um *Hero Card* dedicado à leitura mais recente ou à obra com estudo ativo mais recente. O Hero Card exibe:
- Capa do livro com proporção realista e elevação sutil.
- Título em destaque tipográfico e autor.
- Indicador visual de progresso e atalho direto para "Continuar leitura".

Abaixo da seção em andamento, o acervo é apresentado em uma grade fluida curatorial com:
- Proporção visual realista de livros e acabamento editorial.
- Chips de filtragem rápida por categoria e barra integrada de busca e ordenação.
- Alternância rápida e suave entre modos **Grade** e **Lista** sem recarga da página.
- Efeito tátil suave de elevação no hover (`transform: translateY(-4px)` em 150ms).

**Why this priority**: Conecta o leitor imediatamente ao seu foco intelectual do momento, eliminando atrito para retomar a leitura ativa.

**Independent Test**: Carregar a biblioteca com livros existentes, conferir destaque da obra mais recente no Hero Card, alternar entre grade e lista, e validar preservação de filtros por categoria e busca.

**Acceptance Scenarios**:

1. **Given** uma biblioteca com pelo menos um livro, **When** a página é carregada, **Then** o livro com atividade mais recente é destacado no Hero Card de leitura ativa no topo.
2. **Given** a grade de livros exibida, **When** o usuário alterna o modo para Lista, **Then** a visualização se transforma suavemente sem recarga e mantém os filtros aplicados.
3. **Given** um cartão de livro na grade, **When** o ponteiro passa sobre ele, **Then** ocorre elevação sutil de 4px com transição suave respeitando `--radius-card` e variáveis do tema ativo.

---

### User Story 4 - Responsividade e Acessibilidade (Mobile, Teclado, Reduced Motion) (Priority: P3)

A interface se adapta com perfeição a qualquer resolução:
- **Desktop e Laptops (1280px - 1920px):** Layout espaçoso de 3 blocos no Header, Drawer de 420px, grade de 3 a 4 colunas.
- **Tablets e Telas Intermediárias (768px - 1024px):** Header preserva os 3 blocos sem quebra de linha com espacamentos proporcionais; grade de 2 a 3 colunas.
- **Mobile (< 768px):** Header compacto com navegação primária adaptada, alvos táteis mínimos de $44 \times 44$px, Drawer ocupando 100% da largura.
- **Preferência por Movimento Reduzido (`prefers-reduced-motion`):** As transições do Drawer e animações de hover são reduzidas para 0.01ms instantâneo para conforto visual.
- **Imunidade Cromática:** O novo layout e todos os novos componentes utilizam exclusivamente variáveis CSS semânticas (`--color-surface`, `--color-page`, `--color-text`, `--color-border`, etc.) sem valores fixos de cor, preservando integralmente os 10 temas canônicos.

**Why this priority**: Garante ergonomia universal, conformidade estrita com as diretrizes de acessibilidade e preservação absoluta do sistema visual dos 10 temas.

**Independent Test**: Testar em resoluções de 375px, 768px, 1280px e 1920px, auditar conformidade com `prefers-reduced-motion`, verificar ausência de valores hexadecimais no CSS dos novos componentes e validar que todos os botões possuem área $\ge 44 \times 44$px.

**Acceptance Scenarios**:

1. **Given** tela mobile (< 768px), **When** o Drawer de novo livro é aberto, **Then** ele ocupa 100% da largura da tela com controles de toque $\ge 44 \times 44$px.
2. **Given** o sistema operacional configurado com movimento reduzido, **When** elementos são abertos ou focados, **Then** transições de movimento são instantâneas sem deslizamentos prolongados.
3. **Given** qualquer um dos 10 temas cromáticos ativos, **When** a biblioteca e o novo header são renderizados, **Then** todos os tons, bordas e superfícies refletem as variáveis daquele tema sem desvios ou cores duras.

---

### Edge Cases

- **Biblioteca Vazia (Zero Livros):** Quando não há livros cadastrados, o Hero Card é suprimido graciosamente e o estado vazio orienta o leitor a clicar no botão "+ Adicionar Livro", abrindo o Drawer.
- **Apenas Um Livro no Acervo:** O único livro é exibido tanto no Hero quanto na estante, sem quebras de layout ou duplicação indevida de dados.
- **Título com Nome Excessivamente Longo no Drawer:** O campo de texto acomoda quebra visual de linha sem vazar as margens do Drawer (420px).
- **Tentativa de Sair com Drawer Aberto:** Ao fechar o Drawer via `Esc` ou backdrop, alterações pendentes nos campos disparam a proteção de dados não salvos (`useUnsavedChanges`).
- **Resoluções Intermediárias (ex.: 1024px com zoom de 125%):** O Header Global não sofre estouro horizontal (*overflow-x*), acomodando os 3 blocos sem quebra de linha desagradável.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE refatorar o Header Global (`App Shell`) em 3 zonas operacionais independentes: Marca (esquerda), Navegação Primária e Menu 'Mais' (centro), Centro de Ferramentas e Identidade (direita).
- **FR-002**: O Header DEVE expor na navegação central direta exclusivamente as 4 rotas de leitura ativa: Livros, Destaques, Revisão e Inbox, agrupando Importar, Amigos, Ajustes, Lixeira e Administração dentro do menu retrátil "Mais ▾".
- **FR-003**: O botão avulso "Sair" DEVE ser removido do plano superior do Header e encapsulado no menu suspenso do usuário (`UserDropdown`), preservando a confirmação de logout e o redirecionamento.
- **FR-004**: O layout principal de `/livros` DEVE remover a coluna estática lateral de cadastro, exibindo o acervo em largura total com composição de mesa do leitor.
- **FR-005**: O sistema DEVE fornecer um componente reutilizável e acessível de `Drawer` lateral deslizante com animação acelerada por GPU (`transform`, $\le 220$ms), backdrop suave, retenção de foco e fechamento via `Esc` e clique no backdrop.
- **FR-006**: O cadastro de novo livro DEVE ser realizado integralmente dentro do `Drawer`, mantendo campos de Título (obrigatório), Autor (opcional) e Categorias (opcional) e integração com `api.createBook`.
- **FR-007**: A página `/livros` DEVE exibir na seção de topo um Hero Card da leitura ativa ("Em Andamento") baseado na obra aberta mais recente ou na primeira obra do acervo com estudos ativos.
- **FR-008**: O acervo DEVE manter integralmente os modos de visualização Grade e Lista, busca rápida por texto, filtro por categorias e abas "Meu Acervo" e "Compartilhados Comigo".
- **FR-009**: Todos os botões, links e gatilhos DEVEM possuir alvo tátil mínimo de $44 \times 44$px em resoluções móveis, além de atributos `aria-label`, `aria-expanded` e `aria-haspopup` semânticos.
- **FR-010**: A estilização do novo Header e da página de Livros DEVE consumir exclusivamente as variáveis semânticas CSS dos 10 temas nativos, proibindo valores hexadecimais fixos nos estilos dos novos componentes.
- **FR-011**: O sistema DEVE fornecer suporte obrigatório a `prefers-reduced-motion`, neutralizando transições de movimento para usuários que requisitarem.
- **FR-012**: O código-fonte dos novos componentes DEVE respeitar a regra constitucional de ZERO EMOJIS, utilizando exclusivamente ícones SVG semânticos do catálogo `Icon.vue`.

### Key Entities

- **GlobalHeader**: Componente do App Shell unificado divido em 3 zonas: marca, abas principais com menu retrátil "Mais", e utilitários com menu do usuário.
- **UserDropdown**: Menu contextual do leitor autenticado contendo perfil, identificador, status da conta e a ação segura de logout.
- **Drawer**: Componente estrutural compartilhado de gaveta lateral deslizante acessível com gerenciamento de foco e backdrop modal.
- **BookHeroCard**: Cartão editorial destacado de leitura ativa no topo da biblioteca.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O Header Global reduz seus elementos concorrentes diretos no plano horizontal de 15 para 3 blocos coesos, eliminando quebras de layout em resoluções entre 1024px e 1280px.
- **SC-002**: A área útil dedicada à exploração do acervo na página `/livros` aumenta em mais de 35% com a eliminação da coluna estática de formulário.
- **SC-003**: O tempo para abrir o Drawer de novo livro, preencher o título e confirmar o cadastro é inferior a 10 segundos, com transição fluida de abertura em $\le 220$ms.
- **SC-004**: 100% dos testes da suíte de frontend (`npm test`) continuam passando sem regressões em rotas existentes ou fluxos de biblioteca.
- **SC-005**: 100% de conformidade cromática: todos os 10 temas canônicos mantêm contraste e identidade visual impecáveis sem estilos corrompidos.

---

## Assumptions

- A API backend de livros (`POST /api/books`, `GET /api/books`, etc.) e modelos de dados já existentes permanecem inalterados e plenamente compatíveis.
- O catálogo de ícones do componente `Icon.vue` já fornece todos os ícones necessários (`book-open`, `pencil`, `rotate-ccw`, `inbox`, `more-horizontal`, `search`, `bell`, `sliders`, `trash`, `users`, `plus`, `x`, `log-out`, etc.).
- A preferência de leitura ativa pode derivar do livro com atualização mais recente (`updated_at`) ou do último livro acessado registrado em `localStorage`.
