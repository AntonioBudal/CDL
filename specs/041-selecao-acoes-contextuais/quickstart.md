# Quickstart: Validação da Feature F0.6.2 — Seleção e Ações Contextuais

Este guia descreve os passos automatizados e manuais para validar a feature **F0.6.2 — Seleção e Ações Contextuais**.

---

## 1. Validação Automatizada (Backend)

Executar os testes unitários e de integração do novo modelo e endpoints de destaques utilizando SQLite temporário (`tmp_path`):

```powershell
cd caderno-leitura-0.1\backend
.venv\Scripts\python -m pytest tests/test_study_highlights.py -v
```

### Critérios de Aceite no Backend:
- `test_create_study_highlight`: Criação de destaque com offsets, texto e cor.
- `test_list_study_highlights`: Listagem isolada por estudo e usuário proprietário.
- `test_update_study_highlight`: Atualização de cor e anotação vinculada.
- `test_delete_study_highlight`: Remoção com resposta 204 No Content.
- `test_study_highlight_validation`: Rejeição de tipos inválidos, cores inexistentes ou texto em branco.
- `test_cascade_delete_with_study`: Exclusão em cascata de destaques quando o estudo é excluído.

---

## 2. Validação Automatizada (Frontend)

Executar a suíte de testes de componentes e composables no frontend:

```powershell
cd caderno-leitura-0.1\frontend
npm test -- test/FloatingActionsToolbar.spec.ts test/useTextSelection.spec.ts test/highlightRenderer.spec.ts
```

### Validação de Build:
```powershell
npm run build
```
*(Garante que o TypeScript estrito não acuse erros de tipagem e o bundle seja gerado perfeitamente).*

---

## 3. Roteiro de Validação Manual (Passo a Passo)

### Cenário 1: Seleção e Barra Flutuante no Desktop
1. Inicie a aplicação via `python iniciar.py`.
2. Acesse a tela de leitura de um estudo qualquer (`/books/{bookId}/study/{studyId}`).
3. Selecione com o mouse uma frase na seção **Visão Geral** ou **Aprofundamento**.
4. **Verificação**: A barra flutuante surge suavemente acima ou abaixo da seleção contendo as 5 ações (Destacar, Anotar, Citar, Ocultar e Pergunta).
5. Pressione `Escape` ou clique em outro lugar: a barra fecha imediatamente.

### Cenário 2: Marca-texto e Persistência
1. Selecione uma frase e clique em **Destacar** (amarelo padrão).
2. O trecho recebe a formatação de marca-texto amarelo suave.
3. Recarregue a página (`F5`).
4. **Verificação**: O trecho continua destacado exatamente na mesma posição.
5. Clique sobre o trecho destacado: abre o popover de opções. Altere para a cor verde. O destaque muda de cor na hora.
6. Clique no botão de lixeira: o destaque é removido e o texto volta ao normal.

### Cenário 3: Anotação Vinculada e Copiar Citação
1. Selecione uma frase e clique em **Anotar**. Digite uma reflexão de teste e confirme.
2. **Verificação**: Um indicador visual de nota surge junto ao trecho. Ao clicar nele, a reflexão é exibida.
3. Selecione outro trecho e clique em **Copiar citação**.
4. Cole no Bloco de Notas ou terminal: confira que a citação veio com aspas, o trecho exato e a referência da obra/estudo.

### Cenário 4: Leitura Ativa (Oclusão e Pergunta)
1. Selecione um conceito e clique em **Ocultar trecho**.
2. **Verificação**: O texto é mascarado por um bloco cinza/blur com o botão `[Revelar]`.
3. Ao clicar em `[Revelar]`, o texto original reaparece.
4. Selecione uma definição e clique em **Transformar em pergunta**. Digite uma pergunta de teste.
5. **Verificação**: O bloco exibe a pergunta com o botão `[Ver resposta]`.

### Cenário 5: Experiência Mobile / Touch
1. Abra as Ferramentas de Desenvolvedor (`F12`), ative a emulação de dispositivo móvel (ex.: iPhone 14 ou Pixel 7).
2. Selecione um trecho de texto no estudo.
3. **Verificação**: A barra de ações contextual é exibida de forma fixa na base da tela (*bottom sheet*), com botões grandes de toque (mínimo 44x44px), sem concorrer com as alças de seleção do navegador.
