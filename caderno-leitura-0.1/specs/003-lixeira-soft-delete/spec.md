# Feature Specification: Lixeira e Restauração de Itens (Soft Delete)

**Feature Branch**: `003-lixeira-soft-delete`  
**Created**: 2026-09-18  
**Status**: Draft  
**Input**: User description: "T02 — Lixeira e restauração de itens: soft delete com timestamp para livros, estudos e capítulos, tela de lixeira e exclusão definitiva consciente"

---

## Clarifications

### Session 2026-09-18

- Q: Como o sistema deve tratar o descarte de capítulos na interface e no modelo de dados? (FR-010) → A: Descarte no nível do Livro e do Estudo; capítulos acompanham o ciclo do livro pai sem lixeira própria.
- Q: Ao restaurar um estudo cujo livro ancestral também se encontra na lixeira, como o sistema deve se comportar? (FR-011) → A: Restauração em cascata ascendente automática; reativa o livro pai e respectivo capítulo juntamente com o estudo.
- Q: Qual deve ser a política de retenção temporal para os itens enviados para a lixeira? (FR-012) → A: Purga automática após 30 dias; registros que estejam na lixeira há mais de 30 dias são expurgados permanentemente pelo sistema.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Envio para a Lixeira e Proteção contra Exclusão Acidental (Priority: P1) 🎯 MVP

Como leitor e estudante que organiza seu acervo no Caderno de Leitura, desejo poder mover livros inteiros ou estudos específicos para uma lixeira através da interface, garantindo que itens descartados deixem de poluir o acervo ativo imediatamente, mas sem o risco de perda irrevogável ou acidental de anotações e conteúdos valiosos.

**Why this priority**: É a proteção fundamental contra perda de dados do usuário ao organizar o acervo. A exclusão segura (soft delete) substitui qualquer exclusão destrutiva direta e desbloqueia o botão de descarte na interface de leitura e edição.

**Independent Test**: Pode ser testado abrindo o menu de ações de um livro ou de um estudo ativo, selecionando "Mover para a Lixeira", confirmando a ação e verificando que o item desaparece imediatamente da tela inicial, do índice e das buscas normais, enquanto seus registros continuam íntegros no banco de dados.

**Acceptance Scenarios**:
1. **Given** um livro ativo com capítulos e estudos no acervo, **When** o usuário aciona a opção "Mover para a Lixeira" e confirma, **Then** o livro e todos os seus estudos deixam de ser listados na página principal e no acervo ativo.
2. **Given** um estudo ativo em um capítulo, **When** o usuário seleciona "Mover para a Lixeira" neste estudo, **Then** apenas esse estudo específico é ocultado da visualização do capítulo, mantendo o livro, o capítulo e os demais estudos ativos intactos.
3. **Given** um livro ou estudo que se encontra na lixeira, **When** o usuário tenta acessá-lo por URL direta de leitura ou edição, **Then** o sistema não permite a edição do conteúdo e exibe um aviso informando que o item está na lixeira.
4. **Given** uma tentativa de mover um item para a lixeira, **When** o usuário cancela a confirmação no modal, **Then** nenhuma alteração é feita e o item continua perfeitamente visível e ativo.

---

### User Story 2 - Visualização da Lixeira e Restauração de Itens (Priority: P2)

Como leitor, desejo acessar uma tela dedicada de "Lixeira" para consultar todos os itens previamente descartados e restaurar qualquer livro, capítulo ou estudo de volta ao acervo ativo quando desejar reutilizá-lo.

**Why this priority**: O soft delete só entrega seu valor completo se o usuário puder inspecionar o que descartou e recuperar itens facilmente sem depender de intervenções manuais no banco de dados.

**Independent Test**: Pode ser testado navegando até a página da Lixeira, localizando um livro ou estudo descartado, clicando no botão "Restaurar" e confirmando que o item reaparece imediatamente na sua localização original no acervo ativo com todos os seus vínculos, textos e metadados intactos.

**Acceptance Scenarios**:
1. **Given** a existência de itens descartados, **When** o usuário abre a página da Lixeira, **Then** todos os livros e estudos na lixeira são listados de forma clara, indicando título, tipo de item (Livro ou Estudo), data/hora de descarte e localização original.
2. **Given** um livro descartado na lixeira, **When** o usuário clica em "Restaurar", **Then** o livro e seus estudos filhos voltam a ser exibidos normalmente no acervo ativo (com exceção de estudos que já haviam sido descartados individualmente antes do livro).
3. **Given** um estudo descartado individualmente cujo livro ou capítulo também está na lixeira, **When** o usuário solicita a restauração desse estudo, **Then** o sistema restaura o estudo e reativa automaticamente em cascata ascendente o livro e o respectivo capítulo no acervo ativo.
4. **Given** um item restaurado com sucesso, **When** o usuário recarrega a página ou acessa pelo celular, **Then** o item permanece ativo e a lixeira não o lista mais.

---

### User Story 3 - Exclusão Definitiva Consciente e Esvaziamento da Lixeira (Priority: P3)

Como leitor, desejo poder expurgar permanentemente itens selecionados da lixeira ou esvaziar toda a lixeira em definitivo quando tiver certeza absoluta de que não preciso mais deles, mantendo o banco de dados limpo e sem resíduos indesejados.

**Why this priority**: Fecha o ciclo de vida dos dados, permitindo a exclusão física deliberada e informada após o período de quarentena na lixeira.

**Independent Test**: Pode ser testado selecionando um item específico na lixeira (ou o botão "Esvaziar Lixeira"), confirmando o aviso enfático de destruição irreversível, e verificando que o registro é completamente removido de forma atômica, sem deixar referências órfãs e sem afetar nenhum item ativo.

**Acceptance Scenarios**:
1. **Given** um item listado na lixeira, **When** o usuário clica em "Excluir Definitivamente", **Then** o sistema apresenta um diálogo de confirmação claro ressaltando que a ação é irreversível.
2. **Given** a confirmação da exclusão definitiva de um livro, **When** a ação é processada, **Then** o livro, seus capítulos e estudos associados são permanentemente removidos em uma única transação atômica, garantindo integridade referencial.
3. **Given** múltiplos itens na lixeira, **When** o usuário aciona "Esvaziar Lixeira" e confirma, **Then** todos os itens atualmente descartados são definitivamente expurgados, mantendo o acervo ativo completamente intacto.
4. **Given** registros presentes na lixeira há mais de 30 dias, **When** a rotina de purga automática é executada pelo sistema, **Then** esses registros antigos são permanentemente expurgados de forma atômica e segura.

---

### Edge Cases

- **Descarte em cascata vs. restauração seletiva**: Se o Usuário descartou o Estudo A de um Livro L, e dias depois descartou o Livro L inteiro; ao restaurar o Livro L, o Estudo A NÃO deve ser ressuscitado silenciosamente, permanecendo na lixeira até ser restaurado individualmente.
- **Conflito de descarte e edição concorrente**: Se o usuário tem uma aba aberta editando um estudo e, em outra aba ou dispositivo, o livro pai é movido para a lixeira, ao tentar salvar a edição o sistema deve alertar que o item foi descartado e não aplicar alterações até a restauração.
- **Acesso direto via rotas da API ou navegação manual**: Requisições de leitura direta (`/api/books/{id}`, `/api/studies/{id}`) por padrão devem ignorar itens descartados (retornando 404), exceto se consultados por rotas dedicadas de inspeção da lixeira.
- **Capítulos e descarte**: Capítulos não possuem lixeira independente. Para reorganizar anotações de um capítulo sem descartar o livro, o leitor move os estudos para outro capítulo ativo. Ao descartar um livro, todos os seus capítulos e estudos são ocultados juntos.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE utilizar um campo de data/hora anulável com fuso horário documentado (UTC) para marcar a exclusão lógica (*soft delete*) de registros, em vez de flags booleanas simples.
- **FR-002**: O sistema DEVE suportar soft delete para Livros e Estudos (anotações), garantindo que itens marcados como excluídos sejam automaticamente filtrados de todas as consultas normais de acervo, listagens, buscas e estatísticas.
- **FR-003**: O descarte de um livro DEVE ocultar automaticamente todos os seus capítulos e estudos subordinados do acervo ativo.
- **FR-004**: A restauração de um livro DEVE reativar o livro e seus estudos subordinados, EXCETO aqueles estudos que foram enviados para a lixeira em data/hora anterior ao descarte do livro.
- **FR-005**: O sistema DEVE fornecer uma tela de Lixeira na interface permitindo ao usuário filtrar/visualizar os itens descartados, com ações para "Restaurar" e "Excluir Definitivamente".
- **FR-006**: A exclusão definitiva DEVE ser uma operação transacional atômica e distinta, exigindo confirmação explícita na interface para prevenir perda involuntária.
- **FR-007**: A exclusão definitiva de um livro DEVE remover em cascata controlada todos os seus capítulos e estudos associados, sem violar restrições de chave estrangeira (`PRAGMA foreign_keys = ON`).
- **FR-008**: O sistema DEVE manter os identificadores primários (`id`) inalterados ao restaurar itens da lixeira, preservando qualquer vínculo ou histórico prévio.
- **FR-009**: As rotas de backup existentes e futuras DEVEM continuar arquivando o banco integralmente, incluindo registros ativos e itens da lixeira.
- **FR-010**: Capítulos NÃO possuem ação independente de envio para a lixeira; eles acompanham o ciclo de vida do livro pai, sendo ocultados e reativados em conjunto com o livro.
- **FR-011**: A restauração de um estudo cujo livro pai esteja na lixeira DEVE reativar automaticamente em cascata ascendente o livro pai e o respectivo capítulo no acervo ativo.
- **FR-012**: O sistema DEVE aplicar política de purga automática para itens na lixeira, expurgando permanentemente registros cuja data de descarte (`deleted_at`) tenha mais de 30 dias (calculado em UTC).

---

### Key Entities *(include if feature involves data)*

- **Livro (Book)**: Representa a obra cadastrada no acervo. Ganha registro temporal de descarte (`deleted_at`), permitindo determinar se está no acervo ativo ou na lixeira.
- **Capítulo (Chapter)**: Subdivisão de organização de um livro. Relaciona-se com o livro pai e os estudos subordinados.
- **Estudo (Study)**: Registro de anotações, notas pessoais e análise textual. Ganha registro temporal de descarte (`deleted_at`), permitindo descarte individual ou derivado do livro.
- **Item de Lixeira (TrashItem / Visão de Interface)**: Projeção unificada de livros e estudos excluídos para exibição na tela de Lixeira, contendo metadados de identificação, tipo, título, data de exclusão e contexto hierárquico.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Ao enviar um livro ou estudo para a lixeira, o item desaparece da visualização do acervo ativo em menos de 1 segundo, sem necessidade de reiniciar a aplicação ou recarregar a página manualmente.
- **SC-002**: 100% dos dados, formatações de anotações e relacionamentos são preservados intactos ao restaurar qualquer item da lixeira.
- **SC-003**: 100% das operações de exclusão definitiva ocorrem dentro de transação atômica, garantindo zero registros órfãos ou inconsistências de chaves estrangeiras.
- **SC-004**: Nenhum item marcado como excluído aparece em buscas de acervo, listagens de estudos ativos ou contadores da tela inicial.
- **SC-005**: Toda ação de descarte e exclusão definitiva na interface possui confirmação prévia para evitar cliques acidentais em dispositivos móveis ou teclado.

---

## Assumptions

- O Caderno de Leitura continuará operando como instância única local e privada (sem autenticação multiusuário).
- A convenção de data e hora para marcação de descarte utilizará UTC no backend, convertida para o fuso horário local do leitor no navegador.
- Registros na lixeira são mantidos por até 30 dias antes do expurgo automático, a menos que sejam restaurados ou excluídos manualmente antes desse prazo.
- Backups automáticos e manuais gerados pelo sistema abrangem tanto itens ativos quanto itens na lixeira, assegurando que nada seja perdido em cópias de segurança.
