# EXP-000 — Environment, Reproducibility and Evaluation Foundation

* **Status:** `ACCEPTED` / `CONCLUÍDO` (iniciado e aceito pelo usuário em 2026-09-30 — ver RESULTS.md)
* **Responsável:** Claude Code
* **Data de Criação do Contexto:** 2026-09-30
* **Domínio:** Infraestrutura, Tooling, Avaliação e Reprodutibilidade

---

## 1. Visão Geral e Propósito

O **EXP-000** é o experimento fundacional de todo o subsistema **Document Intelligence**. Ele antecede qualquer trabalho de modelagem ou reconhecimento de texto manuscrito (HTR/OCR).

Nenhum modelo de IA (incluindo o EXP-001) pode ser avaliado ou integrado antes que o ambiente de execução, o pipeline de medição e os testes de infraestrutura estejam 100% funcionais, auditados e homologados neste experimento.

---

## 2. Objetivos Específicos

1. **Validação do Ambiente Python:**
   - Garantir instalação limpa e reproduzível das dependências via `uv sync`.
   - Confirmar versão do Python `>=3.11` em ambiente Windows.
   - Auditar suporte a hardware (CPU threads, detecção de GPU/CUDA ou decisão explícita por CPU baseline).
2. **Framework e Pipeline de Avaliação:**
   - Validar a infraestrutura de cálculo das métricas fundacionais (**CER** - Character Error Rate e **WER** - Word Error Rate) a partir de fixtures sintéticas.
   - Validar cálculo de IoU para caixas delimitadoras e segmentação espacial a partir de dados sintéticos.
3. **Mecanismo de Rastreabilidade e Reprodutibilidade:**
   - Estabelecer a rotina de congelamento de sementes aleatórias (random seeds).
   - Definir formato de log de benchmark e auditoria de consumo de memória/tempo.
4. **Isolamento e Segurança de Fronteira:**
   - Garantir que a suíte de testes de `document-intelligence/` execute sem interagir com `frontend/` ou `backend/`.
   - Garantir isolamento absoluto de dados de produção do Leitorum.

---

## 3. Fora de Escopo do EXP-000

* **NÃO** treinar ou baixar modelos de HTR ou OCR.
* **NÃO** realizar inferência sobre páginas reais de cadernos de anotações.
* **NÃO** implementar algoritmos de visão computacional avançados.
* **NÃO** introduzir dependências pesadas de IA antes de comprovar necessidade em experimentos posteriores.

---

## 4. Critérios de Aceite (Definition of Done)

Para que o Claude Code conclua e homologue o EXP-000, todos os seguintes critérios devem ser satisfeitos:

- [x] `uv sync` executa sem alertas de conflito em ambiente local.
- [x] Arquivo `environment.md` preenchido com especificações reais da máquina (SO, CPU, RAM, GPU/driver, versão do Python, versão do uv).
- [x] Implementação de utilitários de métricas em `src/leitorum_di/metrics/` (CER, WER, IoU) coberta por testes unitários com 100% de passagem em dados sintéticos.
- [x] Execução de `uv run pytest` executando em menos de 5 segundos para a suíte de fundação.
- [x] Execução de linter e formatação (`uv run ruff check .`) com zero violações.
- [x] Arquivo `RESULTS.md` preenchido com os resultados da auditoria de fundação e assinado pelo Claude Code.

---

## 5. Instruções para o Claude Code

1. Quando autorizado pelo usuário a iniciar o EXP-000, altere o status deste documento para `IN PROGRESS`.
2. Não avance para o EXP-001 antes de preencher `environment.md` e `RESULTS.md`.
3. Siga estritamente os princípios da Constituição do Document Intelligence.
