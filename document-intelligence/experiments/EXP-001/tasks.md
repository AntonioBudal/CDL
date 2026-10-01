# Tasks: EXP-001 — HTR em Linhas Manuscritas Isoladas (PT-BR)

**Input**: [spec.md](./spec.md), [plan.md](./plan.md)

**Status**: `APPROVED` em 2026-09-30. **Fases 0, 1 e 2 concluídas.** Fase 3 em diante não iniciada; nenhum
peso ou dataset baixado. Aguardando autorização do usuário para a Fase 3.

**Formato**: `[ID] [P?] [Cenário] Descrição` — `[P]` = pode rodar em paralelo; C1/C2/C3 = cenários da spec.

---

## Fase 0 — Portões (bloqueiam tudo)

- [x] T001 Usuário aprova `spec.md` e `plan.md` e responde às perguntas da spec §6 (dados reais, Tesseract, TrOCR, versionamento). *(2026-09-30; commit inicial `33c293f`.)*
- [x] T002 Atualizar `spec.md` com as respostas (remover `NEEDS CLARIFICATION`) e fixar a lista final de candidatos. *(spec §4.1 e §6.)*

## Fase 1 — Licenças e ambiente (sem download de pesos)

- [x] T003 Fechar a verificação de licença de cada candidato da lista final (código, pesos, dados de treino declarados), com URL e data da consulta, em `docs/models-and-licensing.md`; criar `experiments/EXP-001/candidates.json` com revisão fixa por candidato. *(Inclui o dataset BRESSAY.)*
- [x] T004 Criar os projetos `uv` isolados em `experiments/EXP-001/envs/{pylaia,trocr}/` e conferir por resolução a seco as wheels para Windows. Registrar em `experiments/EXP-001/environment.md`. *(Só `uv lock`; nada instalado. Dois ambientes em vez de um — ver plan.md.)*
- [x] T005 [P] Verificar a licença da fonte usada para renderizar as linhas sintéticas e registrá-la em `dataset/fixtures/exp-001/README.md`. *(Caveat, OFL-1.1.)*

**Checkpoint**: lista de candidatos `VERIFIED` e ambiente resolvível. Reportar ao usuário antes de seguir.

## Fase 2 — Cenário 1: harness validado com sintético (P1)

- [x] T006 [C1] Escrever ~200 frases fictícias PT-BR cobrindo o alfabeto exigido em `dataset/fixtures/exp-001/sentences.json`, com teste de cobertura de caracteres.
- [x] T007 [C1] Gerador de linhas sintéticas (frase → imagem) e manifesto com SHA-256 em `experiments/EXP-001/harness/synth.py`.
- [x] T008 [P] [C1] Utilitário de pico de memória de processo filho, com teste, em `src/leitorum_di/` (genérico, sem dependência nova).
- [x] T009 [C1] Interface de adaptador + reconhecedor de referência ("eco") em `experiments/EXP-001/harness/adapters/`.
- [x] T010 [C1] Supervisor com subprocesso, medição e critérios de parada do plano em `experiments/EXP-001/harness/supervisor.py`.
- [x] T011 [C1] Avaliador (CER/WER por linha e agregados, NFC) e relatório JSON em `experiments/EXP-001/harness/evaluate.py`.
- [x] T012 [C1] Testes do harness: referência dá CER = WER = 0; adaptador falso que estoura memória/tempo vira `ABORTED`; candidato não verificado vira `REFUSED`.
- [x] T013 [C1] Rodar `uv run pytest` e `uv run ruff check .`; executar o harness com o reconhecedor de referência e guardar o log em `evaluation/exp-001/`.

**Checkpoint**: harness demonstrado sem nenhum modelo. Reportar ao usuário. *(Atingido em 2026-09-30.)*

Resultado da Fase 2:

- Ambiente `envs/harness/` (Pillow, fontTools, pytest; sem bibliotecas de modelo).
- `dataset/fixtures/exp-001/sentences.json`: 200 frases fictícias; `synthetic-manifest.json`: 200 linhas, 8.107 caracteres, altura 86 px, largura 396–1.041 px. Imagens em `dataset/processed/exp-001/synthetic/` (fora do Git, regeneráveis).
- Testes: 27 do harness (`experiments/EXP-001/tests/`) + 24 da suíte principal; `ruff` limpo.
- Reconhecedor de referência, 3 execuções × 200 linhas: `OK`, CER = WER = 0, mediana 0,42–0,70 ms/linha, pico de 20 MiB. Log: `evaluation/benchmarks/BENCHMARK-20260930-exp-001-echo-reference.json`.
- **Achado**: com o limite padrão de 1 GiB de RAM livre, a execução foi `SKIPPED` — a máquina tinha ~1.013 MiB livres em uso normal (log `…-skipped-low-ram.json`). A execução de referência usou `--min-free-mib 256`, registrado no relatório. Para a Fase 3 será preciso fechar aplicações antes de medir.

## Fase 3 — Cenário 2: candidatos reais (P2)

- [ ] T014 [C2] Baixar o BRESSAY do Zenodo para `dataset/raw/exp-001/` (1,5 GB), conferir o MD5 publicado, e congelar um subconjunto de linhas do split de teste oficial (manifesto com SHA-256 por imagem, amostragem com seed fixa, um autor por página). Se falhar, registrar e seguir só com o sintético.
- [ ] T015 [C2] Instalar os ambientes (`uv sync` em `envs/pylaia` e `envs/trocr`) e, para cada candidato com `benchmark_allowed`, baixar os pesos da revisão fixada para `models/exp-001/`, conferindo o SHA-256 de `candidates.json` antes de qualquer carga. **Primeira etapa com download de pesos.**
- [ ] T016 [P] [C2] Adaptador `pylaia-rimes` (e `pylaia-iam`), sem modelo de linguagem.
- [ ] T017 [P] [C2] Adaptador `trocr-small-handwritten`, decodificação gulosa; relatórios marcam `LICENSE STATUS: NEEDS VALIDATION`.
- [ ] T018 [C2] Executar o benchmark (3 repetições por candidato) na camada sintética e, se existir, na real; logs em `evaluation/exp-001/`.

**Checkpoint**: tabela comparativa bruta disponível.

## Fase 4 — Cenário 3: análise de erros (P3)

- [ ] T019 [C3] Alinhamento por caractere e matriz de confusão por candidato; taxas por classe (acentuadas, `ç`, dígitos, pontuação).
- [ ] T020 [C3] Listar as 20 confusões mais frequentes por candidato.

## Fase 5 — Relatório e decisão

- [ ] T021 Escrever `experiments/EXP-001/RESULTS.md`: tabela, veredito de H1/H2/H0, limitações (camada de dados usada, ausência de *writer split*), manifesto de reprodutibilidade.
- [ ] T022 Redigir o ADR em `docs/adr/` a partir de `template-madr.md` (adotar / adaptar em experimento futuro / descartar).
- [ ] T023 Conferência final: `uv run pytest`, `uv run ruff check .`, nenhum arquivo alterado fora de `document-intelligence/`, pesos e dados reais fora do Git.
- [ ] T024 Submeter ao usuário para aceite. **Não iniciar o EXP-002 antes do aceite.**

---

## Dependências

- T001 → T002 → T003/T004/T005 → Fase 2 → Fase 3 → Fase 4 → Fase 5.
- A Fase 2 não depende de nenhum modelo e pode ser concluída mesmo que nenhum candidato feche licença.
- T014 depende só da resposta à spec §6.1; T015–T018 dependem de T003 e T013.
- Paralelizáveis: T005 com T003/T004; T008 com T006/T007; T016 com T017.
