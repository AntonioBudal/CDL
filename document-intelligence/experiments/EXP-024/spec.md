# EXP-024 — Melhoria Contínua Autônoma do Organizador e da Pós-Correção da Digitalização (especificação)

**Created**: 2026-10-28 · **Status**: `RASCUNHO PARA REVISÃO` (fase F01; código só depois da revisão do usuário)

**Input**: pedido do usuário (2026-10-28). O Organizador das 4 seções (EXP-023, feature 089) e a leitura da
digitalização (ADR-008, feature 086) devem melhorar sozinhos com o uso. Os sinais são estes:
- as edições que o leitor já faz ao revisar;
- o contexto do livro e do acervo;
- o comportamento na tela;
- um clique de conferência;
- uma nota opcional de 1 a 5.

Tudo em Python puro, local e sem dependência pesada no produto.

**Plano e tarefas:** [plan.md](./plan.md) e [tasks.md](./tasks.md). **Estado:** [STATE.md](./STATE.md).

---

## 1. Pergunta e escopo

Um motor adaptativo leve consegue que **cada página revisada** deixe o Organizador e a pós-correção da leitura
melhores para **aquele leitor e aquele livro**, sem regredir abaixo do modelo estático nem com feedback ruidoso? E
isso cabendo em ≤ 25 ms por atualização e em poucas centenas de KB de estado por usuário?

**Dentro do escopo:**
- **Organizador:** centróides, pesos $W, \mathbf{b}$, temperatura $\beta$, transição $T_{\text{user}}$, pistas de
  referência e seleção do que mostrar para conferir;
- **leitura:** pós-correção por palavra (léxico de 1ª parte e confusões pessoais), limiar de `low_confidence` e
  curadoria de pares para o ajuste fino em lote do EXP-018.

**Fora do escopo:**
- treinar o leitor (o ajuste fino segue em lote, offline, como no EXP-018);
- qualquer mudança no Leitorum (vem depois, por ADR-011 e Spec Kit próprio);
- schema novo do LDF;
- modelo generativo ou serviço externo.

## 2. Ponto de partida (fatos medidos)

| Fato | Fonte | Consequência para o EXP-024 |
| :--- | :--- | :--- |
| `V4` estático: Macro-F1 0,934 (limpo) e 0,825 (CER 25 %) nas páginas fictícias | EXP-023 | linha de base fixa; `organizer-v1.json` é a âncora $W_0$ |
| D-usuário: **0,497**; `references` **0,29** (listas, "Título — Autor", links) | EXP-023, N = 3 | a maior lacuna é o formato real de referência |
| `V6` (centróides do usuário, κ = 25): 0,644 | EXP-023, N = 3 | ganho grande, sem base estatística |
| montagem a frio dos centróides: ~6 s para 500 estudos | EXP-023 | exige acumulação incremental por estudo salvo |
| validação zerou τ, ω (ordem) e α (propagação) | EXP-023 | a ordem global não ajuda; a ordem **de um leitor** pode ajudar |
| leitor em produção: CER ~27 % em manuscrito, ~77–80 % de erro em acentos | EXP-009/014/015 | restaurar acentos com léxico do próprio leitor é o alvo mais barato |
| correção lexical genérica (`wordfreq`, CC-BY-SA): CER 34,4 → 33,8 % | EXP-011 | léxico genérico ajuda pouco **e** não serve ao produto (licença) |
| 16 / 50 / 150 páginas de ajuste fino: CER 19,6 / 15,8 / 13,7 % | EXP-018 | pares limpos do próprio uso valem ouro, se forem confiáveis |
| `human_corrections` (RFC 6902) sobre `recognition.lines` e `semantics.sections` | LDF 2.0 | serve às correções de leitura; **não** às 4 seções do Estudo (§6.1) |

## 3. Sinais disponíveis no produto (o que existe de verdade)

| Sinal | Onde nasce | Já existe no Leitorum? |
| :--- | :--- | :--- |
| leitura bruta × texto revisado | `source_response` × seções salvas (086) | **sim**, em todo estudo digitalizado |
| sugestão do Organizador × seções salvas | resposta do `/organize` × `POST /api/studies` (089) | a resposta **não é guardada**; precisaria ser enviada junto do salvamento |
| movimentos "Mover para…" e "Voltar para texto único" | tela de revisão (089) | acontecem só no navegador |
| livro, autor, capítulo e estudos anteriores do livro | banco | **sim** |
| nota de 1 a 5 | — | **não existe**; seria nova e opcional |

Daí uma restrição de desenho: tudo que o EXP-024 aprende precisa vir de sinais que o produto possa enviar num
salvamento, sem rastreio de tela contínuo. O pacote de feedback de cada página (§6.2) é pequeno e explícito.

## 4. As 6 estratégias

### 4.1 Matriz comparativa

| Estratégia | Impacto esperado | CPU por evento | Atrito para o leitor | Risco de envenenamento | Mitigação |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **E1** diff de revisão | alto (é o rótulo principal) | O(tamanho da página): alinhamento | **nenhum** | médio: reescrita autoral confundida com correção | filtro de ruído de edição (§5.1); suporte mínimo |
| **E2** contexto do livro e do acervo | alto em `references` e em acentos | O(palavras do estudo) | nenhum | baixo: são textos do próprio leitor | contrações por contagem; nada de fora do acervo |
| **E3** comportamento | médio (gate e pesos) | O(1) | nenhum | médio: salvar sem revisar parece aprovação | peso baixo para "não mexeu"; reversão bloqueia |
| **E4** 1 clique de conferência | alto por clique | O(N · 16) por clique (re-decodificação) | **baixo**: o leitor já confere a lista | baixo: clique é rótulo explícito | o clique fica como restrição, não como verdade global |
| **E5** atualização online e pós-correção pessoal | alto a médio prazo | ≤ 25 ms por estudo salvo (meta H5) | nenhum | **alto** sem travas: deriva, esquecimento | âncora L2, projeção, portão-sombra e rollback (§5) |
| **E6** nota 1–5 e curadoria | baixo direto; alto para o ajuste fino | O(1) | opcional | médio: nota contraditória | a nota só modula o peso do "não mexeu"; nunca anula correção explícita |

### 4.2 E1 — Aprendizado implícito por diff de revisão

**Organizador.** Ao salvar uma página organizada, cada unidade sugerida $u_i$ (com seção $\hat y_i$) é procurada
no texto salvo:

1. **Localização:** busca exata do trecho normalizado nas 4 seções salvas. Se não achar, alinhamento aproximado
   por `difflib` com razão mínima $\rho_{\min}$ (calibrada).
2. **Desfecho por unidade:**
   - **mantida** ($y^*_i = \hat y_i$);
   - **movida** ($y^*_i \ne \hat y_i$);
   - **editada** (achada com razão entre $\rho_{\min}$ e 1);
   - **apagada** (não achada).
3. **Rótulos:**
   - movida e mantida viram pares $(\mathbf{x}_i, y^*_i)$ com peso $\omega_i$ (§4.7);
   - editada vira rótulo de seção só se a edição for de leitura (§5.1), não de reescrita;
   - apagada não vira rótulo.
4. **Ordem da página:** a sequência $y^*$ na ordem original das unidades alimenta $T_{\text{user}}$ (E5).
   Estudos importados prontos **não** alimentam $T_{\text{user}}$: as colunas salvas não guardam a ordem das
   unidades na página.

**Leitura.** Para cada página digitalizada, as linhas de `source_response` são alinhadas às linhas do texto
revisado. Primeiro por linha (`difflib` sobre linhas), depois por caractere, com Levenshtein e retroceder
(*backtrace*). O resultado são operações locais com contexto:
- substituição, inserção e apagamento de 1 a 2 caracteres;
- trocas de palavra inteira (palavra lida → palavra corrigida).

**Serialização.** Correções de leitura viram `human_corrections` do LDF 2.0 sobre `recognition.lines`
(`{"op": "replace", "path": "/text", "value": …}`), com `author`, `timestamp` e `reason` (`ocr-fix`). Os
movimentos de seção vão para um JSON Patch RFC 6902 sobre o **documento de resposta do Organizador**
(`organizer-result/1`), por exemplo `{"op": "replace", "path": "/segments/7/section", "value": "references"}`. A
§6.1 explica por que não no LDF.

### 4.3 E2 — Adaptação contextual por livro e acervo

1. **Léxico de 1ª parte, por escopo:**
   - contagens de palavras (forma acentuada e forma dobrada) do título, do autor e dos capítulos do livro;
   - contagens dos estudos salvos do mesmo livro, com peso maior para `concepts` e `references`;
   - contagens do acervo do usuário;
   - sementes MIT do projeto: protótipos do EXP-023 e listas de pistas.

   Sem `wordfreq` nem outro léxico CC-BY-SA.
2. **Centróides hierárquicos.** A mistura de três níveis tem encolhimento bayesiano em cascata:

   $$\mathbf{c}_j = \operatorname{norm}\!\Big((1-\rho_u-\rho_b)\,\mathbf{c}_j^{\text{seed}} + \rho_u\,\hat{\mathbf{c}}_j^{\text{user}} + \rho_b\,\hat{\mathbf{c}}_j^{\text{book}}\Big),\quad \rho_u = (1-\rho_b)\frac{n_u}{n_u+\kappa_u},\quad \rho_b = \frac{n_b}{n_b+\kappa_b}\cdot\phi_b$$

   - $\phi_b \le 1$ limita o peso do livro;
   - $n_u$ e $n_b$ são contagens ponderadas de unidades;
   - os $\hat{\mathbf{c}}$ são somas incrementais normalizadas (E5).
3. **Formatos reais de referência.** São duas camadas:
   - **(a) pistas fixas novas** (MIT, escritas para o projeto):
     - item de lista Markdown com "Título — Autor" ou "Autor — Título";
     - link Markdown `[texto](url)`;
     - linha com URL;
     - "Título (Autor, ano)";
     - "Autor. *Título*".
   - **(b) assinatura de forma aprendida:** cada linha vira uma forma abstrata, como `- Ttt — Ttt` ou
     `[ttt](url)`, com classes de token: maiúscula, minúscula, dígito, travessão, marcador, URL e aspas. Um
     contador por escopo estima $\log \frac{P(\text{forma}\mid\text{references})}{P(\text{forma}\mid\text{outras})}$,
     com suavização. Esse escore entra como uma pista nova, `ref_shape_user`.

   As pistas novas entram como colunas novas de $W$, com **peso 0 na âncora** $W_0$. Só o aprendizado online lhes
   dá peso, e o $W_0$ do EXP-023 continua exatamente reproduzível.

### 4.4 E3 — Sinais comportamentais

| Sinal | Leitura | Efeito |
| :--- | :--- | :--- |
| "Voltar para texto único" e salvar sem organizar | rejeição forte da sugestão | nenhuma atualização positiva dessa página; contador de rejeição do usuário |
| retenção $\varrho$ = fração de caracteres sugeridos mantidos na mesma seção | aprovação implícita graduada | modula o peso das unidades mantidas |
| itens com `review: true` movidos ou confirmados | rótulo explícito | peso máximo |
| salvar sem nenhuma edição, com itens "conferir" ignorados | ambíguo (aprovou ou não olhou?) | peso baixo das mantidas ($\omega_{\text{keep,blind}}$) |
| taxa de rejeição do usuário alta | sugestão não serve a esse leitor | o Organizador passa a marcar mais itens para conferir (margem sobe), sem mudar $W$ |

### 4.5 E4 — Aprendizado ativo cirúrgico de 1 clique

1. **Ordem da lista "Seções para conferir".** O escore de informação por unidade é

   $$g_i = H(\boldsymbol\gamma_i)\cdot\Big(1 + \sum_{k \in \mathcal N(i)} S_{ik}\Big)$$

   - $H$ é a entropia da marginal;
   - o fator de acoplamento conta quantos vizinhos coesos o rótulo de $i$ arrasta.

   Comparação: a margem do EXP-023 (linha de base), só entropia e entropia × acoplamento.
2. **Re-decodificação.** O clique "Mover $u_i$ para $j$" vira restrição rígida ($A_{i\cdot} = -\infty$ fora de
   $j$, como um cabeçalho) e o Viterbi roda de novo, em $O(N\cdot 16)$. Vizinhos acoplados mudam junto.
3. **Variante E4b.** Antes de re-decodificar, um passo local de $W$ com o rótulo clicado (peso alto, só para a
   página). Mede se "aprender no mesmo minuto" corrige mais vizinhos que só a restrição.
4. **Medida:** Macro-F1 e caracteres corrigidos depois de $k = 0, 1, 2, 3$ cliques, com o leitor simulado
   respondendo os itens na ordem mostrada.

### 4.6 E5 — Atualização online incremental e pós-correção pessoal

**Estado por usuário (e por livro dentro dele):**
- somas esparsas dos vetores L0 por seção, mais as contagens ponderadas. A atualização custa O(unidades do estudo),
  independente do histórico. Há poda determinística quando passa de $2K$ (maior magnitude; desempate por hash);
- $\Delta W = W - W_0$ e $\Delta\mathbf{b}$, com $\log\beta$;
- contagens de transição $C_{ab}$ e de início $C_a$;
- léxico, confusões pessoais e calibração de `low_confidence` (pós-correção);
- contadores de comportamento e snapshot "último bom" para rollback.

**Algoritmo de atualização dos pesos (decisão de Categoria 2):**

| Critério | Passive-Aggressive multiclasse (PA-II) | **Regressão logística online com âncora L2** |
| :--- | :--- | :--- |
| Probabilidades calibradas (margem de "conferir", ECE) | não: otimiza margem, não *log-loss* | **sim**: mesma perda do treino do EXP-023 |
| Passo diante de rótulo ruidoso | agressivo: corrige tudo até a margem (limitado por $C$) | proporcional ao erro de probabilidade |
| Ancoragem em $W_0$ | ad hoc | natural: termo $\frac{\mu}{2}\lVert W - W_0\rVert_F^2$ (MAP com prior gaussiano em $W_0$) |
| Peso por rótulo $\omega_i$ | multiplica $C$ | multiplica o gradiente |
| Custo | O(4d) | O(4d) |

**Escolha: regressão logística online com âncora L2 e projeção.** Ela preserva a calibração de que dependem a
margem de "conferir" e a ordem do E4. O PA entra só como braço comparativo na calibração, se a regressão logística
não ganhar.

Para cada rótulo $(\mathbf{x}_i, y_i, \omega_i)$:

$$\mathbf{p} = \operatorname{softmax}\!\big((W\mathbf{x}_i+\mathbf{b})/\beta\big),\qquad
W \leftarrow W - \eta_t\Big[\tfrac{\omega_i}{\beta}(\mathbf{p}-\mathbf{e}_{y_i})\mathbf{x}_i^\top + \mu\,(W - W_0)\Big]$$

- $\mathbf{b}$ é atualizado do mesmo modo.
- Depois do passo vem a **projeção** na bola $\lVert W - W_0\rVert_F \le \Delta_{\max}$.
- $\eta_t = \eta_0/\sqrt{1 + t/t_0}$.
- **Temperatura:** passo em $\log\beta$ pelo gradiente da NLL, preso em $[\beta_0/1{,}5,\ 1{,}5\,\beta_0]$.

**Transição do usuário:**

$$T^{\text{user}}_{ab} = \log\frac{C_{ab} + \alpha_T\,\pi^0_{ab}}{C_a + \alpha_T},\qquad
T = (1-\zeta)\,T^{0} + \zeta\, T^{\text{user}},\quad \zeta = \frac{n_T}{n_T+\kappa_T}$$

$T^0$ é a uniforme do EXP-023, com τ = ω = 0.

**Pós-correção da leitura (por palavra, canal ruidoso):**
- **candidatos:**
  - palavras do léxico de escopo a distância ≤ 2, pelo índice de apagamentos do EXP-011;
  - variantes com o mesmo esqueleto sem acento (restauração de acento);
- **escore:**

  $$\operatorname{score}(c) = \log P_{\text{lex}}(c \mid \text{livro}, \text{usuário}) + \log P_{\text{canal}}(w_{\text{lido}} \mid c)$$

  - o canal usa a matriz de confusão **pessoal**, com prior de Dirichlet no modelo global do EXP-015;
  - troca só se o escore passar o "manter" por uma margem $\theta$ calibrada;
- **regra de proteção:** nenhuma troca em palavra que já está no léxico do escopo com contagem ≥ $m$;
- **limiar de `low_confidence` por usuário:** um logístico de $P(\text{linha editada} \mid \text{confiança})$,
  aprendido das edições. O limiar fica onde a fração marcada ≤ 25 % e a revocação das linhas editadas é máxima.

### 4.7 E6 — Nota opcional de 1 a 5 e curadoria para o ajuste fino

**Peso de aprendizado.** A nota $r = (\text{nota}-1)/4 \in [0,1]$ modula **só** o peso das unidades mantidas sem
edição, a aprovação implícita:

$$\omega_{\text{keep}} = \omega_0 \cdot h(r),\qquad h(r) = \begin{cases} 0{,}5 & \text{sem nota} \\ r & \text{com nota}\end{cases}$$

- Unidades movidas, editadas ou clicadas têm $\omega = 1$, com ou sem nota: o leitor fez o trabalho.
- **Sem nota, o aprendizado continua**, com o padrão 0,5.

**Curadoria de pares (linha, texto revisado) para o EXP-018.** Um par entra no lote só se:
- a edição foi classificada como leitura (§5.1), com distância normalizada $\le d_{\text{cur}}$;
- a linha tem pelo menos 5 caracteres;
- a página não foi rejeitada (E3) e não teve nota 1 ou 2 sem correção;
- não há duplicata.

**Medida:** precisão (fração dos pares curados cujo texto revisado é a transcrição verdadeira) e cobertura.

## 5. Travas de segurança (Safe Continual Learning)

1. **Filtro de ruído de edição.** Para cada linha, a distância normalizada $d = \operatorname{lev}(\text{lido},
   \text{revisado}) / \max(|\cdot|)$ e a razão de tokens alinhados $a$:
   - **correção de leitura** se $d \le \theta_{\text{ocr}}$ e $a \ge a_{\min}$;
   - **reescrita autoral** se $d > \theta_{\text{rw}}$, ou se há palavras novas sem par no lido;
   - entre os dois: **ambígua**, que não alimenta confusões nem curadoria.

   Uma confusão só entra na matriz pessoal depois de **suporte mínimo** $s_{\min}$ em pelo menos 2 linhas.
2. **Reward gating.** A página não gera atualização positiva quando:
   - houve reversão;
   - a nota foi 1 ou 2 sem nenhuma correção;
   - a retenção ficou abaixo de $\varrho_{\min}$ sem movimentos que expliquem.

   Correções explícitas continuam valendo.
3. **Âncora L2 e projeção:** $\lVert W - W_0\rVert_F^2 \le \Delta_{\max}^2$ sempre (§4.6).
4. **Portão-sombra (Shadow Sanity Gate).** Depois de cada atualização de $W, \mathbf{b}, \beta, T$:
   - os protótipos-semente são avaliados em memória (só classificação, vetores em cache);
   - a cada 10 atualizações, também um conjunto-canário congelado de páginas fictícias (decodificação completa).

   Se o Macro-F1 cair mais que $\varepsilon$ em relação ao snapshot "último bom", a atualização é **desfeita**
   (rollback para o snapshot) e registrada como rejeitada.
   - $\varepsilon$ é tolerante de propósito: o estilo do leitor pode legitimamente se afastar da semente.
   - O portão pega mudança **destrutiva**, não adaptação. $\varepsilon$ é calibrado no regime R3 da validação.
5. **Isolamento:** o estado é sempre indexado por `user_id`. Nada de um usuário entra no de outro (teste dedicado).
6. **Privacidade do estado:**
   - o estado guarda n-gramas por *hash* e palavras do próprio acervo. Fica tão privado quanto os estudos:
     nunca em log, nunca fora da máquina;
   - no D-usuário deste experimento, **só em memória**, descartado no fim.

## 6. Decisões de Categoria 2

### 6.1 Onde registrar os movimentos de seção

O LDF 2.0 tem `semantics.sections` com papéis de página (`summary`, `concept`, `quote`…), sem `explanation` nem
`references`. Cada seção aponta para regiões da imagem, e o schema 2.0 está congelado (ADR-004).

**Decisão:**
- correções de **leitura** vão como `human_corrections` do LDF 2.0, que já serve;
- **movimentos de seção** vão como RFC 6902 sobre o documento `organizer-result/1`, um formato do experimento.

Se o EXP-024 for adotado, o ADR-011 propõe um LDF 2.1 com papéis das 4 seções do Estudo e âncoras de texto. Mudar
o schema é feature própria, não deste experimento.

### 6.2 Pacote de feedback por página (contrato do experimento)

```json
{
  "schema": "leitorum-feedback/1",
  "user_id": "u-teste-1", "book_id": "b-teste-1", "page_id": "p-0007",
  "organizer": {
    "suggested": {"segments": [{"index": 0, "start": 0, "end": 51, "section": "summary", "review": false}]},
    "reverted": false,
    "clicks": [{"index": 4, "to": "references"}]
  },
  "reading": {"source_lines": ["…"], "line_confidence": [0.81]},
  "saved": {"summary": "…", "explanation": "…", "concepts": "…", "references": "…"},
  "rating": null
}
```

Tudo é texto fictício no experimento. No produto, o pacote só existe no servidor do próprio usuário.

### 6.3 Pesos de combinação dos sinais (valores iniciais; calibrados na F04)

| Rótulo | $\omega$ inicial |
| :--- | ---: |
| clique de conferência (E4) | 1,0 |
| unidade movida pelo leitor (E1) | 1,0 |
| unidade mantida, página revisada, sem nota | $0{,}5\,\omega_0$ |
| unidade mantida, com nota $r$ | $r\,\omega_0$ |
| unidade mantida, página salva sem nenhuma edição | $\omega_{\text{keep,blind}} = 0{,}1$ |
| página revertida, ou nota 1–2 sem correção | 0 |

## 7. Hipóteses (limiares confirmados na validação, antes do teste)

- **H1 — o Organizador aprende com sinais implícitos.**
  - No regime R1, depois de 40 páginas de adaptação, o Macro-F1 nas páginas *holdout* de cada perfil fica
    **≥ 8 pontos** acima do V4 estático, na média dos perfis.
  - O F1 de `references` no perfil de referências não-ABNT sobe **≥ 20 pontos**.
- **H2 — a pós-correção pessoal reduz o erro de leitura sem estragar o que está certo.**
  - Depois de 40 páginas, o CER *holdout* cai **≥ 15 % relativos** e o erro em acentos **≥ 30 % relativos**.
  - Pelo menos **99,5 %** das palavras já certas são preservadas.
  - A curadoria tem precisão **≥ 0,95**.
- **H3 — robustez sob ruído.**
  - No regime R3 (20 % de feedback ruidoso), o motor completo **nunca** fica mais de 1 ponto abaixo do V4 em
    nenhum $t$.
  - Mantém **≥ 70 %** do ganho do R1.
  - O mesmo motor **sem as travas** é medido para mostrar o que elas evitam.
- **H4 — 1 clique vale mais com ordem por informação e re-decodificação.** O ganho de Macro-F1 do 1º clique com
  E4 (entropia × acoplamento e re-decodificação) é **≥ 2×** o ganho do 1º clique com a ordem por margem e sem
  re-decodificação.
- **H5 — custo.**
  - Atualização por estudo salvo: p95 **≤ 25 ms**, com o portão-sombra rápido.
  - Acréscimo na organização: **≤ 5 ms** de p95 sobre o V4.
  - Estado persistido: **≤ 512 KB** por usuário com 500 estudos em até 20 livros.
  - Reconstrução por *replay* de 500 estudos: **≤ 2 s**.
- **Portão de adoção (ADR-011):**
  - H1, H3 e H5 confirmadas;
  - nenhum vazamento de privacidade;
  - no D-usuário, o motor **não pior** que o V4 estático.

  Com N pequeno, o D-usuário é alerta, como no EXP-023.

## 8. Avaliação

### 8.1 Conjuntos

| Conjunto | Conteúdo | Uso |
| :--- | :--- | :--- |
| **D-longitudinal** | pelo menos 3 perfis de anotação × 2–3 livros fictícios cada. Um perfil copia o estilo do D-usuário: referências em lista Markdown, "Título — Autor" e links. Outro tem ordem própria (por exemplo, conceitos primeiro). Páginas escritas e congeladas com SHA-256 **antes** do motor. Por perfil: fluxo de **adaptação** ($t = 1\dots40$) e páginas ***holdout*** separadas; fluxos de **validação** e de **teste** com livros e sorteios distintos | curvas, ablações, estresse |
| **ruído de leitura** | modelo por caractere do EXP-015 (CER 10 % e 25 %) mais **confundidores recorrentes por escritor**, sintéticos e declarados (o modelo do EXP-015 é global, sem escritor) | pós-correção |
| **canário** | 8 páginas fictícias congeladas, fora de tudo | portão-sombra |
| **D-usuário** | estudos reais do usuário, avaliação **prequencial** (estudo $t$ previsto com o estado aprendido de $1\dots t-1$, por `user_id`, em ordem de criação) | alerta, só números |

**D-usuário sem atalho.** Os estudos reais viram pseudo-páginas na ordem canônica das colunas. Por isso
$T_{\text{user}}$ fica **desligado** nessa avaliação: aprender a ordem canônica seria ganho falso. Para leitura,
só entram estudos com `source_response` de digitalização, e o N sai no relatório.

### 8.2 Simulador do leitor (regimes)

| Regime | Comportamento simulado |
| :--- | :--- |
| **R1** implícito puro | corrige trechos marcados "conferir" com probabilidade alta e os não marcados com probabilidade menor; corrige palavras lidas com probabilidade maior nas linhas de baixa confiança; sem nota |
| **R2** implícito + nota | R1, mais nota coerente com a qualidade da sugestão |
| **R3** estresse | R2 com **20 %** de páginas ruidosas: nota contraditória, página salva sem revisar e reescrita autoral livre de frases |

As probabilidades de correção e a relação confiança × erro da linha seguem o medido na feature 086: limiar 0,75,
20,7 % marcadas, CER 43,5 % nas marcadas contra 23,7 % nas demais. O simulador é determinístico por semente.

### 8.3 Métricas

- **Organizador:** Macro-F1 (por caractere), F1 de `references`, WindowDiff e % de caracteres a mover, em
  $t = 1, 5, 10, 20, 40$.
- **Leitura:** CER, WER, erro em acentos, % de palavras certas preservadas, precisão e cobertura da curadoria, e
  precisão e revocação do `low_confidence`.
- **Custo:** latência da atualização e da organização, e tamanho do estado em KB.

### 8.4 Ablações

- **Escada cumulativa:**

  | Passo | Conteúdo |
  | :--- | :--- |
  | V4 | estático |
  | + E1 | rótulos do diff → centróides do usuário e $W$ online |
  | + E2 | livro, léxico e formas de referência |
  | + E3/E6 | pesos e gates |
  | + E4 | ordem e re-decodificação, medidas com $k$ cliques |
  | completo | travas do E5 |

- **Leave-one-out:** o completo menos cada componente.
- **Leitura:** nenhuma, só léxico, só confusões, os dois, e com e sem filtro de ruído (sob R3).

### 8.5 Protocolo

1. Escrever e congelar o D-longitudinal e o canário (SHA-256) **antes** do motor.
2. Implementar o motor e o simulador.
3. Calibrar **só** nos fluxos de validação e gravar `artifacts/thresholds.json` **antes** de abrir o teste.
4. Abrir o teste uma vez.
5. D-usuário com as travas da §9.

## 9. Privacidade, licenças e recursos

- **D-usuário:**
  - cópia pela API de backup do SQLite numa pasta temporária, com origem e cópia em `mode=ro`, apagada no
    `finally`;
  - **só números agregados**: nenhum título, palavra, trecho ou n-grama legível em saída, log ou arquivo;
  - o estado aprendido fica só em memória.
- **Qual banco ler fica para o usuário decidir** (ver STATE.md, divergência 2):
  - a origem congelada `caderno-leitura-0.1/backend/data/caderno.db`, citada no pedido;
  - ou o banco ativo `D:\Leitorum\db\caderno.db`, mais atual.

  Nos dois casos, só leitura via API de backup.
- **Código e licenças:**
  - motor em Python puro (biblioteca padrão);
  - NumPy e scikit-learn só no ambiente `experiments/EXP-023/envs/organizer` (`uv run --frozen --project …`);
  - léxicos só de 1ª parte e sementes MIT;
  - zero emojis.
- **Recursos:** sem download. Menos de 100 MB em disco e menos de 500 MB de RAM.

## 10. Riscos e limites

- **Circularidade:** o mesmo agente escreve as páginas, o simulador e o motor. Mitigações:
  - dados congelados antes do código;
  - teste aberto uma vez;
  - o D-usuário como checagem externa.

  Ainda assim, **os números do D-longitudinal são um teto otimista**, não uma previsão do produto.
- **O leitor simulado é uma hipótese.** Taxas de correção reais só virão de uso real com consentimento.
- **N do D-usuário pequeno.** Hoje são poucos estudos; o veredito sobre texto real continua dependendo de mais uso.
- **Deriva lenta:** muitas atualizações pequenas e coerentes podem levar $W$ longe da âncora sem que o portão
  perceba. A projeção limita o total, e a curva longa ($t = 40$) mede.
- **Estado como dado pessoal:** os n-gramas por *hash* podem ser recuperados por dicionário. No produto, o estado é
  tratado como os próprios estudos: exportação, exclusão de conta e backup juntos.
