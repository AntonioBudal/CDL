# Feature Specification: F0.7.12 — Backlinks e Menções entre Estudos

**Feature Branch**: `061-backlinks-mencoes-estudos`

**Created**: 2026-10-06

**Status**: Ready for Planning

**Input**: User description: "/speckit-specify 0.7.12" (F 0.7.12 — Backlinks e Menções entre Estudos `[[...]]`)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Autocomplete e Inserção de Menções no Editor de Estudo (Priority: P1) 🎯 MVP

Como leitor e pesquisador redigindo a análise ou reflexão de um estudo, quero poder digitar uma sintaxe amigável (como `[[`) e ver sugestões instantâneas dos estudos do meu acervo para inserir menções diretas a outros conceitos sem precisar abrir outra aba ou copiar URLs manualmente.

**Why this priority**: É a porta de entrada da rede de conhecimento pessoal; sem uma forma fluida de referenciar outros estudos durante a escrita, os backlinks reversos não podem ser originados.

**Independent Test**: No editor de estudos (`StudyEditView.vue` / `StudyEditorFields.vue`), posicionar o cursor em qualquer campo de texto (resumo, explicação, conceitos ou referências), digitar `[[` seguido das primeiras letras do título de outro estudo; verificar o surgimento do popover de autocomplete, selecionar o estudo desejado com clique ou Enter e verificar a inserção automática da sintaxe de menção (`[[Título]]` ou `[[Título|id]]`).

**Acceptance Scenarios**:

1. **Given** um leitor editando uma seção de análise no formulário de estudo, **When** ele digita `[[`, **Then** um menu suspenso leve de autocomplete é exibido com lista filtrada dos estudos ativos do seu acervo.
2. **Given** o menu de sugestões aberto, **When** o usuário digita letras adicionais ou navega com as setas do teclado e pressiona Enter (ou clica em um item), **Then** a menção é inserida no formato `[[Título]]` (ou `[[Título|id]]` em caso de estudos homônimos) e o cursor é posicionado logo após o fechamento `]]`.
3. **Given** o menu de sugestões aberto, **When** o leitor pressiona a tecla `Escape` ou apaga o gatilho `[[`, **Then** o menu é fechado imediatamente sem alterar o restante do texto.

---

### User Story 2 - Renderização de Links Internos e Navegação Direta no Leitor (Priority: P2)

Como leitor revisando um estudo concluído, quero que as menções textuais `[[...]]` sejam renderizadas como links internos claros e clicáveis que me levem diretamente ao estudo citado, permitindo explorar conexões de pensamento de maneira contínua.

**Why this priority**: Conecta a escrita com a leitura: o leitor precisa ser capaz de seguir as referências cruzadas que registrou em sua jornada de estudos.

**Independent Test**: Abrir um estudo que contenha uma ou mais menções `[[...]]` no leitor (`StudyView.vue`), verificar se o trecho é renderizado como link estilizado diferenciado de links externos comuns e, ao clicar, ser redirecionado para a rota do estudo correspondente.

**Acceptance Scenarios**:

1. **Given** um estudo cujo texto analítico contenha `[[Título do Estudo]]` ou `[[Título|id]]`, **When** ele é exibido no leitor de markdown (`MarkdownContent.vue`), **Then** o token é transformado em um link contextual interno com ícone sutil e tooltip informativo indicando livro e capítulo do estudo alvo.
2. **Given** uma menção interna renderizada, **When** o leitor clica no link, **Then** a aplicação navega diretamente para `/livros/:bookId/estudos/:studyId` do estudo citado, preservando histórico de navegação.
3. **Given** uma menção a um estudo que foi posteriormente enviado para a lixeira ou excluído, **When** o texto é exibido, **Then** o link é estilizado com indicador discreto de destino na lixeira/arquivado, prevenindo erro de tela quebrada ao clicar.

---

### User Story 3 - Painel Reverso de Backlinks no Rodapé da Coluna de Leitura (Priority: P3)

Como leitor consultando um conceito ou estudo fundamental, quero visualizar um painel no rodapé ("Mencionado nos estudos:") que liste automaticamente todos os outros estudos que citaram este estudo, permitindo descobrir conexões emergentes de baixo para cima (*bottom-up*).

**Why this priority**: Completa a bidirecionalidade do grafo de conhecimento. Diferencia-se das relações semânticas conceituais de alto nível por representar referências contextuais pontuais no texto.

**Independent Test**: Acessar um estudo que foi citado em dois outros estudos diferentes, rolar até o rodapé da coluna central e verificar a listagem dos 2 estudos de origem, com título da obra, título do estudo e pequeno trecho do contexto em que a menção ocorreu.

**Acceptance Scenarios**:

1. **Given** um estudo B que foi mencionado no estudo A, **When** o leitor abre o estudo B, **Then** um painel semântico no rodapé da coluna central ("Mencionado em:") exibe o cartão do estudo A com título da obra, capítulo e trecho da citação contextual.
2. **Given** múltiplos estudos citando o mesmo estudo, **When** a seção de backlinks é carregada, **Then** a lista exibe cabeçalho com contador de referências ("Mencionado em X estudos") e cartões estruturados com links clicáveis para abrir o estudo de origem.
3. **Given** que o estudo de origem A foi enviado para a lixeira, **When** o estudo B é consultado, **Then** o backlink do estudo A é omitido da lista ativa.

---

### Edge Cases

- **Estudos com o mesmo título em livros distintos**: Dois estudos podem se chamar "Introdução" ou "Conclusão". O sistema utiliza sintaxe limpa por padrão `[[Título]]`; se o autocomplete detectar duplicidade no acervo, exibe as opções qualificadas por livro/capítulo e insere a forma desambiguada com ID numérico `[[Título|id]]`.
- **Estudos renomeados posteriormente**: A tabela `study_mentions` mantém os vínculos indexados pelas chaves estrangeiras `source_study_id` e `target_study_id`. Se o título do estudo alvo mudar, o link interno continua navegável pelo ID associado.
- **Estudos enviados para a lixeira**: Se o estudo alvo for movido para a lixeira (`deleted_at IS NOT NULL`), os backlinks reversos deixam de listá-lo e o link interno ganha estilo discreto de destino na lixeira; se o estudo de origem for para a lixeira, seus backlinks deixam de ser listados nos estudos que ele citava.
- **Ciclos e auto-menção**: Um estudo não deve computar backlink para si mesmo se o usuário citar o próprio título dentro do seu texto.
- **Menções múltiplas no mesmo estudo**: Se o estudo A citar o estudo B três vezes no mesmo texto, o painel de backlinks consolida em uma única entrada para o estudo A, permitindo expandir os trechos de contexto sem poluir a lista.
- **Uso em telas móveis**: O menu de autocomplete no mobile adapta-se acima do teclado virtual (`visualViewport`) sem cobrir a área de digitação e os links no leitor respeitam alvos táteis mínimos de $44 \times 44$px.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE disponibilizar autocomplete de menções no editor de estudo disparado pela digitação do prefixo `[[` (ou atalho de toolbar), filtrando dinamicamente estudos do acervo do usuário por título com busca textual rápida.
- **FR-002**: O sistema DEVE suportar a sintaxe `[[Título do Estudo]]` e a sintaxe com desambiguação explícita `[[Título do Estudo|id]]` para diferenciar estudos homônimos.
- **FR-003**: O sistema DEVE persistir e manter atualizada uma tabela relacional dedicada (`study_mentions`) vinculando `source_study_id`, `target_study_id`, `mention_text`, `context_snippet` e `user_id`.
- **FR-004**: A extração e atualização das menções DEVE ocorrer automaticamente no salvamento do estudo (criação e atualização via API), sem exigir ação manual de sincronização.
- **FR-005**: O renderizador de Markdown (`MarkdownContent.vue`) DEVE converter a sintaxe de menção `[[...]]` em links internos com marcação semântica e estilo visual específico de hiperlink do acervo interno.
- **FR-006**: O leitor de estudos (`StudyView.vue`) DEVE apresentar um componente dedicado de Backlinks (`StudyBacklinksList.vue`) posicionado no rodapé da coluna central (abaixo das abas de análise e acima da lista de relações conceituais), exibindo cabeçalho com contador de referências ("Mencionado em X estudos") e cartões expansíveis contendo obra, capítulo e trecho da citação contextual.
- **FR-007**: O sistema DEVE disponibilizar endpoint `GET /api/studies/{study_id}/backlinks` retornando a listagem de estudos de origem, títulos, metadados de obra/capítulo e trecho de contexto.
- **FR-008**: As menções e backlinks DEVEM respeitar estritamente o isolamento multiusuário, impedindo que menções ou backlinks vazem entre contas distintas.
- **FR-009**: O sistema DEVE manter a integridade relacional por ID na tabela `study_mentions`. Caso o estudo alvo seja movido para a lixeira, os backlinks reversos deixam de listá-lo e o link interno no leitor ganha estilo visual discreto indicando destino indisponível/arquivado; caso o estudo alvo seja renomeado, a menção permanece funcional.
- **FR-010**: O painel de backlinks e os links internos DEVEM atender aos critérios de acessibilidade (WAI-ARIA `<nav aria-label="...">`, alvos de clique móveis $\ge 44 \times 44$px) e não conter emojis informais no código.

### Key Entities *(include if feature involves data)*

- **StudyMention**: Registro relacional entre dois estudos, composto por:
  - `id`: Identificador único numérico (PK)
  - `user_id`: UUID do proprietário (FK users)
  - `source_study_id`: ID do estudo onde a menção foi escrita (FK studies)
  - `target_study_id`: ID do estudo que foi referenciado (FK studies)
  - `section`: Seção do estudo de origem onde a menção ocorreu (`summary`, `explanation`, `concepts`, `references`)
  - `mention_text`: Texto exato utilizado na menção
  - `context_snippet`: Trecho contextual em torno da menção (até 180 caracteres)
  - `created_at`: Data e hora de criação
- **BacklinkItem**: Representação de visualização para o leitor contendo metadados consolidados (`source_study_id`, `source_study_title`, `book_id`, `book_title`, `chapter_id`, `chapter_name`, `section`, `context_snippet`, `created_at`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O leitor consegue referenciar qualquer estudo do seu acervo durante a escrita em menos de 3 segundos utilizando o autocomplete disparado por `[[`.
- **SC-002**: 100% das menções válidas salvas em um estudo geram seus respectivos registros em `study_mentions` e tornam-se imediatamente navegáveis no leitor.
- **SC-003**: A consulta de backlinks (`GET /api/studies/{study_id}/backlinks`) responde em menos de 100ms para estudos com dezenas de referências cruzadas.
- **SC-004**: Ao clicar em uma menção interna no leitor, a navegação ocorre de forma instantânea sem recarregar toda a aplicação.
- **SC-005**: A interface atende plenamente às diretrizes de ergonomia móvel (alvos táteis mínimos de $44 \times 44$px) e ao Design System (ausência de emojis residuais).

## Assumptions

- A sintaxe `[[...]]` é compatível com a biblioteca `markdown-it` utilizada pelo sistema, podendo ser estendida via regra de inline parser ou substituição de tokens segura antes/durante a renderização.
- O sistema de relações conceituais de alto nível (`study_relations`) permanece inalterado e autônomo; as menções textuais complementam a rede sem colidir com as relações.
- O acervo opera com SQLite local no modo WAL, mantendo integridade referencial com chaves estrangeiras ativas.
- Todas as operações preservam o isolamento multiusuário das versões 0.5+.
