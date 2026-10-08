# Quickstart: F0.7.14 — Sessões Estruturadas de Estudo e Auditoria de Aprendizado

**Feature**: F0.7.14 — Sessões Estruturadas de Estudo  
**Branch**: `063-sessoes-estudo`  
**Date**: 2026-10-10  

---

## 1. Visão Geral da Validação

Este guia orienta a validação ponta a ponta da funcionalidade de **Sessões Estruturadas de Estudo**, garantindo isolamento total de dados, estabilidade de migração e conformidade com o sistema visual e acessibilidade.

---

## 2. Validação Automatizada (Backend)

Execute a suíte de testes com banco SQLite efêmero em diretório descartável:

```bash
python -m pytest backend/tests/test_study_sessions.py -v
```

Cenários cobertos pelos testes:
- `test_start_study_session_quick`: Inicialização de sessão rápida de 10 itens.
- `test_start_study_session_dynamic_scope`: Lote dinâmico quando há menos itens que o limite solicitado (Q2: A).
- `test_answer_item_and_update_highlight`: Registro atômico de item e avanço de repetição espaçada.
- `test_complete_study_session_summary`: Finalização de sessão e geração de resumo com taxas de acerto.
- `test_interrupt_session_preserves_answers`: Interrupção de sessão preservando itens respondidos (Q1: A).
- `test_session_history_isolation`: Isolamento multiusuário estrito por `user_id`.

---

## 3. Validação Automatizada (Frontend)

Execute a suíte de testes de componentes e contratos:

```bash
npm test -- tests/study_sessions.test.mjs
```

Cenários validados no frontend:
- Renderização de `StudySessionView.vue` em modo tela limpa sem barras dispersivas.
- Funcionamento da barra de progresso horizontal em `SessionProgressHeader.vue`.
- Atalhos de teclado (`Espaço` para revelar, `1`/`2`/`3` para avaliar retenção, `Esc` para diálogo de confirmação).
- Exibição triunfante e solene no `SessionSummaryModal.vue`.
- Ausência total de emojis e cumprimento da cota de alvos táteis móveis $\ge 44 \times 44$px.

---

## 4. Validação Manual Ponta a Ponta

1. Abra a aplicação no navegador (`http://localhost:8000`).
2. Acesse a Central de Revisão ou qualquer Livro com estudos pendentes.
3. Clique em **"Iniciar Sessão de Estudo"**.
4. Selecione a opção **"Sessão Rápida (10 itens)"**.
5. Verifique a transição suave para o modo imersivo e a indicação de progresso horizontal.
6. Responda aos cartões utilizando tanto o clique do mouse quanto as teclas numéricas `1`, `2` e `3`.
7. Ao responder ao último cartão, verifique o surgimento do modal de encerramento com métricas de tempo, cartões processados e taxa de retenção.
8. Retorne à Central de Revisão e verifique a inclusão da sessão no **Histórico de Sessões**.
