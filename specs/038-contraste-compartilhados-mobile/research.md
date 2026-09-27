# Research & Technical Decisions: F09.5.2 — Contraste Dinâmico, Estudos Compartilhados e Responsividade Mobile

**Branch**: `038-contraste-compartilhados-mobile` | **Date**: 2026-09-26

---

## 1. Motor Centralizado de Contraste WCAG 2.1 e Injeção de Variáveis CSS

### Problema Diagnosticado
No código atual, diversos componentes e seletores em `style.css` e `.vue` contêm cores hard-coded para texto, ícones e estados de interação:
- Em `style.css` (linhas 42-83), existem regras estáticas como:
  ```css
  :root:is([data-theme='noite-suave'], [data-theme='grafite'], ...) select {
    color: #FFFFFF !important;
  }
  :root:not(...) select {
    color: #111827 !important;
  }
  ```
- Em `BooksView.vue`:
  ```css
  .library-tab-button:hover {
    color: var(--color-text-primary, #18181b);
    background: rgba(0, 0, 0, 0.03);
  }
  ```
  Isso gera texto quase preto (`#18181b`) sobre fundo escuro em temas como `Noite Suave`, `Grafite` e `Cyber`.
- Ícones usam cores arbitrárias em vez de herdar o contraste correto do elemento circundante.

### Decisão Técnica Escolhida
Implementar um módulo utilitário centralizado (`frontend/src/utils/contrast.ts`) e um composable Vue (`frontend/src/composables/useAccessibleContrast.ts`):
1. **Algoritmo Matemático Oficial WCAG 2.1**:
   - Linearização de canais sRGB:
     $$C_{\text{linear}} = \begin{cases} \frac{C_{\text{srgb}}}{12.92}, & \text{se } C_{\text{srgb}} \le 0.03928 \\ \left(\frac{C_{\text{srgb}} + 0.055}{1.055}\right)^{2.4}, & \text{caso contrário} \end{cases}$$
   - Cálculo da luminância relativa:
     $$L = 0.2126 \cdot R_{\text{linear}} + 0.7152 \cdot G_{\text{linear}} + 0.0722 \cdot B_{\text{linear}}$$
   - Razão de contraste entre duas cores:
     $$\text{ratio} = \frac{L_1 + 0.05}{L_2 + 0.05} \quad (\text{onde } L_1 > L_2)$$
   - Limiares normativos:
     - Texto regular (< 18pt / < 14pt bold): razão mínima de **4.5:1** (WCAG AA).
     - Texto grande e controles de interface (botões, abas, ícones): razão mínima de **3.0:1** (WCAG AA).
     - Modo de alto contraste (`prefers-contrast: more`): limiares de **7.0:1** e **4.5:1** (WCAG AAA).
2. **Suporte a Cores e Composição Alfa (Alpha Blending)**:
   - Suporte a Hexadecimal (`#RGB`, `#RRGGBB`, `#RRGGBBAA`), RGB/RGBA e nomes CSS.
   - Para cores com transparência ($A < 1$), a cor é sobreposta ao fundo pai conhecido ($C_{\text{efetivo}} = C \cdot A + C_{\text{fundo}} \cdot (1 - A)$).
3. **Injeção de Variáveis CSS via Composable (Decisão Q2: Opção A)**:
   - O composable `useAccessibleContrast()` recebe a cor de fundo (ou nome de variável CSS) e produz um conjunto reativo de variáveis locais:
     - `--dynamic-fg`: cor de primeiro plano de maior contraste para o estado normal.
     - `--dynamic-hover-bg`: fundo ajustado para hover.
     - `--dynamic-hover-fg`: texto de alto contraste para o estado hover.
     - `--dynamic-active-bg`: fundo para active/selected.
     - `--dynamic-active-fg`: texto para active/selected.
     - `--dynamic-border`: borda sutil contrastante.
   - Isso permite que estilos CSS nativos como `:hover`, `:focus` e `:active` utilizem essas variáveis com aceleração de hardware e sem disparar re-renderizações desnecessárias no ciclo do Vue.
4. **Erradicação das Exceções Hard-coded**:
   - Remoção de todos os seletores com `#FFFFFF !important` e `#111827 !important` em `style.css`.
   - Elementos de formulário e botões secundários passam a consumir `--color-surface` e `--dynamic-fg`.

---

## 2. Diagnóstico Estrutural de `SharedStudiesList.vue` e Resolução de SVGs

### Causa Raiz Diagnosticada
1. O repositório **não possui Tailwind CSS instalado**:
   - `frontend/package.json` possui apenas `vue`, `vue-router`, `lucide-vue-next` e `markdown-it`.
   - Não há `@tailwindcss/vite`, `tailwindcss` ou `postcss`.
2. O arquivo `SharedStudiesList.vue` foi escrito empregando dezenas de classes do Tailwind:
   ```html
   <svg class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-400" ...>
   ```
   e classes como `dark:bg-zinc-900`, `border-zinc-200`, `text-zinc-100`, etc.
3. Como as classes `w-4` (width: 1rem) e `h-4` (height: 1rem) não existem em nenhum CSS, o elemento `<svg viewBox="0 0 24 24">` é renderizado sem restrição dimensional. Por especificação da W3C para SVGs com viewBox em containers flexíveis/absolutos, o navegador expande a imagem para preencher a largura total do elemento ancestral, fazendo o ícone de lupa atingir dimensões gigantescas.

### Decisão Técnica Escolhida
1. **Erradicação de Classes Tailwind Fantasmas**:
   - Eliminar 100% das menções a classes inexistentes (`w-4`, `h-4`, `text-zinc-400`, `dark:bg-zinc-900`, etc.).
2. **Adoção do Componente Canônico `<Icon />`**:
   - Substituir todos os SVGs manuais pelo componente oficial `<Icon :name="..." :size="..." />`, que embute ícones do pacote `lucide-vue-next` com dimensões fixas garantidas diretamente no elemento SVG e `currentColor`.
3. **Reformulação Visual Completa da Tela de Estudos Compartilhados**:
   - **Barra de Busca e Filtros**: Campos de busca por texto e `@autor` estilizados com tokens nativos (`--color-surface`, `--color-border`, `--color-text`), com ícone de busca embutido com dimensão garantida (16px) e botão "Limpar filtros" ergonômico (mínimo de 44px de altura).
   - **Cards de Estudo**: Substituição do leiaute desordenado por cards com bordas semânticas (`--color-border`), hover suave (`--color-card-hover`), badge de visibilidade padronizado e tipografia hierárquica clara.
   - **Estado de Carregamento**: Esqueleto de loading (*skeleton*) com 4 cards pulsantes usando os tokens existentes `--skeleton-base` e `--skeleton-shimmer`.
   - **Estado de Erro**: Alerta com ícone de aviso de 18px e botão "Tentar novamente".
   - **Estado Vazio (Empty State)**: Ilustração central contida (máximo de 120px) com título acolhedor e mensagem contextualizada (busca sem resultados vs. acervo vazio).

---

## 3. Arquitetura de Navegação Mobile (Barra Prioritária + Gaveta 'Mais')

### Diagnóstico da Navegação Mobile Atual
- O arquivo `mobile-navigation.css` (linha 79) fixava:
  ```css
  grid-template-columns: repeat(3, minmax(0, 1fr));
  ```
- O componente `App.vue` possui até 6 destinos principais visíveis:
  1. `Livros` ou `Dashboard` (conforme preferência)
  2. `Importar`
  3. `Amigos`
  4. `Administração` (para admins)
  5. `Ajustes`
  6. `Lixeira`
- Em um grid rígido de 3 colunas com altura fixa calculada, 5 ou 6 itens quebram a barra em duas linhas, esmagando os ícones e sobrepondo a margem de leitura do rodapé.

### Decisão Técnica Escolhida (Decisão Q1: Opção A)
1. **Estrutura da Barra Inferior (5 Itens Fixos)**:
   - Dividir a barra inferior em exatamente 5 alvos de navegação proporcionais (`repeat(5, 1fr)`):
     1. **Início**: Rota `/` (Livros ou Dashboard).
     2. **Importar**: Rota `/importar`.
     3. **Amigos**: Rota `/amigos` (com indicador numérico de solicitações pendentes).
     4. **Ajustes**: Rota `/ajustes`.
     5. **Mais**: Ação de abertura da gaveta inferior (*Bottom Sheet*).
2. **Gaveta Inferior (*Bottom Sheet / Drawer*)**:
   - Componente `MobileMoreMenu.vue`:
     - Disparado pelo botão "Mais".
     - Desliza suavemente a partir do fundo com animação tátil e *backdrop* escurecido.
     - Contém as rotas secundárias e de gestão:
       - `Lixeira` (com ícone e rota `/lixeira`).
       - `Administração` (se o usuário for admin, rota `/admin`).
       - `Conexão` (rota `/conexao`).
       - `Meu Perfil` (rota do usuário `@username`).
       - Botão de `Sair da Aplicação` (logout com confirmação).
     - Suporte a fechamento ao tocar no backdrop, ao pressionar `Escape` ou ao clicar em qualquer link interno.
3. **Ergonomia e Acessibilidade**:
   - Cada botão na barra inferior tem alvos de toque de no mínimo 44x44px.
   - Suporte completo às margens de segurança do dispositivo (`env(safe-area-inset-bottom)`).

---

## 4. Navegação por Abas Segmentadas com Rolagem Contida e Máscara Fade

### Diagnóstico de Abas em Telas Pequenas
- O sistema possui telas com muitas abas segmentadas:
  - `SettingsView`: 5 abas (`Perfil & Privacidade`, `Aparência`, `Leitura`, `Sistema`, `Conta & Dispositivos`).
  - `FriendsView`: 4 abas (`Meus Amigos`, `Solicitações Recebidas`, `Enviadas`, `Buscar Leitores`).
  - `StudyTabs`: até 6 seções de estudo.
- Em telas menores que 480px, essas abas sem tratamento de transbordamento estouram a largura da tela ou espremem seus textos.

### Decisão Técnica Escolhida (Decisão Q3: Opção A)
1. **Rolagem Horizontal Suave com Momentum**:
   - Todas as barras de abas (`.settings-tabs`, `.tabs-nav`, `.study-tabs`, `.library-tabs-nav`) utilizam:
     ```css
     display: flex;
     overflow-x: auto;
     scrollbar-width: none;
     -webkit-overflow-scrolling: touch;
     white-space: nowrap;
     ```
2. **Máscara Gradiente Suave de Desvanecimento (*Fade Mask*)**:
   - Quando o container de abas possui rolagem horizontal ativa, uma máscara gradiente nas bordas (`mask-image: linear-gradient(to right, transparent, black 16px, black calc(100% - 16px), transparent)`) indica visualmente que o conteúdo se estende além da borda visível.
3. **Preservação de Semântica WAI-ARIA**:
   - Foco via teclado (setas esquerda/direita), `role="tablist"`, `role="tab"`, `aria-selected` e `tabindex` dinâmico preservados em todos os componentes.
