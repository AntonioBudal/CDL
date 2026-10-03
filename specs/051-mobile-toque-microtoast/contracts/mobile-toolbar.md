# Contract: Barra Flutuante Mobile com Ícones Puros

**Componente**: `frontend/src/components/FloatingActionsToolbar.vue`  
**Objetivo**: Padronizar os botões mobile com ícones puros de 44x44px, ocultação de rótulos textuais e emissão de eventos informativos.

---

## 1. Contrato Visual dos Botões de Ferramenta no Mobile

- No modo mobile (`.is-mobile`), o container dos botões (`.toolbar-btn`) adota:
  ```css
  .is-mobile .toolbar-btn {
    min-height: 44px;
    min-width: 44px;
    padding: 0.5rem;
    flex-direction: row;
    justify-content: center;
    align-items: center;
  }
  .is-mobile .toolbar-btn .btn-text {
    display: none;
  }
  .is-mobile .toolbar-btn .icon-svg {
    width: 22px;
    height: 22px;
  }
  ```
- Cada botão possui atributo `aria-label` completo para leitor de tela (ex.: `aria-label="Destacar com marca-texto"`).

---

## 2. Eventos e Notificações de Ferramenta

A barra flutuante emite um evento informativo adicional `tool-selected` ou dispara callback contendo os metadados da ferramenta acionada:

| Ação | Evento Disparado | Mensagem do Toast |
|---|---|---|
| Destacar | `@highlight` | `"Destaque aplicado"` |
| Mudar Cor | Modo color picker selecionado | `"Cor alterada"` |
| Anotar | `@annotate` ou abertura do prompt | `"Adicionar anotação"` / `"Anotação salva"` |
| Citação | `@copy-quote` | `"Citação copiada"` |
| Ocluir | `@occlude` | `"Trecho ocultado para revisão"` |
| Pergunta | `@ask-question` ou abertura do prompt | `"Criar pergunta"` / `"Pergunta cadastrada"` |
