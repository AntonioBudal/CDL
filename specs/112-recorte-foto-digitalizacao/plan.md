# Implementation Plan: F0.11.10 — Recorte de Foto na Digitalização

**Spec**: [spec.md](spec.md) | **Date**: 2026-11-12 | **Status**: Executado em 2026-11-12

## Technical Context

Vue 3 + TS no navegador (`canvas`, eventos de ponteiro). **Sem migração** e sem mudança de API. Testes `node:test`;
fecho do lote com `npm test` e `pytest` completos.

## Constitution Check

| Regra | Situação |
|---|---|
| Dados do usuário nunca lidos | OK: imagens de teste geradas no próprio teste |
| Banco ativo | Não é tocado |
| Privacidade | O recorte acontece no navegador; o servidor recebe menos da foto do que hoje |
| Lote | 5ª feature, fecha o lote 2 do 0.11 |

## Arquivos e mudanças

| Arquivo | Mudança |
|---|---|
| `frontend/src/utils/photoCrop.ts` (novo) | geometria pura do recorte e do giro; tamanho de saída |
| `frontend/src/components/digitize/PhotoCropper.vue` (novo) | etapa "Ajustar a foto" |
| `frontend/src/composables/useDigitizeDraft.ts` | fase `adjust`, `prepare`, `read` |
| `frontend/src/views/DigitizeNotebookView.vue` | usa o recortador entre escolher e ler |
| testes | `feature-112-recorte-foto.test.mjs` |
| docs | `RETOMADA.md`, `HANDOFF.md` (fecho do lote 2) |

## Decisões

1. **No navegador**: corta antes de enviar; menos dados, leitura mais rápida, nenhuma API nova.
2. **Frações da imagem girada**: o recorte independe do tamanho de exibição; girar é uma transformação simples das
   frações (testável sem `canvas`).
3. **Alças por ponteiro + teclado**: um só código para mouse, toque e caneta; o teclado cobre acessibilidade.
4. **`choose` intacto**: os testes e o comportamento da 086 continuam valendo; o recorte é uma etapa a mais.

## Riscos

| Risco | Mitigação |
|---|---|
| Fotos de celular enormes estourarem a memória do `canvas` | Redução proporcional até 40 MP / 20 MB; aviso e envio da foto inteira se falhar |
| EXIF ignorado em algum navegador | `createImageBitmap(file, { imageOrientation: 'from-image' })` com reserva em `<img>` |
| Arraste rolar a página no celular | `touch-action: none` só na área da imagem |
