# EXP-028B — De onde vem o erro: caixas ou leitura (em imagens de 512 px)

* **Criado em:** 2026-11-20
* **Status:** `DONE` (aprovado e executado em 2026-11-20; [relatório](./report.md))
* **Roadmap:** épico 0.13-0, item **EXP-028B** do [roadmap 0.13](../../docs/replanejamento-0.13/05-roadmaps.md)
* **Depende de:** EXP-028A (referência v3 linha a linha, [relatório parcial](../EXP-028A-referencia-v3/report.md))
* **Decisão do usuário (2026-11-20):** as fotos originais foram perdidas; usar as imagens de 512 px.

---

## 1. Pergunta

O produto erra cerca de 70 % dos caracteres nestas páginas. Quanto disso vem de **achar as linhas** (caixa
perdida, cortada, juntando duas linhas, fora de ordem) e quanto vem de **ler** uma linha bem recortada? A
resposta decide onde o 0.13 e o 0.14 gastam esforço: na detecção (EXP-030A/B) ou no leitor (EXP-033A).

O EXP-028A mostrou que separar isso só pelo texto não funciona (42 de 62 linhas sem par). Aqui a separação é
exata: as **caixas desenhadas pelo autor** dizem onde cada linha está, e o texto dele diz o que está escrito.

## 2. Como (três leituras das mesmas páginas, mesmo leitor)

Todas com o leitor do produto (PP-OCRv6 small, ONNX, margem à direita, escala da página para linhas de ~80 px),
nas imagens de 512 px, nas 4 páginas da v3 (p10, p11, p14, p15; 62 linhas):

| Leitura | Caixas | O que mede |
| :--- | :--- | :--- |
| **A — produto** | as do motor (detecção + fusão + ordem do produto) | o erro de ponta a ponta em 512 px |
| **B — caixas perfeitas** | as do autor, na ordem dele | o erro só do leitor |
| **C — caixas perfeitas, ordem do motor** | as do autor, ordenadas pela regra do produto | quanto a ordem pesa |

* **Parte da detecção** = CER(A) − CER(C); **parte da ordem** = CER(C) − CER(B); **parte do leitor** = CER(B).
* Em B, cada linha lida tem par exato com a linha da referência (mesmo `line_id`): dá também o CER **por linha**
  e a distribuição (quantas linhas o leitor acerta, quantas erra quase tudo).
* **Custo da resolução:** CER(A) em 512 px comparado com o CER do produto nas fotos originais (69,8 %, EXP-028A).
  É a medida de quanto as imagens reduzidas pioram a leitura, e calibra a ressalva de todo resultado em 512 px.

## 3. Hipóteses

| # | Hipótese (do roadmap) | Mede |
| :--- | :--- | :--- |
| **H1** | ≥ 10 pontos do CER de página vêm das caixas e da ordem, não do leitor | CER(A) − CER(B) ≥ 10 p.p. |
| **H2** | o leitor puro, com caixas perfeitas, ainda erra mais de 40 % | CER(B) > 40 % |
| **H3** | a imagem de 512 px piora o produto em mais de 5 pontos | CER(A, 512) − 69,8 % > 5 p.p. |

## 4. Limitações declaradas

* **512 px:** o leitor erra mais em imagem pequena; a parte "leitor" sai **inflada** em relação ao produto real.
  Por isso a H3 mede o tamanho dessa distorção, e o relatório separa o que vale só para 512 px.
* **4 páginas, 62 linhas:** indica a direção; não fecha o portão DG-1.
* **Caixas do autor desenhadas em 512 px**, com cantos ajustados à mão: são a melhor referência disponível, não
  uma caixa "perfeita" de verdade.

## 5. Regras

As 4 páginas são do teste congelado: só medir. Nenhum ajuste de parâmetro, limiar ou modelo é escolhido aqui (isso
é do `dev-val`, EXP-030A). Só números no relatório; nada de texto, imagem ou recorte. Tudo local, em CPU, sem
download. Nenhuma tarefa do usuário.

## 6. Mudança de ordem no roadmap (para aprovar)

O roadmap põe a F-DI-13.02 (harness com trava de hashes entre treino e teste) antes deste experimento. Proponho
adiá-la para **antes do primeiro treino (EXP-033A)**, que é onde a trava importa: este experimento não treina nada
e usa só as 4 páginas medidas no EXP-028A.
