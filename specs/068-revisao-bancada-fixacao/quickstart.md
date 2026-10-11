# Quickstart & Validation Guide: F0.8.03 — Revisão: Bancada de Fixação Cognitiva

**Feature Branch**: `068-revisao-bancada-fixacao` | **Date**: 2026-10-11 | **Spec**: [spec.md](spec.md)

Este guia fornece roteiros executáveis e cenários de teste automatizados e manuais para validar a Central de Revisão redesenhada.

---

## 1. Pré-Requisitos e Ambiente

1. O servidor local pode ser executado em ambiente de desenvolvimento ou testes.
2. Não utilizar o banco de dados ativo de produção para testes automatizados.
3. Runtimes:
   - Node.js $\ge 20$ / npm $\ge 10$
   - Python 3.13 no ambiente virtual do projeto

---

## 2. Cenários de Validação Ponta a Ponta

### Cenário 1: Barra de Prontidão Intelectual e Disparador de Sessão
**Objetivo:** Validar que a Central de Revisão consolida os indicadores em uma faixa única sem caixas repetitivas de estilo SaaS.
- **Passo 1:** Acessar a rota `/revisao` com cartões pendentes cadastrados.
- **Passo 2:** Verificar visualmente a presença da faixa de prontidão: contagem total de itens pendentes, estimativa em minutos (~X min) e proporção entre perguntas e termos ocultos.
- **Passo 3:** Clicar no botão primário "Praticar Revisão Agora".
- **Resultado Esperado:** A sessão é iniciada imediatamente, transicionando para a exibição do primeiro cartão de estudo sem recarregar a página.

---

### Cenário 2: Ciclo de Active Recall 100% via Teclado
**Objetivo:** Provar a ergonomia e acessibilidade da sessão ativa sem necessidade de ponteiro/mouse.
- **Passo 1:** Com o cartão de desafio em tela (frente), pressionar a tecla `Espaço`.
- **Passo 2:** Validar que o verso do cartão é revelado com transição visual suave ($\le 250$ms).
- **Passo 3:** Pressionar a tecla numérica `3` (Bom).
- **Passo 4:** Validar que a resposta é gravada e o cartão subsequente é exibido de imediato com a frente oculta.
- **Resultado Esperado:** O leitor avança pela fila de revisão em alta velocidade utilizando exclusivamente o teclado.

---

### Cenário 3: Interação com Estado Vazio Pedagógico
**Objetivo:** Validar a experiência instrutiva quando o usuário não possui cartões pendentes de revisão.
- **Passo 1:** Acessar a rota `/revisao` em uma conta sem itens para revisão.
- **Passo 2:** Verificar que caixas vermelhas ou mensagens "0 itens" foram suprimidas em favor do guia pedagógico acolhedor.
- **Passo 3:** Clicar na lacuna do termo oculto de demonstração (`[termo oculto]`).
- **Passo 4:** Observar a microinteração que revela a palavra e apresenta a mensagem explicativa sobre a metodologia de *Active Recall*.
- **Resultado Esperado:** O leitor compreende imediatamente o propósito da ferramenta e visualiza as instruções para grifar livros.

---

### Cenário 4: Conclusão Serena da Rodada e Histórico
**Objetivo:** Verificar a transição de encerramento da sessão e a persistência na aba de histórico.
- **Passo 1:** Responder ao último cartão de uma sessão ativa.
- **Passo 2:** Validar a exibição da tela de conclusão serena com o resumo do tempo total e contagem por nível de facilidade.
- **Passo 3:** Acessar a aba "Histórico de Sessões".
- **Resultado Esperado:** A sessão recém-finalizada consta na listagem com data, duração e contagem de itens avaliados.

---

## 3. Comandos de Validação Automatizada

Executar na raiz da aplicação (`caderno-leitura-0.1`):

```bash
# 1. Executar suíte de testes de frontend (unitários e de componentes)
npm test

# 2. Executar validação de tipagem TypeScript estrita e compilação de build
npm run build

# 3. Executar suíte de testes do backend com bancos descartáveis
backend\.venv\Scripts\python.exe -m pytest backend/tests
```
