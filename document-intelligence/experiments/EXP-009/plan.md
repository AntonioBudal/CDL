# Plano e Tarefas: EXP-009 — Leitura de Manuscrito em Português com o Reconhecedor do PP-OCR

* **Especificação:** [`spec.md`](./spec.md) (`DELEGATED`, 2026-10-14)
* **Status:** `DELEGATED` — executado por delegação; o usuário revisa com os resultados

## Método

* **Ambiente:** `experiments/EXP-008/envs/ppocr` (Python 3.12, `rapidocr` 3.10.0, ONNX Runtime), sem mudanças.
  Modelos embutidos no wheel: `PP-OCRv6_det_small.onnx` (SHA-256 `090f04ab…`) e `PP-OCRv6_rec_small.onnx`
  (SHA-256 `6f327246…`), conferidos antes da carga. O classificador de orientação não é usado.
* **Recorte de linha:** para linhas com contorno, o retângulo mínimo é desentortado por perspectiva; senão, a caixa.
* **Ponta a ponta:** detecção → fusão do EXP-008 (`v_overlap` 0,7; `max_gap` 1,0; `max_angle` 20°) → leitura de
  cada linha → linhas ordenadas de cima para baixo (centro vertical; em empate, da esquerda para a direita) →
  texto da página.
* **Teto de página:** as linhas verdadeiras do BRESSAY (os recortes do próprio dataset), na ordem da numeração.
* **Métricas:** CER e WER micro (total de edições / total de unidades), como no EXP-001; CER de página com a
  normalização da spec (FR-002); CER por classe de caractere a partir do alinhamento de Levenshtein.

## Conjuntos

| Conjunto | Origem | Unidades |
| :--- | :--- | ---: |
| `lines-exp001` | `dataset/raw/exp-001/bressay-subset/` (manifesto do EXP-001) | 398 linhas |
| `lines-gnhk` | GNHK teste: linhas manuscritas legíveis, recortadas das fotos de trabalho do EXP-007 | ~2.000 |
| `pages-bressay` | BRESSAY teste (185 páginas utilizáveis do EXP-007, ampliadas 3×) | 185 páginas |
| `lines-bressay` | todos os recortes de linha dessas 185 páginas (para o teto de página) | ~5.500 |

Imagens de trabalho e manifestos com texto ficam fora do Git, em `dataset/processed/exp-009/`.

## Tarefas

- [ ] **T001** Copiar do EXP-008 o supervisor, o worker e a fusão; prefixo `@@EXP009`.
- [ ] **T002** `prepare.py`: manifestos dos quatro conjuntos; recortes das linhas do GNHK; texto das páginas.
- [ ] **T003** Adaptadores `ppocr_rec` (lê um recorte de linha) e `ppocr_page` (detecção + fusão + leitura) com
  testes de recorte e de ordenação em dados fictícios.
- [ ] **T004** `evaluate.py`: CER/WER de linha e de página, normalização de página, CER por classe de caractere,
  com testes.
- [ ] **T005** Rodar os quatro conjuntos (RAM livre ≥ 1 GiB).
- [ ] **T006** `run.py`: relatório, vereditos, LDF 2.0 das páginas; árvore limpa.
- [ ] **T007** `RESULTS.md`, ADR-007, registros, verificação final.

Estimativa: cerca de 8 mil leituras de linha e 185 detecções de página; algo entre 20 e 40 minutos de máquina.
