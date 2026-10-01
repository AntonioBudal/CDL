# EXP-000: Registro de Ambiente de Execução e Hardware

* **Status:** `COMPLETE` — inventário coletado por `collect_environment.ps1` na máquina do usuário
* **Data da Aferição:** 2026-09-30
* **Auditor:** Claude Code

> **Origem dos dados.** Saída de `collect_environment.ps1` executado pelo usuário em PowerShell 5.1
> (2026-09-30), complementada por `.venv/pyvenv.cfg`.

---

## 1. Especificações de Hardware

* **Processador (CPU):** Intel Core i5-8265U @ 1.60 GHz — 4 núcleos / 8 threads
* **Memória RAM:** 7,9 GB
* **Placa de Vídeo Dedicada (GPU):** NVIDIA GeForce MX110 (driver Windows 32.0.15.8129; `nvidia-smi` driver 581.29) + Intel UHD Graphics 620 integrada
* **VRAM da GPU:** 2 GB (2048 MiB)
* **Armazenamento:** SSD NVMe WD_BLACK SN770 500 GB + HDD WDC WD10SPZX 1 TB; livre na unidade do projeto: 139,8 GB
* **Decisão GPU/CPU (baseline):** **CPU-only como baseline.** A MX110 (2 GB) é limitada para HTR/treino;
  uso de CUDA só será avaliado em experimento próprio. RAM de 7,9 GB também limita modelos grandes.

---

## 2. Sistema Operacional e Plataforma

* **Sistema Operacional:** Windows 11 Pro 64-bit, versão 10.0.26300 (build 26300)
* **Nome do dispositivo:** `desktop-so18mo2`
* **Ambiente de Execução:** PowerShell 5.1.26100.9444
* **Codificação de Caracteres:** `sys.getdefaultencoding()` = utf-8; **`locale.getpreferredencoding()` = cp1252**.
  Atenção: toda leitura/escrita de texto no projeto deve passar `encoding="utf-8"` explicitamente
  (os testes atuais já o fazem). A saída do PowerShell 5.1 exibe acentos corrompidos (mojibake) no console.
* **Quebras de Linha do Git:** `core.autocrlf = true` (CRLF no checkout, LF no repositório)

---

## 3. Toolchain e Runtimes de Software

* **Versão do `uv`:** 0.11.21 (5aa65dd7a 2026-06-11, x86_64-pc-windows-msvc)
* **Versão do Python:** 3.14.3, CPython, base `C:\Python314`; **Git:** 2.54.0.windows.1.
  Atende `requires-python >=3.11`.
* **Caminho do Ambiente Virtual:** `.venv/` (gerenciado exclusivamente por `uv`; ignorado pelo Git)
* **Versão do PyTorch (se instalado):** não instalado (confirmado: `torch instalado: False`)
* **Suporte a CUDA detectado:** driver NVIDIA presente (`nvidia-smi` OK); CUDA toolkit/torch não testados (irrelevante na fundação)
* **Dependências resolvidas (`uv sync`):** 16 pacotes resolvidos, 15 conferidos, sem alertas de conflito;
  pytest 9.1.1, pluggy 1.6.0, pytest-cov 7.1.0.
* **Seeds:** as métricas atuais são determinísticas (sem aleatoriedade). O congelamento de seeds está
  implementado em `leitorum_di.reproducibility.freeze_seeds` (seed 1234 aplicada a `random`;
  `PYTHONHASHSEED` não efetivo em processo já iniciado — reportado como `pythonhashseed_effective: false`).

---

## 4. Auditoria de Permissões e Filesystem

* [x] Leitura e escrita no diretório `document-intelligence/`: OK (arquivos de EXP-000 gravados)
* [x] Bloqueio estrito de escrita em `frontend/` e `backend/`: respeitado nesta sessão — apenas
  `document-intelligence/` foi alterado (bloqueio técnico por hook/sandbox **não** testado)
* [x] `.gitignore` ativo impedindo versionamento de `.venv/`, `.pytest_cache/`, `.ruff_cache/`: VERIFICADO (linhas 2, 30, 35)
* [x] Nenhum caminho de produção do Leitorum (`backend/data/caderno.db`) acessado: VERIFICADO
  (`tests/test_boundary.py` passa; nenhum acesso nesta sessão)

---

## 5. Pendências

Reverificação em 2026-09-30 (Claude Code, direto no Windows do usuário):

* ~~Mecanismo de seeds e log de benchmark~~ — implementados e executados no Windows (ver RESULTS.md §4, item 7).
* ~~`uv sync` explícito~~ — executado, exit 0, sem alertas.
* ~~Classifier do Python 3.14~~ — adicionado ao `pyproject.toml`.
* Em aberto: bloqueio técnico de escrita fora de `document-intelligence/` por hook/sandbox continua não testado.
