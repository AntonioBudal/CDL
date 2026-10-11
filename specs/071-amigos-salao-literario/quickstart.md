# Guia de Validação Rápida: F0.8.06 — Amigos: Salão Literário e Círculos de Estudo

**Feature Branch**: `071-amigos-salao-literario`  
**Data**: 2026-10-11  
**Status**: Concluído (Fase 1 do Spec Kit)

Este guia orienta a validação ponta a ponta dos requisitos da **Feature F0.8.06**, abrangendo tanto suítes automatizadas de testes quanto verificação visual interativa dos cenários de uso.

---

## 1. Pré-Requisitos e Ambiente de Execução

- **Ambiente**: Windows local (PowerShell).
- **Repositório**: `caderno-leitura-0.1/`.
- **Node.js**: Versão 24+.
- **Python**: Versão 3.13 no ambiente virtual `backend/.venv`.

---

## 2. Comandos de Validação Automatizada

### 2.1. Suíte de Testes do Frontend (Node Test Runner)

Executa os testes unitários e de contrato do frontend, incluindo o teste de contrato da feature:

```powershell
cd c:\Users\User\caderno\caderno-leitura-0.1\frontend
npm test
```

**Resultado Esperado**:
- Todos os testes passam com status de sucesso (`PASS`).
- Teste `tests/feature-071-amigos-salao-literario.test.mjs` valida com sucesso a presença e contratos de `BookplateCard.vue`, abas WAI-ARIA, duração de 1200ms do selo e ausência de emojis.

### 2.2. Verificação de Tipos e Build de Produção

Garante integridade estrita do TypeScript e empacotamento Vite sem erros:

```powershell
cd c:\Users\User\caderno\caderno-leitura-0.1\frontend
npm run build
```

**Resultado Esperado**:
- O compilador `vue-tsc` conclui sem erros de tipos.
- O build Vite gera a pasta `dist/` com sucesso.

### 2.3. Suíte de Testes do Backend (Pytest)

Valida que nenhum contrato ou endpoint existente foi afetado:

```powershell
cd c:\Users\User\caderno\caderno-leitura-0.1
backend\.venv\Scripts\pytest.exe backend/tests
```

**Resultado Esperado**:
- 100% dos testes do backend passam (`passed`).

---

## 3. Roteiro de Validação Manual (Cenários de Uso)

Inicie o servidor de desenvolvimento para testes interativos:

```powershell
cd c:\Users\User\caderno\caderno-leitura-0.1\frontend
npm run dev
```

Acesse `http://localhost:5173/amigos` (com login de teste efetuado).

---

### Cenário 1: Bookplate Card & Microinteração do Selo (P1 / SC-001 / SC-002)

1. **Ação**: Acessar `/amigos`.
2. **Observação**: No topo da página, acima das abas, verificar a presença do `BookplateCard.vue` contendo avatar, nome de exibição, bio literária e `@identificador`.
3. **Ação**: Clicar no botão "Copiar" do identificador.
4. **Resultado Esperado**:
   - O identificador é copiado para a área de transferência.
   - O botão recebe a classe `.is-stamped`, exibindo leve pulso e feedback do selo.
   - O selo esmaece suavemente em exatamente 1200ms, retornando ao estado de repouso sem travar a interface.

---

### Cenário 2: Compartilhamento de Perfil via Web Share API e Fallback (P1 / FR-004)

1. **Ação (Dispositivo Móvel / Simulação)**: Em ambiente móvel com `navigator.share` ativo, clicar em "Compartilhar Perfil".
2. **Resultado Esperado**: O sistema operacional abre a folha nativa de compartilhamento contendo título e link para `/u/:username`.
3. **Ação (Desktop Clássico)**: No navegador de desktop sem Web Share API, clicar em "Compartilhar Perfil".
4. **Resultado Esperado**: O link público do perfil (`/u/:username`) é copiado para o clipboard e um selo confirmatório é exibido por 1200ms.

---

### Cenário 3: Navegação por Abas e Cartões do Salão Literário (P1 / P2 / FR-005 / FR-006)

1. **Ação**: Clicar na aba "Círculo de Leitura".
2. **Resultado Esperado**: Visualizar os amigos cadastrados em cartões elegantes contendo data amigável ("Amigos desde..."), link para a estante pública (`/u/:username`) e botões contextuais.
3. **Ação**: Clicar na aba "Solicitações".
4. **Resultado Esperado**: Visualizar convites recebidos com botões "Aceitar" e "Recusar", e convites enviados com opção de cancelamento.
5. **Ação**: Clicar na aba "Descobrir Leitores" e digitar na busca.
6. **Resultado Esperado**: A busca é executada com debounce de 300ms, exibindo os cartões com botão de conectar.
7. **Ação**: Clicar na aba "Bloqueados".
8. **Resultado Esperado**: Visualizar leitores bloqueados e opção defensiva de desbloqueio.

---

### Cenário 4: Imunidade Cromática e Acessibilidade (NR-001 / NR-002 / NR-003)

1. **Ação**: Alternar entre os 10 temas visuais do Leitorum nas configurações (Claro, Escuro, Sépia, E-Ink, etc.).
2. **Resultado Esperado**: O Bookplate Card e todos os cartões adaptam suas cores perfeitamente via variáveis CSS, sem fundos brancos estourados nem textos ilegíveis.
3. **Ação**: Inspecionar elementos no DevTools.
4. **Resultado Esperado**:
   - Zero emojis em textos e botões (apenas ícones SVG `<Icon />`).
   - Alvos táteis $\ge 44 \times 44$px para botões e abas.
   - Navegação por teclado operacional com `aria-selected` alternando corretamente.
