# Research: F0.7.12 — Backlinks e Menções entre Estudos

## Decisões Técnicas e Arquiteturais

### 1. Sintaxe de Menção e Extração de Tokens

- **Decisão**: Utilizar a sintaxe estilo wiki `[[Título do Estudo]]` como padrão de escrita, permitindo a forma qualificada com ID `[[Título do Estudo|id]]` para desambiguação determinística quando houver estudos com títulos idênticos no acervo.
- **Racional**:
  - É a sintaxe mais consagrada em ferramentas de pensamento em rede (Obsidian, Roam, Logseq, Notion).
  - Mantém o Markdown 100% legível e elegante no texto puro.
  - A extensão `|id` resolve com precisão matemática casos onde o usuário possui dois estudos com nomes genéricos (ex.: "Introdução" em livros diferentes), sem forçar IDs visíveis em todos os outros estudos.
- **Alternativas consideradas**:
  - `@estudo-id`: Pouco amigável para digitação e expõe UUIDs ou números feios no meio do parágrafo.
  - Links Markdown normais `[Título](/estudos/123)`: Complexo para autocompletar e mistura links externos com referências conceituais do acervo.

---

### 2. Ciclo de Vida e Sincronização Relacional no Banco de Dados

- **Decisão**: Extração atômica síncrona no salvamento do estudo (durante o commit de `create_study` e `update_study`), persistindo na tabela relacional `study_mentions`.
- **Racional**:
  - Evita filas assíncronas ou jobs em segundo plano, que seriam desnecessários e complexos em ambiente SQLite local monolítico.
  - A extração via Regex pré-compilada em 4 seções de texto leva menos de 2 milissegundos para textos de estudos típicos (1.000 a 10.000 caracteres).
  - Garante consistência imediata: ao salvar a edição e abrir o estudo citado, o backlink reverso já está disponível.
- **Alternativas consideradas**:
  - Computação "on the fly" em tempo de leitura com `LIKE %[[...]]%`: Inviável e ineficiente com o crescimento do acervo, além de não permitir índices nem integridade relacional.

---

### 3. Renderização de Hiperlinks Internos no `MarkdownContent.vue`

- **Decisão**: Pré-processar ou pós-processar tokens `[[...]]` no renderizador `markdown-it`, transformando-os em tags `<a>` seguras com classe `study-internal-mention` e captura de clique delegada para navegação SPA via `vue-router`.
- **Racional**:
  - Permite estilização visual temática exclusiva (ex.: badge com ícone de link interno e fundo sutil).
  - A delegação de clique impede recarregamento de página (FOUC), navegando via `router.push`.
  - Tratamento defensivo: se o estudo alvo estiver na lixeira, exibe a classe `is-archived` e tooltip "Estudo na lixeira", prevenindo tela de erro 404 abrupta.
- **Alternativas consideradas**:
  - Converter para Markdown padrão antes de salvar: Alteraria o texto original do usuário e causaria poluição no banco.

---

### 4. Componente de Backlinks e Diferenciação de Relações

- **Decisão**: Criar `StudyBacklinksList.vue` ancorado no rodapé da coluna central de `StudyView.vue` (abaixo das abas analíticas e acima de `StudyRelationsList.vue`).
- **Racional**:
  - Obedece rigorosamente ao modelo mental do leitor:
    - **Relações Semânticas (`study_relations`)**: Relações de alto nível conceituais (*Contradiz*, *Fundamenta*, *Desdobra*), mapeadas no grafo/canvas 2D.
    - **Backlinks / Menções (`study_mentions`)**: Referências bibliográficas contextuais que surgem da escrita fluida nos parágrafos.
  - A exibição do `context_snippet` (citação com o trecho de texto ao redor da menção) dá sentido imediato à referência sem obrigar o leitor a abrir o outro estudo para entender o porquê da menção.
