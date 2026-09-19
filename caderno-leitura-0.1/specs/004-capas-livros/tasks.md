# Tasks: Capas de Livros por Upload e URL

**Feature**: Capas de Livros por Upload e URL  
**Branch**: `004-capas-livros` | **Data**: 2026-09-18  
**Status**: Concluído (100%)  
**Plano**: [plan.md](plan.md) | **Especificação**: [spec.md](spec.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Instalação e configuração de dependências e infraestrutura compartilhada de capas

- [X] T001 [P] Adicionar dependências Pillow>=10.0.0 e python-multipart>=0.0.18 em backend/requirements.in e backend/requirements.txt
- [X] T002 [P] Implementar função canônica get_covers_dir com suporte a CADERNO_COVERS_DIR em backend/app/core/config.py
- [X] T003 [P] Criar router base para entrega de capas estáticas em backend/app/routers/covers.py e registrá-lo em backend/app/main.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Evolução de schema, modelos, schemas Pydantic, tipos e serviços base que bloqueiam as histórias de usuário

> ⚠️ **CRÍTICO**: Nenhuma história de usuário pode ser iniciada antes da conclusão desta fase.

- [X] T004 Adicionar coluna cover_image no modelo Book em backend/app/models/book.py
- [X] T005 Criar migração incremental 0004_add_book_cover_image.py em backend/migrations/versions/0004_add_book_cover_image.py
- [X] T006 [P] Atualizar schemas BookRead e BookPatch com campo cover_image em backend/app/schemas/book.py
- [X] T007 [P] Criar schemas CoverUrlRequest e CoverResponse em backend/app/schemas/cover.py
- [X] T008 [P] Atualizar interface Book e exportar tipo CoverResponse em frontend/src/types.ts
- [X] T009 [P] Criar módulo base do serviço de capas com rotinas de validação de imagem e diretório em backend/app/services/cover_service.py

**Checkpoint**: Fundação pronta — implementação das histórias de usuário pode começar.

---

## Phase 3: User Story 1 - Upload e Visualização de Capa Local (Priority: P1) 🎯 MVP

**Goal**: Leitor pode enviar uma imagem do computador ou smartphone (JPEG, PNG ou WebP), o backend valida a integridade, redimensiona proporcionalmente para largura máxima de 800px no formato WebP otimizado, armazena no diretório de capas, serve via rota controlada com cache HTTP, exibe nos cartões da estante e cabeçalho do livro, e renderiza marcador tipográfico harmônico para livros sem capa.

**Independent Test**: Realizar upload de imagem JPEG de 1600px para um livro ativo, verificar gravação de arquivo WebP com largura máxima de 800px em diretório temporário, confirmar resposta de entrega em `/api/covers/{filename}` e visualização nos cartões e detalhe do livro; verificar exibição de fallback tipográfico elegante para livro sem capa.

### Tests for User Story 1 🧪
- [X] T010 [P] [US1] Criar testes automatizados de upload local, redimensionamento WebP, limites de 5MB e fallback em backend/tests/test_book_covers.py

### Implementation for User Story 1
- [X] T011 [US1] Implementar função process_and_save_cover com redimensionamento Lanczos e conversão WebP em backend/app/services/cover_service.py
- [X] T012 [US1] Implementar endpoint POST /api/books/{id}/cover para upload multipart em backend/app/routers/books.py
- [X] T013 [US1] Implementar endpoint GET /api/covers/{filename} com validação anti-traversal e cache HTTP em backend/app/routers/covers.py
- [X] T014 [P] [US1] Implementar método uploadBookCover no serviço de API em frontend/src/services/api.ts
- [X] T015 [P] [US1] Criar componente BookCover.vue com proporção 2:3, lazy loading e fallback tipográfico harmônico em frontend/src/components/BookCover.vue
- [X] T016 [US1] Integrar componente BookCover nos cartões de livro em frontend/src/views/BooksView.vue
- [X] T017 [US1] Integrar componente BookCover no cabeçalho de detalhes da obra em frontend/src/views/BookView.vue
- [X] T018 [US1] Integrar campo de upload e pré-visualização de capa local em frontend/src/components/BookEditModal.vue

**Checkpoint**: User Story 1 (MVP) completamente funcional e testável de forma independente.

---

## Phase 4: User Story 2 - Importação de Capa por URL Externa Segura (Priority: P2)

**Goal**: Leitor pode informar a URL direta de uma imagem na internet; o servidor backend valida contra SSRF (bloqueando loopback, multicast e faixas privadas RFC 1918), faz o download seguro com timeout de 5 segundos e teto de 5 MB, otimiza para WebP e associa a capa ao livro.

**Independent Test**: Submeter URL pública válida de imagem e comprovar download e conversão WebP; submeter URLs para localhost (`127.0.0.1`) e rede privada (`192.168.1.1`) e verificar bloqueio com HTTP 400 sem disparo de conexão externa.

### Tests for User Story 2 🧪
- [X] T019 [P] [US2] Criar testes automatizados de proteção anti-SSRF, timeouts e importação por URL em backend/tests/test_book_covers.py

### Implementation for User Story 2
- [X] T020 [US2] Implementar validação de endereço e filtro anti-SSRF com socket e ipaddress em backend/app/services/cover_service.py
- [X] T021 [US2] Implementar função download_cover_from_url com httpx, timeout de 5s e teto de 5MB em backend/app/services/cover_service.py
- [X] T022 [US2] Implementar endpoint POST /api/books/{id}/cover/url em backend/app/routers/books.py
- [X] T023 [P] [US2] Implementar método importBookCoverFromUrl no serviço de API em frontend/src/services/api.ts
- [X] T024 [US2] Integrar campo de importação por URL externa com validação e feedback em frontend/src/components/BookEditModal.vue

**Checkpoint**: User Stories 1 e 2 operando e testáveis de forma independente.

---

## Phase 5: User Story 3 - Substituição e Remoção de Capas com Preservação de Integridade (Priority: P3)

**Goal**: Leitor pode remover a capa associada (retornando ao marcador tipográfico) ou substituí-la por outra; o ciclo de vida preserva a capa física na lixeira (soft delete) e expurga o arquivo em disco apenas na exclusão definitiva ou rotina de esvaziamento da lixeira (se órfão).

**Independent Test**: Remover capa de um livro e verificar retorno ao fallback; mover livro com capa para a lixeira e restaurar verificando retenção do arquivo; esvaziar lixeira e verificar remoção física do arquivo de imagem do disco.

### Tests for User Story 3 🧪
- [X] T025 [P] [US3] Criar testes automatizados de remoção, substituição, preservação na lixeira e expurgo atômico em backend/tests/test_book_covers.py

### Implementation for User Story 3
- [X] T026 [US3] Implementar função delete_cover_file_if_orphan para remoção física segura em backend/app/services/cover_service.py
- [X] T027 [US3] Implementar endpoint DELETE /api/books/{id}/cover em backend/app/routers/books.py
- [X] T028 [US3] Integrar expurgo físico de capas órfãs em permanent_delete_book, empty_trash e purge_expired_trash em backend/app/services/trash_service.py
- [X] T029 [P] [US3] Implementar método removeBookCover no serviço de API em frontend/src/services/api.ts
- [X] T030 [US3] Integrar botão e fluxo de remoção de capa com confirmação em frontend/src/components/BookEditModal.vue

**Checkpoint**: Todas as histórias de usuário funcionais, integradas e com ciclo de vida completo.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verificação de qualidade ponta a ponta, testes de regressão, build e alinhamento de documentação

- [X] T031 [P] Executar validação manual e automatizada completa dos 5 cenários descritos em specs/004-capas-livros/quickstart.md
- [X] T032 [P] Atualizar testes de interface do frontend cobrindo BookCover em frontend/tests/
- [X] T033 Executar typecheck com vue-tsc, build do Vite e suíte completa de testes no backend e frontend
- [X] T034 [P] Atualizar documentação de arquitetura e acervo em docs/contexto/PROJETO.md

---

## Dependencies & Execution Order

### Phase Dependencies
- **Setup (Phase 1)**: Sem dependências prévias — concluída.
- **Foundational (Phase 2)**: Depende da Phase 1 — concluída.
- **User Story 1 (Phase 3 - MVP)**: Depende da Phase 2 — concluída.
- **User Story 2 (Phase 4)**: Depende da Phase 2 — concluída.
- **User Story 3 (Phase 5)**: Depende das Phases 2 e 3 — concluída.
- **Polish (Phase 6)**: Concluída.

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Concluir Phase 1: Setup (Pillow, python-multipart, config, router). [Concluído]
2. Concluir Phase 2: Foundational (Schema, migração, schemas Pydantic, tipos TS). [Concluído]
3. Concluir Phase 3: User Story 1 (Upload local, redimensionamento WebP, componente BookCover e fallback). [Concluído]

### Incremental Delivery
1. **Incremento 1 (MVP)**: Setup + Foundational + User Story 1 → Upload e exibição de capas locais. [Concluído]
2. **Incremento 2**: User Story 2 → Importação direta de capas por URL com proteção anti-SSRF. [Concluído]
3. **Incremento 3**: User Story 3 → Remoção, substituição e gestão consistente do ciclo de vida físico na lixeira. [Concluído]
4. **Incremento 4**: Polish → Suíte completa de testes, typecheck e documentação. [Concluído]
