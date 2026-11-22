# EXP-043 — Amostragem das fontes de manuscritos (E1)

* **Criado em:** 2026-11-20
* **Status:** `DONE` ([relatório](./report.md)) — iniciado com a aprovação do usuário à [estratégia de dados v2](../../docs/replanejamento-0.13/09-estrategia-de-aquisicao-de-dados.md)
  ("Aprova a v2 para eu começar pela amostragem das fontes (E1)?" — "Aprovo", 2026-11-20)
* **Etapa:** E1 da estratégia v2 ("descobrir antes de construir")
* **Tipo:** experimento de levantamento; não treina modelo

---

## 1. Pergunta

Quais fontes gratuitas fornecem, **na prática**, mais linhas de manuscrito transcritas, com licença compatível,
coletáveis de forma automática e sem desperdiçar espaço? A resposta escolhe as fontes do EXP-031P (E3) e dos
conectores (E4).

## 2. O que a sondagem de acesso já mostrou (2026-11-20)

| Fonte | Acesso automatizado | Observação |
| :--- | :--- | :--- |
| Library of Congress (By the People) | **bloqueado**: `www.loc.gov`, `crowd.loc.gov` e `tile.loc.gov` respondem 403 com desafio do Cloudflare a clientes não navegadores; os pacotes do `data.labs.loc.gov` não incluem o By the People | não se contorna; status `BLOCKED` (automação), reavaliar depois |
| HTR-United (catálogo) | **livre** (GitHub) | 138 conjuntos; 87 só manuscritos, **~1,49 milhão de linhas**; 105 CC-BY 4.0, 18 CC-BY-SA 4.0; português: só o iForal (medieval, 8 mil linhas); FONDUE-MLT-CAT é **impresso** |
| Teklia no Hugging Face | **livre** (API de linhas do `datasets-server`: imagem + texto por linha, sem baixar o conjunto inteiro) | 12 conjuntos, ~700 mil linhas; rótulo MIT, mas a licença que vale é a da **fonte original** de cada um |
| BRESSAY, GNHK | já baixados | `EXPERIMENT_ONLY` e `APPROVED` |
| Europeana | API exige chave (cadastro) | criar conta não está autorizado; fora da E1 |
| Wikimedia Commons / Wikisource | a política pede contato no User-Agent | decidir o contato antes; fora da E1 |

## 3. Como

1. **Amostras pequenas**, por fonte: até 200 linhas (Teklia, pela API de linhas) ou até 20 páginas com a
   verdade-terreno PAGE/ALTO (HTR-United, conjuntos hospedados no GitHub, que permitem baixar arquivos avulsos).
   Sintético: 200 linhas geradas localmente (fontes OFL do projeto + texto em domínio público).
2. **Procedência de cada arquivo** num manifesto JSONL: fonte, endereço, data, licença declarada e licença da
   fonte original, evidência (cópia dos termos com hash), idioma, época, tipo de transcrição, SHA-256.
3. **Medidas por fonte:** linhas por página; tamanho por linha (original e recodificada em cinza, WebP sem perda,
   altura de 64 px); caracteres por linha; cobertura de acentos do português; linhas utilizáveis (texto não
   vazio, imagem legível); estimativa do total de linhas e de GB no nosso formato; e o **CER do leitor atual do
   produto** nas linhas amostradas (dificuldade e distância do nosso domínio — não diz se a fonte ajuda a treinar,
   isso é o EXP-031P).
4. **Classificação** de cada fonte em `APPROVED`, `EXPERIMENT_ONLY` ou `PENDING_REVIEW` pela §3 da estratégia.

## 4. Regras

* Só endereços públicos, sem conta, sem login, sem contornar bloqueio; User-Agent próprio e sem dado pessoal;
  pausa entre requisições.
* Amostras em `D:\Leitorum-DI\amostras\exp-043\` (teto de **5 GB**), fora do Git. Amostras de fonte
  `PENDING_REVIEW` servem só para esta medida e são **apagadas no fim** se a fonte não for aprovada.
* Nenhum treino. Nenhum dado do usuário.

## 5. Entregas

* `report.md`: tabela "quanto rende cada fonte" e recomendação para o EXP-031P.
* Manifestos de amostra (fora do Git) e um resumo versionado só com números.

## 6. Critério de pronto

Todas as fontes acessíveis da §2 medidas, com classificação e estimativa de volume; recomendação de 3 a 5 fontes
para o EXP-031P, justificada pelos números.
