# Feature Specification: F0.6.3 — Leitura Ativa

**Feature Branch**: `042-leitura-ativa`  
**Created**: 2026-09-27  
**Status**: Draft  
**Input**: User description: "Transformar partes do próprio fichamento em pequenas interações de estudo (active recall / leitura ativa), sem criar um sistema separado de flashcards. O texto continua sendo o centro soberano da experiência com revelação sob demanda, perguntas contextuais e controles de revisão no próprio leitor."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Sessão de Leitura Ativa Integrada ao Fichamento (Priority: P1) 🎯 MVP

Como estudante ou pesquisador revisando um livro ou artigo, quero ativar a barra de Leitura Ativa no próprio leitor do estudo para que todos os trechos de retenção fiquem inicialmente mascarados, permitindo que eu teste minha memória no contexto real da leitura sem recorrer a uma tela paralela de flashcards.

**Why this priority**: É a essência do conceito de estudo ativo do Leitorum. Preserva o texto como centro soberano, permitindo que a retenção aconteça no fluxo natural da argumentação sem fragmentar o raciocínio.

**Independent Test**: Abrir um estudo que contenha trechos ocluídos ou perguntas, acionar o controle de "Leitura Ativa", verificar a ocultação simultânea de todos os trechos com máscaras táteis e a possibilidade de restaurar a visualização padrão com "Revelar todos".

**Acceptance Scenarios**:
1. **Given** um estudo aberto com 3 trechos marcados como oclusão e 2 perguntas, **When** o usuário clica em "Modo Leitura Ativa", **Then** uma barra superior de revisão ativa se torna visível, todas as oclusões assumem o estado oculto e as respostas das perguntas ficam escondidas.
2. **Given** a barra de Leitura Ativa ativa, **When** o usuário clica em "Revelar todos", **Then** todas as oclusões e respostas são exibidas simultaneamente sem recarregar a página.
3. **Given** a barra de Leitura Ativa ativa, **When** o usuário clica em "Ocultar todos", **Then** todos os trechos voltam a ficar mascarados para uma nova rodada de verificação.

---

### User Story 2 - Interação Pontual de Revelação e Oclusão no Fluxo Textual (Priority: P1)

Como leitor, ao me deparar com uma passagem ocluída ou uma pergunta contextual enquanto leio um parágrafo do fichamento, quero poder revelar pontualmente o conteúdo ou a resposta com um único toque ou clique para verificar se acertei a dedução mental.

**Why this priority**: Permite o feedback imediato da aprendizagem ativa (active recall). O usuário tenta recordar o termo ou conceito antes de confirmar a resposta.

**Independent Test**: Clicar no botão `[Revelar]` de um trecho específico; constatar que apenas aquele trecho se torna legível, enquanto os demais permanecem preservados; clicar em `[Ocultar]` e verificar o retorno ao estado mascarado.

**Acceptance Scenarios**:
1. **Given** um trecho oculto no meio de um parágrafo, **When** o usuário clica ou toca no botão `[Revelar]`, **Then** o texto mascarado é imediatamente legível com destaque suave e o rótulo do botão alterna para `[Ocultar]`.
2. **Given** um trecho revelado, **When** o usuário clica em `[Ocultar]`, **Then** o trecho volta ao estado mascarado e o botão retorna para `[Revelar]`.
3. **Given** uma caixa de pergunta contextual com resposta escondida, **When** o usuário aciona `[Ver resposta]`, **Then** a resposta é exibida logo abaixo da pergunta e o botão alterna para `[Esconder resposta]`.

---

### User Story 3 - Contador de Progresso e Navegação entre Trechos Interativos (Priority: P2)

Como estudante revisando um estudo longo, quero ver quantos trechos interativos já testei na sessão atual e conseguir saltar diretamente de um trecho para o próximo usando teclado ou botões de navegação, sem precisar rolar manualmente a tela inteira procurando passagens marcadas.

**Why this priority**: Garante fluidez e produtividade em estudos com centenas de linhas e múltiplos trechos interativos, evitando que pontos-chave sejam esquecidos durante a revisão.

**Independent Test**: Na barra de Leitura Ativa, verificar o contador "0 de 4 revisados", clicar em "Próximo trecho" e constatar que a rolagem suave posiciona o próximo trecho no centro do campo visual, com foco acessível.

**Acceptance Scenarios**:
1. **Given** a barra de Leitura Ativa ativada em uma seção com 5 trechos interativos, **When** a seção é iniciada, **Then** o indicador exibe `0 de 5 revisados (0%)`.
2. **Given** o usuário revela o primeiro trecho interativo, **Then** o indicador atualiza para `1 de 5 revisados (20%)`.
3. **Given** múltiplos trechos interativos distribuídos na seção, **When** o usuário clica no botão "Próximo" ou pressiona a tecla de atalho de próximo item, **Then** a visualização rola suavemente até o próximo trecho e aplica anel de foco.
4. **Given** o último trecho interativo alcançado, **When** o usuário clica em "Próximo", **Then** a navegação retorna ciclicamente ao primeiro ou indica conclusão da rodada.

---

### User Story 4 - Prática de Leitura Ativa em Estudos Compartilhados (Priority: P3)

Como leitor convidado com acesso somente leitura a um estudo compartilhado por um colega ou professor, quero poder utilizar todos os recursos da Leitura Ativa (ocultar, revelar, navegar) para exercitar minha retenção, sem que minhas ações modifiquem os dados ou removam os destaques originais do autor.

**Why this priority**: Democratiza o aprendizado colaborativo e permite o uso pedagógico dos estudos compartilhados no Leitorum.

**Independent Test**: Fazer login com usuário convidado sem permissão de edição, abrir um estudo compartilhado, acionar a Leitura Ativa e verificar funcionamento idêntico da revisão, sem permitir alteração permanente do conteúdo.

**Acceptance Scenarios**:
1. **Given** um usuário visualizando um estudo compartilhado em modo somente leitura (`canEdit = false`), **When** o usuário clica no botão de Leitura Ativa, **Then** a barra de ferramentas de estudo ativo abre normalmente.
2. **Given** o usuário convidado revela trechos e completa a revisão, **When** a página é recarregada, **Then** o estudo é recarregado sem corrupção e os dados salvos pelo proprietário permanecem intactos.

---

### Edge Cases

- **Estudo sem nenhum trecho interativo**: O botão ou acionamento de Leitura Ativa deve exibir estado informativo amigável ("Nenhum trecho oculto ou pergunta cadastrada neste estudo. Selecione um texto para criar oclusões ou perguntas.") sem travar a interface.
- **Alternância entre abas da análise (Resumo, Explicação, Conceitos, Referências)**: Ao trocar de aba, o contador de progresso e os trechos rastreados devem se atualizar para a aba atualmente em foco.
- **Impressão ou exportação durante a Leitura Ativa**: Ao exportar ou imprimir, todos os trechos devem ser renderizados revelados por padrão para não emitir documentos com texto borrado ou botões operacionais.
- **Telas móveis compactas**: Os controles de revisão (progresso, botões Próximo/Anterior, Ocultar/Revelar Todos) devem se adaptar a telas menores que 768px sem cobrir o texto da leitura.
- **Modos de alto contraste e tema E-Ink**: A oclusão em tema E-Ink deve utilizar preenchimento sólido sem gradientes ou filtros de desfoque, mantendo total legibilidade e foco tátil.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE fornecer um acionador dedicado "Leitura Ativa" nas ferramentas do leitor de estudo.
- **FR-002**: Ao ativar a Leitura Ativa, o sistema DEVE exibir um painel contextual de sessão contendo: status da rodada, progresso numérico de trechos revisados, botões de ação em massa ("Ocultar todos" e "Revelar todos") e navegação sequencial ("Anterior" e "Próximo").
- **FR-003**: Cada trecho configurado como oclusão (`hidden`) DEVE conter um botão tátil e acessível de revelação pontual que alterna entre os estados revelado e oculto.
- **FR-004**: Cada trecho configurado como pergunta (`question`) DEVE apresentar o enunciado da pergunta no fluxo do texto e manter o bloco de resposta oculto até o acionamento explícito de visualização.
- **FR-005**: A revelação ou oclusão de trechos durante a sessão de Leitura Ativa NÃO DEVE alterar o conteúdo salvo no banco de dados nem o texto Markdown do estudo.
- **FR-006**: O sistema DEVE calcular dinamicamente o total de trechos interativos da seção ativa e a quantidade de trechos já revelados na sessão atual.
- **FR-007**: O sistema DEVE permitir a navegação por teclado entre os trechos interativos (tecla Tab e atalhos configurados de próximo/anterior).
- **FR-008**: O sistema DEVE permitir o encerramento do modo de Leitura Ativa a qualquer momento, restaurando a visualização padrão de leitura.
- **FR-009**: O recurso de Leitura Ativa DEVE estar plenamente operacional tanto para o proprietário do estudo quanto para usuários com permissão somente leitura.
- **FR-010**: A interface da Leitura Ativa DEVE respeitar os 10 temas visuais do Leitorum, incluindo adaptações específicas para o tema E-Ink e temas escuros.

---

### Key Entities

- **Trecho Interativo (Active Study Node)**: Representação em memória de uma passagem marcada no estudo como oclusão (`hidden`) ou pergunta (`question`), vinculada à seção correspondente, com estado transitório de revelação (`is_revealed: boolean`) e posição visual no documento.
- **Sessão de Leitura Ativa (Active Reading Session)**: Estado efêmero da sessão de estudo no leitor, contendo a lista de trechos interativos da aba ativa, o índice do trecho focado, a contagem de trechos revelados e os controles de exibição em massa.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O usuário consegue ativar o modo de Leitura Ativa e ter todos os trechos mascarados em menos de 1 segundo após o clique.
- **SC-002**: A revelação ou oclusão de qualquer trecho responde em menos de 100 milissegundos sem qualquer salto de layout perceptível (*zero cumulative layout shift*).
- **SC-003**: Em 100% dos casos de estudos compartilhados, a sessão de leitura ativa funciona sem requisições de mutação no banco e sem afetar a visualização de outros leitores.
- **SC-004**: 100% dos controles e botões de revelação cumprem as diretrizes de acessibilidade WCAG AA, com dimensões mínimas de toque de $44 \times 44\text{px}$ no mobile e suporte integral à navegação via teclado.
- **SC-005**: Zero perda ou modificação acidental do Markdown original do estudo em decorrência do uso das ferramentas de estudo ativo.

---

## Assumptions

- O modelo de dados relacional de destaques (`study_highlights`) e os tipos de destaque (`hidden`, `question`, `note`, `highlight`) desenvolvidos na feature F0.6.2 servem como base estrutural para identificar os trechos de estudo ativo.
- A contagem de progresso e o estado revelado/oculto de cada trecho são estritamente efêmeros (pertencem à sessão de leitura corrente do navegador), não necessitando de persistência no banco a cada clique de revelação.
- Leitores em redes móveis ou com leitores de tela dependem de textos claros e descritivos em botões (`aria-expanded`, `aria-label`).
