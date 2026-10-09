# Quickstart: F0.7.15 — Templates Estruturados de Estudo

## Objetivo
Guia prático para validação rápida da feature F0.7.15 ponta a ponta, abrangendo backend (migração, modelo, API e testes efêmeros) e frontend (catálogo, componentes de seleção, modal de prévia, injeção e salvaguarda de conteúdo).

---

## 1. Pré-requisitos
- Python 3.13 / 3.14 com ambiente virtual ativo
- Node.js 20+ instalado
- Banco descartável efêmero via pytest (`tmp_path`)

---

## 2. Cenários de Validação

### Cenário 1: Migração e Contratos no Backend
1. **Comando de Teste**:
   ```bash
   python -m pytest backend/tests/test_study_templates.py -v
   ```
2. **Expectativa**:
   - Criação de estudo com `template_id = 'conceito'` persiste e retorna corretamente.
   - Atualização de estudo via `PUT /api/studies/{id}` altera `template_id` com avanço de versão.
   - Criação de estudo sem `template_id` assume `'classico'`.
   - Consulta de estudo antigo ou com valor inválido faz fallback transparente para `'classico'`.

### Cenário 2: Catálogo Canônico e Integridade no Frontend
1. **Comando de Teste**:
   ```bash
   node --test frontend/tests/study_templates.test.mjs
   ```
2. **Expectativa**:
   - `studyTemplates.ts` define exatamente os 5 templates canônicos (`classico`, `conceito`, `argumento`, `comparativo`, `resenha`).
   - Todos os templates cobrem as 4 seções analíticas (`summary`, `explanation`, `concepts`, `references`).
   - Zero emojis informais nos componentes `TemplateSelectorModal.vue` e `StudyEditorFields.vue`.
   - Alvos de toque $\ge 44 \times 44$px nos botões e seletor.

### Cenário 3: Validação de Interface do Usuário (E2E Manual / Sandbox)
1. **Abertura do Editor**:
   - No editor de estudos (`StudyEditView.vue`), localize o seletor de "Template de Análise".
   - Clique em "Estudo de Conceito" e veja a prévia do modelo.
   - Confirme a aplicação: os campos de texto devem receber os tópicos formatados em Markdown.
2. **Troca Segura com Conteúdo**:
   - Adicione texto pessoal na seção Resumo.
   - Tente trocar o template para "Reconstrução de Argumento".
   - O modal de confirmação deve surgir:
     - Clique em "Anexar ao Final": o texto existente deve ser mantido e o novo esqueleto adicionado ao término.
     - Em novo teste, selecione "Substituir Conteúdo": o texto deve ser substituído pelo novo esqueleto.
3. **Leitor de Estudo**:
   - Salve o estudo e visualize-o em `StudyView.vue`: um badge sutil no topo deve indicar o modelo empregado (ex.: "Estudo de Conceito").

---

## 3. Validação Geral de Regressão
Ao término da implementação, execute:
```bash
python -m pytest backend/tests -v
npm test
npm run build
```
Todas as suítes devem passar com 100% de sucesso e zero erros de compilação TypeScript.
