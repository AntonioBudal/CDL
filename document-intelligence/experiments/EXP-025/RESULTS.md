# EXP-025: Relatório de Resultados — `organizer-v2` estático com as pistas de referência

* **Status:** `CONCLUÍDO` (2026-10-28, por delegação). H1, H2 e H3 dentro do pré-registro; a H4 reprova na medida
  pré-registrada e passa nas complementares (§2.4). [ADR-011](../../docs/adr/ADR-011-organizer-v2-estatico.md)
  `PROPOSED`: a adoção no Leitorum depende do aceite do usuário e de uma feature de produto própria.
* **Executor:** Claude Code
* **Artefatos:**
  - [spec.md](./spec.md) (hipóteses, dados e a decisão tomada na validação, §5);
  - [`artifacts/organizer-v2.json`](./artifacts/organizer-v2.json), SHA-256
    `9f6530a32726d593142b7a2de3bce3efc1c0095abf3a91335364db6343978aee`, congelado no commit `e846623`, antes de
    abrir o teste;
  - [`artifacts/parity-v2.json`](./artifacts/parity-v2.json), 192 casos fictícios para o produto, SHA-256
    `6726ddc4ce9049ec45f393fe84ef9412d70068cbb0c49819ade91e5713b71573`;
  - benchmarks `BENCHMARK-20261028-exp-025-organizer.json` (teste), `-latency.json` e `-dusuario.json`, auditados
    por um subagente revisor antes de gravar.

> **Dados e privacidade.**
> - Treino, validação e teste usam só páginas fictícias do projeto (MIT): EXP-023 e EXP-024.
> - O D-usuário rodou sobre uma cópia temporária do banco ativo do D:, feita pela API de backup, com origem e cópia
>   em `mode=ro` e apagada no fim. Nenhum texto foi impresso, gravado ou lido pelo agente; o relatório tem só
>   números.

---

## 1. Resposta

**Sim, nos formatos fictícios; nos estudos reais, ainda não se sabe.** Aprendidas em lote, as 4 pistas de
referência:
- levam o F1 de Referências do fichamento em lista (P1) de 0,00 a 0,54;
- não mudam nada onde não disparam: o teste do EXP-023 fica idêntico ao do v1;
- custam 0,017 ms por página.

Nos 4 estudos reais do usuário, o v2 dá **exatamente** o resultado do v1: as pistas não disparam nos formatos de
referência que o usuário escreve. A premissa do EXP-024 de que esses são os formatos reais **não se confirma**.

## 2. Vereditos (teste aberto uma vez, com o artefato do commit `e846623`)

### 2.1 H1 — formatos de fichamento (*holdout* de teste do EXP-024): **confirmada**

| Perfil | v1 Macro-F1 | v2 Macro-F1 | v1 Referências | v2 Referências |
| :--- | ---: | ---: | ---: | ---: |
| P1 (lista) | 0,504 | **0,638** | 0,000 | **0,545** |
| P2 | 0,626 | 0,693 | 0,700 | 0,961 |
| P3 | 0,973 | 0,973 | 0,991 | 0,991 |
| P4 | 0,714 | **0,699** | 0,783 | 0,817 |
| **média** | **0,704** | **0,751** | | |

- **Média:** +4,7 pontos (portão ≥ 3). **Referências do P1:** 0,545 (portão ≥ 0,50).
- **O P4 perde 1,5 ponto**, fora do que as hipóteses cobrem:
  - as Referências sobem (0,78 → 0,82);
  - o Resumo (0,83 → 0,79) e os Conceitos (0,59 → 0,53) caem: linhas de Conceitos que têm travessão viram
    Referências.
- **O ECE melhora em todos os perfis** em que o v2 muda (P1 0,41 → 0,26; P2 0,23 → 0,16; P4 0,17 → 0,14).

### 2.2 H2 — sem regressão (teste do EXP-023, 6 condições): **confirmada**

O Macro-F1 é **idêntico** ao do v1 nas 6 condições: 0,934 / 0,908 / 0,891 / 0,841 / 0,825 / 0,710 (limpo, CER 10 % e
25 %, com e sem geometria). Só o ECE varia, na quarta casa.

### 2.3 H3 — estudos reais (D-usuário estático): **sem piora, sem ganho**

| | Estudos | Elegíveis | Usuários | v1 Macro-F1 | v2 Macro-F1 | Referências (v1 = v2) |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| D-usuário | 4 | 4 | 2 | 0,535 | 0,535 | 0,359 |

- O ganho é **0,0**: nenhuma das 4 pistas muda a decisão em nenhuma unidade dos estudos reais.
- Com N = 4, o número é só um alerta, mas o alerta é claro: os formatos do EXP-024 foram escritos pelo agente, não
  observados. O que o usuário escreve em Referências não é lista com travessão, link em Markdown, URL sozinha
  nem "Título (Autor, ano)".

### 2.4 H4 — custo: **reprovada na medida pré-registrada; aprovada nas complementares**

| Medida | Resultado | Portão (≤ 1 ms) |
| :--- | :--- | :--- |
| **pré-registrada:** p95, uma passagem por modelo, em sequência (10 linhas da `evaluate.py`) | diferenças de −1,45 a **+2,18 ms**; acima de 1 ms em 3 das 10 (P1 +2,18; P4 +1,19; CER 10 % sem geometria +1,25) | **reprova** |
| **intercalada:** 5 repetições por página, v1 e v2 alternados (`latency.py`, páginas do EXP-023) | primeira rodada −0,6 a +1,15 ms; segunda (a gravada) −0,73 a +0,18 ms | passa na gravada |
| **custo direto:** as 4 expressões em todas as unidades das páginas de teste | **0,017 ms por página** (1,9 µs por unidade; 214 unidades em 24 páginas) | passa |

- **Leitura:** a medida pré-registrada é dominada pelo ruído da máquina. As diferenças trocam de sinal entre
  perfis, condições e rodadas, e o P2 sai 1,45 ms **mais rápido** no v2. O v2 executa o v1 inteiro mais as 4
  expressões; o que ele faz a mais custa 17 µs por página.
- **Desvio declarado:** o portão da spec (§1) é a medida de passagem única. Aprovar a H4 pelas medidas
  complementares é uma troca de critério depois de ver o resultado. Por isso o ADR-011 fica `PROPOSED` e a
  decisão é do usuário.

## 3. Limites

1. **A H1 mede formatos conhecidos em obras novas.** Os modelos de referência são os mesmos nos fluxos de
   validação e de teste do EXP-024 (risco declarado na spec, §3). Um formato novo não seria reconhecido.
2. **O D-usuário tem N = 4**, de 2 usuários, e as pistas não disparam nele.
3. **O P4 perde 1,5 ponto**, e o que perde é Conceitos com travessão, um formato plausível em cadernos reais.

## 4. Recomendação

- **Adotar o `organizer-v2` no Leitorum é seguro e quase inútil hoje.** Não piora nada medido, salvo o P4, custa
  17 µs por página e ajuda quem escrever referências nos formatos das pistas. Nos estudos do usuário, não muda nada.
- **O que vale mais é o registro do feedback** (`leitorum-feedback/1`): sugestão do Organizador contra as 4 seções
  salvas. Com ele, os formatos reais de Referências passam a ser observados e não inventados, e um
  `organizer-v3` pode aprender pistas dos próprios dados.
- A troca de artefato, o registro do feedback e o adaptador online (dormente até N ≥ 20–30 estudos revisados) são
  uma feature do Leitorum com Spec Kit próprio. A pós-correção automática da leitura continua desligada (EXP-024,
  H2 refutada).

## 5. Reprodução

```powershell
# a partir de document-intelligence/
uv run --frozen --project experiments/EXP-023/envs/organizer python experiments/EXP-025/harness/train.py --mode cues
uv run --frozen --project experiments/EXP-023/envs/organizer python experiments/EXP-025/harness/evaluate.py --split test
uv run --frozen --project experiments/EXP-023/envs/organizer python experiments/EXP-025/harness/latency.py
uv run --frozen --project experiments/EXP-023/envs/organizer python experiments/EXP-025/harness/export_parity.py
uv run --frozen --project experiments/EXP-023/envs/organizer pytest experiments/EXP-025/tests
```

O `dusuario_static.py` exige `--db` e roda só sobre uma cópia temporária (ver o cabeçalho do script).
