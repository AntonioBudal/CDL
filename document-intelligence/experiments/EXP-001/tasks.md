# Tasks: EXP-001 — HTR em Linhas Manuscritas Isoladas (PT-BR)

**Input**: [spec.md](./spec.md), [plan.md](./plan.md)

**Status**: `DRAFT — AWAITING USER REVIEW` — **nenhuma tarefa iniciada**. A execução só começa após a
aprovação da especificação/plano e as respostas às perguntas da spec §6.

**Formato**: `[ID] [P?] [Cenário] Descrição` — `[P]` = pode rodar em paralelo; C1/C2/C3 = cenários da spec.

---

## Fase 0 — Portões (bloqueiam tudo)

- [ ] T001 Usuário aprova `spec.md` e `plan.md` e responde às perguntas da spec §6 (dados reais, Tesseract, TrOCR, versionamento).
- [ ] T002 Atualizar `spec.md` com as respostas (remover `NEEDS CLARIFICATION`) e fixar a lista final de candidatos.

## Fase 1 — Licenças e ambiente (sem download de pesos)

- [ ] T003 Fechar a verificação de licença de cada candidato da lista final (código, pesos, dados de treino declarados), com URL e data da consulta, em `docs/models-and-licensing.md`; criar `experiments/EXP-001/candidates.json` com revisão fixa por candidato.
- [ ] T004 Criar o projeto `uv` isolado em `experiments/EXP-001/pyproject.toml`; conferir por resolução a seco se há wheels Windows para Python 3.14 e, se não houver, fixar 3.13 só ali. Registrar em `experiments/EXP-001/environment.md`.
- [ ] T005 [P] Verificar a licença da fonte usada para renderizar as linhas sintéticas e registrá-la em `dataset/fixtures/exp-001/README.md`.

**Checkpoint**: lista de candidatos `VERIFIED` e ambiente resolvível. Reportar ao usuário antes de seguir.

## Fase 2 — Cenário 1: harness validado com sintético (P1)

- [ ] T006 [C1] Escrever ~200 frases fictícias PT-BR cobrindo o alfabeto exigido em `dataset/fixtures/exp-001/sentences.json`, com teste de cobertura de caracteres.
- [ ] T007 [C1] Gerador de linhas sintéticas (frase → imagem) e manifesto com SHA-256 em `experiments/EXP-001/harness/synth.py`.
- [ ] T008 [P] [C1] Utilitário de pico de memória de processo filho, com teste, em `src/leitorum_di/` (genérico, sem dependência nova).
- [ ] T009 [C1] Interface de adaptador + reconhecedor de referência ("eco") em `experiments/EXP-001/harness/adapters/`.
- [ ] T010 [C1] Supervisor com subprocesso, medição e critérios de parada do plano em `experiments/EXP-001/harness/supervisor.py`.
- [ ] T011 [C1] Avaliador (CER/WER por linha e agregados, NFC) e relatório JSON em `experiments/EXP-001/harness/evaluate.py`.
- [ ] T012 [C1] Testes do harness: referência dá CER = WER = 0; adaptador falso que estoura memória/tempo vira `ABORTED`; candidato não verificado vira `REFUSED`.
- [ ] T013 [C1] Rodar `uv run pytest` e `uv run ruff check .`; executar o harness com o reconhecedor de referência e guardar o log em `evaluation/exp-001/`.

**Checkpoint**: harness demonstrado sem nenhum modelo. Reportar ao usuário.

## Fase 3 — Cenário 2: candidatos reais (P2)

- [ ] T014 [C2] Se a spec §6.1 for (a) ou (b): montar e congelar o conjunto real (manifesto, SHA-256, origem, consentimento) em `dataset/raw/exp-001/`.
- [ ] T015 [C2] Para cada candidato `VERIFIED`: baixar pesos da fonte oficial para `models/exp-001/`, conferir SHA-256 e registrá-lo. **Primeira etapa com download — exige a aprovação de T001.**
- [ ] T016 [P] [C2] Adaptador do candidato A.
- [ ] T017 [P] [C2] Adaptador do candidato B (e demais aprovados), um arquivo por candidato.
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
