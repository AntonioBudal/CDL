# Plano: EXP-031P — Quais fontes abertas ajudam

**Spec:** [spec.md](./spec.md) · **Data:** 2026-11-22 · **Status:** `DONE`

## Contexto técnico

* **Treino:** o harness do EXP-014 (`model.py`, `train.py`: PyTorch + `onnx2torch` sobre o PP-OCRv6 small,
  ambiente `experiments/EXP-014/envs/ft`), chamado por um script do EXP-031P que recebe a lista de linhas do
  catálogo em vez do BRESSAY. Nenhuma mudança no EXP-014 (só importação).
* **Dados:** linhas pelo catálogo (`tools.catalogo`). Para chegar a 8 mil linhas por grupo, um coletor de lote
  pequeno amplia as amostras do EXP-043:
  * Teklia: arquivos Parquet oficiais da divisão de treino quando ≤ 2 GB; senão, a API de linhas (como no
    EXP-043), 1 requisição por segundo;
  * HTR-United: arquivo do repositório no GitHub (download único do `.zip` da versão), PAGE/ALTO → linhas;
  * cada linha entra com `Catalog.ingest_line` (procedência, licença, condições); arquivos temporários em
    `D:\Leitorum-DI\trabalho\`, apagados depois.
* **Sintético:** gerador do EXP-043 com aumentos fortes, gerado na hora, semente fixa; 8 mil linhas.
* **Medida:** BRESSAY teste e GNHK teste pelos dados já preparados (EXP-014/EXP-007, fora do Git); as 62 linhas
  do autor pelas caixas e textos do EXP-028A/B. CER/WER com a normalização do EXP-027.

## Composição dos grupos (8 mil linhas cada, semente fixa)

| Grupo | Fontes | Regra |
| :--- | :--- | :--- |
| A | RIMES, Moonshines, CREMMA séc. XX, Célestine, Notaires de Paris, Belfort, POPP, NorHand v2 | cota igual por fonte, limitada ao que a fonte tem; o que faltar vai para as maiores (NorHand v2 no máximo 40 %) |
| B | HOME-Alcar, Himanis, CREMMA Medieval, iForal | idem |
| S | sintético | 8 mil linhas geradas |

## Orçamento

| Item | Custo estimado |
| :--- | :--- |
| Coleta (A + B, ~16 mil linhas) | 2–6 h de rede (pausas educadas), < 1 GB no catálogo |
| Treino (5 condições × 392 passos) | ~15 h de CPU, uma condição por vez, retomável |
| Avaliação (6 modelos × 3 conjuntos) | ~2 h |

## Riscos

| Risco | Mitigação |
| :--- | :--- |
| Falta de RAM no meio do treino | espera de RAM livre antes de cada etapa; checkpoint a cada 50 passos; retomada (regra do projeto) |
| Caracteres de outros idiomas fora do dicionário (æ, ø, abreviações medievais) | descartar e contar; se > 20 % das linhas de um grupo, registrar como limitação |
| Diferença de convenção de transcrição (abreviações expandidas no histórico) | é parte do que se mede (H2) |
| Ruído entre condições | mesma semente e mesmo orçamento; se a diferença decisiva for < 1,5 ponto, repetir C0/C1 com outra semente |
