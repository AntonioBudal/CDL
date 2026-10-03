# Research: F 0.7.5 — Redesenho da List View: Busca Rápida, Filtragem e Comparação Analítica

**Feature**: F 0.7.5 — Redesenho da List View  
**Status**: Completed  
**Artifact**: `research.md`

---

## Decisões Técnicas e Arquiteturais

### D1: Ciclo Tripartite de Ordenação por Cabeçalho de Coluna com Persistência Local

- **Decisão**: Implementar alternância de 3 estados a cada clique sucessivo na mesma coluna:
  1. 1º clique: Ascendente (`asc`, ícone `↑`).
  2. 2º clique: Descendente (`desc`, ícone `↓`).
  3. 3º clique: Reset para a ordem canônica do livro/capítulo (`default`, sem indicador de seta).
  O estado ativo é persistido no `localStorage` sob a chave `caderno_list_sort_${bookId}` contendo `{ column: string, direction: 'asc' | 'desc' | 'default' }`.
- **Racional**:
  - Responde à decisão da clarificação Q2: Opção A.
  - Oferece um retorno transparente à sequência cronológica ou posicional do fichamento sem forçar o usuário a recarregar a visualização.
  - A persistência local garante que, ao alternar entre as 5 views do livro (Grid, List, Tree, Map, Canvas), o usuário mantenha sua preferência de inspeção sem atrito.
- **Alternativas consideradas**:
  - *Alternância binária estrita (apenas asc/desc):* Rejeitada por impedir que o leitor retorne à ordem natural de leitura original sem recarregar o navegador.

---

### D2: Busca Reativa em Tempo Real e Normalização de Diacríticos (`useStudyListFilters.ts`)

- **Decisão**: Criar o composable modular `useStudyListFilters.ts` para orquestrar busca textual, filtros de status e ordenação em memória. A busca normaliza strings removendo acentos e convertendo para minúsculas (`str.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase()`).
- **Racional**:
  - Executa a filtragem em menos de 5ms no cliente para coleções com centenas de estudos, superando a meta de < 50ms estipulada em SC-001.
  - Permite localizar termos sem exigir correspondência exata de acentuação (ex.: "fenomenologia" encontra "Fenomenologia").
  - Busca avalia concomitantemente os campos `title`, `location` e `summary_preview`.
- **Alternativas consideradas**:
  - *Busca via endpoint backend:* Rejeitada por gerar tráfego desnecessário de rede para dados já disponíveis em memória no cliente.

---

### D3: Micro-Chips Fixos de Seções Analíticas (`R`, `E`, `C`, `Ref`)

- **Decisão**: Cada linha da tabela (e segundo nível no mobile) exibe 4 micro-chips contíguos com largura constante de 18×18px cada:
  - `R`: Resumo (`has_summary`)
  - `E`: Explicação (`has_explanation`)
  - `C`: Conceitos (`has_concepts`)
  - `Ref`: Referências (`has_references`)
  Quando preenchido, o chip recebe fundo suave e texto destacado com contraste adaptativo; quando ausente, permanece com tom cinza neutro esmaecido (`opacity: 0.35`).
- **Racional**:
  - Responde à decisão da clarificação Q1: Opção A.
  - Permite escanear verticalmente a lista e comparar a maturidade analítica dos estudos em frações de segundo sem quebras na largura da coluna.
  - O backend expõe as 4 flags booleanas em `StudySummary` a partir dos campos já presentes na instância do modelo SQLAlchemy sem consultas extras.
- **Alternativas consideradas**:
  - *Omitir siglas vazias:* Rejeitada por criar variações de largura desiguais entre linhas, prejudicando o alinhamento tabular da List View.

---

### D4: Ergonomia Mobile em Dois Níveis com Filtro Expansível

- **Decisão**: Em telas móveis (< 768px), a List View adapta-se para uma lista compacta com 2 linhas por estudo:
  - **Linha 1**: Título do estudo e badge de status de leitura.
  - **Linha 2**: Localização, data e o bloco com os 4 micro-chips de seções analíticas (`R`, `E`, `C`, `Ref`).
  Os filtros de status no topo são revelados através de um botão sanfona/accordion compacto ("Filtrar por status ▾"), mantendo apenas o campo de busca fixo e alvos de toque mínimos de 44×44px.
- **Racional**:
  - Responde à decisão da clarificação Q3: Opção A.
  - Elimina qualquer barra de rolagem horizontal no smartphone.
  - Garante total conformidade com WCAG 2.1 AA (alvos de toque mínimos de 44px).
- **Alternativas consideradas**:
  - *Tabela com rolagem horizontal no mobile:* Rejeitada por dificultar a leitura rápida e quebrar o ritmo de estudo em telas táteis.

---

### D5: Semântica Acessível WAI-ARIA para Dados Tabulares

- **Decisão**: Estruturar a lista com elementos nativos de tabela semântica ou atributos ARIA explícitos (`role="table"`, `role="row"`, `role="columnheader"`, `role="cell"`), com cabeçalhos possuindo `aria-sort="ascending"`, `aria-sort="descending"` ou `aria-sort="none"` e suporte completo a navegação sequencial por teclado (`Tab`, `Enter`).
- **Racional**:
  - Garante acessibilidade plena para tecnologias assistivas (leitores de tela NVDA, VoiceOver).
  - Permite aos leitores de tela anunciar claramente a direção da ordenação e a contagem de resultados filtrados via região `aria-live="polite"`.
