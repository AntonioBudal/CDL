# Research: F0.7.13 — Caixa de Entrada de Capturas (Inbox de Conhecimento)

## Decisões Técnicas e Arquiteturais

### 1. Modelo de Dados e Ciclo de Vida de Status

- **Decisão**: Criar a tabela dedicada `inbox_captures` com a máquina de estados simples: `inbox` (pendente/ativo), `promoted` (convertido em novo estudo formal), `linked` (anexado como nota a um estudo existente) e `archived` (descartado/arquivado sem exclusão física imediata).
- **Racional**:
  - Permite separar radicalmente o momento do "descarrego mental rápido" da formalização conceitual em 4 seções.
  - O status `promoted` preserva a rastreabilidade através de `promoted_study_id`, permitindo saber no futuro de onde veio determinado estudo.
  - O status `linked` mantém o registro histórico da ideia original mesmo após ter sido incorporada a um estudo já existente.
- **Alternativas consideradas**:
  - Salvar capturas diretamente como `studies` com flag `is_draft=True`: Poluiria a tabela de estudos, exigiria burlar as regras de obrigatoriedade de 4 seções de análise e forçaria a criação de livros/capítulos fictícios para notas avulsas.
  - Usar localStorage do navegador: Perderia sincronização multiusuário/multidispositivo e violaria a garantia de preservação de dados do sistema.

---

### 2. Modal Global e Captura Sem Interrupção do Fluxo

- **Decisão**: Implementar `QuickCaptureModal.vue` acoplado ao layout principal (`App.vue`) através do composable global `useQuickCapture()`, com gatilho por atalho universal `Ctrl+Shift+C` e botão rápido no cabeçalho.
- **Racional**:
  - O leitor pode estar lendo um estudo, navegando pelo acervo ou consultando o dashboard e ter uma ideia repentina; o modal abre em primeiro plano sem alterar a rota atual nem descartar o estado da página.
  - Ao submeter o formulário (`Ctrl+Enter` ou clique em Salvar), a API grava a captura em < 50ms, fecha o modal, emite microtoast de confirmação e atualiza o badge de pendências do menu reativamente.
  - Suporta atalho acessível `Escape` para fechar e auto-foco imediato no campo de texto principal.
- **Alternativas consideradas**:
  - Redirecionar obrigatoriamente para `/inbox` para cadastrar qualquer nova nota: Cria fricção excessiva e tira o usuário do seu contexto de leitura.

---

### 3. Fluxo de Promoção para Estudo Formal

- **Decisão**: Ação "Promover para Estudo" abre o fluxo de criação de estudo direcionando para a tela de edição com o texto da captura pré-injetado na seção de **Resumo**, a fonte pré-injetada na seção de **Referências**, e o livro pré-selecionado caso a captura estivesse vinculada a uma obra. O salvamento bem-sucedido aciona a chamada a `POST /api/inbox/{id}/promote` com o `promoted_study_id`.
- **Racional**:
  - Conforme alinhado no esclarecimento de requisitos (Opção A), essa abordagem evita a geração de estudos incompletos ou órfãos no banco caso o usuário desista de formalizar o estudo.
  - Para capturas avulsas sem livro, o editor exige que o usuário escolha o livro e capítulo de destino, respeitando a integridade do acervo.
- **Alternativas consideradas**:
  - Criar o estudo em rascunho de forma cega no backend antes de abrir a tela: Poderia acumular estudos fantasmas se o usuário fechasse a aba antes de revisar.

---

### 4. Vinculação a Estudo Existente

- **Decisão**: Ação "Vincular a Estudo Existente" abre um seletor modal com busca de estudos do usuário. Ao confirmar, o endpoint `POST /api/inbox/{id}/link` anexa o texto formatado da captura ao final da seção selecionada (por padrão `references`) do estudo alvo e marca a captura como `linked` com `promoted_study_id = target_study_id`.
- **Racional**:
  - Formato padronizado de anexo textual:
    ```markdown

    ---
    > {conteúdo da captura}
    *Nota capturada do Inbox em {data} — {fonte}*
    ```
  - Incorpora a reflexão diretamente ao texto de estudo existente sem quebrar a consistência das seções analíticas.
- **Alternativas consideradas**:
  - Apenas copiar para a área de transferência: Exige passos manuais e não altera o status da captura no Inbox.

---

### 5. Contador Reativo de Pendências e Performance

- **Decisão**: Endpoint ultra-leve `GET /api/inbox/count` utilizando índice cobridor composto `ix_inbox_captures_user_status` em `(user_id, status)` no SQLite.
- **Racional**:
  - Uma query `SELECT COUNT(*) FROM inbox_captures WHERE user_id = :uid AND status = 'inbox'` com índice dedicado executa em menos de 1 milissegundo no SQLite local.
  - O composable `useInboxCount()` gerencia o estado reativo do contador, atualizando-o localmente de forma otimista ou invalidando-o quando qualquer ação de captura, exclusão ou promoção é disparada na aplicação.
- **Alternativas consideradas**:
  - Carregar a lista completa de capturas em todas as páginas apenas para contar o tamanho do array: Desperdício desnecessário de tráfego de rede e memória.
