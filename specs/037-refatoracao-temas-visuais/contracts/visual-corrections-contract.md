# Contrato Visual e Dimensional: Correções Visuais (F09.5)

## 1. Contrato de Escala e Alinhamento do Botão "Compartilhar"
- **Elemento**: `.share-action` dentro de `StudyView.vue`
- **Regras CSS Obrigatórias**:
  ```css
  .share-action {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    white-space: nowrap;
  }

  .share-action svg,
  .share-action .icon {
    width: 1.2em;
    height: 1.2em;
    min-width: 1.2em;
    min-height: 1.2em;
    flex-shrink: 0;
  }
  ```
- **Critério de Aceite**: A palavra "Compartilhar" nunca quebra em múltiplas linhas e o ícone mantém proporção de `1.2em`.

---

## 2. Contrato do Estado Vazio em "Estudos Compartilhados"
- **Elemento**: Contêiner visual ilustrativo em `SharedStudiesList.vue`
- **Regras CSS Obrigatórias**:
  ```css
  .shared-studies-empty-icon,
  .shared-empty-illustration svg {
    max-width: 120px;
    max-height: 120px;
    width: 100%;
    height: auto;
    margin: 0 auto;
    display: block;
  }
  ```
- **Critério de Aceite**: O SVG nunca ocupa mais de 120px de largura ou altura, independente da resolução do dispositivo.

---

## 3. Contrato Dimensional e Cromático do Modal "Exportar Estudo"
- **Elemento**: `ExportModal.vue`
- **Regras CSS Obrigatórias**:
  ```css
  .modal-dialog.panel {
    background-color: var(--color-surface, #ffffff);
    color: var(--color-text, #111827);
    border: 1px solid var(--color-border, #e5e7eb);
  }

  .format-name,
  .checkbox-label strong {
    color: var(--color-text, #111827);
  }

  .format-desc,
  .checkbox-desc {
    color: var(--color-muted, #6b7280);
  }

  .radio-card input[type="radio"],
  .checkbox-row input[type="checkbox"] {
    width: 20px;
    height: 20px;
    min-width: 20px;
    min-height: 20px;
    flex-shrink: 0;
  }
  ```
- **Critério de Aceite**: Textos sempre contrastantes com o fundo do modal e controles dimensionados sem deformação de layout.

---

## 4. Contrato de Contraste do Cabeçalho de Agrupamento
- **Elemento**: `.group-header .group-toggle-btn` em `GroupSection.vue`
- **Regras CSS Obrigatórias**:
  ```css
  .group-header {
    background-color: var(--color-surface, #ffffff);
    border-bottom: 1px solid var(--color-border, #e5e7eb);
  }

  .group-toggle-btn {
    color: var(--color-text, #111827);
  }

  .group-chevron-wrap {
    color: var(--color-muted, #6b7280);
  }

  /* Em fundos saturados ou superclasses com destaque */
  :root[data-sc-contrast="high"] .group-toggle-btn,
  .group-header.has-accent-bg .group-toggle-btn {
    color: #ffffff;
  }

  :root[data-sc-contrast="high"] .group-chevron-wrap,
  .group-header.has-accent-bg .group-chevron-wrap {
    color: #ffffff;
  }
  ```
- **Critério de Aceite**: O título do grupo e o chevron de colapso preservam legibilidade nítida (mínimo de 4.5:1) em qualquer tema ou agrupamento selecionado.
