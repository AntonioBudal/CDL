# Experiment Specification: EXP-009 — Leitura de Manuscrito em Português com o Reconhecedor do PP-OCR

**Diretório do experimento**: `experiments/EXP-009/`

**Created**: 2026-10-14

**Status**: `DELEGATED` — especificado, planejado e executado por delegação do usuário, que, ao aprovar o plano do
EXP-008, autorizou: "após realizar as próximas tarefas, planeje as próximas, e continue executando". O usuário
revisa esta especificação junto com os resultados. Spec, plano e tarefas foram escritos antes de qualquer código.

**Input**: ADR-001 (nenhum HTR pronto lê português manuscrito), EXP-001 (melhor CER no BRESSAY: 69,4 %), ADR-006
(`PROPOSED`: detecção de linhas pelo PP-OCR).

---

## 1. Pergunta e Hipóteses

**Pergunta central:** o reconhecedor de texto que já vem no pacote do PP-OCR (PP-OCRv6 small rec, multilíngue,
com português entre as línguas declaradas) lê manuscrito em português? E, junto com o detector do EXP-008, quanto
de uma página se recupera de ponta a ponta?

O ADR-001 é a premissa mais pesada do projeto: sem leitura, não há produto. Ele foi tomado com três candidatos; o
PP-OCRv6 não existia entre eles e não exige download nem dependência nova (já está no ambiente do EXP-008).

- **H1 (linhas, mesmo teste do EXP-001):** CER ≤ 30 % nas 398 linhas do BRESSAY do EXP-001 (contra 69,4 % do
  melhor candidato de então).
- **H2 (critério de adoção do EXP-001):** CER ≤ 12 % e WER ≤ 25 % nessas linhas.
- **H3 (detecção custa pouco):** o CER de página com as linhas detectadas fica no máximo 5 pontos acima do CER de
  página com as linhas verdadeiras.
- **H4 (custo):** mediana ≤ 150 ms por linha e ≤ 2 GiB (critério do EXP-001).
- **H5 (foto de celular):** CER ≤ 20 % nas linhas manuscritas do GNHK (inglês), com as linhas verdadeiras.

## 2. Cenários

1. **Linhas do EXP-001** (398 recortes do BRESSAY, teste oficial): comparação direta com a tabela do EXP-001.
2. **Páginas do BRESSAY** (185 páginas do teste, as do EXP-007): leitura das linhas verdadeiras (teto) e das linhas
   detectadas pelo PP-OCR com a fusão do EXP-008 (ponta a ponta); CER de página contra a transcrição da página.
3. **Linhas do GNHK** (teste, fotos de celular): leitura das linhas verdadeiras manuscritas e legíveis.
4. **Análise:** CER por classe de caractere (letras sem acento, letras acentuadas, dígitos, pontuação), sem expor
   texto.

## 3. Requisitos

- **FR-001:** Só a etapa de reconhecimento e a de detecção do pacote; nenhum modelo novo, nenhum download.
- **FR-002:** Normalização: Unicode NFC no CER de linha, como no EXP-001; no CER de página, também espaços em
  branco colapsados e as marcas de anotação do BRESSAY (`@@`, `##`, `$$`, `--`) removidas, nos dois lados.
- **FR-003:** WER com a normalização aprovada (pontuação de borda removida; acentos e caixa preservados).
- **FR-004:** As transcrições dos datasets são usadas só para calcular métricas. Nenhum texto de referência ou
  reconhecido vai para o Git, para relatórios ou para o chat; os relatórios trazem números e identificadores.
- **FR-005:** Diretórios dos experimentos aceitos só lidos; o subconjunto do EXP-001 é lido onde está.
- **FR-006:** Mesmo supervisor, limites e critério de RAM livre (≥ 1 GiB).
- **FR-007:** Saídas de página em LDF 2.0 com a etapa `recognition` concluída e o texto nas linhas; validadas.
- **FR-008:** `LICENSE STATUS: NEEDS VALIDATION` na parte que depende do BRESSAY; nenhuma conclusão de produto
  apoiada só nele.

## 4. Critérios de Sucesso

- **SC-001:** Veredito de H1 a H5.
- **SC-002:** CER de linha comparável ao EXP-001 (mesmas 398 linhas, mesma métrica).
- **SC-003:** Decomposição da perda de página entre detecção e leitura.
- **SC-004:** 100 % das saídas de página válidas em LDF 2.0.
- **SC-005:** Nenhum texto dos datasets no Git ou nos relatórios.
- **SC-006:** ADR que confirme, revise ou mantenha o ADR-001.

## 5. Fora do escopo

Ajuste de pesos, modelos de linguagem, correção ortográfica, blocos, ordem com notas de margem, integração com o
site.
