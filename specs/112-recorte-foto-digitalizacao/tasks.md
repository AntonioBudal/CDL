# Tasks — F0.11.10: Recorte de Foto na Digitalização

**Input**: [spec.md](spec.md) e [plan.md](plan.md). Imagens de teste geradas; sem migração; fecha o lote 2 do 0.11.

- [x] T001 Testes que falham primeiro: `feature-112-recorte-foto.test.mjs` (geometria e composable).
- [x] T002 `photoCrop.ts`: recorte inicial, alças, mover, limites, giro, tamanho de saída, descrição.
- [x] T003 `useDigitizeDraft`: fase `adjust`, `prepare`, `read`.
- [x] T004 `PhotoCropper.vue`: imagem, máscara, alças, teclado, giro, exportação por `canvas`.
- [x] T005 `DigitizeNotebookView`: etapa entre escolher e ler.
- [x] T006 Testes novos e vizinhos; build; navegador (1366 e 375 px; 10 temas).
- [x] T007 Fecho do lote 2: `npm test` e `pytest` completos (banco descartável); correções de features anteriores em
  commit próprio.
- [x] T008 `RETOMADA.md` e `HANDOFF.md`; commit; levar ao `main`; build no checkout principal.
