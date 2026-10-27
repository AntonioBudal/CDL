# EXP-023 — Organização Automática do Texto nas 4 Seções do Estudo (pesquisa, especificação e plano)

**Created**: 2026-10-27 · **Status**: `APPROVED` — aprovado pelo usuário em 2026-10-27, com as decisões da §11; execução das fases F01 a F05 só dentro de `document-intelligence/`

**Input**: pedido do usuário (2026-10-27, Parte 2). Leitores escrevem no caderno de forma corrida, sem os cabeçalhos
`Resumo / Explicação / Conceitos / Referências` que o parser determinístico do Leitorum
(`caderno-leitura-0.1/backend/app/services/import_parser.py`) exige. Hoje, na tela `/digitalizar`, o texto inteiro
vai para uma única seção. O pedido é um botão **"Organizar nas 4 seções"** que segmenta e distribui o texto entre
`summary`, `explanation`, `concepts` e `references`. A função deve servir também para a importação.

**Restrições do usuário**:
- sem IA de terceiros e sem LLM generativo local;
- pipeline própria, vetorial e relacional, em Python e CPU;
- determinística, auditável, 100 % local;
- menos de 200 ms por página;
- licenças abertas (Apache-2.0, MIT, BSD) e zero emojis.

**Relação com o roadmap**: absorve a parte de texto do `EXP-004` (classificação semântica), restrita às 4 seções
canônicas do Estudo. Diagramas e títulos ficam fora.

---

## 1. Pergunta e hipóteses

Uma pipeline leve, sem modelo generativo, consegue distribuir o texto de uma página de anotações entre as 4 seções
com qualidade suficiente para o leitor só **conferir**, em vez de redistribuir tudo à mão? Isso inclui texto com o
ruído de leitura do manuscrito (24–27 % de CER no leitor de licença livre, ADR-008).

As hipóteses abaixo são propostas. Os limiares absolutos serão confirmados depois de medir as linhas de base (§8),
antes de olhar o conjunto de teste.

- **H1 — Híbrido vale mais que cada parte.** O vetor híbrido (regras ponderadas + léxico de n-gramas de
  caracteres) supera o melhor componente isolado em pelo menos 5 pontos de Macro-F1 ponderado por caracteres, no
  texto limpo e com CER de 25 %.
- **H2 — A matriz relacional reduz a fragmentação sem custar acerto.** A decodificação com transições e coesão
  (§5) reduz o WindowDiff em pelo menos 20 % relativos contra a classificação independente de cada segmento. O
  Macro-F1 não pode cair mais de 1 ponto.
- **H3 — Custo.** p95 ≤ 200 ms por página em Python puro, na máquina de referência, sem dependência nova no
  backend. Construir os centróides do usuário a frio leva ≤ 2 s para 500 estudos.
- **H4 — Calibração local.** Somar os centróides tirados dos estudos do próprio usuário melhora o Macro-F1 em
  pelo menos 3 pontos no conjunto do usuário (§8.1, D-usuário). A medida só acontece se o usuário autorizar.
- **Portão de produto (proposta):** Macro-F1 ≥ 0,70 no texto limpo e ≥ 0,60 com CER de 25 %. Abaixo disso, o
  botão não vai para o produto. Acima, vai sempre como sugestão revisável.

## 2. Visão geral da pipeline

```text
texto da revisão (+ linhas com bbox, se vierem da digitalização)
  │
  ├─ 0. cabeçalhos explícitos? (reaproveita a detecção do import_parser) → restrições rígidas
  ├─ 1. segmentação: linhas físicas → blocos → sentenças (unidades u_1 … u_N)
  ├─ 2. vetor de cada unidade:  x_i = [ f_i (estrutura/discurso) ; s_i (similaridade léxica aos 4 centróides) ]
  ├─ 3. afinidade:  A = log softmax(W x_i + b) / temperatura          → A ∈ R^{N×4}
  ├─ 4. coesão:     S (vizinhança + similaridade + geometria)          → S ∈ R^{N×N}
  │                 Ã = propagação de rótulos de A sobre S
  ├─ 5. decodificação: Viterbi com T ∈ R^{4×4} e custo de troca ponderado por S
  │                 + marginais (forward-backward) → confiança por unidade
  └─ 6. montagem: cada seção = suas unidades na ordem original, texto sem nenhuma alteração
```

**Invariantes**, todos testados em 100 % dos casos:
- **Sem perda:** a concatenação de todas as unidades, nas posições originais, reconstrói o texto de entrada. Os
  deslocamentos `start` e `end` apontam para o texto recebido.
- **Sem reescrita:** nenhuma palavra é alterada, resumida ou criada. O sistema só **move** trechos.
- **Determinismo:** a mesma entrada e a mesma versão de pesos dão a mesma saída. Nada é sorteado em produção.
- **Sem dependência pesada no backend:** a inferência roda em Python puro, com pesos num JSON versionado. NumPy e
  scikit-learn só existem no ambiente do experimento, para treinar e exportar.

## 3. Segmentação pós-leitura (unidades de análise)

O texto do leitor chega com uma linha física por linha da folha. A pontuação às vezes falta, e marcadores visuais
como travessão, seta, bullet e recuo indicam estrutura. A segmentação tem três níveis, com regras explícitas e
parâmetros calibrados.

### 3.1 Linhas físicas → blocos (fusão)

Para cada par de linhas consecutivas $(\ell_k, \ell_{k+1})$, a pipeline calcula um **escore de continuação**
$c_k \in [0,1]$ com um logístico de poucos pesos sobre as pistas abaixo. As linhas se fundem no mesmo bloco se
$c_k \ge 0{,}5$.

| Pista | Fonte | Efeito |
| :--- | :--- | :--- |
| $\ell_k$ termina sem `. ! ? ; :` | texto | a favor de continuar |
| $\ell_k$ termina com hífen de quebra (`…pala-`) | texto | continua e **junta a palavra** só na análise; o texto original não muda |
| $\ell_{k+1}$ começa com minúscula | texto | a favor de continuar |
| $\ell_{k+1}$ começa com marcador (`-`, `–`, `—`, `•`, `*`, `→`, `->`, `=>`, `1.`, `a)`) | texto | **quebra rígida** |
| $\ell_k$ curta e terminada em `:` (rótulo, como "Ideias principais:") | texto | quebra; o rótulo abre bloco |
| linha em branco entre as duas | texto | quebra rígida |
| intervalo vertical $g_k = (y^{top}_{k+1} - y^{bot}_k)/\tilde p$, com $\tilde p$ = passo mediano das linhas da página | LDF/bbox | $g_k > 1{,}6$ indica quebra de parágrafo |
| recuo $\Delta x_k = (x^{left}_{k+1} - x^{left}_k)/w_{texto}$ | LDF/bbox | recuo de primeira linha ou mudança de nível indica quebra |
| largura de $\ell_k$ / largura útil da página | LDF/bbox | linha que não chega perto da margem direita indica fim de parágrafo |
| confiança média de leitura da linha | motor | pistas textuais de linhas incertas pesam menos |

**Sem geometria** (importação, ou texto editado que não casa mais com as linhas lidas), valem só as pistas
textuais. Quando o texto foi editado, as linhas atuais são casadas com as originais por alinhamento de sequência
(`difflib`, Python puro). Linhas casadas herdam `bbox`; linhas novas ficam com as pistas geométricas neutras.

### 3.2 Blocos → sentenças

Dentro de cada bloco, a divisão acontece em `[.!?]` seguido de espaço e maiúscula, ou em `;` quando os dois
lados têm verbo. Uma lista de abreviações impede cortes errados: `p.`, `pp.`, `cf.`, `ed.`, `org.`, `vol.`, `v.`,
`n.`, `cap.`, `fig.`, `et al.`, `op. cit.`, `ibid.`, `id.`, `Sr.`, `Sra.`, `Dr.`, `Prof.`, `séc.`, iniciais de nome.

Algumas linhas viram **unidade inteira, sem divisão interna**:
- uma referência bibliográfica completa (padrão ABNT, §4.1);
- uma citação entre aspas que ocupa a linha toda;
- um par `termo: definição`.

### 3.3 Granularidade e limites

- **Unidade de classificação:** a sentença.
- **O bloco não é forçado a uma única seção.** Ele entra como acoplamento forte em $S$ (§5.3). Assim, um parágrafo
  que abre com uma frase de síntese e segue explicando pode se dividir, mas só se a evidência for clara.
- **Tamanho:** páginas típicas têm de 10 a 60 unidades. O teto é de 400 unidades por pedido, cobrindo textos
  importados longos. Acima disso, a resposta é `413`.

## 4. Vetor de representação $\mathbf{x}_i$

$$\mathbf{x}_i = \big[\, \mathbf{f}_i \;;\; \mathbf{s}_i \,\big] \in \mathbb{R}^{d_f + 4}$$

### 4.1 $\mathbf{f}_i$ — estrutura, morfologia e discurso (~45 dimensões)

Todas as palavras-pista são comparadas **sem acento e sem caixa**. O leitor erra 80 % dos acentos (EXP-009). Para
palavras com 5 letras ou mais, a comparação tolera distância de edição 1, com o índice de deleções já usado no
EXP-011. Cada família abaixo vira contagens normalizadas pelo tamanho da unidade, mais um indicador binário.

| Seção | Famílias de pistas (exemplos; listas completas no artefato de pesos) |
| :--- | :--- |
| `references` | **aspas** (`"…"`, `“…”`, `«…»`) e fração do texto entre aspas; **paginação** `\bp{1,2}\.\s*\d+(\s*[-–]\s*\d+)?`; **autor-data** `\(([A-ZÁ-Ú][A-ZÁ-Ú'\-]+)(\s+et al\.)?,\s*\d{4}[a-z]?(,\s*p{1,2}\.\s*\d+)?\)`; **referência ABNT** `^[A-ZÁ-Ú]{2,},\s+[A-ZÁ-Ú]` + ano + `.`; marcadores `cf.`, `apud`, `ver também`, `In:`, `Disponível em`, `op. cit.`, `ibid.`, `ed.`, `editora`, `ISBN`, URL; ano isolado entre 1500 e 2099 |
| `concepts` | **termo + separador** `^\s*[^\s:]{1,40}(\s+[^\s:]+){0,3}\s*[:—–=]\s+`; **verbos definicionais** (é, são, significa, define-se, denomina-se, consiste em, refere-se a, entende-se por, chama-se, trata-se de, conceito de, noção de); itens curtos de lista; poucos verbos finitos; razão entre o tamanho do termo e o da definição |
| `summary` | **marcadores de síntese** (em suma, em resumo, resumindo, em síntese, de modo geral, a ideia central, a tese, o capítulo trata/aborda/apresenta, o autor defende/argumenta/afirma/sustenta/conclui); verbos de relato na 3ª pessoa; posição no começo da página |
| `explanation` | **conectivos causais e explicativos** (porque, pois, portanto, logo, assim, por isso, já que, uma vez que, visto que, dessa forma, consequentemente, ou seja, isto é, por exemplo, no entanto, contudo, entretanto, embora); **reflexão em 1ª pessoa** (eu, acho, penso, percebo, me parece, concordo, discordo); perguntas; sentenças longas |
| forma (todas) | log do número de palavras; fração de dígitos, de maiúsculas e de pontuação; tem `:`; começa com marcador; nível de recuo; posição relativa na página (0–1); índice do bloco; confiança média de leitura |

Os pesos dessas pistas **não** são escolhidos à mão no fim. As listas são escritas à mão, mas a matriz $W$ que
combina as pistas é aprendida por regressão logística (§4.3). Cada peso continua inspecionável.

### 4.2 $\mathbf{s}_i$ — similaridade léxica aos 4 centróides

Cada unidade vira um vetor esparso $\mathbf{l}_i$ de **n-gramas de caracteres de 3 a 5**, dentro dos limites de
palavra, sem acento e em minúsculas. O vetor é gerado por *hashing* em $2^{18}$ posições, com peso TF-IDF
sublinear e norma L2. O componente léxico entra no classificador como 4 números, um cosseno por seção:

$$s_{ij} = \cos\big(\mathbf{l}_i,\ \mathbf{c}_j\big), \qquad j \in \{\text{sum}, \text{exp}, \text{con}, \text{ref}\}$$

O centróide $\mathbf{c}_j$ vem dos protótipos-semente (§6.1) e, quando autorizado, dos estudos do usuário (§6.2).

Esse desenho tem duas vantagens:
- $W$ não precisa ser retreinado quando os centróides mudam. A calibração local muda só $\mathbf{s}_i$.
- O vetor léxico nunca precisa de vocabulário fixo, porque o *hashing* dispensa dados de treino para existir.

**Comparação das abordagens léxicas**, a medir no experimento:

| Abordagem | Robustez a erro de leitura | Custo em Python puro | Licença dos dados | Papel no EXP-023 |
| :--- | :--- | :--- | :--- | :--- |
| **L0 — n-gramas de caracteres com hashing + TF-IDF**, IDF dos protótipos-semente | alta: um caractere errado afeta poucos n-gramas | ~1 ms por página | nenhum corpus externo; protótipos MIT do projeto | **escolha inicial** |
| L1 — L0 projetado por SVD/LSA (100–300 dimensões) | alta | precisa de NumPy, ou de uma matriz de projeção em JSON (alguns MB) | exige corpus de fundo; só domínio público ou CC-BY, e CC-BY fica `NEEDS VALIDATION` | braço comparativo |
| L2 — BM25 contra vocabulários-semente por seção | baixa em palavra inteira; média com n-gramas | ~1 ms | protótipos do projeto | braço comparativo (ablação das regras) |
| L3 — embeddings estáticos leves em português (fastText com subpalavras, model2vec) | média ou alta (subpalavras) | exige NumPy e arquivo de 100 MB a 1 GB | fastText pt é CC-BY-SA, **fora** do critério; model2vec e similares ficam `NEEDS VALIDATION` caso a caso | só se uma opção passar na licença e ganhar ≥ 3 pontos sobre L0 |

**Recomendação:** começar com L0. Ele é o único que satisfaz ao mesmo tempo Python puro, nenhum corpus externo e
tolerância a ruído de caracteres. L1 e L3 só entram se a medição mostrar ganho real que pague o custo de
dependência e de licença.

### 4.3 Afinidade $A$ (classificador calibrado)

$$P_{ij} = \operatorname{softmax}_j\!\Big(\tfrac{1}{\beta}\,(W\mathbf{x}_i + \mathbf{b})\Big), \qquad A_{ij} = \log P_{ij}, \qquad W \in \mathbb{R}^{4 \times (d_f+4)}$$

- **Treino de $W$ e $\mathbf{b}$:** regressão logística multinomial com regularização L2, só na divisão de treino
  (§8).
- **Temperatura $\beta$:** ajustada na validação para minimizar o erro de calibração (ECE). Assim, as margens
  usadas na interface significam algo.
- **Exportação:** cerca de 200 números em JSON.

## 5. Matriz relacional

Classificar cada sentença sozinha picota parágrafos. A matriz relacional junta três peças.

### 5.1 Afinidade categoria × segmento: $A \in \mathbb{R}^{N \times 4}$

É a da §4.3. As **restrições rígidas** entram em $A$:
- **Cabeçalho explícito** detectado com a lista de sinônimos do `import_parser`: as unidades até o próximo
  cabeçalho ficam com $A_{ij} = -\infty$ fora da seção do cabeçalho.
- **Referência ABNT completa:** recebe um bônus grande em `references`, mas não absoluto, para que um erro do
  padrão possa ser vencido por evidência forte.

### 5.2 Transição entre seções: $T \in \mathbb{R}^{4 \times 4}$

$$T_{ab} = \log \frac{\exp\big(\tau\,[a=b] + \omega\, O_{ab}\big)}{\sum_{b'} \exp\big(\tau\,[a=b'] + \omega\, O_{ab'}\big)}$$

- $\tau$ é a **inércia**: ficar na mesma seção é o caso comum.
- $O$ é uma **ordem branda** com +1 para os passos "naturais" `summary → explanation → concepts → references` e 0
  para os demais.
- Há também uma distribuição inicial $\pi$, com leve preferência por `summary` no começo, e uma final, com leve
  preferência por `references` no fim.

**Por que só dois parâmetros e não 16 contagens:** a ordem real de quem anota à mão é desconhecida. Estimar 16
transições de páginas sintéticas faria $T$ aprender o gerador de dados, e não o leitor. Com $\tau$ e $\omega$,
ajustados na validação e com $\omega$ limitado, a ordem fica um desempate e não uma imposição. Uma página que
começa por conceitos continua possível.

### 5.3 Coesão contextual: $S \in \mathbb{R}^{N \times N}$

$S$ é esparsa, só com vizinhos até $w$ posições de distância (proposta: $w = 3$):

$$S_{ik} = \underbrace{e^{-\,g_{ik}/\sigma_g}}_{\text{proximidade}} \cdot \underbrace{\big(1 + \eta\,[\text{mesmo bloco}]\big)}_{\text{bloco}} \cdot \underbrace{\max\!\big(0, \cos(\mathbf{l}_i, \mathbf{l}_k)\big)}_{\text{similaridade}}, \qquad |i-k| \le w$$

- $g_{ik}$ é o intervalo vertical acumulado entre as unidades, em passos de linha, tirado do LDF/bbox.
- Sem geometria, $g_{ik}$ é a contagem de linhas em branco entre as unidades mais 0,5 por quebra de bloco.

### 5.4 Decodificação: propagação seguida de Viterbi

**Etapa 1 — relaxação (propagação de rótulos, Zhou et al. 2004).** Com $\hat S = D^{-1/2} S D^{-1/2}$:

$$F = (1-\alpha)\,(I - \alpha \hat S)^{-1} P, \qquad \tilde A_{ij} = \log \frac{F_{ij}}{\sum_{j'} F_{ij'}}$$

A inversa nunca é calculada. São 10 iterações de $F \leftarrow \alpha \hat S F + (1-\alpha) P$. Como $S$ tem no
máximo $2w$ vizinhos por linha, cada iteração custa $O(N \cdot w \cdot 4)$. Essa etapa leva a evidência de
vizinhos parecidos, inclusive não adjacentes, para dentro da afinidade. Um exemplo é uma lista de definições
interrompida por um comentário.

**Etapa 2 — Viterbi com custo de troca dependente da posição.** A cadeia é linear e exata:

$$\hat{\mathbf{y}} = \arg\max_{\mathbf{y}} \; \pi_{y_1} + \sum_{i=1}^{N} \tilde A_{i,y_i} + \sum_{i=2}^{N} \Big( T_{y_{i-1} y_i} - \lambda\, S_{i-1,i}\,[y_{i-1} \ne y_i] \Big)$$

Trocar de seção entre duas unidades muito coesas custa caro. Trocar numa quebra de bloco com intervalo grande
custa pouco. A complexidade é $O(N \cdot 4^2)$.

**Confiança.** O forward-backward na mesma cadeia dá a marginal $\gamma_{ij}$. A margem
$m_i = \gamma_{i,(1)} - \gamma_{i,(2)}$ separa as unidades firmes das que a interface marca "conferir a
seção".

**Parâmetros livres** (8, todos ajustados na validação e exportados):
- $\beta$, $\tau$ e $\omega$;
- $\alpha$ e $\lambda$;
- $\sigma_g$, $\eta$ e $w$.

**Custo estimado.** Para $N = 60$, são cerca de 15 mil operações aritméticas na decodificação, mais o *hashing*
das unidades. A expectativa é de 10 a 40 ms em Python puro, muito abaixo dos 200 ms. Isso é uma estimativa a
confirmar em H3.

## 6. Calibração: partida a frio e acervo do usuário

### 6.1 Partida a frio (zero-shot)

O projeto inclui protótipos-semente escritos para ele, com licença MIT e conteúdo fictício e neutro:
- 60 a 80 frases curtas por seção, em estilo de anotação de leitura, com variação de registro (telegráfico,
  corrido, lista);
- as listas de pistas da §4.1.

Esses protótipos geram $\mathbf{c}_j^{seed}$ e o IDF do L0. Eles **nunca** entram em avaliação.

### 6.2 Enriquecimento local com os estudos do usuário (few-shot, opcional)

No produto, a pipeline pode usar os estudos que o próprio usuário já salvou como exemplos rotulados. Cada coluna
(`summary`, `explanation`, `concepts`, `references`) é a seção de referência.

1. **Segmentar** cada coluna com o mesmo segmentador e somar os vetores L0 por seção. A soma é podada para os 5
   mil n-gramas de maior peso.
2. **Misturar com o encolhimento bayesiano**:

   $$\mathbf{c}_j = (1-\rho_j)\,\mathbf{c}_j^{seed} + \rho_j\,\mathbf{c}_j^{user}, \qquad \rho_j = \frac{n_j}{n_j + \kappa}$$

   Aqui $n_j$ é o número de unidades do usuário na seção $j$, e $\kappa \approx 50$ é ajustado em H4. Com poucos
   estudos, a semente domina. Com muitos, prevalece o estilo do usuário.
3. **Prioris de seção:** a proporção de texto em cada coluna também ajusta levemente $\mathbf{b}$ (log das
   frequências, com peso limitado).

**Isolamento e privacidade:**
- Só entram estudos **do próprio usuário**, por consulta filtrada por `user_id`. Estudos compartilhados por amigos
  e estudos na lixeira ficam de fora.
- Os centróides ficam **só em memória**, num cache por usuário invalidado pela contagem e pela última
  `updated_at` dos estudos. Nunca são gravados em disco ou no banco (sem migração), nunca vão para logs e nunca
  saem da máquina.
- Teto de 500 estudos mais recentes.

**Ressalva de domínio.** Muitos estudos do acervo vieram de fichamentos importados, que costumam ter estilo
diferente da anotação manuscrita. O encolhimento limita esse efeito. H4 mede se ajuda de fato antes de virar
padrão.

**Fora do escopo:** aprender com as correções feitas depois de organizar. Isso exigiria guardar o histórico de
movimentações, com tabela nova. Hoje, um estudo salvo com as seções já corrigidas realimenta os centróides de
forma implícita.

## 7. Integração com o Leitorum (proposta para a feature de produto seguinte)

### 7.1 Onde roda

- **Código:** `backend/app/services/organizer/`, em Python puro (segmentador, pistas, L0, decodificação). Assim
  funciona também na importação, sem depender do motor opcional da digitalização.
- **Artefato:** `backend/app/data/organizer/organizer-v1.json`, com $W$, $\mathbf{b}$, os 8 parâmetros, as listas
  de pistas, os centróides-semente podados, a versão e o SHA-256. Ele é produzido pelo EXP-023 e copiado para o
  produto pela spec da feature.
- **Banco:** nenhuma migração.

### 7.2 Contrato: `POST /api/imports/organize`

Fica junto da pré-visualização da importação, porque o insumo é texto. A tela de digitalização manda também as
linhas lidas.

Requisição:

```json
{
  "text": "O capítulo trata da formação do hábito de leitura.\nLeitura ativa: ler fazendo perguntas ao texto.\nIsso importa porque fixa as ideias.\nADLER, Mortimer. Como ler um livro. 2010.",
  "lines": [
    { "text": "O capítulo trata da formação do hábito de leitura.", "bbox": [120, 140, 1480, 210], "confidence": 0.91 }
  ],
  "page": { "width": 1653, "height": 2339 },
  "use_my_studies": true
}
```

- `lines` e `page` são opcionais. Eles vêm só da digitalização, porque o preview da 086 passaria a devolver `bbox`
  por linha (campo novo e aditivo no contrato da 086).
- `use_my_studies` liga a calibração da §6.2.

Resposta `200`:

```json
{
  "sections": {
    "summary": "O capítulo trata da formação do hábito de leitura.",
    "explanation": "Isso importa porque fixa as ideias.",
    "concepts": "Leitura ativa: ler fazendo perguntas ao texto.",
    "references": "ADLER, Mortimer. Como ler um livro. 2010."
  },
  "segments": [
    { "index": 0, "start": 0, "end": 51, "section": "summary", "confidence": 0.82, "margin": 0.64, "review": false },
    { "index": 1, "start": 52, "end": 100, "section": "concepts", "confidence": 0.93, "margin": 0.88, "review": false }
  ],
  "explicit_headings": false,
  "calibration": { "mode": "seed+user", "user_units": 412 },
  "engine": { "name": "leitorum-organizer", "version": "1", "sha256": "…" },
  "elapsed_ms": 18,
  "warnings": [{ "code": "suggestion", "message": "Distribuição automática: confira as seções antes de salvar." }]
}
```

- **Montagem das seções:** cada `sections.X` reúne os trechos atribuídos, na ordem original, separados por quebra
  de linha. O texto vem idêntico ao original.
- **Erros:** `413`, `422` para texto vazio e `401`.
- **Banco:** não grava nada. Só **lê** os estudos do usuário quando `use_my_studies` vale `true`.

### 7.3 Experiência na tela de revisão (`DigitizeNotebookView.vue`)

1. **Modo texto único** (o atual): um editor e a escolha de uma seção. Ao lado da escolha aparece o botão
   **"Organizar nas 4 seções"**.
2. **Ao organizar:**
   - a escolha de seção some, e aparecem **4 editores rotulados** (Resumo, Explicação, Conceitos, Referências),
     reaproveitando o `StudyEditorFields.vue` da importação;
   - no celular, os editores viram abas;
   - os trechos com `review: true` aparecem numa lista "Seções para conferir", no mesmo padrão de "Linhas para
     conferir". Cada item tem um seletor **"Mover para…"**, que tira o trecho de um editor e o põe no outro,
     enquanto ele não tiver sido editado.
3. **"Voltar para texto único"** restaura **exatamente** o texto de antes de organizar, guardado na memória da
   tela. Se os 4 editores foram alterados, a tela pede confirmação antes de descartar.
4. **Ao salvar:**
   - as 4 seções vão no `POST /api/studies`;
   - o `source_response` continua sendo a leitura bruta da máquina, intocada;
   - organizar nunca salva sozinho.
5. **Importação (`ImportView.vue`):** quando o parser não encontra cabeçalhos (todo o texto em `unassigned_text`),
   aparece o mesmo botão para distribuir esse texto nas 4 seções.
6. **Design:** segue o Roadmap 0.9. São tokens semânticos, nenhum emoji, alvos de 44 px, foco visível, aviso
   permanente de "sugestão automática, confira" e a marcação de "conferir" com texto e ícone, não só com cor.

**Recomendação de ordem para o leitor:** organizar **depois** de corrigir a leitura. Com 25 % de CER, as
palavras-pista erram muito, e o texto corrigido rende uma distribuição bem melhor. O botão funciona antes, mas a
tela sugere corrigir primeiro.

## 8. Método de avaliação

### 8.1 Conjuntos de dados

| Conjunto | Origem e licença | Uso | Cuidados |
| :--- | :--- | :--- | :--- |
| **D-semente** | escrito para o projeto, MIT, fictício | centróides e IDF iniciais | nunca avaliado |
| **D-sintético** | ~150 páginas de anotação fictícias, escritas **antes** de fixar as regras e congeladas com SHA-256. Estilos variados: corrido, telegráfico, lista, com e sem pontuação, ordens diferentes das seções | treino, validação e teste (60/20/20 por página) | risco de circularidade: quem escreve as regras também escreve os dados. Mitigação: escrita e congelamento antes do código, divisão por página, teste aberto uma vez só |
| **D-prata** | páginas compostas de trechos de artigos de acesso aberto em português sob **CC-BY**. Exemplos: resumo → `summary`; parágrafo de discussão → `explanation`; lista de referências → `references`; glossários → `concepts` | teste extra de generalização | licença de cada fonte conferida (`NEEDS VALIDATION` até lá); só para experimento, fora do Git; `concepts` é a seção mais fraca aqui |
| **D-usuário** (opcional) | os estudos do próprio usuário, a partir de uma **cópia** do banco gerada pelo backup do app. Para cada estudo com pelo menos 2 colunas preenchidas, as colunas viram uma pseudo-página sem cabeçalhos | o teste mais realista (o estilo do próprio leitor) e H4, por validação deixando um estudo de fora | **só com autorização explícita**. O script abre a cópia em modo leitura e imprime só números agregados. Ninguém lê os textos, nem o agente; o banco ativo não é tocado |

**Linhas físicas simuladas.** Para avaliar a fusão da §3.1 sem fotos de caderno, o texto dos conjuntos é quebrado
em linhas de 40 a 65 caracteres, com quebras de parágrafo, recuos e marcadores. As caixas são geradas por esse
traçado, com ruído. A validação geométrica real espera fotos de caderno, como já registrado no EXP-022.

**Ruído de leitura.** O EXP-015 tem as leituras brutas do leitor original e as referências do BRESSAY. Delas sai
um **modelo de erro por caractere**: substituições, inserções, apagamentos e perda de acento. Só as estatísticas
são guardadas, nenhum texto. Esse modelo é aplicado aos conjuntos com CER-alvo de 10 % e 25 %.

### 8.2 Métricas

- **Macro-F1** das 4 seções por unidade, ponderado por caracteres, porque mover um parágrafo longo errado custa
  mais ao leitor. O relatório traz também a versão não ponderada, a precisão, a revocação e a matriz de confusão
  por seção.
- **Coerência de fronteira:** $P_k$ (Beeferman et al., 1999) e **WindowDiff** (Pevzner & Hearst, 2002) sobre a
  sequência de seções, além da **taxa de fragmentação**, a razão entre o número de trocas de seção previstas e
  as do gabarito.
- **Esforço do leitor:** a fração de caracteres que o leitor precisaria mover para corrigir.
- **Calibração:** ECE das marginais e precisão das unidades com $m_i$ alto, para provar que "firme" quer dizer
  firme.
- **Segmentação:** F1 das fronteiras de unidade contra o gabarito do D-sintético, com tolerância de 1 linha.
- **Custo:** latência p50 e p95 por página em Python puro, tempo de montagem dos centróides do usuário e memória.

### 8.3 Linhas de base e ablações

| ID | Variante |
| :--- | :--- |
| B0 | classe majoritária |
| B1 | `import_parser` atual (só funciona com cabeçalhos; mede o problema) |
| B2 | só pistas $\mathbf{f}_i$, cada unidade isolada |
| B3 | só léxico L0 ($\mathbf{s}_i$), isolado |
| V1 | híbrido $[\mathbf{f}_i; \mathbf{s}_i]$, isolado (H1) |
| V2 | V1 + Viterbi com $T$ |
| V3 | V2 + coesão $S$ no custo de troca |
| V4 | V3 + propagação (pipeline completa) (H2) |
| V5 | V4 com L1 ou L3 no lugar de L0 (braços comparativos) |
| V6 | V4 + centróides do usuário (H4, só D-usuário) |

Cada variante roda em limpo, CER 10 % e CER 25 %, com e sem geometria.

### 8.4 Protocolo

1. Escrever e congelar D-semente e D-sintético, com SHA-256 registrado no relatório.
2. Implementar a pipeline em Python puro e o treino offline em NumPy e scikit-learn (BSD), no ambiente do
   experimento.
3. Ajustar $W$, $\mathbf{b}$ e os 8 parâmetros **só** em treino e validação.
4. **Fixar os limiares das hipóteses** com base nas linhas de base de validação e registrá-los no relatório
   **antes** de abrir o teste.
5. Abrir o teste uma vez. Rodar D-prata e, se autorizado, D-usuário.
6. Relatório só com números e exemplos **fictícios**, com ADR se houver adoção.

## 9. Tarefas e fases (commits `FNN(document-inteligence) [EXP-023] …`)

| Fase | Entregas | Commit |
| :--- | :--- | :--- |
| F01 | esta especificação aprovada | F01 |
| F02 | D-semente, D-sintético congelados e gerador de linhas simuladas; modelo de ruído (só estatísticas); D-prata com licenças conferidas | F02 |
| F03 | pipeline de referência em Python puro (segmentador, pistas, L0, A, T, S, propagação, Viterbi, forward-backward), testes de invariantes (sem perda, determinismo) e medição de latência | F03 |
| F04 | treino e ajuste (W, β, τ, ω, α, λ, σ_g, η, w); limiares das hipóteses registrados; exportação de `organizer-v1.json` | F04 |
| F05 | teste, ablações, braços L1 e L3 se houver opção de licença válida, D-usuário se autorizado; `RESULTS.md`, benchmark JSON e ADR-010 se adotado | F05 |
| depois | feature de produto no Leitorum (Spec Kit próprio): endpoint, serviço, artefato, `bbox` no preview da 086, tela de 4 editores e importação | `feature — …` |

**Recursos:** sem download de modelo no caminho principal. Menos de 50 MB em disco e menos de 500 MB de RAM no
treino. Nenhum ambiente pesado novo: NumPy e scikit-learn num ambiente `uv` próprio do experimento.

## 10. Riscos

- **Ruído de leitura:** com 25 % de CER, pistas de palavra inteira falham com frequência. Mitigações:
  - comparação sem acento e com tolerância de edição;
  - n-gramas de caracteres;
  - peso menor para pistas de linhas com baixa confiança;
  - orientação de organizar depois de corrigir.
- **Domínio desconhecido:** não há anotações reais de caderno rotuladas. D-sintético tem viés de autoria e
  D-prata é texto acadêmico. Só o D-usuário mede o estilo real, e ele depende de autorização.
- **Ambiguidade conceitual:** uma mesma frase pode ser síntese e explicação ao mesmo tempo. O teto de
  concordância humana não é 100 %. A interface trata tudo como sugestão.
- **Páginas curtas:** com 3 a 5 unidades, as prioris pesam muito. A confiança baixa aparece como "conferir".
- **Citação dentro de frase:** "Leitura ativa (ADLER, 2010): …" é conceito com citação. A política proposta é a
  da decisão 2 abaixo.

## 11. Decisões do usuário (aprovação de 2026-10-27)

1. **D-usuário: aprovado com travas de privacidade.**
   - O script copia o banco com a **API de backup do SQLite**. A origem é aberta em modo somente leitura
     (`mode=ro`) e a cópia vai para uma pasta temporária descartável. A cópia também é aberta em `mode=ro` e é
     apagada no fim, em qualquer desfecho.
   - O banco ativo nunca é modificado nem usado diretamente na avaliação.
   - É proibido imprimir, registrar em log, serializar ou gravar qualquer texto, título, n-grama legível ou trecho
     dos estudos. A saída tem só números agregados: estudos elegíveis, Macro-F1, WindowDiff, $P_k$, ECE e latência.
   - Elegíveis são os estudos com pelo menos 2 das 4 seções preenchidas. Com `N` pequeno, a métrica sai com o `N`
     e sem falhar, e D-sintético e D-prata passam a ser os decisores principais.
2. **Citações dentro de frases: aprovada a recomendação.**
   - `references` recebe só referências bibliográficas completas, citações diretas em unidade ou linha própria e
     remissões autônomas (`cf.`, `apud`).
   - Autor-data e página embutidos numa frase de conceito ou explicação ficam na seção da frase.
   - Linhas `p. 42 — comentário do leitor` contam como anotação (`explanation`).
3. **Calibração com os estudos do usuário no produto:** **desligada por padrão.** Ela só passa a padrão na
   feature futura do Leitorum se o braço V6 (H4) mostrar ganho de pelo menos 3 pontos de Macro-F1 sem piorar as
   seções minoritárias.

O código do Leitorum fica intocado até existirem o `RESULTS.md` e o `organizer-v1.json` validados.
