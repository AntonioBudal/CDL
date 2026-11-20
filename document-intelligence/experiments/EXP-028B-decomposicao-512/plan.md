# Plano: EXP-028B — De onde vem o erro: caixas ou leitura (em imagens de 512 px)

**Spec:** [spec.md](./spec.md) · **Data:** 2026-11-20 · **Status:** `DONE`

## Contexto técnico

* **Leitura** no ambiente do motor do produto (`caderno-leitura-0.1/motor/.venv`), só executado, nunca alterado:
  um script do experimento importa `leitorum_motor` e usa as mesmas peças do `PagePipeline.read` —
  `_detect`, `scale_factor`, `merge_lines`, `crop_line`, `prepare_line`, `_read` e `reading_order` — trocando
  só a origem das caixas. Assim a diferença entre A, B e C é só a caixa (e a ordem), nunca o leitor.
* **Medida** no ambiente do subprojeto (`uv`), com `align.levenshtein`/`textnorm` do EXP-027 (mesma normalização).
* Entradas: imagens de trabalho de 512 px (`processed/anotacao/imagens/`), anotações `di-annotation/1` (caixas
  e texto do autor), `test-manifest-v3-parcial.json` (as 4 páginas). Saídas em `processed/exp-028b/` (fora do
  Git) e um benchmark só com números.

## Estrutura

```text
experiments/EXP-028B-decomposicao-512/
├── spec.md, plan.md, tasks.md, report.md (no fim)
├── harness/
│   ├── read_boxes.py   # (ambiente do motor) leituras A, B, C → processed/exp-028b/{a,b,c}/pNN.json
│   └── decompose.py    # (uv) CER de página A/B/C, CER por linha em B, partes, custo da resolução
└── tests/test_exp028b.py  # imagem fictícia com caixas conhecidas; medida com textos fictícios
```

## Decisões

1. **Escala igual à do produto:** em B e C, a página é ampliada pelo mesmo `scale_factor`, calculado pela altura
   mediana das caixas do autor (como o produto faz com as dele), e as caixas são multiplicadas pelo mesmo fator.
2. **Polígono de 4 cantos do autor** vai direto para `crop_line` (o produto aceita polígono).
3. **Ordem do motor em C:** `reading_order` do produto aplicada às caixas do autor.
4. **CER de página** com a mesma conta do EXP-027/028A (texto da página normalizado; distância de caracteres).
5. **Sem semente:** tudo determinístico (ONNX em CPU, leitura gulosa); rodar duas vezes e conferir igualdade.

## Riscos

| Risco | Mitigação |
| :--- | :--- |
| Usar funções internas do motor (`_read`, `_detect`) | só leitura; o script verifica o hash do leitor (`verify`) e registra a versão do motor |
| Amostra pequena | relatório por página e por linha, sem extrapolar; DG-1 continua aberto |
| 512 px distorce a parte do leitor | H3 mede a distorção; conclusões separadas para 512 px |
