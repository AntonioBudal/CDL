# EXP-025 — `organizer-v2` estático com as pistas de referência reais (especificação, plano e tarefas)

**Created**: 2026-10-28 · **Status**: `CONCLUÍDO` (2026-10-28, por delegação; ver [RESULTS.md](./RESULTS.md) e o ADR-011 `ACCEPTED`)

**Input**: pedido do usuário depois do EXP-024, passo 1. Treinar e exportar um `organizer-v2.json` **estático**
(sem estado por usuário) que incorpore as pistas de Referências que, no EXP-024, levaram o F1 de Referências do
perfil de fichamento em lista de 0,00 a 0,78. A integração no Leitorum é uma feature de produto separada, com Spec
Kit próprio e aprovação do usuário.

## 1. Pergunta e hipóteses

As 4 pistas fixas de referência do EXP-024, aprendidas **em lote** (sem aprendizado online), melhoram o
Organizador nos formatos reais de fichamento sem piorar o que o v1 já acerta?

- **H1 — formatos reais.** No *holdout* de teste do EXP-024 (estático, texto limpo, os 4 perfis), o Macro-F1 médio
  do v2 fica **≥ 3 pontos** acima do v1, e o F1 de Referências do perfil P1 fica **≥ 0,50** (v1: 0,00).
- **H2 — sem regressão.** No teste do EXP-023, nas 6 condições (limpo, CER 10 % e CER 25 %, com e sem geometria), o
  v2 fica **no máximo 1 ponto** abaixo do v1 em cada uma.
- **H3 — estudos reais.** No D-usuário estático (todos os estudos elegíveis; banco ativo do D:, só números), o v2
  **não fica abaixo** do v1. Com N pequeno, é alerta.
- **H4 — custo.** A latência p95 por página fica até **1 ms** acima da do v1.
- **Portão de adoção (ADR-011):** H1, H2 e H4 confirmadas, e H3 sem piora.

## 2. Modelo

- **Base:** a pipeline do EXP-023, inalterada: segmentação, as 37 pistas, o L0 (4 colunas `sim_*` contra os
  centróides-semente), a coesão e o Viterbi com custo de troca.
- **Colunas novas (4), as regras fixas do EXP-024**, todas com valor 0 ou 1:

  | Coluna | Expressão (Python `re`) | Exemplo fictício |
  | :--- | :--- | :--- |
  | `ref_md_title_author` | `^\s*(?:[-*•]\|\d{1,2}[.)])\s+\S.{0,120}?\s[—–]\s+\S` (com `match`) | `- A margem e o centro — Lúcia Dantas` |
  | `ref_md_link` | `\[[^\]\n]{2,}\]\((?:https?://\|www\.)[^)\s]+\)` (com `search`) | `- [Chuva e cidade](https://exemplo.org/chuva)` |
  | `ref_url_line` | `^\s*(?:[-*•]\s+)?(?:https?://\|www\.)\S+\s*$` (com `match`) | `https://exemplo.org/chuva` |
  | `ref_title_author_year` | `\([A-ZÁ-Ú][^()\n]{2,60},\s*(?:1[5-9]\d\d\|20\d\d)\)\s*\.?\s*$` (com `search`) | `Céus de outros povos (Patrícia Moura, 2012)` |

  As expressões vão no artefato (`extra_cues`), para o produto reproduzir exatamente.
- **Ficam de fora**, por serem por usuário ou por terem piorado o resultado no EXP-024:
  - a forma de linha aprendida;
  - os centróides do leitor e do livro;
  - $T_{\text{user}}$;
  - o aprendizado online.
- **Parâmetros relacionais:** os do v1 (τ = ω = α = 0, λ = 8, σ_g = 0,75, η = 2, w = 3), mantidos. O C, a temperatura
  β e a margem de "conferir" são reajustados na validação.

## 3. Dados

| Papel | Conteúdo |
| :--- | :--- |
| **treino** | treino do D-sintético do EXP-023 (12 temas; limpo, CER 10 % e 25 %; com e sem geometria), mais as **páginas de adaptação dos fluxos de VALIDAÇÃO do EXP-024** (4 perfis × 40, mesmas condições), que trazem os formatos de fichamento |
| **validação** | validação do EXP-023 mais o *holdout* dos fluxos de VALIDAÇÃO do EXP-024 |
| **teste** | teste do EXP-023 (H2); *holdout* dos fluxos de TESTE do EXP-024 (H1); D-usuário (H3) |

- **Disjunção:** os fluxos de teste do EXP-024 usam outros livros, termos e obras.
- **Risco declarado:** os formatos de linha (os modelos de referência) são os mesmos nos dois splits do EXP-024. A
  H1 mede o reconhecimento do **formato** em obras novas, não em formatos novos. Por isso o D-usuário é a checagem
  externa.

## 4. Plano, tarefas e commits (`FNN(document-inteligence) [EXP-025] …`)

| Fase | Entrega |
| :--- | :--- |
| F01 | esta especificação |
| F02 | `harness/train.py` (Python, NumPy e scikit-learn no ambiente do EXP-023): pistas novas, treino, validação e exportação de `artifacts/organizer-v2.json` (SHA-256) e `artifacts/parity-v2.json` (casos fictícios para o produto); testes (o v2 com as colunas novas zeradas reproduz o v1 na estrutura; determinismo; expressões iguais às do EXP-024) |
| F03 | `harness/evaluate.py --split test` uma vez (H1, H2, H4); `harness/dusuario_static.py` (H3, só números); benchmarks auditados por um subagente; `RESULTS.md`; ADR-011 (`PROPOSED`) se o portão for atingido |

- **Recursos:** sem download, menos de 50 MB, menos de 500 MB de RAM.
- **Privacidade:** a do EXP-024 (cópia pela API de backup, `mode=ro`, apagada no fim, só números).
- **Escopo:** nada em `caderno-leitura-0.1/`. A troca do artefato no Leitorum depende da feature de produto.

## 5. Decisão tomada na validação (F02, antes de abrir o teste)

| Modo (validação) | EXP-024 *holdout*, média | Referências do P1 | P3 | EXP-023, 6 condições |
| :--- | ---: | ---: | ---: | :--- |
| v1 | 0,662 | 0,000 | 0,979 | 0,920 / 0,871 / 0,886 / 0,846 / 0,801 / 0,736 |
| `full` (retreino de todos os pesos) | 0,827 | 0,933 | **0,872** | até **2,9 pontos abaixo** do v1 |
| **`cues`** (v1 congelado, só as 4 pistas aprendidas) | **0,740** | **0,507** | 0,979 | **idêntico ao v1** nas 6 |

- **Escolhido o `cues`.** O `full` ganha mais nos fichamentos, mas desloca o modelo inteiro: o P3 perde 10,7
  pontos e as páginas do EXP-023 reprovariam a H2.
- O `cues` só muda o que as pistas tocam:
  - pesos, viés, temperatura (β = 1,25) e margem de "conferir" (0,20) do v1 continuam iguais;
  - L2 = 0,001, escolhida na validação.
- **Artefato:** `artifacts/organizer-v2.json`, SHA-256 `9f6530a32726d593142b7a2de3bce3efc1c0095abf3a91335364db6343978aee`
  (determinístico: o retreino dá o mesmo hash).
