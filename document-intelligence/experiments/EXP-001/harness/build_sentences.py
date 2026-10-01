"""Gera as frases fictícias em PT-BR da camada sintética do EXP-001 (determinístico).

Uso: ``python build_sentences.py`` — grava ``dataset/fixtures/exp-001/sentences.json``.
Todo o texto é inventado para o experimento; nada vem de cadernos ou do acervo do usuário.
"""

from __future__ import annotations

import json
import random
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUT = ROOT / "dataset" / "fixtures" / "exp-001" / "sentences.json"
SCHEMA = "leitorum-di-sentences/1"
SEED = 1234
COUNT = 200
MAX_CHARS = 64

# Alfabeto mínimo exigido por experiments/EXP-001-context.md §3.
REQUIRED_CHARS = "áéíóúâêôãõàçÇ" + ',.:-"()?' + "0123456789"

TITULOS = [
    "ATENÇÃO", "REVISÃO", "CONCLUSÃO", "INTRODUÇÃO", "QUESTÕES", "EXERCÍCIO", "DEFINIÇÃO",
    "OBSERVAÇÃO", "RESUMO", "DÚVIDA",
]
TEMAS = [
    "a lógica formal", "a função contínua", "o método científico", "a equação linear",
    "o raciocínio dedutivo", "a razão áurea", "o número complexo", "a análise sintática",
    "o período histórico", "a órbita elíptica", "a célula vegetal", "o sistema nervoso",
    "a tabela periódica", "a pressão atmosférica", "o pêndulo simples", "o triângulo retângulo",
    "a frequência de onda", "o fenômeno óptico", "o gênero textual", "as funções inversas",
    "as equações químicas", "as noções básicas", "o princípio da inércia", "a fórmula útil",
    "o binômio perfeito", "a distância média", "o conteúdo da prova", "a ciência política",
    "as três hipóteses", "o índice remissivo",
]
PESSOAS = [
    "o professor Abelardo", "a monitora Cecília", "o tutor Zózimo", "a doutora Íris",
    "o colega Júlio", "a aluna Thaís", "o autor Quirino", "a bibliotecária Hortência",
    "o orientador Wálter", "a pesquisadora Ágata",
]
QUALIDADES = [
    "simples", "difícil", "essencial", "prática", "teórica", "útil", "básica", "avançada",
    "frágil", "sólida", "rápida", "ampla", "concisa", "rigorosa", "ambígua",
]
VERBOS = ["Revisar", "Estudar", "Resumir", "Comparar", "Anotar", "Reler", "Fichar", "Explicar"]
CITACOES = [
    "não há atalho", "a prática vem antes", "meça e só então conclua", "tudo começa na dúvida",
    "o exemplo ensina mais", "ninguém aprende às pressas", "a pergunta já é metade",
]
RAZOES = [
    "a hipótese não se sustenta", "o exemplo contradiz a regra", "faltou medir de novo",
    "a conclusão veio cedo demais", "o método é mais confiável", "a amostra é pequena",
]


def _titulo(rng: random.Random) -> str:
    return f"{rng.choice(TITULOS)}: {rng.choice(TEMAS)}."


def _capitulo(rng: random.Random) -> str:
    return f"Capítulo {rng.randint(1, 29)}: {rng.choice(TEMAS)}"


def _pergunta(rng: random.Random) -> str:
    return f"O que é {rng.choice(TEMAS)}?"


def _pagina(rng: random.Random) -> str:
    tema = rng.choice(TEMAS)
    pagina, secao = rng.randint(10, 480), rng.randint(1, 9)
    return f"{tema[0].upper()}{tema[1:]} - ver página {pagina} (seção {secao})."


def _citacao(rng: random.Random) -> str:
    return f'"{rng.choice(CITACOES).capitalize()}", disse {rng.choice(PESSOAS)}.'


def _exemplo(rng: random.Random) -> str:
    a, b = rng.randint(2, 60), rng.randint(2, 60)
    return f"Exemplo {rng.randint(1, 9)}: somar {a} e {b} dá {a + b}."


def _horario(rng: random.Random) -> str:
    return f"{rng.choice(VERBOS)} {rng.choice(TEMAS)} às {rng.randint(7, 22)}h, não à tarde."


def _porque(rng: random.Random) -> str:
    return f"Por quê? Porque {rng.choice(RAZOES)}."


def _ano(rng: random.Random) -> str:
    pessoa = rng.choice(PESSOAS)
    return f"Em {rng.randint(1950, 2024)}, {pessoa} estudou {rng.choice(TEMAS)}."


def _lista(rng: random.Random) -> str:
    q1, q2, q3 = rng.sample(QUALIDADES, 3)
    tema = rng.choice(TEMAS)
    return f"{tema[0].upper()}{tema[1:]}: {q1}, {q2} e {q3}."


def _questao(rng: random.Random) -> str:
    return f"Questão {rng.randint(1, 40)}: {rng.choice(TEMAS)} é {rng.choice(QUALIDADES)}?"


TEMPLATES = [
    _titulo, _capitulo, _pergunta, _pagina, _citacao, _exemplo, _horario, _porque, _ano, _lista,
    _questao,
]


def build_sentences(count: int = COUNT, seed: int = SEED) -> list[dict[str, str]]:
    """Devolve ``count`` frases únicas, em NFC, cobrindo ``REQUIRED_CHARS``."""
    rng = random.Random(seed)
    seen: set[str] = set()
    texts: list[str] = []
    attempts = 0
    while len(texts) < count:
        attempts += 1
        if attempts > count * 200:
            raise RuntimeError("Não foi possível gerar frases únicas suficientes.")
        # Rodízio pelas tentativas: um modelo de frase esgotado não trava os demais.
        template = TEMPLATES[attempts % len(TEMPLATES)]
        text = unicodedata.normalize("NFC", template(rng))
        if text in seen or len(text) > MAX_CHARS:
            continue
        seen.add(text)
        texts.append(text)

    missing = sorted(set(REQUIRED_CHARS) - set("".join(texts)))
    if missing:
        raise RuntimeError(f"Alfabeto exigido não coberto: {missing}")
    return [{"id": f"syn-{i:04d}", "text": text} for i, text in enumerate(texts, start=1)]


def render_document(count: int = COUNT, seed: int = SEED) -> str:
    document = {
        "schema": SCHEMA,
        "description": "Frases fictícias em PT-BR para a camada sintética do EXP-001.",
        "seed": seed,
        "required_chars": REQUIRED_CHARS,
        "sentences": build_sentences(count, seed),
    }
    return json.dumps(document, ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    DEFAULT_OUT.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_OUT.write_text(render_document(), encoding="utf-8", newline="\n")
    print(f"{COUNT} frases gravadas em {DEFAULT_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
