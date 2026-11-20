# EXP-028A — Referência v3 linha a linha e piso de ruído humano

* **Criado em:** 2026-11-20
* **Status:** `PARTIAL` (aprovado em 2026-11-20; medido em 4 de 20 páginas, sem 2ª passada, por decisão do
  usuário — ver [report](./report.md))
* **Roadmap:** épico 0.13-0 "Régua limpa", item **EXP-028A** (absorve o micro-experimento **A5**) do
  [roadmap 0.13](../../docs/replanejamento-0.13/05-roadmaps.md)
* **Depende de:** F-DI-13.01 (ferramenta de caixas e linhas, [spec 002](../../specs/002-ferramenta-caixas-linhas/spec.md))
* **Libera:** F-DI-13.02 (harness gatekeeper) e EXP-028B (decomposição do erro)

---

## 1. Por que, e o que mudou desde o roadmap

O CER de 56 % do EXP-027 foi medido contra uma referência feita por um modelo externo (Gemini), em nível de
página. O roadmap pediu uma régua melhor antes de qualquer outra medida: caixas reais e texto conferido duas
vezes, linha a linha, nas 20 páginas de teste e em 10 páginas de validação (`dev-val`).

**Três fatos novos mudam o desenho** (levantados em 2026-11-20, só números):

1. **Não há fotos originais.** As 20 fotos de teste chegaram como PNG de até 512 px; o usuário decidiu usá-las
   assim. Nesse tamanho, as caixas não medem o que o produto lê (ele leu as fotos originais), então **nenhuma
   medida de detecção sai deste experimento**. As caixas servem para estruturar o texto em linhas.
2. **A referência do Gemini não tem as quebras de linha.** As 20 páginas somam **50 linhas de texto** na
   referência (de 1 a 9 por página), enquanto o motor encontrou **389 linhas** nas mesmas imagens. A referência é
   um texto em parágrafos. Isso confirma, antes de qualquer medida, metade da hipótese do roadmap ("perda de
   quebras") e impede usar a referência como rascunho por linha do jeito que a ferramenta faz hoje.
3. **As 31 páginas de desenvolvimento não têm imagem no projeto.** O `dev-val` não pode ser anotado agora; pode
   ser **sorteado e congelado** agora, para nunca entrar em treino.

**A boa notícia:** o texto escrito no papel não depende do tamanho da imagem. O autor tem o caderno; a
referência v3 pode ser conferida no próprio papel, e o texto que o produto leu das fotos originais está guardado
(exportação do Leitorum, `processed/exp-027/motor/`). Assim dá para **refazer a medida de página do produto com
uma régua confiável**, mesmo sem as fotos.

## 2. Perguntas e hipóteses

| # | Pergunta | Hipótese | Como se mede |
| :--- | :--- | :--- | :--- |
| **H1** | A referência do Gemini estava errada a ponto de distorcer o CER? | CER(Gemini → v3) **≥ 2 %** | distância de caracteres entre o texto do Gemini e a v3, por página e no total |
| **H2** | Quanto o próprio autor diverge de si mesmo? (micro **A5**) | CER entre a 1ª passada e uma 2ª passada **cega** **≤ 1 %** | 2ª passada cega em 5 páginas sorteadas (~100 linhas) |
| **H3** | O diagnóstico do EXP-027 se mantém com a régua nova? | o CER de página do produto muda **menos de 5 pontos** (56 % → 51–61 %) | mesmo `score.py` do EXP-027, trocando só a referência |
| **H4** | Quantas quebras de linha o Gemini perdeu? | ≥ 80 % das linhas da v3 não começam numa quebra da referência do Gemini | contagem de linhas e alinhamento de quebras |

Nenhuma hipótese depende do tamanho da imagem: todas comparam textos.

## 3. O que o autor faz (e quanto custa)

* **Etapa 1 da ferramenta (caixas), em modo rápido:** só apagar caixas falsas e criar as que faltam; **não
  precisa ajustar cantos** (na p14 isso foi 43 % do tempo e, em 512 px, não serve para medir detecção).
* **1ª passada, com o caderno ao lado:** o rascunho de cada linha vem do texto do Gemini já distribuído pelas
  caixas (§4); a correção é feita olhando o papel, que vale mais que a imagem pequena.
* **2ª passada cega** em 5 das 20 páginas (sorteio fixo, estratificado), sem ver a 1ª nem o rascunho, uns dias
  depois da 1ª, para medir H2.
* **Estimativa:** 19 páginas × ~6 min + 5 × ~7 min ≈ **2,5 h**, em sessões curtas. A p14 já está pronta (com
  rascunho do motor, o que a torna a única página sem viés de ancoragem no Gemini — ver §6).

## 4. O que o experimento constrói

1. **Rascunho por alinhamento:** distribuir o texto do Gemini pelas caixas alinhando as palavras dele com as
   palavras que o motor leu em cada caixa (o alinhamento de palavras do EXP-027). Cada caixa recebe as palavras
   do Gemini que caíram nela; o que não alinhar vai para as sobras. Só preenche páginas sem 1ª passada; nunca
   imprime texto.
2. **Sorteio da 2ª passada** (5 de 20) e do **`dev-val`** (10 de 31), estratificados por escrita e fórmulas,
   com semente fixa, gravados antes de qualquer medida.
3. **Exportação da v3:** `referencia-v3/pNN.txt` (fora do Git), uma linha do papel por linha, na ordem de
   leitura, a partir dos arquivos `di-annotation/1`.
4. **Manifestos versionados (só hashes e contagens):** `splits/test-manifest-v3.json` (as 20 páginas, hash da
   imagem marcada `low_resolution`, hash da referência v3, linhas por página) e `splits/dev-val-manifest.json`
   (as 10 páginas, com `annotation: pendente` até haver imagens).
5. **Relatório** `report.md` com H1–H4, só números e categorias.

## 5. Critérios

* **Aceite:** 20 páginas com 1ª passada completa e válida no schema; 5 com 2ª passada cega; H1–H4 respondidas;
  manifestos gravados; o `score.py` do EXP-027 roda contra a v3 sem mudança de código além do caminho.
* **Abandono / plano B:** se a 1ª passada passar de **15 min por página** nas 5 primeiras, parar e rever o
  rascunho por alinhamento (ele é o que mais pesa no tempo) antes de continuar.

## 6. Limitações declaradas

* **Ancoragem:** com o Gemini como rascunho, o autor tende a aceitar o que já está escrito; isso **subestima**
  H1. A p14 (rascunho do motor) e a 2ª passada cega (sem rascunho) são os controles.
* **Imagem de 512 px:** caixas aproximadas; nada sobre detecção. O EXP-028B (decomposição com caixas perfeitas)
  continua exigindo imagens de verdade — ver §8.
* **O texto do produto é o da exportação** (o que o motor leu das originais em 2026-11-16), não uma leitura nova.

## 7. Regras

Teste congelado: as 20 páginas e a v3 servem só para medir; nunca treino, limiar, dicionário ou ajuste de
rascunho. O `dev-val` é sorteado agora e fica fora de qualquer treino. Nenhum texto, imagem ou recorte vai para
o Git, para o relatório ou para o chat. Tudo local.

## 8. O que depende do usuário

1. **Conferir se o Leitorum guardou as "Folhas originais"** dos estudos do livro de teste (a imagem que o motor
   realmente leu). Se sim, elas substituem as de 512 px e destravam o EXP-028B; se não, seguimos só com o texto.
2. **De onde vieram as imagens de 512 px**, e se existem também para as 31 páginas de desenvolvimento (para
   anotar o `dev-val` mais tarde).
3. **~2,5 h de anotação** com o caderno à mão, e a 2ª passada cega das 5 páginas uns dias depois.
