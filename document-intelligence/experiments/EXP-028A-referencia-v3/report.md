# EXP-028A — Relatório parcial: referência v3 e o que ela muda

* **Data:** 2026-11-20 · **Status:** `PARTIAL` (4 de 20 páginas medidas; ver §4)
* **Spec:** [spec.md](./spec.md) · **Tarefas:** [tasks.md](./tasks.md)
* **Privacidade:** só números e ids neutros; nenhum texto, imagem ou recorte do caderno.

## 1. Resumo

Com 4 páginas de teste transcritas linha a linha pelo autor (referência **v3**, conferida no caderno), a
referência antiga feita pelo Gemini (v2) **difere 8,9 % em caracteres** da do autor, **não tem nenhuma das
quebras de linha** — e, mesmo assim, **o erro do produto quase não muda** com a régua nova: **69,8 %** contra
69,3 % nas mesmas páginas. O diagnóstico do EXP-027 (o leitor erra mais da metade dos caracteres) **se mantém**;
o que a régua antiga não permitia era trabalhar **linha a linha**, que é o que o treino e a decomposição do erro
precisam.

| # | Pergunta | Resultado | Veredito |
| :--- | :--- | :--- | :--- |
| **H1** | A referência do Gemini tinha erro ≥ 2 %? | CER 8,9 % (por página: 4,4 %, 5,2 %, 12,0 %, 13,5 %); WER 8–19 % | **Confirmada** |
| **H2** | O autor diverge de si mesmo ≤ 1 %? | não medida: o autor decidiu não fazer a 2ª passada | **Não medida** |
| **H3** | O CER do produto muda < 5 pontos com a régua nova? | 69,8 % (v3) × 69,3 % (v2), **+0,5 ponto** | **Confirmada** |
| **H4** | O Gemini perdeu ≥ 80 % das quebras de linha? | 0 de 58 quebras preservadas (4 linhas no Gemini × 62 na v3, nas 4 páginas) | **Confirmada** (100 % perdidas) |

## 2. Detalhes

**H1 — erro da referência antiga.** O controle sem ancoragem (p14, transcrita com o rascunho do motor, não do
Gemini) dá 5,2 %, no mesmo intervalo das páginas com rascunho do Gemini (4,4 % a 13,5 %): a ancoragem não parece
ter escondido muita diferença. Parte dos 8,9 % pode vir de linhas que o autor leu diferente do Gemini e parte de
trechos que o Gemini acrescentou ou omitiu; separar as duas exigiria ler o texto, o que este relatório não faz.
A simplificação de LaTeX do EXP-027 não muda o número (as fórmulas destas 4 páginas pesam pouco).

**H3 — o erro do produto com a régua nova.**

| Página | CER do produto (v3) | CER do produto (v2, EXP-027) |
| :--- | ---: | ---: |
| p10 | 65,6 % | 62,2 % |
| p11 | 76,4 % | 76,3 % |
| p14 | 67,2 % | 66,4 % |
| p15 | 62,4 % | 61,7 % |
| **micro** | **69,8 %** | **69,3 %** |

Um erro de ~9 % na régua mexe pouco quando o sistema medido erra ~70 %: as diferenças da referência caem em
trechos que o leitor já errava. Estas 4 páginas são mais difíceis que a média das 20 (56,3 % no EXP-027).

**Decomposição de linhas por texto (sem imagem): não informativa.** Com o leitor errando ~70 %, a
correspondência heurística entre linhas da v3 e linhas lidas falha: 42 das 62 linhas da referência ficaram sem
par (e a parcela "residual" sai negativa, −36 %). Confirma o desenho do roadmap: a decomposição do erro
(EXP-028B) precisa de **caixas sobre imagens de verdade**, não de alinhamento de texto.

**H4 — quebras.** A referência v2 tem 4 linhas nas 4 páginas (texto corrido); a v3 tem 62. Nenhuma quebra da v3
aparece na v2. Uma referência de página não serve para treinar um leitor de linhas nem para medir linhas.

**Tempo de anotação** (caixas + 1ª passada, tempo ativo): p10 6,0 min, p11 11,0, p14 12,1, p15 6,9 — mediana
≈ 9 min com rascunho do Gemini alinhado (a p14, com rascunho do motor, é a mais lenta).

## 3. Exclusões e decisões

* **p16 fora da medida:** a imagem de 512 px dela tem 512 × 250 px, uma faixa da página. A v3 cobre só as
  6 linhas visíveis, enquanto o Gemini e o produto leram a página inteira (o texto do Gemini é 2,4 vezes mais
  longo): incluí-la mediria o recorte da imagem, não a leitura.
* **2ª passada:** o autor decidiu não fazê-la ("consegui escrever tudo na primeira passada"). A H2 (piso de ruído
  humano) fica sem medida; as 2ª passadas feitas em p15 e p16 (não sorteadas) não entram em nada.
* **Medir com o que há:** o autor decidiu medir com as páginas prontas em vez das 20. As 15 restantes (p18 a
  p46) continuam no teste congelado, com o rascunho alinhado pronto na ferramenta.

## 4. Limitações

* **Amostra pequena:** 4 páginas, 62 linhas. Os números indicam direção, não fecham o teste congelado v3. O
  manifesto gravado é `test-manifest-v3-parcial.json`; o oficial (`test-manifest-v3.json`) só existe com as 20.
* **Ancoragem** no Gemini em 3 das 4 páginas (controle: p14).
* **O texto do produto** é o da exportação do Leitorum (leitura das fotos originais em 2026-11-16).

## 5. O que isto muda no plano

1. **O diagnóstico do EXP-027 vale:** o leitor é o problema maior; a régua antiga não o inflou.
2. **A régua de página não serve para o que vem a seguir.** Treino (EXP-033A) e decomposição (EXP-028B) pedem
   texto **por linha**, como a v3. A ferramenta e o rascunho alinhado deixam isso a ~9 min por página.
3. **Sem imagens de verdade, o épico 0 para no texto.** O EXP-028B e o EXP-029 (professores locais) exigem as
   fotos ou as "Folhas originais" do Leitorum; com imagens de 512 px, nenhum dos dois mede o que o produto lê.
