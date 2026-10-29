# Plano Técnico da Fatia 091-C: Adaptador Online Dormente (E1 + E2 + gating)

**Feature**: `091-organizer-v2-feedback`, fatia C | **Date**: 2026-10-28 | **Spec**: [spec.md](spec.md)

**Base**:
- [spec.md](spec.md): US3; FR-004 (`engine.adapter`) e FR-011 a FR-015; SC-004 e SC-005; decisões Q3 (N = 30) e
  Q4 (só organizações salvas contam);
- referência: `document-intelligence/experiments/EXP-024/harness/adaptive_organizer.py`, `state.py` e
  `safety_gate.py`, com os limiares congelados de `artifacts/thresholds.json`.

**Status**: Concluído em 2026-10-28 ([tasks-C.md](tasks-C.md), C001 a C025), com a ativação desligada (opção A).

> **Decisão do usuário depois da medição (C003, 2026-10-28): opção A — ativação desligada por configuração.**
>
> Medição no teste do EXP-024 (Macro-F1 médio dos 4 perfis):
>
> | Regime | v2 | Adaptador sempre ligado | Regra do produto (30 revisados e guarda) |
> | :--- | ---: | ---: | ---: |
> | R1 | 0,751 | 0,772 | 0,759 |
> | R3 | 0,751 | 0,772 | **0,733** |
>
> - **Achados:**
>   - o adaptador ganha na média;
>   - o P2 perde de 6 a 8 pontos em todos os modos;
>   - a guarda erra a escolha, porque o que fica salvo herda o viés da sugestão que o leitor viu.
> - **O que muda:**
>   - `LEITORUM_ORGANIZER_ADAPTER` (padrão `off`) desliga o uso do adaptador na sugestão;
>   - o estado e as medidas da guarda continuam sendo gravados a cada registro;
>   - ligar exige um experimento com os registros reais (N ≥ 30, só números), que valide o adaptador e uma guarda
>     sem esse viés.
> - **Na prática:** com a chave desligada, a sugestão é sempre o v2, com `engine.adapter: null`. Com a chave
>   ligada, vale a regra dos 30 revisados e da guarda.

---

## Summary

1. **Um adaptador por usuário, com estado incremental** (`organizer_user_state`), só com três peças do EXP-024:
   - **E1:** pesos online sobre o diff de revisão, somados aos do v2, com âncora L2 e projeção (raio 4,0);
   - **E2:** centróides do leitor e do livro (8 colunas novas: `usim_*` e `bsim_*`) e a forma de linha de
     referência aprendida (`ref_shape_user`);
   - **gating:** página revertida ou com pouca retenção e sem correções não gera atualização.

   Ficam de fora $T_{\text{user}}$, *replay*, portão-sombra com canário e pós-correção da leitura (FR-012).
2. **O estado é atualizado a cada registro novo da fatia B**, desde o primeiro, em tempo limitado (FR-014).
3. **A sugestão só usa o adaptador com 30 ou mais registros revisados** (Q3 e Q4). Abaixo disso, a sugestão é o v2
   puro, idêntico ao de hoje (FR-013).
4. **Uma guarda automática (C-Q3):** mesmo com 30 registros, o adaptador só entra se, nos últimos 20 registros do
   próprio usuário, tiver acertado pelo menos tanto quanto o v2.
5. **Reconstrução:** um comando de manutenção remonta o estado a partir dos registros, se ele se corromper ou se o
   artefato mudar (FR-015).

## Por que uma referência no `document-intelligence/` antes (C-Q1)

- **Âncora:** o motor do EXP-024 foi escrito sobre o **v1**. Nele, as 4 pistas eram colunas extras com peso zero,
  e no v2 elas já fazem parte do artefato. Copiar o motor como está daria colunas duplicadas e uma âncora errada.
- **Configuração não medida:** a combinação pedida (E1 + E2 + gating, sem *replay*, sem portão-sombra e sem
  $T_{\text{user}}$, sobre o v2) não foi medida assim no EXP-024. A ablação mais próxima, E1 + E2 + gating sobre o
  v1 no regime limpo, deu 0,763 contra 0,777 sem gating. O regime ruidoso (R3) não foi medido nessa combinação.
- **O caminho seguido nas fatias A e B:**
  1. uma **referência em Python puro** no `document-intelligence/`, `EXP-025/harness/adapter_v2.py` (fase F05 do
     EXP-025, por delegação). Ela reaproveita as funções do EXP-024 sem alterá-las e é ancorada no v2;
  2. **uma medição** (C-Q2) nos fluxos de teste do EXP-024, em R1 e R3, contra o v2 estático. É informativa: não
     bloqueia a fatia, porque o adaptador fica dormente e a guarda de C-Q3 o protege;
  3. um **fixture de paridade** (`adapter-parity-v2.json`): um fluxo fictício de páginas, com a sugestão esperada e
     o resumo do estado depois de cada atualização;
  4. o **produto copia a referência literalmente** e confere a paridade, como fez com o `engine_v2.py` e o
     `feedback_signal.py`.

## Technical Context

- **Backend:** Python 3.13, só biblioteca padrão; nenhuma dependência nova.
- **Banco:** as tabelas `organizer_feedback` e `organizer_user_state`, criadas na fatia B. **Nenhuma migração
  nova.**
- **Frontend:**
  - o `engine.adapter` da resposta passa a ir para o registro;
  - a digitalização passa a enviar as linhas com posição (C-Q4);
  - nenhuma mudança visível.
- **Estado:**
  - JSON (`leitorum-learning-state/1`) com Δ dos pesos (4 × 54), centróides por hash de n-gramas (até 2 000 por
    seção no leitor e 300 por livro), tabelas de forma de linha e contadores;
  - **nenhum texto:** só hashes, números e formas abstratas como `- Ttt — Ttt`;
  - **tamanho:** o EXP-024 mediu 749 KB em 500 estudos, com *replay*. Sem *replay*, menos. O plano é medir com dados
    fictícios e fixar um teto de 1 MB por usuário.

## Constitution Check

| Regra | Como a fatia cumpre |
| :--- | :--- |
| Privacidade (AGENTS §1) | o estado não guarda texto; testes só com dados fictícios; logs só com contagens e tempos |
| Banco ativo (AGENTS §2) | sem migração; a reconstrução é um comando manual, rodado só com o serviço parado e com a sua aprovação |
| Spec Kit fatiado (§4) | plano → tarefas → implementação, com aprovação; a referência no `document-intelligence/` segue as regras de lá |
| Commit (§6) | o produto ganha um commit único da 091; o `document-intelligence/` ganha o commit da fase F05 do EXP-025 |
| Pós-correção desligada (FR-016) | o adaptador não toca na leitura |

## Design

### 1. Referência no `document-intelligence/` (EXP-025, fase F05)

**`harness/adapter_v2.py`:** classe `AdapterV2`.
- **Âncora:** os pesos do `organizer-v2.json` (45 colunas), mais 9 colunas extras com peso 0: `ref_shape_user`,
  `usim_*` e `bsim_*`.
- **`organize(state, text, lines, book_id)`:**
  - vetor do v2, mais as 9 extras;
  - probabilidades com $W_0 + \Delta W$;
  - a decisão é **o mesmo `decide` do v2** (Viterbi com custo de troca, margem de "conferir" 0,20), com as
    probabilidades novas;
  - com o estado vazio, o resultado é idêntico ao v2. A paridade testa isso.
- **`learn(state, document, book_id)`:** recebe o registro `leitorum-feedback/1`.
  - alinhamento com `align_units`;
  - gating com `page_weights`;
  - rótulos e pesos por desfecho (mantido 0,5 × fator de "não conferido" 0,05; movido 1,0; editado 0,5);
  - centróides e formas de linha;
  - passo de gradiente com âncora L2 ($\mu$ = 0,02) e taxa $\eta_0$ = 0,1 decrescente, seguido da projeção.

  Parâmetros e limiares vêm de `EXP-024/artifacts/thresholds.json`, sem mudança.
- **Sem `T_user`:** a transição fica plana, como no v2.

**`harness/evaluate_adapter.py`** (C-Q2): roda uma vez nos fluxos de **teste** do EXP-024.
- regimes R1 (implícito) e R3 (20 % de ruído);
- adaptador contra o v2 estático no *holdout* de cada perfil;
- latência p95 da atualização e tamanho do estado em 500 estudos.

**`harness/export_adapter_parity.py`:** gera o fixture `artifacts/adapter-parity-v2.json` (fluxo fictício de 40
páginas, 2 usuários e 2 livros). Cada passo traz:
- a sugestão esperada;
- o resumo do estado: norma de ΔW, contagens e o SHA-256 do estado serializado.

**Testes:** estado vazio igual ao v2; isolamento por usuário; determinismo; gating; projeção.

**Relatório:** uma seção nova no `RESULTS.md` do EXP-025, com benchmark auditado.

### 2. Produto: `app/services/organizer/adapter.py`

- **Origem:** cópia literal de `adapter_v2.py`, com o cabeçalho de sempre. Os imports apontam para `engine_v2` e
  `feedback_signal`.
- **Funções auxiliares** (`line_shape`, `normalized`, `top`, `page_weights`, `project`, as funções de estado):
  copiadas do EXP-024 para `app/services/organizer/adapter_state.py`, também literais.

### 3. Produto: `app/services/organizer/adapter_service.py` (banco)

- **`update_after_feedback(session, row)`:**
  - chamada pela rota da fatia B logo depois de gravar o registro, na mesma requisição, que o navegador não espera;
  - carrega o estado do usuário ou cria um novo; aplica `learn`; grava;
  - fica sob um lock por usuário (processo único);
  - uma falha só vira código no log, e o registro continua gravado.
- **`reviewed_count(session, user_id)`:** conta `organizer_feedback.reviewed = 1`.
- **`suggest(session, user_id, text, lines)`:**
  1. com menos de 30 revisados, ou com o estado num SHA-256 de artefato diferente do atual, devolve o v2 puro e
     `adapter: null`;
  2. senão, aplica a guarda (C-Q3): o adaptador só entra se a média móvel de acerto dele nos últimos 20 registros
     for pelo menos a do v2;
  3. se entrar, devolve a sugestão do adaptador e `adapter: <número de revisados>`.
- **A guarda na prática:** a cada registro novo, **antes** de aprender com ele, o serviço calcula quantos trechos
  o adaptador e o v2 teriam acertado contra as seções salvas, usando `align_units`. Guarda as duas médias móveis
  no próprio estado. Custo: duas organizações por registro, cerca de 20 ms.
- **`book_id`:** vem do capítulo do estudo.

### 4. Rotas e contratos

- **`POST /api/imports/organize`:** passa a chamar `suggest` com o usuário atual. A resposta ganha
  `engine.adapter` (`null` ou a contagem), como pede a FR-004. A forma do resto não muda.
- **`POST /api/studies/{id}/organizer-feedback`:** depois do `recorded`, chama `update_after_feedback`. O log ganha
  o código da atualização (`learned`, `gated`, `misaligned`, `skipped_artifact`, `error`) e o tempo em ms.
- **Contrato da fatia B, só acréscimo** (C-Q4): `organizer.lines`, opcional, com as linhas e caixas que foram
  enviadas ao organizador. Sem elas, a nova análise de uma página digitalizada (feita com layout) pode segmentar
  diferente, e a página sai como `misaligned`, sem aprender.

### 5. Frontend

- **Tipos:** `OrganizeResult.engine` ganha `adapter?: number | null`, e `toSuggestion` passa esse valor adiante.
- **`useSectionOrganizer`:** guarda as `lines` enviadas e as inclui na sugestão.
- **Sem mudança visível.** O adaptador é silencioso, como o registro.

### 6. Manutenção: `backend/scripts/rebuild_organizer_state.py`

- **Uso:** `--user <id>` ou `--all`. Opções `--dry-run`, só com contagens, e `--execute`.
- **O que faz:** apaga o estado e o remonta aplicando os registros em ordem de criação. Isso é a reconstrução
  manual da FR-015, não *replay* online.
- **Quando:** só com o serviço parado. Antes de gravar, um snapshot pela mesma barreira das migrações.
- **Saída:** só contagens: registros, aprendidos, barrados, tempo e tamanho final.

### 7. Testes

**Produto** (banco descartável, dados fictícios):
- **`test_adapter_parity.py`:** o fluxo do `adapter-parity-v2.json` reproduzido passo a passo; com o estado vazio,
  o resultado é igual ao v2 nos 192 casos do `parity-v2`.
- **`test_adapter_service.py`:**
  - com 29 revisados, a sugestão é a do v2 (`adapter: null`); com 30, é a do adaptador, se a guarda deixar;
  - guarda: com o adaptador pior que o v2 nos últimos 20, fica o v2;
  - **isolamento:** salvar como A não muda o estado de B (SC-004);
  - **artefato trocado:** o estado com outro SHA-256 é ignorado até a reconstrução;
  - **organização revertida:** conta como página, não gera rótulo;
  - **falha forçada no `learn`:** o registro fica gravado e a resposta continua `204`;
  - **SC-005:** p95 da atualização ≤ 150 ms em 200 registros fictícios; estado ≤ 1 MB;
  - **logs e estado:** nenhum texto fictício aparece.
- **`test_rebuild_organizer_state.py`:** a reconstrução dá o mesmo estado que a atualização incremental;
  `--dry-run` não grava nada.

**Frontend:** `engine.adapter` e `lines` vão no registro; nada muda na tela.

### 8. Decisões para você (com recomendação)

- **C-Q1 — Referência no `document-intelligence/` antes do produto?** Recomendo **sim**. É o padrão das fatias A
  e B e garante paridade numa configuração que o produto vai rodar sozinho.
- **C-Q2 — Medir essa configuração nos fluxos de teste do EXP-024 (R1 e R3) antes de levar ao produto?** Recomendo
  **sim**, como dado informativo (cerca de 10 a 20 minutos de máquina, com o teto de RAM de sempre). Se o
  adaptador ficar abaixo do v2 no R3, eu aviso antes de seguir.
- **C-Q3 — Guarda automática pelos últimos 20 registros do próprio usuário?** Recomendo **sim**. Não é *replay*
  nem portão-sombra: compara o adaptador e o v2 em cada registro novo, antes de aprender, e o adaptador só entra se
  não estiver perdendo. É a proteção que substitui as travas que ficaram de fora.
- **C-Q4 — A digitalização passa a enviar as linhas com posição no registro?** Recomendo **sim**. Sem elas, boa
  parte das páginas digitalizadas sairia `misaligned` e não ensinaria nada. Custo: cerca de 3 KB a mais por
  registro.

## Fases (detalhadas no `tasks-C.md`)

1. Referência, medição e fixture no `document-intelligence/` (EXP-025 F05), com commit lá.
2. Linha de base dos testes do produto.
3. `adapter.py` e `adapter_state.py` (cópias), com a paridade.
4. `adapter_service.py`, as rotas e a guarda.
5. Frontend (`adapter` e `lines`).
6. Script de reconstrução.
7. Documentação e validação completa.
8. Ambiente real: só reiniciar o serviço (sem migração) e conferir que o estado começou a ser escrito, só com
   contagens.

Depois da fatia C, com as três suítes verdes, sai o commit único da feature 091.

## Riscos

| Risco | Mitigação |
| :--- | :--- |
| A configuração enxuta pode piorar sob feedback ruidoso (sem *replay*) | medição C-Q2 antes; guarda C-Q3 no produto; o adaptador só liga com 30 revisados |
| Estado crescer demais | podas do EXP-024 (2 000 e 300 hashes); teto de 1 MB testado |
| Concorrência (dois salvamentos do mesmo usuário) | lock por usuário no processo único; gravação numa transação curta |
| Artefato trocado no futuro (v3) | o estado guarda o SHA-256; com outro artefato, volta ao estático até a reconstrução |
| Páginas sem `lines` (como o primeiro registro real) | saem `misaligned`, sem aprender; o contador de revisados conta igual, mas a guarda impede um adaptador mal treinado |
