# Feature Specification: F0.6.2 — Seleção e Ações Contextuais

**Feature Branch**: `041-selecao-acoes-contextuais`

**Created**: 2026-09-27

**Status**: Complete

**Input**: User description: "F0.6.2 — Seleção e Ações Contextuais: Permitir que o usuário selecione qualquer trecho do estudo no leitor e encontre ações relevantes diretamente no contexto daquele trecho através de uma barra flutuante (floating toolbar) discreta, sem comandos especiais ou ferramentas permanentemente visíveis, suportando ações como destacar (marca-texto), criar anotação, transformar em citação, ocultar trecho e transformar em pergunta, com ancoragem robusta e persistência no SQLite."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Seleção Textual Fluida e Barra Flutuante Contextual (Priority: P1)

Como estudante lendo um fichamento no Leitorum, desejo selecionar qualquer frase ou trecho do texto com o mouse ou toque e ver surgir uma barra flutuante contextual próxima à seleção com ações relevantes, para que eu possa interagir com o texto sem desviar o olhar nem procurar botões em barras de ferramentas fixas.

**Why this priority**: É o alicerce fundamental de interação da feature (o conceito `Selecionar → Escolher ação → Pronto`). Sem a captura confiável da seleção e a exibição acessível da barra contextual, nenhuma ação secundária pode ocorrer.

**Independent Test**: Abrir a tela de leitura de um estudo (`StudyView.vue`), selecionar com o cursor um trecho de texto em qualquer seção e verificar que a barra flutuante contextual é posicionada de forma estável acima ou abaixo do trecho selecionado, desaparecendo ao clicar fora ou desselecionar.

**Acceptance Scenarios**:

1. **Given** um leitor visualizando um estudo na tela de leitura, **When** selecionar um trecho de texto com mais de 2 caracteres em qualquer uma das seções, **Then** uma barra flutuante com ações contextuais surge suavemente adjacente à seleção.
2. **Given** a barra flutuante aberta sobre um trecho selecionado, **When** o usuário clicar em qualquer área fora da barra ou desmarcar a seleção (ou pressionar `Escape`), **Then** a barra desaparece imediatamente sem deixar resíduos visuais.
3. **Given** uma seleção feita próximo às bordas da janela (topo, base ou laterais), **When** a barra for calculada, **Then** seu posicionamento se ajusta automaticamente para permanecer 100% visível dentro do viewport sem ser cortada.

---

### User Story 2 - Destacar Trechos (Marca-Texto) com Persistência Confiável (Priority: P1) 🎯 MVP

Como estudante, desejo selecionar um trecho do estudo e clicar em "Destacar" para marcar visualmente aquela passagem (com cor de destaque suave e legível), com a garantia de que esse destaque ficará salvo no meu acervo e continuará visível nas próximas vezes que eu abrir o estudo.

**Why this priority**: O marca-texto é a ação de estudo mais universal e frequente. Proporciona valor imediato ao leitor, estabelece o modelo de ancoragem de trechos e valida a persistência no banco SQLite.

**Independent Test**: Selecionar uma frase de um estudo, clicar em "Destacar", recarregar a página ou navegar para outro livro e voltar, confirmando que a frase permanece destacada e que um clique no trecho marcado permite remover o destaque.

**Acceptance Scenarios**:

1. **Given** um trecho de texto selecionado no leitor, **When** o usuário clicar na ação "Destacar" da barra flutuante, **Then** o trecho recebe formatação visual de marca-texto e a barra flutuante é fechada.
2. **Given** um estudo contendo trechos destacados, **When** a página for recarregada ou acessada em outro dispositivo/sessão, **Then** os trechos continuam fielmente destacados nos mesmos pontos do texto.
3. **Given** um trecho já destacado, **When** o usuário clicar sobre ele, **Then** um menu de contexto rápido é aberto permitindo remover o destaque ("Remover marcação") ou alterar sua cor.

---

### User Story 3 - Criar Anotação ou Citação Conectada ao Trecho (Priority: P2)

Como estudante e pesquisador, desejo selecionar uma passagem expressiva do texto e transformá-la em uma citação com reflexão própria ou vincular uma anotação explicativa diretamente àquele trecho, para que meus pensamentos fiquem ancorados na evidência textual do estudo.

**Why this priority**: Aprofunda o estudo crítico e a criação de notas marginais, permitindo conectar a voz do autor às interpretações do leitor sem fragmentar o documento.

**Independent Test**: Selecionar um trecho, acionar "Anotar" na barra flutuante, digitar uma reflexão pessoal no popover/modal e verificar que o trecho recebe um indicador visual discreto que, ao ser clicado, exibe a anotação correspondente.

**Acceptance Scenarios**:

1. **Given** um trecho selecionado, **When** o leitor clicar em "Anotar", **Then** um campo de entrada focado é aberto permitindo redigir uma nota associada àquele trecho.
2. **Given** uma anotação salva para o trecho, **When** o usuário ler o estudo, **Then** um marcador lateral ou sublinhado discreto sinaliza a presença da anotação, abrindo o conteúdo da nota ao passar o cursor ou tocar.
3. **Given** a opção "Copiar como citação", **When** acionada, **Then** o trecho selecionado é copiado para a área de transferência formatado com aspas e metadados do livro/capítulo para fácil referência externa.

---

### User Story 4 - Leitura Ativa: Ocultar Trecho e Transformar em Pergunta (Priority: P2)

Como estudante revisando a matéria, desejo poder ocultar temporariamente partes cruciais de um trecho selecionado (modo oclusão/revelação) ou transformá-lo em uma pergunta de estudo para testar minha retenção antes de ver a resposta.

**Why this priority**: Conclui o rol completo das 5 ações contextuais interativas do leitor, viabilizando o estudo ativo direto no texto sem exigir ferramentas ou telas secundárias separadas.

**Independent Test**: Selecionar um conceito no texto, escolher "Ocultar" e verificar que o trecho se transforma em um bloco clicável `[Revelar]` que mostra a resposta ao clique.

**Acceptance Scenarios**:

1. **Given** um trecho selecionado, **When** o leitor acionar "Ocultar trecho", **Then** o texto selecionado é visualmente protegido por uma barra de oclusão com botão de revelar.
2. **Given** um trecho em modo oclusão, **When** o estudante clicar em "Revelar", **Then** o texto original reaparece suavemente.
3. **Given** a ação "Transformar em pergunta", **When** configurada uma pergunta para o trecho, **Then** a pergunta é exibida sobre o texto original, que permanece escondido até o leitor solicitar a exibição.

---

### Edge Cases

- **Seleções multilinhas e através de formatação Markdown**: A seleção pode começar no meio de um parágrafo normal e terminar dentro de um bloco em negrito ou itálico (`**termo**`). O mecanismo de ancoragem deve calcular offsets de texto puro (text nodes) ou posições estáveis sem quebrar a árvore DOM renderizada.
- **Seleções vazias, espaços em branco ou pontuações isoladas**: Se o usuário selecionar apenas espaços ou quebras de linha acidentais, a barra flutuante não deve ser exibida.
- **Conflito de menus no Mobile/Touch**: Em dispositivos móveis (Android/iOS), a seleção nativa dispara o menu do sistema ("Copiar", "Compartilhar"). A barra flutuante do Leitorum deve se posicionar de forma ergonômica (ex.: acima da seleção ou barra fixa na base) para não conflitar com a seleção nativa.
- **Edição posterior do estudo**: Caso o usuário edite o texto da seção posteriormente e altere a contagem de caracteres, o sistema deve tolerar desvios ou tentar re-ancorar por correspondência de texto exato (`selected_text`) e contexto vizinho, evitando quebrar o carregamento do estudo.
- **Sobreposição de múltiplos destaques no mesmo trecho**: Se o usuário tentar destacar uma frase que já contém uma palavra destacada, o sistema deve mesclar ou priorizar o destaque mais recente de forma elegante.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE capturar eventos de seleção textual na área de leitura de estudos (`StudyView.vue`) utilizando a Selection API e Range API nativas do navegador.
- **FR-002**: O sistema DEVE renderizar uma barra flutuante contextual (`FloatingActionsToolbar`) sempre que uma seleção válida (texto não vazio com ao menos 2 caracteres significativos) for efetuada pelo leitor.
- **FR-003**: A barra flutuante DEVE ser posicionada dinamicamente adjacente à caixa delimitadora da seleção (`getBoundingClientRect`), com compensação automática para não extrapolar as bordas do viewport.
- **FR-004**: A barra flutuante DEVE ser ocultada automaticamente e a seleção liberada sempre que o usuário clicar fora da barra, desselecionar o texto ou pressionar a tecla `Escape`.
- **FR-005**: O sistema DEVE disponibilizar na barra flutuante ações contextuais imediatas:
  - Destacar (marca-texto visual com seletor de paleta de cores suaves);
  - Anotar (adicionar nota reflexiva vinculada ao trecho);
  - Copiar como citação (formatação de citação com metadados do estudo para área de transferência);
  - Ocultar trecho (bloqueio visual de oclusão com botão de revelar sob demanda);
  - Transformar em pergunta (substituição visual por pergunta de estudo ativo);
  - Limpar/Remover marcação (quando acionado sobre um destaque ou elemento contextual existente).
- **FR-006**: O sistema DEVE persistir os trechos destacados e anotados no banco de dados SQLite associados ao identificador do estudo (`study_id`).
- **FR-007**: A entidade de persistência do trecho DEVE armazenar a seção de origem (`summary`, `explanation`, `concepts`, `references`, `source_response`), o texto selecionado literal (`selected_text`), a cor de destaque, o tipo de ação (`highlight`, `note`, `quote`, `question`, `hidden`) e os metadados de ancoragem posicional.
- **FR-008**: Ao carregar um estudo para leitura, o sistema DEVE recuperar todos os trechos associados e renderizá-los sobre o conteúdo das seções de forma não destrutiva, mantendo a integridade do Markdown original.
- **FR-009**: O sistema DEVE permitir a remoção ou edição de um destaque existente com um único clique ou toque sobre a marcação.
- **FR-010**: O sistema DEVE garantir que todas as operações e dados de destaques e anotações sejam estritamente locais e privados, em estrita conformidade com o Artigo I da Constituição do Projeto.
- **FR-011**: O sistema DEVE persistir os trechos através de uma tabela relacional dedicada no SQLite (`study_highlights`), armazenando identificador da seção, `start_offset`, `end_offset`, `selected_text` literal e cor, preservando o Markdown original do estudo 100% limpo e permitindo re-ancoragem tolerante a edições posteriores por correspondência textual exata.
- **FR-012**: O sistema DEVE implementar todas as 5 ações completas na barra flutuante (Destacar, Anotar, Citar, Ocultar trecho e Transformar em pergunta) de ponta a ponta na entrega desta feature, fornecendo a experiência interativa completa de estudo no texto.
- **FR-013**: O sistema DEVE adaptar dinamicamente a apresentação da barra contextual de acordo com a viewport/dispositivo: barra flutuante posicionada diretamente adjacente à seleção no Desktop (cursor) e painel ancorado na base da tela (*bottom sheet* / barra de ação fixa) em telas sensíveis ao toque / mobile (< 768px), prevenindo sobreposição com o menu de seleção nativo do sistema operacional.

### Key Entities *(include if feature involves data)*

- **StudyHighlight** (ou `StudySnippetAnnotation`):
  - `id`: Inteiro ou UUID (Chave Primária)
  - `study_id`: Inteiro (Chave Estrangeira para `studies.id`)
  - `user_id`: Inteiro/UUID (Identificador do autor do destaque)
  - `section`: String (`summary`, `explanation`, `concepts`, `references`, `source_response`)
  - `start_offset`: Inteiro (Índice de início do caractere no texto puro da seção)
  - `end_offset`: Inteiro (Índice de término do caractere no texto puro da seção)
  - `selected_text`: Texto (Conteúdo literal da passagem selecionada para re-ancoragem segura)
  - `color`: String (Identificador da cor da paleta: ex.: `yellow`, `green`, `blue`, `pink`)
  - `kind`: String/Enum (`highlight`, `note`, `quote`, `question`, `hidden`)
  - `note`: Texto (Anotação pessoal ou pergunta associada, opcional)
  - `created_at` / `updated_at`: DateTime UTC

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A barra flutuante contextual deve surgir e estar pronta para interação em menos de 80 milissegundos após o término da seleção pelo leitor.
- **SC-002**: 100% dos destaques criados devem ser restaurados e renderizados corretamente no estudo após o recarregamento da página ou navegação.
- **SC-003**: A barra flutuante deve permanecer 100% contida dentro do viewport visível em 100% dos testes de seleção em bordas de tela.
- **SC-004**: O tempo de resposta ao acionar a remoção de um destaque deve ser instantâneo na interface (< 50ms) com sincronização em segundo plano no SQLite.
- **SC-005**: Em dispositivos móveis, todos os botões da barra flutuante devem ter alvos de toque mínimos de 44x44 pixels para garantir acessibilidade física.

## Assumptions

- O texto base do estudo continua organizado nas 4 seções conceituais canônicas (`summary`, `explanation`, `concepts`, `references`).
- Os destaques são de propriedade exclusiva do leitor proprietário do estudo, com preservação de privacidade e sem compartilhamento público sem permissão explícita.
- A renderização dos destaques deve ser compatível com os 10 temas visuais canônicos e as 5 superclasses de movimento do sistema.
