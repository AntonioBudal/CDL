# EXP-012 — Pipeline Integrado de Ponta a Ponta: Foto → LDF 2.0 (especificação, plano e tarefas)

**Created**: 2026-10-18 · **Status**: `DELEGATED` (autonomia permanente do usuário, 2026-10-18)

**Input**: ADR-006 (detecção de linhas PP-OCRv6 + fusão), ADR-007 (leitura PP-OCRv6 small; recorte ampliado ajuda;
correção lexical do EXP-011), ADR-004 (LDF 2.0). Corresponde ao objetivo do `EXP-006` do roteiro ("receber a
fotografia e emitir o documento LDF"), com os componentes que sobreviveram às imagens reais.

## Pergunta e hipóteses

Juntando os componentes validados, quanto do texto de uma página real o pipeline entrega, em quanto tempo, e a
saída é sempre um LDF 2.0 válido?

- **H1:** página do BRESSAY ampliada 3×: CER de página ≤ 35,7 % (1 ponto melhor que o ponta a ponta do EXP-009,
  36,7 %), pela correção lexical.
- **H2:** página do BRESSAY na **escala nativa**, com a regra de ampliação de linha (recorte com menos de 32 px de
  altura é ampliado 2×): CER no máximo 3 pontos pior que a versão 3× — ou seja, não é preciso ampliar a página
  inteira.
- **H3:** fotos do GNHK (inglês, celular), sem correção lexical: CER de página ≤ 25 %.
- **H4:** ≤ 6 s por página na mediana e ≤ 2 GiB.
- **H5:** 100 % das páginas saem como LDF 2.0 válido, com texto e confiança nas linhas.

## Método

* **Pipeline** (`harness/pipeline.py`, um adaptador no ambiente `EXP-008/envs/ppocr`): detecção PP-OCRv6 small →
  fusão do EXP-008 → recorte desentortado de cada linha → ampliação 2× se a altura for < 32 px → leitura
  PP-OCRv6 small → ordem de cima para baixo. No ambiente do harness: correção lexical (parâmetros do EXP-011, só
  para português) → LDF 2.0 pelo conversor de referência.
* **Conjuntos:** as 185 páginas de teste do BRESSAY (nativa e 3×) e as 172 fotos de teste do GNHK.
* **Referências:** BRESSAY — transcrição da página; GNHK — palavras anotadas agrupadas por linha (índice de linha),
  em ordem horizontal, sem as marcas especiais. Normalização de página do EXP-009.
* Nenhum parâmetro novo: a regra de 32 px vem do EXP-010 (linhas nativas de ~24 px ganharam com 2×).
* Privacidade e licenças como nos anteriores; nenhum texto em relatório.

## Tarefas

- [ ] **T001** Harness (cópia do EXP-009) e `pipeline.py` com testes da regra de ampliação.
- [ ] **T002** `prepare.py`: manifestos das três variantes e referências de página do GNHK.
- [ ] **T003** Rodar o pipeline nas três variantes.
- [ ] **T004** `run.py`: CER/WER de página antes e depois da correção, custo, LDF 2.0; vereditos.
- [ ] **T005** `RESULTS.md`, ADR-008, registros.
