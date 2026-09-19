# Quickstart & Validation: 008 — Mecânica: Superclasse Tátil & Responsiva

**Date**: 2026-09-19  
**Feature**: 008 — Mecânica: Superclasse Tátil & Responsiva  
**Status**: Ready  

---

## 1. Pré-requisitos & Configuração

1. Certifique-se de que o ambiente frontend em `caderno-leitura-0.1/frontend/` está pronto:
   ```powershell
   cd c:\Users\User\caderno\caderno-leitura-0.1\frontend
   ```
2. Arquivos CSS e composables criados ou atualizados:
   - `src/styles/superclasses/mecanica.css`
   - `src/style.css` (import da Mecânica)
   - `index.html` (meta ou preload se aplicável)
   - `tests/superclasses.test.mjs` (testes automatizados estendidos)

---

## 2. Cenários de Validação Automatizada

Execute a suíte de testes unitários do frontend:

```powershell
npm test
```

### Validações Esperadas nos Testes Automatizados:
1. **Ativação da Superclasse**: O seletor `:is(:root[data-superclass="mecanica"], .superclass-mecanica)` declara corretamente:
   - `--sc-border-radius: 2px`
   - `--sc-shadow-idle: 0 calc(3px * var(--sc-intensity)) 0 var(--color-shadow, rgba(0, 0, 0, 0.35))`
   - `--sc-shadow-hover: 0 calc(4px * var(--sc-intensity)) 0 var(--color-shadow, rgba(0, 0, 0, 0.45))`
   - `--sc-shadow-active: 0 0 0 transparent`
   - `--sc-transition-duration: 100ms`
   - `--sc-transition-easing: linear`
2. **Push-Down**: No estado `:active`, o elemento aplica `translateY(calc(3px * var(--sc-intensity)))`.
3. **Inputs Cavados**: Inputs possuem `box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.12)`. No `:focus`, mantêm `transform: none` e espessam a borda.
4. **Switches Rápidos**: Switches operam com transição de `60ms linear`.
5. **Zero Breathing**: Não existem regras `@keyframes` de pulso ou flutuação associadas à classe `superclass-mecanica`.
6. **Imobilidade do Leitor**: `.markdown-content` possui `transform: none !important;` e `animation: none !important;`.
7. **Respeito a Reduced Motion**: `--sc-intensity` é `0.0 !important` e transformações são anuladas.

---

## 3. Validação do Build de Produção

```powershell
npm run build
```
- **Critério**: O build do Vite e a verificação do `vue-tsc` devem completar com zero erros de tipo e assets otimizados.

---

## 4. Cenários de Validação Manual (Inspeção Visual)

Inicie o servidor de desenvolvimento:
```powershell
npm run dev
```

Abra o navegador em `http://localhost:5173/` e execute o checklist visual:

| Cenário | Passos | Comportamento Esperado |
|---|---|---|
| **1. Ativação nos Ajustes** | Navegar até **Ajustes** $\to$ **Superclasses** $\to$ Selecionar **Mecânica**. | Os cartões e painéis adotam cantos secos (2px) e sombras duras sem blur imediatamente. |
| **2. Push-Down em Botões** | Pressionar e segurar um botão qualquer (ex.: "Novo Livro"). | O botão afunda fisicamente 3px e a sombra zera instantaneamente no batente mecânico. |
| **3. Formulários e Inputs** | Clicar em um campo de texto em qualquer formulário. | O campo parece uma fenda escavada na chapa metálica; o foco não faz o campo flutuar, apenas reforça a borda. |
| **4. Sliders de Ajuste** | Alternar o multiplicador de intensidade para "Sutil" (0.5), "Padrão" (1.0) e "Alta" (1.5). | A profundidade da sombra e o curso do clique afundam proporcionalmente à intensidade selecionada. |
| **5. Transição de Rota** | Clicar para alternar entre "Biblioteca", "Anotações" e "Ajustes". | Transição limpa e seca de 100ms sem deslizes laterais ou atrasos perceptíveis. |
| **6. Área de Leitura** | Abrir qualquer livro/capítulo e passar o mouse sobre o texto. | O texto corrido permanece 100% estático e imóvel. |
