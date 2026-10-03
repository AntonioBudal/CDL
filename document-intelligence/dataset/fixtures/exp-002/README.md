# Fixtures do EXP-002 — Páginas Sintéticas de Caderno

Insumos para gerar páginas de caderno sintéticas com geometria conhecida (linhas e blocos). As páginas geradas
ficam em `dataset/processed/exp-002/` (fora do Git) e são regeneráveis a partir destes arquivos e das seeds.

## Fontes manuscritas (todas SIL Open Font License 1.1, `LICENSE STATUS: VERIFIED` em 2026-10-02)

| Arquivo | Origem | SHA-256 |
| :--- | :--- | :--- |
| `fonts/Caveat-Regular.ttf` | `googlefonts/caveat` @ `59745e818ef7973e11e70cb1358d0e902b56c5fc` | `7af58d70e539c9195cc328617a68c9961ed804a4404b0b818989ba7c013e8776` |
| `fonts/IndieFlower-Regular.ttf` | `google/fonts` @ `a0e3dbcdc3a3ecfafff3f071159ae0221628922d` | `ccc94b22b156e9c5dfe50fd051f01b097600b252c24473e624bb43a143140a94` |
| `fonts/Kalam-Regular.ttf` | idem | `57cecb63d4608019371954274ae1d8c397764debd5b19d4a33c1efa4dc923c0b` |
| `fonts/PatrickHand-Regular.ttf` | idem | `0f173b3e6cb6d1af25babf7f0057c5ac4ee11f9992b0469bb817e967ef4ad0fc` |
| `fonts/ShadowsIntoLight.ttf` | idem | `1347863151acdc00fa281daaba1a3543dbce5870b55f9cf7479a15bb84007681` |

O texto de cada licença acompanha as fontes (`fonts/OFL-*.txt`). Todas têm glifos para `á é í ó ú â ê ô ã õ à ç`,
suas maiúsculas, dígitos e a pontuação exigida (conferido com fontTools).

## Manifestos (gerados por `experiments/EXP-002/harness/generate.py`)

| Arquivo | Páginas | Linhas | Uso |
| :--- | ---: | ---: | :--- |
| `dev-manifest.json` | 30 (10 por nível, seeds 10000+) | 589 | **só** calibração do baseline clássico e das regras de blocos |
| `test-manifest.json` | 180 (60 por nível, seeds 20000+) | 3.548 | avaliação congelada; nunca usado para ajuste |
| `large-manifest.json` | 10 (nível leve, ~12 MP, seeds 30000+) | 187 | caso de borda de memória e tempo |

Cada página traz SHA-256 da imagem, nível e parâmetros de degradação, fonte, cantos da folha, linhas (bbox,
polígono, bloco, texto fictício), blocos (`title`, `paragraph`, `margin_note`, `graphic_box`) e regiões "ignorar"
(diagramas). As imagens são regeneráveis; os SHA-256 valem para Pillow 12.3.0, OpenCV 5.0.0 e NumPy 2.5.3.

Nenhum texto do acervo do usuário ou de cadernos reais entra aqui.
