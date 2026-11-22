# EXP-043 — Relatório: quanto rende cada fonte de manuscritos

* **Data:** 2026-11-20 a 2026-11-22 · **Status:** `DONE`
* **Spec:** [spec.md](./spec.md) · **Números:** [resultados.json](./resultados.json) (só medidas, sem texto)
* **Amostras:** `D:\Leitorum-DI\amostras\exp-043\` (~1,5 GB, fora do Git); as das fontes `PENDING_REVIEW`
  (Esposalles, NorHand v3) foram **apagadas** no fim, como manda a regra.

## 1. Resumo

1. **Dados abertos e coletáveis não faltam.** Só nas fontes amostradas há **~350 mil linhas transcritas
   aprovadas** (Teklia + 8 conjuntos do HTR-United), e o catálogo do HTR-United lista **~1,5 milhão de linhas de
   manuscrito**, quase todas CC-BY ou CC-BY-SA.
2. **Espaço não é o limite.** No nosso formato (linha em cinza, 64 px de altura, WebP com perda leve) uma linha
   ocupa **3,5 a 17 KB** (média ~7 KB): 1,5 milhão de linhas cabem em **~10 GB**; sem perda, ~37 GB. Os 100 GB
   sobram.
3. **O que falta é o nosso domínio.** Quase tudo é **histórico** (séc. XIII–XX) e em **francês, latim,
   norueguês e inglês**. Manuscrito em português: só o iForal (medieval). Letra moderna: poucos conjuntos
   pequenos (Moonshines, CREMMA séc. XX, Célestine) e o RIMES (francês contemporâneo, não comercial).
4. **A Library of Congress, que seria a maior fonte com transcrição, bloqueia acesso automatizado** (desafio do
   Cloudflare); não contornamos.
5. **O sintético, como está, é fácil demais** (o leitor erra 8,7 %): só ajuda com aumentos bem mais fortes.

## 2. Fontes medidas

`CER do leitor` = erro do leitor atual do produto em 100 linhas da fonte (quanto mais alto, mais distante do que
ele já sabe ler). `Linhas` = divisão de treino declarada (Teklia) ou volume do catálogo (HTR-United).

| Fonte | Status | Idioma, época | Linhas | KB/linha (com perda / sem) | Acentos /1000 car. | CER do leitor |
| :--- | :--- | :--- | ---: | :---: | ---: | ---: |
| NorHand v2 | `APPROVED` (CC-BY-4.0) | norueguês, 1820–1940 | 145.009 | 7,6 / 29,3 | 0,3 | 34,3 % |
| HOME-Alcar | `APPROVED` (CC-BY-4.0) | latim, medieval | 59.969 | 11,9 / 28,3 | 0,7 | 58,9 % |
| Notaires de Paris (lectaurep) | `APPROVED` (CC-BY-4.0) | francês, 1830–1939 | 29.410 | 3,5 / 10,7 | 17,7 | 36,4 % |
| Belfort | `APPROVED` (CC-BY-4.0) | francês, 1790–1946 | 25.800 | 17,0 / 54,6 | 23,2 | 37,6 % |
| CREMMA Medieval | `APPROVED` (CC-BY-4.0) | francês antigo | 22.848 | 8,4 / 23,1 | 4,7 | 38,7 % |
| NorHand v1 | `APPROVED` (CC-BY-4.0) | norueguês | 19.653 | 8,6 / 30,2 | 0,0 | 42,7 % |
| Himanis | `APPROVED` (CC-BY-4.0) | latim, francês, medieval | 18.504 | 17,2 / 43,3 | 7,2 | 63,9 % |
| RIMES 2011 | `APPROVED` não comercial (CC-BY-NC-4.0) | francês contemporâneo | 10.188 | 6,1 / 10,7 | 23,7 | 20,7 % |
| iForal | `APPROVED` (CC-BY-4.0) | **português**, latim, 1217–1491 | 8.009 | 8,6 / 25,8 | 8,5 | 84,8 % |
| Joseph Hooker | `APPROVED` (CC-BY-SA-4.0) | inglês, 1850–1911 | 7.100 | 4,0 / 16,1 | 0,0 | 57,8 % |
| POPP | `APPROVED` (CC-BY-4.0) | francês, 1926 | 3.835 | 6,8 / 24,5 | 8,4 | 53,4 % |
| Moonshines | `APPROVED` (CC-BY-4.0) | francês, **2023** | 1.016 | 4,8 / 10,8 | 21,2 | 16,2 % |
| Notre-Dame | `APPROVED` (CC-BY-4.0) | francês, 1860 | 735 | 7,0 / 24,7 | 15,8 | 47,8 % |
| CREMMA Manuscrits du 20e | `APPROVED` (CC-BY-4.0) | francês, séc. XX | 224 | 3,8 / 12,9 | 22,5 | 54,8 % |
| Célestine Doniau-Danest | `APPROVED` (CC-BY-4.0) | francês, 1914–1915 | 144 | 12,1 / 34,4 | 22,4 | 28,8 % |
| IAM | `EXPERIMENT_ONLY` (pesquisa) | inglês contemporâneo | 6.482 | 7,5 / 26,2 | 0,0 | **8,3 %** |
| NorHand v3 | `PENDING_REVIEW` (licença da v3 a confirmar) | norueguês | 222.381 | 7,3 / 25,6 | 0,0 | 32,3 % |
| Esposalles | `PENDING_REVIEW` (licença não encontrada) | catalão, séc. XVII | 2.328 | 12,5 / 29,9 | 0,3 | 24,6 % |
| Sintético (Dom Casmurro + fontes OFL) | `APPROVED` | **português** | ilimitado | 3,6 / 6,7 | 18,7 | 8,7 % |

**Observações:**

* **IAM com 8,3 %** indica que o leitor já viu o IAM (ou algo muito parecido) no treino original: não serve como
  teste de "pessoas não vistas".
* A contagem de acentos usa á, à, â, ã, é, ê, í, ó, ô, õ, ú, ü, ç: o francês tem vários deles (é, à, ç, â, ê,
  ô), mas **nenhuma fonte real tem ã/õ em volume** — só o sintético e o iForal.
* Todas as linhas amostradas eram utilizáveis (texto não vazio, imagem legível), exceto 0,1–2 % em dois
  conjuntos.
* **Sintético:** 0,05 s por linha num núcleo (~70 mil linhas por hora), gerado na hora, sem ocupar disco.

## 3. O que não deu certo (e por quê)

| Fonte | Resultado | Motivo |
| :--- | :--- | :--- |
| Library of Congress — By the People | **não acessível** | `www.loc.gov`, `crowd.loc.gov` e `tile.loc.gov` respondem 403 com desafio do Cloudflare a clientes automatizados; o portal de pacotes de dados não tem o By the People. Não contornamos. |
| RASAM 1, Araucania XIX, CHI-KNOW-PO, Bullinger | **sem imagens no repositório** | o GitHub guarda só o XML; as imagens ficam em outro lugar (IIIF, Zenodo) — cabe a um conector específico na E4, se valer a pena |
| HOME-Alcar (1ª tentativa) | 503 temporário | resolvido repetindo; o coletor agora repete erros 5xx com espera crescente |
| Europeana, Wikimedia Commons/Wikisource | não amostrados | a Europeana exige chave de API (cadastro, não autorizado); o Wikimedia pede contato no User-Agent (decisão pendente). O Wikisource foi usado só para o texto do sintético. |
| Conjuntos do HTR-United hospedados no Zenodo | não amostrados | vêm em arquivos `.zip` grandes; ficam para a E4 |

## 4. Recomendação para o EXP-031P (E3)

A pergunta do EXP-031P é: **treinar com esses dados melhora a leitura de letra moderna em português de pessoas
não vistas?** Proposta de grupos, todos `APPROVED`:

| Grupo | Fontes | Linhas | Por quê |
| :--- | :--- | ---: | :--- |
| **A — latino moderno** | RIMES, Moonshines, CREMMA séc. XX, Célestine, Notaires de Paris, Belfort, POPP, NorHand v2 | ~216 mil | letra dos séc. XIX–XXI; o mais perto do nosso domínio que existe aberto |
| **B — histórico** | HOME-Alcar, Himanis, CREMMA Medieval, iForal | ~109 mil | testa se letra antiga ajuda ou atrapalha; traz o único português manuscrito |
| **C — sintético PT** | Dom Casmurro e outros textos em domínio público + fontes OFL, **com aumentos fortes** | ilimitado | ensina ortografia e acentos do português (ã, õ) |

**Como medir (pessoas não vistas):** divisão de teste do **BRESSAY** (português moderno, `EXPERIMENT_ONLY`,
permitido para medir), divisão de teste do **GNHK** (fotos de celular, inglês) e as **4 páginas do autor** com
referência linha a linha (512 px). O IAM fica de fora da medida (contaminado).

**Espaço:** A + B no nosso formato com perda leve ≈ **3 GB**; sem perda ≈ 9 GB. Cabe com folga.

## 5. Próximos passos (estratégia v2)

1. **E2 — catálogo mínimo** (F-DI-13.03 redefinida): SQLite, armazenamento por conteúdo, status, lista de
   bloqueio e manifesto por ciclo de treino — antes de baixar os grupos A e B inteiros.
2. **E3 — EXP-031P** com os grupos acima.
3. **Decisões abertas para o usuário:** contato no User-Agent para usar Wikimedia (Commons/Wikisource) em escala;
   se vale tentar a Europeana (exige cadastro).
