# EXP-031P — Quais fontes abertas ajudam o leitor a ler letra moderna em português?

* **Criado em:** 2026-11-22
* **Status:** `DONE` (aprovado em 2026-11-22; [relatório](./report.md))
* **Etapa:** E3 da [estratégia de dados v2](../../docs/replanejamento-0.13/09-estrategia-de-aquisicao-de-dados.md)
* **Depende de:** EXP-043 (fontes medidas), F-DI-13.03 (catálogo) · **Decide:** o que a E4 coleta em escala

---

## 1. Pergunta

O leitor do produto (PP-OCRv6 small) erra ~50 % numa letra moderna em português que nunca viu (EXP-028B, 512 px).
As fontes abertas e liberadas (EXP-043) são quase todas **históricas** e em **outros idiomas**. **Ajustar o
leitor com elas melhora a leitura de letra moderna em português de pessoas que ele nunca viu?** E qual grupo
rende mais por linha: latino moderno, histórico ou sintético em português?

Se nenhum grupo ajudar, coletar dados abertos em escala (E4) não se justifica, e a estratégia muda.

## 2. Condições (mesmo orçamento de treino em todas)

Receita do EXP-014/018, que já funcionou em CPU: ajuste fino do PP-OCRv6 small, **392 passos de 16 linhas**
(~6,3 mil linhas vistas, ~2,5–3 h de CPU), taxa 5e-5, margem de 640 px, semente fixa; avaliação do **modelo
final** (sem escolher ponto de parada, para não usar nenhum conjunto de teste na escolha).

| Condição | Dados de treino (8 mil linhas por condição) | Situação |
| :--- | :--- | :--- |
| **C0** | nenhum (leitor atual) | — |
| **C1 — A** | latino moderno (séc. XIX–XXI): RIMES, Moonshines, CREMMA séc. XX, Célestine, Notaires de Paris, Belfort, POPP, NorHand v2 | `APPROVED` |
| **C2 — B** | histórico: HOME-Alcar, Himanis, CREMMA Medieval, iForal | `APPROVED` |
| **C3 — S** | sintético em português (domínio público + fontes OFL) com aumentos fortes (inclinação, espessura, ruído, fundo, desfoque) | `APPROVED` |
| **C4 — A+S** | metade de cada | `APPROVED` |
| **C5 — A+B+S** | um terço de cada | `APPROVED` |
| *Referência* | BRESSAY treino (EXP-014): 13,6 % no teste do BRESSAY | `EXPERIMENT_ONLY` — **citado, não retreinado** |

A referência mostra o teto com dado do domínio exato (português moderno); as condições C1–C5 dizem quanto do
caminho os dados liberados percorrem.

## 3. Onde se mede (pessoas que o leitor nunca viu)

| Conjunto | O que é | Papel |
| :--- | :--- | :--- |
| **BRESSAY teste** | redações em português moderno, autores fora do treino (divisão oficial) | **medida principal** (permitida: uso em pesquisa) |
| **GNHK teste** | fotos de celular de anotações em inglês | generalização para foto |
| **4 páginas do autor** | 62 linhas com caixa e texto do EXP-028A/B (512 px) | o caderno real do projeto |

Medidas: CER e WER; **erro nas letras acentuadas** do BRESSAY (como no EXP-014). Nenhuma linha de teste entra em
treino; a trava é por fonte (BRESSAY, GNHK e as páginas do autor não estão no catálogo de treino).

## 4. Hipóteses

| # | Hipótese | Critério |
| :--- | :--- | :--- |
| **H1** | o grupo A melhora o português moderno | CER no BRESSAY teste cai ≥ 3 pontos de C0 para C1 |
| **H2** | o histórico ajuda menos que o moderno | CER(C2) > CER(C1) no BRESSAY teste |
| **H3** | o sintético ensina os acentos | erro nas letras acentuadas cai ≥ 10 pontos de C0 para C3 |
| **H4** | moderno + sintético é a melhor combinação | C4 tem o menor CER no BRESSAY teste entre C1–C5 |

**Regra de decisão para a E4:** escalar o(s) grupo(s) da condição vencedora se ela melhorar ≥ 3 pontos sobre C0
no BRESSAY teste sem piorar > 2 pontos no GNHK; se nenhuma melhorar ≥ 3 pontos, a coleta em escala fica
suspensa e a estratégia é revista.

## 5. Regras

* Dados de treino **só pelo catálogo**: cada condição é um ciclo `experimento` registrado (lista exata de itens);
  o sintético é registrado pela receita e semente do gerador.
* Linhas com caracteres fora do dicionário do leitor são descartadas e contadas (como no EXP-014).
* Tudo local, em CPU, retomável e com espera de RAM livre (regra do projeto: a máquina tem 7,9 GB e é
  compartilhada); espaço extra estimado: ~2 GB no D:.
* Nenhum modelo deste experimento vai ao produto (é um experimento; a promoção seria por ADR e spec próprios).
