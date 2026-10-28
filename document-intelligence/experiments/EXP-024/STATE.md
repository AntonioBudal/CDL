# EXP-024 — Estado do experimento

Melhoria contínua autônoma do Organizador das 4 seções e da pós-correção da digitalização.

Este arquivo é o diário de bordo: é atualizado ao fim de cada fase, antes do commit da fase.

## Fases

| Fase | Conteúdo | Estado | Commit |
| :--- | :--- | :--- | :--- |
| F00 | Diagnóstico e linha de base (só leitura) | **concluída em 2026-10-28** | `F00` (este) |
| F01 | Pesquisa e especificação: `spec.md`, `plan.md`, `tasks.md` | **concluída e aprovada em 2026-10-28** | `F01` |
| F02 | Fluxos longitudinais sintéticos e simulador de feedback | **concluída em 2026-10-28** | `F02` |
| F03 | Motor adaptativo em Python puro e travas anti-regressão | **concluída em 2026-10-28** | `F03` |
| F04 | Calibração, curvas de aprendizado, ablações, estresse e D-usuário | pendente | — |
| F05 | `RESULTS.md`, ADR-011 (se houver adoção) e fechamento; **para para revisão do usuário** | pendente | — |

## F00 — Linha de base (2026-10-28)

### Verificações

| Comando (a partir de `document-intelligence/`) | Resultado |
| :--- | :--- |
| `uv run pytest` | 239 aprovados |
| `uv run ruff check .` | sem avisos |
| `uv run --frozen --project experiments/EXP-023/envs/organizer python -m pytest experiments/EXP-023/tests` | 14 aprovados |

- **Commit de partida:** `aaca5f8`, com a árvore de `document-intelligence/` limpa.
- **Disco:** 13,97 GB em `document-intelligence/`, abaixo do teto de 20 GB; 106 GB livres no C:.
- **RAM livre na medição:** 0,89 GB. Basta para os testes. Qualquer etapa que carregue o motor de leitura espera
  ≥ 1,5 GB livres, pela regra das rodadas longas.

### Artefatos herdados (conferidos)

| Artefato | SHA-256 |
| :--- | :--- |
| `experiments/EXP-023/artifacts/organizer-v1.json` | `60d6538de49495e4bfc01e00f048d5f4c0d1e55a7a84d6df33de9fee99c40d28` (igual ao `organizer-v1.sha256`) |
| `dataset/processed/exp-023/noise-model.json` (fora do Git, só contagens) | existe; CER 29,0 % sobre 495 864 caracteres do EXP-015 |

### Fatos de partida (EXP-023, ADR-010)

- Organizador `V4`, só semente: Macro-F1 0,934 no limpo e 0,825 com CER 25 %, nas páginas fictícias.
- **D-usuário:** só **3 estudos de 2 usuários**. Macro-F1 0,497; `references` 0,29.
- **`V6` com centróides do usuário:** 0,644 (κ = 25). A hipótese H4 ficou **inconclusiva** pelo N.
- **Montagem a frio dos centróides:** 1,2 s por 100 estudos, ~6 s estimados para 500 (meta: 2 s).
- **Parâmetros:** a validação zerou τ, ω e α. Ficaram λ = 8, σ_g = 0,75, η = 2 e β = 1,25.

### Divergências encontradas no diagnóstico (a tratar na F01)

1. **O LDF 2.0 não tem as 4 seções do Estudo.**
   - `semantics.sections.role` aceita só `title`, `summary`, `concept`, `question`, `quote`, `example`,
     `margin_note` e `other`. Não há `explanation` nem `references`.
   - Cada seção aponta para regiões (`region_ids`), não para trechos de texto.
   - O schema 2.0 está congelado (ADR-004).

   Conclusão: `human_corrections` serve direto para as correções de leitura (`recognition.lines`, `replace
   /text`). Os movimentos de seção do organizador não cabem nele sem perda. A decisão fica na spec (Categoria 2).
2. **O banco ativo mudou de lugar.**
   - Desde a feature 090-A do Leitorum (2026-10-28), o banco ativo é `D:\Leitorum\db\caderno.db`.
   - `caderno-leitura-0.1/backend/data/caderno.db` ficou como origem congelada da migração, guardada para
     rollback.
   - O `dusuario.py` do EXP-023 aponta para o caminho antigo.

   Qual cópia o D-usuário da F04 deve ler é decisão do usuário, na revisão da F01.
3. **O ruído do EXP-015 é global, não por escritor.** O `noise-model.json` tem taxas por caractere, sem
   identidade de escritor. Os "confundidores recorrentes por escritor" do simulador terão de ser sintéticos,
   declarados como tal.

## F01 — Especificação (2026-10-28)

- **Artefatos:** [spec.md](./spec.md), [plan.md](./plan.md) e [tasks.md](./tasks.md).
- **Decisões de Categoria 2 registradas:**
  - pesos por **regressão logística online com âncora L2 e projeção**, e não Passive-Aggressive, para preservar a
    calibração (spec §4.6);
  - movimentos de seção em RFC 6902 sobre `organizer-result/1`, e correções de leitura em `human_corrections` do
    LDF 2.0 (spec §6.1);
  - pesos iniciais dos sinais (spec §6.3);
  - schema do estado `leitorum-learning-state/1` (plan §4.1).
- **Achados que mudaram o desenho:**
  - estudos importados não alimentam $T_{\text{user}}$, porque as colunas não guardam a ordem das unidades;
  - no D-usuário, $T_{\text{user}}$ fica desligado, porque as pseudo-páginas estão na ordem canônica e isso daria
    ganho falso.
- **Revisão do usuário (2026-10-28):** F01 aprovada. O D-usuário da F04 lê o **banco ativo do D:**
  (`D:\Leitorum\db\caderno.db`), sempre por cópia temporária via API de backup, em modo só leitura.

## F02 — Fluxos longitudinais e simulador (2026-10-28)

### Dados congelados (2026-10-28, antes de qualquer código de fluxo, simulador ou motor)

Conteúdo normalizado para LF; conferido por `streams.verify_frozen()`.

| Arquivo | SHA-256 |
| :--- | :--- |
| `data/canario.json` | `773edf9dcfb7d6ac20df2f40d0465d854752b57665c25a2eb280f636f3157f8b` |
| `data/confusoes-escritores.json` | `4c5852b1882d69e94ff3f3341e0c00d5dceda187c25f6a6755dc193e2b29a567` |
| `data/frases/reescritas.json` | `30dc2acfb8d4b6e540cd74728e1344a09df768bc4b8fe34ffa17174fe44ccf3c` |
| `data/frases/referencias.json` | `01e4dd8a4db25ef00a02594827da4c18cd9dfec34fa5b779bab266bbaad4a094` |
| `data/frases/secoes.json` | `5d7f167d7a0dec8ecc4bde1b23e61086789f33601606d2f8660f3fa77337a41c` |
| `data/livros.json` | `397664e61b52e5a6389f027c85bccc177c531de0e11e7b530d37dec9dfd6ed00` |
| `data/perfis.json` | `73878fdfa2006c79b1162311e78af3b5aec93690f32970e1c52cc072104b387f` |

- **16 livros fictícios:** 4 perfis × 2 livros de validação + 2 de teste. Cada livro tem 8 termos com glosa e 5
  obras relacionadas.
- **Bancos de frases:** 32 de resumo, 36 de explicação (8 em primeira pessoa), 20 de conceito, 8 citações, 8
  formatos de referência e 20 reescritas autorais (R3).
- **Confundidores de leitura por escritor:** **sintéticos e declarados** (W1–W4, 4 regras cada).
- **Canário:** 8 páginas do split de **teste** do EXP-023, referenciadas pelo SHA-256 do texto.

### Fluxos (`harness/streams.py`)

- **Tamanho:** 4 perfis × 2 splits (validação e teste, com livros disjuntos) × (40 páginas de adaptação + 2 × 12
  *holdout*) = **512 páginas**.
- **Vazamento zero** entre adaptação e *holdout*, por teste: nenhum trecho repetido e Jaccard de 4-gramas de
  palavras < 0,5 em todos os pares. A divisão é por *hash*: modelos de frase (70/30), 3 de 8 termos e 2 de 5 obras
  por livro reservados ao *holdout*. O livro principal só é citado na adaptação.

### Simulador (`harness/simulator.py`)

- **Leitura:** confundidores do escritor, depois o modelo global do EXP-015 com **dificuldade por linha**
  log-normal (σ = 0,6). Sem ela, a confiança não separava as linhas ruins (29,6 % contra 25,2 % de CER).
- **CER medido** nos fluxos de validação: alvo 10 % → 9,4 %; alvo 25 % → 23,3 %. Dentro de ±2 pontos.
- **Confiança por linha:** Beta com média 1,0 − 0,6 × erro da linha, concentração 16, calibrada só na validação
  contra a 086. A 27 % de CER: 20,0 % das linhas marcadas (086: 20,7 %), CER 40,5 % nelas contra 21,8 % nas demais
  (086: 43,5 % e 23,7 %).
- **Leitor simulado:**
  - move 85 % dos trechos errados marcados "conferir" e 45 % dos não marcados;
  - corrige 90 % das palavras erradas em linhas de baixa confiança e 55 % nas demais;
  - reverte em 3 % das páginas, ou em 30 % quando a sugestão acerta menos da metade.
- **Regimes:**
  - **R1:** sem nota.
  - **R2:** nota coerente com a qualidade da sugestão.
  - **R3:** exatamente 20 % de páginas ruidosas, em rodízio: nota contraditória, salva sem revisar e reescrita
    autoral.
- **Primeiro sinal:** com o organizador estático (V4), a qualidade média da sugestão no perfil P1 (referências em
  lista e links) ficou em **0,51**. É perto do 0,497 do D-usuário no EXP-023: o perfil reproduz a lacuna real.

### Verificações

| Comando | Resultado |
| :--- | :--- |
| `uv run --frozen --project experiments/EXP-023/envs/organizer python -m pytest experiments/EXP-024/tests` | 18 aprovados |
| `uv run ruff check .` e `uv run ruff format --check experiments/EXP-024` | sem avisos |
| `uv run pytest` | 239 aprovados |

## F03 — Motor adaptativo e travas (2026-10-28)

### Módulos (só biblioteca padrão; teste garante que nenhum importa NumPy)

| Arquivo | Conteúdo |
| :--- | :--- |
| `harness/state.py` | schema `leitorum-learning-state/1`, poda determinística, (de)serialização |
| `harness/diff_signal.py` | alinhamento sugestão × salvo e lido × revisado, `classify_edit`, RFC 6902 (LDF 2.0 e `organizer-result/1`) |
| `harness/adaptive_organizer.py` | pistas novas, centróides do leitor e do livro, regressão logística online ancorada, $T_{\text{user}}$, $\beta$, ordem por informação e clique (E4/E4b) |
| `harness/adaptive_ocr_corrector.py` | léxico de 1ª parte, confusões pessoais, canal ruidoso, `low_confidence`, curadoria |
| `harness/safety_gate.py` | pesos por página (gating), projeção, portão-sombra |

### Mudanças de desenho em relação à spec (achados medidos nos fluxos de VALIDAÇÃO, nunca no teste)

1. **Centróides do leitor e do livro viraram colunas novas** (`usim_*`, `bsim_*`, peso 0 na âncora), em vez de
   misturados aos centróides-semente (spec §4.3).
   - Misturados, eles pioravam sem parar: P1, só centróides, 0,456 → 0,363.
   - Causa: os pesos $W_0$ do EXP-023 foram treinados para semelhanças contra a semente. Trocar o centróide muda
     escala e sentido das colunas `sim_*` sob pesos fixos. Além disso, o vocabulário do livro aparece nas quatro
     seções, e a semelhança passa a medir assunto, não seção.
   - A versão contrastiva (tirar a média das 4 seções) não resolveu.
   - Com colunas novas, a âncora reproduz o V4 exatamente e o aprendizado decide quanto confiar nelas.
2. **Trecho mantido sem marca "conferir" vale pouco** (`unreviewed_factor` = 0,2). É a própria previsão confiante
   do motor; aprender dela é autotreino e reforça erros. O trecho marcado que o leitor conferiu e manteve continua
   com o peso cheio.
3. **Portão com replay do próprio leitor** (além da semente): a atualização é desfeita se piorar o acerto nas
   últimas 120 correções confiáveis do leitor (ε = 0,02). Sem ele, o perfil P3 (estilo que o V4 já acerta, 0,975)
   caía para 0,884 no R3; com ele, o pior ponto ficou em 0,954.
4. **Curadoria com léxico:** a linha curada precisa ter todas as palavras já conhecidas no léxico antes da página.
   Precisão nos fluxos de validação: 0,49 → 0,91 (R1) e 0,88 (R3), com menos pares.
5. **O pacote de feedback leva o layout** das linhas (`organizer.layout`): sem ele, a re-análise na hora de
   aprender segmentava diferente da sugestão ("misaligned").
6. **Tamanho do estado:** somas podadas em 2 000 entradas por seção no usuário e 300 no livro, números com 5 casas.

### Primeiros sinais (smoke na validação, parâmetros ainda não calibrados)

- **Organizador, Macro-F1 *holdout* em texto limpo, V4 → t = 40 (R1):**
  - P1 0,456 → 0,582;
  - P2 0,406 → 0,513;
  - P3 0,975 → 0,975;
  - P4 0,590 → 0,585.

  O replay rejeitou de 12 a 22 das 40 atualizações; o equilíbrio fica para a calibração.
- **Leitura (P1, 25 % de CER):**
  - CER 23,2 % → 22,2 % (queda relativa de 4 %);
  - erro em acentos 76 % → 67 %.

  Mesmo com limiares agressivos, o teto ficou em 21,6 % e 59,5 %: a 25 % de CER muitas palavras têm 2 ou mais
  erros. É o mesmo achado do EXP-011, e a H2 pode ser refutada.
- **Limiar de `low_confidence`:** quase não se forma no simulador, porque a 25 % de CER quase toda linha é editada.

### Verificações

| Comando | Resultado |
| :--- | :--- |
| `uv run --frozen --project experiments/EXP-023/envs/organizer python -m pytest experiments/EXP-024/tests` | 43 aprovados, 1 pulado (o de LDF) |
| `uv run pytest experiments/EXP-024/tests/test_ldf_patches.py` (ambiente principal, com `jsonschema`) | 2 aprovados |
| `uv run ruff check .` e `uv run ruff format --check experiments/EXP-024` | sem avisos |
| `uv run pytest` | 239 aprovados |

Os testes cobrem:
- âncora igual ao V4 do EXP-023 e usuário novo igual ao estático;
- texto nunca reescrito e determinismo;
- mediana da atualização < 25 ms (o p95 é medido na F04);
- isolamento por `user_id`;
- projeção;
- rollback pelo portão-sombra e pelo replay;
- gating;
- ida e volta do estado (< 512 KB);
- clique;
- restauração de acento e proteção de palavra conhecida;
- confusões aprendidas;
- ausência de NumPy.

## Próximo passo

F04: `calibrate.py` (só validação, `thresholds.json` congelado antes do teste), `evaluate.py --split test`,
`dusuario_continual.py` (banco ativo do D:, só números) e auditoria dos benchmarks.
