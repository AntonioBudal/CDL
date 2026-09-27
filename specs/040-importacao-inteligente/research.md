# Research: F0.6.1 — Importação Inteligente

**Feature**: `040-importacao-inteligente`  
**Date**: 2026-09-27  
**Status**: Concluído (Decisões de Design Consolidadas)

---

## 1. Reconhecimento Tolerante de Cabeçalhos e Variações Semânticas

### Contexto
O parser original em `backend/app/services/import_parser.py` utilizava correspondência rígida de títulos (`## Resumo`, `## Explicação`, etc.), rejeitando títulos sem `##`, títulos com negrito (`**Resumo**`), numerações ordinais (`1. Resumo`) e variações sinônimas em português frequentes em respostas de LLMs (ex.: "Visão Geral", "Aprofundamento", "Vocabulário", "Fontes").

### Decisão
1. **Dicionário Expandido de Sinônimos**:
   Mapear termos sinônimos normalizados (sem acentos, em caixa baixa via NFD) para as 4 chaves canônicas:
   - `summary`: `resumo`, `visao geral`, `visao-geral`, `sintese`, `ideia central`, `introducao`.
   - `explanation`: `explicacao`, `aprofundamento`, `desenvolvimento`, `analise`, `compreensao`, `detalhamento`.
   - `concepts`: `conceitos`, `conceitos-chave`, `termos`, `termos-chave`, `vocabulario`, `glossario`, `definicoes`.
   - `references`: `referencias`, `fontes`, `bibliografia`, `leituras complementares`, `obras citadas`.
2. **Regex de Cabeçalho Tolerante**:
   Permitir marcações Markdown flexíveis (`#`, `##`, `###`, `####`), delimitadores de negrito (`**...**`, `__...__`), prefixos numéricos/ordinais (`1.`, `1 -`, `I.`, `Seção 1:`) e sufixos (`:`, `-`), mantendo isolamento absoluto de code fences (` ``` ` e `~~~`).

### Justificativa
A normalização determinística por regex e dicionário semântico roda instantaneamente (<5ms para 50k caracteres), sem dependências externas ou consumo de rede, atendendo perfeitamente ao princípio constitucional de execução local isolada e determinística.

### Alternativas Consideradas
- *Uso de embeddings locais ou modelo de PLN (spaCy/FastText)*: Rejeitado por adicionar centenas de megabytes de dependências desnecessárias, tempo de inicialização lento e risco de não-determinismo.
- *LLM local (Ollama)*: Rejeitado por exigir hardware dedicado com GPU, dependência externa e latência de vários segundos.

---

## 2. Tratamento de Conteúdo Não Classificado (`unassigned_text`)

### Contexto
Respostas geradas por modelos de linguagem com frequência incluem saudações introdutórias (ex.: "Certamente! Aqui está o resumo do capítulo solicitado:"), comentários ou notas de rodapé que não pertencem a nenhuma das 4 seções.

### Decisão
1. **Sinalização Visual e Atribuição Rápida**:
   Exibir na prévia uma caixa de destaque para o texto não classificado com botões de 1 clique:
   - "Mover para Resumo"
   - "Mover para Explicação"
   - "Mover para Conceitos"
   - "Mover para Referências"
2. **Política de Salvamento Sem Reatribuição**:
   Se o usuário decidir salvar diretamente sem reatribuir o texto não classificado, o sistema anexa automaticamente o conteúdo ao final da seção `explanation` precedido de um separador (`\n\n---\n**Conteúdo Adicional:**\n`), garantindo zero perda de dados.
3. **Preservação Integral**:
   O campo `source_response` do banco armazena o texto colado original 100% inalterado.

### Justificativa
Alinha-se com a diretriz de UX definida na especificação e aprovada pelo usuário (Opção A). O leitor não é bloqueado por preâmbulos do chatbot e nenhuma linha se perde.

### Alternativas Consideradas
- *Bloquear o salvamento com erro*: Rejeitado por quebrar o princípio de baixa fricção.
- *Descartar o texto das seções*: Rejeitado por violar o princípio de não-perda de conteúdo anotado.

---

## 3. Gatilho de Atualização da Prévia Inteligente e Estado Reativo

### Contexto
A experiência anterior exigia um clique obrigatório no botão "Preparar prévia", seguido de rolagem até a seção 2 da página para ver os campos manuais.

### Decisão
1. **Auto-disparo no Evento `paste`**:
   Ao colar o texto na área principal (`source-response`), a função `prepare()` é disparada automaticamente, trazendo a análise estruturada em menos de 100ms.
2. **Botão de Sincronização Sob Demanda**:
   Se o leitor editar manualmente o texto original após a colagem inicial, o sistema sinaliza que o texto mudou e exibe o botão destacado "Atualizar prévia".
3. **Fluxo Principal Direto**:
   O botão "Salvar Estudo" fica posicionado imediatamente abaixo da prévia estruturada, permitindo ao usuário completar a importação no padrão `Colar → Conferir → Salvar`.

### Justificativa
Reduz cliques desnecessários na maioria dos casos (onde o usuário apenas copia do ChatGPT/Claude e cola no Caderno), mantendo controle caso faça ajustes no texto-fonte.

### Alternativas Consideradas
- *Debounce a cada tecla digitada*: Rejeitado por gerar requisições desnecessárias a cada caractere e potencial sensação de instabilidade ou perda de foco durante digitação manual.

---

## 4. Disposição dos Campos Manuais Legados (Modo Avançado)

### Contexto
Alguns usuários ou cenários específicos exigem edição granular de cada seção em campos separados (`StudyEditorFields.vue`) antes do salvamento.

### Decisão
1. **Painel Colapsável (Accordion)**:
   Encapsular os 4 campos `<textarea>` manuais em um bloco expansível `<details class="manual-adjustment-panel">` com o título *"Ajuste manual detalhado (opcional)"*, recolhido por padrão.
2. **Sincronização Bidirecional**:
   O conteúdo exibido nos campos manuais reflete as seções da prévia. Edições manuais feitas nesses campos atualizam diretamente o payload de salvamento sem sobrescrever destrutivamente o `source_response`.

### Justificativa
Mantém a interface limpa e focada para 90% dos casos de uso, sem remover o recurso avançado para os 10% que desejam ajuste fino linha por linha.

### Alternativas Consideradas
- *Remover completamente os 4 campos*: Rejeitado para não diminuir a autonomia do usuário experiente.
- *Abas de tela*: Rejeitado por introduzir complexidade de navegação e duplicação de botões de salvamento.
