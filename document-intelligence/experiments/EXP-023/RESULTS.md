# EXP-023: Relatório de Resultados — Organização Automática nas 4 Seções do Estudo

* **Status:** `CONCLUÍDO` (executado em 2026-10-27, com as decisões do usuário da spec §11). A adoção no produto
  está no [ADR-010](../../docs/adr/ADR-010-organizacao-nas-4-secoes.md), `ACCEPTED` pelo usuário em 2026-10-27.
* **Executor:** Claude Code
* **Artefatos:**
  - [spec.md](./spec.md);
  - [`artifacts/organizer-v1.json`](./artifacts/organizer-v1.json) (SHA-256 em `organizer-v1.sha256`);
  - [`artifacts/thresholds.json`](./artifacts/thresholds.json), registrado antes do teste;
  - benchmarks `BENCHMARK-20261027-exp-023-organizer.json` e `BENCHMARK-20261027-exp-023-dusuario.json`.

> **Dados e privacidade.**
> - D-semente e D-sintético são textos fictícios escritos para o projeto (MIT), congelados com SHA-256 antes de
>   qualquer regra (commit `3716816`).
> - O ruído vem só de contagens de erro do EXP-015, guardadas fora do Git.
> - D-usuário rodou sobre uma cópia temporária do banco, feita pela API de backup, com origem e cópia em `mode=ro`
>   e apagada no fim. Nenhum texto dos estudos foi impresso, gravado ou lido pelo agente; o relatório tem só
>   números.

---

## 1. Resposta

Nas páginas fictícias, a pipeline em Python puro distribui o texto nas 4 seções com **Macro-F1 de 0,93 no texto
limpo** e **0,82 com 25 % de erro de leitura**, quando há a geometria das linhas. Leva **menos de 10 ms por
página**, sem dependência nova. Passa no portão de produto registrado antes do teste.

Duas ressalvas pesam na decisão:

1. **Nos estudos reais do usuário, o acerto cai para 0,50.** São só 3 estudos, mas a queda é grande demais para
   ser ruído. O estilo real (fichamentos salvos no Leitorum) é diferente do estilo dos dados fictícios, que foram
   escritos pela mesma mão que escreveu as regras.
2. **A matriz relacional ajudou menos do que o previsto.** A validação zerou a inércia de transição e a
   propagação de rótulos. O que funcionou foi o **custo de troca de seção ponderado pela coesão** entre vizinhos.

| Hipótese | Veredito | Evidência (teste, pipeline completa V4) |
| :--- | :--- | :--- |
| H1 — híbrido ≥ melhor componente + 5 pontos | **Refutada** | limpo: 0,932 contra 0,921 (+1,1); CER 25 %: 0,818 contra 0,776 (+4,2) |
| H2 — WindowDiff −20 % sem perder > 1 ponto de F1 | **Refutada** | −8,8 % em média; F1 não cai (+0,1 ponto) |
| H3 — p95 ≤ 200 ms por página | **Confirmada** (página); **falha** na montagem a frio dos centróides do usuário | p95 8,2 ms nas páginas fictícias e 42 ms nos estudos reais (textos longos); montagem: 1,2 s por 100 estudos, ~6 s para 500 (meta: 2 s) |
| H4 — centróides do usuário +3 pontos | **Inconclusiva** (N = 3) | 0,50 → 0,62 com κ = 50, só um usuário com 2 estudos |
| Portão de produto (0,70 limpo / 0,60 com ruído) | **Atingido no D-sintético** | 0,908 (digitado, sem geometria) / 0,825 (CER 25 %, com geometria) |

## 2. Resultados no teste (D-sintético: 4 temas, 24 páginas)

Macro-F1 por caractere. Benchmark: commit `58dac1e`, árvore limpa.

| Condição | B0 maioria | B1 cabeçalhos | B2 só pistas | B3 só léxico | V1 híbrido | V2 + T | V3 + custo de troca | **V4 completa** |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| limpo, com geometria | 0,141 | 0,212 | 0,921 | 0,737 | 0,932 | 0,932 | 0,934 | **0,934** |
| limpo, sem geometria | 0,141 | 0,212 | 0,892 | 0,735 | 0,904 | 0,904 | 0,908 | **0,908** |
| CER 10 %, com geometria | 0,141 | 0,202 | 0,876 | 0,685 | 0,882 | 0,882 | 0,891 | **0,891** |
| CER 10 %, sem geometria | 0,141 | 0,202 | 0,828 | 0,659 | 0,838 | 0,838 | 0,841 | **0,841** |
| CER 25 %, com geometria | 0,140 | 0,140 | 0,776 | 0,531 | 0,818 | 0,818 | 0,825 | **0,825** |
| CER 25 %, sem geometria | 0,140 | 0,140 | 0,684 | 0,520 | 0,708 | 0,708 | 0,710 | **0,710** |

Pipeline completa (V4), demais métricas:

| Condição | WindowDiff | $P_k$ | Fragmentação | ECE | F1 das fronteiras de trecho | Caracteres a mover |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| limpo, com geometria | 0,106 | 0,097 | 1,04 | 0,021 | 0,91 | 7,6 % |
| limpo, sem geometria | 0,144 | 0,135 | 1,01 | 0,031 | 0,81 | 10,5 % |
| CER 25 %, com geometria | 0,198 | 0,192 | 0,96 | 0,042 | 0,73 | 19,5 % |
| CER 25 %, sem geometria | 0,319 | 0,313 | 0,70 | 0,045 | 0,48 | 31,7 % |

- **Por seção:**
  - Referências é a mais fácil: 0,91 a 0,99, graças aos padrões ABNT, às aspas e às remissões.
  - Resumo é a que mais sofre com ruído sem geometria: 0,60.
- **Calibração:** a confiança é bem calibrada (ECE ≤ 0,045). A margem de "conferir" foi fixada na validação em
  0,20, o ponto em que as unidades acima dela acertam ≥ 90 %.
- **Geometria:** vale de 3 a 11 pontos de Macro-F1. Ela ajuda sobretudo a separar parágrafos quando o ruído
  apaga a pontuação.

### O que a validação escolheu (8 parâmetros)

- **Transição e propagação desligadas.** A busca pôs a inércia ($\tau$), a ordem branda ($\omega$) e a
  propagação ($\alpha$) em **zero**. A ordem das seções ajuda pouco porque as páginas variam a ordem de propósito.
  Já a propagação espalhava erros entre vizinhos parecidos.
- **Custo de troca alto.** A busca escolheu $\lambda = 8$ e confirmou que 16 é pior, com $\sigma_g = 0{,}75$ e
  $\eta = 2$. Trocar de seção dentro de um bloco coeso fica caro.
- **Temperatura:** $\beta = 1{,}25$.
- **Para o produto:** a decodificação pode ser só Viterbi com custo de troca. A propagação e a matriz $T$ ficam
  no código como opção desligada.

## 3. Estudos do usuário (D-usuário)

Pseudo-páginas a partir das colunas de cada estudo, na ordem canônica, sem cabeçalhos e sem geometria (o cenário
da importação de texto digitado).

| Medida | Valor |
| :--- | :--- |
| Estudos no banco / elegíveis / avaliados | 3 / 3 / 3 (2 usuários) |
| Fração de texto por seção | Resumo 29 %, Explicação 36 %, Conceitos 14 %, Referências 21 % |
| **V4, só semente** | **Macro-F1 0,497**: Resumo 0,75; Explicação 0,45; Conceitos 0,50; Referências 0,29; WindowDiff 0,80 |
| V6, κ = 25 / 50 / 100 | 0,644 / 0,619 / 0,585 |
| Latência p95 | 42 ms (textos longos) |

**Leitura:**
- **Lacuna de domínio grande.** Com 3 estudos, os números não estimam o desempenho real com precisão, mas a
  distância entre 0,91 e 0,50 é grande demais para ser acaso.
- **Referências reais quase não são reconhecidas (0,29).** As regras esperam ABNT, autor-data e aspas.
- **A calibração com os estudos do usuário é promissora, mas sem base estatística.** No único usuário com 2
  estudos, cada um calibra o outro.
- Pela decisão 1 da spec, com N pequeno o D-sintético decide o portão, e este resultado entra como alerta.

## 4. O que fica de fora ou em aberto

- **D-prata (artigos CC-BY) não foi montado.** Exigiria baixar e conferir a licença de cada fonte, e o D-usuário
  já mostrou o que a prata mostraria: a distância para texto real. Fica para quando houver necessidade de outro
  domínio.
- **V5 (LSA ou embeddings estáticos) não rodou.** Nenhum corpus ou modelo com licença verificada (spec §4.2). Além
  disso, a H1 mostrou que o léxico já contribui pouco sobre as pistas.
- **Montagem a frio dos centróides do usuário** acima da meta: ~6 s estimados para 500 estudos. Para ser padrão,
  precisaria de cache incremental por estudo.

## 5. Recomendação (ver ADR-010)

1. **Levar ao Leitorum só como botão explícito "Organizar nas 4 seções"**, sempre revisável: lista de "Seções
   para conferir", "Voltar para texto único", nada salvo sozinho. Usar o artefato `organizer-v1.json` com
   decodificação só por custo de troca. A calibração com os estudos do usuário fica desligada (decisão 3).
2. **Antes de prometer qualidade em texto real:**
   - repetir o D-usuário quando houver pelo menos 30 estudos;
   - ampliar as pistas de Referências para os formatos que aparecem nos fichamentos (listas em markdown,
     "Título — Autor", links);
   - medir em páginas reais de caderno quando elas existirem.

## 6. Reprodução

```powershell
$e = "experiments/EXP-023/envs/organizer"
uv run --frozen --project $e python experiments/EXP-023/harness/noise.py     # modelo de ruído (do EXP-015)
uv run --frozen --project $e python experiments/EXP-023/harness/train.py     # pesos e parâmetros (treino/validação)
uv run --frozen --project $e python experiments/EXP-023/harness/evaluate.py --split val
uv run --frozen --project $e python experiments/EXP-023/harness/evaluate.py --split test --out evaluation/benchmarks/bench.json
uv run --frozen --project $e python experiments/EXP-023/harness/dusuario.py --out evaluation/benchmarks/dusuario.json   # só com autorização
uv run --frozen --project $e python -m pytest experiments/EXP-023/tests
```

*Assinatura do agente executor:* `Claude Code (claude-opus-5-5), 2026-10-27`
