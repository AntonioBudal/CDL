# Feature Specification: Exportação de Anotações em TXT e Markdown

**Feature Branch**: `015-exportacao-anotacoes`  
**Created**: 2026-09-19  
**Status**: Ready for Planning (Clarifications Resolved)  
**Input**: User description: "T07 — Exportação de anotações e estudos de livros em arquivos .txt e .md estruturados (UTF-8, com opções de seleção e exclusão da lixeira)"  

---

## Resolved Clarifications (Session 19/09/2026)

- **Q1 (Pontos de Acionamento e Abrangência)**: **Opção A — Em ambos os níveis (Livro e Estudo individual)**. O usuário pode exportar o livro completo consolidado a partir da página do livro (`/livros/:id`) ou exportar pontualmente o estudo ativo na página de leitura (`/estudos/:id`).
- **Q2 (Seleção de Seções e Conteúdo)**: **Opção A — Modal de confirmação com opções de conteúdo**. Um modal acessível permite escolher o formato (`.md` ou `.txt`) e marcar/desmarcar o conteúdo: `[x] Minhas Anotações` (sempre ativa), `[x] Seções de Estudo (Resumo, Explicação, Conceitos, Referências)` (marcada por padrão) e `[ ] Resposta Original de IA` (opcional/desmarcada por padrão).
- **Q3 (Formatação e Interoperabilidade)**: **Opção A — Markdown com Frontmatter YAML + TXT estruturado**. O arquivo `.md` inclui bloco YAML no topo com metadados da obra (título, autor, ano, categorias, data de exportação), cabeçalhos hierárquicos (`# Livro`, `## Capítulo`, `### Estudo`) e preserva marcadores `==destaque==`. O arquivo `.txt` adota formatação limpa com divisores ASCII legíveis (`===`, `---`) e títulos claros em UTF-8.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Exportação Completa de Anotações de um Livro (Priority: P1) 🎯 MVP

Como um leitor e estudante que acumulou anotações e estudos sobre uma obra, quero exportar todo o conteúdo de um livro em um único arquivo de texto formatado (`.md` ou `.txt`) diretamente para o meu computador ou celular, para que eu possa arquivar minhas notas externamente, imprimir ou utilizá-las em outros aplicativos de escrita e estudo.

**Why this priority**: É o valor central da entrega T07 do Roadmap 0.3. Permite ao leitor ter soberania sobre seus próprios escritos sem depender exclusivamente da interface web do caderno.

**Independent Test**: Acessar um livro com múltiplos capítulos e estudos cadastrados, clicar na ação de exportar, escolher o formato (`.md` ou `.txt`), baixar o arquivo e verificar que o conteúdo foi gerado em UTF-8 com acentos corretos, hierarquia de capítulos preservada e itens da lixeira estritamente excluídos.

**Acceptance Scenarios**:

1. **Given** um livro existente com 2 capítulos e 4 estudos cadastrados, **When** o leitor solicita a exportação em formato Markdown (`.md`), **Then** o sistema gera o download de um arquivo UTF-8 nomeado com o título sanitizado do livro (ex.: `memorias-postumas-de-bras-cubas.md`), contendo cabeçalho da obra, capítulos ordenados, títulos de estudos, localizações e as anotações do leitor.
2. **Given** um livro existente, **When** o leitor seleciona a exportação em formato Texto Puro (`.txt`), **Then** o sistema gera um arquivo `.txt` claro, legível, com divisores de seção em texto puro sem quebras de acentuação no Windows ou mobile.
3. **Given** estudos ou capítulos que foram movidos para a lixeira (`deleted_at` preenchido), **When** a exportação do livro é realizada, **Then** nenhum item excluído deve constar no arquivo exportado.

---

### User Story 2 - Exportação Granular de Estudo Individual (Priority: P2)

Como um estudante focado em um capítulo ou tema específico, quero poder exportar apenas o estudo que estou lendo no momento na tela de leitura, para que eu possa compartilhar um resumo pontual ou colar as anotações específicas sem precisar processar o livro inteiro.

**Why this priority**: Dá agilidade ao fluxo de estudo diário, permitindo extrair rapidamente um único fichamento recém-concluído.

**Independent Test**: Acessar a tela de leitura de um estudo (`/estudos/:id`), clicar no botão "Exportar estudo", escolher `.md` ou `.txt` e verificar que apenas os dados daquele estudo específico são baixados.

**Acceptance Scenarios**:

1. **Given** a tela de leitura de um estudo aberta, **When** o leitor clica na opção de exportar o estudo individual, **Then** o download é iniciado imediatamente com o nome do arquivo refletindo o título do estudo e do livro (ex.: `memorias-postumas-cap-01-estudo.md`).
2. **Given** um estudo individual contendo trechos marcados (`==marcação==`), **When** exportado em Markdown, **Then** as marcações de texto e citações permanecem legíveis e estruturadas.

---

### User Story 3 - Configuração de Conteúdo e Interoperabilidade (Priority: P3)

Como um usuário que utiliza ferramentas externas de anotações (como Obsidian, Logseq ou Notion), quero poder escolher se desejo incluir apenas minhas anotações pessoais ou também as seções de estudo (Resumo, Explicação, Conceitos, Referências) e metadados estruturados (como categorias e ano), para integrar suavemente com meu ecossistema de notas.

**Why this priority**: Proporciona flexibilidade para diferentes perfis de estudantes — desde quem só deseja o texto puro de suas próprias notas até quem quer um dossiê completo de estudo.

**Independent Test**: Abrir as opções de exportação, desmarcar a inclusão das seções automáticas e verificar que o arquivo resultante contém estritamente os metadados do livro e as anotações manuscritas do leitor.

**Acceptance Scenarios**:

1. **Given** o diálogo de exportação aberto, **When** o usuário escolhe incluir metadados adicionais, **Then** o topo do arquivo Markdown exibe informações canônicas de título, autor, ano de publicação e categorias vinculadas.
2. **Given** a seleção personalizada de seções, **When** o arquivo é gerado, **Then** apenas as seções selecionadas pelo usuário são incluídas no corpo do documento.

---

## Edge Cases

- **Títulos de livros ou estudos com caracteres proibidos no sistema de arquivos**: Caracteres como `\`, `/`, `:`, `*`, `?`, `"`, `<`, `>`, `|` devem ser higienizados para evitar erros de download no Windows e mobile.
- **Livro sem capítulos ou sem estudos cadastrados**: O sistema deve exportar um documento legível contendo os metadados da obra e uma mensagem indicativa de que nenhum estudo foi registrado ainda, sem causar erro 500.
- **Estudos com anotações em branco ou nulas**: As seções vazias devem ser omitidas elegantemente para não poluir o documento gerado com cabeçalhos órfãos.
- **Caracteres especiais, emojis e acentuação da língua portuguesa**: O encoding do arquivo gerado deve ser estritamente UTF-8 universal, prevenindo caracteres corrompidos (*mojibake*) no Bloco de Notas do Windows.
- **Acesso pelo navegador móvel via rede local / Tailscale**: O download deve acionar o mecanismo padrão de salvamento de arquivos do navegador móvel (Android/iOS) sem bloquear a tela nem requerer permissões adicionais.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE permitir a exportação do acervo de estudos de um livro nos formatos Markdown (`.md`) e Texto Puro (`.txt`).
- **FR-002**: O sistema DEVE disponibilizar a ação de exportação em dois níveis: na página de visualização do Livro (consolidando todos os capítulos e estudos do livro) e na barra de ferramentas do Leitor de Estudo (exportando apenas o estudo ativo).
- **FR-003**: O sistema DEVE fornecer um diálogo modal acessível (`ExportModal.vue`) que permita ao leitor escolher o formato de download (`.md` ou `.txt`) e selecionar quais blocos de conteúdo deseja incluir: Minhas Anotações (padrão ativado), Seções de Análise do Estudo (Resumo, Explicação, Conceitos, Referências — padrão ativado) e Resposta Original da Importação (opcional desmarcado por padrão).
- **FR-004**: O sistema DEVE formatar os arquivos exportados garantindo alta interoperabilidade: no formato Markdown (`.md`), incluir bloco Frontmatter YAML no topo com metadados canônicos (título, autor, ano, categorias e data da exportação), títulos hierárquicos padronizados (`#`, `##`, `###`) e preservação de trechos destacados (`==texto==`); no formato Texto Puro (`.txt`), apresentar divisores visuais limpos e legíveis (`===`, `---`) em UTF-8.
- **FR-005**: O sistema DEVE codificar todos os arquivos exportados em formato UTF-8, garantindo a preservação exata de diacríticos, acentuação em português e quebras de linha padrão.
- **FR-006**: O sistema DEVE sanitizar os nomes dos arquivos baixados, convertendo caracteres reservados do Windows em hífens ou removendo-os para assegurar compatibilidade no sistema de arquivos local.
- **FR-007**: O sistema DEVE excluir rigorosamente qualquer livro, capítulo ou estudo que esteja marcado como excluído na lixeira (`deleted_at IS NOT NULL`).
- **FR-008**: As anotações originais do usuário (`notes`) DEVEM ser preservadas integralmente no texto gerado, sem alteração de pontuação ou palavras.
- **FR-009**: O processo de download DEVE ser executado diretamente pelo navegador cliente, funcionando de forma idêntica no desktop e em dispositivos móveis conectados via rede local.
- **FR-010**: O sistema NÃO DEVE expor caminhos internos de arquivos do servidor, segredos de ambiente ou identificadores de banco de dados nos arquivos de exportação.

---

### Key Entities *(include if feature involves data)*

- **`ExportRequest`**: Parâmetros de solicitação de exportação:
  - `book_id`: Identificador do livro (obrigatório para exportação de livro).
  - `study_id`: Identificador do estudo (opcional, para exportação individual).
  - `format`: Formato de saída (`'markdown'` ou `'text'`).
  - `include_notes`: Booleano indicando se as notas pessoais do usuário são incluídas (padrão `true`).
  - `include_sections`: Booleano indicando se as 4 seções de análise são incluídas (padrão `true`).
  - `include_source`: Booleano indicando se a resposta original da importação é incluída (padrão `false`).
  - `include_metadata`: Booleano indicando inclusão de categorias, autor e ano.
- **`ExportDocument`**: Representação do artefato gerado:
  - `filename`: Nome sugerido para o arquivo com extensão (`.md` ou `.txt`).
  - `media_type`: Tipo MIME (`text/markdown; charset=utf-8` ou `text/plain; charset=utf-8`).
  - `content`: Conteúdo textual montado em memória para streaming de download.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O download do arquivo exportado inicia em menos de 1 segundo para livros com até 50 estudos.
- **SC-002**: 100% dos arquivos gerados preservam a acentuação e quebras de linha corretas ao serem abertos em editores populares (Bloco de Notas, VS Code, Obsidian, Typora).
- **SC-003**: 0% dos registros presentes na lixeira aparecem em qualquer exportação realizada.
- **SC-004**: O leitor consegue exportar as anotações de um livro em até 3 cliques a partir da tela de visualização do livro.
- **SC-005**: 100% das ações de exportação são acessíveis via teclado e utilizáveis em telas de smartphones.

---

## Assumptions

- A exportação é orientada à leitura e consulta externa pelo usuário, não substituindo o backup de restauração do SQLite (`DatabaseBackup.vue` / T10).
- Os arquivos são gerados dinamicamente em memória ou streaming, sem necessidade de armazenamento temporário persistido em disco no servidor.
- O formato padrão preferencial para quem estuda em ferramentas modernas de anotações é o Markdown (`.md`), mantendo o `.txt` como alternativa universal.
