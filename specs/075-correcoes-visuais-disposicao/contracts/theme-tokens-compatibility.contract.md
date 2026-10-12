# Contract: Camada de Compatibilidade de Tokens CSS (F0.8.10)

**Diretório**: `specs/075-correcoes-visuais-disposicao/contracts/`  
**Arquivo**: `theme-tokens-compatibility.contract.md`  
**Status**: Normativo

---

## 1. Contrato de Declaração de Variáveis CSS em `tokens.css`

O seletor `:root` em `frontend/src/tokens.css` DEVE conter a seguinte matriz de declarações como apelidos diretos para as 127 variáveis canônicas de `tokens.css` e `palettes.css`:

```css
:root {
  /* =========================================================================
     Camada de Compatibilidade de Tokens Legados (Feature 0.8.10)
     Garante herança perfeita de todos os 10 temas em componentes legados
     ========================================================================= */

  /* Cores de Texto */
  --color-text-muted: var(--color-muted);
  --color-text-secondary: var(--color-subtle);
  --color-text-primary: var(--color-text);
  --color-text-main: var(--color-text);
  --color-text-subtle: var(--color-subtle);
  --color-text-contrast: var(--color-text);
  --color-text-dim: var(--color-subtle);
  --color-ink: var(--color-text);
  --text: var(--color-text);
  --text-muted: var(--color-muted);
  --text-secondary: var(--color-subtle);
  --text-primary: var(--color-text);
  --text-main: var(--color-text);
  --muted: var(--color-muted);

  /* Cores Primárias e de Destaque */
  --color-primary: var(--color-accent);
  --color-primary-hover: var(--color-accent-hover);
  --color-primary-light: var(--color-selected-bg);
  --color-primary-subtle: var(--color-selected-bg);
  --color-primary-border: var(--color-border-hover);
  --color-accent-subtle: var(--color-selected-bg);
  --color-accent-hover-subtle: var(--color-tab-hover);
  --accent: var(--color-accent);
  --accent-color: var(--color-accent);
  --accent-hover: var(--color-accent-hover);
  --accent-text: var(--color-on-accent);
  --accent-subtle: var(--color-selected-bg);
  --primary: var(--color-accent);
  --primary-light: var(--color-selected-bg);
  --ring-focus: var(--color-accent);

  /* Cores de Fundo e Superfície */
  --color-bg: var(--color-page);
  --color-bg-subtle: var(--color-surface-soft);
  --color-bg-alt: var(--color-surface-soft);
  --color-bg-hover: var(--color-surface-hover);
  --color-bg-surface: var(--color-surface);
  --color-bg-base: var(--color-page);
  --color-bg-muted: var(--color-surface-soft);
  --color-bg-primary: var(--color-accent);
  --color-background: var(--color-page);
  --color-card-bg: var(--color-surface);
  --color-surface-subtle: var(--color-surface-soft);
  --color-surface-muted: var(--color-surface-inset);
  --color-surface-elevated: var(--color-surface);
  --color-surface-alt: var(--color-surface-soft);
  --color-surface-selected: var(--color-selected-bg);
  --color-surface-ground: var(--color-page);
  --color-surface-input: var(--color-surface);
  --card: var(--color-surface);
  --card-bg: var(--color-surface);
  --bg-surface: var(--color-surface);
  --bg-surface-elevated: var(--color-surface);
  --bg-muted: var(--color-surface-soft);
  --bg-hover: var(--color-surface-hover);

  /* Bordas */
  --color-border-subtle: var(--color-border-divider);
  --color-border-accent: var(--color-accent);
  --border: var(--color-border);
  --border-subtle: var(--color-border-divider);

  /* Estados de Erro / Alerta / Sucesso */
  --color-danger: var(--color-error-text);
  --color-danger-text: var(--color-error-text);
  --color-danger-hover: var(--color-error-detail);
  --color-danger-subtle: var(--color-error-bg);
  --color-border-danger: var(--color-error-border);
  --color-bg-danger-subtle: var(--color-error-bg);
  --color-text-danger: var(--color-error-text);
  --color-accent-danger: var(--color-error-text);
  --color-error: var(--color-error-text);
  --danger: var(--color-error-text);

  --color-warning: var(--color-warning-text);
  --color-warning-subtle: var(--color-warning-bg);
  --color-warning-hover: var(--color-warning-text);
  --color-bg-warning: var(--color-warning-bg);
  --color-border-warning: var(--color-warning-border);

  --color-success: var(--color-success-text);
  --color-bg-success: var(--color-surface-soft);
  --color-border-success: var(--color-border);

  --color-neutral-subtle: var(--color-surface-soft);

  /* Selos de Status de Estudo */
  --badge-draft-bg: transparent;
  --badge-draft-text: var(--color-muted);
  --badge-draft-border: var(--color-border);
  --badge-study-bg: transparent;
  --badge-study-text: var(--color-accent);
  --badge-study-border: var(--color-accent);
  --badge-reviewed-bg: transparent;
  --badge-reviewed-text: var(--color-warning-text);
  --badge-reviewed-border: var(--color-warning-border);
  --badge-done-bg: transparent;
  --badge-done-text: var(--color-success-text);
  --badge-done-border: var(--color-success-text);

  --color-status-rascunho: var(--color-muted);
  --color-status-andamento: var(--color-accent);
  --color-status-revisado: var(--color-warning-text);
  --color-status-concluido: var(--color-success-text);

  /* Raios e Geometria */
  --radius-sm: var(--radius-small);
  --radius-md: var(--radius-card);
  --radius-lg: var(--radius-panel);
  --radius-surface: var(--radius-card);
  --radius: var(--radius-card);
  --radius-full: 9999px;
  --border-radius: var(--radius-card);
  --sc-border-radius: var(--radius-card);

  /* Sombras */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-surface: var(--shadow-panel);
  --sc-box-shadow: none;

  /* Tipografia e Dimensões Complementares */
  --font-family-serif: var(--font-serif);
  --text-h2: 1.5rem;
  --drawer-width: 320px;
}
```

## 2. Regra de Integridade e Validação Automática

O teste de integração `tests/feature-075-css-tokens-integrity.test.mjs` DEVE:
1. Ler e consolidar todas as variáveis declaradas em `tokens.css` e `palettes.css`.
2. Analisar todos os arquivos `.vue` em `frontend/src/`.
3. Para cada chamada `var(--nome-variavel)`, verificar pertinência no conjunto consolidado.
4. Falhar com código de saída $\neq 0$ caso qualquer variável não mapeada seja encontrada.
