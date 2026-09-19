# Phase 0: Research & Technical Decisions — Exportação de Anotações em TXT e Markdown

**Feature Branch**: `015-exportacao-anotacoes`  
**Date**: 2026-09-19  
**Status**: Completed  

---

## 1. Local de Geração do Arquivo (Backend FastAPI vs Frontend Client-side)

### Decisão
Implementar a geração e formatação do documento no backend em um serviço dedicado (`backend/app/services/export_service.py`) servido pelos endpoints `GET /api/books/{book_id}/export` e `GET /api/studies/{study_id}/export`, retornando o conteúdo com cabeçalhos HTTP `Content-Disposition: attachment; filename="..."` e `Content-Type: text/markdown; charset=utf-8` (ou `text/plain; charset=utf-8`). O frontend fornece um modal de seleção (`ExportModal.vue`) e aciona o download por URL direta ou blob stream.

### Racional
- **Performance e Escala**: Para livros com muitos capítulos e estudos, carregar todo o texto bruto para o navegador para depois concatenar em JavaScript consumiria memória excessiva do cliente. No backend, a consulta SQLAlchemy faz a projeção ordenada e o streaming de texto puro sem overhead.
- **Testabilidade Rígida**: Permite testes unitários e de integração 100% automatizados no backend via `pytest` e `TestClient`, garantindo fidelidade de codificação UTF-8, sanitização de nomes de arquivo e exclusão rigorosa de itens da lixeira (`deleted_at IS NOT NULL`).
- **Compatibilidade Multiplataforma**: A resposta HTTP com `Content-Disposition: attachment` é o padrão da web que aciona o gerenciador nativo de downloads de qualquer navegador (Chrome, Edge, Firefox, Safari mobile, Tailscale).

### Alternativas Consideradas
- *Geração 100% no cliente (JavaScript/Blob)*: Exigiria criar rotas para buscar todos os estudos detalhados de um livro no frontend, aumentando o tráfego de rede e dispersando as regras de exclusão da lixeira.

---

## 2. Sanitização de Nomes de Arquivo e Codificação UTF-8

### Decisão
Criar função utilitária `sanitize_filename(title: str, extension: str, max_length: int = 80) -> str` que:
1. Normaliza caracteres com `unicodedata.normalize('NFKD', ...)` ou preserva diacríticos legíveis no Windows.
2. Remove ou substitui caracteres ilegais em sistemas de arquivos Windows/POSIX (`\`, `/`, `:`, `*`, `?`, `"`, `<`, `>`, `|`) por hífens.
3. Remove espaços redundantes e substitui espaços por hífens ou sublinhados legíveis.
4. Trunca o nome em no máximo 80 caracteres para evitar ultrapassar o limite `MAX_PATH` do Windows.
5. Garante codificação de saída estritamente em UTF-8 (`charset=utf-8`).

### Racional
- O ambiente operacional do usuário é Windows local, onde caminhos com caracteres proibidos provocam falhas silenciosas ou erros no download.
- Garante que a abertura do arquivo no Bloco de Notas, VS Code ou Obsidian exiba acentos perfeitos sem *mojibake*.

---

## 3. Estruturação do Formato Markdown com Frontmatter YAML

### Decisão
No formato Markdown (`.md`):
- Se `include_metadata` for verdadeiro, incluir no topo um bloco Frontmatter delimitado por `---` com metadados estruturados:
  ```yaml
  ---
  title: "Título do Livro"
  author: "Autor"
  subtitle: "Subtítulo"
  year: 1956
  categories: ["Ficção", "Literatura Brasileira"]
  date_exported: "2026-09-19T10:00:00Z"
  app: "Caderno de Leitura"
  ---
  ```
- Estrutura hierárquica por títulos:
  - `# Título do Livro`
  - `## Capítulo`
  - `### Título do Estudo` (com linha de localização em itálico)
  - `#### Minhas Anotações` (preservando o texto original)
  - `#### Resumo`, `#### Explicação`, `#### Conceitos`, `#### Referências` (quando selecionadas)
  - `#### Resposta Original` (quando selecionada)
- Preservar marcações `==texto destacado==`.

### Racional
- Totalmente interoperável com os principais softwares de Second Brain e anotações (Obsidian, Logseq, Notion, Zettlr, Dendron).
- Leitores comuns de Markdown tratam o Frontmatter graciosamente sem poluição visual.

---

## 4. Estruturação do Formato Texto Puro (.txt)

### Decisão
No formato Texto Puro (`.txt`):
- Usar divisores ASCII claros (`===...===` para o livro, `---...---` para capítulos e `---` para estudos).
- Cabeçalhos de seção em maiúsculas entre colchetes (ex.: `[MINHAS ANOTAÇÕES]`, `[RESUMO]`).
- Sem tags HTML ou código cercado desnecessário.

### Racional
- Ideal para quem deseja imprimir, abrir em editores simples ou colar em e-mails e documentos convencionais.

---

## 5. Experiência de Usuário: Modal Acessível (`ExportModal.vue`)

### Decisão
Criar o componente `ExportModal.vue` reutilizável, que pode ser disparado a partir de:
1. `BookView.vue`: exporta o livro completo.
2. `StudyView.vue`: exporta apenas o estudo atual.
O modal apresenta:
- Seletor de Formato: Markdown (`.md`) vs Texto Puro (`.txt`).
- Caixas de seleção:
  - `[x] Minhas Anotações` (sempre habilitada e marcada)
  - `[x] Seções de Análise (Resumo, Explicação, Conceitos, Referências)` (marcada por padrão)
  - `[ ] Resposta Original de Importação` (desmarcada por padrão)
- Botão "Baixar arquivo" com estado de carregamento e foco acessível.
