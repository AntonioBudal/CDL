# ADR-008: Pipeline de referência foto → LDF 2.0, com o texto em português tratado como rascunho

* **Status:** ACCEPTED (aceito por delegação permanente do usuário em 2026-10-18)
* **Data:** 2026-10-18
* **Decisores:** Usuário (delegação); Claude Code (proposta e execução)
* **Experimento de Suporte:** [EXP-012](../../experiments/EXP-012/RESULTS.md)
* **Status de Licença:** `rapidocr` e PP-OCRv6 (Apache-2.0), léxico `wordfreq` (dados CC-BY-SA 4.0) — `LICENSE STATUS: VERIFIED`, conforme declarado. Evidência em português depende do BRESSAY (`NEEDS VALIDATION`).

## 1. Contexto

Os ADR-006 e ADR-007 escolheram, separadamente, a detecção de linhas e a leitura. O EXP-012 as juntou com a
correção lexical (EXP-011) e o conversor LDF 2.0 (ADR-004) e mediu a cadeia de ponta a ponta.

## 2. Decisão

1. **Pipeline de referência** para experimentos e para uma futura prévia no site: detecção PP-OCRv6 small → fusão
   de fragmentos (EXP-008) → recorte desentortado → leitura PP-OCRv6 small (ampliando 2× linhas com menos de
   32 px) → correção lexical (só português) → ordem de cima para baixo → LDF 2.0.
2. **Resolução mínima de entrada:** a página deve chegar com linhas de texto de pelo menos ~50 px de altura;
   abaixo disso, ampliar a página inteira antes da detecção (no BRESSAY, 3× deu 36,2 % de CER contra 45,8 % sem
   ampliar).
3. **Texto em português é rascunho:** qualquer uso no produto mostra o texto lido para revisão do leitor, com as
   correções gravadas como `human_corrections` no LDF. Nada sobre leitura em português é apresentado como texto
   final enquanto o CER não chegar perto do critério de adoção (12 %).
4. Continua experimental: nada entra em `src/` sem validação em foto de caderno e spec de produto.

## 3. Evidência

| Variante | CER de página | WER | s por página | LDF 2.0 válido |
| :--- | ---: | ---: | ---: | ---: |
| GNHK, fotos de celular (inglês) | 27,5 % (mediana 17,6 %) | 54,0 % | 2,7 | 172 / 172 |
| BRESSAY 3× (português) | 36,2 % (mediana 28,7 %) | 67,9 % | 5,2 | 185 / 185 |
| BRESSAY nativo (português) | 45,8 % (mediana 34,9 %) | 73,8 % | 2,8 | 185 / 185 |

## 4. Consequências

* Existe um caminho local completo foto → LDF 2.0 em menos de 6 s por página, em CPU.
* **Próximos passos com mais retorno:** (a) uma regra de escala automática (estimar a altura das linhas e ampliar
  a página até a faixa boa), barata e medível já; (b) adaptar o reconhecedor à caligrafia brasileira, que é o
  limite real e depende de dados com licença para produto; (c) validar com fotos de caderno de verdade.
