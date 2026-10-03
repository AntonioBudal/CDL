# EXP-002: Ambientes Isolados do Experimento

* **Status:** resolvidos por `uv lock` em 2026-10-02 — **nada instalado, nenhum peso baixado**
* **Hardware e sistema:** os de [`../EXP-000/environment.md`](../EXP-000/environment.md) (CPU-only)
* **`uv`:** 0.11.21

O `pyproject.toml` e o `uv.lock` principais de `document-intelligence/` não foram alterados.

## 1. Ambientes

| Ambiente | Python | Dependência direta | Versões resolvidas (principais) | Pacotes no lock | Situação |
| :--- | :--- | :--- | :--- | ---: | :--- |
| [`envs/harness/`](./envs/harness/pyproject.toml) | 3.14 | `leitorum-di` (local), `pillow`, `numpy`, `opencv-python-headless`, `fonttools`, `pytest` | opencv-python-headless 5.0.0.93, numpy 2.5.3, pillow 12.3.0 | 17 | será instalado na Fase 2 |
| [`envs/docufcn/`](./envs/docufcn/pyproject.toml) | 3.10 | `doc-ufcn==0.1.9` | torch 2.1.0, numpy 1.26.2, opencv-python-headless 4.7.0.72 | 37 | Fase 3 |
| [`envs/heron/`](./envs/heron/pyproject.toml) | 3.14 | `torch`, `transformers`, `pillow` | torch 2.14.1, transformers 5.18.0 | 56 | Fase 3 |
| [`envs/doctr/`](./envs/doctr/pyproject.toml) | 3.14 | `python-doctr==1.1.0` | torch 2.14.1, opencv-python 5.0.0.93 | 61 | exceção do usuário concedida em 2026-10-02; Fase 3 |

Todos resolvem só com wheels para Windows x86-64, exceto `langdetect` (docTR), que é Python puro e só tem sdist.
O Doc-UFCN reaproveita o CPython 3.10 já gerenciado pelo `uv` desde o EXP-001.

## 2. Estimativa de disco

| Item | Estimativa |
| :--- | ---: |
| `envs/harness` | ~0,15 GB |
| `envs/docufcn` (torch 2.1) | ~1,0 GB |
| `envs/heron` (torch 2.14) | ~0,65 GB |
| `envs/doctr`, se autorizado | ~0,75 GB |
| Pesos (Doc-UFCN 3 × 49 MB, Heron 172 MB, docTR ~100 MB) | ~0,4 GB |
| Páginas geradas (220) | ~0,4 GB |
| **Total adicional** | **~2,6–3,4 GB** |

Uso atual de `document-intelligence/`: ~3,5 GB → previsão de ~6–7 GB, abaixo do teto de 20 GB.
