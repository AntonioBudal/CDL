# Quickstart: F0.7.12 — Backlinks e Menções entre Estudos

Guia de validação e execução ponta a ponta da feature de Backlinks e Menções entre Estudos.

---

## 1. Pré-Requisitos e Ambiente

- Python 3.13 com ambiente virtual configurado em `backend/.venv`
- Node.js 20+ com dependências instaladas em `frontend/`
- Banco SQLite de teste efêmero gerenciado via `pytest`

---

## 2. Cenários de Validação

### Cenário 1: Autocomplete e Salvamento de Menção no Editor
1. Acesse o editor de estudos para o Estudo A (`/livros/1/estudos/10/editar`).
2. No campo **Explicação** (`explanation`), digite `Conforme analisado em [[Estudo`.
3. Verifique o surgimento do popover de autocomplete listando o "Estudo B" com o nome da obra correspondente.
4. Pressione `Enter` para selecionar. O editor insere `[[Estudo B]]`.
5. Clique em **Salvar estudo**.
6. **Resultado Esperado**:
   - A requisição `PATCH /api/studies/10` salva o texto e o backend sincroniza `study_mentions`.
   - Consulta ao banco registra `source_study_id=10`, `target_study_id=20` (ID do Estudo B) e trecho contextual.

### Cenário 2: Renderização de Link Interno e Navegação Direta
1. Visualize o Estudo A no leitor (`/livros/1/estudos/10`).
2. Observe que `[[Estudo B]]` é renderizado como um link com estilo de referência interna (`.study-internal-mention`).
3. Clique no link.
4. **Resultado Esperado**:
   - A aplicação transiciona suavemente via SPA para `/livros/1/estudos/20` (Estudo B) sem recarregar a página.

### Cenário 3: Painel Reverso de Backlinks no Estudo Citado
1. No leitor do Estudo B (`/livros/1/estudos/20`), role até o rodapé da coluna central.
2. Observe a seção **"Mencionado em 1 estudo"**.
3. O card exibe o Estudo A, obra, capítulo e a citação: *"Conforme analisado em [[Estudo B]]..."*.
4. Clique no card do Estudo A para retornar.
5. **Resultado Esperado**:
   - O leitor navega de volta para o Estudo A, fechando o ciclo bidirecional.

### Cenário 4: Isolamento e Estudo na Lixeira
1. Mova o Estudo A para a lixeira (`POST /api/studies/10/trash`).
2. Recarregue a visualização do Estudo B.
3. **Resultado Esperado**:
   - A seção de backlinks do Estudo B oculta o Estudo A e exibe contagem zero (ou estado vazio).

---

## 3. Comandos de Verificação Automatizada

### Testes de Backend (Pytest):
```powershell
cd caderno-leitura-0.1\backend
.\.venv\Scripts\pytest.exe tests/test_study_mentions.py -v
```

### Testes de Frontend (Node Test Runner):
```powershell
cd caderno-leitura-0.1\frontend
node --test tests/study_mentions.test.mjs
```

### Build e Verificação de Tipos TypeScript:
```powershell
cd caderno-leitura-0.1\frontend
npm run build
```
