# Quickstart & Validação: Ajustes — Ateliê de Preferências e Leitura Viva

**Feature**: `072-ajustes-atelie-preferencias`
**Date**: 2026-10-11
**Status**: Concluído

## 1. Visão Geral

Este guia descreve os passos de validação automatizada e manual para comprovar a entrega da **Feature 072: Ajustes — Ateliê de Preferências e Leitura Viva**, cobrindo a nova galeria de temas estilo Windows 11 com caixas de amostra de cor, o menu lateral vertical de 5 seções e a bancada de leitura viva em tempo real.

---

## 2. Pré-requisitos de Ambiente

1. Repositório na raiz `c:\Users\User\caderno\caderno-leitura-0.1`.
2. Dependências do frontend instaladas (`node_modules` presente).
3. Servidor de desenvolvimento ou suite de testes de ponta a ponta pronta.

---

## 3. Comandos de Verificação Automatizada

### 3.1 Testes Unitários e de Integração Frontend

```powershell
cd c:\Users\User\caderno\caderno-leitura-0.1\frontend
npm test
```

**Resultado Esperado**:
- Todos os testes legados continuam aprovados (mínimo 557 testes).
- Os novos testes de contrato da Feature 072 (`tests/feature-072-ajustes-atelie-preferencias.test.mjs`) são executados e aprovados com 100% de sucesso.

### 3.2 Verificação Estrita de Tipos TypeScript e Build de Produção

```powershell
cd c:\Users\User\caderno\caderno-leitura-0.1\frontend
npm run build
```

**Resultado Esperado**:
- `vue-tsc -b` conclui com 0 erros de compilação ou de tipagem.
- O Vite compila os bundles de produção em `dist/` com sucesso.

### 3.3 Verificação de Integridade do Backend

```powershell
cd c:\Users\User\caderno\caderno-leitura-0.1
.\backend\.venv\Scripts\pytest backend/tests
```

**Resultado Esperado**:
- Todos os 458 testes do backend continuam aprovados (1 skipped, 0 falhas).

---

## 4. Roteiro de Validação Manual da Interface

### 4.1 Galeria de Temas Estilo Windows 11
1. Acesse o Caderno de Leitura e navegue para `/ajustes?tab=aparencia`.
2. Verifique se a seção "Aparência" renderiza os 10 cartões de pré-visualização de temas em vez de um `<select>` básico.
3. Observe que cada cartão exibe um box gráfico com:
   - Fundo com a cor de página (`--color-page`).
   - Mockup de janela com a superfície (`--color-surface`).
   - Linha sintética com a cor do texto (`--color-text`).
   - Pílula com a cor de destaque (`--color-accent`).
4. Verifique o tema `e-ink`: ele deve se mostrar estritamente em preto e branco puro.
5. Clique em outro tema (exemplo: `fiorde` ou `pergaminho`):
   - O tema global do sistema e o simulador devem mudar instantaneamente.
   - O cartão selecionado deve receber o anel de seleção luminoso e a marcação ativa.
6. Teste navegação por teclado: pressione `Tab` até o grupo de temas e use as setas (`ArrowRight`/`ArrowDown`/`ArrowLeft`/`ArrowUp`) para alternar a seleção.

### 4.2 Bancada de Leitura Viva em Tempo Real
1. Em tela desktop ($\ge 1024\text{px}$), observe a coluna da direita com o simulador de leitura.
2. Alterne para a aba "Leitura" no menu lateral.
3. Altere o seletor de tamanho do texto (ex.: 120%, 140%):
   - O texto de exemplo no simulador expande imediatamente a 60 FPS sem recarregar.
4. Mude a fonte literária (ex.: Source Sans 3, EB Garamond, OpenDyslexic):
   - A tipografia da amostra reflete a escolha instantaneamente.
5. Reduza a janela para tamanho de celular ($< 768\text{px}$):
   - A coluna da direita se oculta e surge o botão flutuante para abrir o simulador em gaveta inferior retrátil (*bottom sheet*).

### 4.3 Navegação Lateral Vertical
1. No menu lateral vertical, clique sequencialmente em "Perfil & Privacidade", "Aparência", "Leitura", "Sistema" e "Conta & Dispositivos".
2. Verifique a transição suave entre os painéis e a atualização sincronizada da query string na barra de endereços do navegador (`/ajustes?tab=...`).
3. Recarregue a página com `/ajustes?tab=sistema` e comprove que ela inicializa diretamente na aba Sistema.
