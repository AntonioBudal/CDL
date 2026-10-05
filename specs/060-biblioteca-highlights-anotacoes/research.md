# Research: F0.7.11 — Biblioteca Transversal de Highlights e Anotações

**Feature**: [spec.md](spec.md) | **Branch**: `060-biblioteca-highlights-anotacoes` | **Date**: 2026-10-06

Este documento consolida as decisões técnicas, alternativas consideradas e fundamentos arquiteturais para a implementação da Biblioteca Transversal de Highlights e Anotações.

---

## 1. Arquitetura de Consulta Agregada e Performance no SQLite

### Decisão
Criar endpoint consolidado `GET /api/highlights/library` no backend (FastAPI/SQLAlchemy), executando junção indexada entre `study_highlights`, `studies`, `chapters` e `books`, filtrando estritamente pelo `user_id` da sessão ativa e desconsiderando registros marcados para deleção (`deleted_at IS NOT NULL`). Adicionar índice de suporte via migração Alembic: `ix_study_highlights_user_kind_color` em `(user_id, kind, color)`.

### Racional
- As marcações de estudo possuem chaves estrangeiras diretas para `studies`, que por sua vez se ligam a `chapters` e `books`.
- Realizar a junção no banco evita múltiplas idas e vindas de rede (*N+1 queries*) e garante que cada cartão contenha instantaneamente o nome do livro, título do capítulo e título do estudo.
- O isolamento multiusuário é assegurado na cláusula `WHERE study_highlights.user_id == current_user.id`, impedindo qualquer vazamento de dados entre contas.
- Destaques associados a estudos ou livros na lixeira (`deleted_at IS NOT NULL`) são automaticamente suprimidos na consulta SQL.

### Alternativas Consideradas
- *Duplicação de títulos na tabela de highlights*: Armazenar `book_title` e `chapter_title` diretamente em `study_highlights`. Rejeitado para evitar redundância, inconsistência em caso de renomeação de obras e violação de normalização.
- *Carregamento de todos os estudos na memória do Python para filtrar highlights*: Rejeitado por ineficiência severa de memória e lentidão inaceitável à medida que o acervo cresce.

---

## 2. Paginação e Volume de Dados

### Decisão
Adotar paginação estruturada padrão baseada em `page` e `per_page` (padrão de 20 itens por página, configurável até 100), retornando metadados de paginação (`total`, `page`, `per_page`, `pages`, `has_next`, `has_prev`).

### Racional
- Leitores intensivos acumulam facilmente centenas ou milhares de destaques e notas de margem.
- A paginação no backend limita o tamanho da resposta HTTP (JSON) a dezenas de kilobytes, mantendo renderização ultra-rápida no frontend e prevenindo estouro de memória em dispositivos móveis.
- A contagem total permite que o cabeçalho exiba o número exato de itens encontrados (ex.: "142 anotações encontradas").

### Alternativas Consideradas
- *Infinite scroll contínuo desordenado*: Rejeitado por dificultar o alcance do rodapé e a navegação reversa via histórico do navegador em pesquisas densas.
- *Carregamento total sem limite*: Rejeitado por risco de travamento de renderização em acervos históricos extensos.

---

## 3. Filtragem Multidimensional e Sincronização de Estado na URL

### Decisão
Utilizar sincronização bidirecional entre os estados do Vue e os parâmetros de consulta (`query params`) da rota `/highlights`:
- `q`: termo de busca textual.
- `book`: id do livro selecionado.
- `chapter`: id do capítulo selecionado.
- `kind`: tipo de marcação (`highlight`, `note`, `quote`, `hidden`, `question`).
- `color`: cor cromática (`yellow`, `green`, `blue`, `pink`, `purple`).
- `view_mode`: modo de apresentação (`recent` ou `by_book`).
- `page`: índice da página ativa.

O campo de busca no frontend implementa um *debounce* de 250ms antes de disparar a consulta para o backend ou atualizar a URL.

### Racional
- Preserva a intenção do usuário no histórico do navegador (botões avançar/voltar funcionam naturalmente).
- Permite favoritar ou recarregar a página sem perder filtros complexos de pesquisa.
- O debounce de 250ms evita disparos excessivos de requisições enquanto o usuário está ativamente digitando.

### Alternativas Consideradas
- *Filtros mantidos exclusivamente no estado de memória do Pinia/Vue*: Rejeitado porque qualquer recarregamento da página ou navegação externa perderia a visualização de pesquisa do usuário.

---

## 4. Modos de Apresentação: Feed Cronológico ("Recentes") vs "Por Obra"

### Decisão
Implementar um seletor no topo da visualização (`HighlightFilterToolbar`) permitindo alternar entre dois modos:
1. **Recentes** (padrão): Exibição dos cards em ordem cronológica decrescente de criação/atualização, com divisores visuais por data quando aplicável.
2. **Por Obra**: Exibição dos cards agrupados por Livro e por Capítulo, em ordem natural de leitura.

A preferência do modo é sincronizada na URL e memorizada em `localStorage` para persistência entre sessões.

### Racional
- Atende diretamente à escolha do usuário na clarificação (Q1: Opção C).
- O modo "Recentes" funciona como um feed contínuo das reflexões mais frescas do leitor.
- O modo "Por Obra" atende a leitores sistemáticos que revisam um livro em bloco do início ao fim.

### Alternativas Consideradas
- *Apenas feed cronológico sem agrupamento por obra*: Rejeitado pois dispersa marcações de um mesmo capítulo ao longo de datas distintas.

---

## 5. Gestão Rápida In-Card (Edição de Nota e Exclusão)

### Decisão
No componente `HighlightCard.vue`:
- O texto da anotação/comentário pode ser editado in-place clicando em um botão de edição rápida, que abre um campo de texto inline com botões "Salvar" e "Cancelar".
- A exclusão pode ser acionada diretamente no cartão com um diálogo de confirmação acessível (*popover* ou confirmação visual), disparando a remoção no backend e retirando o cartão da lista com transição suave.
- A mutação no backend reutiliza os endpoints já existentes: `PATCH /api/studies/{study_id}/highlights/{highlight_id}` e `DELETE /api/studies/{study_id}/highlights/{highlight_id}` (ou rota utilitária correspondente).

### Racional
- Atende à escolha do usuário na clarificação (Q2: Opção A).
- Reduz atrito: o leitor não precisa abrir o estudo inteiro apenas para corrigir uma palavra numa nota ou remover um destaque acidental.

### Alternativas Consideradas
- *Somente leitura na biblioteca com edição restrita ao leitor do estudo*: Rejeitado pelo usuário para priorizar conveniência e agilidade na curadoria.

---

## 6. Salto Contextual e Foco Visual ("Abrir no Estudo")

### Decisão
O botão primário de cada cartão navega na mesma aba para o estudo correspondente usando o Vue Router:
`router.push({ name: 'study', params: { bookId, studyId }, hash: `#highlight-${highlightId}` })`
No componente de estudo (`StudyView.vue`):
- O utilitário existente `scrollAndFocusHighlight` em `frontend/src/utils/highlightRenderer.ts` localiza o elemento `[data-highlight-id="{id}"]`, executa `element.scrollIntoView({ behavior: 'smooth', block: 'center' })` e adiciona a classe `.study-highlight-focused`.
- Adicionar no CSS do estudo a animação `@keyframes highlight-glow-pulse` com duração de 2 segundos, emitindo uma pulsação luminosa de destaque para conduzir o olhar do leitor.

### Racional
- Atende à escolha do usuário na clarificação (Q3: Opção A).
- Reutiliza a infraestrutura já consolidada de `scrollAndFocusHighlight`, garantindo compatibilidade total e zero código duplicado.

### Alternativas Consideradas
- *Abertura forçada em nova aba*: Rejeitado pelo usuário para evitar acúmulo desordenado de abas no navegador.
- *Painel lateral/gaveta de estudo*: Rejeitado por complexidade desnecessária e menor espaço de leitura.
