# Plano Técnico da Fatia 090-C: Fotos de Conferência, Retenção, "Minhas Imagens e Espaço" e Cotas

**Feature**: `090-armazenamento-hd-cofre-cotas`, fatia C | **Date**: 2026-10-28 | **Spec**: [spec-C.md](spec-C.md)

**Base**:
- [plan.md](plan.md), com o desenho das telas, que continua valendo;
- decisões C-Q1 a C-Q4 aprovadas com as recomendações.

**Status**: Aprovado em 2026-10-28; tarefas em [tasks-C.md](tasks-C.md).

---

## Summary

A fatia completa o ciclo de vida das imagens no cofre da fatia B:

1. **Cotas:** reserva atômica (cota do usuário, cota global e espaço livre real) dentro de `media_service.store()`,
   e portanto para página, capa e avatar.
2. **Foto de conferência:** o leitor decide na revisão. O navegador reenvia a foto ao salvar, para
   `POST /api/studies/{id}/media` (C-Q1 A).
3. **Retenção:** o job `media_retention.run()` roda na partida e a cada 6 h, com relógio injetável. A data de
   conclusão fica em `encrypted_media.completed_seen_at` (C-Q2 A, migração `0032`).
4. **API:** `usage`, a lista enriquecida, `PATCH` de "manter", `bulk-delete` e as fotos do estudo.
5. **Frontend:**
   - "Minhas Imagens e Espaço" (`/minhas-imagens`);
   - "Folha original" no estudo;
   - caixa na digitalização;
   - aviso de cota nas telas de capa e avatar.

---

## Technical Context

Sem mudança de stack e sem pacote novo. Python 3.13, FastAPI, SQLAlchemy 2, Alembic, Pillow e `cryptography`;
Vue 3 e TypeScript.

- **Testes:** `pytest` em `tmp_path`, com o cofre isolado da fatia B (`isolated_media_vault`), relógio injetável,
  `shutil.disk_usage` simulado e gravações concorrentes com `ThreadPoolExecutor`. Também `npm test` e
  `npm run build`.
- **Escala:** ~3 000 páginas por usuário (1 GiB). A varredura do job é limitada ao cofre de uma instância, e o
  custo é um `stat` por mídia ativa.

---

## Constitution Check

- **I. Privacidade: PASS.**
  - Nenhuma foto fica guardada sem a escolha do leitor.
  - A capacidade do servidor só aparece em números para o administrador (C-Q4).
  - Logs só com contagens e bytes.
- **II. Isolamento de testes: PASS.** Tudo em `tmp_path`, com chave de teste. A medição SC-004 usa só páginas
  geradas.
- **III. Arquitetura: PASS.** Mesmo processo único, com tarefa `asyncio` no `lifespan`, como o backup automático.
- **IV. SDD: PASS.** Esta fatia tem spec, plano e tarefas próprios, e um commit `feature —`.
- **V. Migrações: PASS, com portão.** A `0032` só acrescenta uma coluna anulável (`ADD COLUMN`, sem recriar
  tabela) e passa pelo snapshot automático do `migrations/env.py`. No HD real, roda com o serviço parado e com
  a sua aprovação.

---

## Design

### 1. Configuração (FR-C13), em `app/core/config.py`

Novos `get_*` com padrão e validação: inteiro positivo, e retenção entre 1 e 3650 dias.

| Função | Variável | Padrão |
| :--- | :--- | :--- |
| `get_user_storage_quota_bytes()` | `LEITORUM_USER_STORAGE_QUOTA_BYTES` | 1 GiB |
| `get_global_storage_quota_bytes()` | `LEITORUM_GLOBAL_STORAGE_QUOTA_BYTES` | 900 GiB |
| `get_storage_free_margin_bytes()` | `LEITORUM_STORAGE_FREE_MARGIN_BYTES` | 2 GiB |
| `get_media_retention_days()` | `LEITORUM_MEDIA_RETENTION_DAYS` | 30 |
| `get_media_delete_on_completed()` | `LEITORUM_MEDIA_DELETE_ON_COMPLETED` | `true` |
| `get_media_completed_grace_days()` | `LEITORUM_MEDIA_COMPLETED_GRACE_DAYS` | 7 |
| `get_media_job_interval_hours()` | `LEITORUM_MEDIA_JOB_INTERVAL_HOURS` | 6 |

- `validate_media_settings()` é chamada no `lifespan`. Um valor inválido levanta erro com o nome da variável, e
  o servidor não sobe, como pede a spec.
- Diferente das demais variáveis, que caem no padrão em silêncio. A diferença é de propósito: errar a cota não
  pode passar despercebido.

### 2. Migração `0032_media_completed_seen`

- `encrypted_media.completed_seen_at DATETIME NULL` via `op.add_column`, sem recriar a tabela.
- O `downgrade` remove a coluna.
- O modelo `EncryptedMedia` ganha o campo.

### 3. Cotas (FR-C07), num módulo novo `app/services/media_quota.py`

- **`usage(session, user_id)`:** `SUM(byte_size)` e contagem do usuário e de todos, com `status IN ('pending',
  'active', 'deleting')`, mais `shutil.disk_usage(vault_dir).free`.
- **`reserve(session, user_id, nbytes)`:** dentro de um `threading.Lock` do processo:
  1. soma o uso confirmado no banco e as **reservas em andamento**, num dicionário em memória
     `{media_id: (user_id, bytes)}`;
  2. confere a cota do usuário, a cota global e `free - nbytes ≥ margem`;
  3. registra a reserva.
- **Por que reservas em memória:**
  - a linha `pending` que `store()` grava só fica visível às outras sessões depois do commit do chamador;
  - a reserva é liberada pelos eventos `after_commit` e `after_rollback` da sessão do chamador, registrados uma
    vez por sessão;
  - assim não há janela entre a gravação e o commit em que outra requisição veja um uso menor;
  - o servidor é de processo único, então o lock do processo basta.
- **`store()` chama `reserve()`** depois de cifrar, quando já sabe o `byte_size` exato, e antes de gravar os
  arquivos. Na recusa, levanta `QuotaExceeded(code, usage)`.
- **Resposta `507`:** um tratador único converte `QuotaExceeded` em `507`, com `code` `user_quota` ou
  `server_quota`, o `detail` em português ("Seu espaço está cheio: 1,0 GB de 1 GB. Libere espaço em Minhas
  Imagens e Espaço.") e `usage`.
- **Onde o tratador vale:** nas rotas de capa (arquivo e link), avatar e fotos do estudo. O frontend atual de capa
  e avatar já exibe o `detail`.

### 4. Foto de conferência (FR-C01 a FR-C03; C-Q1 A)

**`POST /api/studies/{id}/media`** (multipart `file`):
- só o dono, estudo fora da lixeira, senão `404`;
- valida como a digitalização: JPEG, PNG ou WebP, até 20 MB e 40 MP, com as mensagens de hoje;
- `prepare_page()`, depois `store(kind="notebook_page", study_id=…, book_id=livro do capítulo,
  status="active")`;
- `expires_at = agora + retenção`;
- devolve o item e o `usage`;
- erros: `507` de cota, `503 vault_locked` e `413`/`415`/`422` de validação.

**Mudanças de contrato:**
- `POST /api/media/{id}/attach` e o campo `keep_photo` do `preview` **saem do contrato**;
- o `preview` continua igual à 086: lê e apaga;
- fotos de página não passam mais por `pending` com 24 h.

**Frontend:**
- `useDigitizeDraft` guarda o `File` escolhido enquanto a revisão está aberta. Hoje ele já guarda a URL de
  pré-visualização; o `File` é solto em `releasePhoto()`.
- Novo `state.keepPhoto`, desmarcado por padrão.
- `save()` cria o estudo como hoje. Se `keepPhoto` estiver marcado, chama `gateway.storePhoto(study.id, file)`.
  - Uma falha vira `state.photoWarning`, com o motivo e o link, e o estudo continua salvo (FR-C03).
  - A mensagem final diz "Estudo salvo. Foto guardada até 27/11/2026" ou "Estudo salvo. A foto não foi
    guardada: …".

**`DigitizeNotebookView`:**
- caixa "Guardar a foto com o estudo para conferência (apagada automaticamente em 30 dias)", com o uso "312 MB de
  1 GB";
- a caixa fica desativada, com o motivo, quando `usage.user.level === 'full'` ou o cofre não está `ready`;
- o texto de transparência muda conforme a caixa.

### 5. API de mídia (FR-C08 a FR-C11), em `app/routers/media.py`

| Rota | Comportamento |
| :--- | :--- |
| `GET /api/media/usage` | `user {used_bytes, quota_bytes, count, percent, level}`, `server {level}` e `vault {state}`. Para o administrador, `server` também traz `used_bytes`, `quota_bytes` e `disk_free_bytes` (C-Q4). `level` vale `normal` (< 85 %), `high` (85–99 %) ou `full` (≥ 100 % ou sem espaço livre acima da margem) |
| `GET /api/media` | mantém a paginação por `offset` da fatia B (desvio declarado: o contrato previa `cursor`). Ganha `book_id`, `sort` (`created_desc`, `size_desc`, `expires_asc`) e, por item, `book {id, title}`, `study {id, title, reading_status, in_trash}` e `days_left`. Uma consulta com `outerjoin`, sem N+1 |
| `PATCH /api/media/{id}` | `{"keep_forever": bool}`, só `notebook_page` do dono. `true` limpa `expires_at` e `completed_seen_at`; `false` faz `expires_at = agora + retenção` |
| `POST /api/media/bulk-delete` | `{"filter": "completed_studies" \| "older_than_days", "days"?, "dry_run"}` ou `{"ids": [...], "dry_run"}` (até 500). Só páginas do próprio usuário. `keep_forever` fica fora dos filtros, mas não da lista explícita de `ids`. `completed_studies` apaga na hora, sem os 7 dias (C-Q3). Resposta: `{matched, freed_bytes, deleted}` |
| `GET /api/studies/{id}/media` | fotos `active` e `missing` do estudo, no formato de item, só para o dono (`404` para os demais) |

**Apagamento** (individual, em lote ou pelo job): usa só `media_service.delete()`. Nenhum desses caminhos tem
`session` sobre `Study`, que é a garantia de FR-C04. O teste compara as colunas do estudo, as `study_versions` e
o `updated_at`.

### 6. Job de retenção (FR-C05 e FR-C06), em `app/services/media_retention.py`

`run(session, now) -> dict` devolve as contagens por regra e os bytes liberados. Trabalha em lotes de 200, com
commit por lote. As regras são aplicadas nesta ordem:

| # | Regra | Condição |
| :--- | :--- | :--- |
| 1 | Marca de conclusão | Página `active`, sem `keep_forever`, com estudo `concluido` e `completed_seen_at` nulo: grava `now`. Estudo que não está mais `concluido`: limpa a marca. Desligada se `LEITORUM_MEDIA_DELETE_ON_COMPLETED=false` |
| 2 | Concluído vencido | `completed_seen_at ≤ now − 7 dias` e sem `keep_forever`: apaga |
| 3 | Idade | `kind = notebook_page`, `active`, sem `keep_forever`, `expires_at ≤ now`: apaga |
| 4 | Órfã | Página com `study_id` nulo (estudo purgado) e sem `keep_forever`: `expires_at = min(expires_at, now + 7 dias)`. A regra 3 apaga depois |
| 5 | `pending` abandonada | `pending` com `created_at ≤ now − 24 h`, de qualquer tipo (sobra de gravação interrompida): apaga |
| 6 | `deleting` pendente | tenta de novo remover os arquivos e a linha |
| 7 | Reconciliação | `.tmp` no cofre com mais de 1 h: remove. Linha `active` sem arquivo: `missing`. Arquivo `.enc` com nome de UUID, sem linha e com mais de 24 h: remove |

- **Regra 4:** reaproveita `expires_at`, então a foto órfã aparece na tela como "expira em N dias".
- **Regra 7:** a margem de 24 h protege uma gravação em andamento e um backup restaurado há pouco.
- **Execução:**
  - `_media_retention_loop()` no `lifespan`, como `_auto_backup_loop`: `asyncio.to_thread(run_once)` na partida e
    a cada `get_media_job_interval_hours()`;
  - é cancelado no desligamento;
  - não roda sob pytest; os testes chamam `run()` direto.
- **Cofre indisponível:** com `storage_unavailable`, o job não faz nada. Com `key_missing`, ainda pode apagar, já
  que apagar não precisa da chave.
- **Log:** uma linha com as contagens, por exemplo "Retenção do cofre: 3 apagadas (1,2 MB), 1 marcada como
  ausente". Nunca nomes, títulos ou ids.

### 7. Frontend

| Arquivo | Conteúdo |
| :--- | :--- |
| `src/types/media.ts` | `MediaItem`, `MediaUsage`, `BulkDeleteRequest` e `BulkDeleteResult` |
| `src/services/api.ts` | `getMediaUsage`, `listMedia`, `setMediaKeep`, `deleteMedia`, `bulkDeleteMedia`, `listStudyMedia` e `storeStudyPhoto` |
| `src/utils/mediaFormat.ts` | bytes em "312 MB" e "1 GB" (base 1024, rótulo GB, como o Windows), validade ("expira em N dias", "Mantida permanentemente", "Não expira") e nível em texto |
| `src/composables/useMediaSpace.ts` | uso, lista paginada, filtros, seleção, prévia (`dry_run`) e confirmação de lote; recarrega o uso depois de cada ação |
| `src/composables/useOriginalPage.ts` | fotos do estudo, índice atual, zoom (de 0,5 a 4, passos de 0,25), ajuste à largura, manter e apagar |
| `src/components/media/StorageMeter.vue` | `role="meter"` com `aria-valuetext` igual ao texto; ícone e texto do nível; hachura no tema E-Ink |
| `src/components/media/MediaCard.vue` | miniatura `loading="lazy"` com `alt`; metadados; ações (menu com alvos de 44 px no celular); cartão "Arquivo indisponível" |
| `src/components/media/OriginalPageViewer.vue` | imagem, zoom por botões e teclado (`+`, `−`, `0`), arraste, anterior e próxima, e rodapé com validade, manter e apagar |
| `src/views/MediaSpaceView.vue` | rota `/minhas-imagens`, com links no `UserDropdown` e em `SettingsView` |
| `src/views/StudyView.vue` | botão "Folha original (N)" na barra (só com N > 0). No computador, painel à direita com divisória (`useSplitPanes`, painel direito); no celular, abas "Texto \| Folha original" |
| `src/views/DigitizeNotebookView.vue` e `useDigitizeDraft.ts` | caixa, aviso de cota e mensagem final (§4) |

- **Imagens:** carregadas por URL direta (`/api/media/{id}/content` e `/thumbnail`), com o cookie de sessão. As
  respostas já são `no-store`.
- **Desvio declarado:** o `plan.md` previa `blob:` revogado ao fechar. A URL direta dá o mesmo efeito sem guardar
  cópia em memória e deixa o `loading="lazy"` funcionar na grade.
- **Confirmações:** reaproveitam o `TrashConfirmModal`, que já tem foco preso. O texto fixo é "Os estudos e seus
  textos não serão alterados."
- **Estados:** `EmptyState` (ação "Digitalizar uma página"), `LoadingSkeleton` em cartões, e cofre trancado com o
  caminho `instalar.py --media-key --restore`.

### 8. Medição (SC-004)

Um script de medição, que não é teste automatizado, roda fora do pytest, com o servidor parado ou ligado, sem
tocar no acervo:
- gera 20 páginas fictícias de 12 MP: texto manuscrito simulado em fonte cursiva, fundo de papel, ruído e leve
  inclinação;
- mede o tamanho depois de `prepare_page()`;
- roda o motor da 086 na original e na otimizada, e calcula o CER contra o texto gerado.

O resultado vai para o `tasks-C.md`. Se a RAM livre não bastar para o motor, a medição espera, como na regra das
rodadas longas.

### 9. Documentação

- `AMBIENTE-E-VALIDACAO.md`: cotas, retenção e variáveis.
- `.env.example`: as 7 variáveis.
- `contracts/media-api.contract.md`: as rotas como entregues (sem `attach` nem `keep_photo`, com `offset`, `usage`
  por papel, `POST /api/studies/{id}/media`).
- `data-model.md`: `completed_seen_at` e as regras do job.
- `RETOMADA.md`.

---

## Testes

| Arquivo | Cobertura |
| :--- | :--- |
| `test_media_quota.py` | limite exato (cabe e não cabe por 1 byte); cota global; margem de espaço livre com `disk_usage` simulado; 20 gravações concorrentes no limite (só as que cabem passam, SC-006); reserva liberada no rollback; `507` com `code` e `usage` nas rotas de capa, avatar e foto do estudo |
| `test_study_photo.py` | foto guardada otimizada (≤ 2000 px, sem EXIF/GPS) e cifrada; acesso só do dono; estudo de outro usuário ou na lixeira dá `404`; cota cheia dá `507` com o estudo intacto; `GET /api/studies/{id}/media` |
| `test_media_api_c.py` | `usage` por papel (o usuário comum não vê números do servidor); lista com livro, estudo, `days_left`, filtros e ordenação; `PATCH keep_forever`; `bulk-delete` com `dry_run`, filtros, `ids` e limite de 500; estudos idênticos campo a campo depois de cada apagamento (SC-005) |
| `test_media_retention.py` | relógio injetável; as regras 1 a 7, incluindo concluído, desfeito e concluído de novo; `keep_forever` imune; capa e avatar imunes; órfã depois da purga da lixeira; falha de remoção retomada; `storage_unavailable` sem efeito; log sem ids (SC-009) |
| `test_media_settings.py` | padrões; valores do `.env`; valor inválido impede a partida |
| `test_migration_0032.py` | upgrade e downgrade em banco descartável, com dados da 0031 preservados |
| `frontend/tests/feature-090c-*.test.mjs` | `mediaFormat`; `useMediaSpace` (prévia, seleção, recarga do uso); `useOriginalPage` (zoom e navegação); `useDigitizeDraft` (caixa desmarcada não envia, marcada envia depois do estudo, falha da foto mantém o estudo); medidor acessível (texto e `aria-valuetext`) |

**Linha de base:** `pytest` 595 aprovados e 1 pulado; `npm test` 639.

---

## Fases (detalhadas no `tasks-C.md`)

1. Configuração, migração `0032` e modelo.
2. Cotas e `507`.
3. Foto do estudo (backend).
4. API de mídia (`usage`, lista, `PATCH`, lote, fotos do estudo).
5. Job de retenção.
6. Frontend: tipos, API, utilitários e composables.
7. Frontend: as três telas.
8. Medição SC-004, suítes e documentação; commit `feature — ciclo de vida e cotas das imagens`.
9. **Portão no ambiente real** (cada passo com a sua aprovação):
   - com o serviço parado, migrar o HD para a `0032`, com snapshot verificado;
   - religar o serviço;
   - a conferência visual nos temas, em 320 px e no teclado (SC-010) fica com você.

---

## Riscos

| Risco | Mitigação |
| :--- | :--- |
| A foto sobe duas vezes no celular (até 20 MB) | O texto da caixa avisa. A `prepare_page` reduz a ~400 KB no servidor. Reduzir no navegador antes do envio fica para depois, se incomodar |
| O job apaga algo indevido | Regras com relógio injetável e teste por regra. O job só apaga páginas (capa e avatar só nas regras 5 e 7, que tratam sobras sem referência). O `.enc` órfão só sai com mais de 24 h |
| Reserva em memória vazar (sessão sem commit nem rollback) | A sessão do FastAPI sempre fecha. Ao fechar, `after_soft_rollback` também libera. Teste de reserva liberada em erro |
| A migração `0032` no HD real | Só adiciona coluna anulável; snapshot automático e segunda cópia; serviço parado; aprovação |
