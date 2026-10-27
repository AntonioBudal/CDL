# Tasks: Digitalizar Caderno — Foto de Página Manuscrita para Estudo

**Input**: Design documents from `specs/086-digitalizar-caderno-estudo/`
**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md),
[contracts/digitize-api.contract.md](contracts/digitize-api.contract.md),
[contracts/motor-cli.contract.md](contracts/motor-cli.contract.md), [quickstart.md](quickstart.md)

## Organization

As fases seguem o plano. A fase 2 é o **portão**: se a paridade do motor falhar, nada do backend nem do
frontend é tocado e a fatia para para decisão do usuário. As histórias US1 a US4 vêm depois, em ordem de
prioridade. Os caminhos são relativos à raiz do repositório (`C:\Users\User\caderno`); `L/` abrevia
`caderno-leitura-0.1/`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos distintos, sem dependência mútua)
- **[Story]**: história atendida (US1, US2, US3, US4)

**Regras em todas as tarefas**:
- nunca abrir, ler nem alterar `L/backend/data/caderno.db`;
- testes só com bancos em `tmp_path` e com textos e imagens fictícios;
- nenhum texto lido de imagem real aparece em log, relatório ou chat.

---

## Phase 1: Setup — linha de base

**Propósito**: confirmar que as suítes passam antes de qualquer mudança, para separar regressão de problema
preexistente.

- [X] T001 Rodar `pytest` em `L/backend` e `npm test` + `npm run build` em `L/frontend`; registrar contagens de
  testes aprovados como linha de base (sem alterar nada)

---

## Phase 2: Foundational — motor de leitura (PORTÃO)

**Propósito**: ter o motor do produto lendo igual ao `document-intelligence/`, isolado e verificável, antes de
integrar.

- [X] T002 Criar `L/motor/pyproject.toml` (pacote `leitorum-motor` 0.1.0, Python ≥ 3.13, sem dependência do
  backend) e `L/motor/requirements.txt` com `rapidocr==3.10.0`, `onnxruntime==1.31.0`,
  `opencv-python-headless==5.0.0.93`, `numpy==2.5.4` e as transitivas fixadas (R3)
- [X] T003 [P] Promover `document-intelligence/experiments/EXP-019/harness/merge.py` para
  `L/motor/leitorum_motor/merge.py` sem mudança de lógica (cabeçalho registra a origem e o commit)
- [X] T004 [P] Promover recorte desentortado e ordem de leitura de `EXP-019/harness/crop.py` para
  `L/motor/leitorum_motor/geometry.py` sem mudança de lógica
- [X] T005 Promover `EXP-019/harness/pipeline.py` para `L/motor/leitorum_motor/pipeline.py`:
  - classe `PagePipeline` sem supervisor;
  - lê `config.json`;
  - confere a existência e o SHA-256 dos modelos **antes** de criar o `RapidOCR` (R4, sem download);
  - recusa um leitor com `license_status` ≠ `VERIFIED`;
  - devolve as linhas em ordem de leitura com `text`, `confidence` e `bbox` (data-model §1).
- [X] T006 Criar `L/motor/config.json` (contrato motor-cli) e `L/motor/leitorum_motor/__main__.py`:
  - subcomandos `check` e `read --image --out [--config]`;
  - códigos de saída 0, 2 e 3;
  - `stderr` só com o tipo da exceção.
- [X] T007 Criar `L/motor/.venv` com `py -3.13 -m venv`, depois `pip install -r requirements.txt` e
  `pip install ./motor`, e rodar `python -I -m leitorum_motor check`.
  - Se o Python 3.13 falhar: recriar com `py -3.12` e registrar o motivo no `research.md` R3.
  - Confirmar que `L/.gitignore` cobre `motor/.venv/`.
- [X] T008 Paridade (quickstart §4): rodar o motor nas 15 imagens de `document-intelligence/dataset/raw/exp-022/fotos/`
  e comparar com `dataset/processed/exp-022/read-fotos-original.json`.
  - Comparar a contagem de linhas por página e a taxa de linhas com texto idêntico; aceite: contagem igual e
    ≥ 99 % de linhas idênticas.
  - Rodar com um script no scratchpad e relatar **só números**. Medir também a mediana de tempo por página,
    contando o carregamento.
  - Repetir a comparação depois da mesma normalização que o backend fará (Pillow: `exif_transpose`, RGB, PNG),
    para provar que a normalização não muda a leitura.
  - **PORTÃO**: se falhar, parar e reportar ao usuário.
- [X] T009 Calibrar o limiar de baixa confiança (quickstart §5 e research R10) com leituras por linha já
  existentes no `document-intelligence/`, usando o leitor original.
  - Fixar o valor em `L/motor/config.json`.
  - Registrar só os números: fração marcada e CER das marcadas contra as não marcadas.
- [X] T010 Criar `L/backend/tests/test_digitize_motor_smoke.py`: gera uma página sintética com texto fictício
  ("Livro de Teste", "Capítulo 1") e chama o motor real por linha de comando.
  - Valida o schema `leitorum-motor/1` e se há pelo menos 1 linha.
  - Fica **pulado** quando o `motor/.venv` não existe.

**Checkpoint**: o motor passa no `check`, na paridade e no teste de fumaça. Só então seguem as fases 3 em diante.

---

## Phase 3: Foundational — backend comum

**Propósito**: base do serviço que todas as histórias usam.

- [X] T011 Em `L/backend/app/core/config.py`, adicionar:
  - `get_motor_python()`, a partir de `LEITORUM_MOTOR_PYTHON` com o padrão `motor/.venv` do R9;
  - `get_digitize_min_free_bytes()`, a partir de `LEITORUM_DIGITIZE_MIN_FREE_MB` com padrão de 2048;
  - as constantes de limite: 20 MB, 40 MP e 120 s.
- [X] T012 [P] Criar `L/backend/app/schemas/digitize.py` com `DigitizeStatusRead`, `DigitizeLineRead`,
  `DigitizeWarningRead`, `DigitizeEngineRead` e `DigitizePreviewRead` (data-model §2–3).
- [X] T013 Criar `L/backend/app/services/digitize_service.py` com estas peças:
  - **Erros**: `DigitizeError(status, code, detail)`.
  - **`read_upload_limited`**: leitura do upload em blocos com o limite de 20 MB.
  - **`normalize_image`**: abre com o Pillow, aceita só `JPEG`, `PNG` e `WEBP`, limita a 40 MP, aplica
    `exif_transpose`, converte para RGB e grava como PNG.
  - **`free_memory_bytes`**: `GlobalMemoryStatusEx` via `ctypes` no Windows e `/proc/meminfo` no Linux; devolve
    `None` quando não há medida.
  - **`engine_status`**: roda o `check` e guarda o resultado em cache.
  - **`run_engine`**: usa `Popen` com `-I`, verifica a cada 250 ms o tempo limite e a desconexão, mata o
    processo quando preciso e grava a saída em arquivo.
  - **`to_preview`**: aplica o limiar, monta os avisos `draft`, `no_text` e `many_uncertain`, e omite caminhos e
    `bbox`.
  - **Fila**: `asyncio.Lock` global.
  - **Pasta temporária**: `tempfile.TemporaryDirectory(prefix="leitorum-digitize-")`, removida num `finally`
    com até 2 s de novas tentativas.
  - **Logs**: só código, duração e contagem de linhas, nunca o texto.
- [X] T014 Criar um motor falso para testes em `L/backend/tests/fake_motor.py`, um script que segue o contrato
  motor-cli. O modo é escolhido por variável de ambiente: `ok`, `empty`, `slow`, `crash`, `bad_schema` e
  `integrity`.
  - Ajuste: o script grava a pasta da imagem recebida num arquivo de rastro, para que os testes possam conferir
    a limpeza.

---

## Phase 4: User Story 1 — Fotografar e receber o texto para revisar (P1) [MVP]

**Objetivo**: enviar uma foto e ver o texto num editor com aviso de rascunho e as linhas incertas indicadas.
**Teste independente**: com o motor falso no modo `ok`, enviar uma imagem sintética e receber `200` com linhas,
confiança e aviso `draft`. Na tela, ver o texto, o aviso e a lista "Linhas para conferir".

- [X] T015 [US1] Criar `L/backend/app/routers/digitize.py` com `GET /digitize/status` e
  `POST /digitize/preview`.
  - As duas rotas usam `CurrentUser` e devolvem `Cache-Control: no-store`.
  - O `DigitizeError` vira `{detail, code}` com o status do contrato, e o `busy` leva `Retry-After: 15`.
  - Registrar o router em `L/backend/app/main.py`.
- [X] T016 [US1] Criar `L/backend/tests/test_digitize_api.py` usando o banco em `tmp_path` e o motor falso, com
  estes casos:
  - status disponível e indisponível;
  - `200` com `lines`, `low_confidence` e `draft`;
  - `no_text`;
  - `413` por tamanho e por megapixels;
  - `415`, cobrindo PDF e texto renomeado;
  - `422` para imagem truncada;
  - `500 engine_failed` para `crash` e `bad_schema`;
  - `503 unavailable` e `integrity`;
  - `401` sem sessão quando a autenticação é exigida;
  - foto com EXIF de rotação chegando ao motor já girada.
- [X] T017 [P] [US1] Reescrever `L/frontend/src/types/digitize.ts` com `DigitizeStatus`, `DigitizeLine`,
  `DigitizePreview`, `DigitizeSection`, `DIGITIZE_SECTIONS` (padrão `summary`) e os códigos de erro.
  - Manter `DIGITIZE_EXIT_SHORTCUTS`.
  - Remover `DOCUMENT_INTELLIGENCE_STAGES`.
- [X] T018 [US1] Em `L/frontend/src/services/api.ts`, adicionar `getDigitizeStatus(signal)` e
  `previewDigitize(file, signal)`, que envia `FormData` no campo `file`.
- [X] T019 [US1] Criar `L/frontend/src/composables/useDigitizeDraft.ts`:
  - o gateway é injetável;
  - estados e transições conforme o data-model §4;
  - `choose(file)` e `cancel()` (com `AbortController`);
  - mapeamento de erro para mensagem em português;
  - `uncertainLines`, cada item com o estado "já revisada" quando o texto original não está mais no editor.
- [X] T020 [US1] Reescrever `L/frontend/src/views/DigitizeNotebookView.vue` com os estados idle, reading e
  review:
  - botões "Tirar foto" (`capture="environment"`) e "Escolher imagem", ambos com
    `accept="image/jpeg,image/png,image/webp"`;
  - foto em `blob:` ao lado do editor;
  - aviso de rascunho fixo;
  - lista "Linhas para conferir", em que cada botão seleciona o trecho no textarea;
  - o resultado `no_text` mostra a orientação para tirar outra foto;
  - ao sair da tela durante a leitura, o pedido é abortado em `onBeforeUnmount` e a URL `blob:` é revogada
    (edge case "usuário sai da tela").

**Checkpoint US1**: a foto vira um texto revisável, e todos os erros do contrato aparecem como mensagens claras.

---

## Phase 5: User Story 2 — Salvar o texto revisado como Estudo (P1) [MVP]

**Objetivo**: transformar o texto revisado num Estudo "rascunho" pelo caminho de criação existente.
**Teste independente**: no banco `tmp_path`, criar "Livro de Teste" e "Capítulo 1", salvar o texto pela tela ou
pelo composable com o gateway falso e conferir o estudo com a seção escolhida, o `source_response` e o status
`rascunho`.

- [X] T021 [US2] Em `useDigitizeDraft.ts`, implementar:
  - `save()`, que monta o `StudyCreate` do data-model §5 (só a seção escolhida recebe o texto; `source_response`
    recebe a leitura bruta);
  - `canSave`, `dirty` e `reset()`, com a URL revogada em `reset()`;
  - título padrão "Página digitalizada em DD/MM/AAAA";
  - FR-009: `save()` não roda de novo enquanto está salvando nem depois de salvo, para que um clique duplo não
    crie dois estudos. Uma nova página exige `reset()`.
- [X] T022 [US2] Na view, adicionar:
  - o formulário de destino (livro e capítulo, no padrão do `ImportView.vue`, incluindo o aviso e o link quando o
    livro não tem capítulo);
  - os campos de título e de seção (`DIGITIZE_SECTIONS`);
  - o botão "Salvar como estudo";
  - o estado `saved`, com foco no título de sucesso, link para o estudo e o botão "Digitalizar outra página";
  - `useUnsavedChanges(dirty, busy)`.
- [X] T023 [P] [US2] Em `L/backend/tests/test_digitize_api.py`, adicionar um teste de ponta a ponta no banco
  `tmp_path`:
  1. preview com o motor falso;
  2. `POST /api/studies` com o payload da tela;
  3. confirmar que o estudo foi criado com `reading_status == 'rascunho'`, a seção escolhida preenchida e o
     `source_response` igual ao texto lido.

  O mesmo teste confirma que salvar com o texto vazio continua sendo recusado pela regra existente.

**Checkpoint US2**: há um fluxo completo do envio da foto ao Estudo salvo, em no máximo 4 ações depois da revisão
(SC-006).

---

## Phase 6: User Story 3 — Processamento local e transparente (P2)

**Objetivo**: provar que a foto não sai da máquina e não fica em disco.
**Teste independente**: nos testes, conferir que a pasta temporária some em todos os desfechos. Na validação
manual, conferir a leitura com a rede desligada.

- [X] T024 [US3] Em `test_digitize_api.py`, adicionar os testes de limpeza (SC-002). Pelo arquivo de rastro do
  motor falso, a pasta temporária não pode existir depois de nenhum destes desfechos:
  - sucesso;
  - `crash`;
  - `bad_schema`;
  - `422`;
  - tempo esgotado (`slow`, com limite reduzido por monkeypatch);
  - desconexão simulada (`is_disconnected` devolvendo `True`).

  Conferir também que o processo foi morto nos dois últimos casos.
- [X] T025 [P] [US3] Em `test_digitize_api.py`, testar a fila e a memória:
  - um segundo pedido com o lock ocupado recebe `503 busy` com `Retry-After`;
  - com `free_memory_bytes` simulada abaixo do mínimo, a resposta é `503 low_memory` e o motor não é chamado.
- [X] T026 [P] [US3] Em `test_digitize_api.py`, garantir que o `caplog` do pedido não contém o texto fictício
  lido nem o caminho da pasta temporária.
- [X] T027 [US3] Na view, adicionar o bloco de transparência:
  - processamento no computador onde o Leitorum está instalado, inclusive quando a foto vem do celular;
  - a foto é apagada após a leitura;
  - o texto é um rascunho do leitor de licença livre.

**Checkpoint US3**: os testes provam a limpeza em todos os desfechos, e a tela diz claramente onde o
processamento acontece.

---

## Phase 7: User Story 4 — Estados, temas e celular (P3)

**Objetivo**: a tela segue o padrão visual e ergonômico do Roadmap 0.9 em todos os estados.
**Teste independente**: percorrer os estados em 320 px e em desktop, nos temas claro, escuro e E-Ink, só com
teclado.

- [X] T028 [US4] Na view, implementar os estados restantes:
  - `unavailable`, com `EmptyState`, a ação "Importar texto" e os atalhos `/importar` e `/inbox`;
  - `reading`, com um esqueleto no formato do resultado (`LoadingSkeleton`), progresso e o botão "Cancelar";
  - `error`, com a mensagem e a ação "Tentar outra foto".
- [X] T029 [US4] Revisar o CSS da view:
  - só tokens semânticos, sem cor fixa;
  - ícones SVG;
  - alvos de toque ≥ 44 × 44 px e `:focus-visible`;
  - hierarquia `h1 → h2 → h3`;
  - layout em uma coluna abaixo de 768 px (foto acima do editor);
  - `prefers-reduced-motion`.
- [X] T030 [P] [US4] Em `L/frontend/src/views/ImportView.vue`, trocar no card o selo "Em Pesquisa" por
  "Rascunho a revisar" e ajustar o texto do convite (FR-012).
- [X] T031 [US4] Criar `L/frontend/tests/feature-086-digitalizar-caderno-estudo.test.mjs` e remover
  `feature-069-document-intelligence-placeholder.test.mjs` (R13). O teste novo cobre:
  - **rota**: `/digitalizar`, alias `/scan`, nome e título;
  - **arquivo**: `type="file"`, `capture="environment"`, `accept` restrito, e nenhum `getUserMedia`;
  - **tela**: aviso de rascunho, mensagem de processamento local, atalhos de saída, `useUnsavedChanges`, zero
    emojis e nenhuma cor hexadecimal no `<style>`;
  - **composable** (gateway falso): as transições de estado, o payload do `save()` com a seção escolhida e o
    `source_response`, o bloqueio do salvamento duplo, o mapeamento dos códigos de erro, o "já revisada" e o
    `cancel()`;
  - **card da importação**: atualizado.

**Checkpoint US4**: `npm test` cobre a tela, e a revisão de temas e celular está feita.

---

## Phase 8: Instalação, avisos, validação e registro

- [X] T032 Em `L/instalar.py`, adicionar a flag opcional `--motor`:
  - cria o `motor/.venv`;
  - instala `requirements.txt` e `./motor`;
  - roda o `check`;
  - uma falha só gera aviso e não interrompe a instalação.

  Sem a flag, o comportamento continua idêntico.
- [X] T033 [P] Em `L/AVISOS-DE-TERCEIROS.txt`, adicionar `rapidocr` (Apache-2.0), os modelos PP-OCRv6 small
  (Apache-2.0), ONNX Runtime (MIT), OpenCV (Apache-2.0) e NumPy (BSD-3-Clause), com as versões. Criar
  `L/motor/README.md` com a instalação, a troca de leitor, a regra de licença `VERIFIED` e a origem do código
  (EXP-019 e ADR-008).
- [X] T034 Rodar `pytest`, `npm test` e `npm run build`, e comparar com a linha de base do T001. Tudo precisa
  passar (SC-007).
- [~] T035 Fazer a validação manual do quickstart §3 com banco temporário e porta efêmera:
  - SC-001: tempo da foto ao texto;
  - SC-003: leitura com a rede desligada;
  - SC-002: limpeza dos temporários;
  - SC-004: Leitorum sem o motor;
  - SC-005: 320 px, temas claro, escuro e E-Ink, e teclado.

  Os itens que dependem de mão humana (desligar a rede, testar no celular) ficam listados para o usuário. Não
  são marcados como feitos sem execução.
- [X] T036 [P] No `document-intelligence/`, registrar:
  - a nota de promoção do pipeline ao Leitorum (feature 086) em `docs/adr/ADR-008-pipeline-de-referencia.md`;
  - a entrada no `docs/roadmap-experiments.md`, com a dispensa da validação da câmera crua decidida pelo usuário
    em 2026-10-27;
  - o estado atual no `CLAUDE.md`.

  Commit separado no padrão do `document-intelligence/`.
- [X] T037 Atualizar `L/docs/contexto/RETOMADA.md` com o estado da feature 086. Marcar as tarefas deste arquivo e
  criar **um** commit `feature — digitalizar caderno como estudo` com o Leitorum e `specs/086-*`, sem o
  `motor/.venv`, imagens ou bancos.

---

**Estado do T035 (2026-10-27):** feito pelo agente via API num servidor de validação (SC-001, SC-002, SC-004 por teste, FR-011). Pendentes de execução manual pelo usuário: SC-003 (rede desligada), SC-005 (320 px, temas, teclado) e celular. Ver quickstart §6.

## Dependencies & Execution Order

- **T001** → **Fase 2 (T002–T010, portão)** → **Fase 3 (T011–T014)** → US1 → US2 → US3 → US4 → Fase 8.
- Dentro da fase 2: T003 e T004 podem rodar em paralelo. T005 vem depois deles; T006 depois de T005; T007 depois
  de T002 e T006; T008, T009 e T010 depois de T007.
- US3 e US4 dependem das telas e do serviço de US1 e US2. As tarefas [P] de cada fase mexem em arquivos
  distintos.
- A US2 depende da US1, porque o salvamento parte do preview. As duas formam o MVP.

## Cobertura (requisito → tarefas)

| Requisito | Tarefas |
| :--- | :--- |
| FR-001 | T020 |
| FR-002 | T013, T016 |
| FR-003 | T013, T015, T016 |
| FR-004 | T005, T006, T035 |
| FR-005 | T013, T024 |
| FR-006 | T009, T019, T020 |
| FR-007 | T021, T022, T023 |
| FR-008 | T017, T021, T022 |
| FR-009 | T021 |
| FR-010 | T015, T016, T023 |
| FR-011 | T013, T025 |
| FR-012 | T015, T028, T030 |
| FR-013 | T005, T006, T033 |
| NR-001 | nenhuma migração em qualquer tarefa; T037 confere |
| NR-002 | T008, T009, T026 |
| NR-003 | T005, T033 |
| NR-004 | T007, T010, T032, T035 |
| NR-005 | T029, T031 |
| NR-006 | T014, T016, T034 |
| SC-001 | T008, T035 |
| SC-002 | T024, T035 |
| SC-003 | T035 |
| SC-004 | T016, T035 |
| SC-005 | T029, T035 |
| SC-006 | T022 |
| SC-007 | T034 |
