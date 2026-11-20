# Roadmaps v3 — leitor geral (várias letras)

> **Revisado em 2026-11-20 pela [estratégia de dados v2](./09-estrategia-de-aquisicao-de-dados.md)** (aprovada): os
> dados vêm só da internet, a custo zero; saem o kit de amigos (F-DI-13.03 vira catálogo de procedência), a
> F-DI-13.04 e a Dados-13.G; o teste usa as divisões oficiais por escritor das bases públicas (§10 da estratégia).

**Data:** 2026-11-20 · **Status:** `APROVADO` pelo usuário em 2026-11-20 · **Substitui:** as partes
do [roadmap v2](./05-roadmaps.md) que ajustam o leitor à letra do autor. O que não é citado aqui continua como no v2.

---

## 1. O que mudou

**Decisões do usuário (2026-11-20):**

1. "Não quero ajustar a minha letra … quero fazer um **leitor geral**." O leitor deve funcionar para pessoas
   cuja letra ele nunca viu.
2. Os amigos do usuário podem mandar fotos de cadernos.
3. As fotos originais do usuário foram perdidas; as 20 páginas de teste existem só em 512 px.

**O que os experimentos já mostraram e continua valendo:**

* **O leitor é o problema** (EXP-028B, 512 px): com as caixas certas, o leitor do produto ainda erra 50,9 %;
  ele responde por ~4/5 do erro. A detecção vale até ~11 pontos; a ordem, 2,5.
* **Ajuste fino com muitas letras generaliza** (EXP-014, H2 confirmada): o leitor ajustado com o BRESSAY
  (redações em português de muitas pessoas) caiu para **13,6 %** de CER em pessoas **fora do treino**. É a
  evidência de que um leitor geral em português é alcançável em CPU — com duas ressalvas: eram redações
  **digitalizadas**, não fotos (em foto, o mesmo leitor foi a 21,6 %, EXP-019), e o BRESSAY tem licença só de
  pesquisa (`NEEDS VALIDATION`), então não pode ir ao produto.
* **Poucas páginas já rendem muito** (EXP-018, cada página de uma pessoa diferente, validação em pessoas fora do
  treino): 50 páginas dão 88 % do ganho, 150 páginas chegam a 13,7 %.
* **Fotos reais não se substituem por degradação artificial** (EXP-021), e a régua precisa ser **por linha**
  (EXP-028A).

## 2. Princípios novos

| Princípio | Regra |
| :--- | :--- |
| **Separação por pessoa** | Cada pessoa fica inteira em **um só** conjunto (treino, validação ou teste). O teste mede letras nunca vistas. A trava é por pessoa, além do hash da página. |
| **A medida principal** | CER e WER **nas pessoas do teste**, mais o CER da **pior pessoa** (um leitor geral não pode ser ótimo para uns e inútil para outros). |
| **Consentimento** | Ninguém entra sem termo assinado: uso local, nunca Git nem serviço externo, finalidade (treinar e medir o leitor), direito de retirar a qualquer momento (o retirado sai de todos os conjuntos e o próximo modelo é treinado sem ele). |
| **Anonimato** | Pessoas viram `w01`, `w02`…; nomes e termos assinados ficam fora do Git; no repositório, só o id, a data do termo e o hash do arquivo do termo. |
| **Fotos originais** | Arquivo do celular em tamanho cheio, sem passar por mensageiro (que comprime). Páginas de estudo que a pessoa aceita mostrar. |
| **Quem transcreve** | De preferência, a própria pessoa (é quem lê a própria letra), num arquivo de texto com **uma linha do papel por linha**. |

## 3. De onde vêm os dados

| Fonte | O que é | Pode ir ao produto? | Papel |
| :--- | :--- | :---: | :--- |
| **Amigos** | fotos + transcrição por linha, com termo | sim, com o termo | treino, validação e o **teste geral** |
| **Páginas do usuário** | 20 de teste em 512 px (4 com referência por linha); 31 sem imagem | sim | uma pessoa entre as outras; o teste em 512 px vira **teste do autor (legado)**, acompanhado mas não decisivo |
| **Texto sintético em português** | linhas geradas com fontes manuscritas livres (OFL) sobre papel | sim | pré-treino e variedade (EXP-035) |
| **GNHK** | manuscrito fotografado, **inglês**, CC-BY-4.0 | sim, com atribuição | detecção e pré-treino de traço; não ensina português |
| **BRESSAY** | redações em português, muitas pessoas | **hoje não** (licença só de pesquisa) | só experimento; se os autores autorizarem o uso, vira a maior fonte em português (item **L-01**) |

## 4. Conjuntos

* **`test-geral`** — 3 pessoas inteiras (≈ 30 páginas), sorteadas entre as primeiras a entregar, congeladas antes de
  qualquer medida.
* **`dev-val`** — 2 pessoas inteiras (≈ 20 páginas), para escolher modelos, limiares e épocas.
* **`dev-train`** — todas as outras pessoas (o usuário incluído, quando houver imagens).
* **`test-autor-512`** — as 20 páginas do usuário em 512 px: acompanhada em todo relatório, com a marca "512 px".
* O `dev-val` antigo (10 páginas do usuário, sem imagem) é aposentado: uma validação de uma pessoa só não mede
  generalização.

## 5. Versões revisadas

### 0.13 — Régua e coleta multi-pessoa

| Item | O quê | Aceite | Depende de |
| :--- | :--- | :--- | :--- |
| **F-DI-13.03** (novo) | **Kit de coleta**: modelo de termo de consentimento, guia de foto de 1 página, registro anônimo de pessoas (`w01`…, fora do Git o que identifica), `register.py` com `writer_id`, pasta por pessoa | termo e guia aprovados pelo usuário; registro de 2 pessoas fictícias de ponta a ponta | — |
| **F-DI-13.04** (novo) | **Transcrição pela própria pessoa**: importar um `.txt` por página (uma linha do papel por linha) e alinhá-lo às caixas (generaliza o rascunho alinhado do EXP-028A); `writer_id` na ferramenta | página fictícia importada com 100 % das linhas no lugar certo quando o motor acha todas as caixas | F-DI-13.03 |
| **F-DI-13.02** (trazido de volta) | Harness com **trava por pessoa e por hash** entre treino, validação e teste; relatório com CER por pessoa e da pior pessoa | teste automatizado do bloqueio; relatório reproduzível | F-DI-13.03 |
| **Dados-13.G** (novo) | **Coleta, fase 1**: ≥ 8 pessoas além do usuário × 8–10 páginas (≈ 80 páginas, ≈ 1.500 linhas) [estimativa a calibrar] | 3 pessoas no `test-geral`, 2 no `dev-val`, o resto no treino, tudo com termo | F-DI-13.03/04 |
| **EXP-029** (mantido) | Professores locais (VLM) para rascunho, agora no `dev-val` de 2 pessoas | escolher o professor com menor CER no `dev-val` em ≤ 5 GB de RAM | Dados-13.G |
| **EXP-030A/B** (mantidos) | Calibrar detecção e escala, agora em fotos de várias pessoas | recall de linhas ≥ 92 % no `dev-val` | Dados-13.G |
| **L-01** (novo, do usuário) | Pedir aos autores do BRESSAY autorização de uso no Leitorum | resposta registrada (sim/não) | — |

**Saída do 0.13:** coleta fase 1 completa e congelada, detecção calibrada (M1) no `test-geral`.

### 0.14 — Leitor geral v1

| Item | O quê | Aceite |
| :--- | :--- | :--- |
| **EXP-A2** (mantido) | dicionário de caracteres do leitor × português do `dev-val` | cobertura 100 % ou plano de expansão |
| **EXP-033G** (substitui 033A/B) | ajuste fino do PP-OCRv6 small com o `dev-train` de várias pessoas (+ sintético; + BRESSAY só se L-01 autorizar), melhor época pelo `dev-val`; curva por **número de pessoas** (4 → 6 → todas) | CER no `test-geral` ≤ 30 % e pior pessoa ≤ 40 % [hipóteses a calibrar com a fase 1] |
| **EXP-035** (mantido) | sintético PT-BR: quanto ajuda com poucas pessoas reais | ganho líquido no `dev-val` |
| **EXP-034** (mantido) | disputa de arquitetura leve | só troca com ≥ 2,5 pontos no `dev-val` |
| **EXP-A6/A7** (mantidos) | sementes, congelamento de camadas; INT8 × FP32 | receita e exportação fixadas |
| **DG-3 / CR-F14.x** | promoção ao motor | CER no `test-geral` ≤ 30 %, ≤ 10 s e ≤ 1,5 GB por página |

### 0.14.5 — Coleta pelo próprio Leitorum

Os CR-F13.1/13.2 do v2 ganham peso: o Leitorum já tem várias contas; com **conferência linha a linha** e
**exportador com consentimento por conta**, amigos que usarem o Leitorum passam a contribuir pelo próprio uso
(opt-in, desligável, com o mesmo termo). Isso substitui a coleta manual como fonte principal a partir do 0.15.

### 0.15 — Leitor geral v2, léxico e ordem

* **Dados-15.G:** 15–25 pessoas; um **teste de deriva por pessoas novas** (pessoas que chegaram depois) em vez
  de páginas novas do mesmo autor.
* **EXP-037:** léxico **geral** de português (corpus livre); sai o léxico das notas do autor.
* **EXP-038:** ordem e zonas (inalterado).

### 0.16 — Fórmulas, zonas e LDF 2.1

Inalterado, com uma ressalva: os recortes de fórmula vêm de várias pessoas.

### MP — Modelo próprio geral

Inalterado na forma (pré-treino sintético + ajuste fino), mas o alvo passa a ser **o leitor geral**: comparação
no `test-geral` e na deriva por pessoas novas.

## 6. O que sai ou muda

| Item do v2 | No v3 |
| :--- | :--- |
| EXP-033A/033B (ajuste à letra do autor) | **sai** → EXP-033G (várias pessoas) |
| Dados-13.1, 14.1 (páginas do autor) | **sai** → Dados-13.G, 15.G (várias pessoas) |
| MP-0 léxico do autor | **sai** → léxico geral (EXP-037) |
| MP-6 "outros autores" (adiado) | **vira o objetivo central** |
| `frozen-test-v3` (20 páginas do autor) | vira `test-autor-512` (legado); o portão passa a ser o `test-geral` |
| EXP-028A (referência do autor) | mantido como está (resultado parcial); a régua por linha vale para todos |

## 7. Primeiro passo

**F-DI-13.03, o kit de coleta** — sem ele não dá para pedir nada aos amigos com segurança. Spec, plano e tarefas
apresentados para aprovação antes de qualquer código, como sempre.

## 8. O que depende do usuário

1. **Aprovar este v3** (ou ajustar).
2. **Quantas pessoas dá para chamar** e se elas topariam transcrever as próprias páginas (≈ 10 min por página).
3. **L-01:** se quer pedir aos autores do BRESSAY autorização de uso (posso escrever o texto do pedido).
