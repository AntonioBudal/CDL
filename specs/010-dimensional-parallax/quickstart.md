# Quickstart & Validation: 010 — Dimensional: Superclasse Cinemática & Profunda

**Feature**: 010 — Dimensional: Superclasse Cinemática & Profunda (3D Parallax Espacial)  
**Date**: 2026-09-19  
**Status**: Ready  

---

## 1. Pré-requisitos & Configuração

1. Navegar até o diretório do frontend:
   ```powershell
   cd c:\Users\User\caderno\caderno-leitura-0.1\frontend
   ```

2. Arquivos alterados/criados nesta feature:
   - `src/styles/superclasses/dimensional.css` (novo)
   - `src/style.css` (import de `dimensional.css`)
   - `tests/superclasses.test.mjs` (testes automatizados para tokens 3D, tilt e paralaxe)

---

## 2. Validação Automatizada

Execute a suíte de testes unitários do frontend:

```powershell
npm test
```

### Critérios de Aceite Automatizados:
1. **Declaração de Tokens da Dimensional**:
   - `--sc-perspective: 1000px`
   - `--sc-tilt-max-x: calc(1.5deg * var(--sc-intensity))`
   - `--sc-tilt-max-y: calc(2.0deg * var(--sc-intensity))`
   - `--sc-transition-duration: 320ms`
   - `--sc-transition-easing: cubic-bezier(0.16, 1, 0.3, 1)`
2. **Tilt 3D nos Cartões**:
   - `transform: perspective(...) rotateX(...) rotateY(...)`
   - Sombras direcionais projetadas opostas ao cursor
3. **Paralaxe Multicamada**:
   - Capa (1px), título (2px) e marcadores (3px) escalonados com `translate3d`
4. **Transição de Rota Cinemática**:
   - `.page-enter-active` e `.page-leave-active` com interpolação de escala `scale()` e `translateY`
5. **Acessibilidade e Blindagem**:
   - `.markdown-content` com `transform: none !important; animation: none !important;`
   - `prefers-reduced-motion: reduce` e `data-motion="off"` forçando `--sc-intensity: 0.0 !important;`

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
| **1. Ativação da Dimensional** | Em **Ajustes**, selecionar **Dimensional — Cinemática & Profunda**. | Interface atualiza em tempo real; painéis e cartões recebem sombras volumétricas suaves. |
| **2. Tilt 3D no Acervo** | Mover o cursor sobre as extremidades de um cartão de livro. | O cartão inclina-se sutilmente (máximo de 1.5° em X e 2.0° em Y) em direção ao mouse com sombra direcional fluida. |
| **3. Parallax Interno** | Observar a miniatura da capa e o título do livro durante o tilt. | A capa e o título movem-se com leve defasagem tátil, criando efeito de profundidade artesanal. |
| **4. Retorno Inercial** | Tirar o cursor bruscamente do cartão. | O cartão retorna suavemente à posição plana neutra em ~320ms sem estalos ou tremores. |
| **5. Estabilidade de Leitura** | Abrir um capítulo para estudo. | O texto do leitor permanece 100% estático e imóvel. |
