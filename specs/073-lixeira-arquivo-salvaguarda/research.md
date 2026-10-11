# Pesquisa e Decisões Técnicas: Lixeira — Arquivo de Salvaguarda e Segurança

Este documento consolida as pesquisas técnicas, decisões de arquitetura e padrões ergonômicos para a implementação da Feature F0.8.8 (Feature 08 do Roadmap 0.8).

---

## 1. Indicador Visual de Contagem Regressiva e Retenção de 30 Dias

### Contexto
Atualmente, os itens descartados apresentam um badge textual simples (`Expurgo em X dias`), sem senso imediato de urgência ou visualização de progressão temporal.

### Decisão
Implementar um componente visual de retenção temporal composto por:
1. **Badge de Retenção com Barra de Progresso Sutil ou Anel Visual**:
   - Exibição destacada da quantidade de dias restantes: `30 - dias_descartado`.
   - Cálculo de completude: `percentual_decorrido = clamp(((30 - days_until_purge) / 30) * 100, 0, 100)%`.
   - Barra de linha fina na base do badge ou indicador circular de preenchimento proporcional ao tempo transcorrido.
2. **Nível de Urgência Estilizado**:
   - Normal (`> 5` dias): Tons neutros/amparados pelo tema (`var(--color-text-muted)` e `var(--color-surface)`).
   - Urgente (`<= 5` dias): Destaque em tom de alerta (`var(--color-danger, #e53e3e)` ou amarelo/laranja de atenção), com texto em negrito e ícone sutil de ampulheta/relógio (`clock`).

### Racional
Proporciona clareza instantânea ao leitor, permitindo distinguir em milissegundos itens recém-descartados daqueles em risco iminente de expurgo permanente.

### Alternativas Consideradas
- *Exibir apenas data exata de descarte*: Rejeitado porque exige esforço mental do usuário para calcular quando a exclusão automática ocorrerá.
- *Modal de contagem regressiva ao abrir a página*: Rejeitado por ser intrusivo e bloquear o fluxo de navegação.

---

## 2. Barra Flutuante de Ações em Lote (Floating Batch Action Bar)

### Contexto
O usuário precisa de uma forma rápida e intuitiva de marcar múltiplos itens e acionar restauração ou exclusão em massa sem repetição monótona.

### Decisão
Implementar uma barra flutuante de ações (`.trash-batch-bar`) fixada na parte inferior central da viewport:
1. **Transição de Entrada/Saída**:
   - `transition: transform 200ms cubic-bezier(0.16, 1, 0.3, 1), opacity 200ms ease`.
   - Oculta: `transform: translateY(100%) translateY(20px)`, `opacity: 0`.
   - Ativa: `transform: translateY(0)`, `opacity: 1`.
2. **Estrutura de Controles**:
   - Contador dinâmico: `X selecionados` (com variação singular/plural).
   - Botão de alternância: `Selecionar todos` / `Desmarcar todos` sincronizado com a aba ativa (`all`, `books`, `studies`).
   - Botão `Restaurar selecionados`: Dispara a restauração concorrente dos itens marcados com barra/spinner de progresso.
   - Botão `Excluir definitivamente`: Abre modal de confirmação reforçada quantificando livros e estudos selecionados.
   - Botão de fechar/cancelar seleção (`x`) ou tecla `Escape`.
3. **Acessibilidade e Semântica**:
   - `role="region"`, `aria-label="Ações em lote da lixeira"`.
   - Ativação por teclado (tecla `Espaço` nos checkboxes e atalhos claros).

### Racional
A barra flutuante é o padrão de ouro de ergonomia para ações em lote em interfaces modernas, evitando poluir o cabeçalho fixo quando nenhum item está marcado.

### Alternativas Consideradas
- *Ações em lote fixas no topo da tabela*: Rejeitado porque consome espaço vertical constante mesmo quando o usuário está apenas visualizando os itens.

---

## 3. Barreira Deliberada e Confirmação de Expurgo Permanente

### Contexto
A exclusão definitiva de registros no banco de dados SQLite local é irreversível. O botão "Esvaziar lixeira" e os botões de exclusão definitiva não podem permitir cliques acidentais.

### Decisão
Aprimorar `TrashConfirmModal.vue`:
1. **Semântica WAI-ARIA**:
   - Atualizar `role="alertdialog"` para diálogos perigosos (`danger: true`), conforme WCAG 2.1 e padrões WAI-ARIA Authoring Practices.
2. **Foco e Retenção (*Focus Trap*)**:
   - Ao abrir em modo `danger`, o foco inicial vai obrigatoriamente para o botão de `Cancelar` (evitando confirmação por clique distraído na tecla Enter).
   - Fechamento imediato com tecla `Escape`.
3. **Detalhamento Quantitativo**:
   - Para esvaziamento total: Explicitar quantos livros e quantos estudos serão destruídos.
   - Para exclusão em lote: Mensagem exata discriminando: `"Tem certeza de que deseja excluir definitivamente X livros e Y estudos? Esta ação é irreversível."`.

### Racional
Garante proteção máxima do acervo e respeito estrito ao Artigo I da Constituição do Projeto ("Proteção Absoluta do Acervo").

### Alternativas Consideradas
- *Exigir digitação da palavra "EXCLUIR"*: Considerado excessivamente burocrático para uma aplicação pessoal monousuário/local, embora o modal com botão focado em cancelar forneça o equilíbrio perfeito entre segurança e fluidez.

---

## 4. Animação de Saída e Feedback na Restauração

### Contexto
Quando o usuário restaura um item, a remoção instantânea da lista causa descontinuidade visual (salto no layout).

### Decisão
1. **Transição Suave de Saída**:
   - Aplicar classe CSS de restauração ativa (`.is-restoring`):
     `transform: translateY(-20px); opacity: 0; transition: transform 180ms ease-out, opacity 180ms ease-out;`.
   - Remover o item do estado reativo do frontend logo após a conclusão da animação (180ms).
2. **Atualização Imediata de Contadores**:
   - Decrementar localmente os contadores da aba correspondente e do total sem esperar requisição de recarga completa da página.
3. **Notificação Informativa (*Toast*)**:
   - Exibir mensagem amigável: `"Livro 'X' restaurado com sucesso para o acervo ativo!"`.
   - Para estudos cujo livro de origem também estava na lixeira: `"Estudo 'Y' restaurado! O livro ancestral também foi reativado no acervo ativo."` (aproveitando o campo `book_restored` já retornado pela API).

### Racional
Elimina qualquer sensação de lentidão e fornece clareza total sobre o destino do item restaurado.

---

## 5. Estratégia de Execução em Lote

### Contexto
Avaliar se a restauração e exclusão em lote devem ocorrer via orquestração concorrente no frontend ou via novo endpoint dedicado no backend.

### Decisão
Utilizar orquestração no frontend com chamadas paralelas/concorrentes às rotas REST existentes (`Promise.allSettled`), com tratamento granular de erros:
- Para restauração: Executar `api.restoreBook` e `api.restoreStudy` em paralelo para os IDs selecionados.
- Para exclusão definitiva: Executar `api.permanentDeleteBook` e `api.permanentDeleteStudy` em paralelo para os IDs selecionados.
- Após a conclusão do lote:
  - Recarregar a lista da lixeira (`loadTrash()`).
  - Limpar a seleção ativa.
  - Emitir notificação consolidada de sucesso (ex.: `"5 itens restaurados com sucesso!"` ou alerta caso algum item falhe).

### Racional
- Mantém o backend e os testes de API 100% estáveis e compatíveis com as versões anteriores.
- Dá visibilidade granular sobre o progresso e simplifica a manutenção.

---

## 6. Conformidade com o Sistema Visual e Constituição

- **Zero Emojis**: Utilizar exclusivamente componentes `<Icon name="..." />` da biblioteca `lucide-vue-next` (ex.: `trash`, `clock`, `check-square`, `square`, `rotate-ccw`, `alert-triangle`, `x`).
- **Tokens Semânticos**: Uso estrito das variáveis CSS do sistema (`--color-page`, `--color-surface`, `--color-text`, `--color-text-muted`, `--color-border`, `--color-primary`, `--color-danger`).
- **Alvos de Toque**: Todos os botões e checkboxes possuem dimensão mínima de 44x44px em telas sensíveis ao toque.
