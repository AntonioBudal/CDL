# Feature Specification: F0.8.01 — Curadoria Editorial, Biblioteca Ativa e Novo Header Global

**Feature Branch**: `065-livros-header`

**Created**: 2026-10-10

**Status**: Ready for Implementation Refinement

**Input**: User description: "Feature 01: Header Global & Livros (Mesa Curatorial) — Resolução da fragmentação visual do cabeçalho e estante fluida com drawer de cadastro"

---

## 1. Diagnóstico Visual Crítico: O Problema do Header Atual

A análise da implementação visual revela um problema de **fragmentação e peso visual excessivo** decorrente do enfileiramento de elementos no cabeçalho:

```text
[Leitorum]  [Livros] [Destaques] [Revisão] [Inbox] [Mais v]  [Sync]  [Buscar Ctrl K]  [Capturar Ctrl+Shift+C]  [Sino]  [Antonio v]
```

1. **Efeito "Blocos de Lego":** Os botões da direita (`Sincronizado`, `Buscar`, `Capturar`, `Notificações`, `Perfil`) e o menu `Mais ▾` foram estilizados como retângulos escuros maciços enfileirados lado a lado. Parecem blocos industriais isolados, e não elementos de uma barra de navegação integrada e elegante.
2. **Quebra de Linguagem entre Abas e Menus:** As abas principais (`Livros`, `Destaques`, `Revisão`, `Inbox`) usam fundo claro/transparente com tipografia limpa, enquanto o botão `Mais ▾` adjacente recebeu preenchimento escuro pesado, parecendo uma ação de outra categoria em vez de uma extensão natural da navegação.
3. **Ausência de Hierarquia de Atenção e Sobrecarga de Atalhos:** Elementos de pesos cognitivos totalmente distintos receberam o mesmo tratamento visual pesado:
   - *Status de Sincronização:* É apenas uma informação passiva de telemetria. Deve ser estritamente um **ícone pequeno** discreto (nuvem/check) com cor semântica suave e tooltip informativo, sem caixa escura, sem bordas pesadas e sem texto ao redor.
   - *Busca:* Deve funcionar como um campo/pílula sutil de pesquisa, integrado suavemente ao fundo da barra com fundo neutro translúcido (`--bg-subtle`), ícone de lupa e rótulo 'Buscar' — **sem o badge `Ctrl K`** visível poluindo a pílula.
   - *Captura Rápida:* Esta sim é a ação primária, merecendo destaque intencional como botão real, contendo **apenas o `+`** (ícone vetorial de adição em botão circular/arredondado de destaque suave), eliminando textos compridos e atalhos visuais pesados.
   - *Sininho e Avatar:* Devem ser ícones de utilidade limpos sobre superfície transparente, acionando seus respectivos popovers sem bordas de botão duro.
   - *Perfil e Logout:* Pílula simples com as iniciais `AN` e nome; o clique abre menu suspenso contendo "Ajustes rápidos", "Meu Perfil" e a ação de Sair da conta (eliminando de vez o botão `Sair` solto no header).
4. **Centralização Perfeita:** A barra de navegação central (`Livros`, `Destaques`, `Revisão`, `Inbox`, `Mais ▾`) deve possuir **centralização horizontal matemática**, usando CSS Grid (`1fr auto 1fr`), para que permaneça rigorosamente no centro exato da tela independente da assimetria entre o logotipo à esquerda e as ferramentas à direita.

---

## 2. User Scenarios & Testing *(mandatory)*

### User Story 1 - Header Global Fluido, Leve e Hierarquizado (Priority: P1) [MVP]

O leitor acessa a aplicação e encontra um cabeçalho global reestruturado de forma leve, fluida e integrada (*App Shell*):
1. **Zona de Navegação:**
   - Centralização horizontal matemática via CSS Grid (`1fr auto 1fr`).
   - Abas em texto com indicador sutil inferior ou pílula suave com cantos arredondados no item ativo.
   - O menu retrátil **"Mais ▾"** segue exatamente a mesma tipografia, altura e estados de hover/ativo das abas principais (`Livros`, `Destaques`, `Revisão`, `Inbox`), diferenciando-se unicamente pelo glifo sutil de seta `▾`.
   - Agrupa utilitários secundários e de ciclo estendido: `Importar`, `Amigos`, `Ajustes`, `Lixeira` (e `Administração` quando aplicável).
2. **Zona de Status (Sincronização):**
   - **Apenas um ícone pequeno** discreto (nuvem/check) com cor semântica suave de sucesso e tooltip informativo, sem texto, sem caixa retangular escura e sem bordas duras.
3. **Zona de Busca Global:**
   - Pílula minimalista com fundo neutro translúcido (`--bg-subtle` / `--color-surface-soft`), ícone de lupa e rótulo 'Buscar' — **sem o badge `Ctrl K`** para uma estética limpa e refinada.
4. **Ação Primária (Captura Rápida):**
   - Botão de ação primária destacado contendo **apenas o `+`** (ícone vetorial de adição em formato circular/arredondado elegante), com tooltip informativo (`title="Captura rápida (Ctrl+Shift+C)"`).
5. **Utilitários e Identidade (Sininho e Perfil):**
   - Sino de notificações sobre superfície limpa/transparente com badge numérico quando houver avisos não lidos.
   - Pílula de perfil com as iniciais e nome do leitor, cujo clique abre menu suspenso contendo "Ajustes rápidos", "Meu Perfil" e a ação de **Sair da conta** (eliminando o botão solto `Sair`).

**Why this priority**: Elimina a fragmentação visual e o efeito "blocos de lego", estabelecendo a fundação ergonômica e a hierarquia correta de atenção para todo o sistema.

**Independent Test**: Navegar por todas as páginas autenticadas verificando ausência de caixas escuras pesadas enfileiradas, integração perfeita do gatilho "Mais ▾" com as abas, presença do botão de captura com destaque intencional e acionamento de logout seguro de dentro do dropdown do usuário.

**Acceptance Scenarios**:

1. **Given** um usuário autenticado no sistema, **When** visualiza o header global, **Then** as abas centrais e o botão "Mais ▾" compartilham a mesma tipografia, alinhamento e estilo visual transparente/leve.
2. **Given** o status de sincronização, **When** renderizado no header, **Then** ele surge como ícone discreto com tooltip, sem caixa retangular escura ao redor.
3. **Given** o botão de Busca Global, **When** inspecionado, **Then** exibe formato de pílula minimalista com fundo translúcido sutil e badge de `Ctrl K` discreto.
4. **Given** o menu suspenso do usuário aberto, **When** o usuário examina suas opções, **Then** encontra links de perfil, ajustes e o botão "Sair da conta" com confirmação de saída.

---

### User Story 2 - Biblioteca Ativa em Largura Total e Drawer Deslizante de Cadastro (Priority: P1) [MVP]

Ao acessar `/livros`, o leitor encontra a biblioteca ocupando a largura total do espaço de leitura, com as seguintes transformações:
1. **Extinção Imediata da Barra Lateral:** A coluna fixa de cadastro (que ocupava cerca de 35% da tela) é completamente removida do layout desktop.
2. **Botão "+ Adicionar Livro":** Posicionado estrategicamente no topo da estante de livros, aciona um painel lateral deslizante (*drawer*).
3. **Drawer Lateral Deslizante:**
   - Ocupa 420px de largura no desktop e 100% no mobile.
   - Transição suave acelerada por GPU (`transform: translateX(0)` em $\le 220$ms).
   - Backdrop escurecido suave e retenção de foco do teclado no primeiro campo (`Título do livro`).
   - Fechamento imediato via tecla `Esc`, clique no botão de fechar ou clique no backdrop.
   - Campos essenciais: Título (obrigatório), Autor (opcional) e Categorias (opcional).

**Why this priority**: Devolve mais de um terço do espaço útil à contemplação e estudo das obras, substituindo uma tela transacional rígida por um ambiente focado e imersivo.

**Independent Test**: Acessar `/livros`, certificar ausência de formulário lateral visível, clicar em "+ Adicionar Livro", conferir abertura suave do Drawer em 220ms, preencher os campos, salvar com sucesso e validar fechamento via `Esc` e backdrop.

**Acceptance Scenarios**:

1. **Given** a página `/livros` carregada no desktop, **When** examinada a composição da tela, **Then** o acervo ocupa 100% da largura útil sem qualquer formulário fixo lateral.
2. **Given** o botão "+ Adicionar Livro" clicado, **When** o Drawer é exibido, **Then** o foco vai automaticamente para o campo de título e o backdrop atenuado cobre o restante da tela.
3. **Given** o Drawer aberto, **When** o leitor pressiona a tecla `Esc` ou clica fora da gaveta no backdrop, **Then** o Drawer se fecha suavemente e o foco retorna ao botão disparador.
4. **Given** os dados de um novo livro preenchidos no Drawer, **When** o formulário é submetido, **Then** o livro é cadastrado via API e a estante é atualizada sem recarga de página.

---

### User Story 3 - Hero "Lendo Agora" e Estante Fluida Editorial (Priority: P2)

No topo da estante de livros, o sistema destaca a seção **"Lendo Agora"** (*Active Reading Hero*):
1. **Hero "Lendo Agora":**
   - Cartão assimétrico no topo destacando o livro com estudo ou leitura mais recente.
   - Capa com proporção realista e elevação tátil.
   - Tipografia editorial para título e autor, indicador de progresso e botão direto de "Continuar Leitura".
2. **Estante Fluida do Acervo:**
   - Grade responsiva preenchendo a largura total da página.
   - Capas dos livros com proporção realista, acabamento editorial e elevação sutil no hover (`transform: translateY(-4px)` em 150ms).
   - Badges sutis de contagem de destaques e estudos sem poluição visual.
   - Preservação dos filtros por categoria, busca por texto, ordenação e alternância entre modos Grade e Lista.

**Why this priority**: Conecta o leitor imediatamente ao seu foco intelectual do momento, eliminando atrito para retomar a leitura ativa.

**Independent Test**: Carregar a biblioteca com livros cadastrados, validar destaque da obra em andamento no Hero Card, alternar entre modos Grade e Lista e conferir filtros por categoria e busca.

**Acceptance Scenarios**:

1. **Given** uma biblioteca com pelo menos um livro, **When** a página `/livros` é carregada, **Then** a obra mais recente é destacada no cartão Hero "Lendo Agora" no topo da estante.
2. **Given** a estante de livros, **When** o ponteiro passa sobre a capa de um livro, **Then** ocorre elevação suave de 4px com transição de sombra em 150ms.
3. **Given** os controles de visualização, **When** o usuário alterna entre Grade e Lista, **Then** o layout se reorganiza de forma suave mantendo todos os filtros e seleções.

---

### User Story 4 - Responsividade, Acessibilidade e Imunidade Cromática (Priority: P3)

A interface se adapta com perfeição a qualquer resolução e dispositivo:
1. **Responsividade:**
   - *Desktop Amplo (1440px+)* e *Laptops (1024px a 1280px)*: Header preserva os 3 blocos sem estouro horizontal (*overflow-x*) e sem quebra de linha.
   - *Mobile (< 768px)*: Alvos de toque $\ge 44 \times 44$px e Drawer ocupando 100% da largura.
2. **Acessibilidade Universal & Reduced Motion:**
   - Suporte pleno a navegação por teclado sem armadilhas de foco (*focus traps*).
   - Sob `prefers-reduced-motion: reduce`, todas as transições de movimento são suprimidas (duração $\le 0.01$ms).
3. **Imunidade Cromática & Zero Emojis:**
   - Uso exclusivo dos tokens semânticos dos 10 temas nativos (`--color-surface`, `--color-page`, `--color-text`, `--color-text-muted`, `--color-border`, `--color-accent`, etc.).
   - Ausência absoluta de emojis literais em favor do catálogo vetorial SVG `Icon.vue`.

**Why this priority**: Garante que o redesenho atenda a padrões rigorosos de acessibilidade, ergonomia e consistência com os 10 temas da aplicação.

**Independent Test**: Testar em resoluções de 375px, 768px, 1280px e 1920px, alternar entre temas Claro, Escuro e Sépia, e verificar respeito a movimento reduzido.

**Acceptance Scenarios**:

1. **Given** o sistema operacional configurado com movimento reduzido, **When** o Drawer é acionado, **Then** ele surge de forma instantânea sem deslizamentos.
2. **Given** alternância entre temas Claro, Noturno e Sépia, **When** o Header e a página de Livros são inspecionados, **Then** nenhuma cor dura ou bloco escuro fixo destoa da paleta ativa.

---

## 3. Checklist Sequencial de Execução (Tasks da Feature 01)

- [ ] **Task 1.1:** Refatorar o Header no layout base: remover fundos escuros pesados dos utilitários da direita, convertendo `Sincronizado` em badge informativo e `Buscar` em pílula de busca refinada.
- [ ] **Task 1.2:** Padronizar visualmente o gatilho `Mais ▾` para seguir a mesma tipografia e estado de hover das abas `Livros`, `Destaques`, `Revisão` e `Inbox`.
- [ ] **Task 1.3:** Agrupar `Sair da conta` dentro do dropdown do avatar do usuário.
- [ ] **Task 1.4:** Remover o formulário estático lateral da tela de Livros.
- [ ] **Task 1.5:** Criar o componente `Drawer` acessível para o cadastro de novo livro, disparado por "+ Adicionar Livro".
- [ ] **Task 1.6:** Implementar a seção Hero do "Livro em Leitura Ativa" no topo do acervo.
- [ ] **Task 1.7:** Reorganizar o grid da biblioteca para preencher a largura total, com animações suaves de hover nas capas.

---

## 4. Critérios de Homologação (Verify)

- [ ] O header não apresenta botões pesados em sequência estilo "tijolos escuros".
- [ ] O menu `Mais ▾` está visualmente integrado à linha de abas de navegação.
- [ ] A página de Livros não possui formulário visível ocupando espaço lateral no desktop.
- [ ] O cadastro de livros abre e fecha via drawer lateral com foco retido e tecla `Esc` ativa.
- [ ] O layout funciona perfeitamente nos temas claro, escuro e sépia.
- [ ] 100% dos testes automatizados continuam passando sem regressões (`npm test` e `npm run build`).
