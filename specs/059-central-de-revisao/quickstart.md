# Guia de Validação Rápida: F 0.7.10 — Central de Revisão de Perguntas e Clozes

**Feature**: F 0.7.10 — Central de Revisão de Perguntas e Clozes  
**Branch**: `059-central-de-revisao`  
**Date**: 2026-10-04  

Este documento descreve 5 cenários práticos de teste fim a fim para validar todas as capacidades entregues na Central de Revisão de Perguntas e Clozes.

---

## Cenário 1: Acesso ao Hub de Revisão e Visualização de Estatísticas Globais

### Objetivo
Validar que a nova rota `/review` exibe o painel consolidado com a contagem exata de itens interativos do usuário ativo.

### Passos de Teste
1. Acessar o sistema e clicar no novo item **"Revisão"** no menu principal de navegação.
2. Observar os cards de métricas no topo:
   - Total de itens interativos elegíveis.
   - Distribuição entre Perguntas de Fixação e Termos Ocultos (clozes).
   - Contagem de itens revisados no dia de hoje.
3. **Resultado Esperado**:
   - Os números refletem com fidelidade os destaques ativos do acervo.
   - Se não houver itens cadastrados, um estado vazio acolhedor orienta como criar perguntas nos estudos.

---

## Cenário 2: Filtragem por Livro e Início de Sessão em Bloco de 10 Itens

### Objetivo
Confirmar que o leitor pode focar seus estudos em uma obra específica e iniciar um bloco padrão de 10 cards.

### Passos de Teste
1. No seletor de livros do painel de revisão, selecionar um livro com perguntas cadastradas.
2. Observar a atualização dinâmica do botão de ação primária: *"Iniciar Revisão (10 de X itens)"*.
3. Clicar no botão **"Iniciar Revisão"**.
4. **Resultado Esperado**:
   - A interface entra em modo de estudo imersivo em tela limpa.
   - O indicador de progresso no topo exibe "1 de 10 (10%)".
   - Apenas itens pertencentes ao livro selecionado são apresentados.

---

## Cenário 3: Resolução de Pergunta com Atalhos de Teclado no Desktop

### Objetivo
Garantir a operação rápida e confortável via teclado (`Barra de Espaço` para revelar e `1`, `2`, `3` para classificar).

### Passos de Teste
1. Na visualização de um card do tipo pergunta, ler o enunciado:
   - A resposta esperada permanece oculta.
   - Os botões de classificação (*Difícil*, *Médio*, *Fácil*) estão desabilitados.
2. Pressionar a **Barra de Espaço**:
   - A resposta oculta surge imediatamente com animação sutil.
   - Os botões de classificação tornam-se interativos.
3. Pressionar a tecla numérica **`3`** (Fácil):
   - O sistema registra a avaliação `easy`.
   - Um leitor de tela anuncia o registro da resposta.
   - O card avança automaticamente para o item "2 de 10".

---

## Cenário 4: Resolução de Termo Oculto (Cloze) no Mobile

### Objetivo
Validar que a interface móvel (< 768px) é confortável para uso com uma só mão e alvos táteis mínimos de $44 \times 44$px.

### Passos de Teste
1. Emular dispositivo móvel (largura 375px no navegador) ou acessar via celular em rede local.
2. Quando um card de termo oculto for apresentado:
   - O texto exibe a lacuna estilizada `[...]`.
   - O botão inferior "Revelar Resposta" possui altura mínima de 44px e ocupa a largura necessária para o polegar.
3. Tocar em "Revelar Resposta":
   - A lacuna `[...]` é preenchida pelo termo correto com destaque visual suave.
4. Tocar no botão **"Médio"**:
   - A avaliação `medium` é persistida com feedback tátil e avanço para o próximo item.

---

## Cenário 5: Conclusão da Rodada, Métricas de Retenção e Continuação

### Objetivo
Validar o fechamento de ciclo após a resolução do 10º card do bloco.

### Passos de Teste
1. Responder aos cards restantes até atingir 10 de 10.
2. Ao classificar o último card:
   - A interface exibe a tela de celebração e conclusão da rodada.
   - Exibição do gráfico/balanço:
     - Quantidade e percentual de itens fáceis (verde).
     - Quantidade e percentual de itens médios (amarelo).
     - Quantidade e percentual de itens difíceis (vermelho/coral).
3. Clicar em **"Revisar mais 10"**:
   - Uma nova rodada é montada com os próximos itens pendentes na fila de prioridade.
4. Clicar em **"Voltar ao Caderno"**:
   - O usuário retorna à tela inicial de livros com as estatísticas do dia atualizadas.
