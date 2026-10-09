# Research: F0.7.15 — Templates Estruturados de Estudo

## Contexto e Objetivos Técnicos
A feature F0.7.15 introduz 5 templates canônicos de estudo para orientar o leitor em diferentes modalidades de fichamento (Fichamento Clássico, Estudo de Conceito, Reconstrução de Argumento, Análise Comparativa e Resenha Crítica), sem alterar a estrutura basilar de 4 campos do banco de dados (`summary`, `explanation`, `concepts`, `references`).

---

## Decisões Técnicas

### 1. Catálogo dos Templates Canônicos
- **Decisão**: Centralizar o catálogo em `frontend/src/constants/studyTemplates.ts` como constantes TypeScript estritas e imutáveis.
- **Racional**:
  - Os 5 templates canônicos são fixos e definidos no Roadmap 0.7 para evitar a sobrecarga de um construtor genérico de formulários arrastáveis.
  - A injeção de esqueletos e placeholders em Markdown ocorre exclusivamente no frontend no momento da edição.
  - O backend apenas armazena e valida o identificador textual `template_id: str` no modelo `Study`.
- **Alternativas consideradas**:
  - *Tabela `study_templates` no SQLite*: Rejeitada por violar o princípio de simplicidade da Constituição. Templates não são criados dinamicamente pelos usuários no Roadmap 0.7; criar uma tabela para 5 registros estáticos traria complexidade desnecessária de cache, sincronização e migrações.

### 2. Mapeamento das 4 Seções Analíticas
- **Decisão**: Cada template canônico mapeia proporcionalmente seus tópicos nas seções existentes:
  1. `classico`: `summary` (Resumo Geral), `explanation` (Desenvolvimento), `concepts` (Conceitos-Chave), `references` (Citações e Referências).
  2. `conceito`: `summary` (Definição Essencial), `explanation` (Etimologia e Origem), `concepts` (Aplicações e Exemplos), `references` (Contrapontos e Limites).
  3. `argumento`: `summary` (Tese Central), `explanation` (Premissas e Evidências), `concepts` (Objeções Possíveis), `references` (Conclusão Dialética).
  4. `comparativo`: `summary` (Objeto da Comparação), `explanation` (Pontos de Convergência), `concepts` (Pontos de Divergência), `references` (Síntese Crítica).
  5. `resenha`: `summary` (Contexto e Autor), `explanation` (Julgamento da Tese), `concepts` (Limitações e Pontos Cegos), `references` (Posicionamento do Leitor).
- **Racional**:
  - Preserva 100% da integridade de consultas, indexação de busca textual, marcações de highlights, e cálculos de completude existentes (`has_summary`, `has_explanation`, etc.).
- **Alternativas consideradas**:
  - *Adicionar campos dinâmicos JSON no banco*: Rejeitada categoricamente. Quebraria o contrato histórico do SQLite e a interoperabilidade com todas as views existentes (`StudyView`, `StudyGridView`, `StudyListView`, `StudyTreeView`, `StudyMapView`, `StudyCanvasView`).

### 3. Proteção e Política de Troca de Template (Q1: A)
- **Decisão**: Quando o formulário já contém anotações digitadas em qualquer das 4 seções, a troca de template abre um diálogo modal de confirmação com três opções:
  1. **Substituir Conteúdo**: Limpa e substitui os campos pelo novo esqueleto do template.
  2. **Anexar ao Final**: Concatena o novo esqueleto ao final do texto já existente, separando por duas quebras de linha.
  3. **Cancelar**: Fecha o diálogo sem realizar qualquer alteração nos campos.
- **Racional**:
  - Garante total segurança ao trabalho intelectual do usuário, sem risco de deleção acidental de notas manuscritas ao explorar modelos visuais.
- **Alternativas consideradas**:
  - *Substituição forçada silenciosa*: Rejeitada por risco inaceitável de perda de dados.
  - *Apenas anexar sem opção de substituir*: Rejeitada porque o usuário muitas vezes deseja reiniciar a estrutura com um modelo mais limpo.

### 4. Promoção de Capturas do Inbox (Q2: A)
- **Decisão**: A rota `/importar` quando acionada via `promote_inbox_id` inicia com o template `classico` por padrão, permitindo que o usuário altere livremente o template no seletor do editor.
- **Racional**: Mantém o fluxo de promoção de ideias rápido e com fricção mínima.

### 5. Persistência e Migração Alembic
- **Decisão**: Criar a migração `0029_add_template_id_to_studies.py` adicionando a coluna `template_id` (`String(30)`, default `'classico'`, `server_default='classico'`, `nullable=False`).
- **Racional**:
  - Todo o acervo pré-existente (estudos antigos sem template) passa a ter `'classico'` como padrão de forma consistente no banco.
  - Compatibilidade garantida com SQLite WAL e sincronização incremental.

### 6. Acessibilidade e Componentes de Interface
- **Decisão**:
  - Criar `TemplateSelectorModal.vue` com navegação por teclado (`Tab`, `Esc`, `Enter`), prévia de cada template em cards distintos, e alvos táteis mínimos de $44 \times 44$px para mobile.
  - Integrar seletor sutil em `StudyEditorFields.vue` e `StudyEditView.vue`.
  - Exibir badge sutil e semântico em `StudyView.vue` para identificar o modelo utilizado quando for diferente do clássico.
- **Racional**: Respeita rigorosamente a Constituição Visual (sem emojis, contraste adaptativo e alvos ergonômicos).
