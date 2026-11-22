# Estratégia de aquisição de dados em escala — v2

**Data:** 2026-11-20 · **Status:** `APROVADO v2` pelo usuário em 2026-11-20 · **Complementa:** o
[roadmap v3 — leitor geral](./08-roadmaps-v3-leitor-geral.md) e o revisa onde indicado (§10).

> **Aviso.** Análise técnica com fontes, não parecer jurídico. Onde a lei ou a licença é incerta, o texto diz.

---

## 0. Decisões do usuário que esta versão incorpora (2026-11-20)

1. **O Leitorum nunca terá finalidade comercial**: sem anúncios, assinaturas, venda de dados ou licenciamento;
   só doações voluntárias, sem contrapartida. Licenças "não comerciais" devem ser **avaliadas uma a uma**.
2. **Os dados vêm da internet**, não mais de fotos entregues à mão; qualquer idioma serve para a capacidade geral.
3. **Até 100 GB no HD (D:)**, como teto, com economia de espaço.
4. **Categoria para situação incerta** (`FLAG` ou `PENDING_REVIEW`), fora do treino, com revisão periódica, e
   **rastreabilidade** de quais itens entraram em cada modelo.
5. **Custo zero**: nada pago, nenhuma nuvem; pago só como possibilidade futura.
6. **Sem autorização individual** quando domínio público ou licença pública já permitem; nunca contornar
   paywall, CAPTCHA, login ou bloqueio.
7. **Descobrir antes de construir**: medir quais fontes ajudam antes de montar infraestrutura.

## 1. O que muda em relação à v1

| v1 | v2 | Por quê |
| :--- | :--- | :--- |
| Amigos com termo (kit F-DI-13.03), transcrição pela pessoa (F-DI-13.04) | **saem** | decisão 2; o kit vira só o **catálogo de procedência** |
| Categorias A0 / A1 / A2 / B / C | `APPROVED`, `EXPERIMENT_ONLY`, `PENDING_REVIEW`, `REJECTED`, `BLOCKED` (§5) | decisões 1 e 4: "não comercial" deixa de ser automaticamente "só experimento"; o incerto ganha ciclo de vida |
| "Não comercial ⇒ fora do produto" | **avaliação por licença** (§3) | decisão 1 |
| Compra, parceria, Biblioteca Nacional como parceria | **fora do plano atual** (§9) | decisões 5 e 6 |
| `test-geral` com 3 amigos | **divisões oficiais por escritor** dos próprios datasets públicos (§6) | sem amigos, as bases públicas já trazem treino e teste separados por pessoa |
| Infraestrutura completa (E1–E6) | **amostrar primeiro**, construir o mínimo, escalar só o que ajuda (§8) | decisão 7 |

---

## 2. O que o modelo precisa (critério para ranquear fontes)

Em ordem de valor para um leitor de manuscrito geral:

1. **Imagem de manuscrito + transcrição por linha** (treino supervisionado direto).
2. **Imagem + transcrição por página** (precisa alinhar à linha, como fizemos no EXP-028A).
3. **Imagem sem transcrição** (detecção, pré-treino e rascunho de professor com revisão por amostra) — vale
   menos e custa espaço; só entra com propósito definido.
4. **Texto em português** (para o sintético e o léxico) e **fontes manuscritas livres** — volume ilimitado, zero
   espaço se gerado na hora.

Letra moderna e português pesam mais; letra histórica e outros idiomas servem para **capacidade geral**
(traço, inclinação, conexões), a ser **medida** antes de escalar (EXP-031P, §8).

---

## 3. Licenças à luz do uso não comercial

A licença NC da Creative Commons define não comercial como uso "não principalmente destinado a vantagem
comercial ou compensação monetária"; o tipo de usuário pesa menos que o uso ([CC wiki](https://wiki.creativecommons.org/NonCommercial_interpretation);
[Pitt](https://pitt.libguides.com/openlicensing/cc-non-comerical)). Uma diretriz **proposta** da CC (2006, não
confirmada como adotada) tratava doação opcional a pessoa ou entidade sem fins lucrativos como uso não comercial
([lista CC](https://lists.ibiblio.org/sympa/arc/cc-licenses/2006-01/msg00035/pdflZDb4RzeKF.pdf)).

| Licença | Para o Leitorum (não comercial, doação voluntária) | Condições a cumprir | Categoria |
| :--- | :--- | :--- | :--- |
| Domínio público, CC0, PDM | compatível | conferir o rótulo por amostra | `APPROVED` |
| CC-BY | compatível | atribuição no "resumo do conteúdo de treino" e no cartão do modelo | `APPROVED` |
| CC-BY-SA | compatível | atribuição; se o modelo for considerado "adaptação" (incerto), distribuí-lo sob licença compatível | `APPROVED` com registro |
| **CC-BY-NC** | **compatível** pelo texto da licença, desde que: sem anúncio, sem cobrança, sem venda, doação sem contrapartida | registrar essas condições como regra do projeto; reavaliar se algo mudar | `APPROVED` (condicional) |
| **CC-BY-NC-SA** | compatível como acima | **licenciar os pesos do leitor sob CC BY-NC-SA** (a 3.0 permite versão posterior com os mesmos elementos); atribuição | `APPROVED` (condicional) |
| CC-BY-ND / NC-ND | **incerto**: treinar pode ser considerado criar obra derivada | — | `PENDING_REVIEW` |
| "Só pesquisa" / "pesquisa e ensino" (IAM; README do BRESSAY) | **incerto para o produto**: o Leitorum não é pesquisa nem ensino em sentido estrito | experimentos internos são pesquisa | `EXPERIMENT_ONLY` |
| Licença de reempacotamento diferente da original (ex.: IAM-line da Teklia marcado MIT no Hugging Face) | **vale a mais restritiva, a da fonte original** | rastrear a fonte de cada reempacotamento | conforme a original |
| Sem licença declarada / termos não encontrados | incerto | guardar só metadados até esclarecer | `PENDING_REVIEW` |
| Paywall, login, opt-out de IA, termos que proíbem coleta | — | não coletar | `BLOCKED` |

**Dois casos concretos que esta tabela decide:**

* **BRESSAY** (português moderno, ~1.000 autores): a página TC-11 declara **CC BY-NC-SA 3.0**
  ([TC-11](https://tc11.cvc.uab.es/datasets/BRESSAY_1)), o Zenodo diz CC-BY-4.0 nos metadados e o README do
  arquivo restringe a "pesquisa e ensino não comerciais". Vale a mais restritiva: **`EXPERIMENT_ONLY`** — entra
  em experimentos e na medida (inclusive como teste de pessoas não vistas), mas **não** num modelo distribuído
  até o conflito ser esclarecido. Ele fica na lista de revisão periódica.
* **IAM** (inglês, 657 escritores): "non-commercial research purposes only" ([IAM](https://fki.tic.heia-fr.ch/databases/iam-handwriting-database)):
  **`EXPERIMENT_ONLY`**, mesmo no reempacotamento MIT.

---

## 4. Fontes, por volume útil, transcrição e automação

Estimativas de volume são as publicadas pelas fontes; "a medir" quer dizer que a amostragem (§8, E1) dirá.

| # | Fonte | Endereço | Volume e conteúdo | Transcrição | Licença | Automação | Categoria esperada |
| :---: | :--- | :--- | :--- | :---: | :--- | :--- | :--- |
| 1 | **Library of Congress — By the People** | [crowd.loc.gov](https://crowd.loc.gov/about/) · [datasets](https://labs.loc.gov/work/experiments/crowd) | > 1 milhão de transcrições concluídas (mar/2026); 52 campanhas; manuscritos históricos, sobretudo inglês, muito cursivo do séc. XIX | **por página** | transcrições em **domínio público**; imagens com direito por item (o acervo é majoritariamente sem restrição conhecida — conferir campo de direitos) | **CSV em lote** por campanha + API JSON do loc.gov | `APPROVED` (itens com direitos livres) |
| 2 | **Coleção ATR da Teklia** (Hugging Face) | [coleção](https://huggingface.co/collections/Teklia/datasets-atr-line-level-65f171515df9c72ff26f655a) | IAM, RIMES, NorHand v1–v3, Esposalles, Himanis, HOME-Alcar, POPP, Belfort, NewsEye, CASIA (chinês) — vários idiomas e épocas | **por linha** | rótulo do repositório + **licença original de cada um** | download direto (`datasets`/Parquet) | por conjunto: IAM `EXPERIMENT_ONLY`; NorHand e outros conforme a original |
| 3 | **HTR-United** (catálogo) | [htr-united.github.io](https://htr-united.github.io/catalog.html) | dezenas de conjuntos de verdade-terreno, inclusive português histórico (IISH CC-BY-SA-4.0; iForal) | por linha (PAGE/ALTO) | por conjunto, muitos CC-BY/BY-SA | GitHub/Zenodo | por conjunto |
| 4 | **BRESSAY** | [TC-11](https://tc11.cvc.uab.es/datasets/BRESSAY_1) | redações em **português moderno**, ~1.000 autores, com divisão oficial por autor | por linha | conflitante (§3) | download único (já temos) | `EXPERIMENT_ONLY` |
| 5 | **Wikisource + Commons** | [ProofreadPage](https://en.wikisource.org/wiki/Wikisource:ProofreadPage) · [API](https://www.mediawiki.org/wiki/Wikimedia_APIs/Access_policy) | páginas escaneadas com transcrição revisada, muitos idiomas (inclusive pt); maioria impressa, parte manuscrita | por página | domínio público ou CC-BY-SA; licença do escaneado por arquivo no Commons | **API** com User-Agent e limites | `APPROVED` por arquivo |
| 6 | **READ / ICDAR 2017 HTR** | [Zenodo](https://zenodo.org/record/835488) | documentos históricos europeus | por linha | **a confirmar** no registro | download único | `PENDING_REVIEW` até confirmar |
| 7 | **GNHK** | [GitHub](https://github.com/GoodNotes/GNHK-dataset) | 687 fotos de celular de anotações (inglês) | por linha | CC-BY-4.0 | download único (já temos) | `APPROVED` |
| 8 | **Europeana** | [europeana.eu](https://www.europeana.eu/en/rights/terms-of-use) | milhões de itens; filtro por direitos (CC0/PDM/CC-BY) | transcrições do Transcribe: **licença incerta** (CC BY-SA ou sem direitos, fontes divergem) | por item | **API** | imagens `APPROVED` por item; transcrições `PENDING_REVIEW` |
| 9 | **Smithsonian Transcription Center** | [transcription.si.edu](https://transcription.si.edu/) | > 1 milhão de páginas transcritas (2022) | por página | licença das transcrições **não encontrada** | site; API a verificar | `PENDING_REVIEW` |
| 10 | **Sintético** | fontes OFL ([Google Fonts](https://github.com/google/fonts)) + texto em domínio público | ilimitado, português | perfeita | OFL + domínio público | gerado localmente | `APPROVED` |

**Prioridade inicial (o que mais rende primeiro):** 1, 2, 3 e 10, com 4 e 7 (já baixados) como régua. Cobrem
transcrição por linha ou página, vários idiomas, volume alto, download em lote e licença verificável. 5, 8 e 9
entram depois da amostragem, se a E1 mostrar volume manuscrito útil.

**Scraping:** só onde não houver API ou arquivo em lote **e** os termos permitirem: robô com User-Agent
próprio, `robots.txt` e `Crawl-delay` respeitados, limite de requisições, retomável. Nunca login, paywall,
CAPTCHA ou troca de IP para fugir de limite.

---

## 5. Classificação e a categoria `PENDING_REVIEW`

**Nome:** `PENDING_REVIEW` (o termo `FLAG` vira só um rótulo visual). É mais claro sobre o que falta — uma
revisão — e não se confunde com outras marcas.

| Status | Significado | Entra no treino? | Arquivos guardados |
| :--- | :--- | :--- | :--- |
| `APPROVED` | licença ou domínio público verificados e compatíveis | **sim** | sim |
| `EXPERIMENT_ONLY` | permitido para pesquisa, não para modelo distribuído | só em experimentos; **nunca** num modelo promovido ao Leitorum | sim |
| `PENDING_REVIEW` | útil, mas licença não confirmada | **não** | **só metadados e endereço** (sem baixar o arquivo, economiza espaço e risco) |
| `REJECTED` | confirmado que não pode | não | **apagados**: originais, recortes, caches, derivados; o hash e o endereço vão para a lista de bloqueio, para nunca voltarem |
| `BLOCKED` | fonte que não se coleta (paywall, opt-out, termos) | não | nada |

**Ciclo de revisão:**

1. A ingestão classifica sozinha pelas regras da §3; o que não se encaixa vai para `PENDING_REVIEW` com o
   motivo (`sem_licenca`, `licenca_conflitante`, `nd`, `rotulo_suspeito`…) e a evidência coletada (cópia dos
   termos com data e hash).
2. **Revisão periódica**: antes de cada ciclo de treino e, no mínimo, uma vez por mês. Uma lista agrupada **por
   fonte e motivo** (não item a item): resolver o motivo de uma fonte resolve todos os itens dela.
3. Aprovado → `APPROVED` (ou `EXPERIMENT_ONLY`), o arquivo é baixado e entra no **próximo** ciclo.
4. Rejeitado → `REJECTED` com apagamento completo (passo verificado por um teste que procura o hash em todas as
   pastas).
5. Ainda incerto → fica, com a data da última revisão.

---

## 6. Rastreabilidade do treino

* **Manifesto por ciclo de treino:** lista exata de itens (id, hash do conteúdo, status e licença naquele
  momento), receita, semente e hash do código. Gravado junto do checkpoint; o "resumo do conteúdo de treino"
  e o cartão do modelo saem dele.
* **Portão de promoção:** um modelo só vai para o Leitorum se **todos** os itens do manifesto estiverem
  `APPROVED` (nenhum `EXPERIMENT_ONLY`, `PENDING_REVIEW` ou `REJECTED`).
* **Exclusão posterior não desfaz aprendizado.** Por isso: quando um item vira `REJECTED`, todos os modelos cujo
  manifesto o contém ficam **contaminados**: deixam de ser usados e distribuídos e entram na fila de **retreino
  sem o item** (a receita e a semente guardadas tornam isso reprodutível; em CPU, horas). Os checkpoints
  contaminados são apagados depois que o substituto passar no teste.
* **Teste por pessoa não vista:** as divisões oficiais por escritor dos datasets (BRESSAY, IAM, GNHK) e as 20
  páginas do autor em 512 px; nenhum escritor de teste entra no treino (trava por escritor e por hash).

---

## 7. Os 100 GB (D:)

Tudo em `D:\Leitorum-DI\` (fora do repositório e dos backups do Leitorum), com armazenamento **por conteúdo**:
cada arquivo é gravado com o nome do próprio SHA-256, então duplicata exata não ocupa espaço duas vezes.

| Pasta | Teto | O que guarda | Economia |
| :--- | ---: | :--- | :--- |
| `catalogo/` | 1 GB | SQLite local (fontes, itens, arquivos, revisões, ciclos de treino, itens por ciclo) + cópias datadas dos termos | metadados só |
| `originais/` | 30 GB | páginas originais **só quando necessário** (teste, validação, fonte sem endereço estável) | o resto é rebaixável pelo endereço registrado |
| `linhas/` | 45 GB | recortes de linha em cinza, WebP sem perda, altura padronizada; ~5–15 KB por linha → **3 a 6 milhões de linhas** | é o que o treino usa; página inteira é descartada depois de recortada |
| `pendentes/` | 2 GB | só metadados e miniaturas dos `PENDING_REVIEW` | sem arquivo original |
| `modelos/` | 10 GB | checkpoints com manifesto; mantém os últimos e os promovidos | poda automática |
| `trabalho/` | 10 GB | temporários de ingestão | limpo a cada lote |
| reserva | 2 GB | — | — |

**Deduplicação e integridade:** SHA-256 (exata) e *hash* perceptivo de página (quase-duplicata, ex.: o mesmo
manuscrito em duas bibliotecas); recorte de linha deduplicado por hash do recorte normalizado + texto; conferência
periódica dos hashes. **Filtros antes de gravar:** resolução mínima, presença de texto (detector do produto),
transcrição presente ou utilidade declarada; o que não passa não ocupa espaço. **Sintético:** gerado na hora do
treino, não armazenado (só um conjunto fixo pequeno de validação).

---

## 8. Plano: descobrir antes de construir

| Etapa | O quê | Entrega | Por que nesta ordem |
| :---: | :--- | :--- | :--- |
| **E1 — Amostragem das fontes** ✅ ([EXP-043](../../experiments/EXP-043-amostragem-de-fontes/report.md)) | para as fontes 1, 2, 3 e 10 (e 5, 8 se houver tempo): baixar **amostras pequenas** (~200 itens cada), guardar a evidência de licença, medir idioma, época, tipo de transcrição, qualidade da imagem, linhas por página, espaço por linha | tabela "quanto rende cada fonte" com números; < 5 GB | evita construir conectores para fontes que não servem |
| **E2 — Catálogo mínimo** | SQLite + armazenamento por conteúdo + status (§5) + manifesto por ciclo (§6) + lista de bloqueio; sem interface | `F-DI-13.03` (redefinida) | é o que garante procedência desde o primeiro arquivo |
| **E3 — EXP-031P: quais fontes ajudam?** | ajuste do leitor com cada fonte amostrada (e combinações), medido em pessoas não vistas: BRESSAY teste, GNHK teste, as 20 páginas do autor (512 px) | relatório; decisão de escala | a regra do projeto: medir antes; histórico/inglês pode não ajudar a letra moderna |
| **E4 — Escala do que ajudou** | conectores completos só para as fontes vencedoras, dentro do teto de 100 GB; ingestão automática com filtros e deduplicação | `F-DI-13.05` (conectores), `F-DI-13.06` (ingestão) | só depois da evidência |
| **E5 — Leitor geral v1** | EXP-033G com o acervo aprovado + sintético | 0.14 | — |
| **E6 — Governança** | revisão mensal dos `PENDING_REVIEW`, resumo do conteúdo de treino por modelo, portão de promoção, retreino quando houver contaminação | parte do harness (F-DI-13.02) | permanente |

**Custo:** tudo em Python e bibliotecas abertas, SQLite, CPU local e o HD D:. Nenhum serviço pago.

---

## 9. Possibilidades futuras (fora do plano atual)

Pagas ou dependentes de terceiros — **não fazem parte do planejamento**, ficam só registradas: GPU na nuvem
para pré-treino; compra de datasets comerciais de manuscrito; parcerias com instituições (ex.: Biblioteca
Nacional, que hoje reproduz só domínio público sob a Lei 9.610/98 e não publica licença aberta para o acervo
digital — [BN](https://www.gov.br/bn/pt-br/servicos/reproducao-do-acervo-1)); coleta opt-in pelos usuários do
Leitorum (0.14.5), que voltaria a ser útil se houver usuários dispostos.

---

## 10. Impacto no roadmap v3

| Item do v3 | Agora |
| :--- | :--- |
| F-DI-13.03 kit de coleta (amigos) | **redefinido**: catálogo de procedência (E2); termo e guia para amigos saem |
| F-DI-13.04 transcrição pela pessoa | **sai** |
| Dados-13.G (≥ 8 amigos) | **sai** → E1 + E4 (fontes da internet) |
| `test-geral` (3 amigos) | **divisões oficiais por escritor** (BRESSAY, IAM, GNHK) + `test-autor-512` |
| F-DI-13.02 (trava por pessoa) | inclui trava **por escritor e por fonte** e o portão de promoção (§6) |
| EXP-029 professores | `dev-val` a partir das bases públicas |
| EXP-033G, EXP-035 | mantidos; o acervo vem de E4 |
| L-01 (pedir ao BRESSAY) | sai do plano ativo (era pedido individual); o BRESSAY fica `EXPERIMENT_ONLY` e na revisão periódica |

---

## 11. Riscos

| Risco | Mitigação |
| :--- | :--- |
| Ler NC como liberado sem cumprir as condições | regra do projeto escrita (§3); revisão se o modelo de doações mudar |
| SA obrigar a licença dos pesos | licenciar o leitor sob CC BY-NC-SA quando houver dado SA/NC-SA no manifesto |
| Rótulo de licença errado na fonte | conferência por amostra; evidência guardada |
| Reempacotamento com licença mais frouxa | vale a da fonte original |
| Fonte histórica/inglesa não ajudar | E3 mede antes de escalar |
| Estourar os 100 GB | tetos por pasta; medição antes de cada lote; parar e perguntar |
| Dado pessoal em documentos modernos | preferir acervos históricos e bases publicadas; filtro e `PENDING_REVIEW` |
| Termos mudarem | cópia datada dos termos; revisão periódica |
| Item rejeitado já ensinado a um modelo | manifesto + contaminação + retreino (§6) |

---

## Fontes consultadas (2026-11-20)

Licenças: [CC — NC](https://wiki.creativecommons.org/NonCommercial_interpretation),
[Pitt](https://pitt.libguides.com/openlicensing/cc-non-comerical),
[lista CC (proposta, 2006)](https://lists.ibiblio.org/sympa/arc/cc-licenses/2006-01/msg00035/pdflZDb4RzeKF.pdf) ·
Fontes: [By the People](https://crowd.loc.gov/about/), [LC Labs](https://labs.loc.gov/work/experiments/crowd),
[Signal (mar/2026)](https://blogs.loc.gov/thesignal/2026/03/),
[Teklia](https://huggingface.co/collections/Teklia/datasets-atr-line-level-65f171515df9c72ff26f655a),
[HTR-United](https://htr-united.github.io/catalog.html),
[IISH](https://b2find.eudat.eu/dataset/b4137503-c8e1-5816-852e-4446dd652b13),
[iForal](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11856379/),
[BRESSAY](https://tc11.cvc.uab.es/datasets/BRESSAY_1),
[IAM](https://fki.tic.heia-fr.ch/databases/iam-handwriting-database),
[Wikisource](https://en.wikisource.org/wiki/Wikisource:ProofreadPage),
[Wikimedia API](https://www.mediawiki.org/wiki/Wikimedia_APIs/Access_policy),
[READ-ICDAR2017](https://zenodo.org/record/835488),
[GNHK](https://github.com/GoodNotes/GNHK-dataset),
[Europeana — transcrições](https://leuven2012.europeana.eu/post/transcriptions-subtitles-and-enrichments-sharing-our-copyright-approach),
[Smithsonian](https://transcription.si.edu/about),
[Biblioteca Nacional](https://www.gov.br/bn/pt-br/servicos/reproducao-do-acervo-1) ·
Práticas e lei (v1): [OpenAI](https://help.openai.com/articles/7842364),
[Anthropic](https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler),
[Common Crawl](https://commoncrawl.org/faq), [LAION](https://laion.ai/blog/relaion-5b/),
[PL 2338](https://institutobrasileiro.ia.br/artigos/pl-2338-2023-onde-esta-o-projeto-de-lei-de-ia/),
[FGV](https://direitosp.fgv.br/sites/default/files/arquivos/inovacao-e-tutela-juridica-a-utilizacao-de-obras-protegidas-por-direitos-autorais-para-o-treinamento-de-inteligencia-artificial-generativa-de-imagens.pdf),
[Reed Smith](https://www.reedsmith.com/articles/entertainment-media-guide-to-ai-three-years-on/text-data-mining-in-the-eu/),
[Ballard Spahr](https://www.ballardspahr.com/insights/alerts-and-articles/2026/10/third-circuit-addresses-fair-use-in-ai-training-but-leaves-generative-ai-questions-unresolved).

A pesquisa da versão 1 que continua valendo está nos apêndices A e B.

---

## Apêndice A — O que as grandes empresas documentam (da v1)

Só o que está publicado por elas ou por quem audita.

| Prática | O que é documentado | Fonte |
| :--- | :--- | :--- |
| Web pública com robô identificado | OpenAI coleta com o **GPTBot** e aceita opt-out por `robots.txt` ou bloqueio de IPs; Anthropic usa o **ClaudeBot**, honra `robots.txt`, não contorna CAPTCHA e diz honrar um sinal legível por máquina de "não treinar" (rascunho IETF) | [OpenAI](https://help.openai.com/articles/7842364); [Anthropic](https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler) |
| Exclusões na coleta | OpenAI declara excluir fontes com paywall, agregadores de dado pessoal, conteúdo que viola políticas, quem fez opt-out e domínios reincidentes em pirataria (lista do USTR) | [OpenAI](https://openai.com/index/approach-to-data-and-ai); [resumo de treino](https://cdn.openai.com/pdf/gpt-5-5-eu-ai-act-public-summary-of-training-content.pdf) |
| Parcerias e licenças | citadas, sem detalhes nem valores (não divulgados, segundo o índice de transparência de Stanford) | [FMTI OpenAI](https://crfm.stanford.edu/fmti/December-2025/company-reports/OpenAI_FinalReport_FMTI2025.html); [FMTI Anthropic](https://crfm.stanford.edu/fmti/December-2025/company-reports/Anthropic_FinalReport_FMTI2025.html) |
| Dados sintéticos | uso crescente declarado | [OpenAI](https://openai.com/index/approach-to-data-and-ai) |
| Transparência (UE) | resumo público do conteúdo de treino e política de respeito ao opt-out (AI Act, art. 53) | [IAPP](https://iapp.org/news/a/the-eu-ai-act-and-copyrights-compliance) |
| Datasets abertos de imagem | LAION/DataComp vêm do Common Crawl; o Re-LAION-5B removeu 2.236 links de abuso infantil com listas de hash; ~700 milhões de duplicatas estimadas no original | [LAION](https://laion.ai/blog/relaion-5b/); [arXiv 2506.17185](https://arxiv.org/pdf/2506.17185) |
| Common Crawl | CCBot honra `robots.txt` e `Crawl-delay`; o arquivo antigo é anterior a muitos opt-outs | [FAQ](https://commoncrawl.org/faq) |
| Origem lícita (EUA) | *Bartz v. Anthropic*: treino com livros foi uso justo, cópias piratas não (acordo de US$ 1,5 bi); *Thomson Reuters v. Ross* (3º Circuito, set/2026): não foi uso justo para ferramenta não generativa concorrente | [Ballard Spahr](https://www.ballardspahr.com/insights/alerts-and-articles/2026/10/third-circuit-addresses-fair-use-in-ai-training-but-leaves-generative-ai-questions-unresolved); [Cleary](https://www.clearyiptechinsights.com/2026/01/the-open-questions-in-u-s-generative-ai-copyright-litigation/) |
| Consentimento em escala | Common Voice: contribuidores dedicam ao domínio público (CC0) uma vez, ao contribuir | [Common Voice](https://common-voice.github.io/community-playbook/sub_pages/cc0waiver_process.html) |

**Reproduzível por nós:** robô identificado que honra `robots.txt` e sinais de "não treinar"; nada de paywall,
login ou CAPTCHA; política por fonte; deduplicação por hash; procedência por item; lista de remoção; resumo do
conteúdo de treino por modelo; sintético como base. **Desconhecido:** proporções, filtros internos, valores.

## Apêndice B — Quadro jurídico (da v1)

| Situação | Brasil | EUA | UE |
| :--- | :--- | :--- | :--- |
| Domínio público (BR: em regra 70 anos após a morte do autor), CC0, CC-BY | livre (com atribuição no CC-BY) | livre | livre |
| Público na internet, sem licença | **sem exceção de mineração** na Lei 9.610/98 (leitura dominante: art. 29 e art. 46 restritivo) | uso justo possível, caso a caso; origem lícita pesa | art. 4 da Diretiva DSM: permitido se o titular não reservou por meio legível por máquina |
| Projeto de lei | PL 2338/2023 (exceção para pesquisa, opt-out, remuneração) **parado na Câmara** | — | — |
| Termos da plataforma | contrato à parte; cumprir sempre | idem | idem |
| Dado pessoal | LGPD: dado público continua pessoal | — | GDPR |

Fontes: [FGV Direito SP](https://direitosp.fgv.br/sites/default/files/arquivos/inovacao-e-tutela-juridica-a-utilizacao-de-obras-protegidas-por-direitos-autorais-para-o-treinamento-de-inteligencia-artificial-generativa-de-imagens.pdf);
[Congresso em Foco](https://congressoemfoco.com.br/noticia/11743/inteligencia-artificial-direitos-autorais-e-mineracao-de-dados-um-dialogo-necessario);
[PL 2338](https://institutobrasileiro.ia.br/artigos/pl-2338-2023-onde-esta-o-projeto-de-lei-de-ia/);
[Reed Smith](https://www.reedsmith.com/articles/entertainment-media-guide-to-ai-three-years-on/text-data-mining-in-the-eu/).
Consequência para o plano: no Brasil, material só "público" sem licença fica em `PENDING_REVIEW`.
