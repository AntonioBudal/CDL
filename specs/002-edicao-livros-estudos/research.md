# Technical Research: Edição Completa de Metadados de Livros, Capítulos e Anotações

**Feature**: `002-edicao-livros-estudos`  
**Date**: 2026-09-17  
**Status**: Completed  

---

## 1. Decisões Técnicas

### D1: Evolução do Modelo de Livros e Schema Relacional
- **Decisão**: Adicionar os campos opcionais `subtitle` (TEXT, default vazio) e `year` (INTEGER, anulável), além do timestamp de atualização `updated_at` (DATETIME UTC) no modelo `Book`.
- **Racional**:
  - Atende diretamente à resposta do usuário (Q1: Título obrigatório; Autor, subtítulo e ano de publicação opcionais).
  - O campo `updated_at` habilita o controle de concorrência otimista exigido em Q3.
  - Utiliza Alembic para a migração `0002_add_book_metadata_and_concurrency.py`, beneficiando-se da barreira atômica de snapshot pré-migração estabelecida na Feature 001.
- **Alternativas Rejeitadas**:
  - *Armazenar metadados em campo JSON genérico*: Rejeitado por dificultar buscas, ordenação e tipagem estrita no SQLite/SQLAlchemy.

---

### D2: Mecanismo de Reordenação e Edição de Capítulos
- **Decisão**: Oferecer edição de nome de capítulo via `PATCH /books/{book_id}/chapters/{chapter_id}` e reordenação através de endpoint transacional de movimentação (`POST .../reorder` ou troca atômica de posições), acionado pelos botões subir/descer (▲ / ▼) na listagem.
- **Racional**:
  - Atende à decisão do usuário (Q2: botões subir/descer na interface).
  - É ergonômico tanto no desktop (mouse/teclado) quanto em telas sensíveis ao toque de celulares (sem a instabilidade de bibliotecas de drag-and-drop no mobile).
  - A troca de posição (`position`) entre dois capítulos adjacentes é feita atomicamente em uma única transação de banco de dados, garantindo que nenhum índice fique duplicado ou inconsistente.
- **Alternativas Rejeitadas**:
  - *Drag-and-drop exclusivo com HTML5 Drag Events*: Incompatível ou muito suscetível a erros de rolagem em navegadores mobile (Android/iOS).

---

### D3: Concorrência Otimista e Prevenção de Perda de Dados
- **Decisão**: Implementar verificação de versão otimista via timestamp `updated_at` nos endpoints de atualização (`PATCH`).
- **Racional**:
  - Atende estritamente à resposta do usuário (Q3: bloquear salvamento, avisar o usuário e preservar o texto digitado).
  - Quando o cliente envia um `PATCH`, inclui o `updated_at` do momento em que carregou o registro.
  - Se o registro no banco tiver `updated_at > payload.updated_at`, o backend recusa com `HTTP 409 Conflict`.
  - O frontend captura o status 409, exibe um alerta explicativo ("Este item foi modificado em outro dispositivo"), mantendo 100% dos dados digitados nos campos para que o usuário não perca seu trabalho.
- **Alternativas Rejeitadas**:
  - *Last Write Wins (sobrescrita silenciosa)*: Causa perda oculta de notas detalhadas se o usuário alternar entre o celular e o PC.
  - *Pessimistic locking (bloqueio de registro)*: Inviável em arquitetura monousuário desconectada com suporte a redes móveis e Tailscale.

---

### D4: Integração na Interface Vue 3
- **Decisão**:
  1. Em `BookView.vue`, adicionar modal de edição de metadados do livro (`EditBookModal.vue` ou componente inline modular) e controles de ação rápida na lista de capítulos (botões subir/descer e botão de renomear).
  2. Em `StudyEditView.vue`, incorporar a validação de concorrência com tratamento de erro 409 e banner de preservação de texto.
  3. Reutilizar o composable existente `useUnsavedChanges` para proteger contra fechamento acidental da aba ou navegação não confirmada.
- **Racional**:
  - Mantém a identidade visual minimalista do Caderno de Leitura, sem poluição visual.
  - Compatível com todos os temas (Claro, Escuro, E-Ink) e paletas existentes.

---

## 2. Matriz de Dependências e Riscos

| Risco Identificado | Severidade | Mitigação Arquitetural |
|---|---|---|
| Migração de schema em acervo existente | Alta | O hook da Feature 001 (`ensure_pre_upgrade_snapshot`) garante snapshot automático testado antes de rodar o Alembic. |
| Colisão de `position` em capítulos | Média | Troca de posições realizada em transação atômica única com renumeração contínua. |
| Perda de rascunho longo de anotações em erro | Alta | `useUnsavedChanges` + preservação de estado em memória reativa sem limpar formulário em 409/500. |
