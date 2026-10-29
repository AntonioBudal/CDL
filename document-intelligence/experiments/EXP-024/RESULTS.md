# EXP-024: Relatório de Resultados — Melhoria Contínua Autônoma do Organizador e da Pós-Correção da Leitura

* **Status:** `CONCLUÍDO` (2026-10-28). **Portão de adoção não atingido**: nenhuma adoção do motor adaptativo no
  produto e nenhum ADR de adoção. **Revisado pelo usuário:** as três recomendações do §8 foram levadas adiante pelo
  EXP-025 (ADR-011) e pela feature 091 do Leitorum; ver [STATE.md](./STATE.md), "Revisão do usuário".
* **Executor:** Claude Code
* **Artefatos:**
  - [spec.md](./spec.md), [plan.md](./plan.md), [tasks.md](./tasks.md), [STATE.md](./STATE.md);
  - [`artifacts/thresholds.json`](./artifacts/thresholds.json), congelado na validação **antes** do teste (commit
    `249fd51`), com o registro da busca em `artifacts/tuning-log.json`;
  - benchmarks `BENCHMARK-20261028-exp-024-continual.json` (teste) e `BENCHMARK-20261028-exp-024-dusuario.json`,
    auditados por um subagente revisor antes de gravar.

> **Dados e privacidade.**
> - Páginas, livros, perfis e o leitor simulado são fictícios, escritos para o projeto (MIT) e congelados com
>   SHA-256 antes de qualquer código (commit `d919571`).
> - Os confundidores de leitura por escritor são **sintéticos e declarados**; o ruído global vem só de contagens do
>   EXP-015.
> - O D-usuário rodou sobre uma cópia temporária do banco ativo do D: (decisão do usuário), feita pela API de
>   backup, com origem e cópia em `mode=ro` e apagada no fim. Nenhum texto foi impresso, gravado ou lido pelo
>   agente; o relatório tem só números.

---

## 1. Resposta

**Não, ainda não.** O motor aprende com o uso, mas não o bastante, nem com segurança e custo suficientes, para ir
ao produto. Nenhuma das cinco hipóteses foi confirmada por inteiro.

Três achados valem mais que os vereditos:

1. **As pistas novas de referência resolvem a maior lacuna do EXP-023.** No perfil que imita os fichamentos reais
   (listas Markdown, "Título — Autor", links), o F1 de Referências vai de **0,000 para 0,783** em 40 páginas.
2. **Sob feedback ruidoso, aprender sem travas é pior que não aprender.** Sem travas, o R3 termina **abaixo** do V4
   estático: 0,693 contra 0,704 de Macro-F1, com pior queda de 8,0 pontos. Com as travas, chega a 0,739, e a pior
   queda é de 2,3.
3. **No regime limpo (R1), a versão mais simples rende mais.** Só os pesos online sobre o diff de revisão, com as
   pistas novas, chegam a **0,777**. O motor completo, com gating e travas, fica em 0,758. A proteção custa cerca de
   2 pontos no R1.

A pós-correção da leitura **não** funciona a 25 % de CER: tira só 6–7 % do erro e estraga palavras certas. É o mesmo
teto do EXP-011. Nos estudos reais (N = 2), ela piorou um texto que já estava quase limpo.

| Hipótese | Veredito | Evidência (teste) |
| :--- | :--- | :--- |
| H1 — +8 pontos de Macro-F1 após 40 páginas (R1); +20 em Referências no perfil não-ABNT | **Refutada** (Referências passa) | média 0,704 → 0,758 (+5,3); P1 Referências 0,000 → 0,783 (+78); P2 **cai** 5,2 |
| H2 — CER −15 %, acentos −30 %, ≥ 99,5 % das palavras certas preservadas, curadoria ≥ 0,95 | **Refutada** | CER 25 %: −6,0 a −7,4 %; acentos −10 a −19 %; preservação 98,2–99,8 %; curadoria 0,87–0,94. CER 10 %: −14,7 a −20,1 %; acentos −29 a −54 %; preservação 98,5–99,3 % |
| H3 — no R3, nunca mais de 1 ponto abaixo do V4 e ≥ 70 % do ganho do R1 | **Refutada** | pior queda de 2,3 pontos; 64 % do ganho do R1. Sem travas: pior queda de 8,0 e t = 40 abaixo do V4 |
| H4 — 1º clique com ordem por informação e re-decodificação ≥ 2× o 1º clique por margem | **Refutada** | razão entre 0,87× e 1,24×; o passo local piora |
| H5 — atualização p95 ≤ 25 ms; acréscimo ≤ 5 ms; estado ≤ 512 KB com 500 estudos; replay ≤ 2 s | **Refutada** | 73–87 ms; 6,9 ms; 749 KB; 32,8 s |
| Portão de adoção (H1, H3 e H5 confirmadas; D-usuário não pior) | **Não atingido** | — |

## 2. Organizador (teste, 4 perfis × 40 páginas de adaptação, 24 páginas *holdout* cada)

Macro-F1 por caractere, na régua do EXP-023. As páginas *holdout* estão em texto limpo, o cenário de "organizar
depois de corrigir". t = 0 é o V4 estático.

### 2.1 Curva de aprendizado no R1 (sem nota)

| Perfil | t = 0 | 1 | 5 | 10 | 20 | 40 | Referências t = 0 → 40 | Caracteres a mover t = 0 → 40 |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | :--- | :--- |
| P1 (lista, Markdown, links) | 0,504 | 0,504 | 0,557 | 0,609 | 0,650 | **0,732** | 0,000 → **0,783** | 42,6 % → 26,8 % |
| P2 (conceitos primeiro) | 0,626 | 0,621 | 0,606 | 0,597 | 0,586 | **0,574** | 0,700 → 0,733 | 37,4 % → 45,0 % |
| P3 (reflexivo, ABNT) | 0,973 | 0,973 | 0,973 | 0,973 | 0,973 | 0,973 | 0,991 → 0,991 | 2,5 % → 2,5 % |
| P4 (misto) | 0,714 | 0,701 | 0,724 | 0,752 | 0,730 | 0,751 | 0,783 → 0,873 | 30,8 % → 25,2 % |
| **Média** | **0,704** | | | | | **0,758** | | |

- **O ganho é real onde o V4 errava por formato (P1, P4).** O ganho vem sobretudo de Referências.
- **O P2 piora devagar.** O perfil abre a página pelos conceitos e é telegráfico. A transição pessoal $T_{\text{user}}$
  e o replay não seguraram essa deriva lenta, coerente com o leitor (spec §10, risco previsto).
- **O P3**, estilo que o V4 já acerta, fica estável.

### 2.2 Regimes com nota e com ruído (média dos perfis)

| Regime | t = 40 | Ganho | Pior queda abaixo do V4 em qualquer t |
| :--- | ---: | ---: | ---: |
| R1 (implícito) | 0,758 | +5,3 | 5,2 (P2) |
| R2 (+ nota coerente) | 0,740 | +3,5 | 3,6 |
| R3 (20 % ruidoso) | 0,739 | +3,4 | 2,3 |
| **R3 sem travas** (sem gating, replay, portão nem projeção; filtro de leitura desligado) | **0,693** | **−1,1** | **8,0** |

- **A nota coerente (R2) não ajudou; atrapalhou um pouco.** Explicação provável, não testada à parte: com nota
  alta, trechos mantidos ganham mais peso mesmo quando estão errados e não foram conferidos.
- **As travas são o que separa aprender de piorar sob ruído:** +4,6 pontos no R3.

### 2.3 Ablações (R1, t = 40, média dos perfis)

| Escada cumulativa | Macro-F1 | P1 | P2 | P3 | P4 |
| :--- | ---: | ---: | ---: | ---: | ---: |
| + E1 (pesos online sobre o diff; sem gating, sem travas) | 0,773 | 0,740 | 0,619 | 0,976 | 0,759 |
| + E2 (pistas novas de referência, centróides do leitor e do livro) | **0,777** | 0,760 | 0,619 | 0,972 | 0,759 |
| + E3/E6 (gating por comportamento e nota) | 0,763 | 0,751 | 0,583 | 0,959 | 0,759 |
| completo (+ $T_{\text{user}}$, replay, portão-sombra, projeção) | 0,758 | 0,732 | 0,574 | 0,973 | 0,751 |

| Completo menos… | Macro-F1 | Leitura |
| :--- | ---: | :--- |
| pistas novas de referência | 0,740 | as pistas são o componente que mais pesa (P1: 0,732 → 0,694) |
| centróides (leitor e livro) | 0,751 | ajudam pouco (+0,7) |
| $T_{\text{user}}$ | **0,776** | a transição pessoal **atrapalha** (−1,8) |
| gating | 0,691 | sem gating, com as travas ligadas, o P1 desaba (Referências 0,0). Explicação provável: o replay passa a guardar rótulos errados e a barrar as correções certas |
| portão-sombra da semente | 0,758 | **não agiu** no teste (idêntico) |
| replay | 0,746 | o replay é a trava ativa |
| todas as travas | 0,746 | a projeção também não agiu |

### 2.4 Um clique (E4)

O leitor simulado corrige, na ordem mostrada, o primeiro trecho errado. Ganho de Macro-F1 do 1º clique (R1):

| Perfil | Margem, sem re-decodificar | Entropia × acoplamento, re-decodifica | … com passo local (E4b) |
| :--- | ---: | ---: | ---: |
| P1 (t = 40) | 0,114 | 0,126 | 0,091 |
| P2 (t = 40) | 0,120 | 0,149 | 0,117 |
| P3 (t = 40) | 0,015 | 0,014 | 0,017 |
| P4 (t = 40) | 0,103 | 0,090 | 0,033 |

- **O clique vale muito (10 a 15 pontos numa página), mas a ordem e a re-decodificação mudam pouco.** O leitor
  procura o primeiro trecho errado em qualquer ordem, e o custo de troca do Viterbi já mantém os vizinhos coerentes.
- **O passo local de aprendizado no mesmo minuto piora:** um rótulo com peso alto puxa os vizinhos para o lado
  errado.

## 3. Pós-correção da leitura (teste, *holdout*)

| CER do leitor | Perfil | CER bruto → corrigido (queda relativa) | Erro em acentos (queda relativa) | Palavras certas preservadas | Curadoria (pares, precisão) |
| :--- | :--- | :--- | :--- | ---: | :--- |
| 25 % | P1 | 21,8 % → 20,5 % (6,0 %) | 77,6 % → 62,5 % (19,4 %) | 98,2 % | 72; 0,889 |
| 25 % | P2 | 20,5 % → 19,0 % (7,2 %) | 55,6 % → 45,8 % (17,6 %) | 98,9 % | 125; 0,872 |
| 25 % | P3 | 22,4 % → 20,8 % (7,4 %) | 56,2 % → 48,3 % (13,9 %) | 98,7 % | 94; 0,904 |
| 25 % | P4 | 24,5 % → 23,1 % (6,0 %) | 71,8 % → 64,3 % (10,4 %) | 99,8 % | 72; 0,944 |
| 10 % | P1–P4 | queda de 14,7 a 20,1 % | queda de 29 a 54 % | 98,5–99,3 % | — |

- **Ablação:**
  - só léxico: queda de 2,6–3,2 % do CER;
  - só léxico sem o livro: 1,3–2,2 %;
  - léxico e confusões pessoais: 5,6–6,7 %.

  O livro e as confusões pessoais somam, mas o teto é baixo: a 25 % de CER, muitas palavras têm dois erros ou mais e
  ficam fora do alcance do léxico.
- **O custo inaceitável é o dano.** Entre 0,2 % e 1,8 % das palavras já certas são trocadas. Num leitor que corrige
  o resto à mão, estragar uma palavra certa é pior que não corrigir.
- **A curadoria para o EXP-018 fica perto, mas abaixo, de 0,95.** O filtro de léxico (todas as palavras já
  conhecidas) levou a precisão de 0,49 para cerca de 0,9 na validação. O resto são linhas em que o leitor deixou um
  erro que forma palavra válida.
- **O limiar pessoal de `low_confidence` não se formou** no simulador: a 25 % de CER quase toda linha é editada.

## 4. Estudos reais do usuário (D-usuário, prequencial, só números)

| Medida | Valor |
| :--- | :--- |
| Estudos / elegíveis / usuários | 4 / 4 / 2 |
| Avaliados de forma prequencial (cada estudo com o estado só dos anteriores) | **2** (o 1º estudo de cada usuário não tem histórico) |
| Macro-F1 V4 → adaptativo | **0,599 → 0,667** (+6,8) |
| F1 por seção, V4 → adaptativo | Resumo 0,80 → 0,70; Explicação 0,55 → 0,64; Conceitos 0,67 → 0,91; Referências 0,39 → 0,41 |
| Estudos digitalizados com leitura bruta | 2 |
| Leitura: CER bruto → corrigido | **0,45 % → 0,76 %** (a pós-correção piorou) |
| $T_{\text{user}}$ | desligado (pseudo-páginas na ordem canônica: ganho falso) |

**Leitura:**
- N = 2 não estima nada com precisão. O sinal é coerente com o teste: o Organizador melhora, e a pós-correção estraga
  texto que já estava quase limpo.
- O ganho em Referências reais é pequeno (+2,4), embora no P1 fictício tenha sido enorme. Os formatos reais podem
  ser outros, e só mais estudos dirão.

## 5. Custo (máquina de referência, 0,9 GB de RAM livre durante a medição)

| Medida | Valor | Meta |
| :--- | ---: | ---: |
| Atualização do Organizador por página, p50 / p95 | 34–42 / 73–87 ms | p95 ≤ 25 |
| Atualização da leitura por página, p95 | 150–197 ms | — |
| Acréscimo na organização, p95 | 6,9 ms (25,5 → 32,4) | ≤ 5 |
| Estado por usuário após 40 páginas | 214–304 KB | — |
| Estado com 500 estudos em 16 livros | **749 KB** | ≤ 512 |
| Reconstrução por replay de 500 estudos | **32,8 s** | ≤ 2 |

- A máquina estava mais lenta que nos testes de fumaça: p50 de 9–20 ms antes.
- Ainda assim, o replay e o tamanho falham por estrutura:
  - cada estudo reaprendido re-analisa a página e roda os portões;
  - cada livro guarda somas próprias.

## 6. O que mudou no desenho durante o experimento (medido só na validação)

1. **Centróides do leitor viraram colunas novas, com peso 0 na âncora.** Misturá-los aos centróides-semente piorava
   o acerto sem parar: os pesos do EXP-023 perdiam o sentido, e o vocabulário do livro media assunto, não seção.
2. **Trecho mantido sem "conferir" quase não ensina** (peso 0,05): é a própria previsão do motor.
3. **Replay das correções do próprio leitor** como trava principal. O portão da semente nunca agiu no teste.
4. **Curadoria com léxico:** precisão de 0,49 → ~0,9.

## 7. Limites

- **Circularidade:** o mesmo agente escreveu páginas, leitor simulado e motor. Os números das páginas fictícias são
  um teto otimista. Mesmo esse teto não passou nos portões.
- **O leitor simulado é uma hipótese** (taxas de correção, nota, ruído). O efeito das travas depende de como o ruído
  real se parece.
- **N do D-usuário = 2.**
- **Medições de tempo numa máquina com pouca RAM livre.**

## 8. Recomendação

Não levar o motor adaptativo ao Leitorum agora. Há três passos de baixo risco que o experimento sustenta:

1. **Levar só as pistas novas de referência para o Organizador estático.** Elas são regras fixas, não aprendizado,
   mas precisam de pesos que o `organizer-v1` não tem: é um `organizer-v2` treinado em lote no EXP-023, sem estado
   por usuário. É o maior ganho medido, sem os riscos do aprendizado online.
2. **Começar a guardar o sinal, sem aprender com ele ainda.** O produto pode registrar, com consentimento:
   - a sugestão do Organizador e o estudo salvo (o pacote `leitorum-feedback/1`);
   - as correções de leitura como `human_corrections`.

   Isso cria o D-usuário longitudinal real que falta para decidir.
3. **Não ligar a pós-correção automática da leitura.** No máximo, sugestões de acento com confirmação do leitor.

**Para retomar o aprendizado online:**
- repetir com pelo menos 30 estudos reais e com o pacote de feedback real;
- tirar $T_{\text{user}}$;
- trocar a reconstrução por replay por um estado salvo incrementalmente;
- limitar as somas por livro.

## 9. Reprodução

```powershell
$e = "experiments/EXP-023/envs/organizer"
uv run --frozen --project $e python -m pytest experiments/EXP-024/tests          # 46 aprovados, 1 pulado (LDF)
uv run pytest experiments/EXP-024/tests/test_ldf_patches.py                       # 2 aprovados (ambiente principal)
uv run --frozen --project $e python experiments/EXP-024/harness/calibrate.py      # só validação -> thresholds.json
uv run --frozen --project $e python experiments/EXP-024/harness/evaluate.py --split test --out evaluation/benchmarks/bench.json
uv run --frozen --project $e python experiments/EXP-024/harness/dusuario_continual.py --db "D:/Leitorum/db/caderno.db" --out dusuario.json   # só com autorização
```

*Assinatura do agente executor:* `Claude Code (claude-opus-5-5), 2026-10-28`
