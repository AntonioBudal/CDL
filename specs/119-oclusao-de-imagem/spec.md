# Feature Specification: F0.12.06 — Oclusão de imagem

**Feature Branch**: `119-oclusao-de-imagem`

**Created**: 2026-11-15

**Status**: Concluída

**Input**: Item "Oclusão de imagem em SVG — cartões de revisão sobre imagens" do `docs/contexto/ROADMAP-0.12.md`. Sexta
feature do 0.12 (abre o lote 2). **Com migração** (`0041`).

---

## 1. Contexto (auditoria de 2026-11-15)

| Ponto | Situação | Onde |
|---|---|---|
| Imagens de um estudo | Já existem: "folha original" (fotos de conferência, tipo `notebook_page`), cifradas no cofre, vistas ao lado do texto | `routers/media.py` (`/studies/{id}/media`), `StudyView.vue` |
| Validade das fotos | A foto expira algum tempo depois de o estudo ser concluído, salvo "manter para sempre" (`keep_forever`) | `services/media_retention.py` |
| Revisão | Central de Revisão com Perguntas, Termos ocultos (destaques) e Conceitos (F0.11.08, tabela própria); mesmas notas fácil/médio/difícil, mesmos baldes e pesos | `services/review_service.py`, `concept_review_service.py`, `ReviewCard.vue` |
| Requisito | Imagens dependem do **cofre** configurado; sem cofre, a função aparece desativada com o aviso que já existe | `media_service.require_vault` |

**Oclusão de imagem:** o leitor cobre partes de uma imagem (um diagrama, um mapa, uma tabela fotografada) com
retângulos; cada retângulo vira um cartão. Na revisão, a imagem aparece com as áreas cobertas e uma delas destacada
("o que está aqui?"); ao revelar, a área destacada se abre.

---

## 2. User Stories

### US1 — Criar cartões sobre uma imagem do estudo (P1)

**Acceptance**:
1. No painel **"Folha original"** do estudo (só o dono), cada imagem ganha **"Criar cartões nesta imagem"**. Também dá
   para **adicionar uma imagem** ao estudo ali (o mesmo envio de foto que já existe), para quem quer só um diagrama.
2. O editor mostra a imagem com uma camada **SVG** por cima: arrastar desenha um retângulo; cada retângulo tem uma
   **resposta** opcional (texto curto, ex.: "Ventrículo esquerdo"); dá para mover, redimensionar, apagar e desfazer.
   No celular funciona por toque (arrastar com o dedo).
3. **Salvar** grava os retângulos em coordenadas **relativas** (0–1 da largura e altura), então valem em qualquer tamanho
   de tela. Abrir de novo mostra os retângulos salvos para editar.
4. Ao salvar cartões numa foto, ela passa a **"manter para sempre"** (não expira mais); o aviso diz isso. Apagar a imagem
   apaga os cartões dela (com o aviso de quantos cartões vão junto).

### US2 — Revisar (P1)

**Acceptance**:
1. Na **Central de Revisão**, um tipo novo: **"Imagens"**, ao lado de Perguntas, Termos ocultos e Conceitos (filtro,
   contagens e baldes como os outros). Em "Todos", os cartões de imagem entram na fila junto.
2. O cartão mostra a imagem com **todas as áreas cobertas** e a área perguntada **destacada**; "Revelar" abre só ela e
   mostra a resposta escrita, se houver. Notas fácil/médio/difícil com o mesmo peso e os mesmos baldes.
3. A imagem do cartão vem do endereço protegido que já existe (`/api/media/{id}/content`); nunca vai para outro lugar.

### Edge Cases

- Retângulo minúsculo (menos de 1% de lado) ou fora da imagem: recortado aos limites; minúsculo é recusado.
- Até **50** retângulos por imagem.
- Cofre trancado ou ausente: editor e cartão mostram o aviso do cofre; os cartões continuam guardados.
- Estudo na lixeira: cartões fora da revisão (como os outros tipos); voltam com o estudo.
- Imagem de outro leitor, ou estudo compartilhado comigo: não posso criar cartões nela (404).
- Editar retângulos de um cartão já revisado: mudar posição ou resposta mantém o histórico; apagar o retângulo apaga o
  cartão.
- Desligar "manter para sempre" numa foto com cartões: recusado (409), com o aviso de apagar os cartões antes.

---

## 3. Requirements

- **FR-001**: Migração `0041`: tabela `image_occlusion_cards` (`user_id`, `study_id` CASCADE, `media_id` CASCADE,
  `x`, `y`, `width`, `height` reais entre 0 e 1, `label` até 200 caracteres, `position`, campos de revisão iguais aos de
  `concept_reviews`).
- **FR-002**: `services/image_occlusion_service.py`: listar e salvar os retângulos de uma imagem (substituição em lote
  que mantém o histórico pelos ids), validar limites, ligar `keep_forever`; cartões, baldes e nota para a revisão.
- **FR-003**: Rotas: `GET`/`PUT /api/studies/{id}/media/{media_id}/occlusions`; na revisão, `kind=image` em
  `/review/stats` e `/review/items`, e `POST /review/images/{card_id}/record`.
- **FR-004**: Frontend: `ImageOcclusionEditor.vue` (SVG, mouse, toque e teclado: Delete apaga, setas movem),
  botão no painel "Folha original"; "Imagens" no filtro da revisão; `ReviewCard.vue` com o modo imagem.
- **FR-005**: Versão `0.12.0-alpha.6` e F0.12.06 marcada na linha do tempo.

## 4. Success Criteria

- **SC-001**: Testes: salvar/listar/editar/apagar retângulos; limites e recorte; 50 no máximo; `keep_forever` ligado;
  imagem apagada leva os cartões; isolamento (outro leitor 404); revisão (itens, baldes, nota, lixeira fora, filtro
  "Todos" inclui imagens); migração sobe e desce em banco descartável.
- **SC-002**: Navegador (dados fictícios, imagem sintética gerada no teste): desenhar 3 áreas, salvar, revisar uma; em
  375 px por toque; contraste nos 10 temas.
- **SC-003**: Testes novos e vizinhos; build; versão `alpha.6`; commit; levar ao `main`. A migração no banco ativo fica
  para quando o serviço for atualizado (procedimento dos 4 comandos).

## 5. Fora do escopo

- Formas além do retângulo (elipse, polígono, desenho livre).
- Modo "esconder uma, mostrar as outras" (fica para depois se fizer falta; o modo entregue é o de "todas cobertas").
- Oclusão em imagens fora de um estudo (capa, avatar) e importação de pacotes de oclusão de outros programas.
- Agrupar várias áreas num mesmo cartão.
