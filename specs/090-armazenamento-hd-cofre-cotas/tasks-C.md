# Tasks — Fatia 090-C: Fotos de Conferência, Retenção, "Minhas Imagens e Espaço" e Cotas

**Input**:
- [spec-C.md](spec-C.md) (US3 a US7, FR-C01 a FR-C13, SC-004 a SC-006, SC-009 e SC-010; decisões C-Q1 a C-Q4);
- [plan-C.md](plan-C.md) (§1 a §9);
- [plan.md](plan.md) (desenho das telas);
- [data-model.md](data-model.md) (§2 a §5).

**Escopo da fatia C**:
- cotas atômicas em toda gravação no cofre, com `507`;
- foto de conferência guardada ao salvar o estudo (`POST /api/studies/{id}/media`);
- job de retenção e reconciliação do cofre;
- API: `usage`, lista enriquecida, `PATCH` de "manter", apagamento em lote e fotos do estudo;
- telas: "Minhas Imagens e Espaço", "Folha original" e a caixa na digitalização.

**Decisões desta fatia** (aprovadas em 2026-10-28):
- **C-Q1 A:** a foto é reenviada pelo navegador ao salvar. O `preview` não muda, e `attach` e `keep_photo` saem
  do contrato.
- **C-Q2 A:** `encrypted_media.completed_seen_at`, preenchida pelo job (migração `0032`).
- **C-Q3:** o lote "estudos concluídos" apaga na hora, sem os 7 dias.
- **C-Q4:** só o administrador vê os números do servidor. Os demais veem o nível.

Caminhos relativos a `C:\Users\User\caderno`; `L/` = `caderno-leitura-0.1/`.

**Regras em todas as tarefas**:
- testes só em `tmp_path`, com o cofre isolado (`isolated_media_vault`), chave de teste, imagens e textos
  fictícios;
- o `pytest` roda com `CADERNO_DATABASE_PATH` descartável, mais `LEITORUM_STORAGE_ROOT=""` e
  `LEITORUM_SECONDARY_BACKUP_DIR=""`;
- nenhum teste toca o banco ativo nem `D:\`;
- logs só com contagens e bytes, nunca ids, títulos ou bytes de imagem;
- não rodar `npm run build` em paralelo com o `pytest` (o build esvazia `frontend/dist` e quebra o teste do
  `iniciar.py`).

---

## Phase 1: Setup

- [x] C001 Linha de base: `pytest` (595 aprovados e 1 pulado), `npm test` (639) e `npm run build`.

## Phase 2: Configuração, migração e modelo

- [x] C002 Em `L/backend/app/core/config.py`, criar os 7 `get_*` do plan-C §1 (cotas, margem, retenção, conclusão,
  espera e intervalo), com os padrões do data-model §5.
  - `validate_media_settings()` levanta `ValueError` com o nome da variável quando o valor é inválido: não
    inteiro, ≤ 0, ou retenção fora de 1–3650 dias.
- [x] C003 Chamar `validate_media_settings()` no `lifespan` (`L/backend/app/main.py`), antes de servir.
  Configuração inválida impede a partida, com a mensagem no log.
- [x] C004 Criar `L/backend/migrations/versions/0032_media_completed_seen.py`:
  - `op.add_column("encrypted_media", completed_seen_at DATETIME NULL)`;
  - `downgrade` remove a coluna;
  - acrescentar o campo em `L/backend/app/models/encrypted_media.py`.

## Phase 3: Cotas (US6)

- [x] C005 Criar `L/backend/app/services/media_quota.py`:
  - `usage(session, user_id)` com o uso do usuário e o global (`pending`, `active`, `deleting`), a contagem
    `active` e `disk_usage(vault).free`;
  - `level()`: `normal` (< 85 %), `high` (85–99 %) ou `full`;
  - `reserve(session, user_id, media_id, nbytes)` sob `threading.Lock`, somando as reservas em memória. A reserva
    é liberada pelos eventos `after_commit`, `after_rollback` e `after_soft_rollback` da sessão;
  - `QuotaExceeded(code, usage)`.

  **Desvio na implementação:** a soma do uso roda numa sessão curta e separada, não na sessão de quem grava. Na
  sessão de quem grava, essa leitura abria um retrato do banco, e o INSERT seguinte era recusado pelo SQLite
  ("database is locked") quando outra gravação terminava no meio. O teste de 20 gravações simultâneas pegou o
  problema. O que ainda não foi confirmado continua nas reservas em memória. O `507` leva o uso na visão de
  usuário comum (C-Q4).
- [x] C006 Em `media_service.store()`, chamar `reserve()` depois de cifrar e antes de gravar os arquivos.
- [x] C007 Converter `QuotaExceeded` em `507`, com `{detail, code, usage}`, nas rotas de capa (arquivo e link),
  avatar e foto do estudo. O `detail` vem em português e aponta "Minhas Imagens e Espaço".

## Phase 4: Foto de conferência no backend (US3)

- [x] C008 Criar `POST /api/studies/{id}/media` (multipart `file`):
  - só o dono, estudo fora da lixeira, senão `404`;
  - validação igual à da digitalização: JPEG, PNG ou WebP, até 20 MB e 40 MP, com `413`, `415` e `422`;
  - `prepare_page()` e `store(kind="notebook_page", study_id, book_id do capítulo, status="active")`;
  - `expires_at = agora + retenção`;
  - devolve o item e o `usage`;
  - erros `503 vault_locked` e `507`.
- [x] C009 Criar `GET /api/studies/{id}/media`: fotos `active` e `missing` do estudo, no formato de item da lista,
  só para o dono.

## Phase 5: API de mídia (US5)

- [x] C010 Criar `GET /api/media/usage` com o formato do plan-C §5. `server` só traz números para
  `role == "admin"`.
- [x] C011 Ampliar `GET /api/media`:
  - filtro `book_id`;
  - `sort` (`created_desc`, `size_desc`, `expires_asc`);
  - por item, `book {id, title}`, `study {id, title, reading_status, in_trash}` e `days_left`;
  - numa consulta só com `outerjoin`; paginação por `offset` mantida.
- [x] C012 Criar `PATCH /api/media/{id}` (`keep_forever`): só `notebook_page` do dono, senão `404`.
  - `true` limpa `expires_at` e `completed_seen_at`;
  - `false` faz `expires_at = agora + retenção`.
- [x] C013 Criar `POST /api/media/bulk-delete`:
  - filtros `completed_studies` (sem os 7 dias) e `older_than_days` (1–3650), mais `ids` (até 500, senão `422`);
  - `dry_run`;
  - só páginas do próprio usuário;
  - `keep_forever` fica fora dos filtros;
  - apaga por `media_service.delete()`;
  - resposta `{matched, freed_bytes, deleted}`.

## Phase 6: Job de retenção (US4)

- [x] C014 Criar `L/backend/app/services/media_retention.py` com `run(session, now) -> dict`, que aplica as regras
  1 a 7 do plan-C §6 em lotes de 200, com commit por lote.
  - `storage_unavailable` não faz nada.
  - `key_missing` ainda apaga.
- [x] C015 Criar `_media_retention_loop()` no `lifespan`:
  - `asyncio.to_thread`, na partida e a cada `get_media_job_interval_hours()`;
  - cancelado no desligamento;
  - fora do pytest;
  - registra uma linha só com contagens e bytes.

## Phase 7: Frontend, base

- [x] C016 Criar `L/frontend/src/types/media.ts` e os métodos em `L/frontend/src/services/api.ts`:
  `getMediaUsage`, `listMedia`, `setMediaKeep`, `deleteMedia`, `bulkDeleteMedia`, `listStudyMedia` e
  `storeStudyPhoto`.
- [x] C017 Criar `L/frontend/src/utils/mediaFormat.ts`: bytes (base 1024, rótulo "MB" e "GB"), validade e nível
  em texto.
- [x] C018 Criar `L/frontend/src/composables/useMediaSpace.ts`: uso, lista paginada, filtros, ordenação, seleção,
  prévia de lote, confirmação e recarga do uso depois de cada ação.
- [x] C019 Criar `L/frontend/src/composables/useOriginalPage.ts`: fotos do estudo, índice, zoom (0,5–4, passo
  0,25), ajuste à largura, manter e apagar.
- [x] C020 Em `L/frontend/src/composables/useDigitizeDraft.ts`:
  - guardar o `File` durante a revisão, soltando-o em `releasePhoto()` e `reset()`;
  - `keepPhoto` desmarcado por padrão;
  - `save()` envia a foto depois de criar o estudo;
  - falha vira `photoWarning`, com o estudo mantido;
  - nova dependência `storePhoto` no `DigitizeGateway`.

## Phase 8: Frontend, telas

- [x] C021 Criar `L/frontend/src/components/media/StorageMeter.vue`:
  - `role="meter"` com `aria-valuenow`, `aria-valuemax` e `aria-valuetext` iguais ao texto;
  - nível em texto e ícone;
  - cores só por tokens;
  - hachura no tema E-Ink.
- [x] C022 Criar `L/frontend/src/components/media/MediaCard.vue`:
  - miniatura `loading="lazy"` com `alt`;
  - livro, estudo (ou "Estudo na lixeira" ou "Estudo apagado"), data, validade e tamanho;
  - ações Ver, Manter (`aria-pressed`, só páginas), Abrir o estudo e Apagar;
  - menu por cartão com alvos de 44 px no celular;
  - cartão "Arquivo indisponível".
- [x] C023 Criar `L/frontend/src/views/MediaSpaceView.vue` e a rota `/minhas-imagens`, com links no
  `UserDropdown` e em `SettingsView`. A tela tem:
  - os medidores;
  - "Liberar espaço" com a prévia no rótulo;
  - filtros e ordenação;
  - seleção com barra fixa no celular;
  - `TrashConfirmModal` com "Os estudos e seus textos não serão alterados.";
  - `EmptyState`, `LoadingSkeleton` e o estado do cofre trancado.

  A rota `media-space` foi registrada nos contratos de responsividade das features 076 (classificação 1) e 081
  (linha 26, "Pendente" até a conferência C037), que os testes-guarda exigem para toda rota nomeada. A barra de
  seleção fixa no celular respeita `--mobile-nav-offset`, como a da lixeira.
- [x] C024 Criar `L/frontend/src/components/media/OriginalPageViewer.vue`:
  - zoom por botões e teclas (`+`, `−`, `0`);
  - arraste;
  - anterior e próxima;
  - rodapé com validade, Manter e Apagar foto, com confirmação.
- [x] C025 Em `L/frontend/src/views/StudyView.vue`:
  - botão "Folha original (N)" só com N > 0;
  - painel direito com divisória (`useSplitPanes`) no computador;
  - abas "Texto | Folha original" no celular;
  - fotos pedidas só ao abrir.

  **Desvio na implementação:** a divisória é própria da tela (arrastar ou setas do teclado; a largura fica no
  navegador), e não o `useSplitPanes`, que é o layout de três painéis do livro. Componentes `.vue` só podem usar
  variáveis CSS dos tokens globais, então a largura vai inline no `grid-template-columns`.
- [x] C026 Em `L/frontend/src/views/DigitizeNotebookView.vue`:
  - a caixa, com o texto de retenção e o uso;
  - desativada com o motivo quando o uso está `full` ou o cofre não está `ready`;
  - texto de transparência conforme a escolha;
  - mensagem final com a data ou o motivo da recusa e o link.

## Phase 9: Testes

- [x] C027 `L/backend/tests/test_media_quota.py`:
  - limite exato (cabe e não cabe por 1 byte);
  - cota global;
  - margem com `disk_usage` simulado;
  - 20 gravações concorrentes no limite (SC-006);
  - reserva liberada em rollback e em erro;
  - `507` com `code` e `usage` em capa, avatar e foto do estudo.
- [x] C028 `L/backend/tests/test_study_photo.py`:
  - foto otimizada (≤ 2000 px), sem EXIF/GPS (imagem com GPS falso), cifrada no disco;
  - só o dono lê;
  - `404` para estudo alheio ou na lixeira;
  - cota cheia dá `507` com o estudo intacto;
  - `GET /api/studies/{id}/media`.
- [x] C029 `L/backend/tests/test_media_api_c.py`:
  - `usage` por papel;
  - lista com livro, estudo, `days_left`, filtros e ordenação;
  - `PATCH keep_forever`;
  - `bulk-delete` (`dry_run`, filtros, `ids`, limite);
  - estudos idênticos campo a campo, com `version`, `updated_at` e `study_versions`, depois de cada apagamento
    (SC-005).
- [x] C030 `L/backend/tests/test_media_retention.py`, com relógio injetável:
  - regras 1 a 7;
  - concluído, desfeito e concluído de novo;
  - `keep_forever`, capa e avatar imunes;
  - órfã depois da purga;
  - `deleting` retomado;
  - `storage_unavailable` sem efeito;
  - log sem ids (SC-009).
- [x] C031 `L/backend/tests/test_media_settings.py` (padrões, `.env` e valor inválido) e
  `L/backend/tests/test_migration_0032.py` (upgrade e downgrade em banco descartável, com os dados da 0031
  preservados).
- [x] C032 `L/frontend/tests/feature-090c-*.test.mjs`:
  - `mediaFormat`;
  - `useMediaSpace`;
  - `useOriginalPage`;
  - `useDigitizeDraft`: desmarcada não envia, marcada envia depois do estudo, falha mantém o estudo;
  - medidor com texto e `aria-valuetext`;
  - links da rota.
- [x] C033 Medição SC-004 com um script na pasta temporária da sessão, fora dos testes:
  - 20 páginas fictícias de 12 MP;
  - mediana do tamanho depois de `prepare_page()` (meta ≤ 450 KB);
  - CER do motor da 086 na original e na otimizada (meta: ≤ 2 pontos de diferença);
  - espera RAM livre antes de rodar o motor;
  - registrar o resultado aqui.

  **Resultado** (20 páginas de 3000 × 4000 geradas com a fonte Ink Free, papel, ruído, inclinação de até 1,5° e
  JPEG q90):
  - tamanho: original com mediana de 1 156 KB; otimizada com mediana de 101 KB e máximo de 105 KB. **Passa.**
  - CER: original com mediana de 0,77 %; otimizada com 0,00 % em todas as páginas. A diferença ficou entre
    −1,77 e −0,17 ponto: a otimizada foi lida **melhor**. **Passa.**
  - **Limite da medição:** a fonte imita letra manual, mas é regular. Em caderno real, o tamanho pode subir (mais
    textura e traços) e a vantagem da versão reduzida pode não se repetir. Vale reconferir com fotos reais na
    C037.

## Phase 10: Validação e registro

- [x] C034 `pytest` (banco descartável), depois `npm test` e `npm run build`, em sequência, comparando com a linha
  de base.

  **Resultado:** `pytest` 635 aprovados e 1 pulado (linha de base 595 e 1; 40 novos); `npm test` 653 (linha de
  base 639; 14 novos); `npm run build` ok.
- [x] C035 Documentação:
  - `AMBIENTE-E-VALIDACAO.md` (cotas, retenção, variáveis);
  - `.env.example`;
  - `contracts/media-api.contract.md` como entregue;
  - `data-model.md` (`completed_seen_at` e regras do job);
  - `RETOMADA.md`.

  **Um** commit `feature — ciclo de vida e cotas das imagens`.

## Phase 11: Ambiente real (PORTÃO; cada passo só com a sua aprovação)

- [x] C036 Com o serviço parado, atualizar o banco no HD para a `0032` (snapshot automático verificado e segunda
  cópia) e conferir.

  **Resultado (28/10/2026):** antes, serviço parado, porta 8000 livre, `quick_check` ok. Snapshot
  `caderno-pre-migracao-20261028-164420.db` (versão `0031`) íntegro, segunda cópia com o mesmo SHA-256. Depois,
  banco em `0032_media_completed_seen`, `quick_check` e `foreign_key_check` ok, coluna `completed_seen_at` criada,
  a capa existente intacta. A retenção de 5 snapshots retirou do HD o `caderno-pre-migracao-20261011-141854.db`,
  que continua em `backend\dataackups`.
- [x] C037 **Você** religa o serviço e faz a conferência visual (SC-010):
  - "Minhas Imagens e Espaço", "Folha original" e a caixa na digitalização;
  - nos 10 temas, em 320 px e no teclado;
  - uma digitalização de teste com a caixa marcada.

  **Resultado (28/10/2026):** o usuário religou o serviço, digitalizou uma página real com a caixa marcada e
  conferiu as telas nos temas, em 320 px e no teclado: tudo ok. Conferência no HD, só com metadados: uma página
  `active` de 1526 × 2000 px, com 69 KB no cofre (imagem mais miniatura), cabeçalho `LMV1`, nenhuma assinatura de
  imagem em claro, ligada ao estudo e ao livro, e saída automática em 27/11/2026. A linha 26 do contrato da
  feature 081 passou de "Pendente" para "Pass".

---

## Dependencies

C001 → C002 → C003 → C004 → C005 → C006 → C007 → C008 → C009 → C010 … C013 → C014 → C015 → C016 → C017 → C018 /
C019 / C020 [P] → C021 … C026 → C027 … C033 → C034 → C035 → (portão) C036 → C037.

## Cobertura

| Requisito | Tarefas |
| :--- | :--- |
| FR-C01 | C008, C028 |
| FR-C02 | C020, C026, C032 |
| FR-C03 | C008, C020, C028, C032 |
| FR-C04 | C012, C013, C014, C029, C030 |
| FR-C05 | C014, C015, C030 |
| FR-C06 | C014, C030 |
| FR-C07 | C005, C006, C007, C027 |
| FR-C08 | C010, C029 |
| FR-C09 | C011, C029 |
| FR-C10 | C012, C013, C029 |
| FR-C11 | C009, C028 |
| FR-C12 | C021 … C026, C037 |
| FR-C13 | C002, C003, C031 |
| SC-004 | C033 |
| SC-005 | C029, C030 |
| SC-006 | C027 |
| SC-009 | C030 |
| SC-010 | C037 |
