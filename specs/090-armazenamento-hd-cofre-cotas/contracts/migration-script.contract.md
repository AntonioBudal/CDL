# Contrato: `scripts/migrate_storage_to_hd.py`

**Feature**: `090-armazenamento-hd-cofre-cotas` (fatia A; `--vault-import` na fatia B)

O script leva o banco, os backups e, na fatia B, as imagens para `LEITORUM_STORAGE_ROOT` (o HD de 1 TB) **sem nunca
alterar o banco de origem**. A troca do caminho ativo é a **última** etapa e só acontece se todas as verificações
passarem.

**Testes:** o script é validado inteiro em `tmp_path` antes de rodar no ambiente real, incluindo cada falha
injetada abaixo.

---

## Modos

| Comando | Efeito |
| :--- | :--- |
| `--target D:\Leitorum --plan` | só lê e relata: origem, tamanhos, espaço livre, sistema de arquivos, pré-condições. Não grava nada. |
| `--target D:\Leitorum --execute` | etapas 0 a 7 |
| `--verify` | confere uma raiz já migrada (marcador, `storage_id`, integridade, revisão Alembic) |
| `--vault-import` (fatia B) | importa as capas e os avatares existentes para o cofre (research R10) |
| `--rollback-info` | mostra o caminho do `.env` anterior e do banco original; não apaga nada |

**Saída:** um relatório JSON **só com números e caminhos** (contagens, tamanhos, hashes), gravado em
`<raiz>/migration-report-<data>.json` e no console. Nenhum conteúdo de estudo.

## Etapas de `--execute`

0. **Pré-condições**, todas obrigatórias:
   - **servidor parado:** a porta configurada está livre **e** não existe o arquivo de trava `leitorum.lock` (que
     o `iniciar.py` passa a criar enquanto roda);
   - **alvo:**
     - caminho absoluto, local (não `\\servidor`) e NTFS;
     - com permissão de escrita e **sem** `db/caderno.db` existente;
     - com espaço livre de pelo menos 3 × (banco + backups + imagens) mais 2 GiB;
   - **chave:** com `--vault-import`, a chave mestra **não** pode estar dentro do alvo;
   - **`.env`:** sem `CADERNO_DATABASE_PATH` definido. Se estiver, o script para e explica a precedência; só segue
     com `--replace-database-path`.
1. **Snapshot pré-migração verificado** no disco de origem, com o serviço de backup existente:
   - API de backup e `integrity_check`;
   - SHA-256 do snapshot registrado no relatório.

   Isso cumpre o `AGENTS.md` §2.
2. **Marcador:** cria `<raiz>/.leitorum-storage.json` com um `storage_id` (UUID) novo e as pastas `db/`,
   `backups/` e `vault/`.
3. **Cópia do banco:**
   - origem aberta com `sqlite3.connect("file:...?mode=ro", uri=True)`;
   - destino `db/caderno.db.tmp`;
   - `src.backup(dst, pages=1024)` com progresso.
4. **Conferência da cópia** (qualquer falha encerra sem trocar nada e remove o `.tmp`):
   - `PRAGMA integrity_check` completo igual a `ok`;
   - `PRAGMA foreign_key_check` vazio;
   - mesma lista de tabelas e mesma contagem de linhas por tabela;
   - **SHA-256 lógico** igual na origem e na cópia, calculado sobre cada tabela em ordem de `rowid` (ou chave
     primária), linha a linha, numa serialização canônica de tipos;
   - `alembic_version` igual;
   - `journal_mode` do destino ajustado para `wal`.
5. **Finalização do banco:**
   - grava `storage_settings.storage_id` na **cópia**, numa transação curta, e confere de novo com `quick_check`;
   - `os.replace` de `caderno.db.tmp` para `caderno.db` e `fsync` da pasta.

   O banco original não é tocado.
6. **Backups:** copia `backups/*.db` e `*.zip` (e, se houver, `covers/` e `avatars/` como legado) com SHA-256 de
   cada arquivo, antes e depois, iguais.
7. **Troca do caminho ativo:**
   - salva o `.env` atual em `.env.bak-<data>`;
   - escreve `LEITORUM_STORAGE_ROOT=<raiz>`;
   - em subprocesso limpo, roda `get_database_path()` e confere que resolve para `<raiz>\db\caderno.db`;
   - abre esse banco em `mode=ro` e confere a revisão Alembic e o `storage_id`.

   Se falhar, restaura o `.env.bak` e encerra.

## Rollback

- O banco e os arquivos de origem **ficam intactos**: o script nunca abre a origem para escrita nem apaga nada
  nela.
- Para voltar, basta restaurar `.env.bak-<data>`. O `--rollback-info` mostra como.
- Recomenda-se manter a origem por pelo menos 30 dias antes de o usuário apagá-la manualmente.

## Falhas injetadas nos testes (em todas, nada é trocado)

| Falha | Esperado |
| :--- | :--- |
| `leitorum.lock` presente ou porta ocupada | para na etapa 0 |
| alvo com `db/caderno.db` existente | para na etapa 0 |
| alvo em caminho de rede ou sem espaço | para na etapa 0 |
| `CADERNO_DATABASE_PATH` no `.env` | para na etapa 0 (sem `--replace-database-path`) |
| `integrity_check` diferente de `ok` na cópia (simulado) | para na etapa 4, remove o `.tmp` |
| SHA-256 lógico diferente (simulado) | para na etapa 4 |
| SHA-256 de um backup copiado diferente | para na etapa 6, mantém o `.env` original |
| subprocesso de conferência resolve outro caminho | restaura o `.env.bak` na etapa 7 |
