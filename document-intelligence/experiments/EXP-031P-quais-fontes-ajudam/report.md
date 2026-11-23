# EXP-031P — Relatório: quais fontes abertas ajudam o leitor

* **Data:** 2026-11-22 a 2026-11-23 · **Status:** `DONE`
* **Spec:** [spec.md](./spec.md) · **Plano:** [plan.md](./plan.md) · **Números:** [resultados.json](./resultados.json)
  (só medidas, sem texto)
* **Dados e modelos:** `D:\Leitorum-DI\` (catálogo, listas, modelos de experimento), fora do Git. Nenhum modelo
  deste experimento vai ao produto.

## 1. Resumo

1. **Nenhuma fonte aberta melhora a leitura de letra moderna em português.** O melhor resultado no BRESSAY teste
   foi 28,9 % contra 29,9 % sem treino, e a repetição com outra semente deu 30,3 %. A média do grupo A fica a
   0,3 ponto do leitor atual. A referência com o domínio certo (BRESSAY treino, mesmo orçamento) leva a 13,6 %.
2. **O histórico atrapalha muito.** O grupo B leva o BRESSAY a 46,9 % e o GNHK a 31,7 %.
3. **O sintético ensina os acentos, mas sozinho estraga o resto.** O erro nas letras acentuadas cai de 76 % para
   61 % (só sintético) e 59 % (moderno + sintético). O CER geral só não piora quando o sintético vem misturado.
4. **Todo treino piora o GNHK** (fotos em inglês) em 2 a 17 pontos.
5. **Nas 62 linhas do autor (512 px), nada muda além do ruído.** O melhor resultado foi 63,5 %, contra 65,8 % sem treino.
6. **Decisão para a E4, pela regra da spec:** nenhuma condição melhora ≥ 3 pontos. **A coleta em escala fica
   suspensa e a estratégia de dados é revista** (§6).

## 2. Resultados

CER de linha (WER e acentos no BRESSAY). Mesmo orçamento em todas: 392 passos de 16 linhas, taxa 5e-5, margem
640 px, modelo final. BRESSAY = 2.000 linhas sorteadas do teste; GNHK = teste completo (1.918 linhas);
autor = 62 linhas de 4 páginas, imagens de 512 px.

| Condição | Dados | BRESSAY | WER | Acentos | GNHK | Autor |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: |
| C0 | nenhum (leitor atual) | 29,9 % | 73,1 % | 76,0 % | 15,1 % | 65,8 % |
| C1 | A, latino moderno | **28,9 %** | 71,7 % | 66,0 % | 18,7 % | 65,5 % |
| C1, semente 4321 | A, a mesma lista | 30,3 % | 73,3 % | 61,5 % | 18,1 % | **63,5 %** |
| C2 | B, histórico | 46,9 % | 90,1 % | 94,4 % | 31,7 % | 87,8 % |
| C3 | S, sintético em português | 38,1 % | 85,2 % | 60,8 % | 27,4 % | 70,7 % |
| C4 | A + S | 29,4 % | 71,6 % | **59,2 %** | 18,3 % | 65,5 % |
| C5 | A + B + S | 32,1 % | 75,0 % | 68,7 % | 17,1 % | 68,4 % |
| *Referência (EXP-014)* | *BRESSAY treino* | *13,6 %* | | | | |

A referência foi medida no teste completo; o C0 dá 29,7 % no teste completo e 29,9 % na amostra, então a amostra
representa bem o conjunto.

**Ruído.** As duas sementes do C1 diferem 1,4 ponto no BRESSAY e 2,0 no autor. Diferenças menores que isso não
distinguem condições.

**Treino.** Nenhuma linha foi descartada por caractere fora do dicionário. Cada condição levou ~1h30 de CPU,
sem pausa por falta de memória. Cada lista é um ciclo `experimento` no catálogo (run-0001 a run-0006, nenhum
contaminado).

## 3. Hipóteses

| # | Hipótese | Resultado |
| :--- | :--- | :--- |
| **H1** | o grupo A melhora o português moderno (≥ 3 pontos) | **refutada**: −1,0 e +0,4 ponto nas duas sementes |
| **H2** | o histórico ajuda menos que o moderno | **confirmada**: 46,9 % contra 28,9 %; o histórico piora 17 pontos |
| **H3** | o sintético ensina os acentos (≥ 10 pontos) | **confirmada**: 76,0 % → 60,8 % (−15,2) |
| **H4** | moderno + sintético é a melhor combinação | **não sustentada**: C4 (29,4 %) empata com o C1 (28,9 % e 30,3 %) dentro do ruído |

## 4. O que isso quer dizer

* **O domínio pesa mais que o volume.** Com o mesmo orçamento, 6 mil linhas de redação em português tiram 16
  pontos do erro; 6 mil linhas de francês e norueguês modernos não tiram nenhum. O leitor já lê letra latina
  razoavelmente; o que ele não sabe é a letra e a língua do nosso domínio.
* **O histórico ensina convenções erradas** para o nosso uso: abreviações, letras antigas e grafias medievais.
* **Os acentos são o único ganho transferível**, e vêm de duas fontes: o sintético em português e o francês
  moderno do grupo A, que também tem acentos (−10 a −15 pontos).
* **O GNHK piora com qualquer treino.** O ajuste empurra o leitor para longe do inglês fotografado; um leitor
  geral precisa manter inglês e foto no treino.

## 5. Limites

* **Orçamento pequeno.** 392 passos são menos de uma época sobre 8 mil linhas. Um treino longo com muito mais
  linhas pode transferir algo que este não mostrou; o experimento responde "rende por linha", não "nunca rende".
* **Um só português moderno de medida.** O BRESSAY é redação escaneada de estudantes; as páginas do autor são
  poucas e de 512 px.
* **O sintético tem uma fonte de texto** (20 capítulos de Dom Casmurro) e as fontes OFL do EXP-043.

## 6. Decisão e revisão da estratégia

Pela regra da spec, a **E4 (coletor em escala) fica suspensa**: escalar fontes que não ajudam só gasta disco e
rede. O catálogo, a procedência e o registro de ciclos continuam valendo para qualquer fonte nova.

O que a evidência indica para a revisão, em ordem:

1. **Procurar manuscrito moderno em português e espanhol com licença aberta**, que é o domínio que funcionou. A
   busca é barata e a medida já está pronta: este experimento vira a régua de qualquer fonte nova.
2. **Esclarecer a licença do BRESSAY** com os autores. É o único conjunto que já provou o ganho (29,7 % → 13,6 %).
   Esse passo envia uma mensagem a terceiros e depende do usuário.
3. **Usar o sintético só para acentos**, misturado em pequena parte, nunca como volume.
4. **Medir um treino longo uma vez** (A + S, várias épocas) para descartar o efeito de orçamento antes de
   abandonar de vez as fontes latinas modernas.

A revisão em si é um documento próprio, a ser aprovado pelo usuário antes de qualquer coleta nova.
