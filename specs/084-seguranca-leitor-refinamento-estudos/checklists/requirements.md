# Requirements Checklist: F0.9.03 — Segurança Operacional e Refinamento do Leitor de Estudos

## 1. Escopo e Limites da Feature
- [x] O escopo não introduz novos módulos, rotas de backend ou modelos no banco de dados.
- [x] A feature se concentra no leitor (`StudyView.vue`), editor (`StudyEditView.vue`), barra de leitura (`ActiveReadingBar.vue`) e abas (`StudyTabs.vue`).
- [x] Conformidade com a política Zero Emojis em todos os textos e código.

## 2. User Story 1 — Menu Contextual de Ações Secundárias no Leitor
- [x] Apenas "Editar estudo" e pílula de status ficam em destaque primário.
- [x] Ações secundárias (Compartilhar, Exportar, Histórico, Lixeira) encapsuladas em menu dropdown.
- [x] Ação de exclusão destacada com estilo de perigo e separador semântico.
- [x] Proteção obrigatória com confirmação via `TrashConfirmModal.vue`.
- [x] Modo somente leitura (`canEdit === false`) suprime botão de edição e ação de exclusão.
- [x] Acessibilidade WAI-ARIA completa (`aria-haspopup`, `aria-expanded`, navegação por teclado).

## 3. User Story 2 — Indicador Visual de Persistência no Editor
- [x] Pílula de status renderizada ao lado do título em `StudyEditView.vue`.
- [x] Estados reativos: "Salvando…", "Rascunho salvo neste navegador" e "Alterações salvas".
- [x] Acessibilidade com `role="status"` e `aria-live="polite"`.
- [x] Integração harmônica com `useStudyDraft` e `useStudyEdit`.

## 4. User Story 3 — Alvos de Toque Ergonômicos
- [x] Todos os botões da barra de leitura ativa (`ActiveReadingBar.vue`) com dimensão mínima de 44x44px no mobile/touch.
- [x] Botão de fechar `.close-btn` com área tátil mínima de 44x44px.
- [x] Botões de abas em `StudyTabs.vue` com altura mínima de 44px.
- [x] Suporte a `@media (pointer: coarse)`.

## 5. Validação e Qualidade
- [x] Testes automatizados unitários cobrindo todas as histórias de usuário.
- [x] Ausência de cores hexadecimais fixas nos novos elementos.
- [x] Execução e aprovação em `npm test`, `npm run build` e `pytest`.
