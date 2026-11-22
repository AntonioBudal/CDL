"""EXP-043 — amostra de conjuntos do catálogo HTR-United hospedados no GitHub: até ``--pages``
páginas por conjunto (imagem + PAGE XML ou ALTO), baixadas arquivo a arquivo (sem clonar o
repositório), com as linhas recortadas pelas coordenadas da verdade-terreno. Arquivos guardados
no Git LFS ficam de fora (anotado).

Uso: ``python sample_htr_united.py [--sets 12] [--pages 15]``
"""

from __future__ import annotations

import argparse
import io
import json
import random
import re
import sys
import xml.etree.ElementTree as ET

import common
import yaml

CATALOG = "https://raw.githubusercontent.com/HTR-United/htr-united/master/htr-united.yml"
IMAGE_EXT = (".jpg", ".jpeg", ".png", ".tif", ".tiff")
MAX_IMAGE_BYTES = 15 * 1024**2
ALREADY_IN_TEKLIA = ("belfort", "popp")
LICENSE_STATUS = {
    "CC-BY 4.0": "APPROVED",
    "CC-BY-SA 4.0": "APPROVED",
    "Etalab OL 2.0": "APPROVED",
    "Apache-2.0 License": "APPROVED",
    "CC-BY-NC-SA 4.0": "APPROVED_NC",
    "CC BY-NC-SA 4.0": "APPROVED_NC",
    "CC-BY-NC-SA 3.0": "APPROVED_NC",
}


def license_name(entry: dict) -> str | None:
    value = entry.get("license")
    if isinstance(value, list) and value:
        value = value[0]
    return value.get("name") if isinstance(value, dict) else value


def line_count(entry: dict) -> int:
    return sum(
        (v.get("count") or 0) for v in entry.get("volume") or [] if v.get("metric") == "lines"
    )


def era_end(entry: dict) -> int:
    match = re.match(r"\d{3,4}", str((entry.get("time") or {}).get("notAfter", "0")))
    return int(match.group()) if match else 0


def choose(catalog: list[dict], count: int) -> list[dict]:
    pool = []
    for entry in catalog:
        url = entry.get("url") or ""
        name = (entry.get("title") or "").lower()
        if "manuscript" not in str(entry.get("script-type")):
            continue
        if not re.match(r"https?://github\.com/[^/]+/[^/]+", url):
            continue
        if license_name(entry) not in LICENSE_STATUS or any(k in name for k in ALREADY_IN_TEKLIA):
            continue
        pool.append(entry)
    portuguese = [e for e in pool if "por" in (e.get("language") or [])]
    rest = sorted(
        (e for e in pool if e not in portuguese),
        key=lambda e: (era_end(e) >= 1850, line_count(e)),
        reverse=True,
    )
    picked, languages = list(portuguese), set()
    for entry in rest:  # diversidade de idioma primeiro, depois volume
        lang = (entry.get("language") or ["?"])[0]
        if lang not in languages or len(picked) >= count // 2:
            picked.append(entry)
            languages.add(lang)
        if len(picked) >= count:
            break
    return picked


def parse_lines(xml_bytes: bytes) -> list[tuple[list[tuple[float, float]], str]]:
    root = ET.fromstring(xml_bytes)
    lines = []
    for element in root.iter():
        tag = element.tag.rsplit("}", 1)[-1]
        if tag != "TextLine":
            continue
        points, text = None, ""
        for child in element:
            ctag = child.tag.rsplit("}", 1)[-1]
            if ctag == "Coords" and child.get("points"):
                points = [tuple(map(float, p.split(","))) for p in child.get("points").split()]
            if ctag == "TextEquiv":
                unicode_el = next((c for c in child if c.tag.endswith("Unicode")), None)
                if unicode_el is not None and unicode_el.text:
                    text = unicode_el.text
        if points is None and element.get("HPOS"):  # ALTO
            x, y = float(element.get("HPOS")), float(element.get("VPOS"))
            w, h = float(element.get("WIDTH")), float(element.get("HEIGHT"))
            points = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
            words = [s.get("CONTENT", "") for s in element.iter() if s.tag.endswith("String")]
            text = " ".join(w for w in words if w)
        if points:
            lines.append((points, text))
    return lines


def crop(image, points) -> bytes:
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    box = (max(0, int(min(xs))), max(0, int(min(ys))), int(max(xs)) + 1, int(max(ys)) + 1)
    out = io.BytesIO()
    image.crop(box).save(out, "PNG")
    return out.getvalue()


def sample_set(entry: dict, pages: int, rng: random.Random) -> dict:
    from PIL import Image

    owner, repo = re.match(r"https?://github\.com/([^/]+)/([^/#?]+)", entry["url"]).groups()
    repo = repo.removesuffix(".git")
    source = f"htr-united-{repo}"
    lic = license_name(entry)
    status = LICENSE_STATUS[lic]
    stats = {
        "title": entry.get("title"),
        "repo": f"{owner}/{repo}",
        "license": lic,
        "status": status,
        "language": entry.get("language"),
        "era": entry.get("time"),
        "catalog_lines": line_count(entry),
        "pages": 0,
        "lines": 0,
        "usable": 0,
        "lfs_skipped": 0,
        "bytes_page": 0,
        "bytes_original": 0,
        "bytes_ours": 0,
        "bytes_ours_lossy": 0,
        "chars": 0,
        "pt_accents": 0,
        "blocked": None,
    }
    meta = common.fetch_json(f"https://api.github.com/repos/{owner}/{repo}")
    branch = meta["default_branch"]
    tree = common.fetch_json(
        f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    )
    files = [t["path"] for t in tree.get("tree", []) if t.get("type") == "blob"]
    images = {
        p.rsplit(".", 1)[0].rsplit("/", 1)[-1]: p for p in files if p.lower().endswith(IMAGE_EXT)
    }
    pairs = [
        (x, images[x.rsplit(".", 1)[0].rsplit("/", 1)[-1]])
        for x in files
        if x.lower().endswith(".xml") and x.rsplit(".", 1)[0].rsplit("/", 1)[-1] in images
    ]
    stats["pairs_in_repo"] = len(pairs)
    raw = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/"
    for xml_path, image_path in rng.sample(pairs, min(pages, len(pairs))):
        try:
            xml_bytes = common.fetch(raw + xml_path)
            image_bytes = common.fetch(raw + image_path)
        except common.BlockedError as error:
            stats["blocked"] = str(error)
            break
        if image_bytes.startswith(b"version https://git-lfs"):
            stats["lfs_skipped"] += 1
            continue
        if len(image_bytes) > MAX_IMAGE_BYTES:
            continue
        try:
            lines = parse_lines(xml_bytes)
            image = Image.open(io.BytesIO(image_bytes))
            image.load()
        except Exception:  # noqa: BLE001 — XML ou imagem ilegível: só conta
            continue
        page_path = common.store(source, image_bytes, "." + image_path.rsplit(".", 1)[-1].lower())
        common.store(source, xml_bytes, ".xml")
        stats["pages"] += 1
        stats["bytes_page"] += len(image_bytes)
        for points, text in lines:
            try:
                line_bytes = crop(image, points)
                measures = common.line_measures(line_bytes, text)
            except Exception:  # noqa: BLE001
                continue
            line_path = common.store(source, line_bytes, ".png")
            common.record(
                source,
                {
                    "source": f"HTR-United/{entry.get('title')}",
                    "source_url": entry["url"],
                    "page_file": page_path.name,
                    "page_url": raw + image_path,
                    "file": line_path.name,
                    "sha256": line_path.stem,
                    "license": lic,
                    "status": status,
                    "language": entry.get("language"),
                    "era": entry.get("time"),
                    "transcription": "line",
                    "text": text,
                    **measures,
                },
            )
            stats["lines"] += 1
            stats["usable"] += measures["usable"]
            for key in ("bytes_original", "bytes_ours", "bytes_ours_lossy", "chars", "pt_accents"):
                stats[key] += measures[key]
    return stats


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sets", type=int, default=12)
    parser.add_argument("--pages", type=int, default=15)
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    catalog_bytes = common.fetch(CATALOG)
    evidence = common.store("htr-united", catalog_bytes, ".yml")
    catalog = yaml.safe_load(catalog_bytes)
    rng = random.Random("exp-043")
    results = []
    for entry in choose(catalog, args.sets):
        try:
            result = sample_set(entry, args.pages, rng)
        except common.BlockedError as error:
            result = {"title": entry.get("title"), "blocked": str(error)}
        except Exception as error:  # noqa: BLE001 — registra e segue para o próximo
            result = {
                "title": entry.get("title"),
                "error": f"{type(error).__name__}: {str(error)[:120]}",
            }
        results.append(result)
        print(
            json.dumps(
                {
                    k: result.get(k)
                    for k in ("title", "pages", "lines", "lfs_skipped", "blocked", "error")
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
    out = common.ROOT / "resumo-htr-united.json"
    out.write_text(
        json.dumps(
            {"catalog_sha256": evidence.stem, "results": results}, ensure_ascii=False, indent=2
        ),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
