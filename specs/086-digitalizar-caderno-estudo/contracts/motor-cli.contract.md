# Contrato: Linha de Comando do Motor de Leitura

**Feature**: `086-digitalizar-caderno-estudo` | Pacote: `caderno-leitura-0.1/motor/leitorum_motor/`

O motor é chamado pelo backend sempre com `-I` (modo isolado: ignora `PYTHONPATH`, pasta atual e pacotes do
usuário), num processo novo por pedido. Ele não acessa a rede nem o banco e só lê a imagem recebida e os próprios
arquivos.

---

## `python -I -m leitorum_motor check`

Confere o ambiente: as bibliotecas importam, os modelos existem e o SHA-256 confere, e o leitor configurado tem
`license_status = VERIFIED`.

| Saída | Significado |
| :--- | :--- |
| código 0, `stdout` = `{"ok": true, "engine": {...}}` | pronto |
| código 3, `stdout` = `{"ok": false, "reason": "integrity_failed"}` | modelo ausente, SHA diferente ou licença não verificada |
| outro código / falha ao iniciar | backend trata como `not_installed` |

## `python -I -m leitorum_motor read --image <png> --out <json> [--config <json>]`

Lê uma página e grava o resultado `leitorum-motor/1` (ver [data-model.md §1](../data-model.md)) em `--out`.

| Código | Significado |
| :--- | :--- |
| 0 | leitura feita (pode ter zero linhas) |
| 2 | imagem ilegível pelo OpenCV |
| 3 | integridade dos modelos ou licença do leitor |
| outro | erro inesperado; `stderr` só com o tipo da exceção, sem texto lido |

`--config` é opcional e por padrão vale `motor/config.json` do pacote. Os testes usam esse parâmetro para
apontar um config de teste.

## `motor/config.json`

```json
{
  "reader": { "file": null, "sha256": "6f327246b50388f3c176ae304bd95767ea6dc0c9ae92153ef8cbe210b3c14884",
              "name": "PP-OCRv6 small", "license": "Apache-2.0", "license_status": "VERIFIED" },
  "detector": { "file": "PP-OCRv6_det_small.onnx",
                "sha256": "090f04abcd9d9a7498bc4ebf677e4cb9bdce1fe4197ddb7e529f1ef44e1ff94f" },
  "target": 80,
  "merge": { "v_overlap": 0.7, "max_gap": 1.0, "max_angle": 20.0 },
  "right_margin": 640,
  "low_confidence": 0.75
}
```

`reader.file = null` significa usar o modelo embutido no wheel do `rapidocr`. Um caminho relativo é resolvido a
partir da pasta `motor/`.

## Troca de leitor (FR-013)

Para trocar o leitor:
1. coloque o novo ONNX em `motor/models/`;
2. atualize em `reader` os campos `file`, `sha256`, `name`, `license` e `license_status`;
3. ajuste `low_confidence` se o novo leitor for calibrado de outro jeito.

Nenhuma mudança no backend, na API ou no frontend. O motor recusa um leitor com `license_status` diferente de
`VERIFIED` (NR-003).
