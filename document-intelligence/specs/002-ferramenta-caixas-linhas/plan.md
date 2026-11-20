# Plano técnico: F-DI-13.01 — Ferramenta de caixas e linhas

**Spec:** [spec.md](./spec.md) · **Data:** 2026-11-20 · **Status:** `IMPLEMENTED`

## Contexto técnico

* Python 3.11+ do subprojeto (`uv`), **sem dependência nova** no `pyproject.toml`: o servidor usa só a
  biblioteca padrão; `jsonschema` já é dependência.
* Interface: um HTML com JS e CSS locais (canvas 2D), no padrão do `tool/index.html` do EXP-027, sem framework e
  sem CDN.
* Preparação das imagens e das caixas: script rodado no ambiente do motor do produto
  (`caderno-leitura-0.1/motor/.venv`, que já tem Pillow e OpenCV), só leitura, como o `run_motor.py` do EXP-027.
  Nada fora de `document-intelligence/` é alterado.
* Recortes de linha feitos no navegador a partir da foto de trabalho (sem servidor de imagem).

## Verificação das regras

| Regra | Situação |
| :--- | :--- |
| Escopo só em `document-intelligence/` | OK: código em `tools/anotar/`, testes em `tests/tools/`; o motor é só executado |
| Privacidade | OK: dados em `dataset/` (fora do Git); testes com páginas fictícias; nenhuma imagem ou texto no chat |
| Local e sem custo | OK: `127.0.0.1`, sem rede, sem dependência nova |
| Experimento ≠ feature | OK: ferramenta de anotação, não toca no pipeline nem em `src/` |
| Teste congelado | A ferramenta grava, não mede; o uso das páginas de teste é regido pelo EXP-028A |

## Estrutura

```text
document-intelligence/
├── tools/anotar/
│   ├── README.md            # uso em 5 passos
│   ├── paths.py             # raízes de dados (variável ANOTAR_DATA_ROOT para rodar em worktree)
│   ├── prepare.py           # (ambiente do motor) foto → JPEG orientado + caixas/texto do motor
│   ├── store.py             # ler/validar/gravar pNN.json: schema, hashes, versão, gravação atômica
│   ├── server.py            # HTTP local: lista de páginas, imagem, GET/PUT da anotação
│   ├── schema/di-annotation-1.schema.json
│   └── static/              # index.html, app.js, style.css
└── tests/tools/
    ├── synthetic.py         # páginas fictícias (fundo pautado + "linhas" desenhadas sem texto real)
    └── test_anotar.py
```

## Decisões

1. **Caixa de 4 cantos livres, começando como retângulo.** O motor devolve retângulos; linhas de caderno
   inclinam. Quatro cantos cobrem a inclinação sem a complexidade de polígonos livres (que ficam para depois, se
   o EXP-028B mostrar necessidade).
2. **`line_id` com contador por página (`next_line_id`).** Garante que um id apagado nunca volta; é a base das
   divisões de treino e teste por linha.
3. **Servidor valida, o navegador só edita.** Toda regra de integridade (schema, `$`, hashes, versão) roda no
   `store.py`, que é testável sem navegador.
4. **Hash da foto conferido contra o EXP-027.** Assim, a página `p10` anotada é comprovadamente a mesma `p10`
   do teste congelado.
5. **Rascunho importado distribuído em ordem**, com "sobras" visíveis, em vez de alinhamento automático: o texto
   de página do professor externo não tem caixas; alinhar automaticamente é um problema do EXP-028A, não da
   ferramenta.
6. **Tempo ativo medido no navegador** (sem interação por 60 s pausa o relógio) e somado no servidor a cada
   gravação; é a medida da SC-001.
7. **Gravação atômica + `version`:** o `PUT` traz a versão que leu; se o arquivo já estiver em outra versão,
   responde 409 e a tela avisa.

## Interface (API local)

| Rota | Faz |
| :--- | :--- |
| `GET /api/pages` | lista `pNN` com split, hash conferido, estado e tempos |
| `GET /api/pages/{id}` | anotação atual, ou a inicial montada das caixas do motor |
| `GET /img/{id}.jpg` | foto de trabalho (só se o hash conferiu) |
| `PUT /api/pages/{id}` | valida e grava; 422 com o motivo, 409 em conflito |
| `POST /api/pages/{id}/draft` | importa rascunho de página (texto), devolve a distribuição e as sobras |

## Riscos

| Risco | Mitigação |
| :--- | :--- |
| Foto de 12 MP pesada no canvas | JPEG de trabalho com lado maior de até 4000 px; recorte por `drawImage` só da área visível |
| Fotos não voltarem ao projeto | a construção e os testes não dependem delas; só a SC-001 espera |
| Distribuição do rascunho desalinhar | sobras visíveis e destaque de divergência; o EXP-028A mede o efeito |
| Tempo por página acima de 10 min | anotar o tempo por etapa (caixas × texto) para saber onde está o gargalo |
