# EXP-001: Ambientes Isolados do Experimento

* **Status:** os três ambientes instalados em 2026-09-30; pesos em `models/exp-001/` (fora do Git), SHA-256 conferidos
* **Hardware e sistema:** os de [`../EXP-000/environment.md`](../EXP-000/environment.md) (CPU-only)
* **`uv`:** 0.11.21

O `pyproject.toml` e o `uv.lock` principais de `document-intelligence/` não foram alterados por estes ambientes.

---

## 1. Ambientes

| Ambiente | Python | Dependência direta | Versões resolvidas (principais) | Pacotes no lock |
| :--- | :--- | :--- | :--- | :--- |
| [`envs/trocr/`](./envs/trocr/pyproject.toml) | 3.14 (o do projeto) | `torch`, `transformers`, `sentencepiece`, `pillow` | torch 2.14.1, transformers 5.18.0, sentencepiece 0.2.2, pillow 12.3.0, numpy 2.5.3 | 57 |
| [`envs/harness/`](./envs/harness/pyproject.toml) | 3.14 | `leitorum-di` (local), `pillow`, `fonttools`, `pytest` | pillow 12.3.0, fonttools 4.66.1, pytest 9.1.1 | 15 — **instalado** (Fase 2) |
| [`envs/pylaia/`](./envs/pylaia/pyproject.toml) | 3.10 | `pylaia==1.1.2` | torch 1.13.1, pytorch-lightning 1.4.2, numpy 1.26.4, pillow 12.3.0 | 63 |

## 2. Resultado da verificação de wheels (Windows x86-64)

* **Stack do TrOCR:** resolve só com wheels em Python 3.14 **e** em 3.13. Não foi preciso rebaixar o Python.
* **PyLaia:** exige Python `>=3.9,<3.11`; por isso o ambiente usa 3.10. Resolve com wheels, exceto `mdutils==1.6.0`,
  que só tem sdist (Python puro) e é construído localmente pelo `uv`.
* `torch` do PyPI no Windows é a compilação CPU; nenhuma dependência de CUDA.

## 3. Observações

* **Python 3.10 gerenciado pelo `uv`:** ao resolver o ambiente do PyLaia, o `uv` baixou sozinho o CPython 3.10.20
  para o seu diretório próprio (`%APPDATA%\uv\python`). Não entra no PATH nem altera o Python do sistema, mas
  fica fora de `document-intelligence/`. Para remover: `uv python uninstall 3.10`.
* **Cache do `uv`:** metadados de pacotes ficam no cache global do `uv`, como em qualquer `uv sync`.
* **Segurança:** `torch` 1.13.1 é uma versão antiga; os checkpoints de PyLaia e TrOCR são arquivos pickle. Só
  serão carregados depois de conferir o SHA-256 contra [`candidates.json`](./candidates.json).
* **RAM livre:** em 2026-09-30, em uso normal, a máquina tinha cerca de 1.013 MiB livres de 8.072 MiB — abaixo do
  mínimo de 1 GiB que o supervisor exige para iniciar um candidato.
* **Instalação efetiva (T015):** `envs/trocr/.venv` ≈ 631 MiB; `envs/pylaia/.venv` ≈ 1.059 MiB (antes do ajuste do
  `setuptools`). `envs/pylaia` fixa `setuptools<81` porque o `torchmetrics` 0.7 importa `pkg_resources`.
* **Pesos:** `pylaia-rimes` e `pylaia-iam` ≈ 43 MB cada; `trocr-small-handwritten` ≈ 246 MB.
* **Dataset:** `dataset/raw/exp-001/bressay.zip` (1,5 GB) baixado e **não extraído** — licença em aberto.
