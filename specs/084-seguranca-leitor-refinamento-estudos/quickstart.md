# Quickstart & Verification Guide: F0.9.03 — Segurança Operacional e Refinamento do Leitor de Estudos

**Feature**: `specs/084-seguranca-leitor-refinamento-estudos`  
**Parent Roadmap**: `docs/contexto/ROADMAP-0.9.md` (Feature F03)  
**Zero Emojis Policy**: Rigorosamente respeitada.

---

## 1. Execução Rápida dos Testes da Feature

Para validar as alterações da Feature F03 de forma isolada no frontend:

```powershell
cd caderno-leitura-0.1/frontend
node --test tests/feature-084-study-reader-safety.test.mjs
```

---

## 2. Validação Completa das Suítes do Projeto

Antes de qualquer commit, a validação integral deve ser executada:

```powershell
# 1. Testes unitários do frontend
cd caderno-leitura-0.1/frontend
npm test

# 2. Compilação TypeScript e empacotamento Vite
npm run build

# 3. Testes do backend em ambiente isolado
cd ../backend
.venv/Scripts/pytest.exe
```

---

## 3. Roteiro de Verificação Manual no Navegador

### Cenário 1 — Menu Contextual e Proteção de Exclusão no Leitor (`/livros/:bookId/estudos/:studyId`)
1. Abrir um livro e acessar um estudo.
2. Observar o cabeçalho: apenas "Editar estudo" e pílula de status aparecem diretamente.
3. Clicar no botão "Mais opções" (`more-horizontal`).
4. Constatar a abertura do menu suspenso contendo "Compartilhar", "Exportar", "Histórico de versões", separador visual e "Mover para a lixeira" com estilo de alerta.
5. Clicar fora ou pressionar `Escape`; verificar o fechamento suave do menu.
6. Clicar em "Mover para a lixeira"; verificar que o modal de confirmação (`TrashConfirmModal.vue`) é exibido e que a exclusão requer confirmação deliberada.

### Cenário 2 — Pílula de Status no Editor de Estudo (`/livros/:bookId/estudos/:studyId/editar`)
1. Clicar em "Editar estudo".
2. Ao carregar sem alterações, constatar que a pílula exibe "Alterações salvas".
3. Alterar o texto de uma das seções; constatar que a pílula atualiza imediatamente para "Rascunho salvo neste navegador".
4. Clicar no botão primário "Salvar alterações"; constatar que a pílula exibe temporariamente "Salvando…".
5. Após o salvamento, constatar o retorno para "Alterações salvas".

### Cenário 3 — Alvos de Toque no Mobile e Barra de Leitura Ativa
1. Abrir a ferramenta de desenvolvimento do navegador no modo de emulação de celular (ex.: 390x844px).
2. Ativar a sessão de leitura ativa.
3. Inspecionar as dimensões de todos os botões da barra inferior (`.reading-bar-btn`, inclusive `.close-btn`); confirmar que nenhum possui dimensão inferior a 44x44px.
4. Inspecionar as abas de análise (`.study-tabs [role="tab"]`); confirmar altura mínima de 44px.
