# Quickstart & Validation Guide: F0.9.02 — Ergonomia Mobile e Descongestionamento da Página do Livro

**Feature**: `specs/083-ergonomia-mobile-pagina-livro`  
**Date**: 2026-10-21  

---

## 1. Pré-requisitos de Ambiente

- Node.js 20+ instalado.
- Dependências do frontend instaladas em `caderno-leitura-0.1/frontend`.
- Terminal PowerShell no ambiente Windows local.

---

## 2. Validação Automatizada (Suíte de Testes da Feature)

A validação unitária e de regressão da Feature 083 será executada através de um script de teste dedicado construído com o test runner nativo do Node.js (`node:test`):

```powershell
cd caderno-leitura-0.1/frontend
node --test tests/feature-083-book-mobile-layout.test.mjs
```

### Critérios de Sucesso dos Testes Unitários

1. **F083-US1 (Cabeçalho Condensado):** Verifica a presença da miniatura de capa (48x72px), o truncamento de título no mobile e o agrupamento das ações no menu `DropdownMenu.vue`.
2. **F083-US2 (Faixa de Capítulos Unificada):** Valida a supressão de `.chapters-nav-strip` no mobile (`display: none !important`) e a permanência do seletor único com suporte a adição de capítulo.
3. **F083-US3 (Inspetor Analítico Recolhível):** Valida a inicialização colapsada do inspetor analítico no mobile, a presença do botão de alternância com `:aria-expanded` e a persistência do inspetor sempre aberto no desktop.
4. **F083-Polish (Conformidade Constitucional):** Confirma a ausência total de emojis no código e estilos de `BookView.vue` e valida que nenhum seletor novo utiliza cores hexadecimais fixas.

---

## 3. Validação da Suíte Completa e Build de Produção

Antes de submeter o commit atômico, a suíte de testes de regressão completa e a checagem de tipos estritos do TypeScript devem passar com 100% de sucesso:

```powershell
# 1. Executar suíte completa do frontend
cd caderno-leitura-0.1/frontend
npm test

# 2. Executar checagem de tipos e build do Vite
npm run build
```

---

## 4. Guia de Validação Manual da Interface

Para validação visual através do navegador:

1. **Executar o ambiente:** Inicie o servidor local através de `python iniciar.py` na raiz do projeto ou `npm run dev` no frontend.
2. **Simular Viewport Móvel (DevTools):**
   - Abra o DevTools (F12) e ative a simulação de dispositivo móvel (ex.: iPhone 14/15 com 390x844px ou Galaxy S20 com 360x740px).
   - Navegue até a página de qualquer livro (`/livros/:bookId`).
3. **Verificar Primeira Dobra da Tela:**
   - O cabeçalho deve exibir a miniatura da capa e o título do livro de forma compacta (menos de 160px de altura).
   - A barra de capítulos deve exibir apenas o seletor dropdown e o botão de novo capítulo.
   - O primeiro card de estudo ou a mensagem de capítulo vazio deve estar visível imediatamente na primeira dobra (sem rolagem).
4. **Testar Menu de Ações Agrupadas:**
   - Toque em "Ações do livro" e verifique a abertura do menu suspenso.
   - Teste acionar o "Modo foco", "Exportar anotações", "Editar livro" e "Mover para a lixeira".
5. **Testar Inspetor Recolhível:**
   - Role até o final da página e confirme que o inspetor inicia com "Ver detalhes do livro".
   - Toque no botão e confirme a revelação suave das métricas.
   - Toque novamente e confirme o fechamento.
6. **Alternar para Desktop:**
   - Desative a simulação móvel ou expanda a janela para `>= 768px`.
   - Confirme que a capa expande para o tamanho normal, os 4 botões em pílula retornam e a esteira horizontal de pílulas roláveis de capítulos é restaurada.
