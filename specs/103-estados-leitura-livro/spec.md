# Feature Specification: F0.11.01 — Estados de Leitura do Livro

**Feature Branch**: `103-estados-leitura-livro`

**Created**: 2026-11-09

**Status**: Concluída em 2026-11-09 (US4 revista na execução, ver abaixo)

**Input**: Primeiro item do Roadmap 0.11 (motores) no HANDOFF: "Estados de leitura do livro (exige migração)". Base para
os círculos de leitura do 1.0. Primeira feature do lote 1 do 0.11.

---

## 1. Contexto (auditoria de 2026-11-09, só código)

| Ponto | Situação | Onde |
|---|---|---|
| Estado do **estudo** | Existe: `studies.reading_status` (`rascunho`, `em_estudo`, `revisado`, `concluido`) — é o andamento do fichamento, não da leitura do livro | `models/study.py`, `schemas/study_grouping.py` |
| Estado do **livro** | **Não existe**. `books` tem título, autor, subtítulo, ano, capa, visibilidade e versão; nada sobre "quero ler", "lendo", "lido" ou datas | `models/book.py`, `schemas/book.py` |
| Gravação | `PATCH /api/books/{id}` aplica os campos enviados com controle de versão (`expected_version`); acrescentar campos ao `BookPatch` basta | `routers/books.py` |
| Exportação | O `.zip` da conta e o Markdown do livro levam título, autor, subtítulo, ano e categorias | `services/export_service.py` |
| Migrações | Alembic em `backend/migrations/versions`, última `0033_organizer_feedback` | — |
| **Implantação** | `iniciar.py` **recusa iniciar** quando a revisão do banco não é a última do código ("Execute INSTALAR.cmd ou 'alembic upgrade head'"). O `instalar.py` roda `alembic upgrade head` **sem fazer backup antes** | `iniciar.py`, `instalar.py` |

**Consequência para a implantação:** depois do push, o serviço só volta a subir quando o banco ativo receber a
migração. Pelo AGENTS.md §2, isso exige pedido explícito e backup verificado antes. Esta feature entrega a migração e
um script que faz backup, verifica e só então migra (US4); **quem roda no banco ativo é você** (ou eu, se você pedir).

---

## 2. User Stories

### US1 — Marcar o estado de leitura de um livro (P1)

**Acceptance**:
1. Estados: **Quero ler**, **Lendo**, **Lido**, **Abandonado**, ou nenhum (padrão de todos os livros existentes —
   nada é inventado na migração).
2. Na página do livro, abaixo do autor, um seletor de estado (`radiogroup`, teclado com setas) e as datas
   **Início** e **Fim** (opcionais, editáveis).
3. Ao passar para **Lendo** sem data de início, ela vira hoje; para **Lido** sem data de fim, ela vira hoje. Datas
   já preenchidas não mudam. Voltar para "nenhum" ou "Quero ler" mantém as datas (o leitor apaga se quiser).
4. Fim antes do início é recusado com mensagem clara (422).
5. Grava pelo `PATCH` existente com `expected_version`; conflito de versão mostra a mensagem atual de conflito.

### US2 — Ver e filtrar pela biblioteca (P1)

**Acceptance**:
1. Cada cartão/linha de livro mostra um selo discreto com o estado (sem selo quando não há estado).
2. A barra da biblioteca ganha o filtro de estado (Todos · Quero ler · Lendo · Lido · Abandonado · Sem estado),
   combinável com busca e categoria, lembrado no navegador.

### US3 — Os dados saem junto (P1)

**Acceptance**: o `.zip` da conta (JSON) e o Markdown do livro levam `reading_state`, `reading_started_on` e
`reading_finished_on`. Na API, livros de terceiros (compartilhados) **não** expõem o estado nem as datas — é dado
pessoal; os círculos de leitura do 1.0 decidem o que compartilhar.

### US4 — Migração com backup verificado (P1)

> **Revista na execução (2026-11-09):** a auditoria inicial não viu que `migrations/env.py` já chama
> `maintenance.ensure_pre_upgrade_snapshot` antes de qualquer migração: o `alembic upgrade head` cria e valida um
> snapshot (`create_database_backup`), copia para a segunda pasta de backups e **aborta** se o snapshot falhar; e
> `python -m app.services.maintenance verificar-snapshot` confere o arquivo. O script novo
> `scripts/migrar_com_backup.py` duplicaria isso e **não foi criado**; os itens 2 a 4 abaixo ficam atendidos pelo
> mecanismo existente, com o procedimento no HANDOFF. Um teste novo prova que o upgrade para a 0034 gera o snapshot.

**Acceptance**:
1. Migração `0034_book_reading_state`: três colunas novas em `books` (`reading_state` texto nulo com `CHECK` nos
   quatro valores; `reading_started_on` e `reading_finished_on` datas nulas), índice `(user_id, reading_state)`.
   `downgrade` remove (modo batch do SQLite). Nenhum dado existente é alterado.
2. Script `scripts/migrar_com_backup.py`: lê o caminho do banco da configuração, cria um backup com
   `create_database_backup` na pasta de backups, confere com `verify_sqlite_integrity`, confere que a revisão do
   backup é a mesma do banco, **só então** roda `alembic upgrade head`, e no fim roda `quick_check` no banco migrado.
   Qualquer falha antes da migração para tudo sem tocar o banco. Mostra o caminho do backup.
3. O script recusa rodar com o serviço Leitorum ativo (mensagem pedindo `Stop-Service -Name Leitorum`).
4. Testes do script só em `tmp_path` (banco descartável com dados fictícios).

### Edge Cases

- Livro na lixeira mantém o estado; restaurado, volta com ele.
- Data futura é aceita (planejamento), mas fim > hoje + 1 dia não é bloqueado — só fim < início.
- Livro de outro leitor aberto por compartilhamento: o seletor não aparece.
- Celular (375/320 px): o seletor quebra linha; datas empilham.

---

## 3. Requirements

- **FR-001**: Modelo `Book`: `reading_state: str | None`, `reading_started_on: date | None`,
  `reading_finished_on: date | None`; migração `0034`.
- **FR-002**: `BookPatch` aceita os três (`Literal` para o estado, datas ISO); validação cruzada no serviço; regra de
  datas automáticas ao mudar o estado; `BookRead` devolve os três só ao dono.
- **FR-003**: Exportação JSON e Markdown com os campos.
- **FR-004**: Frontend: tipos, `BookReadingState.vue` (seletor + datas) na `BookView`, selo nos cartões, filtro em
  `useLibraryFilter`/`LibraryToolbar` com `localStorage` (com `try/catch`).
- **FR-005**: `scripts/migrar_com_backup.py` como descrito na US4.
- **FR-006**: Só tokens, `.quiet` nos controles não selecionados, alvos de 44 px, contraste ≥ 4,5:1 nos 10 temas.

## 4. Success Criteria

- **SC-001**: Testes de backend: migração sobe e desce em banco descartável (dados fictícios preservados);
  `PATCH` com estados e datas, datas automáticas, fim < início → 422, conflito de versão; estado oculto para
  terceiros; exportação com os campos; script de migração (sucesso, backup criado e íntegro, falha antes da
  migração não toca o banco, recusa com serviço ativo simulado).
- **SC-002**: Testes de frontend: seletor como `radiogroup`, datas, selo, filtro e persistência.
- **SC-003**: Navegador (servidor de validação, banco temporário migrado): marcar estados, datas automáticas,
  filtro, 1366 e 375 px, contraste nos 10 temas.
- **SC-004**: `npm run build`, testes novos e vizinhos (livros, exportação, sincronização, compartilhamento);
  commit; levar ao `main`.
- **SC-005**: Instruções de implantação no relatório final: parar o serviço, rodar o script, conferir o backup,
  reiniciar. Eu não rodo no banco ativo sem você pedir.

## 5. Fora do escopo

- Estado de leitura por capítulo (a "bandeja de triagem por capítulo" é outro item do 0.11).
- Painéis e metas de leitura (livros lidos por ano), histórico de releituras.
- Compartilhar o estado com amigos (círculos de leitura, 1.0).
- Mudar o `reading_status` dos estudos.
