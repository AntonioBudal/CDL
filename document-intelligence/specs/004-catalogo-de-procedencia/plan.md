# Plano técnico: F-DI-13.03 — Catálogo de procedência (E2)

**Spec:** [spec.md](./spec.md) · **Data:** 2026-11-22 · **Status:** `IMPLEMENTED`

## Contexto técnico

* Python do subprojeto (`uv`), `sqlite3` da biblioteca padrão.
* **Dependência nova proposta: Pillow** (licença MIT-CMU/HPND, sem pesos nem modelo), para recodificar linhas,
  ler dimensões e calcular o *hash* perceptivo. Hoje o Pillow só existe no ambiente do motor; trazê-lo para o
  subprojeto evita rodar o catálogo num ambiente alheio. Registro em `docs/models-and-licensing.md`.
* Código em `tools/catalogo/` (ferramenta, não produto, como `tools/anotar/`); testes em `tests/tools/`.

## Esquema (SQLite)

| Tabela | Campos principais |
| :--- | :--- |
| `sources` | `source_id`, nome, endereço, licença e condições padrão, situação padrão, forma de acesso (`api`, `download`, `scrape`, `blocked`), hash dos termos |
| `terms` | hash, fonte, endereço, data, caminho da cópia |
| `items` | `item_id` (`fonte:id_nativo`), fonte, endereço, autor/titular, licença, condições, situação e motivo, idioma, época, tipo de escrita, escritor, divisão oficial, tipo de transcrição, transcrição, data e meio de aquisição |
| `files` | `sha256`, tipo (linha, página, xml, termos), bytes, formato, largura, altura, `phash` |
| `item_files` | item, arquivo, papel (`linha`, `pagina_origem`…) |
| `reviews` | escopo (fonte/item), alvo, de → para, motivo, evidência, data |
| `blocklist` | tipo (`sha256`, `url`, `item_id`), valor, motivo, data |
| `training_runs` | `run_id`, finalidade (`experimento`/`produto`), receita, commit, semente, data, contaminado (e por quê) |
| `run_items` | ciclo, item, hash, situação e licença no momento |
| `schema_version` | versão do esquema (migração simples por número) |

## Decisões

1. **Formato de linha padrão:** cinza, 64 px de altura, **PNG** (1 canal). *Revisto na execução*: o WebP sem
   perda no modo mais compacto custava 164 ms por linha contra 2,7 ms do PNG, com só ~15 % menos espaço
   (80 linhas reais). Na importação real a média ficou em **~51 KB por linha** (linhas largas do HTR-United):
   1,5 milhão de linhas passariam do teto de `linhas/`; os grupos do EXP-031P (~325 mil linhas) cabem com
   folga (~16 GB). O formato e o teto são revistos na E4. O endereço de origem fica registrado para rebaixar em resolução
   maior se um dia for preciso; o original só é guardado quando a fonte não tem endereço estável.
2. **Pendente não baixa arquivo** — só metadados; quando a fonte é aprovada, o próximo lote baixa.
3. **Apagar = arquivo fora do disco + registro mantido** (item `REJECTED`, hash e endereço bloqueados): o
   histórico explica por que o item sumiu e impede que volte.
4. **Contaminação é derivada dos registros:** rejeitar um item marca, na mesma transação, todo ciclo em
   `run_items` que o contém.
5. **Situação no momento do ciclo** fica copiada em `run_items`: a conferência compara com a atual.
6. **Tetos por pasta** (estratégia §7): `linhas/` 45 GB, `originais/` 30 GB, `modelos/` 10 GB, `trabalho/` 10 GB,
   `catalogo/` 1 GB, `pendentes/` 2 GB; total 100 GB.
7. **Importador de exemplo:** as amostras aprovadas do EXP-043 entram pelo mesmo caminho que os conectores da E4
   vão usar (API Python `catalog.ingest_line(...)`).

## Riscos

| Risco | Mitigação |
| :--- | :--- |
| SQLite corromper | modo WAL, transações curtas, cópia do arquivo antes de migração de esquema |
| Apagar arquivo usado por outro item | só apaga arquivo sem outra referência em `item_files` (teste) |
| Esquecer de registrar um ciclo | o treino (EXP-031P em diante) só recebe a lista de itens **pelo** catálogo |
| Espaço medido errado | uso calculado pelo disco, não pelo banco; conferência no relatório |
