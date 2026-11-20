# Ferramenta de caixas e linhas (F-DI-13.01)

Ferramenta local para anotar páginas de caderno: caixas de linha sobre a foto, texto por linha (`line_id`),
fórmulas entre `$…$` e 2ª passada. Spec: [`specs/002-ferramenta-caixas-linhas`](../../specs/002-ferramenta-caixas-linhas/spec.md).
Roda só no seu computador (`127.0.0.1`); fotos, imagens e anotações ficam em `dataset/`, fora do Git.

## Uso em 4 passos (a partir de `document-intelligence/`)

1. **Fotos:** coloque as fotos originais do celular em `dataset/raw/exp-027/fotos/` (qualquer nome, sem converter
   nem recortar). Só abre a foto cujo SHA-256 bate com o registrado pelo EXP-027
   (`experiments/EXP-027-analise-50-paginas/splits/pages-sha256.json`).
2. **Preparar** (ambiente do motor do produto; cria a imagem de trabalho e as caixas iniciais do motor; retomável):

   ```powershell
   ..\caderno-leitura-0.1\motor\.venv\Scripts\python.exe -m tools.anotar.prepare
   ```

   No fim aparece um resumo: fotos encontradas, registradas, não registradas e páginas que faltam.
3. **Abrir a ferramenta:**

   ```powershell
   uv run python -m tools.anotar.server
   ```

   e abrir http://127.0.0.1:8766/ no navegador.
4. **Anotar** cada página em três etapas (abas no alto):
   1. **Caixas:** apague as falsas (`Delete`), ajuste as cortadas (arraste um canto), desenhe as que faltam
      (arraste na foto), confira a ordem e marque **Caixas prontas**.
   2. **1ª passada:** corrija o rascunho de cada linha olhando o recorte e aperte `Enter`. `Ctrl+M` envolve a
      seleção em `$…$`. Para usar o rascunho de outro sistema, cole o texto em "Importar rascunho de página".
   3. **2ª passada** (teste congelado e `dev-val`): modo **revisão** (vê a 1ª) ou **cego** (campo vazio).

A gravação é automática a cada linha confirmada (e `Ctrl+S`). O tempo ativo por etapa aparece no alto e fica
gravado no arquivo (pausa depois de 60 s parado).

## Onde ficam os dados

| O quê | Onde |
| :--- | :--- |
| Anotações `pNN.json` (`di-annotation/1`) e a versão anterior `pNN.prev.json` | `dataset/raw/anotacao/` |
| Imagem de trabalho, caixas do motor, índice | `dataset/processed/anotacao/` |

Numa worktree, aponte para os dados do checkout principal com `ANOTAR_DATA_ROOT` (e, se preciso,
`ANOTAR_MOTOR_DIR` para o motor).

## Regras de integridade (o servidor confere ao gravar)

* Schema [`di-annotation-1.schema.json`](./schema/di-annotation-1.schema.json); documento inválido não é gravado.
* `line_id` nunca reaproveitado (`next_line_id` só cresce); ordem 1..n; polígono dentro da imagem.
* `$` em número par em cada linha (`\$` é cifrão comum); texto confirmado não pode ser vazio (use `[?]`).
* Hash da foto conferido; `content_sha256` do conteúdo; versão para evitar sobrescrever outra aba.
