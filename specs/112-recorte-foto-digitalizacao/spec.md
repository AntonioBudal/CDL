# Feature Specification: F0.11.10 — Recorte de Foto na Digitalização

**Feature Branch**: `112-recorte-foto-digitalizacao`

**Created**: 2026-11-12

**Status**: Concluída em 2026-11-12

**Input**: Item "recorte de foto para a digitalização" do Roadmap 0.11 no HANDOFF. Quinta e última feature do lote 2
do 0.11 (fecha o lote: suítes completas). **Sem migração.**

---

## 1. Contexto (auditoria de 2026-11-12, só código)

| Ponto | Situação | Onde |
|---|---|---|
| Fluxo | Escolher/tirar foto → **leitura imediata** (OCR local no servidor) → revisão → salvar | `views/DigitizeNotebookView.vue`, `composables/useDigitizeDraft.ts` (`choose`) |
| Orientação | Só a do arquivo; não há girar | — |
| Recorte | **Não existe.** Mesa, dedo, a página vizinha e a sombra entram na leitura e viram lixo ou linhas incertas | — |
| Limites | JPEG/PNG/WebP, 20 MB, 40 megapixels no servidor | `types/digitize.ts`, `core/config.py` |
| Foto de conferência | Opcional (F0.090-C): guarda a foto enviada | `useDigitizeDraft.ts` (`keepPhoto`) |

**Decisão:** o recorte e o giro acontecem **no navegador**, antes da leitura; o servidor recebe só a imagem já
recortada (menor, mais rápida de ler). Nada muda na API nem no banco.

---

## 2. User Stories

### US1 — Recortar antes de ler (P1)

**Acceptance**:
1. Depois de escolher ou tirar a foto, a tela mostra a etapa **"Ajustar a foto"** com a imagem e um retângulo de
   recorte que começa com uma margem de 4% (quase a foto inteira).
2. O retângulo se ajusta arrastando os **4 cantos** e as **4 bordas**, ou movendo-o inteiro (mouse, toque e caneta,
   por eventos de ponteiro). Alvos de toque de 44 px. Tamanho mínimo: 10% de cada lado.
3. Botões: **"Ler a página"** (recorta e envia), **"Usar a foto inteira"** (envia como está, igual a hoje),
   **"Escolher outra foto"**.
4. A área fora do recorte fica escurecida; a área dentro fica nítida.

### US2 — Girar (P1)

**Acceptance**:
1. **"Girar à esquerda"** e **"Girar à direita"** (90°). O recorte acompanha o giro (continua sobre o mesmo trecho
   da página).
2. A orientação gravada na foto pelo celular (EXIF) é respeitada na tela e no recorte.

### US3 — Acessível pelo teclado (P1)

**Acceptance**:
1. Cada canto e o retângulo inteiro são focáveis; setas movem 1% (com Shift, 5%); o nome lido pelo leitor de tela
   diz o que cada um ajusta ("Canto superior esquerdo do recorte").
2. Um texto ao vivo anuncia o recorte atual em porcentagem ("Recorte: 4% a 96% na largura, 4% a 96% na altura").

### US4 — Imagem enviada (P2)

**Acceptance**:
1. O recorte é desenhado num `canvas` na resolução original (sem perder nitidez) e enviado como JPEG de qualidade
   0,92 (PNG continua PNG). Se passar de 40 megapixels ou 20 MB, é reduzido proporcionalmente até caber.
2. "Tentar de novo" e a foto de conferência usam a imagem **recortada**.
3. Se o navegador não conseguir recortar (sem `canvas`), a tela avisa e envia a foto inteira.

### Edge Cases

- Foto muito pequena (menos de 300 px no lado menor): pula a etapa de recorte e lê direto, como hoje.
- Rotação + recorte: o resultado é o trecho recortado já na orientação escolhida.
- Celular: imagem cabe na largura; nada de rolagem lateral; arrastar o recorte não rola a página
  (`touch-action: none` só na área da imagem).
- Cancelar durante a leitura volta à etapa inicial (como hoje).

---

## 3. Requirements

- **FR-001**: `utils/photoCrop.ts` (puro): `initialCrop()`, `moveHandle(crop, handle, dx, dy)`, `moveCrop`,
  `clampCrop` (mínimo 10%, dentro da imagem), `rotateCrop(crop, direction)`, `outputSize(w, h, crop, rotation)`
  (aplica os limites), `describeCrop(crop)`. O recorte é guardado em frações (0–1) da imagem **já girada**.
- **FR-002**: `components/digitize/PhotoCropper.vue`: imagem, máscara, alças, botões, teclado, `aria-live`; emite
  `confirm(File)`, `whole()`, `another()`. Desenho e exportação por `canvas` (`toBlob`).
- **FR-003**: `useDigitizeDraft`: nova fase `adjust`; `prepare(file)` valida e mostra a etapa; `read(file)` lê o
  arquivo dado (o recortado ou o original); `choose(file)` continua lendo direto (compatibilidade e fotos pequenas).
- **FR-004**: Só tokens existentes, `.quiet` nos botões secundários, 44 px, contraste ≥ 4,5:1 nos 10 temas.

## 4. Success Criteria

- **SC-001**: Testes puros: recorte inicial, cada alça, mover inteiro, limites e mínimo, giro nos dois sentidos (ida e
  volta igual ao original), tamanho de saída com e sem redução, descrição.
- **SC-002**: Testes do composable: `prepare` → `adjust`; `read` com o arquivo recortado → `review` e "Tentar de novo"
  reusa o recortado; foto pequena lê direto; testes antigos da 086 continuam passando.
- **SC-003**: Navegador (imagem fictícia gerada no próprio teste, nunca foto real): recorte por arraste e por teclado,
  giro, envio do recortado (tamanho conferido no pedido), "Usar a foto inteira"; 1366 e 375 px; contraste nos 10 temas.
- **SC-004**: Fecho do lote 2: `npm test` e `pytest` **completos** (com banco descartável), build; falha de feature
  anterior em commit próprio; commit; levar ao `main`.

## 5. Fora do escopo

- Detecção automática das bordas da folha e correção de perspectiva (exigiria visão computacional no navegador ou no
  servidor).
- Ajustes de brilho/contraste; várias páginas por estudo.
