# Guia Rápido de Validação e Homologação: F0.8.15 — Bateria Completa de Regressão e Consolidação do Roadmap de Responsividade

**Feature**: `081-regressao-responsiva`  
**Data**: 2026-10-12  
**Status**: Operacional  

---

## 1. Pré-requisitos e Ambiente

- **Sistema Operacional**: Windows 10/11 com PowerShell.
- **Node.js**: v20 ou superior.
- **Python**: 3.13 de 64 bits.
- **Isolamento de Dados**: O banco ativo local (`backend/data/caderno.db`) NUNCA deve ser modificado ou utilizado para testes manuais destrutivos. Todas as validações utilizam bancos descartáveis ou dados fictícios.

---

## 2. Execução dos Testes Automatizados

No terminal PowerShell, a partir da raiz do repositório (`c:\Users\User\caderno`):

### 2.1. Teste-Guarda Consolidado de Regressão
Executa a suíte de testes de integridade responsiva:

```powershell
cd caderno-leitura-0.1/frontend
npm test -- tests/feature-081-responsive-regression.test.mjs
```

### 2.2. Bateria Completa de Testes do Frontend
Garante que todas as suítes (incluindo as features 076 a 080) continuam 100% verdes:

```powershell
npm test
```

### 2.3. Verificação de Tipos e Build de Produção
Compila o frontend com o compilador estrito do TypeScript (`vue-tsc`):

```powershell
npm run build
```

### 2.4. Bateria de Testes do Backend
Confirma que o backend e os endpoints da API permanecem estáveis:

```powershell
cd ../backend
pytest
```

---

## 3. Homologação em Aparelhos Físicos (Rede Local / Tailscale)

Para validar o comportamento dinâmico de gestos táteis, teclado virtual e safe areas em aparelhos reais:

### 3.1. Inicialização do Servidor Único
A partir da raiz do projeto (`caderno-leitura-0.1/`):

```powershell
python iniciar.py
```

O terminal exibirá os endereços de acesso local (`http://localhost:8000`) e na rede (`http://<IP-LOCAL>:8000` ou endereço Tailscale).

### 3.2. Roteiro Passo a Passo de Teste no Aparelho Móvel

#### Cenário 1: Navegação Shell e Alvos de Toque (320px–390px)
1. Abra o navegador do smartphone e acesse o endereço do servidor.
2. Faça login com uma conta fictícia de teste.
3. Observe a barra inferior móvel (`MobileTabBar`):
   - Toque em cada um dos ícones (Livros, Destaques, Revisão, Caixa, Mais).
   - Verifique que o toque é imediato, confortável e sem miss-click (área $\ge 44 \times 44\text{ px}$).
4. Abra o menu "Mais":
   - Verifique que os itens secundários aparecem alinhados e fecham ao tocar fora ou selecionar uma opção.

#### Cenário 2: Visualizações Móveis (Mapa, Canvas, Árvore)
1. Navegue até um livro de teste e abra a aba de **Mapa**:
   - Faça gestos de pan (arrastar com um dedo) e pinch-to-zoom (pinça com dois dedos).
   - Alterne para o modo de Lista Semântica pelo botão de alternância; verifique a leitura em lista vertical.
2. Alterne para a aba de **Canvas**:
   - Role a página verticalmente sobre o canvas; confirme que o scroll vertical não é bloqueado (`touch-action: pan-y`).
3. Alterne para a aba de **Árvore**:
   - Verifique que não há alça de arrasto visível e que a indentação dos ramos está compacta e legível.

#### Cenário 3: Biblioteca de Destaques
1. Navegue até a tela de Destaques (`/destaques`):
   - Verifique a barra de filtros no topo: a busca deve ocupar largura total e os botões devem quebrar elegantemente sem transbordamento lateral.
   - Role até o final da página e confirme que o último card ou a paginação não fica coberto pela barra inferior fixa.

#### Cenário 4: Formulários e Teclado Virtual
1. Abra a tela de edição de estudo (`/livros/1/estudos/1/editar`):
   - Toque no campo de texto para abrir o teclado virtual nativo.
   - Confirme que o botão de salvar permanece acessível ou rola suavemente para visualização sem quebrar o layout.

#### Cenário 5: Rotação para Modo Paisagem (844×390px)
1. Gire o smartphone para a orientação horizontal:
   - Verifique se o conteúdo respeita as bordas do aparelho (`safe-area-inset`).
   - Confirme a ausência de barra de rolagem horizontal espúria.

---

## 4. Checklist de Aceite e Fechamento

- [ ] Todas as 25 rotas exibem `scrollWidth === clientWidth` em todas as viewports.
- [ ] 19 problemas (P-01 a P-19) verificados e com resolução atestada.
- [ ] `npm test` executa com 100% de sucesso.
- [ ] `npm run build` conclui sem erros de tipos ou empacotamento.
- [ ] `pytest` executa com 100% de sucesso.
- [ ] Zero emojis em todo o código e documentação.
- [ ] Atualização formal de `docs/contexto/RETOMADA.md`.
