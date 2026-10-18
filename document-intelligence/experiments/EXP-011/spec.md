# EXP-011 — Correção Lexical da Leitura em Português (especificação, plano e tarefas)

**Created**: 2026-10-18 · **Status**: `DELEGATED` — especificado, planejado e executado por delegação permanente do
usuário (2026-10-18: "sempre aceitarei o seu plano e suas permissões").

**Input**: ADR-007 (`ACCEPTED`): melhor leitura pronta em português é o PP-OCRv6 small com recorte ampliado 2×
(CER 34,4 %, WER 74,1 % nas 398 linhas do EXP-001); letras acentuadas com ~80 % de erro, enquanto o mesmo modelo lê
inglês com 14,8 %. Hipótese de trabalho: parte do erro é de vocabulário (palavras quase certas, acentos perdidos),
recuperável sem treinar modelo.

## Pergunta e hipóteses

Um pós-processamento barato, que troca cada palavra lida que não existe em português pela palavra portuguesa mais
provável e próxima, reduz o erro de leitura?

- **H1:** WER cai pelo menos 10 pontos nas 398 linhas do EXP-001 (de 74,1 % para ≤ 64,1 %).
- **H2:** CER cai pelo menos 3 pontos (≤ 31,4 %).
- **H3:** o erro em letras acentuadas cai pelo menos 15 pontos.
- **H4:** a correção custa ≤ 20 ms por linha, sem modelo.
- **H5 (controle):** a correção não piora as linhas que já estavam certas (palavras corretas trocadas ≤ 2 % das
  palavras corretas antes da correção).

## Método

* **Léxico:** frequências de palavras do português do pacote `wordfreq` (código Apache-2.0; dados CC-BY-SA 4.0,
  agregados de fontes públicas) — `LICENSE STATUS: VERIFIED` conforme declarado; usado só como dado de experimento,
  exportado uma vez para `dataset/processed/exp-011/` (fora do Git). Nenhum texto do BRESSAY entra no léxico.
* **Correção por palavra** (pontuação de borda e caixa preservadas):
  1. palavra no léxico → mantém;
  2. senão, mesma palavra sem acentos coincide com palavra do léxico → troca pela forma acentuada mais frequente;
  3. senão, candidatos a distância de edição ≤ *d* (índice de deleções, estilo SymSpell) → troca pelo mais
     frequente de menor distância; sem candidato → mantém.
* **Parâmetros:** tamanho do léxico (20 mil, 50 mil, 100 mil palavras) × distância máxima (0 = só acentos, 1, 2) ×
  comprimento mínimo da palavra para corrigir (1, 3). Escolhidos **só na validação**: as linhas da divisão oficial
  de **validação** do BRESSAY, lidas pelo mesmo leitor (PP-OCRv6 small, 2×).
* **Teste:** as 398 linhas do EXP-001 e todas as 5.496 linhas das 185 páginas de teste, lidas a 2×; uma vez.
* **Métricas:** as do EXP-009 (CER/WER micro, NFC; CER por classe); palavras corretas que viraram erradas (H5).
* Privacidade: transcrições só para métricas; nenhum texto em relatório, Git ou chat.

## Tarefas

- [ ] **T001** Ambiente `envs/lex` com `wordfreq`; exportar o léxico português com frequências.
- [ ] **T002** `lexicon.py` (correção) com testes em palavras fictícias.
- [ ] **T003** Recortes e leitura (small 2×) das linhas de validação do BRESSAY e de todas as linhas de teste.
- [ ] **T004** `calibrate.py` na validação; `run.py` no teste; relatório.
- [ ] **T005** `RESULTS.md`, ADR (ou evidência no ADR-007), registros, verificação.
