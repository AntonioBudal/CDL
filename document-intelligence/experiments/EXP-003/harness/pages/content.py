"""Texto fictício em PT-BR para as páginas sintéticas (títulos, parágrafos, notas e rótulos).

Todo o conteúdo é inventado para o experimento; nada vem de cadernos ou do acervo do usuário.
"""

from __future__ import annotations

import random

# Alfabeto mínimo exigido (mesmo do EXP-001) — coberto pelo conjunto de teste, conferido nos testes.
REQUIRED_CHARS = "áéíóúâêôãõàçÁÉÍÓÚÂÊÔÃÕÀÇ" + ',.:-"()?' + "0123456789"

TEMAS = [
    "a lógica formal",
    "a função contínua",
    "o método científico",
    "a equação linear",
    "o raciocínio dedutivo",
    "a razão áurea",
    "o número complexo",
    "a análise sintática",
    "o período histórico",
    "a órbita elíptica",
    "a célula vegetal",
    "o sistema nervoso",
    "a tabela periódica",
    "a pressão atmosférica",
    "o pêndulo simples",
    "o triângulo retângulo",
    "a frequência de onda",
    "o fenômeno óptico",
    "o gênero textual",
    "as funções inversas",
    "as equações químicas",
    "as noções básicas",
    "o princípio da inércia",
    "a fórmula útil",
    "o binômio perfeito",
    "a distância média",
    "o conteúdo da prova",
    "a ciência política",
    "as três hipóteses",
    "o índice remissivo",
    "a revolução industrial",
    "a colonização",
    "o ciclo da água",
    "a fotossíntese",
    "a mitose",
    "a constituição",
    "o romantismo",
]
TITULOS = [
    "Aula {n}: {Tema}",
    "Capítulo {n} - {Tema}",
    "Resumo: {Tema}",
    "Revisão de {tema}",
    "{Tema} (parte {n})",
    "Exercícios sobre {tema}",
    "Introdução à {tema_sem_artigo}",
    "Questões de {tema}",
    "Fichamento: {Tema}",
]
SUJEITOS = [
    "O professor",
    "A autora",
    "O texto",
    "O exemplo",
    "A definição",
    "O capítulo",
    "A turma",
    "O exercício",
    "A hipótese",
    "O gráfico",
    "A monitora",
    "O livro",
]
VERBOS = [
    "explica",
    "discute",
    "compara",
    "resume",
    "demonstra",
    "questiona",
    "relaciona",
    "apresenta",
    "revisa",
    "critica",
    "ilustra",
    "retoma",
]
COMPLEMENTOS = [
    "com exemplos práticos",
    "de forma resumida",
    "a partir da página {n}",
    "em três etapas",
    "usando um gráfico",
    "à luz da teoria",
    "sem rodeios",
    "com atenção aos detalhes",
    "na seção {n}.{m}",
    "(ver anexo {n})",
    "de modo crítico",
    "em {ano}",
]
CONECTIVOS = [
    "Além disso,",
    "Por outro lado,",
    "Em seguida,",
    "Portanto,",
    "Ou seja,",
    "Por exemplo,",
    "Em resumo,",
    "No entanto,",
    "Assim,",
    "Também",
]
PERGUNTAS = [
    "Por quê?",
    "Qual é a relação com {tema}?",
    "Isso vale sempre?",
    "Como medir isso?",
    "O que muda em {ano}?",
]
NOTAS = [
    "ver p. {n}",
    "revisar!",
    "dúvida",
    "importante",
    "cf. cap. {n}",
    "(prova)",
    "atenção",
    "exemplo {n}",
    "definição?",
    "ok",
    "rever",
    "nota {n}",
    "pergunta",
    "conferir",
    "ótimo",
]
ROTULOS = [
    "Calor",
    "Trabalho",
    "Energia",
    "Ação",
    "Reação",
    "Causa",
    "Efeito",
    "Estado",
    "Nação",
    "Força",
    "Massa",
    "Teoria",
    "Prática",
    "Hipótese",
    "Conclusão",
    "Célula",
    "Órgão",
    "Questão",
    "Razão",
    "Função",
]


def _fill(template: str, rng: random.Random) -> str:
    tema = rng.choice(TEMAS)
    sem_artigo = tema.split(" ", 1)[1] if " " in tema else tema
    return template.format(
        n=rng.randint(1, 29),
        m=rng.randint(1, 9),
        ano=rng.randint(1950, 2024),
        tema=tema,
        Tema=tema[0].upper() + tema[1:],
        tema_sem_artigo=sem_artigo,
    )


def title(rng: random.Random) -> str:
    return _fill(rng.choice(TITULOS), rng)


def sentence(rng: random.Random) -> str:
    kind = rng.random()
    if kind < 0.12:
        return _fill(rng.choice(PERGUNTAS), rng)
    start = rng.choice(CONECTIVOS) + " " if kind < 0.4 else ""
    subject = rng.choice(SUJEITOS)
    if start:
        subject = subject[0].lower() + subject[1:]
    body = (
        f"{subject} {rng.choice(VERBOS)} {rng.choice(TEMAS)} {_fill(rng.choice(COMPLEMENTOS), rng)}"
    )
    if rng.random() < 0.15:
        body += f': "{rng.choice(["não há atalho", "meça antes", "a dúvida ensina"])}"'
    return start + body + "."


def paragraph_words(rng: random.Random, sentences: int) -> list[str]:
    words: list[str] = []
    for _ in range(sentences):
        words.extend(sentence(rng).split())
    return words


def margin_note(rng: random.Random) -> str:
    return _fill(rng.choice(NOTAS), rng)


def diagram_labels(rng: random.Random, count: int) -> list[str]:
    return rng.sample(ROTULOS, count)
