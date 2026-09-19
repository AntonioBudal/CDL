# Pesquisa Técnica: Acervo — Visualização, Busca e Ordenação

**Feature**: Acervo: Visualização, Busca e Ordenação  
**Branch**: `005-acervo-busca-ordenacao`  
**Data**: 2026-09-18  

---

## 1. Pesquisa e Decisões de Arquitetura

### 1.1 Filtragem Textual Insensível a Acentos e Caixa (Client-Side)

- **Contexto**: O acervo pessoal é uma aplicação local de processo único onde os livros ativos são carregados na visão principal. A busca deve responder instantaneamente a cada tecla digitada (<100ms) sem lag de rede ou requisições desnecessárias.
- **Decisão**: Implementar a busca reativa no frontend com normalização Unicode NFD:
  ```ts
  function normalizeText(value: string): string {
    return value
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .toLowerCase()
      .trim()
  }
  ```
  A busca divide o termo digitado em tokens (palavras separadas por espaço) e exige que todos os tokens estejam presentes no título, autor ou subtítulo do livro (`AND` lógico entre palavras):
  ```ts
  const tokens = normalizeText(query).split(/\s+/).filter(Boolean)
  const matches = tokens.every(token => normalizedBookText.includes(token))
  ```
- **Justificativa**: Permite que buscas como `"memorias machado"` localizem *"Memórias Póstumas de Brás Cubas"* de *"Machado de Assis"*, mesmo com ou sem acentos, maiúsculas ou ordem invertida de palavras.
- **Alternativas consideradas**:
  - *Regex dinâmica*: Rejeitada por risco de injeção de caracteres especiais que causam erro de sintaxe regex e menor performance em loops.
  - *Filtragem apenas no backend via SQL LIKE*: Rejeitada para a experiência em tempo real por introduzir latência de round-trip a cada tecla em conexões lentas (ex.: celular em Wi-Fi fraco).

---

### 1.2 Ordenação Previsível e Collation em Português

- **Contexto**: Ordenar por texto em português exige respeito às regras de collation (ex.: "Árvore" e "Amor" devem ser ordenados de forma coerente sem bugs ASCII onde maiúsculas ou acentos ficam no final).
- **Decisão**:
  - Para ordenação textual (Título e Autor): usar `Intl.Collator('pt-BR', { sensitivity: 'base', numeric: true })`.
  - Para ordenação temporal: comparar os timestamps ISO 8601 (`created_at` e `updated_at`) diretamente com `new Date(a).getTime() - new Date(b).getTime()`.
  - Para ordenação por ano: tratar valores nulos posicionando-os no final da lista.
  - **Opções disponíveis de ordenação**:
    1. `title-asc`: Título (A–Z)
    2. `title-desc`: Título (Z–A)
    3. `author-asc`: Autor (A–Z)
    4. `recent-created`: Recentemente adicionados (mais novos primeiro)
    5. `recent-updated`: Recentemente modificados (última atividade primeiro)
    6. `oldest-created`: Mais antigos adicionados (mais antigos primeiro)
    7. `year-desc`: Ano de publicação (mais recentes primeiro)
- **Justificativa**: Atende perfeitamente à opção **A** selecionada na especificação e oferece a ordenação padrão ideal para estudos.

---

### 1.3 Modos de Visualização: Grade de Capas vs. Lista Compacta

- **Contexto**: A visão atual em `BooksView.vue` apresenta uma grade de cartões com proporção vertical. Usuários com muitos livros ou visualizando em celulares pequenos necessitam de uma visão mais densa e rápida.
- **Decisão**:
  - **Modo Grade (`grid`)**: Mantém o design atual com cartões visuais enriquecidos com capas de proporção 2:3 (`size="md"`), número de ordem, título em destaque, autor e link.
  - **Modo Lista (`list`)**: Layout em tabela ou linhas compactas horizontais contendo:
    - Miniatura da capa em tamanho pequeno (`size="sm"` ou `36x54px`).
    - Título e subtítulo.
    - Autor e ano de publicação.
    - Quantidade de capítulos cadastrados.
    - Data da última atividade/modificação formatada.
    - Ação rápida para abrir o livro.
- **Persistência**:
  - O modo de visualização utiliza a preferência `library` de `cadernoAppearance` (`'grid' | 'list'`) já declarada no ecossistema do Caderno de Leitura, complementada com persistência imediata em `localStorage`.
  - A opção de ordenação é armazenada em `localStorage.getItem('caderno_books_sort')` (com fallback padrão para `recent-updated` ou `title-asc`).

---

### 1.4 Enriquecimento da API Backend (`GET /api/books`)

- **Contexto**: Embora o frontend faça busca e ordenação instantânea para o acervo carregado, o endpoint `GET /api/books` deve suportar parâmetros opcionais de consulta (`q`, `sort`, `order`) para clientes que consomem a API diretamente ou para testes de integração automatizados.
- **Decisão**:
  - Adicionar parâmetros opcionais em `GET /api/books`:
    - `q: str | None = None`: busca em `title`, `author`, `subtitle`.
    - `sort: str | None = None`: `title`, `author`, `created_at`, `updated_at`, `year`.
    - `order: str = "asc"`: `asc` ou `desc`.
  - Preservar retrocompatibilidade total: requisições sem parâmetros continuam retornando a lista completa de livros ativos ordenados por `id` asc (ou `created_at` asc).
  - Manter garantia constitucional: livros com `deleted_at IS NOT NULL` continuam 100% filtrados em qualquer cenário.

---

## 2. Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|
| Perda de fluidez em buscas rápidas no celular | Baixa | Médio | Usar computeds eficientes do Vue 3 e normalização em memória; o tamanho do acervo pessoal (dezenas a centenas de obras) executa em <5ms. |
| Inconsistência de ordenação entre navegadores | Baixa | Baixo | Usar `Intl.Collator` padrão ECMA-402 suportado por 100% dos navegadores modernos. |
| Quebra de layout com títulos muito longos | Média | Baixo | Aplicar `line-clamp` com reticências CSS e `overflow-wrap: break-word` tanto na grade quanto na lista. |
| Estado vazio confuso quando a busca não retorna nada | Média | Médio | Criar painel de estado vazio específico com botão "Limpar filtro" e mensagem explicativa. |
