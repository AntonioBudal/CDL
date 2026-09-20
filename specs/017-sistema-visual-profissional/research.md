# Research & Design Decisions: F09 - Sistema Visual Profissional

**Branch**: `017-sistema-visual-profissional`  
**Feature**: F09 — Sistema Visual Profissional  
**Data**: 2026-09-19  

Este documento registra a análise técnica e as decisões consolidadas de design para a erradicação de emojis, introdução de iconografia vetorial com Lucide Icons, purificação semântica de termos de IA e padronização dos estados de interface (Empty State, Loading Skeleton e Status Badges).

---

## 1. Iconografia Vetorial: Adoção de `lucide-vue-next`

### Decisão
Adotar oficialmente a biblioteca **Lucide Icons** (`lucide-vue-next`) integrada através de um componente envelope unificado `Icon.vue` localizado em `frontend/src/components/ui/Icon.vue`.

### Racional
- **Consistência Visual Editorial:** Lucide possui traço geométrico sóbrio (stroke padrão de 1.5–2px, proporção 24x24px), ideal para produtos de leitura e estudo sério.
- **Tree-Shaking e Performance:** Ao utilizar componentes nomeados ou um mapa estrito de ícones no `Icon.vue`, o empacotador Vite inclui no bundle de produção apenas os glifos realmente utilizados, sem inflar o tamanho do script gerado.
- **Acessibilidade Nativa:** Todos os ícones são renderizados como `<svg>` inline com `aria-hidden="true"` quando puramente decorativos, ou acompanhados de `aria-label` / `role="img"` quando exercem função interativa ou informativa.
- **Adaptação Cromática:** Herdam nativamente `currentColor`, respondendo instantaneamente aos temas Claro, Escuro e Sépia, além da cor de destaque e intensidade de contraste da Superclasse ativa.

### Alternativas Avaliadas e Rejeitadas
- **Conjunto manual de SVGs inline:** Rejeitado devido ao custo contínuo de manutenção e à dificuldade de manter rigor geométrico e espessura de traço idênticos ao expandir as features F01 a F10 da versão 0.4.
- **Heroicons (`@heroicons/vue`):** Rejeitado por possuir catálogo mais restrito de metáforas específicas para estudos, categorização literária e topologia de conhecimento.
- **Webfont de Ícones (ex.: FontAwesome):** Rejeitado categoricamente por depender de download assíncrono de fontes, introduzir FOIT/FOUT (flash de texto/ícone invisível) e quebrar em ambientes estritamente offline ou de rede local restrita.

---

## 2. Componente de Esqueleto de Carregamento (*Loading Skeleton*)

### Decisão
Criar o componente `LoadingSkeleton.vue` (`frontend/src/components/ui/LoadingSkeleton.vue`) baseado em CSS puro utilizando `color-mix` ancorado nas variáveis do sistema (`--bg-surface` e `--border-subtle`).

### Racional
- **Animação Adaptativa:** Pulso suave com gradiente *shimmer* sutil por padrão.
- **Respeito à Acessibilidade e E-Ink:** Comuta automaticamente para bloco estático com opacidade fixa (sem oscilação de brilho) quando `@media (prefers-reduced-motion: reduce)` estiver ativado no sistema operacional ou em modos monocromáticos.
- **Prevenção de Layout Shift:** O componente aceita propriedades tipadas (`width`, `height`, `shape: 'rect' | 'circle' | 'text'`, `lines`) para espelhar exatamente a geometria do elemento real que substituirá, garantindo CLS < 0.05.

### Alternativas Avaliadas e Rejeitadas
- **Spinners circulares tradicionais:** Rejeitados por causarem sensação de lentidão e não comunicarem a estrutura do conteúdo que está sendo carregado.

---

## 3. Componente de Estado Vazio (*Empty State*)

### Decisão
Criar o componente `EmptyState.vue` (`frontend/src/components/ui/EmptyState.vue`) para unificar as telas e contêineres sem dados.

### Racional
- **Estrutura Canônica:**
  1. Ícone vetorial Lucide envolto em círculo discreto com cor atenuada (`var(--text-muted)`).
  2. Título curto e sóbrio (`<h2>` ou `<h3>`).
  3. Parágrafo explicativo orientando a próxima ação do leitor.
  4. Slot de ação primária (ex.: botão "Adicionar Livro", "Importar Fichamento", "Restaurar Acervo").
- **Substituição de Emojis:** Elimina os emojis hardcoded atualmente presentes em `TrashView.vue` (`🗑️`) e `DashboardView.vue` (`📖`).

---

## 4. Purificação Semântica e Terminologias Editoriais

### Decisão
Eliminar 100% das menções a "IA", "resposta do ChatGPT" e "prompt" no frontend e nas mensagens da API, adotando a terminologia canônica **"Fichamento da Fonte"** para o campo `source_response`.

### Mapeamento de Vocabulário Editorial

| Localização | Texto Anterior (Informal / IA) | Novo Texto Canônico (Editorial) |
| :--- | :--- | :--- |
| `StudyView.vue` | "Consultar resposta original" | "Consultar Fichamento da Fonte" |
| `ImportView.vue` (header) | "Importar resposta" | "Importar Fichamento" |
| `ImportView.vue` (label) | "Resposta inteira do ChatGPT" | "Fichamento da Fonte" |
| `ImportView.vue` (placeholder) | "Cole a resposta aqui…" | "Cole o texto-base ou fichamento aqui…" |
| `ImportView.vue` (aviso) | "A resposta mudou. A prévia..." | "O texto foi alterado. A prévia..." |
| `ImportView.vue` (save bar) | "A resposta original será guardada..." | "O fichamento da fonte será preservado..." |
| `BookView.vue` | "Importe uma resposta do ChatGPT para começar." | "Cadastre ou importe um fichamento para começar." |
| `ExportModal.vue` | "Resposta Original de Importação" | "Fichamento da Fonte" |
| `useImportDraft.ts` | "Cole a resposta do ChatGPT." | "Cole o texto-base do fichamento." |
| `backend/app/schemas/imports.py` | "Cole a resposta do ChatGPT para preparar a prévia." | "Cole o texto-base do fichamento para preparar a prévia." |

### Preservação do Banco de Dados
A coluna interna do SQLite continua chamando-se `source_response` na tabela `studies`, garantindo estabilidade absoluta de schema, compatibilidade retroativa e integridade de backups ZIP e restaurações.

---

## 5. Mapeamento de Substituição de Emojis por Ícones Lucide

| Arquivo | Emoji Anterior | Novo Ícone Lucide | Função |
| :--- | :--- | :--- | :--- |
| `BookView.vue` | `✎` | `Pencil` / `Edit3` | Editar capítulo |
| `BookView.vue` | `🗑` | `Trash2` | Excluir capítulo/estudo |
| `TrashView.vue` | `🗑️` | `Trash2` (em `EmptyState`) | Estado de lixeira limpa |
| `DashboardView.vue` | `📖` | `BookOpen` (em `EmptyState`) | Estado de estudos vazios |
| `DashboardView.vue` | `🔥` | `Flame` | Indicador de dias consecutivos |
| `DashboardView.vue` | `✕ Limpar` | `X` + "Limpar" | Limpar filtro de data |
| `BookCover.vue` | `'📖'` | `Book` (SVG vetorial) | Fallback para livro sem capa |
| `TrashConfirmModal.vue` | `⚠️ Atenção:` | `AlertTriangle` + "Atenção:" | Alerta de exclusão definitiva |
| `TrashConfirmModal.vue` | `✕` | `X` | Botão fechar modal |
| `BookEditModal.vue` | `✕` | `X` | Botão fechar modal |
| `ExportModal.vue` | `✕` | `X` | Botão fechar modal |
| `RestoreModal.vue` | `✓ Acervo Restaurado` | `CheckCircle` + "Acervo Restaurado" | Confirmação de restauração |
| `LibraryToolbar.vue` | `✕` | `X` | Limpar campo de busca |
| `App.vue` | SVGs inline manuais | `BookOpen`, `LayoutDashboard`, `Plus`, `Sliders`, `Trash2` | Navegação principal |
