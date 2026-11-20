# Plano técnico: F-DI-13.03 — Kit de coleta de páginas de várias pessoas

**Spec:** [spec.md](./spec.md) · **Data:** 2026-11-20 · **Status:** `DRAFT`

## Contexto técnico

* Python do subprojeto (`uv`), sem dependência nova. O tamanho das fotos é lido pelo Pillow **no ambiente do
  motor**, como no `register.py` atual; o comando roda lá (`..\caderno-leitura-0.1\motor\.venv\Scripts\python.exe
  -m tools.anotar.pessoas …`). Sem Pillow disponível, `registrar-fotos` recusa e explica.
* Documentos em Markdown em `docs/coleta/` (versionados: são modelos, sem dado de ninguém).

## Estrutura

```text
document-intelligence/
├── docs/coleta/
│   ├── termo-de-consentimento.md
│   └── guia-para-quem-participa.md
├── splits/                          # novo: registro versionado (só ids, datas, hashes)
│   ├── pessoas.json                 # wNN → data do termo, sha256 do termo, conjunto, situação
│   └── paginas.json                 # wNN-pNN → sha256, largura, altura, low_resolution
├── tools/anotar/pessoas.py          # adicionar, registrar-fotos, retirar, listar, conferir
└── tests/tools/test_pessoas.py
dataset/raw/pessoas/                 # fora do Git
└── wNN/{privado.json, termo/, fotos/, transcricoes/}
```

## Decisões

1. **Dois arquivos versionados, um privado por pessoa.** `privado.json` (nome, contato, observações) nunca sai
   de `dataset/raw/pessoas/wNN/`. O versionado tem uma lista fechada de campos, conferida por teste.
2. **Ids sequenciais, nunca reaproveitados:** `w01`, `w02`…; uma pessoa retirada mantém o id como `retirada`.
3. **Página `wNN-pMM`** em ordem de data do arquivo (EXIF, senão nome), como no EXP-027.
4. **Recusa de foto comprimida:** lado maior < 2000 px (uma foto de celular tem 3000–4000 px; mensageiros
   reduzem para ~1600). Limiar registrado no código e no guia.
5. **Retirada apaga** as pastas em `dataset/raw/pessoas/wNN/`, `dataset/raw/anotacao/wNN-*`,
   `dataset/processed/anotacao/{imagens,motor}/wNN-*` e as entradas de `paginas.json`; registra a emenda.
6. **O autor (`w00`)** é registrado a partir do `pages-sha256.json` do EXP-027 (20 páginas, 512 px), sem copiar
   imagens.

## Riscos

| Risco | Mitigação |
| :--- | :--- |
| Nome vazar para o Git | lista fechada de campos + teste que procura o nome fictício nos arquivos versionados |
| Retirada incompleta | teste que varre `dataset/` atrás do id depois de retirar |
| Termo mal entendido | linguagem simples, resumo em 5 tópicos no topo, revisão pelo usuário |
