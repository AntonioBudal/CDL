# Arquitetura de Temas, Persistência e Sistema Visual — Leitorum

Este documento consolida as diretrizes da **Feature 9.5 (Refatoração de Temas, Persistência e Correções Visuais)**, definindo o catálogo canônico de 10 temas, a estratégia de persistência síncrona contra regressão no reload (F5) e regras de contenção e contraste.

---

## 1. Catálogo Canônico de Temas (10 Temas)

O catálogo de temas é consolidado em exatamente 10 opções focadas em sobriedade estética, leitura prolongada e conforto ocular, divididas em 5 temas minimalistas de baixo contraste e 5 clássicos consagrados com nomenclatura direta e substantiva:

### A. Novos Temas Minimalistas de Baixo Contraste
1. **Papel Fosco (`papel-fosco`)** — *Claro (Padrão Oficial do Sistema)*:
   - Fundo: `#f5f5f5` | Superfície: `#ffffff` | Texto: `#333333` | Muted: `#555555` | Destaque: `#475569` (ardósia/cinza-azulado suave).
2. **Noite Suave (`noite-suave`)** — *Escuro*:
   - Fundo: `#1e1e24` | Superfície: `#26262e` | Texto: `#d4d4d4` | Muted: `#9ca3af` | Destaque: `#64748b` (azul acinzentado opaco).
3. **Cinza Neutro (`cinza-neutro`)** — *Claro*:
   - Fundo: `#e8e8e8` | Superfície: `#f0f0f0` | Texto: `#2b2b2b` | Muted: `#52525b` | Destaque: `#52525b` (cinza médio-escuro).
4. **Grafite (`grafite`)** — *Escuro*:
   - Fundo: `#222222` | Superfície: `#2a2a2a` | Texto: `#cccccc` | Muted: `#888888` | Destaque: `#78716c` (marrom-acinzentado/bege discreto).
5. **Monocromático (`monocromatico`)** — *Claro*:
   - Fundo: `#ffffff` | Superfície: `#f8fafc` | Texto: `#111111` | Muted: `#444444` | Destaque: `#111111` (preto sólido e contornos nítidos).

### B. Temas Clássicos Preservados (Nomes Simplificados)
6. **Sépia (`pergaminho`)** — *Claro*: Fundo `#e7cca0`, texto `#35200f`, destaque `#873018`.
7. **E-Ink (`e-ink`)** — *Monocromático*: Fundo `#ffffff`, texto `#000000`, contraste puro para e-readers.
8. **Solarized (`solario`)** — *Claro*: Fundo `#fdf6e3`, texto `#3f5962`, destaque `#00686d`.
9. **Nord (`fiorde`)** — *Escuro*: Fundo `#2e3440`, texto `#eceff4`, destaque `#98d0e0`.
10. **Cyber (`voltagem`)** — *Escuro*: Fundo `#181820`, texto `#eceaf4`, destaque `#f6ff00`.

### C. Temas Excluídos e Migração Automática
Os temas `porcelana`, `breu`, `vinil`, `sequoia` e `vespera` foram completamente expurgados do código. Qualquer preferência legada salva em `localStorage` ou backend é automaticamente migrada:
- `porcelana` ou `light` → `papel-fosco`
- `breu`, `sequoia`, `vespera` ou `dark` → `noite-suave`
- `vinil` → `grafite`
- `sepia` → `pergaminho`

---

## 2. Persistência Síncrona e Prevenção de Reset (F5 / Rotas)

### Diagnóstico da Causa Raiz
Anteriormente, o script de bootstrap aplicava o tema salvo nominalmente, mas a inicialização do Vue montava `usePreferences` com o valor default genérico `'dark'`, disparando `applyPreferencesToDocument` e sobrescrevendo o tema real para um valor genérico ou revertendo para o primeiro item da lista ao recarregar a página ou transitar de rota.

### Arquitetura de Blindagem
1. **Bootstrap Precoce (`appearance-bootstrap.js`)**: Executa imediatamente antes do parse do DOM e normaliza os identificadores em `caderno.aparencia.v2`.
2. **Hidratação Síncrona (`main.ts`)**: `usePreferences().loadFromLocal()` é chamado de maneira síncrona antes de `app.mount('#app')`, lendo o tema ativo de `caderno.aparencia.v2` e populando o estado reativo.
3. **Resolução Canônica (`usePreferences.ts`)**: A função `resolveCanonicalTheme` valida e restringe valores, impedindo que strings arbitrárias ou desatualizadas sobrescrevam o atributo `data-theme`.
4. **Sincronização Bidirecional (`SettingsView.vue`)**: Qualquer comutação manual de tema atualiza simultaneamente a store de aparência local e a store de sincronização remota (`user_preferences`).

---

## 3. Contenção Dimensional e Blindagem Vetorial (SVG)

1. **Estado Vazio em Estudos Compartilhados (`SharedStudiesList.vue`)**:
   - Classe `.empty-state-svg` com `max-width: 120px; max-height: 120px; width: 100%; height: auto; margin: 0 auto;`.
2. **Botão Compartilhar (`StudyView.vue`)**:
   - Classe `.share-action` com `display: inline-flex; align-items: center; gap: 8px; white-space: nowrap;`.
   - SVG filho restrito a `width: 1.2em; height: 1.2em; flex-shrink: 0; min-width: 1.2em; min-height: 1.2em;`.
3. **Seletores do Modal de Exportação (`ExportModal.vue`)**:
   - Inputs radio e checkbox fixados rigidamente em `24x24px` (`width: 24px; height: 24px; min-width: 24px; min-height: 24px; flex-shrink: 0;`).

---

## 4. Contraste Dinâmico e Herança de Tokens

1. **Modal de Exportação (`ExportModal.vue`)**:
   - Padronizado no uso das variáveis canônicas de `palettes.css`: `--color-surface`, `--color-text`, `--color-muted`, `--color-border`, `--color-accent`.
2. **Badges de Status (`StudyStatusBadge.vue`)**:
   - Regras específicas para temas escuros (`noite-suave`, `grafite`, `fiorde`, `voltagem`) com transparências e contrastes calibrados (WCAG AA).
3. **Cabeçalhos de Agrupamento (`GroupSection.vue`)**:
   - `.group-header`, `.group-title`, `.group-chevron-wrap` e `.group-count-badge` utilizam variáveis do tema e forçam alto contraste em fundos escuros e saturados.
