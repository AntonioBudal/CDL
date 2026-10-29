# Tasks — Fatia 091-C: Adaptador Online Dormente (E1 + E2 + gating)

**Input**:
- [spec.md](spec.md): US3; FR-004 e FR-011 a FR-015; SC-004 e SC-005; decisões Q3 e Q4;
- [plan-C.md](plan-C.md): §1 a §7; decisões C-Q1 a C-Q4, aprovadas em 2026-10-28 pela recomendação.

**Escopo da fatia C**:
- referência `adapter_v2.py` no EXP-025 (F05), com uma medição e o fixture de paridade;
- cópia literal no produto;
- serviço com o estado por usuário, a ativação com 30 revisados e a guarda dos últimos 20;
- `engine.adapter` na resposta, e `lines` no registro;
- script de reconstrução.

Caminhos relativos a `C:\Users\User\caderno`:
- `L/` = `caderno-leitura-0.1/`;
- `E24/` e `E25/` = `document-intelligence/experiments/EXP-024/` e `EXP-025/`.

**Regras em todas as tarefas**:
- **Dados e privacidade:**
  - dados fictícios;
  - nenhum texto no estado nem nos logs;
  - testes do produto em `tmp_path`, com as variáveis descartáveis do `pytest`.
- **Banco ativo:** nenhum acesso ao banco ativo nem ao `D:\` antes da Phase 8. Nenhuma migração.
- **`document-intelligence/`:**
  - nada no EXP-024 é alterado; a referência só importa as funções de lá;
  - o EXP-025 segue as regras de lá: `ruff`, commit `FNN(document-inteligence) [EXP-025] …`, RAM ≥ 1,5 GB livre
    antes de rodar a medição.
- **Build:** não rodar `npm run build` em paralelo com o `pytest`.

---

## Phase 1: Referência no `document-intelligence/` (EXP-025, F05) — C-Q1 e C-Q2

- [x] C001 Criar `E25/harness/adapter_v2.py` com a classe `AdapterV2`.
  - **âncora:** os pesos do `organizer-v2.json` mais 9 colunas extras com peso 0 (`ref_shape_user`, `usim_*` e
    `bsim_*`);
  - **`organize`:** usa o `decide` do v2 com as probabilidades adaptadas;
  - **`learn`:** recebe um documento `leitorum-feedback/1` e aplica E1, E2 e gating, com os limiares de
    `E24/artifacts/thresholds.json`;
  - **guarda:** a média móvel dos últimos 20 registros (C-Q3), do adaptador e do v2, medida antes de aprender;
  - **fora:** sem `T_user`, sem *replay*, sem portão-sombra;
  - importa `line_shape`, `normalized`, `top`, `page_weights`, `project` e as funções de `state` do EXP-024, sem
    alterá-las.
- [x] C002 Testes em `E25/tests/test_adapter_v2.py`:
  - com o estado vazio, o resultado é idêntico ao do v2 (nos 192 casos do `parity-v2`);
  - isolamento por usuário; determinismo;
  - página revertida e página de pouca retenção sem correções não aprendem;
  - a projeção respeita o raio 4,0;
  - o estado serializado não contém nenhum texto das páginas.
- [x] C003 Criar `E25/harness/evaluate_adapter.py` e rodar **uma vez** nos fluxos de **teste** do EXP-024.
  - regimes R1 e R3;
  - adaptador contra o v2 estático no *holdout* de cada perfil;
  - p95 da atualização e tamanho do estado em 500 estudos.

  Se o adaptador ficar abaixo do v2 no R3, **parar e avisar o usuário** antes da Phase 3.

  **Resultado (28/10/2026, uma rodada, 63 s), Macro-F1 médio:**

  | Regime | v2 | Adaptador sempre ligado | Regra do produto |
  | :--- | ---: | ---: | ---: |
  | R1 | 0,751 | 0,772 | 0,759 |
  | R3 | 0,751 | 0,772 | **0,733** |

  - **Por perfil:**
    - o P2 piora de 6 a 8 pontos;
    - no P1, as Referências vão de 0,54 a 0,87–0,92.
  - **A guarda:** escolheu errado no P1 e no P2, por causa do viés da sugestão exibida.
  - **Custos:** atualização com p95 de 30 ms; estado de 919 KB em 500 estudos.
  - **Decisão do usuário: opção A.** O adaptador entra com a ativação desligada (`LEITORUM_ORGANIZER_ADAPTER=off`,
    padrão), e o estado e a guarda continuam sendo gravados. Ligar depende de um experimento futuro com os
    registros reais.
- [x] C004 Criar `E25/harness/export_adapter_parity.py` e gerar `E25/artifacts/adapter-parity-v2.json`, com
  SHA-256: fluxo fictício de 40 páginas, 2 usuários e 2 livros. Em cada passo:
  - a sugestão esperada;
  - o código do `learn`;
  - a norma de ΔW;
  - as contagens e o SHA-256 do estado.
- [x] C005 Auditar o benchmark com um subagente, gravar em `evaluation/benchmarks/BENCHMARK-20261028-exp-025-adapter.json`
  e escrever a §6 do `E25/RESULTS.md`. Depois: `ruff`, os testes do EXP-023/024/025 e o commit
  `F05(document-inteligence) [EXP-025] adaptador de referencia (E1+E2+gating sobre o v2)`.

  **Resultado:**
  - commit `c8a5082`;
  - auditoria aprovada com 3 ressalvas, todas atendidas: os arquivos da F05 versionados junto com o benchmark, as
    metas da H5 registradas e páginas de **validação** nos testes e na paridade;
  - fixture `bef19d26…`, determinístico.

## Phase 2: Setup do produto

- [x] C006 Linha de base: `pytest` (esperado 674 aprovados e 1 pulado), `npm test` (662) e `npm run build`.
  **Usada a medida da B021**, na mesma árvore. Depois dela, só mudou a frase da página "Sobre".

## Phase 3: Cópias e paridade (plan-C §2) — US3

- [x] C007 Copiar para `L/backend/app/services/organizer/`:
  - `adapter_state.py`: cópia literal das funções usadas de `E24/harness/state.py` e `safety_gate.py`
    (`page_weights`, `project`, `frobenius`) e de `adaptive_organizer.py` (`line_shape`, `normalized`, `top`,
    `softmax`), com o cabeçalho de origem;
  - `adapter.py`: cópia literal de `E25/harness/adapter_v2.py`, com os imports apontando para `engine_v2`,
    `feedback_signal` e `adapter_state`.
- [x] C008 Copiar o fixture para `L/backend/tests/fixtures/adapter-parity-v2.json` e criar
  `L/backend/tests/test_adapter_parity.py`:
  - o fluxo reproduzido passo a passo (sugestões, códigos, normas e SHA-256 do estado);
  - com o estado vazio, o resultado é igual ao v2 nos 192 casos.

## Phase 4: Serviço, guarda e rotas (plan-C §3 e §4) — US3, FR-004, FR-011 a FR-015

- [x] C009 Criar `L/backend/app/services/organizer/adapter_service.py`.
  - **chave `LEITORUM_ORGANIZER_ADAPTER`** (`off` por padrão; `on` só para teste ou depois do experimento): com
    `off`, `suggest` devolve sempre o v2 e `adapter: null`, mas o estado e a guarda continuam sendo atualizados;
    um valor inválido impede a partida, como as chaves da 090-C;
  - `update_after_feedback(session, row)`, com lock por usuário e transação curta, devolvendo código e ms;
  - `reviewed_count(session, user_id)`;
  - `suggest(session, user_id, text, lines)`:
    - com menos de 30 revisados, ou com o artefato diferente, devolve o v2 puro;
    - senão, a guarda decide entre o adaptador e o v2;
  - `book_id` pelo capítulo do estudo;
  - teto de 1 MB para o estado: acima disso, poda os centróides e registra o código.
- [x] C010 Rota de organização (`L/backend/app/routers/imports.py` e `loader.organize`): passar o usuário, usar
  `suggest` e acrescentar `engine.adapter` à resposta, sem mudar o resto.
- [x] C011 Rota de feedback (`L/backend/app/routers/organizer_feedback.py`):
  - depois do `recorded`, chamar `update_after_feedback`;
  - log com o código e os ms;
  - uma falha não muda o `204` nem apaga o registro.
- [x] C012 Esquema do registro (`L/backend/app/schemas/organizer_feedback.py` e `feedback.py`): `organizer.lines`
  opcional, com até 400 linhas, guardado no documento (C-Q4).
- [x] C013 Criar `L/backend/tests/test_adapter_service.py`:
  - **chave desligada (padrão):** com 30 ou mais revisados e a guarda favorável, a sugestão continua o v2 e o
    estado continua sendo atualizado;
  - **ativação e guarda (chave `on`):**
    - com 29 revisados, a sugestão é o v2 (`adapter: null`); com 30, o adaptador, se a guarda deixar;
    - com o adaptador pior nos últimos 20, fica o v2;
  - **isolamento:** A não muda o estado de B (SC-004);
  - **artefato:** com outro SHA-256 no estado, a sugestão é o v2;
  - **registros especiais:**
    - revertido conta como página, sem rótulo;
    - registro sem `lines` de uma página com layout sai `misaligned`;
  - **falhas:** com falha forçada no `learn`, o registro fica e a resposta é `204`;
  - **SC-005:** p95 ≤ 150 ms em 200 registros fictícios; estado ≤ 1 MB;
  - **privacidade:** nem os logs nem o estado contêm texto fictício.
- [x] C014 Atualizar `L/backend/tests/test_organize_api.py`: `engine.adapter` é `null` sem registros, e o resto da
  resposta não muda.

## Phase 5: Frontend (plan-C §5)

- [x] C015 Tipos e organizador:
  - em `L/frontend/src/types/organize.ts`, `engine.adapter?` e `lines?` na sugestão; `toSuggestion` passa o
    `adapter`;
  - em `useSectionOrganizer.ts`, guardar as `lines` enviadas e incluí-las na sugestão.
- [x] C016 Testes em `L/frontend/tests/feature-091b-feedback-organizador.test.mjs` (ou num `091c` novo):
  - a digitalização organizada manda `lines` e o `adapter` da resposta;
  - a importação manda sem `lines`;
  - nada muda na tela.

## Phase 6: Reconstrução (plan-C §6) — FR-015

- [x] C017 Criar `L/backend/scripts/rebuild_organizer_state.py`:
  - argumentos `--user <id>` ou `--all`, com `--dry-run` (padrão) ou `--execute`;
  - snapshot pela barreira das migrações antes de gravar;
  - recusa rodar com o serviço de pé (porta 8000 ouvindo);
  - saída só com contagens.
- [x] C018 Criar `L/backend/tests/test_rebuild_organizer_state.py`:
  - a reconstrução dá o mesmo estado da atualização incremental;
  - o `--dry-run` não grava;
  - a recusa com a porta ocupada (simulada).

## Phase 7: Documentação e validação

- [x] C019 Documentação:
  - acréscimo no contrato `organizer-feedback.contract.md` (`lines`) e no contrato da 089 (`engine.adapter`);
  - `data-model.md` (formato do estado);
  - `AMBIENTE-E-VALIDACAO.md` §8 (adaptador, guarda e reconstrução);
  - `RETOMADA.md`.
- [x] C020 Validação completa, em sequência: `pytest`, `npm test` e `npm run build`. Comparar com a linha de base.
  **Resultado:** `pytest` 693 aprovados e 1 pulado (+19); `npm test` 663 (+1); build ok.
- [x] C021 Revisar o diff:
  - nenhum arquivo do EXP-024 alterado;
  - `engine.py`, `engine_v2.py` e `feedback_signal.py` intocados;
  - nenhum texto no estado nem nos logs;
  - nenhuma pós-correção de leitura.

  **Resultado:**
  - EXP-024 intocado; `engine.py` intocado;
  - `feedback_signal.py` idêntico à referência;
  - `engine_v2.py` e `adapter.py` diferem da referência só nas adaptações declaradas;
  - o `adapter_service` não registra log; a rota registra só códigos, contagens e ms.

  **Desvio:** a reconstrução grava e relê o estado a cada registro. Com isso, os números ficam com as mesmas 5
  casas da atualização incremental, e o estado reconstruído sai idêntico.
- [x] C022 Marcar a fatia C como implementada.

## Phase 8: Ambiente real e fechamento da feature (com o usuário)

- [x] C023 Você reinicia o serviço (sem migração). Eu confiro o reinício pelo log do NSSM.
- [x] C024 Você salva um estudo digitalizado e organizado. Eu confiro, numa cópia temporária pela API de backup e
  **só com contagens**:
  - o registro tem `lines`;
  - o estado do usuário existe, com o código `learned` ou `gated`, o tamanho em bytes e `reviewed_count`;
  - a organização continua com `adapter: null`, porque ainda não há 30 revisados.
- [x] C025 Fechar a feature 091:
  - marcar spec, planos e tarefas como concluídos;
  - **commit único da feature** em português (por exemplo, `feature — organizador v2 e registro do feedback`),
    depois das três suítes verdes. Só arquivos da 091: ficam de fora `query`, `stop` e os do EXP-025, que têm commit
    próprio.

  **Resultado C023–C024 (28/10/2026):**
  - o serviço foi reiniciado às 23:28:32, confirmado pelo log do NSSM;
  - `LEITORUM_ORGANIZER_ADAPTER` não está no `.env`, então o adaptador está desligado;
  - a pedido do usuário, sem estudo novo: a conferência usou o registro antigo da B027, numa cópia temporária
    pela API de backup, apagada no fim, **só com contagens**:
    - banco em `0033`, 1 registro (revisado) e nenhum estado gravado. É o esperado: o registro é anterior à fatia
      C, e o estado só nasce com o próximo;
    - o adaptador, rodado em memória sobre esse registro, devolve `misaligned`, porque o registro não tem as
      linhas com posição (C-Q4). Nada aprendido, a guarda não libera, e nada foi gravado no banco real.
  - O próximo estudo digitalizado e organizado já vai com as linhas e cria o estado.

---

## Dependências

- C001 → C002 → C003 (portão: avisar se ficar abaixo do v2 no R3) → C004 → C005.
- C006 → C007 → C008 → C009 → C010 a C012 → C013 → C014.
- C015 → C016 (pode correr junto com a Phase 4, depois da C012).
- C017 → C018.
- C019 → C020 → C021 → C022 → C023 → C024 → C025.
