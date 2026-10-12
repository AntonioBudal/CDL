# Guia de Validação Rápida (Quickstart): Página Inicial sem Login (SEO) — Manifesto do Leitor Reflexivo

**Feature**: `074-manifesto-leitor-reflexivo`  
**Data**: 2026-10-11  
**Status**: Concluído (Phase 1)  

---

## 1. Pré-Requisitos

- Ambiente Windows local com Node.js e PowerShell.
- Dependências do frontend instaladas em `caderno-leitura-0.1/frontend`.
- Dependências do backend instaladas no ambiente Python 3.13.

---

## 2. Cenários de Validação Automatizada

### Cenário 1: Testes Unitários de Frontend da Landing Page
Valida o comportamento dos componentes da landing page, a sincronização do simulador em 4 dimensões, o composable `useVisitorTheme`, o Schema.org e a acessibilidade ARIA.

```powershell
cd c:\Users\User\caderno\caderno-leitura-0.1\frontend
npm test -- src/views/__tests__/LandingView.spec.ts src/composables/__tests__/useVisitorTheme.spec.ts
```
**Resultado Esperado**: Todos os testes passam (GREEN), validando a alternância de abas, sincronização de realces e restauração de tema em memória.

### Cenário 2: Verificação de Build e Code-Splitting do Vite
Valida que as rotas autenticadas pesadas foram desacopladas via dynamic import e que o bundle da página inicial permanece enxuto.

```powershell
cd c:\Users\User\caderno\caderno-leitura-0.1\frontend
npm run build
```
**Resultado Esperado**: O build compila sem erros de TypeScript e sem warnings de tamanho excessivo de chunk na rota inicial.

### Cenário 3: Validação da Suíte Backend (Integridade dos Serviços e SEO)
Valida que os endpoints de `robots.txt`, `sitemap.xml` e rotas do backend continuam íntegros e isolados.

```powershell
cd c:\Users\User\caderno\caderno-leitura-0.1\backend
pytest tests/test_seo.py
```
**Resultado Esperado**: Todos os testes passam (GREEN).

---

## 3. Cenários de Validação Manual e Interativa

### Cenário 4: Interação com o Simulador em 4 Dimensões
1. Iniciar a aplicação via `python iniciar.py` ou `npm run dev`.
2. Acessar `http://localhost:5173/` em um navegador sem usuário logado.
3. Rolar até a seção `#metodo` (Bancada do Simulador).
4. Clicar sucessivamente nas abas: "Resumo analítico", "Explicação aprofundada", "Conceitos-chave" e "Referências e conexões".
5. **Verificação**: O texto transita suavemente sem saltos de página (CLS = 0) e as marcações correspondentes no trecho de Machado de Assis à esquerda recebem destaque visual duplo.
6. Testar navegação por teclado: focar nas abas e pressionar as setas direcionais (esquerda/direita). A aba ativa deve mudar e receber foco.

### Cenário 5: Ateliê Vitrine dos 10 Temas
1. Na mesma página, rolar até a seção `#temas`.
2. Clicar sobre o tema `pergaminho` e depois sobre `solario`.
3. **Verificação**: A página inteira é repintada imediatamente na nova paleta. O leitor de tela anuncia: *"Tema aplicado: [Nome]. A página inteira foi repintada."*
4. Clicar em "Já possuo conta (Entrar)" para navegar até `/login`.
5. **Verificação**: O tema temporário do visitante é limpo e a tela de login exibe a preferência padrão do sistema.

### Cenário 6: Validação de SEO e Schema.org no DOM
1. Inspecionar o código-fonte da página ou abrir as ferramentas de desenvolvedor.
2. Inspecionar `<script id="schema-json-ld">`.
3. **Verificação**: Contém JSON-LD válido com `@type: ['SoftwareApplication', 'WebApplication']`, `applicationCategory: "EducationalApplication"`, `offers: { price: "0" }`.
4. Inspecionar `<head>`: tags `og:title`, `og:description`, `twitter:card`, `link[rel="canonical"]` preenchidas com dados do manifesto.
