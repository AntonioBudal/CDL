# Contracts: Ajustes — Ateliê de Preferências e Leitura Viva

**Feature**: `072-ajustes-atelie-preferencias`
**Date**: 2026-10-11
**Status**: Concluído

## 1. Contrato de Componente: `ThemePreviewGrid.vue`

### 1.1 Props & Emits

```typescript
export interface ThemePreviewGridProps {
  modelValue: CanonicalThemeId
  disabled?: boolean
}

export interface ThemePreviewGridEmits {
  (e: 'update:modelValue', value: CanonicalThemeId): void
  (e: 'change', value: CanonicalThemeId): void
}
```

### 1.2 Estrutura de Markup e Acessibilidade (WAI-ARIA)

```html
<div
  class="theme-preview-grid"
  role="radiogroup"
  aria-label="Seleção de temas visuais do Caderno de Leitura"
>
  <button
    v-for="theme in themes"
    :key="theme.id"
    type="button"
    role="radio"
    :aria-checked="modelValue === theme.id"
    :tabindex="modelValue === theme.id ? 0 : -1"
    class="theme-preview-card"
    :class="{ 'is-active': modelValue === theme.id }"
    @click="selectTheme(theme.id)"
    @keydown="onKeyDown($event, theme.id)"
  >
    <!-- Box visual estilo Windows 11 com as cores da paleta -->
    <div
      class="theme-color-box"
      :style="{
        backgroundColor: theme.colors.page,
        borderColor: theme.colors.border
      }"
    >
      <div
        class="theme-window-mockup"
        :style="{
          backgroundColor: theme.colors.surface,
          borderColor: theme.colors.border
        }"
      >
        <div
          class="mockup-header"
          :style="{ backgroundColor: theme.colors.page }"
        >
          <span
            class="mockup-accent-pill"
            :style="{ backgroundColor: theme.colors.accent }"
          ></span>
        </div>
        <div class="mockup-body">
          <span
            class="mockup-line"
            :style="{ backgroundColor: theme.colors.text }"
          ></span>
          <span
            class="mockup-line short"
            :style="{ backgroundColor: theme.colors.text }"
          ></span>
        </div>
      </div>
    </div>

    <!-- Rótulo do tema e indicador de ativo -->
    <div class="theme-card-footer">
      <span class="theme-name">{{ theme.label }}</span>
      <span
        v-if="modelValue === theme.id"
        class="theme-active-indicator"
        aria-hidden="true"
      >
        <!-- Ícone SVG de marcação -->
      </span>
    </div>
  </button>
</div>
```

---

## 2. Contrato de Componente: `SettingsView.vue` (Navegação Vertical & Layout)

### 2.1 Contrato de URL e Roteamento

- **Rota**: `/ajustes`
- **Query Params**:
  - `tab`: `'perfil' | 'aparencia' | 'leitura' | 'sistema' | 'conta'` (Padrão: `'perfil'`)
- **Comportamento**:
  - Na montagem do componente, lê `route.query.tab`. Se for um valor válido, ativa a seção correspondente.
  - Ao alternar a seção, atualiza a URL sem recarregar (`router.replace({ query: { ...route.query, tab: newTab } })`).

### 2.2 Layout em Desktop ($\ge 1024\text{px}$)

```
+------------------------------------------------------------------------------------------------+
| Header Global                                                                                  |
+------------------------------------------------------------------------------------------------+
| .settings-layout                                                                               |
| +--------------------+ +-------------------------------------+ +------------------------------+ |
| | .settings-nav      | | .settings-main                      | | .settings-preview-col        | |
| | (Menu Lateral)     | | (Formulário da Seção Ativa)         | | (Bancada de Leitura Viva)    | |
| |                    | |                                     | |                              | |
| | - Perfil           | | [Aparência]                         | | [Amostra ao Vivo]            | |
| | - Aparência (ativo)| | - Galeria de Temas (Windows 11)     | | - Prévia de Estudo           | |
| | - Leitura          | |   [Card 1] [Card 2] [Card 3]        | | - Tipografia ativa           | |
| | - Sistema          | | - Superclasse Física                | | - Tamanho percentual         | |
| | - Conta            | | - Densidade e Contraste             | | - Entrelinha e alinhamento   | |
| +--------------------+ +-------------------------------------+ +------------------------------+ |
+------------------------------------------------------------------------------------------------+
```

### 2.3 Layout em Telas Móveis ($< 1024\text{px}$)

- Menu horizontal de navegação deslizável suavemente no topo.
- Formulário ativo ocupando a largura total com alvos táteis $\ge 44 \times 44\text{px}$.
- Botão de ação flutuante / ancorado: *"Ver Demonstração de Leitura"*.
- Ao tocar, expande um *bottom sheet* com o simulador de leitura completo (`AppearancePreview.vue`), com botão de recolher sem perda de contexto.

---

## 3. Contrato de Componente: `AppearancePreview.vue` (Bancada de Leitura Viva)

### 3.1 Props

```typescript
export interface AppearancePreviewProps {
  preferences: AppearancePreferences
  isMobileDrawer?: boolean
}
```

### 3.2 Escopo e Isolamento Estilístico

- Todo estilo aplicado no simulador (tamanho percentual, fonte, entrelinha) é delimitado pela classe `.appearance-preview` ou pelo `div.preview-container`.
- As variáveis CSS calculadas:
  - `--preview-font-size: ${preferences['reader-size'] || 100}%`
  - `--preview-font-family: ${resolvedFontFamily}`
  - `--preview-line-height: ${preferences.density === 'comfortable' ? '1.8' : preferences.density === 'compact' ? '1.4' : '1.6'}`
  - `--preview-text-align: ${preferences.align || 'left'}`
- Sem efeito colateral nos controles da página de ajustes.
