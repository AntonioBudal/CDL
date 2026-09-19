# Quickstart & Validation: 011 — Monolítica: Superclasse Pesada & Solene

**Feature**: 011 — Monolítica: Superclasse Pesada & Solene (Brutalista & Arquitetura em Pedra)  
**Date**: 2026-09-19  
**Status**: Ready  

---

## 1. Pré-requisitos & Configuração

1. Navegar até o diretório do frontend:
   ```powershell
   cd c:\Users\User\caderno\caderno-leitura-0.1\frontend
   ```

2. Arquivos alterados/criados nesta feature:
   - `src/styles/superclasses/monolitica.css` (novo)
   - `src/style.css` (import de `monolitica.css`)
   - `tests/superclasses.test.mjs` (testes automatizados para tokens, cantos retos, ausência de sombras e transições solenes)

---

## 2. Validação Automatizada

Execute a suíte de testes unitários do frontend:

```powershell
npm test
```

### Critérios de Aceite Automatizados:
1. **Declaração de Tokens da Monolítica**:
   - `--sc-border-radius: 0px !important`
   - `--sc-border-width: calc(var(--border-width, 1px) + 1px)`
   - `--sc-shadow-idle: none !important`
   - `--sc-shadow-hover: none !important`
   - `--sc-shadow-active: none !important`
   - `--sc-transition-duration: 380ms`
   - `--sc-transition-easing: cubic-bezier(0.25, 1, 0.5, 1)`
2. **Geometria de Blocos e Ausência de Sombras nos Cartões**:
   - `border-radius: 0px` e `box-shadow: none` em `.book-card`
   - `transform: none !important;` (sem elevação flutuante nem inclinação 3D)
3. **Botões Monolíticos**:
   - Cantos retos, sem sombras plásticas, com inversão de alto contraste no `:active`
4. **Transição de Rota Solene**:
   - `.page-enter-active` com `opacity 380ms` e `.page-leave-active` com `opacity 220ms`
   - `transform: none !important` (sem saltos de viewport)
5. **Acessibilidade e Blindagem**:
   - `.markdown-content` com `transform: none !important; animation: none !important;`
   - `prefers-reduced-motion: reduce` e `data-motion="off"` forçando `transition: none !important;` e `--sc-intensity: 0.0 !important;`

---

## 3. Validação do Build de Produção

```powershell
npm run build
```
- **Critério**: O build do Vite e a checagem de tipos do TypeScript (`vue-tsc`) devem concluir com zero erros.

---

## 4. Roteiro de Inspeção Visual (Manual)

Inicie o servidor de desenvolvimento:
```powershell
npm run dev
```

Abra o navegador em `http://localhost:5173/`:

| Cenário | Ação | Comportamento Esperado |
|---|---|---|
| **1. Ativação da Monolítica** | Em **Ajustes**, selecionar **Monolítica — Pesada & Solene**. | Interface atualiza em tempo real; todos os cantos tornam-se retos (`0px`) e todas as sombras desaparecem. |
| **2. Cartões do Acervo** | Mover o cursor sobre os cartões de livros. | O cartão permanece imóvel no espaço, transitando de forma ponderada e sutil de cor de fundo/borda em ~380ms. |
| **3. Clique em Botões** | Pressionar e manter um botão de ação. | O botão responde com inversão de alto contraste firme, transmitindo peso de bloco de pedra sem encolher ou afundar. |
| **4. Navegação entre Telas** | Navegar entre a estante de livros e um livro ou estudo. | A troca de tela dissolve suavemente em opacidade ponderada sem saltos ou oscilações de scroll. |
| **5. Estabilidade de Leitura** | Abrir um capítulo para estudo. | O texto do leitor permanece 100% estático e imóvel. |
