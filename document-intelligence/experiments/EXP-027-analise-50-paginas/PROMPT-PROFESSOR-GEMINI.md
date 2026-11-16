# Prompt para o professor externo (Gemini) — transcrição das páginas de teste do EXP-027

Uso pelo usuário, fora do projeto, por decisão dele em 2026-11-16. A resposta do modelo é um **rascunho de
professor**, não a referência: entra na ferramenta de transcrição para ser conferida linha a linha contra o
caderno de papel, com 2ª passada nas páginas de teste. A resposta original fica guardada em
`dataset/raw/exp-027/gemini/` e é pontuada depois como sistema `gemini` (referência de "grande modelo
multimodal").

Ordem das imagens de teste: `p10 p11 p14 p15 p18 p20 p21 p22 p26 p27 p30 p31 p35 p36 p37 p38 p41 p44 p45 p46`.

---

## Prompt (copiar a partir daqui)

Você vai transcrever fotos de páginas de um caderno manuscrito em português. Vou enviar as imagens em lotes,
sempre na ordem desta lista de identificadores, e cada imagem recebe o próximo identificador ainda não usado:

p10, p11, p14, p15, p18, p20, p21, p22, p26, p27, p30, p31, p35, p36, p37, p38, p41, p44, p45, p46

Regras de saída, sem exceção:

1. Para cada imagem, comece um bloco com uma linha contendo só `=== pNN ===` (o identificador da vez).
2. Dentro do bloco, escreva **uma linha de saída por linha física escrita no caderno**, na ordem natural de
   leitura (de cima para baixo; numa página com colunas ou notas de margem, termine a coluna principal e depois
   as notas, na posição em que um leitor as leria). Numere cada linha no começo, no formato `01: `, `02: `, …
3. Transcreva **fielmente o que está escrito**: mantenha acentos, maiúsculas, pontuação, abreviações e os erros
   de ortografia do autor. Não corrija, não complete palavras cortadas, não resuma, não traduza, não reordene
   frases para fazer sentido.
4. Fórmulas, equações e símbolos matemáticos vão entre cifrões, em LaTeX simples: `$x^2 + 1$`, `$\frac{a}{b}$`,
   `$\int_0^1 f(x)\,dx$`, `$\alpha \leq \beta$`. Uma expressão matemática no meio de uma frase também vai entre
   cifrões. Se não tiver certeza do símbolo, use o LaTeX mais provável, sempre entre cifrões.
5. Um desenho, diagrama, tabela desenhada ou esquema que não seja texto vira uma linha contendo só `[figura]`.
   Texto legível dentro de um diagrama é transcrito como linhas normais logo depois de `[figura]`.
6. Um trecho que você não consegue ler vira `[?]` no lugar exato do trecho. Não invente palavras para
   preencher.
7. Texto riscado pelo autor: não transcreva. Texto sublinhado ou destacado: transcreva normalmente, sem marcação.
8. Não escreva nada além dos blocos: sem comentários, sem explicações, sem cabeçalhos extras, sem resumo no fim.
   Não use blocos de código. Responda em texto puro.

Exemplo do formato (conteúdo inventado):

=== p10 ===
01: Capítulo 3 — a leitura atenta
02: O autor defende que reler é pensar de novo
03: A área do círculo é $A = \pi r^2$ e a do quadrado $l^2$
04: [figura]
05: Pergunta: isso vale para textos curtos? [?] depois
=== p11 ===
01: ...

Se alguma imagem estiver ilegível por inteiro, escreva o bloco com uma única linha `01: [?]`.

Confirme que entendeu respondendo apenas "Pronto. Envie as imagens." e aguarde o primeiro lote.
