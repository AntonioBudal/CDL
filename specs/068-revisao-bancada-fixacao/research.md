# Research & Architecture Decisions: F0.8.03 — Revisão: Bancada de Fixação Cognitiva

**Feature Branch**: `068-revisao-bancada-fixacao` | **Date**: 2026-10-11 | **Spec**: [spec.md](spec.md)

Este documento registra as decisões arquiteturais, justificativas e alternativas avaliadas para o redesign da Central de Revisão no Roadmap 0.8 do Leitorum.

---

## Decisão 1: Barra Unificada de Prontidão Intelectual vs. 5 Cards Numéricos de SaaS

- **Decisão**: Substituir os 5 cards isolados com números "0" destacados em cores saturadas por um componente coeso (`ReviewStatsHeader.vue` / `ReviewReadinessBar.vue`) que sintetiza:
  1. Volume de cartões elegíveis para o dia atual.
  2. Estimativa de tempo de estudo em minutos (calibrada em média de 30 a 45 segundos por cartão).
  3. Divisão proporcional discreta entre Perguntas reflexivas e Termos ocultos (*clozes*).
  4. Botão primário de destaque ("Praticar Revisão Agora") centralizado ou alinhado de forma evidente.
- **Justificativa**: O formato atual de 5 caixas retangulares simula um dashboard de monitoramento de servidor ou faturamento de SaaS, quebrando a serenidade do leitor e fragmentando dados que fazem parte de um mesmo juízo: *“Quantos itens tenho para hoje e quanto tempo vou precisar dedicar?”*.
- **Alternativas consideradas**:
  - *Manter os 5 cards com cores menos saturadas:* Rejeitado porque a proliferação de 5 caixas retangulares polui a tela em laptops e tablets, ocupando espaço vertical desnecessário.
  - *Ocultar todas as métricas:* Rejeitado porque o leitor precisa de previsibilidade sobre o compromisso diário antes de iniciar a sessão.

---

## Decisão 2: Transição de Virada de Cartão e Cinemática com Respeito a `prefers-reduced-motion`

- **Decisão**: Implementar o efeito de revelação da resposta no cartão de estudo (`ReviewCard.vue`) com transição suave baseada em `opacity` e `transform: translateY` ou rotação suave limitada a 200–250ms a 60 FPS, com desativação imediata quando o leitor tem movimento reduzido ativado.
- **Justificativa**: A virada do cartão deve trazer a sensação tátil de um fichário real de estudo, sem lentidão que impeça sessões ágeis de revisão. O uso restrito de propriedades aceleradas por GPU (`transform` e `opacity`) garante performance sem travamentos.
- **Alternativas consideradas**:
  - *Virada 3D complexa (`rotateY(180deg)`) com perspectiva pesada:* Rejeitado porque causa problemas de renderização de fontes e subpixel antialiasing em navegadores WebKit/Chromium em resoluções intermediárias e atrasa a revisão rápida.
  - *Troca estática sem transição:* Rejeitado porque perde o feedback visual tátil do método de Active Recall.

---

## Decisão 3: Ergonomia Operacional por Teclado Global

- **Decisão**: Dotar a bancada de revisão de atalhos de teclado de primeira classe durante a sessão ativa:
  - `Espaço`: Revela a resposta do cartão atual (verso).
  - Teclas `1`, `2`, `3`, `4`: Registram a avaliação de facilidade (1 = Errei, 2 = Difícil, 3 = Bom, 4 = Fácil) e avançam para o próximo cartão.
  - Desativação defensiva de atalhos caso o usuário esteja com foco em inputs de texto ou diálogos modais.
- **Justificativa**: Praticantes de repetição espaçada revisam dezenas de itens por dia; obrigar o uso do mouse para cada clique de revelação e classificação desacelera o ritmo cognitivo e causa fadiga motora.
- **Alternativas consideradas**:
  - *Apenas atalhos de letras (`E` para errei, `F` para fácil):* Rejeitado porque as teclas numéricas `1-4` seguem a convenção ergonômica universal de repetição espaçada (Anki, SuperMemo) e permitem posicionamento confortável de uma só mão no teclado numérico ou linha superior.

---

## Decisão 4: Estado Vazio Pedagógico com Demonstração Interativa de Termo Oculto

- **Decisão**: Criar o componente `ReviewPedagogicalEmpty.vue` para substituir mensagens genéricas de "Nenhum item" e contadores zerados. O componente exibe:
  1. Uma frase-modelo elegante simulando uma passagem de leitura com uma lacuna camuflada (`[termo oculto]`).
  2. Ao clicar ou tocar na lacuna, ela se desfaz suavemente revelando o termo original, com uma mensagem explicativa: *"Você acabou de praticar Active Recall com um termo oculto"*.
  3. Guia prático de 3 passos ilustrando como grifar textos durante a leitura para abastecer a bancada.
- **Justificativa**: Usuários recém-chegados ao Leitorum muitas vezes não sabem como surgem os cartões de revisão. Um exemplo vivo interativo ensina o conceito em menos de 5 segundos de forma memorável e prazerosa.
- **Alternativas consideradas**:
  - *Texto explicativo estático em parágrafos:* Rejeitado por ser tedioso e raramente lido.
  - *Vídeo ou GIF animado:* Rejeitado por peso de assets, dependência externa e quebra de fidelidade com os 10 temas visuais.

---

## Decisão 5: Conclusão Serena da Rodada e Preservação de Histórico

- **Decisão**: Ao zerar os cartões da sessão, transicionar o fluxo para um painel comemorativo calmo (`ReviewSessionSummary.vue` / `ReviewSummaryModal.vue`), apresentando:
  - Mensagem de encorajamento serena sem confetes invasivos.
  - Métricas da sessão recém-concluída: total de cartões, tempo investido e balanço das respostas.
  - Acesso à aba "Histórico de Sessões" com listagem visualmente refinada de ciclos de estudo passados.
- **Justificativa**: O reforço positivo do estudo deve ser sóbrio e contemplativo, em linha com o manifesto editorial do Leitorum, valorizando a constância em vez de gamificação infantilizada.
- **Alternativas consideradas**:
  - *Redirecionar bruscamente para a página inicial:* Rejeitado porque impede o leitor de assimilar o resultado da sessão e gera desorientação.
  - *Gamificação com pontos e níveis:* Rejeitado por violar o princípio de imersão e foco duradouro do produto.
