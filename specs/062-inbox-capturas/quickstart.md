# Quickstart & Validation Guide: F0.7.13 — Caixa de Entrada de Capturas

Este guia apresenta os passos de validação ponta a ponta e testes automatizados para verificar a implementação do Inbox de Capturas.

---

## 1. Pré-Requisitos e Ambiente de Teste

- Python 3.13 ativo em `backend/.venv`
- Dependências Node / Vite instaladas em `frontend/`
- Bancos de dados de teste isolados em `tmp_path` (em conformidade com a Constituição do Projeto)

---

## 2. Testes Automatizados

### Backend (Pytest)

Executar a suíte de testes de endpoints e persistência de capturas:

```powershell
backend\.venv\Scripts\pytest -q backend\tests\test_inbox.py
```

**Cenários cobertos:**
1. Criação de captura rápida (`POST /api/inbox`) com conteúdo obrigatório e livro opcional.
2. Contagem leve de pendências (`GET /api/inbox/count`) com isolamento multiusuário estrito.
3. Listagem filtrada por status (`inbox`, `promoted`, `linked`, `archived`) e busca textual (`GET /api/inbox?q=termo`).
4. Atualização parcial e edição inline (`PATCH /api/inbox/{id}`).
5. Exclusão de captura (`DELETE /api/inbox/{id}`).
6. Promoção para estudo (`POST /api/inbox/{id}/promote`) vinculando `promoted_study_id` e alterando status para `promoted`.
7. Vinculação a estudo existente (`POST /api/inbox/{id}/link`) anexando citação formatada à seção `references` e alterando status para `linked`.

### Frontend (Node Test Runner / Vitest)

Executar os testes de componentes e composables:

```powershell
npm --prefix frontend test -- tests/inbox.test.mjs
```

**Cenários cobertos:**
1. `useQuickCapture` composable: abertura, fechamento e envio assíncrono.
2. `QuickCaptureModal.vue`: foco no textarea, atalho `Escape` e submissão `Ctrl+Enter`.
3. `CaptureItemCard.vue`: renderização de metadados, expansão de texto longo e disparos de eventos de promoção e descarte.
4. `InboxView.vue`: filtros por abas, busca textual e estado vazio informativo.

---

## 3. Roteiro de Validação Manual (Ponta a Ponta)

### Cenário 1: Captura Rápida Global (Atalho e Header)
1. Iniciar a aplicação local via `python iniciar.py`.
2. Em qualquer tela (ex.: `/livros` ou `/dashboard`), pressionar `Ctrl+Shift+C` ou clicar no botão "Capturar" do cabeçalho.
3. Verificar a abertura instantânea do modal com o cursor já focado no campo de texto.
4. Digitar uma anotação fictícia (ex.: "O conceito de atenção plena exige pausas conscientes.") e indicar fonte "Livro Teste, pág. 12".
5. Pressionar `Ctrl+Enter` para salvar.
6. **Resultado Esperado**: O modal se fecha instantaneamente, um microtoast informa o sucesso e o badge no menu lateral exibe `1`.

### Cenário 2: Triagem e Gestão no Inbox
1. Clicar no item "Inbox" do menu lateral (rota `/inbox`).
2. Verificar a exibição do cartão recém-criado com data relativa e fonte visível.
3. Testar a busca textual digitando "atenção" no filtro do topo.
4. Testar a edição rápida alterando uma palavra e salvando.
5. **Resultado Esperado**: Lista atualizada sem recarregar a página inteira.

### Cenário 3: Promoção para Estudo
1. No cartão da captura, clicar em **"Promover para Estudo"**.
2. Verificar o redirecionamento para o editor de estudos com o texto pré-injetado no campo "Resumo" e a fonte em "Referências".
3. Selecionar o livro e capítulo de destino, digitar um título para o estudo e clicar em "Salvar".
4. Retornar ao `/inbox`.
5. **Resultado Esperado**: O badge do menu foi decrementado para `0` e o item agora aparece na aba de "Promovidos" com link direto para o estudo gerado.

### Cenário 4: Vinculação a Estudo Existente
1. Criar uma nova captura rápida via `Ctrl+Shift+C`.
2. No `/inbox`, clicar em **"Vincular a Estudo Existente"**.
3. Selecionar um estudo na lista de busca e confirmar.
4. Abrir o estudo selecionado no leitor.
5. **Resultado Esperado**: O trecho da captura aparece incorporado na seção de Referências/Notas do estudo e a captura passa para o status `linked`.
