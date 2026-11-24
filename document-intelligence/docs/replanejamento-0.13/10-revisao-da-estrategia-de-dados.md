# Revisão da estratégia de dados — v3 (depois do EXP-031P)

**Data:** 2026-11-23 · **Status:** `APROVADO v3` pelo usuário em 2026-11-23 · **Revisa:** a
[estratégia de dados v2](./09-estrategia-de-aquisicao-de-dados.md), §8 (plano E1–E6) · **Motivo:** o
[EXP-031P](../../experiments/EXP-031P-quais-fontes-ajudam/report.md) suspendeu a E4.

> **EXP-044 (2026-11-24):** a BFL é a primeira fonte da internet que ensina o domínio (BRESSAY 29,9 % → 23,0 %,
> acentos 76 % → 32 %), mas piora o GNHK em 5,4 pontos; a E4' não é disparada. Próximo passo proposto: misturar a
> BFL com inglês e foto para proteger o GNHK ([report](../../experiments/EXP-044-portugues-perto-do-dominio/report.md), §6).

> **Aviso.** Análise técnica com fontes, não parecer jurídico. Onde a licença é incerta, o texto diz.

---

## 0. Por que revisar

O EXP-031P treinou o leitor com 8 mil linhas de cada grupo de fontes abertas e mediu em pessoas que ele nunca viu.

| Treino (mesmo orçamento) | BRESSAY teste |
| :--- | ---: |
| nenhum | 29,9 % |
| latino moderno (francês, norueguês) | 28,9–30,3 % |
| histórico (latim, francês antigo) | 46,9 % |
| sintético em português | 38,1 % |
| **redações em português (BRESSAY treino, EXP-014)** | **13,6 %** |

**O domínio pesa mais que o volume.** Coletar em escala fontes de outra língua e outra época não ajuda; o que
ajuda é manuscrito moderno em português. A v2 previa isso como risco (§11: "fonte histórica/inglesa não ajudar")
e a regra da spec mandou rever.

## 1. O que fica e o que muda

**Fica, sem mudança:** as decisões do usuário de 2026-11-20 (não comercial, só internet, custo zero, 100 GB no
D:, nunca contornar bloqueio), as cinco situações do catálogo, a rastreabilidade por ciclo, o catálogo de
procedência (F-DI-13.03) e a régua do EXP-031P.

**Muda:**

1. **Sai a E4 como estava** (conectores completos para Teklia e HTR-United). As 16 mil linhas já coletadas ficam
   no catálogo (0,8 GB) como dado de mistura, para proteger o inglês e a foto (§4.3).
2. **Entra uma busca dirigida ao domínio:** português, manuscrito, de preferência moderno. Cada fonte nova passa
   pela mesma régua antes de qualquer escala.
3. **Volta a pergunta aos autores, só onde a licença conflita** (§3). A decisão 6 da v2 dispensa autorização
   individual quando a licença pública **já permite**; quando os sinais da própria fonte se contradizem, perguntar
   é o caminho limpo e gratuito.

## 2. Fontes em português encontradas (2026-11-23)

| Fonte | O que é | Transcrição | Licença (evidência) | Situação proposta |
| :--- | :--- | :--- | :--- | :--- |
| **BRESSAY** | redações de estudantes brasileiros; 1.000 páginas, 1.000 pessoas, ~30 mil linhas | por linha | **três sinais**: CC BY 4.0 no Zenodo; README do arquivo: "non-commercial research and teaching purposes only"; página do TC-11 citada como CC BY-NC-SA 3.0 (fora do ar nesta consulta) | `EXPERIMENT_ONLY` (como hoje) + **pergunta aos autores** |
| **BFL** (Brazilian Forensic Letter, UFPR, 2008) | 315 pessoas × 3 cópias de **uma mesma carta de 131 palavras**; 945 páginas A4, cinza, 300 dpi | **nenhuma**, mas o texto da carta é fixo e conhecido | página da UFPR: selo CC BY 4.0 **e** a frase "may be used for non-commercial research" | `EXPERIMENT_ONLY` + **pergunta aos autores** |
| LHTR.br (UFF, 2023) | a BFL segmentada em linhas (16.744), com ~200 linhas anotadas por símbolo | ~200 linhas | não encontrada no artigo (OSF) | `PENDING_REVIEW`; pouco útil (a BFL de origem rende mais) |
| **TraPrInq** (Inquisição portuguesa) | 6.417 páginas manuscritas em português, séc. XVI–XIX, 6,7 GB | por linha (PAGE, Transkribus) | **CC BY 4.0** no Zenodo, acesso aberto | `APPROVED` |
| Modelo TraPrInq (Kraken) | leitor treinado nessas páginas (93 % de acerto de caractere no domínio dele) | — | CC BY 4.0 | `APPROVED`, como possível professor ou ponto de partida (a medir) |

**Não achado:** um conjunto de manuscrito moderno em português **ou espanhol** com licença aberta e sem
restrição de pesquisa. O espanhol moderno aberto só aparece em caracteres e palavras soltas (CC BY-NC) ou em
acervos históricos.

**Sobre a BFL.** Ela não tem transcrição por linha, mas todos copiaram o mesmo texto. Transcrevemos a carta uma
vez, a partir da imagem de exemplo pública. Depois, o detector de linhas do produto separa as linhas e um
alinhamento forçado pelo leitor distribui o texto conhecido entre elas, descartando as de baixa confiança.
Isso rende até ~12–16 mil linhas de 315 pessoas modernas. **Limite:** o vocabulário é de 131 palavras. Por isso
ela entra como parte da mistura, nunca sozinha, e nunca é usada para medir.

## 3. Pergunta aos autores (decisão do usuário)

Duas mensagens curtas, uma para o grupo do BRESSAY e uma para o da BFL, pedindo **uma frase de esclarecimento**:
"o uso para treinar um modelo distribuído de graça, num aplicativo local, aberto e sem nenhum fim comercial, é
permitido?". O rascunho está no Apêndice A.

* **Quem envia:** o usuário, do próprio e-mail. O agente não envia mensagens.
* **Custo:** zero. **Risco:** nenhum para o projeto; sem resposta, nada muda.
* **Se a resposta for sim:** a fonte passa a `APPROVED` com a resposta guardada como evidência no catálogo. O
  BRESSAY sozinho já mostrou 16 pontos de ganho (EXP-014).
* **Se for não ou não houver resposta:** fica `EXPERIMENT_ONLY`. Serve como régua e para descobrir o que
  funciona, nunca para um modelo do produto.

## 4. Plano revisado (substitui E3–E5 da v2)

| Etapa | O quê | Entrega | Situação dos dados |
| :---: | :--- | :--- | :--- |
| **E3** ✅ | EXP-031P: quais fontes abertas ajudam | nenhuma; E4 suspensa | — |
| **E3.1** ✅ | **EXP-044 — português perto do domínio**, mesma régua e mesmo orçamento do EXP-031P (§4.1) ([report](../../experiments/EXP-044-portugues-perto-do-dominio/report.md): a BFL leva o BRESSAY de 29,9 % a 23,0 %, mas piora o GNHK em 5,4; TraPrInq e treino longo não ajudam) | relatório; decisão de escala | TraPrInq `APPROVED`; BFL `EXPERIMENT_ONLY` |
| **E3.2** | pergunta aos autores (§3), em paralelo, sem bloquear nada | resposta guardada como evidência | — |
| **E4'** ⏸ | escala **só** do que passar na régua: TraPrInq inteira (6,7 GB) e/ou BFL alinhada inteira. *Não disparada pelo EXP-044:* nenhuma condição passa na regra completa (GNHK); a BFL já está inteira no catálogo e a TraPrInq não ajuda | ingestão pelo catálogo | conforme a situação |
| **E5** | leitor geral v1 (EXP-033G) | 0.14 | **só `APPROVED`** no modelo promovido |

### 4.1 EXP-044 — condições propostas

Mesma receita (392 passos de 16, taxa 5e-5, margem 640, semente fixa), mesmas medidas (BRESSAY teste, GNHK
teste, 62 linhas do autor em 512 px), mesma regra: ganhar ≥ 3 pontos no BRESSAY sem piorar > 2 no GNHK.

| Condição | Dados | Pergunta |
| :--- | :--- | :--- |
| D1 | TraPrInq, preferindo os documentos mais recentes (séc. XVIII–XIX) | o português histórico ajuda onde o histórico latino atrapalhou? |
| D2 | BFL alinhada (`EXPERIMENT_ONLY`) | letra moderna brasileira com texto fixo ensina o domínio? |
| D3 | D1 + D2 + sintético em pequena parte | a mistura soma? |
| D4 | latino moderno + sintético com **4× o orçamento** (~6 h de CPU) | o EXP-031P falhou por treino curto? |

A D4 só confirma ou descarta o efeito do orçamento; se ela também não ganhar, as fontes latinas modernas saem de
vez. Antes de treinar, uma amostra de 200 linhas de cada fonte mede o erro do leitor atual, como no EXP-043.

### 4.2 O sintético

Fica só como **ensino de acentos**, em parte pequena da mistura (≤ 25 %), nunca como volume (EXP-031P: −15 a −17
pontos de erro nos acentos, mas piora geral sozinho).

### 4.3 Proteger o inglês e a foto

Todo treino do EXP-031P piorou o GNHK de 2 a 17 pontos. O leitor geral precisa ler mais que português: as linhas
do grupo A já coletadas (`APPROVED`) ficam como reserva para misturar, e o EXP-044 continua medindo o GNHK.

## 5. Espaço e custo

| Item | Espaço no D: |
| :--- | ---: |
| Hoje (catálogo + modelos + trabalho do EXP-031P) | ~1,3 GB |
| TraPrInq inteira (zip) e linhas extraídas | ~6,7 GB + ~2 GB |
| BFL (945 páginas, 300 dpi) e linhas alinhadas | a medir no download (estimado < 2 GB) |
| **Total previsto** | **~12 GB de 100 GB** |

CPU local, bibliotecas abertas, nenhum serviço pago.

## 6. Riscos

| Risco | Mitigação |
| :--- | :--- |
| BFL decorada (mesmo texto em todas as páginas) | nunca medir na BFL; limitar a fatia dela na mistura; medir só em BRESSAY, GNHK e autor |
| Alinhamento forçado erra a linha | descartar por confiança; conferir uma amostra de 50 linhas a olho (dado público, não do usuário) |
| TraPrInq com abreviações e grafias antigas (como o grupo B) | preferir os séculos mais recentes; a condição D1 mede isso |
| Respostas dos autores demoram ou não vêm | nada depende delas para seguir os experimentos |
| Achar nada que ajude além do BRESSAY | a decisão volta ao usuário: o BRESSAY é o único caminho medido, e a licença dele é a pergunta |

## 7. Decisões que ficam com o usuário

1. **Aprovar esta revisão** (E3.1 com o EXP-044 e E4' condicionada).
2. **Enviar as duas mensagens** do Apêndice A, quando e se quiser.
3. Continuam em aberto, sem pressa: contato no User-Agent para o Wikimedia em escala; cadastro na Europeana.

## Fontes consultadas (2026-11-23)

* BRESSAY no Zenodo: <https://zenodo.org/records/11637681> (licença lida pela API: `cc-by-4.0`, acesso aberto).
* BRESSAY no TC-11: <https://tc11.cvc.uab.es/datasets/BRESSAY_1> (fora do ar na consulta; licença citada por
  resultado de busca).
* Escriba-OCR, que deriva do BRESSAY e repete a restrição de pesquisa e ensino: <https://github.com/tardellirs/escriba-ocr>.
* BFL na UFPR: <https://web.inf.ufpr.br/vri/databases/brazilian-forensic-letter-database/>; espelho no Mendeley:
  <https://data.mendeley.com/datasets/m8d45ykf9n/1> (licença não legível na consulta).
* LHTR.br (DSW 2023): <https://sol.sbc.org.br/index.php/dsw/article/view/25501>.
* TraPrInq, dados: <https://zenodo.org/records/13986218>; modelo: <https://zenodo.org/records/14538271> (ambos
  `cc-by-4.0` pela API).
* CVL (alemão e inglês, CC BY-NC 3.0, "non-commercial research purpose only"): fora do domínio, não proposto.

## Apêndice A — Rascunho das mensagens (o usuário envia, se quiser)

**Assunto:** Esclarecimento de licença do [BRESSAY / BFL] para uso não comercial

> Olá,
>
> Desenvolvo o Leitorum, um aplicativo pessoal, gratuito e sem nenhum fim comercial (sem anúncios, assinatura
> ou venda de dados), que lê cadernos manuscritos localmente, no computador de quem usa.
>
> Gostaria de usar o conjunto [BRESSAY / Brazilian Forensic Letter Database] para treinar o reconhecedor de
> texto desse aplicativo. O modelo treinado seria distribuído de graça junto com o aplicativo; as imagens e as
> transcrições não seriam redistribuídas, e o trabalho de vocês seria citado.
>
> Encontrei sinais diferentes sobre a licença: [BRESSAY: o registro no Zenodo indica CC BY 4.0, e o README do
> arquivo restringe a "non-commercial research and teaching purposes only" / BFL: a página indica CC BY 4.0 e
> também "non-commercial research"]. Esse uso é permitido?
>
> Obrigado pela atenção e pelo trabalho de disponibilizar os dados.
>
> [nome]
