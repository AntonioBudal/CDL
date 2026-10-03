# Quickstart & Guia de Validação: F0.6.7 — Normalização de Categorias

Este guia descreve os cenários de teste e validação de ponta a ponta para homologação da **Feature 046 — Normalização e Simplificação de Categorias**.

---

## 1. Pré-Requisitos e Ambiente de Teste

* **Isolamento Absoluto**: Todos os testes executam sobre bancos SQLite efêmeros em diretórios descartáveis (`tmp_path`), garantindo zero contato com o banco de produção ativo (`backend/data/caderno.db`), conforme o Princípio II da Constituição.
* **Ambiente Ativo**:
  - Python 3.13 (`caderno-leitura-0.1/backend/.venv`)
  - Node.js e npm (`caderno-leitura-0.1/frontend`)

---

## 2. Cenários Executáveis de Validação

### Cenário 1: Normalização e Atribuição Distributiva Sem Perda de Livros
* **Objetivo**: Provar que categorias legadas compostas distribuem corretamente os livros para as categorias canônicas correspondentes sem duplicatas em `book_categories`.
* **Comando de Teste**:
  ```powershell
  cd caderno-leitura-0.1/backend
  .venv\Scripts\python.exe -m pytest tests/test_category_normalization.py -k "test_distributive_category_migration" -v
  ```
* **Resultado Esperado**:
  - Livro com categoria legada `"Ciências Sociais e Humanas"` recebe `"Ciência"` e `"Humanidades"`.
  - Livro com categoria legada `"Filosofias"` recebe a forma singular `"Filosofia"`.
  - Chave composta em `book_categories` não gera duplicidade nem erro de chave primária.

---

### Cenário 2: Validação e Sugestão Assistida de Novas Categorias (API)
* **Objetivo**: Provar que o endpoint `GET /api/categories/suggest` sugere a forma singular e `POST /api/categories` converte/reutiliza a categoria canônica existente.
* **Comando de Teste**:
  ```powershell
  .venv\Scripts\python.exe -m pytest tests/test_category_normalization.py -k "test_suggest_and_create_canonical_category" -v
  ```
* **Resultado Esperado**:
  - Termo `"Direitos"` gera sugestão `"Direito"`.
  - Termo `"direito"` com minúsculas associa ao ID `"direito"` e exibe `"Direito"`.
  - Submissão com múltiplos termos ou caracteres inválidos retorna `HTTP 400 Bad Request`.

---

### Cenário 3: Taxonomia Plana e Filtro na Biblioteca (Frontend)
* **Objetivo**: Provar que o frontend exibe as categorias em formato plano (sem nós aninhados arbitrários) e que a filtragem por categoria funciona de forma instantânea.
* **Comando de Teste**:
  ```powershell
  cd caderno-leitura-0.1/frontend
  npm test tests/category_filter.test.mjs
  ```
* **Resultado Esperado**:
  - Lista de categorias exibe apenas termos canônicos no singular.
  - Ao selecionar um filtro de categoria, apenas os livros vinculados são exibidos.
  - O componente `CategoryInput.vue` exibe sugestões de termos canônicos no singular com feedback visual imediato.

---

### Cenário 4: Regressão Geral e Integridade de Build
* **Objetivo**: Garantir que as alterações não introduziram quebras nas suítes de teste existentes.
* **Comandos de Validação**:
  ```powershell
  # Backend regression
  cd caderno-leitura-0.1/backend
  .venv\Scripts\python.exe -m pytest tests/

  # Frontend tests & build
  cd ../frontend
  npm test
  npm run build
  ```
* **Resultado Esperado**:
  - 100% dos testes aprovados (0 falhas).
  - TypeScript e Vite compilam sem erros de tipagem.
