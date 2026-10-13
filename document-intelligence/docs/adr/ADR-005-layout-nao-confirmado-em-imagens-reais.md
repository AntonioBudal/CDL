# ADR-005: A direção de layout do ADR-002 não se confirma em imagens reais; benchmark real passa a ser obrigatório

* **Status:** ACCEPTED (aceito pelo usuário em 2026-10-13)
* **Data:** 2026-10-13
* **Decisores:** Usuário (decisão); Claude Code (proposta)
* **Experimento de Suporte:** [EXP-007](../../experiments/EXP-007/RESULTS.md)
* **Status de Licença:** componentes do pipeline `LICENSE STATUS: VERIFIED` (os do ADR-002). Evidência: GNHK, CC-BY-4.0 conforme declarado — `VERIFIED`; BRESSAY — `LICENSE STATUS: NEEDS VALIDATION`, uso experimental local autorizado pelo usuário, **não pode embasar decisão de produto**. As conclusões abaixo se sustentam só com o GNHK onde indicado.

---

## 1. Contexto e Declaração do Problema

O ADR-002 definiu a direção de trabalho para layout (Doc-UFCN `norhand` para linhas, Docling Heron para blocos,
retificação por contorno) e o ADR-003, a ordem de leitura por ancoragem. Os dois se apoiaram só em páginas
sintéticas: texto em fonte manuscrita, fotografia simulada por código. Os próprios relatórios registraram isso
como a principal limitação.

O EXP-007 mediu o mesmo pipeline, sem nenhum ajuste, em 172 fotos de celular de anotações manuscritas (GNHK) e em
185 páginas de redações manuscritas em português (BRESSAY).

---

## 2. Drivers de Decisão (Critérios de Avaliação)

* **Driver 1:** A decisão de layout precisa valer para imagens reais, não para o gerador sintético.
* **Driver 2:** Local-first, licenças verificadas, sem dependência nova.
* **Driver 3:** Não promover nem descartar componente sem medição.
* **Driver 4:** Evitar que o erro se repita nos próximos experimentos.

---

## 3. Opções Consideradas

### Opção A: Manter o ADR-002 como está e seguir para o EXP-004

Ignora a evidência: o F1 de linhas medido em imagens reais é menos da metade do sintético.

### Opção B: Rejeitar o ADR-002 por inteiro

Vai além do que os dados mostram. O Doc-UFCN localiza o texto (poucas linhas não vistas); o Heron localiza o bloco
de texto com boa precisão geométrica; nenhum componente foi comparado com alternativas em dados reais.

### Opção C: Rebaixar o ADR-002 a hipótese não confirmada, suspender a retificação e exigir benchmark real

Registra o que foi medido, mantém os componentes como candidatos e muda a regra de evidência daqui em diante.

---

## 4. Decisão Escolhida

**Opção C.**

1. **Linhas — o Doc-UFCN `norhand`, usado como está, não é adequado.** F1 de 0,345 em fotos de celular e 0,372 em
   caligrafia portuguesa, contra 0,78 a 0,93 no sintético. O detector acha o texto, mas parte cada linha em
   fragmentos (1,5 caixa por linha). Ele continua candidato, mas só acompanhado de pós-processamento e comparado
   com alternativas em dados reais.
2. **Retificação por contorno — suspensa.** Devolveu um quadrilátero em 100 % das fotos e piorou o resultado em
   todas as faixas (0,345 → 0,239 no geral). Só volta a ser considerada com um critério que diga quando há de fato
   uma folha inteira a endireitar, medido em fotos reais.
3. **Blocos — o Heron fica como detector da região de texto, não de parágrafos.** Em texto manuscrito corrido ele
   devolve um bloco único. Sua capacidade de separar título, nota de margem e caixa gráfica em caderno real
   **continua sem medição**.
4. **Ordem de leitura — o ADR-003 se mantém** no que afirma: o método não erra quando recebe os blocos certos. O
   gargalo continua sendo a detecção, agora com mais peso.
5. **Regra nova de evidência:** nenhum componente de layout é adotado como direção de trabalho sem medição em
   imagens reais. As divisões de teste do GNHK e do BRESSAY usadas no EXP-007 passam a ser o benchmark de
   referência para linhas. As páginas sintéticas ficam para testes de regressão e para o que só elas permitem
   (ordem com notas de margem), nunca como única evidência.
6. **Efeito sobre o ADR-002:** com o aceite deste ADR (2026-10-13), o ADR-002 passa a `SUPERSEDED por ADR-005` nos itens 1 e 2,
   e recebe uma nota no item 3. Nada disso altera os diretórios dos experimentos aceitos.

Nada é promovido a produto.

---

## 5. Evidência Empírica do Experimento

Benchmark do commit `8bf4e5f`, árvore limpa; pipeline e parâmetros idênticos aos dos ADR-002 e ADR-003.

| Métrica | Sintético | GNHK (fotos) | BRESSAY (português) |
| :--- | ---: | ---: | ---: |
| F1 de linhas, sem retificação | 0,784 a 0,928 | 0,345 | 0,372 |
| F1 de linhas, com retificação | 0,845 | 0,239 | — |
| F1 de linhas com fusão ideal de fragmentos (teto) | — | 0,535 | 0,712 |
| Blocos | mAP50 0,781 (com classe) | — | F1 0,354; AP50 0,334 (sem classe) |
| Ordem com blocos detectados | 0,773 | — | 0,239 |
| Ordem só nos blocos casados | 0,950 | — | 1,000 |
| Tempo por página | 4,6 s | 5,0 s | 5,5 s |

* Das linhas verdadeiras não casadas, só 3 % a 7 % não foram vistas; 39 % a 67 % foram partidas em fragmentos.
* Dos parágrafos não casados no BRESSAY, 99 % estão dentro de um bloco detectado maior.
* As 542 saídas foram gravadas em LDF 2.0 e são todas válidas.
* A conclusão sobre linhas se sustenta só com o GNHK (`VERIFIED`); o BRESSAY a reforça e é a única fonte sobre
  blocos e ordem.

---

## 6. Consequências

### Consequências Positivas

* A maior incerteza do projeto deixou de ser desconhecida: foi medida, e é grande.
* Existe agora um benchmark real, reproduzível e com verdade de chão, para qualquer candidato de linhas.
* O contrato LDF 2.0 e o harness aguentaram dados reais sem mudança.

### Consequências Negativas / Trade-offs

* **Não há hoje componente de linhas que funcione em caligrafia real.** Somado ao ADR-001 (não há reconhecedor
  para português), o pipeline não tem nenhuma etapa validada em dados reais. Um primeiro teste no site fica mais
  distante do que os resultados sintéticos sugeriam.
* O EXP-004 (classificação semântica) e o EXP-005 (diagramas) dependem de linhas e blocos; fazê-los antes de
  resolver a detecção produziria números sobre uma base que não se sustenta.
* **Os benchmarks reais não são o caso de uso:** o GNHK é em inglês e não é caderno; o BRESSAY não é foto e tem
  licença em validação. Página de caderno brasileiro fotografada e ordem com notas de margem seguem sem medição.
* A verdade de chão de linha do GNHK é derivada, e o critério de IoU com a linha inteira pune fragmentos que um
  reconhecedor talvez aproveitasse. A queda medida pode estar um pouco exagerada; a direção dela não está em dúvida.

### Próximo passo sugerido (não decidido aqui)

Um experimento de detecção de linhas em dados reais: o Doc-UFCN com fusão de fragmentos, um método clássico e os
candidatos com licença verificada que rodem por wheels, com a divisão de treino do GNHK para calibrar e as de teste
do GNHK e do BRESSAY para medir.

### Conformidade com a Constituição

* [x] Local-first: nenhum serviço externo; o único download foi o dataset, autorizado.
* [x] Evidência antes de decisão: nada calibrado nos dados de teste; a decisão rebaixa uma direção anterior com
  base em medição.
* [x] Licenças: estados declarados em todos os relatórios; o BRESSAY não embasa produto.
* [x] Privacidade: nada do acervo do usuário; conteúdo de terceiros fora do Git e dos relatórios.
* [x] LDF como contrato: saídas em 2.0; lacuna (um componente por etapa) registrada, contrato intocado.
