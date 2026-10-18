# EXP-013 — Escala Automática da Página (especificação, plano e tarefas)

**Created**: 2026-10-18 · **Status**: `DELEGATED` (autonomia permanente do usuário, 2026-10-18)

**Input**: ADR-008: a mesma página de redação lida com 45,8 % de CER na escala original e 36,2 % ampliada 3×; as fotos
do GNHK (2.048 px) quase não precisam de ampliação. Uma escala fixa não serve a todas as entradas.

## Pergunta e hipóteses

Uma regra que mede a altura das linhas na própria página e escolhe o fator de ampliação recupera o ganho da
ampliação fixa sem saber de antemão de onde veio a imagem?

- **H1:** BRESSAY na escala original com a regra automática: CER de página no máximo 1 ponto pior que a ampliação
  fixa 3× (36,2 %).
- **H2:** GNHK com a regra automática: CER de página não piora mais de 1 ponto em relação ao EXP-012 (27,5 %).
- **H3:** custo ≤ 6 s por página na mediana.

## Método

* **Regra:** primeira passada de detecção na imagem recebida → altura mediana das linhas detectadas *h* → fator
  *s* = arredondamento de *alvo / h*, limitado a [1, 4] → se *s* > 1, a página é ampliada (bicúbica) e o pipeline do
  ADR-008 roda sobre ela; as coordenadas voltam para a imagem original no LDF.
* **Calibração do alvo** (só calibração): alvos de 48, 64 e 80 px, nas 154 páginas de **validação** do BRESSAY (escala
  original) e nas 150 fotos de **treino** do GNHK do EXP-008; critério: média do CER de página dos dois conjuntos.
* **Teste:** 185 páginas de teste do BRESSAY (escala original) e 172 fotos de teste do GNHK, uma vez.
* Sem modelo novo, sem dependência nova; mesmas regras de privacidade e licença.

## Tarefas

- [x] **T001** Harness (cópia do EXP-012) com a regra de escala e testes.
- [x] **T002** Conjuntos de calibração com referência de página (BRESSAY validação; GNHK treino).
- [x] **T003** Calibrar o alvo; testar uma vez.
- [x] **T004** Relatório, evidência no ADR-008, registros.
