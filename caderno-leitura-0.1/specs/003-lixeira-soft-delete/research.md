# Research & Technical Decisions: Lixeira e Restauração de Itens (Soft Delete)

**Feature**: `003-lixeira-soft-delete`  
**Date**: 2026-09-18  
**Status**: Completed  

---

## Technical Context & Decisions

### Decision 1: Modelagem de Soft Delete com Timestamp UTC Anulável

- **Decisão**: Adicionar a coluna `deleted_at: Mapped[datetime | None]` em `books` e `studies`. O valor padrão é `None` (registro ativo). Quando descartado, registra a data e hora em UTC através de `UTCDateTime()` e `utc_now()`. Capítulos (`chapters`) não recebem coluna própria de exclusão, pertencendo indissociavelmente ao ciclo de vida do livro pai (conforme esclarecido em FR-010).
- **Racional**:
  - Timestamps (`deleted_at`) fornecem rastreabilidade exata de quando a exclusão ocorreu, permitindo implementar a política de expurgo de 30 dias (FR-012) e ordenação temporal na tela da Lixeira. Flags booleanas (`is_deleted`) perdem essa informação temporal crucial.
  - Como os capítulos estruturam o sumário do livro, não faz sentido descartar capítulos isoladamente sem os estudos. Deixar capítulos ancorados no livro simplifica a modelagem relacional e mantém a integridade referencial.
- **Alternativas consideradas**:
  - *Tabela separada de lixeira (`trash_items`)*: Descartada pois quebra relacionamentos de chave estrangeira com integridade ativada (`PRAGMA foreign_keys = ON`), exigiria cópia física de dados para outra tabela e dificultaria a restauração.
  - *Booleano `is_deleted` com trigger*: Descartado por ser incompatível com a política de purga temporal de 30 dias e por adicionar complexidade desnecessária em triggers SQLite.

---

### Decision 2: Estratégia de Filtragem de Acervo Ativo e Restauração em Cascata

- **Decisão**:
  1. **Filtragem do Acervo Ativo**: Todas as consultas padrão de livros e estudos aplicam explicitamente `WHERE books.deleted_at IS NULL` e `WHERE studies.deleted_at IS NULL`. Para estudos carregados via livro/capítulo, assegura-se que `books.deleted_at IS NULL` também seja respeitado.
  2. **Descarte de Livro**: Ao descartar um livro (`POST /api/books/{id}/trash`), seta-se `Book.deleted_at = utc_now()`. Os estudos ativos que estavam sob esse livro continuam com `Study.deleted_at = None`, mas ficam ocultos porque o livro pai está descartado.
  3. **Restauração de Livro**: Ao restaurar um livro (`POST /api/books/{id}/restore`), seta-se `Book.deleted_at = None`. Os estudos com `Study.deleted_at = None` voltam automaticamente a ser exibidos. Estudos que haviam sido descartados individualmente antes (`Study.deleted_at IS NOT NULL`) permanecem na lixeira.
  4. **Restauração de Estudo com Livro na Lixeira**: Ao restaurar um estudo (`POST /api/studies/{id}/restore`), o sistema verifica se o livro pai está na lixeira (`parent_book.deleted_at IS NOT NULL`). Se estiver, restaura o estudo (`Study.deleted_at = None`) E restaura automaticamente o livro pai (`Book.deleted_at = None`) em cascata ascendente (conforme esclarecido em FR-011).
- **Racional**:
  - Evita mutações em massa (bulk updates de centenas de estudos) ao descartar um livro com muitos estudos, tornando o descarte e a restauração instantâneos (< 5ms).
  - Preserva o estado de estudos descartados individualmente antes do descarte do livro pai, cumprindo com perfeição o requisito de aceite do Roadmap 0.3.
- **Alternativas consideradas**:
  - *Seta `deleted_at` em todos os estudos filhos no descarte do livro*: Descartada porque se um estudo já estava na lixeira antes, não seria possível distinguir se ele foi descartado individualmente ou em cascata pelo livro, corrompendo o critério de restauração seletiva.

---

### Decision 3: Política de Retenção e Purga Automática após 30 Dias

- **Decisão**:
  - Itens na lixeira possuem validade de 30 dias a partir de `deleted_at`.
  - Uma rotina atômica de limpeza (`purge_expired_trash(session, threshold_days=30)`) é executada:
    1. Automaticamente no hook de startup da aplicação (`@app.on_event("startup")` ou lifespan do FastAPI).
    2. Sob demanda via endpoint `POST /api/trash/purge-expired`.
    3. Ao carregar a tela da Lixeira via `GET /api/trash`.
  - A purga remove permanentemente registros onde `deleted_at < datetime.now(timezone.utc) - timedelta(days=30)`.
  - A exclusão permanente respeita chaves estrangeiras (`PRAGMA foreign_keys = ON`): ao expurgar um livro, seus estudos e capítulos são deletados de forma segura e transacional.
- **Racional**:
  - Mantém o banco local limpo e em conformidade estrita com o FR-012 aprovado pelo usuário, sem sobrecarregar o SQLite com jobs em segundo plano contínuos ou threads em loop.
- **Alternativas consideradas**:
  - *Background thread com `sleep`*: Descartada por consumir recursos em segundo plano desnecessariamente em uma aplicação local monousuário. Executar no startup e na leitura da lixeira é determinístico, testável e seguro.

---

### Decision 4: Interface do Usuário e Rotas de Lixeira

- **Decisão**:
  - **Ações na Interface**:
    - Em `BookView.vue`: Botão/menu "Mover para Lixeira" no cabeçalho do livro (com modal de confirmação) e ícone de lixeira em cada item de estudo listado.
    - Na barra lateral ou menu superior: Link "Lixeira" com ícone e badge com a contagem de itens descartados.
    - Nova view `TrashView.vue`: Listagem com abas ou filtros ("Livros" e "Estudos"), exibindo título, data de descarte, dias restantes até expurgo, botão "Restaurar" e botão "Excluir Definitivamente". No topo, botão em destaque "Esvaziar Lixeira".
  - **Tratamento de Acesso a Itens Descartados**:
    - Tentar acessar `/books/{id}` ou `/studies/{id}` de um item na lixeira retorna HTTP 404 (ou redirecionamento informativo), impedindo edição ou exibição no acervo ativo.
- **Racional**:
  - Clareza visual absoluta e prevenção de perda involuntária de dados através de diálogos de confirmação com visual de perigo para ações destrutivas permanentes.
