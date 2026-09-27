# Phase 0: Research & Technical Decisions — F0.6.4

**Feature**: F0.6.4 — Exportação com Destaques e Caderno de Revisão  
**Branch**: `043-exportacao-revisao`  
**Date**: 2026-09-27  

Este documento registra as pesquisas técnicas, decisões arquiteturais e alternativas avaliadas para a extensão do subsistema de exportação do Leitorum.

---

## 1. Algoritmo de Injeção de Destaques sem Deriva de Offsets

### Contexto
No Leitorum, os destaques (`StudyHighlight`) são salvos de forma não intrusiva com `start_offset`, `end_offset`, `section`, `selected_text`, `prefix`, `suffix`, `kind` e `note`. O texto original do estudo (em `summary`, `explanation`, `concepts`, `references` e `source_response`) permanece limpo no banco de dados SQLite.

Ao exportar em modo integral (`full`) com `include_highlights=True`, o sistema deve injetar as marcações visuais (`==texto==[^N]`) e compilar as notas de rodapé no final de cada seção.

### Decisão
**Algoritmo de Inserção Reversa por Seção**:
1. Para cada seção que possua destaques, filtrar os registros de `StudyHighlight` daquela seção.
2. Ordenar os destaques em ordem **decrescente de `start_offset`** (`start_offset DESC, end_offset DESC`).
3. Para cada destaque:
   - Validar se o trecho em `section_text[start_offset:end_offset]` corresponde a `selected_text`.
   - Se houver divergência (ex.: texto foi levemente editado sem recalcular offsets), aplicar busca pontual por substring usando `selected_text` com ancoragem em `prefix`/`suffix`.
   - Se dois destaques colidirem em sobreposição parcial, o destaque mais externo ou prioritário é preservado para evitar quebras de delimitadores no Markdown.
   - Substituir o trecho por:
     - **Markdown**: `=={selected_text}==[^{note_idx}]` (ou `<mark>{selected_text}</mark>[^{note_idx}]` se houver necessidade de compatibilidade com renderizadores sem extensão de realce).
     - **Texto Puro**: `«{selected_text}» [{note_idx}]`.
   - Como a substituição ocorre do final para o início do texto da seção, o deslocamento de caracteres afeta apenas posições posteriores já processadas, preservando a integridade exata de todos os offsets anteriores.
4. Compilar as notas de rodapé numeradas `[^1]`, `[^2]`, etc., e anexá-las ao final da seção correspondente.

### Alternativas Consideradas
- **Pré-processar via AST Markdown (markdown-it no backend)**: Rejeitado por adicionar dependência desnecessária ou exigir parser JS no Node.js/Python, tornando a exportação mais lenta e frágil.
- **Inserção direta de início para o fim com acumulador de delta**: Rejeitado por ser muito mais suscetível a erros de indexação cumulativa ("off-by-one errors") comparado ao algoritmo reverso natural.

---

## 2. Convenção de Marcação Markdown e Texto Puro

### Contexto
Usuários exportam seus estudos para visualização em Obsidian, Typora, VS Code, Notion ou editores de texto simples, além de eventuais impressões.

### Decisão
- **Markdown (`.md`)**:
  - **Grifo/Destaque**: Sintaxe de destaque duplo de igual `==texto destacador==` com fallback semanticamente compatível.
  - **Notas e Perguntas**: Notas de rodapé padrão Markdown / GFM:
    - No corpo: `==texto destacador==[^1]`
    - No rodapé da seção:
      ```markdown
      [^1]: **[Anotação]** Minha reflexão sobre este conceito.
      [^2]: **[Pergunta]** Qual o impacto histórico? *(Resposta: ...)*
      ```
  - **Oclusões (`kind == "hidden"`) no Modo Full**:
    - No corpo: `==texto ocluído==[^3]` com nota: `[^3]: **[Termo Ocluído]** (Trecho marcado para memorização)`.
- **Texto Puro (`.txt`)**:
  - Delimitadores tipográficos limpos `«texto» [1]`.
  - Bloco de rodapé ao término da seção:
    ```text
    --------------------------------------------------------------------------------
    NOTAS DA SEÇÃO:
    [1] [Anotação] Minha reflexão sobre este conceito.
    [2] [Pergunta] Qual o impacto histórico? (Resposta: ...)
    --------------------------------------------------------------------------------
    ```

### Alternativas Consideradas
- **Inserir notas diretamente em parênteses ou blockquotes no meio do texto**: Rejeitado pois polui a leitura contínua do texto original do autor.
- **Usar comentários HTML `<!-- nota -->`**: Rejeitado pois ferramentas como Obsidian e visualizadores comuns escondem os comentários por padrão.

---

## 3. Estrutura Canônica do Caderno de Revisão (Digest) e Modos de Revisão

### Contexto
O Caderno de Revisão tem por objetivo transformar todo o esforço de retenção ativa (perguntas, oclusões, notas e citações) em um material consolidado de estudo rápido e memorização espaçada, operando em escopo de estudo individual ou livro completo.

### Decisão
A estrutura canônica do documento é dividida em 4 blocos temáticos:

1. **Metadados e Sumário**:
   - Título da Obra/Estudo, autor, data de exportação e estatísticas de retenção (ex.: "12 perguntas, 8 termos ocluídos, 5 anotações").
   - No caso de livro completo: Sumário com âncoras para os capítulos e estudos.
2. **Perguntas de Retenção (Active Recall)**:
   - Agrupadas por Capítulo / Estudo.
   - Formato no **Modo Exercício** (`exercise_mode=True`):
     ```markdown
     1. **[Capítulo 2 — Introdução / Estudo 1]** O que caracteriza a primeira fase da teoria?
        *Resposta:* __________________________________________________
     ```
   - Formato no **Modo Estudo** (`exercise_mode=False`):
     ```markdown
     1. **[Capítulo 2 — Introdução / Estudo 1]** O que caracteriza a primeira fase da teoria?
        - **Resposta:** [Texto alvo da resposta registrado na base]
     ```
3. **Trechos Chave & Termos Ocluídos (Cloze Deletions)**:
   - Excertos contextuais contendo o prefixo e sufixo.
   - Formato no **Modo Exercício**:
     `"...o processo de desenvolvimento depende primariamente da [ _______ ] entre os agentes..."`
   - Formato no **Modo Estudo**:
     `"...o processo de desenvolvimento depende primariamente da ==cooperação mútua== entre os agentes..."`
4. **Notas Marginais e Citações Relevantes**:
   - Compilação dos grifos (`kind == "highlight"`), citações (`kind == "quote"`) e anotações (`kind == "note"`), organizadas por seção e estudo com suas devidas observações.
5. **Gabarito de Revisão (Apenas no Modo Exercício)**:
   - Seção final numerada correspondendo exatamente às perguntas e termos ocluídos das seções 2 e 3, permitindo autocorreção rápida.

### Alternativas Consideradas
- **Exportação em formato CSV/Anki Deck**: Considerado para roadmap futuro, mas o foco imediato da F0.6.4 é o Caderno de Leitura em Markdown/Texto Puro conforme a especificação do Roadmap 0.6.

---

## 4. Retrocompatibilidade de Schemas e Endpoints

### Contexto
Os endpoints existentes `/api/books/{book_id}/export` e `/api/studies/{study_id}/export` já são consumidos pelo frontend e por eventuais scripts de backup com parâmetros existentes (`format`, `include_notes`, `include_sections`, `include_source`, `include_metadata`).

### Decisão
- Estender `ExportOptions` no backend com valores default estritamente compatíveis:
  - `include_highlights: bool = True` (se o cliente não enviar, inclui destaques por padrão no full).
  - `export_type: str = "full"` (opções válidas: `"full"`, `"digest"`).
  - `exercise_mode: bool = False` (aplicável quando `export_type == "digest"`).
- Adicionar os novos query parameters com defaults nas rotas FastAPI `export_book` e `export_study`.
- Atualizar `sanitize_filename`:
  - Se `export_type == "digest"`, nomeia o arquivo como:
    `caderno-revisao-{titulo}.md` ou `caderno-revisao-exercicio-{titulo}.md`.
- No frontend, estender `ExportConfig` em `types.ts` e a função auxiliar `buildExportQuery(config)` em `api.ts`. Clientes sem essas opções continuam recebendo o formato integral clássico.

---

## 5. Interface do Usuário no `ExportModal.vue` e Acessibilidade

### Contexto
O modal atual possui seletores para formato e conteúdo do estudo completo. Ele precisa agora permitir a alternância intuitiva entre a exportação do documento integral e o Caderno de Revisão.

### Decisão
- **Layout em Abas/Radio Cards de Modo**:
  - Cartão 1: **Documento Completo** ("Exporta o texto integral do livro ou estudo, com opções de anotações e destaques").
  - Cartão 2: **Caderno de Revisão (Digest)** ("Compila exclusivamente perguntas ativas, termos ocluídos e notas de estudo").
- **Opções Condicionais**:
  - Quando "Documento Completo" estiver selecionado: exibe as opções de seções e o novo checkbox "Incluir destaques e anotações no texto".
  - Quando "Caderno de Revisão" estiver selecionado: oculta opções irrelevantes de texto integral e exibe a opção de destaque:
    - Checkbox: "Modo Exercício (Ocultar respostas com gabarito no final)".
- **Acessibilidade e Usabilidade**:
  - Respeita o padrão de botões e checkboxes acessíveis de pelo menos $44 \times 44\text{px}$.
  - Foco inicial preservado e fechamento via tecla `Escape`.
  - Zero emojis em todo o código fonte e estilo estritamente alinhado às variáveis CSS de tema.
