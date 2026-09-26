# Feature Specification: F07 — Compartilhamento e Permissões por Recurso (ACL)

**Feature Branch**: `034-compartilhamento-permissoes`

**Created**: 2026-09-26

**Status**: Ready for Planning

**Input**: User description: "F07 — Compartilhamento e Permissões por Recurso (ACL): Permitir o compartilhamento granular e seletivo de livros, estudos e dashboards com amigos ou com o público, sob o princípio de estrita segurança em somente-leitura."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Modos Fundamentais de Visibilidade (Privado, Amigos, Público) (Priority: P1)

Como um leitor proprietário de livros e anotações de estudo, desejo definir o nível de visibilidade de cada estudo ou livro entre Privado, Amigos e Público, para que eu possa manter minhas anotações pessoais sob estrito sigilo ou compartilhá-las com meu círculo social de forma simples e segura em modo somente-leitura.

**Why this priority**: Constitui o núcleo funcional essencial (MVP) do compartilhamento de conteúdo na plataforma. Sem os níveis canônicos de visibilidade e a garantia irrestrita de somente-leitura no servidor, nenhum compartilhamento pode ocorrer com segurança.

**Independent Test**: Pode ser testado de forma isolada configurando um estudo como `friends`. Um amigo aceito do proprietário autentica-se e consegue ler o estudo na íntegra, enquanto um terceiro usuário (que não é amigo) recebe resposta 404 (Não Encontrado). Em seguida, ao alterar para `public`, o terceiro usuário passa a ter acesso de leitura. Nenhuma ação de edição (PATCH/PUT/DELETE) é permitida para não-proprietários.

**Acceptance Scenarios**:

1. **Acesso Privado Padrão**:
   - **Given** que um livro ou estudo é criado pelo leitor A;
   - **When** o nível de visibilidade permanece o padrão (`private`);
   - **Then** apenas o leitor A tem permissão de visualizar e consultar o recurso; qualquer outro usuário recebe erro de recurso não encontrado (404), sem vazamento de existência.

2. **Compartilhamento com Amigos (`friends`)**:
   - **Given** que o leitor A define a visibilidade de um estudo como `friends`;
   - **When** o leitor B (que possui vínculo de amizade aceita com A) solicita a visualização do estudo;
   - **Then** o sistema entrega o conteúdo completo do estudo em modo estritamente somente-leitura, com identificação visual do autor (`@username_a`).
   - **And** se o leitor C (que não é amigo de A) tentar acessar o mesmo recurso, recebe 404.

3. **Compartilhamento Público (`public`)**:
   - **Given** que o leitor A define a visibilidade de um estudo como `public`;
   - **When** qualquer leitor autorizado acessa o link direto do estudo;
   - **Then** o sistema exibe o estudo completo em modo de leitura, indicando claramente que se trata de uma obra pública do autor.

4. **Blindagem Estrita de Somente-Leitura**:
   - **Given** que o leitor B está acessando um estudo compartilhado pelo leitor A (seja em modo `friends`, `custom` ou `public`);
   - **When** o leitor B tenta submeter qualquer alteração de dados, adicionar comentários, criar relações no canvas, mudar categorias ou excluir o estudo;
   - **Then** o servidor rejeita sumariamente a operação com `403 Forbidden`, e a interface não apresenta botões de edição ou salvamento para o leitor convidado.

---

### User Story 2 - Permissões Granulares Nominais / ACL Customizada (Priority: P2)

Como um leitor que deseja compartilhar um estudo sensível ou específico apenas com um ou mais amigos selecionados (e não com toda a lista de amigos), quero definir a visibilidade como `custom` e conceder ou revogar nominalmente a permissão de leitura para leitores específicos via `@username`.

**Why this priority**: Atende à necessidade de colaboração seletiva e confidencialidade dirigida entre leitores, permitindo círculos de estudo pontuais sem expor anotações a todos os contatos.

**Independent Test**: O leitor A define o estudo como `custom` e concede acesso nominal a `@leitor_b`. O leitor B consegue visualizar e ler o estudo. O leitor C (mesmo sendo amigo aceito de A) não consegue acessar e recebe 404. O leitor A revoga o acesso de B; o leitor B imediatamente perde o acesso e passa a receber 404.

**Acceptance Scenarios**:

1. **Concessão Nominal por Handle**:
   - **Given** que o leitor A abre o modal de compartilhamento de um estudo e seleciona o modo `custom`;
   - **When** digita o `@username` de um usuário ativo e aciona "Adicionar Leitor";
   - **Then** o leitor é adicionado à lista de permissões ativas daquele estudo e passa a ter acesso imediato de leitura.

2. **Validação de Destinatário Válido**:
   - **Given** que o leitor A tenta adicionar um usuário inexistente ou a si próprio;
   - **When** submete a inclusão na lista;
   - **Then** o sistema valida e bloqueia a ação, apresentando mensagem amigável de erro.

3. **Revogação Instantânea de Permissão**:
   - **Given** que o leitor B consta na lista de permissões nominais de um estudo de A;
   - **When** o leitor A clica no botão de remover/revogar permissão;
   - **Then** o registro de permissão é excluído atonicamente no servidor e o leitor B tem seu acesso revogado de imediato.

---

### User Story 3 - Navegação e Acesso a Recursos "Compartilhados Comigo" (Priority: P3)

Como um leitor que recebeu acesso a livros e anotações compartilhadas por outros colegas de leitura, desejo encontrar facilmente esses recursos em uma visualização organizada na interface, para que eu possa consultar os estudos compartilhados sem precisar guardar links manuais.

**Why this priority**: Garante usabilidade e descobrimento fluido do acervo compartilhado, conectando o ecossistema social ao fluxo de estudo diário.

**Independent Test**: O usuário B acessa a área de recursos compartilhados na interface e visualiza a listagem dos estudos de A aos quais tem acesso (`friends`, `custom` ou `public` de amigos), com indicação do livro, capítulo, autor e data, podendo clicar e abrir o leitor em modo visualização.

**Acceptance Scenarios**:

1. **Listagem Consolidada de Itens Compartilhados**:
   - **Given** que outros leitores compartilharam estudos ou livros com o usuário B;
   - **When** o usuário B navega até a seção de itens compartilhados;
   - **Then** a interface apresenta a lista com cartões descritivos contendo título do estudo, obra de origem, avatar e `@username` do autor original.

2. **Diferenciação Visual entre Acervo Próprio e Conteúdo Convidado**:
   - **Given** que o usuário B abre um estudo compartilhado;
   - **When** o conteúdo é carregado na tela;
   - **Then** um banner informativo ou badge superior indica "Estudo compartilhado por @autor (Modo Leitura)", desabilitando atalhos de teclado de edição e botões de mutação.

---

### User Story 4 - Blindagem Rigorosa contra Bloqueios e Acessos Indevidos (Priority: P4)

Como um leitor que bloqueou outro usuário (ou foi bloqueado por ele), quero ter a certeza absoluta de que nenhum estudo, livro ou anotação minha será acessível para a parte bloqueada, independentemente de o recurso estar configurado como `public`, `friends` ou `custom`.

**Why this priority**: Protege a integridade física e emocional dos usuários, impedindo qualquer forma de acompanhamento indesejado ou evasão de bloqueio.

**Independent Test**: O leitor A possui estudos com visibilidade `public` e `friends`. O leitor A bloqueia o leitor B (ou B bloqueia A). O leitor B tenta acessar qualquer estudo de A via URL direta ou listagem; o servidor retorna `404 Not Found` em todas as tentativas.

**Acceptance Scenarios**:

1. **Invalidação Total de Acesso sob Bloqueio**:
   - **Given** que existe bloqueio ativo entre A e B (em qualquer uma das duas direções);
   - **When** o usuário bloqueado tenta acessar qualquer estudo de A (mesmo configurado como `public`);
   - **Then** o sistema retorna `404 Not Found`, ocultando a existência do recurso.

2. **Impossibilidade de Concessão a Usuários Bloqueados**:
   - **Given** que A e B possuem relação de bloqueio;
   - **When** A tenta conceder permissão nominal a B no modo `custom`;
   - **Then** o sistema rejeita a operação e impede a inclusão.

---

### Edge Cases

- **Exclusão de Estudo Compartilhado**: Quando o proprietário move um estudo compartilhado para a lixeira ou o exclui definitivamente, todas as permissões nominais associadas são limpas em cascata e convidados deixam de acessá-lo imediatamente (404).
- **Desfazimento de Amizade Posterior**: Se A e B deixam de ser amigos, estudos de A configurados como `friends` deixam de ser acessíveis para B de forma automática e instantânea no momento da remoção do vínculo.
- **Conflito de Concorrência ao Compartilhar**: Se o proprietário altera o modo de visibilidade simultaneamente no PC e no celular, a última gravação confirmada no banco SQLite prevalece com versionamento consistente.
- **Herança com Sobrescrita (Override)**: O estudo herda por padrão a visibilidade do livro a que pertence (`inherit`), mas o proprietário pode definir uma visibilidade individual e específica para o estudo (ex.: Livro Privado, mas Estudo X com visibilidade `friends` ou `custom`).
- **Localização na Interface de Compartilhados Comigo**: A visualização de recursos compartilhados com o leitor é centralizada na tela da Biblioteca/Acervo através de uma aba/filtro dedicado "Compartilhados Comigo" (ao lado de "Meu Acervo"), mantendo a experiência de leitura e navegação uniforme.
- **Acesso a Recursos Públicos Restrito a Usuários Autenticados**: Recursos configurados como `public` estão disponíveis para todos os leitores do sistema através de link direto ou busca, mas o acesso exige autenticação no Caderno de Leitura para garantir governança, proteção de conexões do servidor local e auditoria de sessão.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE fornecer os quatro níveis canônicos de visibilidade para recursos de estudo e livros: `private` (privado), `friends` (amigos), `custom` (personalizado por lista de permissões) e `public` (público).
- **FR-002**: O sistema DEVE garantir que qualquer acesso concedido a usuários não-proprietários seja estritamente de somente-leitura (Read-Only), bloqueando qualquer método de escrita (`POST`, `PUT`, `PATCH`, `DELETE`).
- **FR-003**: O sistema DEVE permitir ao proprietário gerenciar permissões nominais para visibilidade `custom`, vinculando o recurso ao identificador de leitores autorizados.
- **FR-004**: O sistema DEVE permitir a busca de leitores pelo handle `@username` durante a concessão nominal no modo `custom`, respeitando a flag `is_discoverable` e as regras de bloqueio.
- **FR-005**: O sistema DEVE revogar imediatamente o acesso a recursos do tipo `friends` caso a amizade entre os usuários seja desfeita ou convertida em bloqueio.
- **FR-006**: O sistema DEVE aplicar blindagem anti-enumeração (retornando `404 Not Found`) para qualquer tentativa de acesso não autorizada ou proveniente de usuário bloqueado.
- **FR-007**: O sistema DEVE disponibilizar um modal de compartilhamento integrado à interface de leitura e ao catálogo do acervo, com controle visual acessível e alvos táteis mínimos de 44x44px.
- **FR-008**: O sistema DEVE disponibilizar endpoints na API para consultar os recursos compartilhados com o leitor autenticado (`GET /api/shared/studies` e `GET /api/shared/books`).
- **FR-009**: O sistema DEVE suportar cópia rápida do link do estudo compartilhado para a área de transferência com feedback tátil e visual ao usuário.
- **FR-010**: O sistema DEVE suportar o modo de visibilidade herdada (`inherit`) em estudos, adotando automaticamente a política de visibilidade do livro associado quando não houver sobrescrita explícita.
- **FR-011**: O sistema DEVE exigir autenticação prévia para acesso a recursos com visibilidade `public`, impedindo acessos anônimos não autenticados.
- **FR-012**: A interface da Biblioteca DEVE disponibilizar uma aba/alternador entre "Meu Acervo" e "Compartilhados Comigo" com suporte a busca, filtros e identificação clara do autor original.

### Key Entities *(include if feature involves data)*

- **ResourceVisibility (Enum)**: Níveis de visibilidade aplicados a entidades do acervo:
  - `private`: Estritamente reservado ao proprietário do recurso.
  - `friends`: Acessível por todos os usuários com amizade aceita (`status == 'accepted'`).
  - `custom`: Acessível pelo proprietário e por usuários nominais registrados na ACL.
  - `public`: Acessível por qualquer leitor autorizado do sistema com o link direto.
- **ResourcePermission (Entidade ACL)**: Tabela de concessões nominais para granularidade `custom`:
  - `id`: Identificador inteiro único.
  - `resource_type`: Tipo do recurso (`study` ou `book`).
  - `resource_id`: Identificador numérico do recurso associado.
  - `granted_to_user_id`: Identificador UUID do usuário beneficiado pela permissão.
  - `created_at`: Data e hora da concessão em UTC.
  - Restrições: Chave única composta `(resource_type, resource_id, granted_to_user_id)` para evitar duplicatas, exclusão em cascata ao deletar usuário ou recurso.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O proprietário consegue alterar a visibilidade de um estudo ou adicionar um amigo à lista de permissões em menos de 3 cliques e com resposta do sistema em menos de 1 segundo.
- **SC-002**: 100% das tentativas de mutação (edição de texto, exclusão, alteração de tags) realizadas por leitores convidados sobre recursos de terceiros são bloqueadas com código de proteção de acesso.
- **SC-003**: 100% das tentativas de acesso por usuários bloqueados a estudos de seu bloqueador resultam em resposta de recurso não encontrado (`404`), sem revelar a existência do material.
- **SC-004**: Ao desfazer uma amizade ou revogar uma permissão, o acesso do leitor convidado é interrompido de imediato, sem persistência indevida de dados em cache no servidor.

---

## Assumptions

- O Caderno de Leitura já conta com base multiusuário (F01), autenticação e sessões seguras (F02) e o sistema bilateral de amizades e bloqueios (F06) em pleno funcionamento.
- A edição colaborativa simultânea (estilo Google Docs ou CRDTs) está fora de escopo para a versão 0.5; todo acesso compartilhado é estritamente de consulta (Read-Only).
- Os recursos compartilhados são visualizados dentro da interface padrão da aplicação, utilizando o mesmo motor de renderização Markdown e tipografia acessível já consolidados.
- A exclusão de um recurso pelo proprietário remove automaticamente suas entradas de permissão sem deixar órfãos no banco de dados.
