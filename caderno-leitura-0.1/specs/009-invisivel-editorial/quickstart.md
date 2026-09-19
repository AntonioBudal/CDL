# Quickstart & Validation: 009 — Invisível: Superclasse Silenciosa & Editorial e Limpeza de Ajustes

**Date**: 2026-09-19  
**Feature**: 009 — Invisível: Superclasse Silenciosa & Editorial e Limpeza de Ajustes  
**Status**: Ready  

---

## 1. Pré-requisitos & Configuração

1. Navegar até o diretório do frontend:
   ```powershell
   cd c:\Users\User\caderno\caderno-leitura-0.1\frontend
   ```

2. Arquivos alterados/criados nesta feature:
   - `src/styles/superclasses/invisivel.css` (novo)
   - `src/style.css` (import de `invisivel.css`)
   - `src/appearance-bootstrap.js` (remoção de `style`, `surface`, `button-style` e normalização defensiva)
   - `src/appearance.d.ts` (atualização dos tipos tipados de preferências)
   - `src/components/AppearanceControls.vue` (limpeza de campos ignorados/órfãos)
   - `tests/superclasses.test.mjs` (testes automatizados para tokens da Invisível e catálogo limpo)

---

## 2. Cenários de Validação Automatizada

Execute a suíte de testes unitários do frontend:

```powershell
npm test
```

### Validações Esperadas nos Testes Automatizados:
1. **Ativação da Superclasse**: O seletor `:is(:root[data-superclass="invisivel"], .superclass-invisivel)` declara:
   - `--sc-border-radius: 0px`
   - `--sc-shadow-idle: none`
   - `--sc-shadow-hover: none`
   - `--sc-reading-shift-x: calc(4px * var(--sc-intensity))`
   - `--sc-transition-duration: 200ms`
   - `--sc-transition-easing: cubic-bezier(0.2, 0, 0, 1)`
2. **Desmaterialização de Caixas**: Cartões possuem fundo transparente e bordas eliminadas.
3. **Deslocamento Lateral**: Itens no hover aplicam `translateX(var(--sc-reading-shift-x))`.
4. **Sublinhado Progressivo**: Títulos e links ativam linha de sublinhado animada com `scaleX(1)`.
5. **Catálogo Podado**: Os campos `style`, `surface` e `button-style` não constam mais em `cadernoAppearance.fields`.
6. **Migração Segura**: Normalização tolera dados antigos sem quebrar preferências ativas.
7. **Imobilidade do Leitor**: `.markdown-content` mantém `transform: none !important; animation: none !important;`.

---

## 3. Validação do Build de Produção

```powershell
npm run build
```
- **Critério**: O build do Vite e a verificação do `vue-tsc` devem completar com zero erros de tipo e sem referências aos campos obsoletos removidos.

---

## 4. Cenários de Validação Manual (Inspeção Visual)

Inicie o servidor de desenvolvimento:
```powershell
npm run dev
```

Abra o navegador em `http://localhost:5173/` e execute o checklist visual:

| Cenário | Passos | Comportamento Esperado |
|---|---|---|
| **1. Tela de Ajustes Limpa** | Acessar **Ajustes**. | Os campos "Formato das caixas", "Contraste da interface (Cartões)" e "Preenchimento de Botões" não estão mais presentes; a tela exibe apenas os controles fundamentais e o bloco de Superclasses. |
| **2. Ativação da Invisível** | Selecionar **Invisível — Silenciosa & Funcional**. | As caixas e sombras pesadas desaparecem instantaneamente; a interface respira com estética tipográfica limpa. |
| **3. Deslocamento Lateral no Acervo** | Passar o mouse sobre os livros na estante. | O livro desloca-se sutilmente 4px para a direita acompanhado pelo traçado de uma linha fina sob o título. |
| **4. Cascata Temporal de Rota** | Clicar em um livro para abrir seus detalhes. | O título surge suavemente, seguido pelos metadados e pelo sumário em cascata temporal agradável de 120ms. |
| **5. Estabilidade da Leitura** | Abrir um capítulo para leitura. | O texto corrido permanece 100% imóvel, preservando a imersão absoluta. |
