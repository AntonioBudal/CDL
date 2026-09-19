# Feature Specification: Edição Completa de Metadados de Livros, Capítulos e Anotações

**Feature Branch**: `002-edicao-livros-estudos`  
**Created**: 2026-09-17  
**Status**: Draft  
**Input**: User description: "Edição completa de metadados de livros, capítulos e anotações existentes"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Edição de Metadados de Livros (Priority: P1) 🎯 MVP

Como leitor e estudante que organiza sua biblioteca pessoal no Caderno de Leitura, desejo editar o título e o autor de um livro previamente cadastrado para corrigir erros de digitação, ajustar a formatação ou complementar dados, garantindo que todos os capítulos e anotações continuem vinculados ao livro.

**Why this priority**: É a necessidade mais frequente e direta na curadoria do acervo. Permite corrigir nomes de obras e autores imediatamente após o cadastro ou importação.

**Independent Test**: Pode ser testado abrindo os detalhes de um livro existente, alterando seu título e autor, salvando e recarregando a página para comprovar a persistência sem afetar os capítulos existentes.

**Acceptance Scenarios**:
1. **Given** um livro existente no acervo com capítulos e estudos associados, **When** o usuário edita seu título e autor para novos valores válidos e confirma, **Then** as alterações são salvas com sucesso, exibidas imediatamente e todos os vínculos com capítulos e estudos permanecem intactos.
2. **Given** o formulário de edição de um livro aberto, **When** o usuário apaga o título deixando o campo em branco e tenta salvar, **Then** o sistema bloqueia o salvamento, exibe mensagem de validação clara e mantém os dados do formulário sem descartar o texto digitado.
3. **Given** a edição de um livro, **When** o usuário cancela a operação ou clica fora sem salvar, **Then** os dados originais são mantidos inalterados.

---

### User Story 2 - Edição e Reordenação de Capítulos (Priority: P2)

Como leitor, desejo alterar o nome de um capítulo existente e ajustar sua sequência ou posição no livro, para que a estrutura do índice reflita fielmente o sumário da obra estudada.

**Why this priority**: Capítulos organizam as leituras e estudos. Poder renomear ou reorganizar capítulos é essencial para corrigir índices incompletos gerados na importação.

**Independent Test**: Pode ser testado selecionando um capítulo existente de um livro, alterando seu nome e sua posição na lista, confirmando e verificando que a listagem de capítulos passa a exibir a nova ordem e nome.

**Acceptance Scenarios**:
1. **Given** um capítulo existente em um livro, **When** o usuário altera o nome do capítulo e confirma, **Then** o novo nome passa a ser exibido no sumário e no cabeçalho dos estudos daquele capítulo.
2. **Given** múltiplos capítulos em um livro, **When** o usuário altera a ordem/posição de um capítulo, **Then** a listagem de capítulos reflete a nova sequência sem duplicar nem perder capítulos.
3. **Given** um formulário de edição de capítulo, **When** o usuário insere um nome composto apenas por espaços, **Then** o sistema impede o salvamento e solicita um nome válido.

---

### User Story 3 - Edição e Refinamento de Estudos e Anotações (Priority: P3)

Como estudante, desejo revisar e atualizar as notas pessoais, o título, a localização e os textos analíticos de um estudo já salvo, com garantia absoluta de que a resposta original importada nunca seja corrompida nem apagada.

**Why this priority**: O aprendizado é iterativo; o leitor frequentemente aprofunda suas anotações dias ou semanas após a primeira leitura.

**Independent Test**: Pode ser testado abrindo a edição de um estudo existente, alterando o texto das anotações pessoais e o resumo, salvando e comprovando que o texto original da IA foi rigorosamente preservado no banco e que as novas anotações persistem após recarregar.

**Acceptance Scenarios**:
1. **Given** um estudo já registrado com notas e resposta de IA original, **When** o usuário altera o título, a localização e suas anotações pessoais e salva, **Then** as novas notas são persistidas e a resposta de origem permanece estritamente idêntica.
2. **Given** a edição de um estudo em andamento com alterações não salvas, **When** o usuário tenta navegar para outra página ou recarregar, **Then** o sistema solicita confirmação para evitar perda acidental do texto digitado.
3. **Given** a edição de um estudo, **When** o usuário limpa todas as quatro seções de análise e tenta salvar sem qualquer conteúdo analítico, **Then** o sistema avisa que ao menos uma seção analítica deve permanecer preenchida e preserva o rascunho.

---

### Edge Cases

- **Conflito de edição entre dispositivos**: O que acontece se o usuário abrir o mesmo estudo no PC e no celular e salvar edições conflitantes? O sistema deve impedir a sobrescrita cega e alertar o usuário.
- **Caracteres especiais e emojis**: Nomes de livros, capítulos e anotações com emojis, aspas tipográficas e caracteres Unicode internacionais devem ser aceitos e persistidos sem distorção.
- **Títulos longos**: Títulos extensos de livros e capítulos não devem quebrar o layout visual da interface nem o formulário de edição.
- **Tentativa de salvar com falha de rede temporária**: Se a conexão oscilar ao clicar em salvar, o formulário deve manter todo o texto digitado acessível para nova tentativa, sem limpar os campos.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE permitir a edição do título e do autor de qualquer livro existente no acervo ativo.
- **FR-002**: O sistema DEVE validar que o título do livro não seja vazio nem composto apenas por espaços em branco (campo obrigatório).
- **FR-003**: O sistema DEVE suportar os seguintes metadados opcionais para livros: autor, subtítulo e ano de publicação (numérico de 4 dígitos).
- **FR-004**: O sistema DEVE permitir renomear qualquer capítulo existente dentro de um livro.
- **FR-005**: O sistema DEVE permitir reordenar a sequência de capítulos de um livro através de controles diretos de subir/descer (▲ / ▼) na listagem de capítulos.
- **FR-006**: O sistema DEVE garantir que a renomeação ou reordenação de capítulos preserve integralmente todos os estudos associados àquele capítulo.
- **FR-007**: O sistema DEVE permitir a edição de título, localização, seções de análise (resumo, explicação, conceitos, referências) e notas pessoais de qualquer estudo existente.
- **FR-008**: O sistema DEVE preservar a resposta original (`source_response`) como somente-leitura imutável durante a edição de estudos.
- **FR-009**: O sistema DEVE proteger contra perda de dados em caso de edição concorrente entre dispositivos, bloqueando o salvamento em caso de conflito de versão, alertando o usuário e preservando o texto digitado intacto no formulário.
- **FR-010**: O sistema DEVE avisar o usuário sobre alterações não salvas antes de abandonar uma tela de edição.
- **FR-011**: Todas as operações de edição DEVEM ser plenamente operáveis por teclado e adaptadas para uso confortável em telas de smartphones.

---

### Key Entities *(include if feature involves data)*

- **Livro (Book)**: Obra registrada no acervo. Possui título, autor e metadados descritivos. Contém um ou mais capítulos vinculados.
- **Capítulo (Chapter)**: Subdivisão temática ou estrutural de um livro. Possui nome, posição numérica na sequência do livro e vínculo direto com o livro pai.
- **Estudo (Study)**: Ficha de anotação e reflexão de leitura. Pertence a um capítulo e contém título, localização na obra, textos de análise, anotações pessoais do leitor e o registro original imutável do assistente.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O leitor consegue editar e salvar o título e autor de um livro em menos de 10 segundos a partir da visualização da obra.
- **SC-002**: 100% dos vínculos de integridade entre livros, capítulos e estudos permanecem intactos após quaisquer operações de edição.
- **SC-003**: 0% de perda da resposta de origem (`source_response`): o texto original importado permanece idêntico após qualquer edição de anotações.
- **SC-004**: Formulários de edição retêm 100% do texto digitado pelo usuário em caso de falha de validação ou erro momentâneo de comunicação.
- **SC-005**: A interface de edição atinge usabilidade total em telas móveis e navegação por teclado (foco e atalhos claros).

---

## Assumptions

- O acervo continuará operando em modo monousuário com servidor local, servindo o PC e dispositivos na rede privada/Tailscale.
- A exclusão de livros e estudos não faz parte desta fatia, pois depende da implementação da Lixeira / Soft Delete (T02) para evitar exclusões destrutivas prematuras.
- A edição de estudos já possui fluxo parcial funcional na versão 0.2 (`StudyEditView.vue` e `PATCH /studies/{id}`), que será consolidado e harmonizado com a edição de livros e capítulos.
