# EXP-011: Relatório de Resultados — Correção Lexical da Leitura em Português

* **Status:** `ACCEPTED` / `CONCLUÍDO` (executado e aceito por delegação permanente do usuário, 2026-10-18)
* **Executor:** Claude Code
* **Decisão:** evidência acrescentada ao [ADR-007](../../docs/adr/ADR-007-leitura-pp-ocr-sem-portugues-suficiente.md)
* **Artefato do ciclo:** [spec.md](./spec.md)

> **Licenças.** Léxico: `wordfreq` 3.1.1 (código Apache-2.0; dados CC-BY-SA 4.0), conforme declarado — usado só
> como dado de experimento, fora do Git. Leitor: PP-OCRv6 small (Apache-2.0). BRESSAY: `LICENSE STATUS: NEEDS
> VALIDATION`; nada aqui embasa produto. Nenhum texto de referência ou lido aparece neste relatório.

---

## 1. Resposta

**A correção lexical ajuda pouco e quase só nas palavras.** Nas 398 linhas do EXP-001, o erro de palavra cai 7
pontos (74,1 % → 67,0 %), mas o de caractere cai menos de 1 ponto (34,4 % → 33,8 %). Nos acentos, o ganho é de 5
pontos (79,7 % → 74,9 %). O resultado indica que a maior parte do erro não é "palavra quase certa": é leitura
errada demais para um dicionário consertar.

| Hipótese | Veredito | Evidência (398 linhas do EXP-001) |
| :--- | :--- | :--- |
| H1 — WER cai ≥ 10 pontos | **Refutada** | 74,1 % → 67,0 % (−7,1) |
| H2 — CER cai ≥ 3 pontos | **Refutada** | 34,4 % → 33,8 % (−0,6) |
| H3 — acentos caem ≥ 15 pontos | **Refutada** | 79,7 % → 74,9 % (−4,8) |
| H4 — ≤ 20 ms por linha | **Confirmada** | 0,4 ms por linha |
| H5 — ≤ 2 % das palavras certas estragadas | **Confirmada** | 1,0 % (15 de 1.438) |

## 2. Resultados

Benchmark: [`BENCHMARK-20261018-exp-011-lexicon.json`](../../evaluation/benchmarks/BENCHMARK-20261018-exp-011-lexicon.json),
commit `b48cecd`, árvore limpa. Leitor: PP-OCRv6 small, recorte 2× (o melhor do EXP-010).

| Conjunto | CER antes → depois | WER antes → depois | Acentos antes → depois | Linhas com CER < 10 % | Palavras certas estragadas |
| :--- | :--- | :--- | :--- | :--- | ---: |
| 398 linhas do EXP-001 | 34,4 % → **33,8 %** | 74,1 % → **67,0 %** | 79,7 % → 74,9 % | 34 → 52 | 1,0 % |
| 5.496 linhas de teste | 37,8 % → **37,3 %** | 75,1 % → **68,6 %** | 78,5 % → 73,6 % | 469 → 639 | 1,2 % |

* Palavras erradas consertadas: 336 nas linhas do EXP-001; 4.481 em todas as linhas de teste.
* Letras sem acento, dígitos, pontuação e espaços praticamente não mudam: a correção só age onde a palavra já
  estava a um passo de uma palavra portuguesa.

### Calibração (só validação, 4.609 linhas)

Sem correção: CER 41,5 %, WER 77,2 %. Escolhido: léxico de 100 mil palavras, distância 1, palavras de 3 letras ou
mais, troca da forma sem acento quando a acentuada é 20× mais frequente — CER 41,2 %, WER 71,5 %. A distância 2
piora o CER (troca demais) e só melhora o WER marginalmente. As 54 combinações estão em
[`calibration.json`](./calibration.json).

## 3. O que isso diz sobre o próximo passo

O corretor é barato, seguro (1 % de palavras estragadas) e vale manter no pipeline como última etapa. Mas ele não
muda a ordem de grandeza do problema: com um terço dos caracteres errados, o texto lido não serve ao leitor do
Leitorum. O que falta é um reconhecedor que leia caligrafia brasileira — adaptação do modelo, não pós-processamento.

## 4. Desvios e limitações

* Ciclo executado por delegação, sem aprovação intermediária.
* O índice de candidatos a distância 2 é aproximado (declarado no código e nos testes).
* O léxico vem de texto da internet; nomes próprios, gírias e erros de ortografia dos autores das redações não
  estão nele — a correção pode "consertar" um erro original do autor, o que conta como acerto contra a transcrição
  fiel do BRESSAY só se a transcrição também tiver o erro.
* A calibração mediu CER na validação enquanto a leitura do teste rodava; isso não afeta métricas de acerto.

## 5. Reprodução

```powershell
$h = "experiments/EXP-002/envs/harness"
experiments/EXP-011/envs/lex/.venv/Scripts/python.exe  # exportação do léxico (ver spec.md, T001)
uv run --frozen --project $h python experiments/EXP-011/harness/prepare.py
uv run --frozen --project $h python experiments/EXP-011/harness/read.py --set val-lines
uv run --frozen --project $h python experiments/EXP-011/harness/read.py --set lines-bressay
uv run --frozen --project $h python experiments/EXP-011/harness/calibrate.py
uv run --frozen --project $h python experiments/EXP-011/harness/run.py --out evaluation/benchmarks/bench.json
```

*Assinatura do agente executor:* `Claude Code (claude-opus-5-5), 2026-10-18`
