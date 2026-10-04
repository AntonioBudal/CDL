# Research: F 0.7.9 — Refinamento do Editor de Estudos e Correção de Ícones de Categorias

**Date**: 2026-10-04  
**Feature**: F 0.7.9 — Refinamento do Editor de Estudos  
**Branch**: `058-refinamento-editor`

---

## Technical Decisions

### Decision 1 (D1): Arquitetura de Abas / Seção Focada e Modo Contínuo em `StudyEditorFields.vue`
- **Decisão**: Implementar uma barra de pílulas/abas no topo do formulário de análise (`Resumo`, `Explicação`, `Conceitos`, `Referências` e `Notas`) com estado `activeTab`, combinada a um botão toggle de visualização ("Focado" vs "Ver todas").
- **Racional**:
  - No fluxo focado (padrão especialmente no mobile), apenas a seção ativa é renderizada no DOM visível, reduzindo a altura do formulário em mais de 65% e eliminando rolagens verticais desgastantes.
  - Para leitores em telas amplas de desktop que preferem visualizar o ensaio corrido de ponta a ponta, o modo "Ver todas" mantém o layout tradicional com as seções em sequência.
  - Cada pílula de aba exibe um micro-indicador (ponto discreto) caso a seção correspondente já contenha texto preenchido, permitindo saber instantaneamente quais partes do estudo já foram redigidas.
- **Alternativas consideradas**:
  - *Acordeão vertical expansível*: Rejeitado porque no mobile ainda exige que o usuário desça verticalmente por vários blocos e o acordeão pode expandir para além da viewport.
  - *Breakpoint rígido CSS*: Rejeitado porque priva usuários de desktop em janelas divididas (split screen) ou tablets do modo focado.

---

### Decision 2 (D2): Renderização de Pré-Visualização (Preview) In-Place com `markdown-it`
- **Decisão**: Adicionar um botão de alternância "Editar / Prévia" diretamente no cabeçalho de cada seção analítica (ao lado do label ou da toolbar), utilizando a biblioteca nativa `markdown-it` já integrada no projeto.
- **Racional**:
  - Permite verificar a renderização tipográfica do texto Markdown (títulos, listas, blocos de citação e links) de forma pontual e contextual, sem quebrar o layout da página nem abrir modais externos.
  - O container de prévia herda as classes `.markdown-body` e a tipografia editorial do Leitorum (EB Garamond / Source Sans 3).
  - Um clique retorna imediatamente para o modo de edição com o cursor posicionado.
- **Alternativas consideradas**:
  - *Divisão lado a lado (Split View)*: Rejeitada porque consome excessiva largura horizontal e torna o layout inviável no mobile.
  - *Modal flutuante de visualização*: Rejeitado por adicionar atrito cognitivo e distanciar o leitor do contexto de escrita da seção.

---

### Decision 3 (D3): Ergonomia Tátil da `MarkdownToolbar.vue` e Atalhos Universais
- **Decisão**: Ajustar a barra de ferramentas `MarkdownToolbar.vue` com botões que respeitam a área mínima tátil de $44 \times 44$px no mobile através de padding e toque acessível (`touch-action: manipulation`), rolagem horizontal sem scrollbar feia e preservação do evento `@mousedown.prevent` para não roubar o foco da textarea.
- **Racional**:
  - No mobile, clicar num botão de formatação não pode desfazer a seleção de texto nem fechar o teclado virtual. O `@mousedown.prevent` mantém o cursor intacto na textarea ativa.
  - Atalhos de teclado universais (`Ctrl+B`, `Ctrl+I`, `Ctrl+K`) já possuem manipulador em `MarkdownToolbar.vue`, mas serão estendidos para todas as seções e caixas de texto com feedback tátil suave.
- **Alternativas consideradas**:
  - *Toolbar flutuante fixa no rodapé da viewport*: Rejeitada por conflitar com o teclado virtual de dispositivos Android e iOS e cobrir o botão nativo de salvar.

---

### Decision 4 (D4): Persistência de Rascunho em `sessionStorage` e Restauração Transparente
- **Decisão**: Implementar um composable `useStudyDraft.ts` que escuta as mutações de `state.title`, `state.location`, `state.sections` e `state.notes` com debounce de 500ms, armazenando em `sessionStorage` sob a chave `caderno_draft_study_<id>`.
- **Racional**:
  - Se a aba for recarregada acidentalmente ou o navegador fechado em segundo plano, os dados do rascunho são recuperados na montagem do componente.
  - O formulário restaura os dados automaticamente e exibe um banner discreto no topo: *"Rascunho não salvo recuperado. [Descartar rascunho]"*.
  - Clicar em "Descartar rascunho" limpa o `sessionStorage` e recarrega os dados oficiais do servidor.
  - Ao salvar o estudo com sucesso no backend, o rascunho no `sessionStorage` é limpo imediatamente.
- **Alternativas consideradas**:
  - *Auto-save direto no banco SQLite*: Rejeitado pela Constituição do Projeto (Princípio I e IV), pois geraria revisões espúrias no histórico de versões sem a intenção explícita do leitor.
  - *Uso de `localStorage` permanente*: Rejeitado porque rascunhos de sessão não devem ficar esquecidos indefinidamente em dispositivos compartilhados.

---

### Decision 5 (D5): Padronização e Polimento de Ícones em `CategoryBadge.vue` e `CategoryInput.vue`
- **Decisão**: Substituir todos os SVGs inline codificados manualmente e caminhos poligonais obsoletos pelo componente oficial `<Icon name="x" :size="12" />`, `<Icon name="folder" :size="14" />` e `<Icon name="search" :size="14" />`.
- **Racional**:
  - Garante consistência tipográfica, herança de `currentColor`, controle de espessura de traço (`stroke-width`) e alinhamento flexível padronizado (`inline-flex items-center justify-center`).
  - Corrige distorções relatadas no Firefox e Safari mobile onde os botões de fechar do badge ficavam recortados ou fora do fluxo vertical.
  - Adiciona suporte a navegação acessível por teclado com `:aria-label="Remover categoria ${category.name}"` e alvos táteis mínimos de $44 \times 44$px no mobile.
- **Alternativas consideradas**:
  - *Manter SVG inline com ajustes de CSS*: Rejeitado por violar a padronização do sistema de design onde todos os ícones da UI devem fluir pelo catálogo central de `<Icon.vue>`.
