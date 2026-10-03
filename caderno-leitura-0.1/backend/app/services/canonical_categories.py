"""Catálogo canônico e regras declarativas de mapeamento taxonômico."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class CanonicalCategoryDef:
    id: str
    name: str
    description: str = ""


# Catálogo oficial de categorias canônicas (estritamente singulares e curtas)
CANONICAL_CATEGORIES: Final[list[CanonicalCategoryDef]] = [
    CanonicalCategoryDef("antropologia", "Antropologia", "Estudo das culturas e sociedades humanas"),
    CanonicalCategoryDef("arte", "Arte", "Manifestações artísticas, plásticas e visuais"),
    CanonicalCategoryDef("biografia", "Biografia", "Vidas, memórias e relatos autobiográficos"),
    CanonicalCategoryDef("ciencia", "Ciência", "Ciências naturais, exatas e método científico"),
    CanonicalCategoryDef("cinema", "Cinema", "Audiovisual, filmes e história cinematográfica"),
    CanonicalCategoryDef("critica", "Crítica", "Crítica literária, ensaística e de arte"),
    CanonicalCategoryDef("direito", "Direito", "Ciências jurídicas, leis e teoria do direito"),
    CanonicalCategoryDef("economia", "Economia", "Economia política, finanças e desenvolvimento"),
    CanonicalCategoryDef("educacao", "Educação", "Pedagogia, ensino e formação"),
    CanonicalCategoryDef("ensaio", "Ensaio", "Reflexões ensaísticas e pensadores"),
    CanonicalCategoryDef("ficcao", "Ficção", "Obras de imaginação, contos e romances"),
    CanonicalCategoryDef("filosofia", "Filosofia", "Epistemologia, ética, lógica e metafísica"),
    CanonicalCategoryDef("historia", "História", "Historiografia e processos históricos"),
    CanonicalCategoryDef("linguistica", "Linguística", "Estudo da linguagem e semiótica"),
    CanonicalCategoryDef("literatura", "Literatura", "Estudos e clássicos literários"),
    CanonicalCategoryDef("medicina", "Medicina", "Saúde, ciências médicas e biológicas"),
    CanonicalCategoryDef("musica", "Música", "Teoria, história e cultura musical"),
    CanonicalCategoryDef("poesia", "Poesia", "Lírica, poemas e versos"),
    CanonicalCategoryDef("politica", "Política", "Teoria política, governança e poder"),
    CanonicalCategoryDef("psicologia", "Psicologia", "Mente humana, psicanálise e comportamento"),
    CanonicalCategoryDef("religiao", "Religião", "Teologia, espiritualidade e crenças"),
    CanonicalCategoryDef("sociologia", "Sociologia", "Estruturas, relações e teorias sociais"),
    CanonicalCategoryDef("teatro", "Teatro", "Dramaturgia e artes cênicas"),
    CanonicalCategoryDef("tecnologia", "Tecnologia", "Computação, engenharia e inovação"),
]

CANONICAL_INDEX_BY_SLUG: Final[dict[str, CanonicalCategoryDef]] = {
    c.id: c for c in CANONICAL_CATEGORIES
}

CANONICAL_INDEX_BY_NAME_LOWER: Final[dict[str, CanonicalCategoryDef]] = {
    c.name.lower(): c for c in CANONICAL_CATEGORIES
}

# Tabela declarativa de mapeamento para atribuição distributiva de categorias legadas (normalizadas em minúsculas)
LEGACY_CATEGORY_MAPPING: Final[dict[str, list[str]]] = {
    # Termos plurais simples
    "filosofias": ["filosofia"],
    "historias": ["historia"],
    "histórias": ["historia"],
    "ciencias": ["ciencia"],
    "ciências": ["ciencia"],
    "literaturas": ["literatura"],
    "ficcoes": ["ficcao"],
    "ficções": ["ficcao"],
    "poesias": ["poesia"],
    "artes": ["arte"],
    "direitos": ["direito"],
    "economias": ["economia"],
    "politicas": ["politica"],
    "políticas": ["politica"],
    "sociologias": ["sociologia"],
    "psicologias": ["psicologia"],
    "tecnologias": ["tecnologia"],
    "religioes": ["religiao"],
    "religiões": ["religiao"],
    "biografias": ["biografia"],
    "educacoes": ["educacao"],
    "educações": ["educacao"],

    # Termos compostos e longos com atribuição distributiva (1 para N)
    "ciencias sociais e humanas": ["ciencia", "sociologia"],
    "ciências sociais e humanas": ["ciencia", "sociologia"],
    "ciencias sociais": ["sociologia"],
    "ciências sociais": ["sociologia"],
    "ciencias humanas": ["historia", "filosofia"],
    "ciências humanas": ["historia", "filosofia"],
    "ciencias naturais": ["ciencia"],
    "ciências naturais": ["ciencia"],
    "ciencias exatas": ["ciencia"],
    "ciências exatas": ["ciencia"],
    "historias de ficcao": ["historia", "ficcao"],
    "histórias de ficção": ["historia", "ficcao"],
    "ficcao cientifica": ["ficcao", "ciencia"],
    "ficção científica": ["ficcao", "ciencia"],
    "teorias politicas modernas": ["politica"],
    "teorias políticas modernas": ["politica"],
    "ciencia politica": ["politica"],
    "ciência política": ["politica"],
    "artes visuais": ["arte"],
    "historia da arte": ["historia", "arte"],
    "história da arte": ["historia", "arte"],
    "filosofia politica": ["filosofia", "politica"],
    "filosofia política": ["filosofia", "politica"],
    "filosofia da mente": ["filosofia", "psicologia"],
    "historia e filosofia": ["historia", "filosofia"],
    "história e filosofia": ["historia", "filosofia"],
    "estudos literarios": ["literatura"],
    "estudos literários": ["literatura"],
    "teoria literaria": ["literatura"],
    "teoria literária": ["literatura"],
    "psicanalise": ["psicologia"],
    "psicanálise": ["psicologia"],
}


def get_canonical_catalog() -> list[CanonicalCategoryDef]:
    """Retorna a lista imutável de categorias canônicas oficiais."""
    return list(CANONICAL_CATEGORIES)


def is_canonical_slug(slug: str) -> bool:
    """Verifica se um slug pertence ao catálogo canônico."""
    return slug in CANONICAL_INDEX_BY_SLUG


def resolve_legacy_mapping(normalized_term: str) -> list[str]:
    """Retorna os slugs canônicos equivalentes para um termo legado ou variante."""
    term = normalized_term.strip().lower()
    if term in LEGACY_CATEGORY_MAPPING:
        return list(LEGACY_CATEGORY_MAPPING[term])

    # Se já é um slug canônico
    if term in CANONICAL_INDEX_BY_SLUG:
        return [term]

    # Se bate com nome canônico
    if term in CANONICAL_INDEX_BY_NAME_LOWER:
        return [CANONICAL_INDEX_BY_NAME_LOWER[term].id]

    return []
