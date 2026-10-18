"""Correção lexical (EXP-011), com um léxico fictício."""

from lexicon import Corrector, LexiconParams, recase, strip_accents

WORDS = [
    ["de", 0.05],
    ["que", 0.04],
    ["não", 0.03],
    ["nao", 0.000001],
    ["educação", 0.001],
    ["casa", 0.002],
    ["cama", 0.0019],
    ["caso", 0.0018],
    ["escola", 0.001],
    ["sociedade", 0.0009],
]


def corrector(distance=1, min_length=3, size=1000):
    return Corrector(WORDS, LexiconParams(size=size, max_distance=distance, min_length=min_length))


def test_known_words_are_kept():
    assert corrector().correct_line("casa de escola") == "casa de escola"


def test_missing_accents_are_restored_with_the_most_frequent_form():
    fix = corrector(distance=0)
    assert fix.correct_word("educacao") == "educação"
    assert fix.correct_word("nao") == "nao"  # está no léxico (forma rara): mantida
    assert fix.correct_line("Educacao,") == "Educação,"


def test_close_misspellings_are_corrected_by_distance_then_frequency():
    fix = corrector(distance=1)
    assert fix.correct_word("escoia") == "escola"
    # casa, cama e caso a distância 1: vence a mais frequente
    assert fix.correct_word("casx") == "casa"
    assert corrector(distance=0).correct_word("escoia") == "escoia"


def test_distance_two_and_unknown_words():
    assert corrector(distance=2).correct_word("xociedadex") == "sociedade"
    assert corrector(distance=1).correct_word("xociedadex") == "xociedadex"
    # Limite declarado: pares que exigem duas deleções do lado do léxico não são encontrados.
    assert corrector(distance=2).correct_word("socedadi") == "socedadi"
    assert corrector(distance=2).correct_word("xyzwq") == "xyzwq"


def test_short_words_numbers_and_punctuation_are_left_alone():
    fix = corrector(distance=2, min_length=3)
    assert fix.correct_word("qe") == "qe"
    assert fix.correct_line("1990 - casx!") == "1990 - casa!"
    assert fix.correct_line("  dupla   espaço ") == "  dupla   espaço "


def test_case_is_preserved():
    assert recase("educação", "EDUCACAO") == "EDUCAÇÃO"
    assert recase("educação", "Educacao") == "Educação"
    assert corrector().correct_line("ESCOIA") == "ESCOLA"


def test_lexicon_size_limits_the_vocabulary():
    assert corrector(size=2).correct_word("escoia") == "escoia"
    assert strip_accents("Ação") == "Acao"


def test_frequent_accented_form_replaces_a_rare_unaccented_entry():
    plain = corrector(distance=0)
    ratio = Corrector(WORDS, LexiconParams(size=1000, max_distance=0, accent_ratio=10))
    assert plain.correct_word("nao") == "nao"
    assert ratio.correct_word("nao") == "não"
    assert ratio.correct_word("Nao") == "Não"
    assert ratio.correct_word("casa") == "casa"
