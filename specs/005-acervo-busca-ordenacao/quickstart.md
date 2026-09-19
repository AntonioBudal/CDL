# Guia Rápido de Validação: Acervo — Visualização, Busca e Ordenação

**Feature**: Acervo: Visualização, Busca e Ordenação  
**Branch**: `005-acervo-busca-ordenacao`  
**Data**: 2026-09-18  

Este guia detalha os procedimentos para validar de ponta a ponta as capacidades de busca instantânea, ordenação e alternância de visualização da estante.

---

## 1. Cenários de Validação Rápida

### Cenário 1: Busca Instantânea Insensível a Acentos e Diacríticos
1. **Ação**: Acesse a tela principal do acervo (`/`).
2. **Ação**: No campo de busca, digite uma palavra sem acento (ex.: `memorias`, `arvore` ou `machado`).
3. **Resultado Esperado**:
   - Apenas os livros contendo o termo correspondente (mesmo que com acento, ex.: "Memórias", "Árvore") são exibidos.
   - O indicador exibe a contagem correta: `Exibindo 1 de X livros`.
   - Um botão "✕" aparece dentro do campo para limpar o filtro com um clique.

### Cenário 2: Alternância de Modo (Grade de Capas vs. Lista Compacta)
1. **Ação**: Na barra de ferramentas do acervo, clique no botão com ícone de lista (`Lista compacta`).
2. **Resultado Esperado**:
   - A grade de cartões converte-se imediatamente para o layout de linhas compactas.
   - Cada linha exibe miniatura proporcional 2:3 da capa, título, autor, ano e data de atividade.
   - Títulos longos não quebram o alinhamento.
3. **Ação**: Recarregue a página (`F5`).
4. **Resultado Esperado**:
   - A preferência é mantida e a página já inicia no modo `Lista compacta`.
5. **Ação**: Clique no botão de grade (`Grade de capas`) e recarregue novamente.
6. **Resultado Esperado**:
   - A exibição volta a ser em grade e persiste no navegador.

### Cenário 3: Ordenação de Livros
1. **Ação**: Altere o seletor de ordenação para **"Recentemente adicionados"**.
2. **Resultado Esperado**:
   - Os livros mais novos (maior `created_at`) aparecem no topo.
3. **Ação**: Altere para **"Recentemente modificados"**.
4. **Resultado Esperado**:
   - Livros com edições mais recentes (maior `updated_at`) assumem o topo.
5. **Ação**: Altere para **"Título (A–Z)"**.
6. **Resultado Esperado**:
   - Os livros são organizados em ordem alfabética estrita, respeitando o português.

### Cenário 4: Isolamento da Lixeira
1. **Ação**: Envie um livro para a lixeira.
2. **Ação**: Volte ao acervo e digite o título desse livro na busca.
3. **Resultado Esperado**:
   - O livro não aparece nos resultados nem na contagem geral.

---

## 2. Comandos de Validação Automatizada

### Backend
```powershell
cd C:\Users\User\caderno\caderno-leitura-0.1\backend
.\.venv\Scripts\pytest tests/test_books_search_and_sort.py -v
```

### Frontend
```powershell
cd C:\Users\User\caderno\caderno-leitura-0.1\frontend
npm test
npm run build
```
