# Research & Technical Decisions: F09.5 — Refatoração de Temas, Persistência e Correções Visuais

## 1. Persistência de Tema e Prevenção de Reset no F5 / Navegação

### Contexto e Diagnóstico do Problema
Atualmente, o Caderno possui dois subsistemas de preferências visuais:
1. `appearance-bootstrap.js` (executado no `<head>` do `index.html`), que grava e lê `caderno.aparencia.v2` no `localStorage` com IDs nominais de tema (`porcelana`, `breu`, `fiorde`, etc.).
2. `usePreferences.ts` (composable e store reativa montada com o Vue), que mantém um estado reativo em `caderno_user_preferences` com `theme_mode` genérico (`dark`/`light`).

**Causa Raiz do Bug**:
Quando o leitor escolhe um tema como "Nord" (`fiorde`), `appearance-bootstrap.js` aplica `data-theme="fiorde"`. Porém, ao recarregar a página ou navegar, a store `usePreferences` inicializava com seu valor padrão `theme_mode: 'dark'` e chamava `applyPreferencesToDocument()`, que sobrescrevia `data-theme` para `"dark"` ou revertia para o primeiro elemento padrão da lista.

### Decisão Técnica
- **Fonte de Verdade Unificada**:
  - O tema ativo passa a ser representado exclusivamente pelo seu identificador nominal (ex.: `papel-fosco`, `nord`, etc.).
  - A leitura do `localStorage` (`caderno.aparencia.v2`) continua ocorrendo no `<head>` para blindagem contra Flash of Unstyled Content (FOUC).
  - Em `main.ts`, imediatamente antes de `app.mount('#app')`, o composable de preferências lê de forma síncrona o tema ativo e inicializa o estado reativo da aplicação.
  - Em `usePreferences.ts`, a função `applyPreferencesToDocument` é atualizada para respeitar os identificadores nominais do catálogo oficial e não mais forçar `theme_mode` genérico se houver preferência nominal salva.
- **Alternativas Consideradas**:
  - *Alternativa B (Delegação Total sem Store)*: Rejeitada porque a store reativa precisa informar componentes Vue (como gráficos e seletores) sobre a mudança reativa de tema sem depender de `window.dispatchEvent` manual.

---

## 2. Nomenclatura Simplificada e Catálogo de 10 Temas

### Decisão Técnica
O catálogo de temas da plataforma é rigorosamente consolidado em **10 temas** com nomes diretos e substantivos:

#### A. 5 Temas Preservados (Nomenclatura Simplificada - Q1: Opção B)
1. `pergaminho` (Claro) → Nome de exibição: **Sépia**
2. `e-ink` (Monocromático) → Nome de exibição: **E-Ink**
3. `solario` (Claro) → Nome de exibição: **Solarized**
4. `fiorde` (Escuro) → Nome de exibição: **Nord**
5. `voltagem` (Escuro) → Nome de exibição: **Cyber**

#### B. 5 Novos Temas Minimalistas de Baixo Contraste (Q2: Opção A)
6. `papel-fosco` (Claro - **Padrão do Sistema**):
   - Fundo: `#f5f5f5`, Superfície: `#ffffff`, Superfície soft: `#ebebeb`
   - Texto: `#333333`, Muted: `#555555`, Destaque/Accent: `#475569` (ardósia/cinza-azulado suave)
   - Bordas: `#dcdcdc`, Borda forte: `#94a3b8`
7. `noite-suave` (Escuro):
   - Fundo: `#1e1e24`, Superfície: `#26262e`, Superfície soft: `#2f2f38`
   - Texto: `#d4d4d4`, Muted: `#9ca3af`, Destaque/Accent: `#64748b` (azul acinzentado opaco)
   - Bordas: `#383842`, Borda forte: `#4b5563`
8. `cinza-neutro` (Claro):
   - Fundo: `#e8e8e8`, Superfície: `#f0f0f0`, Superfície soft: `#dedede`
   - Texto: `#2b2b2b`, Muted: `#52525b`, Destaque/Accent: `#52525b` (cinza médio-escuro)
   - Bordas: `#cfcfcf`, Borda forte: `#71717a`
9. `grafite` (Escuro):
   - Fundo: `#222222`, Superfície: `#2a2a2a`, Superfície soft: `#333333`
   - Texto: `#cccccc`, Muted: `#888888`, Destaque/Accent: `#78716c` (marrom-acinzentado/bege discreto)
   - Bordas: `#3d3d3d`, Borda forte: `#57534e`
10. `monocromatico` (Claro):
    - Fundo: `#ffffff`, Superfície: `#f8fafc` (painéis cinza gelo sutil), Superfície soft: `#f1f5f9`
    - Texto: `#111111`, Muted: `#444444`, Destaque/Accent: `#111111` (preto ou contornos pretos)
    - Bordas: `#d1d5db`, Borda forte: `#111111`

#### C. 5 Temas Excluídos com Migração Automática
- `porcelana` → Migrado automaticamente para `papel-fosco`
- `breu` → Migrado automaticamente para `noite-suave`
- `vinil` → Migrado automaticamente para `grafite`
- `sequoia` → Migrado automaticamente para `noite-suave`
- `vespera` → Migrado automaticamente para `noite-suave`

---

## 3. Correções Dimensionais e Estabilização de SVGs

### Problemas e Resoluções
1. **Empty State em "Estudos Compartilhados" (`SharedStudiesList.vue`)**:
   - *Causa*: SVGs puros herdando 100% de largura do container ou sem classe de contenção de altura quando estilizados sem classes Tailwind compiladas.
   - *Resolução*: Fixar contenção máxima dimensional no container e no elemento vetorial: `max-width: 120px; max-height: 120px; width: 100%; height: auto; margin: 0 auto;`.
2. **Botão "Compartilhar" (`StudyView.vue`)**:
   - *Causa*: SVG sem `flex-shrink: 0` e largura relativa que forçava a palavra a quebrar em linhas verticais ("Comp / artilh / ar").
   - *Resolução*: No botão `.share-action`, aplicar `display: inline-flex; align-items: center; gap: 8px; white-space: nowrap;`. No ícone SVG, fixar `width: 1.2em; height: 1.2em; flex-shrink: 0; min-width: 1.2em; min-height: 1.2em;`.
3. **Modal "Exportar Estudo" (`ExportModal.vue`)**:
   - *Causa*: Checkboxes e rádios estilizados estourando ou sobrepondo labels descritivas.
   - *Resolução*: Fixar o tamanho dos inputs/ícones em `24px` (`width: 24px; height: 24px; flex-shrink: 0;`), com alinhamento flex centralizado com os textos descritivos à direita.

---

## 4. Contraste Dinâmico e Herança de Cores do Tema

### Problemas e Resoluções
1. **Modal "Exportar Estudo" (`ExportModal.vue`)**:
   - *Causa*: Uso de variáveis inexistentes (`--color-bg`, `--text-primary`), gerando textos pretos em fundo preto sob temas escuros.
   - *Resolução*: Padronizar nas variáveis canônicas: `--color-surface` para o painel, `--color-text` para títulos, `--color-muted` para descrições e `--color-border` para contornos.
2. **Status de Leitura (`StudyStatusBadge.vue`)**:
   - *Causa*: Cores de fundo e texto estáticas com baixo contraste em temas escuros.
   - *Resolução*: Adequar as classes de badges (`.badge-rascunho`, `.badge-em-estudo`, `.badge-revisado`, `.badge-concluido`) para usar pares contrastantes calibrados que respeitem o esquema de cores claro/escuro.
3. **Cabeçalho de Agrupamento (`GroupSection.vue`)**:
   - *Causa*: `.group-toggle-btn` com fundo colorido/saturado sob certas superclasses ou temas contrastava mal com títulos escuros e ícone cinza.
   - *Resolução*: Garantir que `.group-toggle-btn` herde `--color-surface` e `--color-text`, ou, ao receber fundo de destaque saturado, force explicitamente `color: #ffffff` e `stroke: #ffffff` para o ícone chevron.
