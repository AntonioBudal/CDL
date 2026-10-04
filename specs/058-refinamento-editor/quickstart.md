# Guia de Validação Rápida: F 0.7.9 — Refinamento do Editor de Estudos e Correção de Ícones de Categorias

**Feature**: F 0.7.9 — Refinamento do Editor de Estudos  
**Branch**: `058-refinamento-editor`  
**Date**: 2026-10-04  

Este documento descreve 5 cenários práticos de teste fim a fim para validar todas as capacidades entregues na Feature F 0.7.9.

---

## Cenário 1: Navegação Focada por Abas de Seções no Mobile e Desktop

### Objetivo
Validar que o leitor consegue focar em uma única seção analítica por vez, reduzindo o comprimento vertical da página, com opção de alternar para visualização contínua.

### Passos de Teste
1. Abrir a rota de edição de um estudo existente (ex.: `/#/books/1/studies/10/edit`).
2. Observar a barra superior de abas: `Resumo`, `Explicação`, `Conceitos`, `Referências` e `Notas`.
3. Clicar na aba **Conceitos**:
   - Apenas o campo "Conceitos centrais" e sua toolbar de Markdown devem estar visíveis.
   - O indicador de conteúdo (ponto sutil) deve estar ativo se houver texto prévio.
4. Clicar no botão toggle **"Ver todas as seções"**:
   - Todas as 5 caixas de texto devem expandir em sequência contínua (estilo tradicional).
5. Retornar ao modo **"Focado"**:
   - A visualização volta imediatamente a exibir somente a seção selecionada.

---

## Cenário 2: Alternância Instantânea "Editar / Prévia" In-Place

### Objetivo
Confirmar que o leitor pode conferir a renderização do Markdown sem sair do formulário ou abrir janelas modais.

### Passos de Teste
1. Na seção ativa (ex.: "Explicação"), digitar uma citação e uma lista:
   ```markdown
   > O conhecimento é uma construção constante.
   - Ponto de apoio A
   - Ponto de apoio B
   ```
2. Clicar no botão **"Prévia"** no cabeçalho da seção.
3. **Resultado Esperado**:
   - A caixa de edição é substituída in-place por uma área de leitura formatada em HTML.
   - A citação exibe a borda lateral de citação e a lista exibe marcadores estilizados.
4. Clicar em **"Editar"**:
   - A textarea reaparece com o texto intacto e o foco do cursor pronto para digitação.

---

## Cenário 3: Formatação Tátil Móvel (44px) e Atalhos de Teclado

### Objetivo
Garantir que a toolbar de formatação seja confortável no toque e que atalhos como `Ctrl+B`, `Ctrl+I` e `Ctrl+K` funcionem perfeitamente.

### Passos de Teste
1. No Desktop:
   - Selecionar uma palavra na textarea e pressionar `Ctrl+B`.
   - O texto torna-se `**palavra**`.
   - Selecionar outra palavra e pressionar `Ctrl+I` (torna-se `*palavra*`).
   - Pressionar `Ctrl+K` (insere sintaxe de link `[palavra](url)`).
2. Emular dispositivo móvel (largura 375px no DevTools):
   - Inspecionar a barra `MarkdownToolbar.vue`.
   - Constatar que os botões possuem área de clique $\ge 44 \times 44$px.
   - A barra desliza suavemente na horizontal caso não caibam todos os botões na tela.

---

## Cenário 4: Preservação e Restauração de Rascunho via `sessionStorage`

### Objetivo
Validar que recarregar a página ou fechar a aba acidentalmente não causa perda do texto digitado.

### Passos de Teste
1. Digitar um parágrafo novo no campo de anotações: *"Reflexão temporária não salva..."*.
2. Aguardar 1 segundo para o debounce do rascunho persistir no `sessionStorage`.
3. Recarregar o navegador (`F5` ou `Ctrl+R`).
4. **Resultado Esperado**:
   - O formulário carrega e restaura automaticamente o texto digitado.
   - Um banner discreto no topo informa: *"Rascunho não salvo recuperado. [Descartar rascunho]"*.
5. Clicar em **"Descartar rascunho"**:
   - O formulário reverte imediatamente aos dados persistidos no banco.
6. Digitar novamente e clicar em **"Salvar alterações"**:
   - O estudo é salvo no backend e a chave no `sessionStorage` é limpa.

---

## Cenário 5: Adição e Remoção de Categorias com Ícones Padronizados

### Objetivo
Validar que os ícones do seletor e badges de categorias estão perfeitamente renderizados, sem SVGs cortados ou desalinhados.

### Passos de Teste
1. Acessar a edição de livro ou estudo onde `CategoryInput.vue` é exibido.
2. Observar o campo de busca com ícone padronizado via `<Icon />`.
3. Digitar uma categoria e pressionar `Enter` para adicionar:
   - O badge aparece com o nome da categoria e um botão de remover em formato de `x`.
   - O ícone `x` está centralizado verticalmente, sem deformações visuais.
4. Passar o mouse / focar com o teclado e clicar no botão `x`:
   - A categoria é removida com suavidade.
   - O botão possui `aria-label="Remover categoria [Nome]"`.
