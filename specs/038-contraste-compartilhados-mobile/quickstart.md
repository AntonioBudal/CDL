# Quickstart & Validation Guide: F09.5.2 — Contraste Dinâmico, Estudos Compartilhados e Responsividade Mobile

**Branch**: `038-contraste-compartilhados-mobile` | **Date**: 2026-09-26

Este guia fornece os passos e comandos necessários para validar de ponta a ponta as três frentes implementadas nesta feature: o motor centralizado de contraste dinâmico, a reformulação visual de Estudos Compartilhados e a arquitetura de navegação móvel.

---

## 1. Pré-Requisitos e Ambiente

- **Node.js**: Versão 24+ ativa.
- **Python**: Versão 3.13 64-bit com ambiente virtual (`.venv`).
- **Repositório**: Branch `main` ou `038-contraste-compartilhados-mobile`.
- **Servidor Local**: Iniciado através do comando padrão:
  ```powershell
  python iniciar.py
  ```

---

## 2. Validação 1: Motor de Contraste Dinâmico WCAG 2.1

### Cenário de Teste Automatizado
Executar a suíte de testes unitários do motor de contraste:
```powershell
cd caderno-leitura-0.1\frontend
node --test tests/contrast_engine.test.mjs
```

### Resultados Esperados
- Todos os testes de cálculo de luminância relativa $L = 0.2126R + 0.7152G + 0.0722B$ passam com tolerância de $0.001$.
- Para fundos escuros (`#1e1e24`, `#222222`, `#18181b`), a cor calculada é clara (`#ffffff` ou `--color-text` claro) com contraste $\ge 4.5:1$.
- Para fundos claros (`#ffffff`, `#f5f5f5`, `#e8e8e8`), a cor calculada é escura com contraste $\ge 4.5:1$.
- Composição alfa de fundos semi-transparentes calcula a luminância exata combinada com o container pai.

### Validação Manual na Interface
1. Abrir a aplicação em `http://localhost:8000/ajustes?tab=aparencia`.
2. Alternar entre um tema claro (ex.: "Papel Fosco" ou "Solarized") e um tema escuro (ex.: "Noite Suave" ou "Grafite").
3. Inspecionar os campos `<select>` e botões secundários nos Ajustes: verificar que o texto nunca fica invisível nem depende de seletores estáticos com `!important`.
4. Inspecionar as abas de navegação em repouso e sob `:hover`: verificar que a cor do texto e dos ícones acompanha o novo fundo sem perda de legibilidade.

---

## 3. Validação 2: Tela de Estudos Compartilhados e Blindagem de SVGs

### Validação Manual na Interface
1. Acessar a biblioteca (`http://localhost:8000/books`) e clicar na aba **"Compartilhados Comigo"**.
2. **Inspeção de Ícones e SVGs**:
   - Inspecionar o ícone de lupa na barra de busca: constatar que mede exatamente **16px por 16px**, sem estourar dimensões.
   - Inspecionar o estado vazio quando não há estudos: verificar que a ilustração gráfica possui tamanho contido de no máximo **120px** e está perfeitamente centralizada.
3. **Filtros e Busca**:
   - Digitar um termo no campo de busca: verificar debounce de 300ms e requisição de busca.
   - Digitar um `@autor` no campo correspondente: verificar filtragem por autor.
   - Clicar no botão **"Limpar filtros"**: verificar que os campos são limpos e o botão possui alvo de toque ergonômico $\ge 44\text{px}$.
4. **Cards de Estudos**:
   - Inspecionar os cards renderizados: constatar que utilizam exclusivamente variáveis de tema do Leitorum (`--color-surface`, `--color-border`, `--color-text`), sem classes `zinc` ou `dark:` órfãs.

---

## 4. Validação 3: Arquitetura de Navegação Mobile e Abas

### Cenário de Teste em Smartphone (DevTools Device Mode)
1. Abrir as Ferramentas de Desenvolvedor (F12) e alternar para modo responsivo móvel (dimensões de 375x667px ou 390x844px).
2. **Barra de Navegação no Rodapé**:
   - Constatar que a barra inferior exibe exatamente **5 alvos de toque**: `Início`, `Importar`, `Amigos`, `Ajustes` e `Mais`.
   - Cada botão possui no mínimo 44x44px de área clicável e rótulo claro com ícone.
3. **Gaveta Inferior (*Bottom Sheet*) 'Mais'**:
   - Tocar no botão **"Mais"**: verificar que a gaveta desliza suavemente do rodapé com fundo escurecido.
   - Constatar que a gaveta lista as opções secundárias: `Lixeira`, `Administração` (se admin), `Conexão`, `Meu Perfil` e `Encerrar Sessão`.
   - Tocar fora da gaveta ou pressionar `Escape`: verificar fechamento imediato.
4. **Rolagem Horizontal de Abas com Gradiente Fade**:
   - Acessar `/ajustes`: constatar que as 5 abas segmentadas fluem horizontalmente sem quebrar linhas e exibem um gradiente de desvanecimento sutil nas laterais indicando conteúdo a rolar.
   - Deslizar com o dedo/mouse: constatar rolagem fluida e seleção tátil precisa.

---

## 5. Validação de Não-Regressão e Tipagem

Executar a verificação estrita de TypeScript e testes gerais:
```powershell
cd caderno-leitura-0.1\frontend
npm run build
npm test
```
**Resultado Esperado**: Zero erros de TypeScript (`vue-tsc -b` limpo), build do Vite bem-sucedido e todos os testes automatizados passando.
