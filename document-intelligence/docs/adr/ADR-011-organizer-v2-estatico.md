# ADR-011: `organizer-v2` estático — o v1 congelado mais 4 pistas fixas de referência

* **Status:** PROPOSED (2026-10-28; aguarda o aceite do usuário. A H4 reprova na medida pré-registrada, ver §3)
* **Data:** 2026-10-28
* **Decisores:** Usuário; Claude Code (proposta e execução do EXP-025, por delegação)
* **Experimento de suporte:** [EXP-025](../../experiments/EXP-025/RESULTS.md); origem das pistas no
  [EXP-024](../../experiments/EXP-024/RESULTS.md)
* **Complementa:** [ADR-010](./ADR-010-organizacao-nas-4-secoes.md) (a pipeline e o v1 continuam como estão)
* **Status de licença:**
  - código e pesos sob MIT, ajustados só em dados fictícios do projeto (EXP-023 e EXP-024);
  - nenhum corpus, modelo ou serviço externo.

## 1. Contexto

No EXP-024, 4 regras fixas de formato de referência levaram o F1 de Referências do fichamento em lista de 0,00 a
0,78, mas dentro de um motor online que não passou no portão de adoção. O EXP-025 testou as mesmas regras
aprendidas **em lote**, sem estado por usuário, para ir ao produto sem aprendizado online.

## 2. Decisão proposta

1. **Trocar `organizer-v1.json` por `organizer-v2.json`** (SHA-256 `9f6530a3…8aee`) no Organizador do Leitorum:
   - os pesos, o viés, a temperatura (β = 1,25) e a margem de "conferir" (0,20) do v1 ficam **congelados**;
   - entram 4 colunas novas, valendo 0 ou 1: `ref_md_title_author`, `ref_md_link`, `ref_url_line` e
     `ref_title_author_year`;
   - os pesos aprendidos dessas colunas somam-se aos *logits* do v1;
   - onde nenhuma pista dispara, o resultado é **idêntico** ao do v1.
2. **As expressões vão no artefato** (`extra_cues`, com padrão e modo `match`/`search`). O produto as lê de lá e
   recusa um artefato cujas pistas não conheça.
3. **Paridade obrigatória:** o produto reproduz os 192 casos de `parity-v2.json` (SHA-256 `6726ddc4…1573`).
4. **Ficam de fora:** o retreino de todos os pesos (modo `full`, rejeitado na validação), os centróides do leitor
   e do livro, $T_{\text{user}}$ e o aprendizado online.

## 3. Evidência (teste aberto uma vez)

| Hipótese | Resultado | Portão |
| :--- | :--- | :--- |
| H1 — fichamentos (EXP-024) | média 0,704 → **0,751**; Referências do P1 0,00 → **0,545**; P4 **−1,5 ponto** | ≥ +3 e ≥ 0,50: **confirmada** |
| H2 — EXP-023, 6 condições | **idêntico** ao v1 em todas | ≤ 1 ponto abaixo: **confirmada** |
| H3 — estudos reais (N = 4) | 0,535 = 0,535; as pistas não disparam | sem piora: **atendida, ganho nulo** |
| H4 — latência p95 | passagem única: até **+2,18 ms** (reprova em 3 de 10); intercalada: −0,73 a +0,18 ms; custo direto **0,017 ms por página** | ≤ 1 ms: **reprova no pré-registro** |

A H4 reprovada é ruído de medida: as diferenças trocam de sinal, e o que o v2 executa a mais custa 17 µs. Aceitar
isso é trocar o critério depois de ver o resultado, e por isso a decisão fica com o usuário.

## 4. Consequências

- **Nos dados do usuário, o ganho hoje é zero.** As pistas foram escritas pelo agente, não observadas. A adoção é
  barata e não piora o que foi medido, salvo o P4 (Conceitos com travessão passam a ir para Referências).
- **O passo que importa é o registro do feedback** (`leitorum-feedback/1`): com a sugestão contra as 4 seções
  salvas, os formatos reais de Referências passam a ser medidos, e um `organizer-v3` pode aprender pistas dos
  próprios dados.
- A integração (troca do artefato, registro do feedback, adaptador online dormente até N ≥ 20–30 estudos
  revisados, pós-correção da leitura desligada) é uma feature do Leitorum com Spec Kit próprio.
