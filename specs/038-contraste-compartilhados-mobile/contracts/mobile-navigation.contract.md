# Contract: Arquitetura de Navegação Mobile e Rolagem de Abas

**Packages**: `frontend/src/mobile-navigation.css`, `frontend/src/App.vue`, `frontend/src/components/navigation/MobileMoreMenu.vue`

---

## 1. Contrato da Barra Inferior Mobile (`.app-header .main-nav`)

Sob `@media (max-width: 767px)`:

```css
.app-header .main-nav {
  position: fixed;
  inset: auto 0 0;
  z-index: 20;

  /* Exatamente 5 colunas proporcionais */
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  align-items: stretch;
  gap: calc(var(--space-unit) * .15);

  width: 100%;
  height: var(--mobile-nav-offset);
  margin: 0;

  padding-top: calc(var(--space-unit) * .25);
  padding-bottom: calc(var(--space-unit) * .25 + env(safe-area-inset-bottom, 0px));
  padding-left: max(calc(var(--space-unit) * .25), env(safe-area-inset-left, 0px));
  padding-right: max(calc(var(--space-unit) * .25), env(safe-area-inset-right, 0px));

  border-top: var(--border-width) solid var(--color-border-strong);
  background: var(--color-surface);
  box-shadow: var(--shadow-panel);
}

.app-header .main-nav a,
.app-header .main-nav button {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  min-width: 44px;
  padding: calc(var(--space-unit) * .2);
  background: transparent;
  border: none;
  color: var(--color-muted);
  font-size: 0.75rem;
  line-height: 1.2;
  text-decoration: none;
  cursor: pointer;
}

.app-header .main-nav a.selected,
.app-header .main-nav button.active {
  color: var(--color-accent);
  font-weight: 700;
}
```

---

## 2. Contrato da Gaveta Inferior (*Bottom Sheet*) `MobileMoreMenu.vue`

### Comportamento e Interação:
- **Disparador**: Botão "Mais" na barra inferior móvel.
- **Abertura**: Desliza verticalmente de baixo para cima (`transform: translateY(0)`), acompanhado de opacidade no backdrop (`rgba(0, 0, 0, 0.4)`).
- **Conteúdo da Gaveta**:
  - Cabeçalho com título "Mais Opções" e botão de fechar (ou toque fora).
  - Grade ou lista vertical de itens secundários:
    - **Lixeira**: `/lixeira` com ícone `trash`
    - **Administração**: `/admin` com ícone `shield` (se usuário for admin)
    - **Conexão**: `/conexao` com ícone `sliders`
    - **Meu Perfil**: `/@username` com ícone `user`
    - **Encerrar Sessão**: Ação de logout com estilo de perigo / confirmação
- **Acessibilidade**:
  - `role="dialog"`, `aria-modal="true"`, `aria-label="Menu de opções adicionais"`.
  - Fechamento imediato com tecla `Escape` e ao clicar em qualquer link interno.

---

## 3. Contrato da Máscara Gradiente para Abas (*Tabs Fade Mask*)

Para containers de abas que possuam rolagem horizontal (`.settings-tabs`, `.tabs-nav`, `.study-tabs`, `.library-tabs-nav`):

```css
.tabs-scroll-wrapper {
  position: relative;
  width: 100%;
  overflow: hidden;
}

.tabs-scroll-wrapper::before,
.tabs-scroll-wrapper::after {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  width: 1.25rem;
  pointer-events: none;
  z-index: 2;
  transition: opacity 0.2s ease;
}

.tabs-scroll-wrapper::before {
  left: 0;
  background: linear-gradient(to right, var(--color-surface), transparent);
}

.tabs-scroll-wrapper::after {
  right: 0;
  background: linear-gradient(to left, var(--color-surface), transparent);
}

.tabs-scroll-content {
  display: flex;
  overflow-x: auto;
  scrollbar-width: none; /* Firefox */
  -webkit-overflow-scrolling: touch;
  white-space: nowrap;
  gap: calc(var(--space-unit) * 0.5);
}

.tabs-scroll-content::-webkit-scrollbar {
  display: none; /* Chrome/Safari */
}
```
