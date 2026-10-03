"""Serviço de normalização gramatical, singularização e validação de categorias."""

from __future__ import annotations

import re
import unicodedata

from app.services.canonical_categories import (
    CANONICAL_INDEX_BY_NAME_LOWER,
    CANONICAL_INDEX_BY_SLUG,
    resolve_legacy_mapping,
)


def strip_accents(text: str) -> str:
    """Remove marcas diacríticas preservando os caracteres base."""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def normalize_for_search(text: str) -> str:
    """Converte para minúsculas, sem acentos, sem pontuação estranha e com espaços únicos."""
    clean = re.sub(r"[^\w\s-]", "", strip_accents(text.strip().lower()))
    return re.sub(r"\s+", " ", clean).strip()


def slugify_category(name: str) -> str:
    """Gera o identificador slug estável para a categoria."""
    norm = normalize_for_search(name)
    slug = re.sub(r"[^\w]+", "-", norm).strip("-")
    return slug or "categoria"


def singularize_portuguese(word: str) -> str:
    """Aplica regras determinísticas de singularização para substantivos em português."""
    lower = word.strip().lower()
    
    # Exceções ou palavras que já estão no singular terminadas em 's'
    invariables = {"lápis", "vírus", "atlas", "ônibus", "caos", "práxis", "status"}
    if lower in invariables:
        return word

    # Plurais em -ões / -ães / -ãos -> -ão
    if lower.endswith("ões"):
        return word[:-3] + "ão"
    if lower.endswith("ães"):
        return word[:-3] + "ão"
    if lower.endswith("ãos"):
        return word[:-3] + "ão"

    # Plurais em -ns -> -m
    if lower.endswith("ns") and len(lower) > 3:
        return word[:-2] + "m"

    # Plurais em -res / -zes / -nes -> -r / -z / -n
    if lower.endswith("res") and len(lower) > 4:
        return word[:-2]
    if lower.endswith("zes") and len(lower) > 4:
        return word[:-2]

    # Plurais em -ais / -éis / -óis / -uis -> -al / -el / -ol / -ul
    if lower.endswith("ais") and len(lower) > 4:
        return word[:-3] + "al"
    if lower.endswith("éis") and len(lower) > 4:
        return word[:-3] + "el"
    if lower.endswith("óis") and len(lower) > 4:
        return word[:-3] + "ol"

    # Plurais em -es após consoantes comuns (ex.: artes -> arte, fontes -> fonte)
    if lower.endswith("es") and len(lower) > 4:
        # Se antes do 'es' tiver vogal, remove apenas 's' (ex.: noites -> noite)
        return word[:-1]

    # Plurais comuns em -as / -os (ex.: filosofias -> filosofia, direitos -> direito)
    if (lower.endswith("as") or lower.endswith("os")) and len(lower) > 3:
        return word[:-1]

    # Plural genérico em 's' após vogal (ex.: livros -> livro)
    if lower.endswith("s") and len(lower) > 3 and lower[-2] in "aeiouáéíóúãõâêô":
        return word[:-1]

    return word


def canonicalize_name(raw_name: str) -> str:
    """Normaliza um termo para a forma canônica singular e capitalizada."""
    cleaned = re.sub(r"\s+", " ", raw_name.strip())
    if not cleaned:
        return ""

    # Verifica se já bate diretamente com catálogo canônico
    lower = cleaned.lower()
    if lower in CANONICAL_INDEX_BY_NAME_LOWER:
        return CANONICAL_INDEX_BY_NAME_LOWER[lower].name
    
    slug = slugify_category(cleaned)
    if slug in CANONICAL_INDEX_BY_SLUG:
        return CANONICAL_INDEX_BY_SLUG[slug].name

    # Verifica mapeamento de legados
    mapped_slugs = resolve_legacy_mapping(lower)
    if mapped_slugs and mapped_slugs[0] in CANONICAL_INDEX_BY_SLUG:
        return CANONICAL_INDEX_BY_SLUG[mapped_slugs[0]].name

    # Singulariza o termo
    singular = singularize_portuguese(cleaned)
    sing_lower = singular.lower()
    if sing_lower in CANONICAL_INDEX_BY_NAME_LOWER:
        return CANONICAL_INDEX_BY_NAME_LOWER[sing_lower].name

    sing_slug = slugify_category(singular)
    if sing_slug in CANONICAL_INDEX_BY_SLUG:
        return CANONICAL_INDEX_BY_SLUG[sing_slug].name

    # Formatação padrão: Title Case
    return singular[0].upper() + singular[1:]


def validate_category_name(raw_name: str) -> tuple[bool, str]:
    """Valida se um nome de categoria respeita os limites de tamanho e formato."""
    trimmed = raw_name.strip()
    if len(trimmed) < 2:
        return False, "O nome da categoria deve ter pelo menos 2 caracteres."
    if len(trimmed) > 30:
        return False, "O nome da categoria deve ter no máximo 30 caracteres."

    # Bloqueia pontuações arbitrárias ou operadores
    if re.search(r"[/\\;<>_{}\[\]\|*^~]", trimmed):
        return False, "O nome da categoria não pode conter símbolos especiais."

    return True, ""
