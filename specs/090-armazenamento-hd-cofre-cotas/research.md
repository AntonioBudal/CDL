# Research: Armazenamento no HD de 1 TB, Cofre de Imagens Criptografadas e Cotas

**Feature**: `090-armazenamento-hd-cofre-cotas` | **Date**: 2026-10-27 | **Plan**: [plan.md](plan.md)

Auditoria do código atual e decisões técnicas (R1–R12). Cada decisão traz o motivo e as alternativas descartadas.

---

## R0. Auditoria do armazenamento atual

| Módulo | Comportamento hoje | Risco para esta feature |
| :--- | :--- | :--- |
| `app/core/config.py` | `get_database_path()` usa `CADERNO_DATABASE_PATH` ou `backend/data/caderno.db`. `get_backup_dir`, `get_covers_dir` e `get_avatars_dir` derivam do pai do banco e **criam a pasta** (`mkdir(parents=True)`). | Com o HD desconectado ou com outra letra de unidade, o app **cria uma árvore vazia** e um banco novo sem avisar. |
| `app/db/session.py` | `create_sqlite_engine` faz `path.parent.mkdir(...)`. O engine fica em cache por caminho. | Mesmo risco. Não há marcador que prove que a raiz é a certa. |
| `app/services/backups.py` | Snapshot pela API de backup do SQLite, `PRAGMA quick_check`, SHA-256 por arquivo, pacote ZIP com `caderno.db`, `covers/` e `manifest.json`. | Os backups ficam em `<pasta do banco>/backups`, ou seja, **no mesmo disco** do banco. O pacote não conhece o cofre. |
| `app/services/restore_service.py` | Restaura o ZIP numa área isolada, com verificação. | Precisa restaurar também o cofre e checar a impressão digital da chave. |
| `app/services/avatar_service.py` | Recorta para 256 × 256, aplica `exif_transpose`, grava WebP **em claro** em `avatars/`. | O arquivo é aberto. O EXIF some só porque o Pillow não o copia na regravação. |
| `app/routers/profile.py` (`/api/avatars/{arquivo}`) | Serve o arquivo **sem autenticação**, pelo nome. | Qualquer um na rede que saiba o nome baixa o avatar. Os avatares aparecem para amigos e em livros compartilhados (`sharing_service`). |
| `app/services/cover_service.py` e `app/routers/covers.py` | Capas em WebP **em claro** (largura 800); download por URL com validação; `/api/covers/{arquivo}` **sem autenticação**. | Mesmo problema. As capas de livros compartilhados aparecem para outros leitores. |
| `app/services/digitize_service.py` | A foto existe só numa pasta temporária do sistema durante a leitura, e a tela promete que ela é apagada. | Guardar a foto **muda uma promessa feita ao leitor** (feature 086). |
| `app/main.py` (`lifespan`) | Manutenção só na partida, com `get_session()` direto (purga lixeira, categorias, notificações). | Não há tarefa periódica. A sessão direta ignora a sessão de teste; a correção está pendente numa tarefa separada. |
| `requirements.txt` | `cryptography==50.0.1` já instalado (transitivo); Pillow 12.3 com WebP. | AES-GCM e HKDF disponíveis **sem pacote novo**, só declarar como dependência direta. |

## R1. Raiz unificada de armazenamento e falha segura

**Decisão**:
- **Raiz:** `LEITORUM_STORAGE_ROOT`, por exemplo `D:\Leitorum`, com a estrutura:

  ```text
  <raiz>/
  ├── .leitorum-storage.json   # marcador: storage_id (UUID), criado_em, versão do formato
  ├── db/caderno.db            # + caderno.db-wal / -shm
  ├── backups/                 # snapshots e pacotes .zip (cópias dos .enc, sem chave)
  └── vault/<aa>/<media_uuid>.enc   # <aa> = 2 primeiros hex do UUID (evita pastas gigantes)
  ```

- **Precedência**, compatível com o que existe:
  - `CADERNO_DATABASE_PATH`, `CADERNO_COVERS_DIR` e `CADERNO_AVATARS_DIR` explícitos **continuam vencendo**;
  - sem eles, os caminhos derivam de `LEITORUM_STORAGE_ROOT`;
  - sem nenhum dos dois, vale o comportamento atual, em `backend/data/`.
- **Falha segura:** com a raiz configurada, o app só inicia se a pasta existir **e** tiver o marcador
  `.leitorum-storage.json`, com o `storage_id` igual ao registrado em `storage_settings.storage_id` (tabela nova, de uma linha) dentro do próprio
  banco.
  - Sem marcador ou com ID divergente, o `iniciar.py` para com a mensagem "HD de armazenamento não encontrado ou
    diferente do esperado" e **não cria nada**.
  - As funções `get_*_dir` deixam de criar pastas sob uma raiz configurada. Elas só criam subpastas de uma raiz
    válida.

**Alternativa descartada**: só trocar `CADERNO_DATABASE_PATH`. Não resolve a criação silenciosa de um banco vazio
quando o disco some, que é o risco mais grave de levar o banco para outro HD.

**Recomendações ao usuário** (configurações que ele faz, não o app):
- usar HD interno ou externo sempre conectado, formatado em NTFS, e nunca unidade de rede, que é insegura para o
  WAL do SQLite;
- desativar a suspensão do disco para a unidade;
- ativar o **BitLocker** na unidade. O cofre protege só as imagens; o banco (textos dos estudos) e os backups no
  HD ficam legíveis por quem tiver o disco. O Windows 11 Pro inclui BitLocker.

## R2. Formato do arquivo `.enc` (versão 1)

**Decisão**: arquivo binário com cabeçalho fixo de 36 bytes, seguido do texto cifrado com a tag GCM no fim.

| Offset | Tamanho | Campo | Valor |
| ---: | ---: | :--- | :--- |
| 0 | 4 | `magic` | `LMV1` (ASCII) |
| 4 | 1 | `format_version` | `1` |
| 5 | 1 | `cipher_id` | `1` = AES-256-GCM |
| 6 | 1 | `kdf_id` | `1` = HKDF-SHA256 |
| 7 | 1 | `key_epoch` | 0–255 (rotação futura da chave mestra) |
| 8 | 16 | `media_id` | UUID em bytes (o mesmo do nome do arquivo e da linha no banco) |
| 24 | 12 | `nonce` | 96 bits aleatórios (`os.urandom`) |
| 36 | N | `ciphertext` | bytes WebP cifrados |
| 36 + N | 16 | `tag` | tag GCM de 128 bits |

- **Dados associados (AAD)** = os 36 bytes do cabeçalho mais `user_id` em UTF-8.
  - Qualquer alteração no cabeçalho, ou um arquivo copiado para outro usuário ou outra mídia, falha na
    autenticação.
  - O `user_id` não fica no arquivo, porque vem do banco.
- **Chave do arquivo:**

  ```text
  HKDF-SHA256(ikm = chave mestra (32 bytes), salt = "leitorum-media-v1",
              info = "media|" + user_id + "|" + media_id + "|" + key_epoch)
  ```

  O resultado tem 32 bytes.
- **Nonce:** a chave é única por mídia e cada mídia é gravada uma vez, então não há risco de reuso de nonce.
  Mesmo assim, o nonce é aleatório, e uma regravação (rotação) usa nonce novo.
- **Gravação atômica:**
  1. grava em `<uuid>.enc.tmp`, na mesma pasta;
  2. faz `flush` e `os.fsync`;
  3. aplica `os.replace`.

  Um `.tmp` órfão é removido pelo job.
- **Integridade:** o SHA-256 do arquivo inteiro fica no banco, para conferência de backup e migração sem a chave.
  A tag GCM garante a autenticidade na leitura.
- **Implementação:** `cryptography.hazmat.primitives.ciphers.aead.AESGCM` e `...kdf.hkdf.HKDF`, da biblioteca
  `cryptography` (Apache-2.0 / BSD), já instalada. Passa a ser declarada em `requirements.in`.

**Limite conhecido do desenho pedido**: com a chave derivada por HKDF de forma determinística, os bytes de um
arquivo apagado que ainda existam no disco, sem sobrescrita, continuam decifráveis por quem tiver a chave mestra.
"Apagar" libera espaço, mas não é apagamento criptográfico. A alternativa seria uma chave aleatória por arquivo,
embrulhada e guardada na linha do banco. Ela foi descartada nesta fatia porque os backups do banco guardariam a
chave embrulhada do mesmo jeito, o que anula o ganho, e porque o pedido especifica HKDF. O formato reserva
`kdf_id` para essa mudança no futuro.

## R3. Proteção da chave mestra fora do HD

**Decisão**:
- **Chave:** 32 bytes aleatórios, gerados uma vez por `instalar.py --media-key`.
- **Duas formas de guardar, em ordem de preferência:**
  1. **DPAPI do Windows** (`CryptProtectData` via `ctypes`, escopo do usuário atual), em
     `%LOCALAPPDATA%\Leitorum\media-master.key`, no disco do sistema;
  2. `LEITORUM_MEDIA_MASTER_KEY` (base64) no `.env` do sistema principal, para ambientes sem DPAPI.
- **Barreira na partida:** o app **recusa** iniciar o cofre se o caminho da chave ou do `.env` resolver para dentro
  de `LEITORUM_STORAGE_ROOT` (mesma unidade e prefixo). A chave **nunca** vai para o HD, para logs, para backups
  ou para o pacote ZIP.
- **Impressão digital:** `HKDF(chave, info="fingerprint")[:8]` em hexadecimal, gravada em `storage_settings`. Na
  partida, chave errada ou ausente é detectada uma vez, com estado `vault: key_mismatch`, em vez de falhar imagem
  por imagem.
  - Sem a chave certa, o cofre fica **só para leitura do índice**: a lista e a cota funcionam, mas imagens não
    abrem nem gravam.
  - O resto do Leitorum funciona normalmente.
- **Recuperação:**
  - na criação, o instalador mostra uma única vez um **código de recuperação** (a chave em base32, em grupos),
    para o usuário anotar ou guardar num pendrive;
  - `instalar.py --media-key --restore` aceita esse código.
  - **Sem a chave, as imagens são irrecuperáveis.** Isso vai escrito na tela e no `LEIA-ME`.
- **DPAPI está atrelado à conta do Windows.** Reinstalar o sistema ou trocar de usuário perde o acesso sem o
  código de recuperação.

## R4. Pipeline de gravação

1. **Validação:**
   - formatos JPEG, PNG e WebP;
   - limites atuais: 20 MB e 40 MP para páginas, 2 MB para avatar, 5 MB para capa.
2. **Sanitização:**
   - `exif_transpose`;
   - conversão para RGB, ou RGBA no avatar;
   - regravação **sem** os parâmetros `exif=`, `icc_profile=` e `xmp=`. Nenhum metadado de origem sobrevive,
     incluindo GPS, data e aparelho.
3. **Otimização por tipo:**

   | Tipo | Regra |
   | :--- | :--- |
   | `notebook_page` | lado maior até 2000 px (Lanczos), WebP qualidade 80, `method=6` |
   | `avatar` | 256 × 256, WebP qualidade 85 (como hoje) |
   | `cover` | largura até 800 px, WebP qualidade 85 (como hoje) |

   A meta para páginas é de 300 a 400 KB, a ser medida na validação com páginas fictícias. A legibilidade é
   conferida rodando o motor de leitura na imagem otimizada contra a original, com páginas fictícias.
4. **Reserva de cota** (R7), depois cifragem (R2), gravação atômica e confirmação da linha.

**Exceção declarada**: durante a leitura da digitalização, o motor precisa da imagem em claro numa pasta
temporária do **sistema** (disco C:), como na 086. Ela é apagada no fim do pedido e **nunca** vai para o HD. A
versão guardada para conferência é a otimizada e cifrada.

## R5. Pipeline de leitura e autorização

- **Endpoint:** `GET /api/media/{id}/content`. Ele:
  1. exige sessão;
  2. aplica a **regra de acesso por tipo**;
  3. decifra em memória;
  4. devolve `image/webp` com os cabeçalhos:
     - `Cache-Control: private, no-store, no-cache, max-age=0`;
     - `Pragma: no-cache`;
     - `X-Content-Type-Options: nosniff`;
     - `Content-Disposition: inline`.
- **Regras de acesso:**

  | Tipo | Quem lê |
  | :--- | :--- |
  | `notebook_page` | **só o dono** (`media.user_id == current_user.id`) |
  | `avatar` | **qualquer usuário logado sem bloqueio com o dono** (`is_blocked_between`). Os avatares aparecem em listas de amigos, pedidos, busca e livros compartilhados; exigir "ver o perfil" quebraria essas telas. Hoje eles são públicos até para quem não está logado |
  | `cover` | quem pode ler o livro: `can_read_book` do `sharing_service` (dono; público; amigos; bloqueio nega) |

  Restringir avatar e capa só ao dono quebraria o perfil, as amizades e os livros compartilhados, que já existem.
- **Resposta para quem não pode ver:** `404`, e não `403`, para não revelar a existência da mídia.
- **Miniaturas:** `GET /api/media/{id}/thumbnail` decifra e reduz para 320 px na hora, sem guardar nada. O custo
  estimado é de 20 a 40 ms por imagem, carregada sob demanda na grade.
- **Rotas antigas:** `/api/avatars/{arquivo}` e `/api/covers/{arquivo}` continuam funcionando durante a transição,
  resolvendo para a mídia cifrada pela referência no banco e com a **mesma** regra de acesso. Ao final, deixam de
  servir arquivos em claro.

## R6. Ciclo de vida e retenção das fotos de conferência

- **Opção, não padrão escondido:** na revisão da digitalização, a caixa "Guardar a foto com o estudo para
  conferência" decide se a foto fica. Ela mostra a retenção e a cota.
  - O valor inicial está na decisão Q1 de [spec.md](spec.md).
  - O texto de transparência da tela muda conforme a escolha.
- **Vínculo em duas etapas:**
  1. a pré-visualização devolve `media_id`, com estado `pending` e validade de 24 h;
  2. depois de `POST /api/studies`, o frontend chama `POST /api/media/{id}/attach {study_id}`.

  O schema do Estudo não muda. Uma foto não vinculada em 24 h é apagada pelo job.
- **Independência do texto:** `encrypted_media.study_id` usa `ON DELETE SET NULL`. Apagar uma mídia **nunca** toca
  em `studies`. Apagar um estudo (lixeira) não apaga a foto na hora: quando o estudo é purgado, a foto fica órfã e
  o job a remove depois de 7 dias.
- **Regras do job:**

  | Regra | Condição | Padrão |
  | :--- | :--- | :--- |
  | Expiração por idade | `kind = notebook_page`, `keep_forever = false` e `expires_at <= agora` | `expires_at = created_at + LEITORUM_MEDIA_RETENTION_DAYS` (30) |
  | Estudo concluído | estudo vinculado com `reading_status = 'concluido'` há mais de `LEITORUM_MEDIA_COMPLETED_GRACE_DAYS` (7) | ligado (`LEITORUM_MEDIA_DELETE_ON_COMPLETED=true`) |
  | Nunca expiram | avatares e capas | — |
  | Sem vínculo | `pending` com mais de 24 h; `study_id` nulo há mais de 7 dias | — |

  A espera de 7 dias depois de "concluído" protege contra marcar por engano.
- **Job:**
  - roda na partida, dentro do `lifespan`, e a cada `LEITORUM_MEDIA_JOB_INTERVAL_HOURS` (6), numa tarefa `asyncio`
    criada no `lifespan` e cancelada no desligamento;
  - usa sessão do engine configurado e trabalha em lotes de 200;
  - nunca registra nomes ou títulos em log, só contagens e bytes;
  - também reconcilia o cofre: `.tmp` velhos, arquivos sem linha (órfãos) e linhas cujo arquivo sumiu, que ficam
    `missing`, visíveis ao usuário.
- **Apagamento em duas fases:**
  1. a linha passa a `deleting`;
  2. o arquivo é apagado;
  3. a linha é apagada.

  Uma falha no meio é retomada pelo job. A cota só conta linhas `active` e `pending`.

## R7. Cotas

- **Configuração:**
  - `LEITORUM_USER_STORAGE_QUOTA_BYTES`, padrão `1_073_741_824` (1 GiB);
  - `LEITORUM_GLOBAL_STORAGE_QUOTA_BYTES`, padrão `966_367_641_600` (900 GiB);
  - `LEITORUM_STORAGE_FREE_MARGIN_BYTES`, padrão 2 GiB.
- **O que conta:** o tamanho em disco do `.enc` (`byte_size`), de linhas `active`, `pending` e `deleting`.
- **Verificação atômica:** a gravação faz, sob um `threading.Lock` do processo (o servidor é processo único):
  1. soma o uso do usuário e o global (consultas indexadas);
  2. confere a cota do usuário, a cota global e o espaço livre real com `shutil.disk_usage(raiz).free - margem`;
  3. insere a linha `pending` com o tamanho;
  4. libera o lock e grava o arquivo.

  Na falha, a linha é removida.
- **Recusa:** `507 Insufficient Storage` com código `user_quota` ou `server_quota`, mais a mensagem que aponta
  "Minhas Imagens e Espaço" e os tamanhos atuais.
- **Contagem por usuário:** avatares e capas contam na cota do dono. São pequenos, mas consomem o mesmo disco.

## R8. Migração para o HD (script)

O protocolo completo está em [contracts/migration-script.contract.md](contracts/migration-script.contract.md). Em
resumo:
- o banco de origem é aberto **só para leitura** (`mode=ro`);
- a cópia é feita pela API de backup;
- conferência na cópia: `PRAGMA integrity_check` completo, `foreign_key_check`, contagem por tabela, **SHA-256
  lógico** das linhas em ordem canônica (iguais na origem e na cópia) e revisão Alembic igual;
- a troca do caminho ativo é só a reescrita do `.env`, com backup do `.env` anterior;
- **o banco original fica intacto** como rollback.

**Por que não comparar o SHA-256 do arquivo**: o backup do SQLite pode reorganizar páginas livres e o estado do
WAL. Arquivos com conteúdo idêntico podem ter bytes diferentes. O SHA-256 por arquivo vale para os backups `.db` e
`.zip` copiados, que são cópias de bytes. Para o banco ativo, vale a comparação lógica.

**Requisito do `AGENTS.md`**: antes de qualquer migração Alembic no banco ativo, é preciso um backup consistente e
verificado. A migração das tabelas novas acontece **depois** da mudança de disco, sobre o banco já no HD, com o
snapshot pré-migração do Leitorum.

## R9. Backups, restauração, exportação e exclusão de conta

- **Pacote de backup:**
  - passa a incluir `vault/**.enc` (cifrados) e, no `manifest.json`, o SHA-256 de cada `.enc`, a impressão digital
    da chave e o `storage_id`;
  - nunca inclui a chave.
- **Restauração:** confere a impressão digital. Com outra chave, restaura o banco e o cofre, mas avisa que as
  imagens só abrem com a chave original (código de recuperação).
- **Segunda cópia:** recomendar, e oferecer por configuração, `LEITORUM_SECONDARY_BACKUP_DIR` no C: ou noutro
  disco. Backup só no mesmo HD não protege contra perda do HD.
- **Exportação de conta (LGPD):** o ZIP de exportação inclui as imagens do usuário **decifradas**, porque
  portabilidade exige formato aberto.
- **Exclusão de conta:** apaga todas as mídias do usuário em duas fases, antes de remover o usuário.

## R10. Migração das capas e avatares existentes para o cofre

Etapa separada do script, `--vault-import`, executada depois que o cofre estiver ativo:
1. para cada arquivo referenciado em `books.cover_image` e `user_profiles.avatar_url`: sanitizar, cifrar, criar a
   linha e atualizar a referência para a mídia;
2. decifrar de volta e comparar com o WebP gerado;
3. os originais em claro **não são apagados** pelo script, que lista o que pode ser apagado depois da confirmação
   do usuário.

## R11. Fatiamento (Constituição IV.1)

A arquitetura é grande demais para uma fatia. A proposta são três features, cada uma com o próprio ciclo
spec → plan → tasks e o próprio commit:

| Fatia | Conteúdo | Muda o banco? |
| :--- | :--- | :--- |
| **090-A** | raiz `LEITORUM_STORAGE_ROOT`, falha segura, script de migração para o HD, segunda cópia de backup | só `storage_settings.storage_id` (tabela nova, de uma linha) (migração pequena) |
| **090-B** | cofre: formato `.enc`, chave mestra, `encrypted_media`, avatares e capas no cofre, rotas com autorização, backup e restauração do cofre | sim (tabela nova) |
| **090-C** | fotos de conferência na digitalização, visualizador no estudo, retenção e job, "Minhas Imagens e Espaço", cotas | não (usa a tabela da B) |

Cada fatia passa sozinha por `pytest`, `npm test` e `npm run build`. A A pode ir para produção sem a B. A C depende
da B.

## R12. Testes

- **Isolamento:** tudo em `tmp_path`, com raiz falsa de "HD", banco descartável e chave mestra de teste gerada no
  teste.
- **Cripto:**
  - ida e volta;
  - tag adulterada, cabeçalho adulterado, arquivo trocado entre usuários e chave errada devem falhar;
  - nonces distintos;
  - nenhum EXIF depois da sanitização, conferido com imagem fictícia que tem GPS falso.
- **Migração:** caminho feliz e injeção de falhas (integridade, hash lógico, destino existente, lock do servidor,
  `.env` com `CADERNO_DATABASE_PATH`). Em toda falha, **nada é trocado**.
- **Cotas:** limite exato, concorrência simulada e espaço livre falso (monkeypatch de `disk_usage`).
- **Job:** relógio injetável; expiração; "manter permanentemente"; estudo concluído com espera; órfãos;
  reconciliação.
- **Autorização:** a matriz de acesso da R5, com usuários fictícios.
