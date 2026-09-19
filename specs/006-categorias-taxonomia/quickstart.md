# Quickstart & Validation Guide: Categorias e Taxonomia de Livros (T05)

**Feature**: `006-categorias-taxonomia`  
**Date**: 2026-09-18  
**Status**: Ready

Guia prático para validação ponta a ponta dos requisitos da **Feature 006 (T05 — Categorias e Taxonomia)**.

---

## 1. Pré-requisitos e Ambiente

Certifique-se de estar com o ambiente configurado no Windows PowerShell dentro da pasta `caderno-leitura-0.1`:

```powershell
# No terminal PowerShell em C:\Users\User\caderno\caderno-leitura-0.1:
cd C:\Users\User\caderno\caderno-leitura-0.1
$env:PYTHONPATH = "backend"
```

---

## 2. Cenários de Validação Automatizada

### Cenário 1: Validação do Catálogo Canônico e Ausência de Ciclos
Verifica se o arquivo `backend/app/data/canonical_categories.json` contém mais de 100 categorias, todos os `parent_id` são válidos e a árvore não possui nenhum ciclo:

```powershell
.\backend\.venv\Scripts\pytest.exe backend/tests/test_categories.py -k "test_canonical_catalogue_integrity" -v
```
**Resultado esperado**: Teste passa confirmando que o catálogo possui >100 entradas sem duplicatas e sem referências circulares.

---

### Cenário 2: Idempotência de Carga e Migração do Banco
Executa a sincronização do catálogo repetidamente em um banco efêmero isolado (`tmp_path`) contendo livros com categorias associadas:

```powershell
.\backend\.venv\Scripts\pytest.exe backend/tests/test_categories.py -k "test_sync_categories_is_idempotent" -v
```
**Resultado esperado**: Contagem de categorias permanece exatamente idêntica e todos os vínculos existentes são 100% preservados.

---

### Cenário 3: Associação de Múltiplas Categorias e Preservação em Edições Parciais
Cria um livro com múltiplas categorias, executa uma edição parcial (apenas de título ou ano) e verifica que as categorias associadas não são perdidas:

```powershell
.\backend\.venv\Scripts\pytest.exe backend/tests/test_categories.py -k "test_book_categories_crud_and_patch_preservation" -v
```
**Resultado esperado**:
1. Criação do livro persiste as categorias informadas.
2. `PATCH` alterando apenas o título mantém todas as categorias intactas.
3. `PATCH` com `category_ids: ["nova-cat"]` atualiza os vínculos atomicamente.

---

### Cenário 4: Filtro Recursivo/Inclusivo no Acervo
Cadastra livros em subcategorias de "Filosofia" (ex.: "Filosofia / Ética") e pesquisa na rota de acervo por `category=filosofia`:

```powershell
.\backend\.venv\Scripts\pytest.exe backend/tests/test_categories.py -k "test_books_filter_by_recursive_category" -v
```
**Resultado esperado**: A busca pela categoria pai retorna todos os livros vinculados a ela e a qualquer uma de suas subcategorias descendentes.

---

### Cenário 5: Isolamento da Lixeira e Exclusão Definitiva
Envia um livro categorizado para a lixeira e verifica que ele não aparece em filtros de categoria ativos; ao restaurar, recupera as categorias; ao excluir definitivamente, remove os registros em `book_categories` sem afetar a categoria no catálogo:

```powershell
.\backend\.venv\Scripts\pytest.exe backend/tests/test_categories.py -k "test_category_lifecycle_with_trash" -v
```
**Resultado esperado**: Zero impacto no catálogo e comportamento íntegro na lixeira e no expurgo definitivo.

---

### Cenário 6: Testes do Frontend e Build de Produção
Executa a suíte de testes de unidade do composable de categorias e a compilação do TypeScript/Vite:

```powershell
cd frontend
node --test tests/library-filter.test.mjs
node --test tests/categories.test.mjs
npm run build
cd ..
```
**Resultado esperado**:
- Todos os testes unitários passando.
- `vue-tsc -b` executando com zero erros de tipo.
- `vite build` gerando o bundle estático em `dist/`.

---

## 3. Verificação Manual no Navegador

1. Iniciar o servidor local:
   ```powershell
   .\backend\.venv\Scripts\python.exe iniciar.py
   ```
2. Acessar `http://127.0.0.1:8000` no navegador.
3. No modal de cadastro/edição de livro:
   - Digitar fragmentos no campo de categorias (ex.: "etica", "brasil").
   - Verificar as sugestões com caminhos hierárquicos legíveis.
   - Adicionar duas categorias e salvar.
   - Confirmar a exibição das etiquetas nos cartões da estante e na ficha da obra.
4. Na barra de ferramentas do acervo:
   - Selecionar a categoria pai no filtro e comprovar que os livros das subcategorias aparecem no resultado.
   - Combinar com busca de texto e ordenação.
