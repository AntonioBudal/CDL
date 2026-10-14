# ADR-007: O reconhecedor do PP-OCRv6 é o melhor leitor pronto medido, mas não lê português o bastante; o ADR-001 se mantém

* **Status:** PROPOSED
* **Data:** 2026-10-14
* **Decisores:** Usuário (decisão); Claude Code (proposta)
* **Experimento de Suporte:** [EXP-009](../../experiments/EXP-009/RESULTS.md)
* **Status de Licença:** PP-OCRv6 small rec e det via `rapidocr` (Apache-2.0) — `LICENSE STATUS: VERIFIED`, conforme declarado. A medida em português depende do BRESSAY (`NEEDS VALIDATION`): serve para orientar experimentos, não para decisão de produto.

## 1. Contexto

O ADR-001 decidiu não adotar reconhecedor de manuscrito pronto sem treino em português: o melhor candidato do
EXP-001 errava 69,4 % dos caracteres. O ADR-006 (proposto) trouxe o pacote do PP-OCR para a detecção de linhas; o
mesmo pacote tem um reconhecedor multilíngue que declara português. O EXP-009 o mediu.

## 2. Opções consideradas

* **A — Adotar o PP-OCRv6 small rec como leitor.** CER de 38,5 % nas linhas do EXP-001: longe do critério de
  adoção (12 %).
* **B — Descartá-lo.** Ignora que ele é, de longe, o melhor medido e que lê manuscrito inglês com 14,8 %.
* **C — Manter o ADR-001 e registrar o PP-OCR como ponto de partida** para a próxima etapa de leitura.

## 3. Decisão

**Opção C.**

1. O ADR-001 continua valendo: nenhum leitor pronto atinge o critério em português manuscrito.
2. O PP-OCRv6 small rec passa a ser a **referência** a ser batida (38,5 % no conjunto do EXP-001), no lugar dos
   69,4 % do TrOCR.
3. A falha é localizada: letras acentuadas com 80 % de erro, contra 12,7 % de erro em letras no inglês. A próxima
   etapa ataca o português, não o traço manuscrito.

## 4. Consequências

* O pipeline detecção → leitura funciona de ponta a ponta, localmente, em 5 s por página, com saída LDF 2.0
  válida — mas o texto lido ainda não serve para o leitor do Leitorum.
* **Próximo passo sugerido:** (a) medir os outros reconhecedores do mesmo ecossistema (PP-OCRv6 medium,
  PP-OCRv5 latino) e o efeito da resolução da linha, que custam só download; (b) se nenhum chegar perto do
  critério, ajustar o reconhecedor com manuscrito em português — o que exige dados com licença adequada para
  produto (o BRESSAY não tem) ou dados próprios.
* Fica registrado que o texto de ponta a ponta melhorou com a página ampliada (36,7 % contra 41,4 %): a escala da
  linha é uma variável a medir, não um detalhe.

## 5. Conformidade

* [x] Local-first; [x] evidência antes de decisão; [x] licenças declaradas; [x] nenhum texto de terceiros em
  relatório.
