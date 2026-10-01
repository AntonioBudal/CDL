# Experiment Plan: EXP-001 — HTR em Linhas Manuscritas Isoladas (PT-BR)

**Diretório**: `experiments/EXP-001/` | **Date**: 2026-09-30 | **Spec**: [spec.md](./spec.md)

**Status**: `DRAFT — AWAITING USER REVIEW` (plano apenas; nada foi instalado, baixado ou executado)

## Summary

Construir um harness de benchmark de reconhecimento de linha, validá-lo com linhas sintéticas e um
reconhecedor de referência, e então executar em CPU cada candidato de licença verificada, um por subprocesso,
sob teto de 2 GB e limites de latência. Saída: tabela comparativa, análise de erros PT-BR, registro de
licenças e um ADR.

## Technical Context

**Language/Version**: Python 3.14.3 no projeto principal. Ambiente do experimento: 3.14 se houver wheels
Windows para as dependências dos candidatos; senão, fixar 3.13 **somente** em `experiments/EXP-001/` (a verificar em T004).

**Primary Dependencies**: projeto principal inalterado (`pydantic`). Ambiente isolado do experimento: Pillow
(leitura/geração de imagem) + uma dependência por candidato aprovado (wrapper do Tesseract, PyLaia/Torch CPU,
etc.). Nenhuma delas entra no `pyproject.toml` da raiz de `document-intelligence/`.

**Storage**: arquivos locais. Pesos em `models/exp-001/` (ignorado pelo Git). Imagens reais, se houver, em
`dataset/raw/exp-001/` (ignorado). Logs em `evaluation/exp-001/`.

**Testing**: `pytest` no projeto principal para o código genérico; testes do harness rodam sem nenhum modelo instalado.

**Target Platform**: Windows 11, i5-8265U (4c/8t), 7,9 GB RAM, **CPU-only**.

**Performance Goals (hipóteses a medir)**: ≤ 150 ms/linha (mediana); CER ≤ 12 %; WER ≤ 25 %.

**Constraints**: pico de memória ≤ 2,0 GB por candidato; inferência offline; nenhum dado sai da máquina.

**Scale/Scope**: 3 a 5 candidatos considerados, 2+ executados; ~200 linhas sintéticas + conjunto real conforme `spec.md` §6.

## Constitution Check

| Princípio | Situação no plano |
| :--- | :--- |
| 1 — Local-first | PASS: inferência offline; rede só para instalar pacotes e baixar pesos verificados. Modelos de plataforma (Transkribus) excluídos. |
| 2 — Evidência antes de decisão | PASS: nenhum candidato é adotado; o experimento só mede. |
| 3 — Reprodutibilidade | **CONDICIONAL**: manifesto exige hash Git, e `document-intelligence/` ainda não está versionado (spec §6, pergunta 4). |
| 4 — Reconhecimento × interpretação | PASS: saída bruta preservada; sem correção por dicionário/LM externo. |
| 5 — Human-in-the-loop | N/A neste experimento (sem fluxo de correção). |
| 6 — Medir antes de otimizar | PASS: sem quantização, ONNX customizado ou código nativo próprio. |
| 7 — Experimentos antes de features | PASS: código de candidatos fica em `experiments/EXP-001/`; ADR ao final. |
| 8 — LDF como contrato soberano | PASS: nenhuma troca de dados com o Leitorum. |
| Governança de escopo (fronteira) | PASS, com uma exceção a autorizar: binário do Tesseract instalado no sistema (spec §6, pergunta 2). |
| Privacidade (AGENTS da raiz §1) | PASS: só dados sintéticos ou amostras fornecidas com consentimento explícito. |

## Arquitetura do Benchmark

```text
manifesto de linhas (JSON)          candidato (subprocesso, CPU)
  id, imagem, sha256, referência ──►  carrega modelo ─► lê N linhas ─► escreve predições (JSONL)
                                             ▲                              │
              supervisor (processo pai) ─────┘                              ▼
              mede pico de memória e tempo,                 avaliador: CER/WER (leitorum_di.metrics),
              aplica critérios de parada                    confusões por caractere, relatório JSON
```

1. **Supervisor** (processo pai, sem dependências pesadas): lança um subprocesso por candidato, lê
   periodicamente o pico de memória do filho (PeakWorkingSetSize, mesma API já validada no EXP-000) e o
   encerra se violar um critério de parada.
2. **Adaptador de candidato**: interface mínima — `load()`, `recognize(caminho_da_imagem) -> texto`,
   `describe() -> {id, revisão, sha256 dos pesos}`. Um arquivo por candidato. O **reconhecedor de referência**
   ("eco") devolve a transcrição de referência e serve para validar o harness.
3. **Avaliador**: roda no pai, só com `leitorum_di.metrics`; nunca importa bibliotecas de modelo.
4. **Portão de licença**: antes de qualquer download, o supervisor confere em `candidates.json` que código e
   pesos estão `VERIFIED` e que o SHA-256 baixado confere; senão registra `REFUSED`.

Separar pai e filho mantém a medição de memória honesta (o pico do modelo não se mistura com o do avaliador) e
permite que cada candidato tenha suas próprias dependências.

## Protocolo de Medição

- **Aquecimento**: 3 linhas descartadas após a carga do modelo.
- **Latência**: `perf_counter_ns` por linha, lote de tamanho 1; reportar mediana, p95 e tempo de carga separadamente.
- **Memória**: pico de working set do subprocesso, do início ao fim.
- **Threads**: valor padrão da biblioteca e, se o tempo permitir, uma segunda rodada limitada a 4 threads; registrar ambos.
- **Repetições**: 3 execuções por candidato; reportar mediana das medianas e a dispersão.
- **Determinismo**: `freeze_seeds(1234)`; decodificação gulosa (*greedy*), sem amostragem.
- **Texto**: NFC em referência e predição; nenhuma outra normalização antes do CER.

## Critérios de Parada

| Situação | Ação |
| :--- | :--- |
| Pico de memória > 2,0 GB | encerrar o subprocesso; status `ABORTED: memory` |
| Carga do modelo > 120 s | `ABORTED: load timeout` |
| Mediana das 20 primeiras linhas > 1 500 ms (10× a meta) | `ABORTED: latency`; métricas parciais registradas como tal |
| Tempo total do candidato > 20 min | `ABORTED: wall time` |
| Licença não `VERIFIED` ou SHA-256 divergente | `REFUSED`, antes de baixar ou carregar |
| RAM livre do sistema < 1 GB antes de iniciar | não iniciar; pedir ao usuário para fechar aplicações |
| Qualquer leitura fora de `document-intelligence/` exigida por um candidato | parar e consultar o usuário |

Um `ABORTED` conta como resultado e entra no relatório.

## Dados

- **Camada sintética (sempre)**: ~200 frases fictícias em PT-BR cobrindo o alfabeto de `EXP-001-context.md` §3,
  renderizadas em imagem. Serve para validar o harness e medir custo; **não** vale como métrica de HTR real
  (`docs/dataset-and-evaluation.md` §3). A fonte de renderização precisa de licença verificada (ex.: OFL) ou
  usa-se uma fonte já presente no sistema apenas localmente, sem redistribuir.
- **Camada real (depende da decisão do usuário, spec §6.1)**: conjunto congelado, com SHA-256 por imagem,
  origem, consentimento e metadados de aquisição. Nunca usado para ajuste de parâmetros.

## Project Structure

```text
experiments/EXP-001/
├── spec.md  plan.md  tasks.md      # ciclo Spec Kit (este conjunto)
├── pyproject.toml  uv.lock         # ambiente uv isolado do experimento (criado em T004)
├── candidates.json                 # candidatos, revisões, licenças, sha256
├── harness/                        # supervisor, adaptadores, avaliador
├── environment.md                  # versões efetivamente usadas
└── RESULTS.md                      # relatório final

dataset/fixtures/exp-001/           # manifesto e frases sintéticas (versionável)
dataset/raw/exp-001/                # imagens reais, se houver (ignorado pelo Git)
models/exp-001/                     # pesos baixados (ignorado pelo Git)
evaluation/exp-001/                 # logs JSON das execuções
docs/models-and-licensing.md        # tabela de rastreabilidade
docs/adr/                           # ADR de saída
```

**Structure Decision**: o código do experimento fica todo em `experiments/EXP-001/`. `src/leitorum_di/` só
recebe mudanças se for um utilitário genérico de medição (ex.: leitura de pico de memória de processo filho),
coberto por teste e sem dependência nova.

## Riscos

| Risco | Mitigação |
| :--- | :--- |
| Nenhum segundo candidato fecha licença | Registrar e reportar com um candidato; decisão do usuário sobre aceitar C para uso experimental. |
| Sem wheels para Python 3.14 | Fixar 3.13 só no ambiente do experimento; registrar em `environment.md`. |
| Só dados sintéticos disponíveis | H1 fica declarada como **não respondida**; só H2 é avaliada. |
| 7,9 GB de RAM com outras aplicações abertas | Checagem de RAM livre antes de cada candidato. |
| Modelos em inglês/francês sem diacríticos no vocabulário | É o resultado esperado (H0); a análise de erros o quantifica. |

## Complexity Tracking

| Desvio | Por que é necessário | Alternativa mais simples rejeitada porque |
| :--- | :--- | :--- |
| Segundo projeto `uv` em `experiments/EXP-001/` | Impede que Torch e afins entrem no `pyproject.toml` principal (CLAUDE.md §4.2). | Grupo de dependências no projeto principal contaminaria o `uv.lock` da fundação. |
| Subprocesso por candidato | Medição de memória isolada e encerramento seguro. | Medir no mesmo processo mistura picos e não permite abortar. |
