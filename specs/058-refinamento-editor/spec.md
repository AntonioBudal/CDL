# Feature Specification: F 0.7.9 — Refinamento do Editor de Estudos e Correção de Ícones de Categorias

**Feature Branch**: `058-refinamento-editor`  
**Created**: 2026-10-04  
**Status**: Draft  
**Input**: User description: "/speckit-specify F0.7.9"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Navegação Responsiva de Seções e Modo Focado de Escrita (Priority: P1) 🎯 MVP

O leitor acessa o formulário de edição de um estudo em qualquer dispositivo e conta com uma navegação ágil entre as seções analíticas (`Resumo`, `Explicação`, `Conceitos`, `Referências` e `Notas`), eliminando a rolagem vertical infinita e evitando sobrecarga visual no Desktop e Mobile.

**Why this priority**: A edição de estudos é a atividade central de reflexão do leitor. Atualmente, os 4 campos empilhados com 9 linhas cada tornam a página extensa, cansativa e propensa a cliques acidentais no mobile.

**Independent Test**: Abrir `StudyEditView.vue` em resolução móvel e desktop; alternar entre seções via pílulas de navegação; preencher o conteúdo; verificar que a visualização permanece compacta, sem barras de rolagem horizontais e permitindo salvar mantendo a regra de preenchimento mínimo.

**Acceptance Scenarios**:

1. **Given** um estudo aberto para edição no mobile (< 768px), **When** o usuário toca na seção "Conceitos", **Then** o formulário foca imediatamente no campo de conceitos com sua barra de ferramentas dedicada, ocultando ou recolhendo as demais seções.
2. **Given** o editor em tela ampla (Desktop), **When** o usuário prefere inspecionar o estudo por completo, **Then** ele pode alternar para o modo "Todas as seções" mantendo o fluxo contínuo.
3. **Given** um formulário com apenas uma das seções preenchidas, **When** o usuário clica em "Salvar alterações", **Then** a validação `hasAnalysis` autoriza o salvamento com sucesso e redireciona para a leitura do estudo.

---

### User Story 2 - Barra de Formatação Markdown Otimizada, Atalhos e Prévia Imediata (Priority: P2)

O leitor utiliza botões táteis ergonômicos na barra de ferramentas (`MarkdownToolbar.vue`) ou atalhos de teclado universais (`Ctrl+B`, `Ctrl+I`, `Ctrl+K`) para formatar seu texto com precisão, dispondo de alternância instantânea entre edição e pré-visualização renderizada.

**Why this priority**: Markdown é o formato essencial de anotação do Leitorum. Formatar textos no mobile exige botões acessíveis ($\ge 44 \times 44$px) e no desktop atalhos sem quebra de foco, além de verificação visual antes de salvar.

**Independent Test**: Selecionar um trecho em qualquer textarea analítica; pressionar `Ctrl+B` ou tocar no botão de negrito; verificar que a tag `**` envolve a seleção perfeitamente sem deslocar o cursor de forma errática; alternar para a prévia visual e confirmar a renderização em HTML estilizado.

**Acceptance Scenarios**:

1. **Given** o cursor posicionado em uma textarea, **When** o usuário pressiona `Ctrl+B` (ou `Cmd+B`), **Then** o texto selecionado é envolvido por `**` e a barra de status marca o estudo como alterado (`dirty`).
2. **Given** a barra `MarkdownToolbar.vue` em tela móvel, **When** o usuário interage com os botões, **Then** os alvos táteis possuem área mínima de $44 \times 44$px e a barra possui rolagem horizontal suave sem quebrar a largura da página.
3. **Given** uma seção com texto em Markdown, **When** o usuário ativa o modo de prévia, **Then** o HTML correspondente é exibido de forma segura, com tipografia fiel ao tema ativo.

---

### User Story 3 - Correção Definitiva de Ícones de Categorias e Proteção de Rascunho em Sessão (Priority: P3)

O leitor associa e gerencia categorias em livros e estudos sem falhas visuais, com ícones SVG consistentes no seletor (`CategoryInput.vue`) e nos badges (`CategoryBadge.vue`), contando também com recuperação automática de rascunhos temporários salvos em `sessionStorage`.

**Why this priority**: Ícones desalinhados ou SVG cortados transmitem sensação de sistema inacabado. Além disso, o fechamento acidental da aba do navegador não deve ocasionar perda de reflexões longas em andamento.

**Independent Test**: Adicionar e remover categorias em `CategoryInput.vue`, validando que os ícones de tag, busca e o botão de fechar renderizam perfeitamente sem bordas cortadas; digitar um texto longo no editor, fechar a aba/recarregar a página e confirmar que o rascunho temporário é recuperável.

**Acceptance Scenarios**:

1. **Given** uma categoria selecionada em `CategoryBadge.vue`, **When** inspecionado visualmente, **Then** o botão de remoção utiliza ícone padronizado via `<Icon name="x" />`, alinhado verticalmente e com foco acessível via teclado.
2. **Given** o campo de busca de categorias em `CategoryInput.vue`, **When** o leitor digita termos ou recebe sugestões canônicas, **Then** os elementos gráficos e badges possuem tamanho uniforme e rótulos acessíveis.
3. **Given** uma edição em progresso não salva, **When** a página é recarregada pelo usuário, **Then** o estado do rascunho é preservado em `sessionStorage` e o usuário pode restaurá-lo com um clique.

---

### Edge Cases

- O que acontece quando o usuário edita duas abas diferentes simultaneamente com estudos distintos? O `sessionStorage` isola os rascunhos por chave única baseada no `studyId`.
- Como o sistema se comporta se o usuário limpar completamente o texto de todas as 4 seções analíticas? O botão "Salvar" é desabilitado, exibindo a mensagem explicativa de que ao menos uma seção de análise deve estar preenchida.
- O que ocorre se um atalho de formatação (`Ctrl+B`) for acionado sem nenhuma seleção de texto? A ferramenta insere a sintaxe padrão `**texto em negrito**` e posiciona o cursor entre os delimitadores.
- Como o seletor de categorias reage a nomes muito extensos? Os badges aplicam truncamento elíptico com largura máxima delimitada e atributo `title` nativo preservando a leitura completa.

---

## Clarifications

### Session 2026-10-04
- **Q1 (Navegação de Seções)**: Pílulas/Abas no topo com alternância rápida entre seções individuais (`Resumo`, `Explicação`, `Conceitos`, `Referências`, `Notas`) e opção toggle "Ver todas as seções" para quem prefere o fluxo contínuo. -> **Option A (Accepted)**
- **Q2 (Modo de Prévia)**: Botão toggle "Editar / Prévia" diretamente no cabeçalho de cada seção analítica, permitindo verificar a renderização Markdown in-place instantaneamente. -> **Option A (Accepted)**
- **Q3 (Recuperação de Rascunho)**: Restauração automática do rascunho com banner discreto no topo ("Rascunho recuperado automaticamente. [Descartar rascunho]"), garantindo zero atrito com opção de reverter. -> **Option A (Accepted)**

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE fornecer modo de visualização focado no editor de estudos (`StudyEditorFields.vue`), permitindo navegar entre as seções analíticas por pílulas/abas no topo com alternância rápida entre seções individuais e opção toggle "Ver todas as seções" para exibição contínua.
- **FR-002**: O sistema DEVE disponibilizar modo de pré-visualização (Preview) do Markdown diretamente no cabeçalho de cada seção através de um botão toggle "Editar / Prévia" in-place antes da confirmação do salvamento.
- **FR-003**: A barra de ferramentas de formatação `MarkdownToolbar.vue` DEVE ter alvos táteis mínimos de $44 \times 44$px no mobile e rolagem horizontal suave sem transbordamento do layout.
- **FR-004**: O editor DEVE responder aos atalhos universais de teclado de formatação (`Ctrl+B` para negrito, `Ctrl+I` para itálico e `Ctrl+K` para links) diretamente dentro das caixas de texto.
- **FR-005**: O sistema DEVE salvar rascunhos de edição em tempo real no `sessionStorage` atrelados ao identificador do estudo (`caderno_draft_study_<id>`), restaurando o conteúdo automaticamente ao reabrir a tela com exibição de banner discreto no topo contendo botão para descartar e reverter à versão do servidor.
- **FR-006**: Os componentes `CategoryBadge.vue` e `CategoryInput.vue` DEVEM utilizar o componente canônico `<Icon />` com alinhamento flexível padronizado e sem SVG inline corrompido ou desalinhado.
- **FR-007**: A remoção e inclusão de categorias DEVE disponibilizar rótulos `aria-label` claros e suporte a controle completo por teclado (`Enter`, `Backspace`, `Tab`).
- **FR-008**: A proteção contra abandono de alterações não salvas (`useUnsavedChanges`) DEVE permanecer estritamente ativa e integrada com o estado do formulário.

---

### Key Entities *(include if feature involves data)*

- **StudyEditorDraft**: Representação temporária em `sessionStorage` contendo `{ studyId, title, location, sections: { summary, explanation, concepts, references }, notes, updatedAt }`.
- **CategoryBadgeItem**: Representação visual da taxonomia com chave canônica, nome formatado, caminho hierárquico e estado interativo (removível ou somente leitura).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A rolagem vertical necessária para editar qualquer seção no mobile é reduzida em pelo menos 60% através da navegação focada por seções.
- **SC-002**: 100% dos botões interativos na `MarkdownToolbar.vue` e `CategoryBadge.vue` atendem aos critérios de acessibilidade móvel com alvos $\ge 44 \times 44$px ou espaçamento tátil equivalente.
- **SC-003**: Zero artefatos visuais ou quebras de alinhamento SVG relatados no seletor de categorias em qualquer navegador moderno.
- **SC-004**: Rascunhos não salvos são preservados e recuperáveis em 100% dos casos de recarregamento acidental da aba durante a edição.
- **SC-005**: 100% de cobertura de testes automatizados com zero regressões na suíte existente (`npm test`, `pytest`, `npm run build`).

---

## Assumptions

- O armazenamento de rascunhos em `sessionStorage` não substitui a persistência definitiva no banco SQLite via API REST; serve unicamente como rede de segurança volátil de navegação.
- O formato do banco de dados e as migrações permanecem intactos (zero impacto no schema SQLite e nos contratos da API REST de estudos e categorias).
- A validação de negócio que exige ao menos uma seção de análise preenchida (`hasAnalysis`) é mantida estritamente sem alterações.
