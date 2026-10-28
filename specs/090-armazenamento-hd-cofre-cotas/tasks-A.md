# Tasks — Fatia 090-A: Raiz Única no HD de 1 TB e Migração Segura

**Input**:
- [spec.md](spec.md) (US1; FR-001 a FR-003; NR-001 e NR-002);
- [plan.md](plan.md), [research.md](research.md) (R1, R8, R9);
- [data-model.md](data-model.md) (§1 e §5);
- [contracts/migration-script.contract.md](contracts/migration-script.contract.md).

**Escopo da fatia A**:
- raiz `LEITORUM_STORAGE_ROOT` com marcador e falha segura;
- tabela `storage_settings`;
- trava do servidor (`leitorum.lock`);
- segunda cópia de backup;
- script `scripts/migrate_storage_to_hd.py`.

Cofre, chave e imagens ficam para a fatia B. Fotos de conferência, retenção e cotas ficam para a C.

Caminhos relativos a `C:\Users\User\caderno`; `L/` = `caderno-leitura-0.1/`.

**Regras em todas as tarefas**:
- nunca abrir, ler ou alterar `L/backend/data/caderno.db` nem o HD real durante o desenvolvimento;
- testes só em `tmp_path`, com raiz falsa de "HD" e banco descartável;
- o `pytest` roda com `CADERNO_DATABASE_PATH` descartável;
- nenhum relatório com conteúdo de estudos;
- o `.env` real nunca é impresso.

---

## Phase 1: Setup — linha de base

- [X] A001 Registrar a linha de base: `pytest` com banco descartável, `npm test` e `npm run build`. Só contagens.

## Phase 2: Fundação — raiz, marcador e falha segura

- [X] A002 Criar `L/backend/app/core/storage.py`:
  - `StorageError`;
  - `read_marker(root)`, `write_marker(root, storage_id)` (JSON `{storage_id, created_at, format: 1}`, gravação
    atômica);
  - `verify_root(root, expected_storage_id | None)`.

  Mensagens em português, sem caminhos internos nas respostas da API.
- [X] A003 Em `L/backend/app/core/config.py`:
  - **`get_storage_root()`:** lê `LEITORUM_STORAGE_ROOT`; exige caminho absoluto; **não cria** a pasta;
  - **precedência:** `CADERNO_DATABASE_PATH` > `<raiz>/db/caderno.db` > `backend/data/caderno.db`. Igual para
    capas e avatares (legado em `<raiz>/covers` e `<raiz>/avatars`) e backups (`<raiz>/backups`);
  - **criação de subpastas:** `get_backup_dir`, `get_covers_dir` e `get_avatars_dir` só criam subpastas de uma
    raiz **com marcador**. Sem marcador, levantam `StorageError`;
  - **`get_secondary_backup_dir()`:** a partir de `LEITORUM_SECONDARY_BACKUP_DIR`; recusa se estiver dentro da
    raiz.
- [X] A004 Criar o modelo `L/backend/app/models/storage_settings.py` (data-model §1, `CHECK (id = 1)`) e a migração
  `L/backend/migrations/versions/0030_storage_settings.py`, com upgrade e downgrade. O snapshot pré-migração já é
  automático (`ensure_pre_upgrade_snapshot`). Testar o upgrade e o downgrade em `tmp_path`.
- [X] A005 Em `L/backend/app/db/session.py`, quando `LEITORUM_STORAGE_ROOT` estiver ativo, `get_engine()` chama
  `ensure_storage_ready()` antes de criar o engine. Ela:
  - confere que o marcador existe;
  - confere que o `storage_id` do marcador é igual ao de `storage_settings` (lido em `mode=ro`);
  - levanta `StorageError` caso contrário.

  A verificação roda **uma vez por caminho**, junto do engine em cache, e não a cada requisição.

  O `create_sqlite_engine` deixa de criar a pasta do banco sob raiz configurada. Sem raiz configurada, nada muda
  (testes e instalações atuais).
- [X] A006 Em `L/iniciar.py`:
  - **verificação da raiz:** antes de importar o app, confere a raiz. Em falha, imprime "HD de armazenamento não
    encontrado ou diferente do esperado" com a orientação e sai com código 1, sem criar nada;
  - **trava `L/leitorum.lock`:** JSON com `pid`, `port` e `started_at`, criado ao iniciar e removido ao sair. Uma
    trava de PID inexistente é tratada como velha (verificação via `ctypes` `OpenProcess` no Windows);
  - **informação:** imprime "Armazenamento: <raiz>" quando configurado.
- [X] A007 Em `L/backend/app/services/backups.py`, depois de criar snapshot ou pacote, copia para
  `get_secondary_backup_dir()`, se configurado, com SHA-256 conferido. Uma falha na segunda cópia gera aviso e não
  invalida o backup principal. Aplicar também ao snapshot pré-migração.
- [X] A008 Criar `L/backend/tests/test_storage_root.py` (tudo em `tmp_path`), cobrindo:
  - **precedência:** as variáveis `CADERNO_*` vencem a raiz;
  - **caminhos derivados** da raiz;
  - **nenhuma pasta criada** com raiz ausente, sem marcador ou com `storage_id` divergente (o engine se recusa);
  - **segunda cópia:** com hash conferido, e recusa quando está dentro da raiz;
  - **trava:** criada e removida; trava velha ignorada;
  - **compatibilidade:** sem raiz, tudo igual a hoje;
  - **HD que some com o servidor rodando** (edge case da spec): pastas renomeadas depois da partida; as
    requisições que tocam o banco recebem `503` pelo manipulador existente, e nenhum banco ou pasta é criado em
    outro lugar.

**Checkpoint**: com a raiz configurada e o HD "ausente", nenhum arquivo é criado e o app explica o motivo.

## Phase 3: Script de migração (US1)

- [X] A009 Criar `L/scripts/migrate_storage_to_hd.py`:
  - modos `--plan`, `--execute`, `--verify` e `--rollback-info`;
  - relatório JSON só com números e caminhos;
  - não importa o app para escrever em lugar nenhum;
  - funções testáveis, com caminhos injetáveis (raiz do projeto, `.env`, porta).
- [X] A010 Pré-condições (etapa 0 do contrato):
  - **servidor parado:** trava e porta;
  - **alvo:** caminho absoluto e local (recusa `\\`); sistema de arquivos NTFS via `GetVolumeInformationW`;
    espaço livre ≥ 3 × (banco + backups + pastas legadas `covers/` e `avatars/`) + 2 GiB; sem
    `db/caderno.db` existente;
  - **`.env`:** sem `CADERNO_DATABASE_PATH`, ou com `--replace-database-path`;
  - **revisão do banco de origem:** igual à `head`, com `storage_settings` existente. Se não, o script para e
    orienta a rodar a atualização normal antes.
- [X] A011 Snapshot pré-migração verificado na origem, pelo serviço de backup existente: integridade e SHA-256 no
  relatório. Mais a segunda cópia, se configurada.
- [X] A012 Cópia e conferência (etapas 2 a 4):
  - marcador novo;
  - origem aberta em `file:...?mode=ro`;
  - `backup()` com progresso para `db/caderno.db.tmp`;
  - **conferência:** `integrity_check` completo, `foreign_key_check`, mesma lista de tabelas e contagens, SHA-256
    lógico por tabela (ordem de chave primária e serialização canônica de tipos), `alembic_version` igual e
    `journal_mode = wal` no destino.

  Em falha, remove o `.tmp` e o marcador recém-criado.
- [X] A013 Finalização (etapa 5):
  - grava `storage_settings` (`id = 1` e `storage_id`) **na cópia**;
  - roda `quick_check`;
  - `os.replace` de `.tmp` para `caderno.db` e `fsync` da pasta.
- [X] A014 Backups (etapa 6): copia `backups/*.db` e `*.zip`, e as pastas legadas `covers/` e `avatars/`, com
  SHA-256 antes e depois de cada arquivo.
- [X] A015 Troca (etapa 7):
  - salva o `.env` em `.env.bak-<data>`;
  - escreve `LEITORUM_STORAGE_ROOT`, preservando as outras linhas e sem imprimir valores;
  - em subprocesso limpo, confere `get_database_path()`, a revisão Alembic e o `storage_id`;
  - em falha, restaura o `.env.bak`.

  `--rollback-info` lista o `.env.bak` e a origem.
- [X] A016 Criar `L/backend/tests/test_migrate_storage_to_hd.py` (tudo em `tmp_path`, banco fictício migrado até a
  `head` com alguns livros e estudos fictícios), cobrindo:
  - **caminho feliz:** contagens e SHA-256 lógico iguais; o app, apontado para a raiz nova, abre o banco;
    `--verify` passa;
  - **origem intacta:** o SHA-256 do **arquivo** de origem é igual antes e depois;
  - **cada falha injetada da tabela do contrato:** nenhuma troca, `.env` igual e origem intacta;
  - **`--plan`:** não grava nada (varredura de arquivos antes e depois).

**Checkpoint**: o script passa por todas as falhas sem trocar nada e o caminho feliz abre o banco na raiz nova.

## Phase 4: Documentação e instalação

- [X] A017 Atualizar a documentação de instalação e ambiente (`L/LEIA-ME-0.1.md` ou `L/docs/contexto/AMBIENTE-E-VALIDACAO.md`)
  e o `.env.example`, se existir:
  - `LEITORUM_STORAGE_ROOT`, `LEITORUM_SECONDARY_BACKUP_DIR` e a precedência;
  - o passo a passo da migração (`--plan`, aprovação, `--execute`, `--verify`) e o rollback;
  - recomendações: HD NTFS sempre conectado, sem suspensão do disco, **BitLocker** na unidade.

## Phase 5: Validação e registro

- [X] A018 Rodar `pytest` (com `CADERNO_DATABASE_PATH` descartável), `npm test` e `npm run build`, e comparar com a
  linha de base.
- [X] A019 Atualizar `L/docs/contexto/RETOMADA.md` e criar **um** commit `feature — armazenamento no HD com
  migração segura`.

## Phase 5b: Camadas extras de proteção (pedido do usuário, 2026-10-27: "quero as camadas 2 e 3")

Proteger a pasta inteira por permissão do Windows quebraria o SQLite, a rotação de backups e a restauração. A
proteção real contra perda são **cópias em outros lugares**.

- [X] A024 **Backup automático diário (camada 2):**
  - em `L/backend/app/services/maintenance.py`, a função `run_auto_backup_if_due(now)` cria
    `caderno-auto-<data>.db` na pasta de backups quando o último automático tem mais de
    `LEITORUM_AUTO_BACKUP_HOURS` (padrão 24; `0` desliga);
  - usa a API de backup com verificação de integridade, faz a segunda cópia (`copy_to_secondary`) e mantém os
    `LEITORUM_AUTO_BACKUP_KEEP` mais recentes (padrão 14) **nas duas pastas**, apagando só arquivos
    `caderno-auto-*`;
  - em `L/backend/app/main.py`, uma tarefa `asyncio` no `lifespan` roda a verificação na partida e a cada hora,
    em thread separada, e é cancelada no desligamento;
  - desligada sob pytest, salvo pedido explícito.
- [X] A025 Testes em `tmp_path`:
  - criação quando vence;
  - nada antes do prazo;
  - rotação só dos automáticos (snapshots pré-migração e pacotes intactos);
  - segunda cópia com rotação;
  - `0` desliga.
- [X] A026 **"Proteção do sistema" no `D:\` (camada 3):** instruções passo a passo na documentação e no relatório
  final. **O usuário ativa**, por ser configuração de segurança do Windows.

## Phase 6: Execução no ambiente real (PORTÃO; só com aprovação explícita em chat)

Esta fase não roda automaticamente. Cada passo abaixo espera a sua confirmação.

- [X] A020 Você informa o caminho no HD (por exemplo `D:\Leitorum`) e se quer a segunda cópia de backup (e onde, fora
  do HD).
- [X] A021 Com o servidor parado, rodo a atualização normal do banco: `alembic upgrade head` pela instalação, que cria
  o snapshot pré-migração verificado automaticamente. Ela aplica a migração `0030` no banco ativo. **Só com a sua
  aprovação.**
- [X] A022 Rodo `--plan` contra o banco real e o HD. O banco é só lido e nada é gravado. Apresento o relatório.
- [X] A023 Com a sua aprovação do relatório, rodo `--execute`, depois `--verify`, e informo como voltar atrás.

---

**Resultado da fatia A (2026-10-27):**
- linha de base: backend 513 aprovados / 1 pulado; frontend 633 aprovados;
- depois da fatia: backend **541 aprovados / 1 pulado** (+28: 15 da raiz de armazenamento e 13 do script de
  migração); frontend 633; build ok;
- todas as falhas injetadas do contrato terminam sem troca, com origem e `.env` intactos.

A fase 6 (A020–A023) espera o usuário. O alvo informado é `D:\`, com a pasta sugerida `D:\Leitorum`.

## Dependencies & Execution Order

A001 → A002 → A003 → A004 → A005 → A006 / A007 [P] → A008 → A009 → A010 … A015 → A016 → A017 → A018 → A019 → (portão) A020 → A021 → A022 → A023.

## Cobertura

| Requisito | Tarefas |
| :--- | :--- |
| FR-001 | A003, A008 |
| FR-002 | A002, A004, A005, A006, A008 |
| FR-003 | A009–A016, A020–A023 |
| NR-001 | A004 (snapshot automático), A011, A016, A021–A023 |
| NR-002 | A008, A016 |
| Q6 (segunda cópia) | A003, A007, A011 |
| SC-001 | A016 |
| SC-008 | A018 |
