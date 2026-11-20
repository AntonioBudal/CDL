# Especificação: F-DI-13.01 — Ferramenta de caixas e linhas

* **Feature:** `002-ferramenta-caixas-linhas` (item **F-DI-13.01** do [roadmap 0.13](../../docs/replanejamento-0.13/05-roadmaps.md))
* **Criada em:** 2026-11-20
* **Status:** `IMPLEMENTED` (aprovada pelo usuário em 2026-11-20; SC-002 a SC-004 conferidas; SC-001 espera as
  fotos reais)
* **Tipo:** feature utilitária do Document Intelligence (não é experimento; não baixa modelos; não entra no produto)
* **Origem:** épico 0.13-0 "Régua limpa"; evolução da ferramenta de transcrição do
  [EXP-027](../../experiments/EXP-027-analise-50-paginas/report.md) (`harness/transcribe_server.py`)
* **Próximo item que depende dela:** EXP-028A (caixas reais + 2ª passada nas 20 páginas de teste e 10 de `dev-val`)

---

## 1. Por que agora

O EXP-027 mediu CER de 56 % nas 51 páginas reais, mas só em nível de página: a referência é um texto corrido por
página, sem caixas. Sem saber **onde** está cada linha na foto, não dá para separar o erro do detector (linha
perdida ou cortada) do erro do leitor (linha vista e lida errado), nem treinar o leitor com pares
recorte ↔ texto. Todo o 0.13 e o 0.14 dependem desses pares.

A revisão crítica externa (07-plano-revisado, ponto 4) mostrou que a ferramenta do EXP-027 não basta: ela só
mostra as caixas que o motor achou, e nas páginas ruins o motor perde até metade das linhas. É preciso **criar e
ajustar caixas** e separar a anotação de caixas da transcrição.

## 2. O que a ferramenta faz (em uma frase cada)

* **Mostra a foto da página** com as caixas de linha que o motor achou, para conferir de relance o que falta.
* **Deixa ajustar, criar e apagar caixas** de linha (4 cantos, para acompanhar linhas inclinadas).
* **Mostra o recorte de cada linha acima do campo de texto**, já preenchido com um rascunho, para corrigir só o
  que está errado e apertar `Enter` para ir à próxima.
* **Marca fórmulas com `$…$`** por atalho, e recusa salvar uma linha com `$` desequilibrado.
* **Faz uma 2ª passada** sobre a mesma página, guardando o texto das duas passadas separados (para medir a
  divergência humana no EXP-028A), em modo revisão (vê a 1ª) ou cego (campo vazio).
* **Exporta um JSON por página** validado por schema, com o hash da foto e o hash do próprio conteúdo.

## 3. Histórias de uso

### História 1 — Caixas de linha certas (P1)

O autor abre uma página, vê as caixas do motor sobre a foto, apaga as falsas, ajusta as cortadas e desenha as
que faltam, até cada linha escrita ter uma caixa.

**Aceite:**
1. As caixas iniciais vêm da detecção do motor do produto na foto original (mesmo detector e parâmetros do
   `caderno-leitura-0.1/motor/config.json`), cada uma com origem `motor`.
2. Criar caixa: arrastar na foto. Ajustar: arrastar um canto (4 cantos livres) ou a caixa inteira. Apagar:
   tecla `Delete`. Cada caixa guarda a origem (`motor`, `ajustada`, `criada`).
3. A ordem de leitura começa de cima para baixo e pode ser trocada (subir/descer a linha na lista).
4. Zoom e arrasto da foto funcionam numa foto de celular inteira (12 MP) sem travar.

### História 2 — Texto por linha com rascunho (P1)

Com as caixas prontas, o autor percorre as linhas: vê o recorte, corrige o rascunho, aperta `Enter`.

**Aceite:**
1. Cada linha tem um `line_id` estável (`L001`, `L002`…) que **nunca é reaproveitado**, mesmo se a caixa for
   apagada; é por ele que treino, teste e correções futuras se referem à linha.
2. O rascunho de cada linha vem do texto que o motor leu naquela caixa; opcionalmente, de um rascunho de página
   importado (texto com uma linha por linha do papel, distribuído na ordem das caixas; o que sobrar fica numa
   área "sobras" para colar à mão).
3. Quando há rascunho importado, as palavras em que motor e rascunho discordam aparecem destacadas (mitigação
   do risco R5: alucinação do professor virar verdade).
4. Atalho para envolver a seleção em `$…$`; a linha com número ímpar de `$` (sem contar `\$`) não é salva.
5. A regra de transcrição fica visível na tela: **escrever o que está no papel** (abreviações como estão, sem
   corrigir ortografia, riscos ignorados).

### História 3 — 2ª passada (P1)

Para o teste congelado e o `dev-val`, cada página é conferida duas vezes.

**Aceite:**
1. A 2ª passada é um modo da mesma página: em **revisão** o campo vem com o texto da 1ª passada; em **cego** vem
   vazio. O modo fica gravado na linha.
2. O texto das duas passadas é guardado separado; a 1ª passada não é sobrescrita pela 2ª.
3. A lista de páginas mostra o estado de cada uma: caixas prontas, 1ª passada, 2ª passada.

### História 4 — Exportação confiável (P1)

**Aceite:**
1. Um arquivo `pNN.json` por página, no schema `di-annotation/1` (§5), validado antes de gravar; documento
   inválido não é gravado e a tela diz por quê.
2. O arquivo traz o SHA-256 da foto, conferido contra `splits/pages-sha256.json` do EXP-027: foto com hash
   diferente do registrado não abre (garante que é a mesma página do teste congelado).
3. O arquivo traz `content_sha256`, o hash do próprio conteúdo canônico; recalcular dá o mesmo valor.
4. A gravação é atômica (arquivo temporário + troca), e a versão anterior fica como `pNN.prev.json`.
5. O tempo ativo de edição por passada é medido (pausa depois de 60 s sem interação) e gravado.

### Casos-limite

* Foto HEIC: convertida antes, como no EXP-027 (o navegador não abre HEIC).
* Página sem nenhuma caixa do motor: abre só com a foto, para desenhar tudo à mão.
* Duas abas abertas na mesma página: a gravação com versão desatualizada é recusada (conflito), sem perder a
  outra.
* Linha em branco de propósito (pauta vazia dentro de uma caixa): a caixa deve ser apagada; texto vazio não é
  aceito numa caixa marcada como pronta.

## 4. Requisitos

* **FR-001** Servidor local só em `127.0.0.1`, biblioteca padrão do Python, sem rede externa; a página usa só
  HTML/JS/CSS locais (sem CDN).
* **FR-002** Preparação por script, rodado no ambiente do motor: foto orientada pelo EXIF em JPEG de trabalho e
  caixas + texto do motor por página, tudo em `dataset/processed/anotacao/` (fora do Git).
* **FR-003** Editor de caixas de 4 cantos com origem por caixa; ordem de leitura editável.
* **FR-004** Texto por `line_id` estável, rascunho do motor ou importado, destaque de divergência, `$…$`.
* **FR-005** 1ª e 2ª passada (revisão ou cega) guardadas separadamente.
* **FR-006** Schema `di-annotation/1` em `tools/anotar/schema/`, validação no servidor antes de gravar,
  hashes da foto e do conteúdo, gravação atômica, conflito de versão.
* **FR-007** Tempo ativo por passada gravado no arquivo.
* **FR-008** Recusa de caminhos fora da pasta de dados (nada de `../`), e de páginas sem hash conferido.

## 5. Formato `di-annotation/1` (resumo; o schema é a fonte)

```json
{
  "schema": "di-annotation/1",
  "page_id": "p10",
  "image": { "sha256": "…", "width": 3000, "height": 4000 },
  "split": "test | dev-val | dev-train | sem-split",
  "draft_source": "motor | importado:<rótulo>",
  "next_line_id": 34,
  "lines": [
    {
      "line_id": "L001",
      "order": 1,
      "polygon": [[x, y], [x, y], [x, y], [x, y]],
      "box_origin": "motor | ajustada | criada",
      "motor_text": "texto que o motor leu nesta caixa ou null",
      "pass1": { "text": "…", "at": "2026-11-20T12:00:00Z" },
      "pass2": { "text": "…", "at": "…", "mode": "revisao | cego" }
    }
  ],
  "status": { "boxes_done": true, "pass1_done": true, "pass2_done": false },
  "seconds": { "boxes": 120, "pass1": 380, "pass2": 0 },
  "version": 7,
  "updated_at": "…",
  "content_sha256": "…"
}
```

Coordenadas em pixels da **imagem de trabalho**: a foto orientada pelo EXIF, reduzida só quando o lado maior passa
de 6000 px (fator em `image.scale`). Polígono em sentido horário a partir do canto superior esquerdo. Cada linha
guarda também o rascunho usado (`draft`), para medir depois quanto a revisão humana mudou o rascunho.

## 5.1 Onde ficam os dados

| O quê | Onde | Git |
| :--- | :--- | :---: |
| Fotos originais | `dataset/raw/exp-027/fotos/` (já previsto pelo EXP-027) | não |
| Foto de trabalho e caixas do motor | `dataset/processed/anotacao/` | não |
| Anotações `pNN.json` | `dataset/raw/anotacao/` (é dado do autor, como a referência) | não |
| Código, schema, testes | `tools/anotar/`, `tests/tools/` | sim |

## 6. Critérios de sucesso

* **SC-001** (o do roadmap) O autor anota **1 página real completa** (caixas + 1ª passada) e exporta em
  **≤ 10 min** de tempo ativo, medido pela própria ferramenta; o arquivo passa no schema.
* **SC-002** Testes automatizados com páginas **fictícias** (geradas por script): schema válido e inválido,
  `$` desequilibrado, `line_id` nunca reaproveitado, hash de conteúdo estável, foto com hash errado recusada,
  conflito de versão, caminho com `../` recusado, servidor só em `127.0.0.1`.
* **SC-003** `uv run pytest` e `uv run ruff check .` verdes no subprojeto.
* **SC-004** Conferência no navegador com página fictícia: criar, ajustar e apagar caixa, ordem, `Enter`,
  `$…$`, 2ª passada cega e revisão, gravar e reabrir igual.

## 7. Fora do escopo

* Rodar o professor VLM (EXP-029) ou anotar as páginas de verdade (EXP-028A e Dados-13.1).
* Polígonos com mais de 4 pontos, segmentação de palavras, zonas de página (0.15/0.16).
* Qualquer mudança no Leitorum ou no LDF; integração com o produto (CR-F13.1, no 0.14.5).

## 8. O que depende do usuário

* **Para a SC-001 (e para todo o épico 0):** as fotos originais das páginas de volta em
  `dataset/raw/exp-027/fotos/`. A pasta está vazia hoje; o EXP-027 registrou os hashes das fotos que usou, e a
  ferramenta só abre a foto cujo hash bate. Pode ser feito em paralelo à construção.
* Uma página de cerca de 10 minutos de anotação no fim, para medir a SC-001.
