# Quickstart: Validação da Feature 013 (Dashboard de Leitura com Calendário e Timeline)

**Feature**: `013-dashboard-calendario-timeline`  
**Date**: 2026-09-19  
**Status**: Approved  

---

## 1. Cenário 1: Visualização Inicial e Estado Vazio Acolhedor

**Objetivo:** Garantir que um acervo sem estudos ou livros carregue o Dashboard com segurança e sem quebras visuais.

1. Inicie a aplicação via `python iniciar.py` ou ambiente de testes.
2. Acesse a rota `/dashboard` pelo menu superior.
   - *Resultado esperado*:
     - O Dashboard abre instantaneamente (< 1s).
     - Os cartões de resumo exibem contadores zerados de forma limpa: `0 livros`, `0 estudos`, `0 dias ativos`, `0 dias de sequência`.
     - Um estado vazio explicativo é exibido com botão direto convidando o leitor a importar ou cadastrar sua primeira obra.
     - Nenhum erro de renderização ou valor indefinido (`NaN` ou `undefined`) aparece na interface.

---

## 2. Cenário 2: Adição de Livros e Estudos com Atualização de Métricas

**Objetivo:** Verificar o cálculo matemático das métricas de produtividade.

1. Cadastre um novo livro (ex.: "Dom Casmurro").
2. Crie dois estudos em capítulos distintos do livro.
3. Edite as anotações de um dos estudos para salvar uma revisão.
4. Abra o Dashboard em `/dashboard`.
   - *Resultado esperado*:
     - O cartão "Livros no acervo" exibe `1`.
     - O cartão "Estudos concluídos" exibe `2`.
     - O cartão "Dias com estudo" exibe `1`.
     - A "Sequência atual" indica `1 dia`.
     - A média de estudos por livro indica `2.0`.

---

## 3. Cenário 3: Mapa de Calor Visual e Responsividade Mobile

**Objetivo:** Comprovar a escala de 4 intensidades do heatmap e a alternância responsiva entre desktop e mobile.

1. No desktop (largura > 768px), visualize o bloco do mapa de calor.
   - *Resultado esperado*: A grade exibe o panorama anual de ~52 semanas com legendas dos meses e dias da semana.
2. Redimensione a janela para resolução mobile (< 640px) ou inspecione com simulação de smartphone.
   - *Resultado esperado*: O calendário adota automaticamente o recorte condensado dos últimos 3 a 4 meses, com células confortáveis para o toque (> 18px).
3. Clique no botão "Ver ano completo".
   - *Resultado esperado*: O calendário expande permitindo rolagem horizontal suave sem deformar o restante da página.
4. Passe o cursor (ou toque) sobre o dia atual.
   - *Resultado esperado*: Uma dica de contexto (tooltip) exibe a data formatada e a contagem exata de atividades.

---

## 4. Cenário 4: Interação de Filtro por Data e Timeline de Atividades

**Objetivo:** Validar o filtro interativo entre o heatmap e a lista cronológica reversa.

1. Na seção da Timeline, verifique a listagem dos eventos recentes:
   - *Resultado esperado*: A lista exibe os eventos em ordem cronológica decrescente com etiquetas distintas ("Novo livro", "Novo estudo", "Anotação revisada"), links clicáveis e carimbos relativos ("hoje", "ontem").
2. Clique em uma célula específica do mapa de calor que possua atividade.
   - *Resultado esperado*:
     - A timeline é filtrada em menos de 100ms, exibindo apenas as ações daquela data.
     - Um banner com chip informativo é exibido: "Filtrando por: DD de Mês de AAAA" com botão "Limpar filtro".
3. Clique em "Limpar filtro".
   - *Resultado esperado*: A timeline volta a exibir o histórico completo.

---

## 5. Cenário 5: Respeito Estrito à Lixeira (Soft Delete e Restauração)

**Objetivo:** Comprovar a regra Q3 (Opção A): itens na lixeira deixam de pontuar imediatamente e retornam ao serem restaurados.

1. Anote os valores atuais do Dashboard (ex.: 2 estudos, 1 dia ativo).
2. Acesse o livro e mova um dos estudos para a lixeira.
3. Retorne ao Dashboard em `/dashboard`.
   - *Resultado esperado*:
     - O total de estudos é recalculado imediatamente para `1`.
     - O evento do estudo excluído não aparece mais na timeline nem pontua na contagem da célula do heatmap daquele dia.
4. Acesse a Lixeira (`/lixeira`) e restaure o estudo excluído.
5. Retorne ao Dashboard.
   - *Resultado esperado*: O estudo reaparece na timeline e seus pontos históricos retornam ao cálculo com total fidelidade.
