# Experiment Specification: EXP-007 — Validação do Layout e da Ordem de Leitura em Fotografias Reais

**Diretório do experimento**: `experiments/EXP-007/`

**Created**: 2026-10-12

**Status**: `DRAFT` — aguardando aprovação do usuário. Nenhum plano, tarefa, código ou coleta antes disso.

**Input**: ADR-002, ADR-003 e ADR-004 (aceitos); limitações declaradas nos EXP-002 e EXP-003 ("só páginas
sintéticas"); `dataset/README.md` (política de privacidade).

**Pré-requisito**: contrato LDF 2.0 aceito (2026-10-12).

**Numeração**: recebe o número 007 porque 004 a 006 já estão reservados no roteiro. A ordem de execução passa a ser
001 → 002 → 003 → **007** → 004 → 005 → 006.

---

## 1. Pergunta e Hipóteses

**Pergunta central:** o que os EXP-002 e EXP-003 mediram em fotografias **simuladas** se mantém em fotografias
**de verdade**, tiradas com celular? Se não, onde quebra: na retificação, nas linhas, nos blocos ou na ordem?

Hoje toda a direção de trabalho (Doc-UFCN para linhas, Heron para blocos, retificação por contorno, ordem por
ancoragem) apoia-se em páginas renderizadas e degradadas por código. Sombra, perspectiva e desfoque foram
imitados, não fotografados. É a maior incerteza do que foi decidido até aqui.

- **H1 (retificação):** a retificação por contorno encontra a folha em ≥ 90 % das fotos.
- **H2 (linhas):** o F1 de linhas do Doc-UFCN `norhand` com retificação fica a no máximo 0,05 do medido no nível
  sintético equivalente (0,920 limpo, 0,845 com degradação forte).
- **H3 (blocos):** o mAP de blocos do Heron fica a no máximo 0,10 do sintético (0,781).
- **H4 (ordem de ponta a ponta):** a acurácia de ordem com layout detectado fica a no máximo 0,10 da sintética (0,77).
- **H5 (condições):** a queda concentra-se em condições identificáveis (luz lateral, ângulo, mão segurando a
  folha), e não é uniforme.

Os limiares são critérios de avaliação. O experimento conclui com veredito explícito para cada hipótese, inclusive
"refutada".

---

## 2. A questão central: de onde vêm as fotos

A política do projeto proíbe fotos do seu acervo pessoal no repositório, e você já decidiu não fornecer amostras
manuscritas pessoais. Há três caminhos compatíveis com isso.

| Opção | Como | Verdade de chão | O que mede | O que não mede |
| :--- | :--- | :--- | :--- | :--- |
| **A — Imprimir e fotografar (recomendada)** | Gero as páginas sintéticas já usadas, você imprime e fotografa com o celular | **Gratuita e exata**: vem do manifesto; só é preciso localizar os quatro cantos da folha em cada foto | Câmera, luz, sombra, perspectiva, desfoque, papel de verdade | Caligrafia real (a letra é de fonte), pauta e textura de caderno |
| **B — Páginas escritas para o teste** | Você copia à mão textos fictícios que eu forneço e fotografa | Precisa ser anotada à mão (caixas de linhas e blocos) | Tudo da opção A mais caligrafia e caderno reais | — |
| **C — Dataset público** | Fotos de páginas manuscritas com licença verificada | Depende do dataset; raramente tem blocos e ordem | Variedade de escritores | Raramente é caderno de estudo; licença costuma ser só pesquisa |

**Recomendação:** começar pela **A**. É a única com verdade de chão exata e sem trabalho de anotação, não envolve
nada pessoal, e isola a variável que nunca foi medida: a fotografia. A **B** fica como segunda fase, pequena
(10 a 15 páginas), se a A confirmar que o pipeline sobrevive à câmera. A **C** só entra se você quiser e depois de
auditoria de licença.

**Custo para você na opção A:** imprimir cerca de 30 páginas e tirar cerca de 90 fotos (cada página em três
condições). Estimativa: 30 a 40 minutos.

---

## 3. Cenários Experimentais

### Cenário 1 — Kit de impressão e protocolo de captura (P1)

Gero um PDF com as páginas a imprimir e um roteiro de captura de uma página: quais condições fotografar, como
nomear os arquivos e onde salvá-los.

**Critério de aceite:** você consegue imprimir e fotografar seguindo só o roteiro, sem perguntar nada.

### Cenário 2 — Registro das fotos com a verdade de chão (P1)

Cada foto é ligada à sua página de origem, e a verdade de chão (linhas, blocos, ordem) é levada para as
coordenadas da foto.

**Critério de aceite:** em uma amostra conferida visualmente, as caixas projetadas caem sobre o conteúdo
impresso com erro de poucos pixels. Fotos em que o registro falha são listadas, não descartadas em silêncio.

### Cenário 3 — Medição com o pipeline dos ADR-002 e ADR-003 (P1)

Os mesmos componentes, pesos, parâmetros e métricas dos experimentos aceitos, sem recalibrar nada nas fotos.

**Critério de aceite:** relatórios no formato dos anteriores, com as saídas gravadas em **LDF 2.0** e válidas.

### Cenário 4 — Comparação sintético × real e análise de falhas (P1)

Tabela lado a lado por métrica e por condição de captura; análise de onde a queda acontece.

**Critério de aceite:** veredito para H1 a H5 e recomendação de próximo passo.

### Cenário 5 — Páginas escritas à mão (P2, opcional)

Só se você aprovar a opção B depois dos resultados do cenário 4.

### Casos de borda

- Foto em que a folha não aparece inteira, ou com dedos e objetos sobre ela.
- Página impressa com escala diferente (margens da impressora).
- Foto na horizontal ou de cabeça para baixo.
- Fotos repetidas da mesma página e condição.
- Metadados do celular (localização, modelo) nos arquivos.

---

## 4. Requisitos

- **FR-001:** As páginas impressas são geradas pelo gerador já existente, com conteúdo fictício e sementes
  registradas; cada uma traz um identificador legível por máquina impresso fora da área de conteúdo.
- **FR-002:** O conjunto de páginas cobre as famílias de layout dos EXP-002/003 (coluna única, nota de margem,
  destaque lateral, caixa gráfica).
- **FR-003:** O protocolo define ao menos três condições de captura por página: boa (de frente, luz uniforme),
  inclinada, e difícil (luz lateral com sombra).
- **FR-004:** As fotos ficam em `dataset/raw/exp-007/`, **fora do Git**. No Git entram só manifesto, hashes e
  métricas.
- **FR-005:** Os metadados EXIF são removidos de qualquer cópia de trabalho; nenhum dado de localização ou do
  aparelho vai para relatórios.
- **FR-006:** Nenhuma foto, recorte ou trecho de imagem é enviado a serviços externos nem exibido em relatório
  versionado. Miniaturas de análise, se houver, ficam fora do Git.
- **FR-007:** O pipeline medido é exatamente o dos ADR-002 e ADR-003. Nenhum parâmetro é ajustado nas fotos; se
  alguma parte do conjunto for usada para ajuste, ela é separada antes e não entra na medição.
- **FR-008:** As métricas são as dos experimentos anteriores (F1 de linhas, mAP de blocos, acurácia de ordem),
  mais taxa de sucesso da retificação e do registro.
- **FR-009:** Os diretórios dos EXP-001 a EXP-003 não são modificados; o que for reaproveitado é copiado, como no
  EXP-003. Ambientes existentes são usados com `--frozen`.
- **FR-010:** Saídas em LDF 2.0, pelo conversor de referência.
- **FR-011:** Sem modelo, peso ou dependência nova. Se alguma se mostrar necessária, a execução para e pergunta.
- **FR-012:** Critérios de parada dos experimentos anteriores (memória, tempo, RAM livre) continuam valendo.

## 5. Critérios de Sucesso

- **SC-001:** Ao menos 80 fotos registradas com verdade de chão, cobrindo todas as famílias e condições.
- **SC-002:** Veredito explícito para H1 a H5, com os números sintéticos de referência ao lado.
- **SC-003:** Análise de falhas que diga em qual etapa cada perda acontece.
- **SC-004:** 100 % das saídas válidas em LDF 2.0.
- **SC-005:** Nenhuma foto no Git; nada fora de `document-intelligence/`; uso de disco dentro do teto de 20 GB.
- **SC-006:** ADR novo ou revisão dos ADR-002/003, conforme o que os dados mostrarem.

## 6. Fora do escopo

- Reconhecimento de texto (não há modelo para português; ADR-001).
- Treinar, ajustar ou trocar modelos.
- Fotos do seu acervo pessoal, em qualquer hipótese.
- Classificação semântica e diagramas (EXP-004 e EXP-005).
- Qualquer integração com o site.

## 7. Limitações já conhecidas

- A opção A não mede caligrafia real nem pauta de caderno: um resultado bom nela é necessário, não suficiente.
- Um celular, uma impressora e um ambiente: pouca variedade de equipamento.
- O registro foto → página introduz erro próprio, que precisa ser medido e reportado junto.

## 8. Perguntas para o usuário

1. **Origem das fotos:** opção A (imprimir e fotografar), como recomendo? Você tem impressora à mão?
2. **Quantidade:** cerca de 30 páginas em três condições (90 fotos) está bom, ou prefere um conjunto menor para
   começar (por exemplo, 12 páginas, 36 fotos)?
3. **Fase B:** fica combinada como opcional, a decidir depois dos resultados, ou você prefere descartá-la desde já?
4. **Numeração:** concorda com EXP-007, mantendo 004 a 006 como estão no roteiro?
