# Research & Technical Decisions: F0.6.2 — Seleção e Ações Contextuais

**Feature**: F0.6.2 — Seleção e Ações Contextuais  
**Directory**: `specs/041-selecao-acoes-contextuais/`  
**Date**: 2026-09-27  

---

## 1. Ancoragem de Trechos sobre HTML Renderizado (Markdown-it)

### Contexto
O Leitorum renderiza as seções do estudo (`summary`, `explanation`, `concepts`, `references`) utilizando `markdown-it` com `html: false` no componente `MarkdownContent.vue`. Quando o usuário seleciona um trecho na tela, a seleção ocorre sobre nós de texto (`TextNode`) dentro da árvore DOM gerada (que pode conter `<p>`, `<strong>`, `<em>`, `<code>`, `<li>`, etc.).

### Decisão
Adotar o modelo híbrido **Text Quote Selector + Text Position Selector** (baseado na especificação W3C Web Annotation):
1. **No momento da seleção**:
   - Capturar o texto literal selecionado: `selected_text = selection.toString().trim()`.
   - Capturar contexto adjacente para desambiguação: `prefix` (até 30 caracteres anteriores no texto da seção) e `suffix` (até 30 caracteres posteriores).
   - Calcular os offsets `start_offset` e `end_offset` relativos ao `textContent` puro da seção inteira.
2. **Na renderização / restauração**:
   - Um composable reutilizável (`useHighlightOverlay` ou `highlightRenderer.ts`) percorre os nós de texto do elemento renderizado (`TreeWalker` filtrando `NodeFilter.SHOW_TEXT`).
   - Localiza a ocorrência com base em `start_offset`/`end_offset` e valida contra `selected_text` (com `prefix`/`suffix` como fallback tolerante a pequenas divergências de espaçamento ou edições posteriores).
   - Divide os nós de texto com `splitText` e envolve as frações correspondentes em elementos `<mark class="study-highlight hl-{color}" data-highlight-id="{id}">` sem corromper a árvore de tags Markdown circundante.

### Alternativas Consideradas
- **Inserir marcação inline no Markdown original (`==destaque==` ou `<mark>`)**: Rejeitada. Polui o texto fonte do usuário, corrompe a fidelidade da importação e impede que múltiplos metadados (anotações reflexivas, modo pergunta, autoria) coexistam sem sintaxe proprietária complexa.
- **Armazenamento de seletores CSS / XPath rígidos**: Rejeitada. Frágil a qualquer variação na versão do parser Markdown ou estilos CSS.

---

## 2. Ergonomia da Barra Contextual: Desktop vs. Mobile

### Contexto
Em navegadores desktop, a barra flutuante adjacente à seleção (`floating toolbar`) oferece o fluxo de menor atrito visual. Contudo, em dispositivos móveis (smartphones/tablets), a seleção nativa do sistema operacional (Android / iOS) dispara automaticamente menus do sistema ("Copiar", "Compartilhar", "Pesquisar na Web") que cobrem elementos flutuantes próximos ao texto.

### Decisão
Implementar comportamento adaptativo baseado no dispositivo e viewport:
1. **Desktop / Cursor (> 768px)**:
   - A barra flutuante é posicionada com `position: fixed` imediatamente acima (ou abaixo, se próximo ao topo da tela) da caixa delimitadora da seleção (`range.getBoundingClientRect()`), com margens de segurança para mantê-la dentro do viewport.
2. **Mobile / Telas de Toque (<= 768px)**:
   - A barra contextual é apresentada como uma **Barra de Ação Fixa / Mini Bottom Sheet** na base da tela (`bottom: 0`, com suporte a `env(safe-area-inset-bottom)`).
   - Os botões possuem dimensões ergonômicas de toque mínimas de 44x44 pixels (WCAG 2.1 AAA).
   - Essa abordagem elimina completamente a disputa de espaço e eventos de toque com a barra nativa do sistema móvel.

### Alternativas Consideradas
- **Barra flutuante fixa acima no mobile com offset aumentado**: Rejeitada. Telas pequenas e seleções no terço superior da tela ainda sofrem oclusão e cortes indesejados.
- **Botão flutuante único FAB**: Rejeitada. Exigiria dois toques para qualquer ação simples de marca-texto, reduzindo a fluidez da leitura.

---

## 3. Escopo das 5 Ações Contextuais no Editor

### Decisão
Implementar de ponta a ponta as **5 ações contextuais** no mesmo ciclo:
1. **Destacar (Marca-texto)**:
   - Paleta suave com 5 cores canônicas: Amarelo suave (`#fef08a`), Verde menta (`#bbf7d0`), Azul celeste (`#bae6fd`), Rosa pálido (`#fbcfe8`) e Lilás (`#e9d5ff`).
   - Ação imediata de 1 clique para a cor padrão com seletor popover para troca rápida.
2. **Anotar (Nota Conectada)**:
   - Abre popover compacto de edição para redigir uma reflexão vinculada ao trecho.
   - Trecho anotado recebe indicador visual discreto (ícone 📝 ou sublinhado pontilhado suave).
3. **Copiar como Citação**:
   - Formata automaticamente para a área de transferência:
     ```markdown
     > "Trecho selecionado do estudo"
     >
     > — *Título do Estudo*, Capítulo (Livro)
     ```
   - Exibe feedback visual tipo toast "Citação copiada!".
4. **Ocultar Trecho (Oclusão / Active Recall)**:
   - Marca o trecho com `kind = 'hidden'`.
   - Renderiza um bloco de oclusão com blur/fundo sólido e botão interativo `[Revelar]`.
   - Ao clicar, o trecho é revelado instantaneamente; um novo clique permite ocultar novamente.
5. **Transformar em Pergunta (Prompt de Retenção)**:
   - Permite ao leitor redigir uma pergunta associada ao trecho (ex.: "Qual o conceito-chave aqui?").
   - Na visualização, o texto do trecho fica oculto e exibe uma caixa elegante: `❓ Pergunta: [Texto da pergunta] [Ver resposta]`.
   - Ao clicar em "Ver resposta", expande o trecho original para autocorreção do estudante.

---

## 4. Persistência Relacional e Modelo de Dados

### Decisão
Criar tabela dedicada `study_highlights` gerenciada via SQLAlchemy 2.0 e migração Alembic `0020_add_study_highlights.py`:
- `id`: Inteiro primário autoincrementado.
- `study_id`: FK para `studies.id` com `ondelete="CASCADE"`.
- `user_id`: FK para `users.id` com `ondelete="CASCADE"`.
- `section`: Enum / String (`summary`, `explanation`, `concepts`, `references`, `source_response`).
- `start_offset`: Inteiro (posição inicial no texto puro).
- `end_offset`: Inteiro (posição final no texto puro).
- `selected_text`: Texto literal da passagem.
- `prefix`: String(150) (contexto anterior).
- `suffix`: String(150) (contexto posterior).
- `color`: String(30) (cor do destaque, default `yellow`).
- `kind`: String(30) (`highlight`, `note`, `quote`, `hidden`, `question`).
- `note`: Texto (conteúdo da anotação ou enunciado da pergunta).
- `created_at` e `updated_at`: `UTCDateTime`.

### Endpoints REST
- `GET /api/studies/{study_id}/highlights`: Lista todos os destaques do estudo pertencentes ao usuário (ou visíveis com permissão).
- `POST /api/studies/{study_id}/highlights`: Cria um novo destaque.
- `PATCH /api/studies/{study_id}/highlights/{highlight_id}`: Atualiza cor, nota ou tipo.
- `DELETE /api/studies/{study_id}/highlights/{highlight_id}`: Remove o destaque.
