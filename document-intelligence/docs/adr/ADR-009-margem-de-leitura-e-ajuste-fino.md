# ADR-009: Leitura direta com margem à direita; ajuste fino com dados licenciados como caminho para o português

* **Status:** ACCEPTED (aceito por delegação permanente do usuário em 2026-10-22)
* **Data:** 2026-10-22
* **Decisores:** Usuário (delegação); Claude Code (proposta e execução)
* **Experimento de Suporte:** [EXP-014](../../experiments/EXP-014/RESULTS.md)
* **Status de Licença:** modelo de partida PP-OCRv6 small rec (Apache-2.0) e ferramentas (`VERIFIED`, conforme declarado). O modelo ajustado no EXP-014 usou o BRESSAY (`NEEDS VALIDATION`): **experimental, proibido no produto**.

## 1. Contexto

O ADR-007 manteve o ADR-001: nenhum leitor pronto lia português manuscrito o bastante (34–38 % de CER). O EXP-014
investigou o ajuste fino e, no caminho, descobriu que o pacote `rapidocr` piorava a leitura do próprio modelo.

## 2. Decisão

1. **Leitura direta pelo ONNX Runtime, com 640 px de margem vazia à direita da linha**, no lugar do reconhecedor
   do `rapidocr`. Mesmo modelo, sem treino: CER de linha em português 41,9 % → 29,7 %. Passa a fazer parte do
   pipeline de referência do ADR-008 (a detecção continua pelo `rapidocr`).
2. **Os números de leitura dos EXP-009 a EXP-013 ficam como medidas do pacote**, não do modelo. Não são
   recalculados; este ADR registra a correção.
3. **O caminho para ler português é o ajuste fino.** Menos de uma época em CPU levou o CER de 29,7 % para 13,6 %
   (12,4 % com correção lexical) e os acentos de 77 % para 21,5 % de erro.
4. **O modelo ajustado no BRESSAY não vai para o produto.** Para o produto, o mesmo procedimento deve ser repetido
   com manuscrito em português com licença adequada (por exemplo, páginas escritas para esse fim, com
   consentimento). Esta é a principal dependência externa do projeto agora.
5. O ADR-001 é superado no que diz respeito a "não há caminho": o caminho existe e foi medido; continua valendo que
   nenhum modelo **pronto** serve.

## 3. Evidência

| Leitura | Todas as linhas de teste: CER / WER | Com correção lexical |
| :--- | :--- | :--- |
| `rapidocr` (EXP-009 a 013) | 41,9 % / 77,5 % | 41,5 % / 71,6 % |
| ONNX Runtime + margem 640 px | 29,7 % / 72,0 % | 28,9 % / 64,1 % |
| Ajustado (BRESSAY) + margem | 13,6 % / 44,1 % | 12,4 % / 34,1 % |

## 4. Consequências

* Próximo passo técnico sem dependência externa: aplicar a leitura direta com margem ao pipeline do ADR-008 e medir
  de ponta a ponta.
* Próximo passo com dependência externa: obter manuscrito em português com licença para produto e repetir o ajuste.
* A inferência do modelo ajustado precisa voltar para ONNX (hoje 280 ms por linha no PyTorch).
