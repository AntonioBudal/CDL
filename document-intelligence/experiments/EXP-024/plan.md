# EXP-024 — Plano técnico

**Spec:** [spec.md](./spec.md) · **Tarefas:** [tasks.md](./tasks.md) · **Estado:** [STATE.md](./STATE.md)

## 1. Ambiente

- **Motor e simulador:** Python 3.13, só biblioteca padrão (`re`, `math`, `difflib`, `json`, `hashlib`, `zlib`,
  `collections`, `dataclasses`, `time`).
- **Organizador base:** o motor reaproveita o do EXP-023 por import, sem copiar nem alterar nada em
  `experiments/EXP-023/`:
  - `harness/organizer.py` (segmentação, pistas, L0, Viterbi);
  - `artifacts/organizer-v1.json`, a âncora $W_0$, conferida pelo SHA-256.
- **Execução:** tudo roda pelo ambiente existente
  `uv run --frozen --project experiments/EXP-023/envs/organizer python …`, que já tem `pytest`. NumPy só em
  `calibrate.py`/`evaluate.py` se precisar de estatística; o motor não importa NumPy (teste dedicado).
- **Lint:** `uv run ruff check .`, a partir de `document-intelligence/`, cobre os arquivos novos.

## 2. Estrutura de arquivos

```text
experiments/EXP-024/
├── spec.md · plan.md · tasks.md · STATE.md · RESULTS.md (F05)
├── data/                         # F02, congelado (SHA256SUMS)
│   ├── perfis.json               # perfis de anotação (estilo, ordem habitual, formatos de referência)
│   ├── livros.json               # livros fictícios: título, autor, capítulos, vocabulário temático
│   ├── frases/                   # bancos de frases fictícias por seção e por estilo (MIT)
│   ├── confusoes-escritores.json # confundidores recorrentes sintéticos por escritor
│   ├── canario.json              # 8 páginas fictícias do portão-sombra
│   └── SHA256SUMS
├── harness/
│   ├── streams.py                # monta os fluxos longitudinais a partir de data/ (determinístico)
│   ├── simulator.py              # leitura ruidosa + leitor simulado (R1, R2, R3) → pacotes de feedback
│   ├── diff_signal.py            # alinhamentos, filtro de ruído de edição, rótulos, JSON Patch
│   ├── adaptive_organizer.py     # estado incremental, atualização online, pistas novas, E4
│   ├── adaptive_ocr_corrector.py # léxico de escopo, confusões pessoais, correção, low_confidence, curadoria
│   ├── safety_gate.py            # gates de recompensa, projeção, portão-sombra, snapshot e rollback
│   ├── state.py                  # (de)serialização versionada do estado por usuário
│   ├── calibrate.py              # F04: busca nos fluxos de validação → artifacts/thresholds.json
│   ├── evaluate.py               # F04: teste, curvas, ablações, estresse, custo
│   └── dusuario_continual.py     # F04: avaliação prequencial em cópia temporária, só números
├── artifacts/
│   └── thresholds.json           # F04, congelado antes do teste
└── tests/
    ├── conftest.py
    ├── test_simulator.py         # F02
    ├── test_diff_signal.py       # F03
    └── test_adaptive_engine.py   # F03
```

## 3. Dados longitudinais (F02)

### 3.1 Perfis

São pelo menos 4. Cada perfil é um JSON com:
- **pesos de estilo:** corrido, telegráfico ou lista;
- **ordem habitual das seções:** uma distribuição sobre permutações. O P2 começa por conceitos;
- **formato de referência:**
  - P1: lista Markdown com "Título — Autor" e links, o estilo inferido do D-usuário;
  - P3: ABNT;
  - P4: misto;
- **taxa de reflexão em 1ª pessoa;**
- **escritor:** índice dos confundidores recorrentes.

### 3.2 Livros e frases

- **Livros:** 2 a 3 por perfil, todos fictícios. Cada um tem título, autor, 3 a 6 capítulos e 30 a 60 termos
  temáticos, alguns com acento de propósito (por exemplo "hermenêutica", "ação comunicativa").
- **Bancos de frases:** por seção e estilo, com lacunas `{termo}`, `{autor}` e `{titulo}`, preenchidas com o
  vocabulário do livro. São escritos à mão para o projeto (MIT) e congelados.

### 3.3 Fluxos

Para cada perfil, dois fluxos independentes, um de **validação** e um de **teste**, com livros e sementes
diferentes. Cada fluxo tem:
- 40 páginas de adaptação, intercalando os livros do perfil;
- 12 páginas *holdout* por livro, nunca vistas na adaptação.

A verificação de vazamento compara os conjuntos de frases preenchidas entre adaptação e *holdout*: interseção
exata vazia, e similaridade Jaccard de 4-gramas de palavras < 0,5 por par.

### 3.4 Leitura ruidosa e confiança

- **Texto:** `noise.corrupt` do EXP-023 (CER-alvo 10 % e 25 %) mais os confundidores do escritor, por exemplo
  `ç→c` sempre, `rn↔m` ou `a→o` em fim de palavra.
- **Confiança da linha:** sorteada por uma Beta cuja média cai com a taxa de erro da linha. É calibrada para
  reproduzir a 086: 20,7 % das linhas abaixo de 0,75, com CER 43,5 % nessas contra 23,7 % nas demais.

## 4. Motor (F03)

### 4.1 Estado por usuário (`state.py`, schema `leitorum-learning-state/1`)

```json
{
  "schema": "leitorum-learning-state/1",
  "anchor_sha256": "60d6538d…",
  "user_id": "u-teste-1",
  "updates": 37,
  "organizer": {
    "user":  {"sums": {"summary": {"12345": 0.42}}, "counts": {"summary": 118.5}},
    "books": {"b-teste-1": {"sums": {}, "counts": {}}},
    "delta_W": [[0.0]], "delta_b": [0.0], "log_beta": 0.223,
    "transitions": {"counts": [[0]], "start": [0]},
    "ref_shapes": {"user": {"- Ttt — Ttt": [9, 1]}, "books": {}},
    "extra_features": ["ref_md_title_author", "ref_md_link", "ref_url_line", "ref_title_author_year", "ref_shape_user"],
    "behaviour": {"pages": 40, "reverted": 2, "blind_saves": 3}
  },
  "reading": {
    "lexicon": {"user": {"hermeneutica": {"hermenêutica": 7}}, "books": {}},
    "confusions": {"c>ç": [14, 3], "rn>m": [5, 2]},
    "low_confidence": {"a": -3.1, "b": 4.2, "threshold": 0.71}
  },
  "last_good": {"delta_W": "…", "delta_b": "…", "log_beta": 0.223, "transitions": "…"}
}
```

- **Poda das somas:** usuário $K = 5000$, livro $K = 1000$. A poda só roda quando passa de $2K$, e é
  determinística: magnitude, com desempate pelo *hash*.
- **Confusões:** `[contagem, linhas distintas]`, para o suporte mínimo.
- **Serialização:** JSON compacto. O tamanho é medido em bytes (H5).

### 4.2 `diff_signal.py`

1. **`align_units(suggested, saved)`:** para cada segmento sugerido, um desfecho (mantida, movida, editada ou
   apagada), a seção final e a razão de semelhança. Estratégia: busca exata do texto normalizado nas seções
   salvas, de trás para frente para lidar com repetição; senão, `difflib.SequenceMatcher` com `autojunk=False`
   contra janelas das seções.
2. **`align_reading(source_lines, revised_text)`:**
   - linhas casadas por `SequenceMatcher` de linhas;
   - depois Levenshtein com *backtrace* por linha;
   - operações locais de até 2 caracteres e trocas de palavra inteira.
3. **`classify_edit(read, revised)`:** `ocr`, `rewrite` ou `ambiguous` (spec §5.1), com $d$ e $a$.
4. **Saída em JSON Patch:**
   - `to_ldf_corrections(…)`: lista no formato `correction` do LDF 2.0, validada contra o schema por
     `leitorum_di.contracts.ldf`;
   - `to_organizer_patch(…)`: RFC 6902 sobre `organizer-result/1`, aplicável pelo `apply_operation` do LDF.

### 4.3 `adaptive_organizer.py`

`AdaptiveOrganizer(base: Organizer, state, params)`:
- **`analyse`:**
  - chama a segmentação e as pistas do EXP-023;
  - acrescenta as pistas novas de referência e `ref_shape_user`;
  - calcula os $s_{ij}$ com os centróides hierárquicos (cache normalizado por escopo, invalidado por versão);
- **`organize(text, layout, book_id)`:** afinidade com $W_0 + \Delta W$ e $\beta$, transição mista, Viterbi e
  marginais. Devolve a saída do EXP-023 mais `review_order`, ordenada por $g_i$;
- **`click(page_state, index, section, local_step=False)`:** restrição rígida, passo local opcional (E4b) e
  re-decodificação;
- **`learn(feedback)`:**
  1. pesos dos rótulos ($\omega$);
  2. gates;
  3. somas de centróides;
  4. formas de referência;
  5. transições;
  6. passos de $W, \mathbf{b}, \beta$ com âncora e projeção;
  7. portão-sombra.

  Devolve um relatório da atualização: aceita ou desfeita, e tempo.

### 4.4 `adaptive_ocr_corrector.py`

`AdaptiveReader(state, global_noise)`:
- **`correct_line(text, book_id)`:**
  - candidatos por índice de apagamentos sobre o léxico do escopo (livro, depois usuário, depois semente);
  - canal pela matriz de confusão pessoal com prior global (custos de Levenshtein ponderados por $-\log P$);
  - margem $\theta$ e regra de proteção;
- **`learn(feedback)`:** atualiza o léxico com o texto salvo, as confusões com as edições `ocr` com suporte, e o
  logístico de `low_confidence`;
- **`curate(feedback)`:** pares aprovados para o EXP-018, com motivo de aceite ou recusa.

### 4.5 `safety_gate.py`

- `reward_gate(feedback) -> GateDecision`;
- `project(delta_W, delta_b, radius)`;
- **`ShadowGate(seed_units, canary_pages)`:**
  - `check(model_view) -> (ok, f1_seed, f1_canary)`;
  - vetores das sementes em cache por versão dos centróides;
  - canário a cada 10 atualizações;
- **`Snapshot`:** cópia de $\Delta W, \Delta\mathbf{b}, \log\beta$ e das transições. O rollback restaura em O(4d).

As somas de centróides e o léxico **não** passam pelo rollback. Elas são aditivas e ponderadas por $\omega$ (a
página rejeitada entra com peso 0), e desfazê-las exigiria um diário por página. Esse desvio é medido no R3.

### 4.6 Simulador e fluxo de uma sessão

```text
página (verdade: seções e texto limpo) ──► leitura ruidosa + confiança ──► AdaptiveReader.correct_line
      ──► AdaptiveOrganizer.organize ──► leitor simulado (regime) ──► pacote de feedback
      ──► AdaptiveReader.learn / AdaptiveOrganizer.learn ──► (holdout em t ∈ {1,5,10,20,40})
```

O leitor simulado só vê a sugestão e a verdade. Ele decide o que corrigir com as probabilidades do regime e salva
as seções finais. Em R3, injeta os casos ruidosos.

## 5. Calibração e avaliação (F04)

- **`calibrate.py`:** busca em grade, pequena e registrada, só nos fluxos de validação. Parâmetros:
  - $\eta_0$, $\mu$, $\Delta_{\max}$, $\kappa_u$, $\kappa_b$, $\phi_b$, $\kappa_T$;
  - $\omega_0$, $\omega_{\text{keep,blind}}$;
  - $\theta_{\text{ocr}}$, $\theta_{\text{rw}}$, $a_{\min}$, $s_{\min}$, $\theta$, $m$;
  - $\varepsilon$ do portão e $d_{\text{cur}}$.

  O objetivo é a média do Macro-F1 *holdout* em $t = 40$ no R1, com restrição de não regredir em R3, mais o CER.
  Grava `thresholds.json`, os limiares finais das hipóteses (confirmando ou ajustando a spec §7 com justificativa)
  e o SHA-256 do arquivo no `STATE.md` **antes** de abrir o teste.
- **`evaluate.py --split test`:** curvas, ablações, estresse e custo. Grava
  `evaluation/benchmarks/BENCHMARK-AAAAMMDD-exp-024-*.json`.
- **Medição de tempo:** `time.perf_counter_ns`, p50 e p95 sobre todas as atualizações dos fluxos de teste, com
  aquecimento de 3 páginas.
- **`dusuario_continual.py`:**
  - pede `--db` explícito (o usuário escolhe; spec §9);
  - copia pela API de backup para `tempfile.TemporaryDirectory`, origem e cópia em `mode=ro`, apaga no `finally`;
  - avaliação prequencial por usuário, com $T_{\text{user}}$ desligado;
  - imprime só números: N de estudos e de usuários, Macro-F1 V4 contra adaptativo, F1 por seção e N e CER dos
    estudos digitalizados;
  - um teste garante que a saída só tem números e chaves fixas.
- **Auditoria antes de gravar os benchmarks:** um subagente revisor confere se os JSON têm só números e nomes
  fixos.

## 6. Testes (F02–F03)

| Arquivo | O que garante |
| :--- | :--- |
| `test_simulator.py` | determinismo por semente; CER do ruído dentro de ±2 pontos do alvo; confiança × erro reproduzindo a 086 (tolerância declarada); zero vazamento adaptação × *holdout*; regimes com as frações pedidas (R3: 20 % ± 2); SHA-256 dos dados confere |
| `test_diff_signal.py` | alinhamento correto em casos fictícios (mantida, movida, editada, apagada, repetida); classificação `ocr`/`rewrite`; JSON Patch válido e aplicável (LDF via `leitorum_di`, `organizer-result/1` via `apply_operation`) |
| `test_adaptive_engine.py` | determinismo; sem reescrita (a saída do organizador reconstrói o texto); atualização p95 < 25 ms numa sequência fictícia; isolamento por `user_id`; projeção respeitada; portão-sombra desfaz uma atualização destrutiva injetada; estado (de)serializa sem perda; o motor não importa NumPy; pós-correção não muda palavra protegida |

## 7. Riscos de execução

- **Pouca RAM livre (0,9 GB):** o EXP-024 não carrega modelos. O simulador e o motor ficam abaixo de 500 MB.
- **Tempo de calibração:** a grade é pequena (~200 combinações × 4 perfis × 40 páginas). Se passar de 30 min, a
  busca vira por coordenadas, e isso fica registrado.
- **Import do EXP-023:** feito por caminho relativo dentro de `document-intelligence/`, sem sair da fronteira
  (`tests/test_boundary.py`).
