"""EXP-031P — completa no catálogo as linhas de cada fonte até a cota do grupo (+5 % de folga),
pelas mesmas vias do EXP-043: API de linhas do Hugging Face (Teklia) e arquivos avulsos do GitHub
(HTR-United). Retomável: o que já está no catálogo não é baixado de novo; as páginas já lidas
ficam num estado local.

Uso: ``python collect.py [--groups A,B]``
"""

from __future__ import annotations

import argparse
import importlib.util
import io
import json
import random
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

import groups
from PIL import Image

from tools.catalogo import Catalog

HERE = Path(__file__).resolve().parent
EXP043 = HERE.parents[1] / "EXP-043-amostragem-de-fontes" / "harness" / "common.py"
_spec = importlib.util.spec_from_file_location("exp043_common", EXP043)
net = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(net)

WORK = Path("D:/Leitorum-DI/trabalho/exp-031p")
STATE = WORK / "coleta-paginas-lidas.json"
API = "https://datasets-server.huggingface.co"
IMAGE_EXT = (".jpg", ".jpeg", ".png", ".tif", ".tiff")


def valid_count(cat, source_id, charset) -> int:
    return len(groups.candidates(cat, source_id, charset))


def collect_teklia(cat, source, need, charset, rng) -> int:
    dataset = source["url"].split("/datasets/")[1]
    base = {"dataset": dataset, "config": "default", "split": "train"}
    first = net.fetch_json(
        f"{API}/rows?{urllib.parse.urlencode({**base, 'offset': 0, 'length': 1})}"
    )
    total = first["num_rows_total"]
    added = 0
    tries = 0
    while valid_count(cat, source["source_id"], charset) < need and tries < 400:
        tries += 1
        offset = rng.randrange(0, max(1, total - 100))
        params = {**base, "offset": offset, "length": 100}
        rows = net.fetch_json(f"{API}/rows?{urllib.parse.urlencode(params)}")["rows"]
        for entry in rows:
            native = f"train-{entry['row_idx']}"
            if cat.item(f"{source['source_id']}:{native}", required=False):
                continue
            text = entry["row"].get("text") or ""
            if not groups.valid_text(text, charset):
                continue
            image = net.fetch(entry["row"]["image"]["src"])
            result = cat.ingest_line(
                source["source_id"],
                native,
                image=image,
                text=text,
                url=f"{source['url']}#{native}",
                script="manuscript",
                split="train",
                acquired_via="exp-031p",
                language=None,
            )
            added += result.created
        cat.flush()
        print(
            f"  {source['source_id']}: {valid_count(cat, source['source_id'], charset)}/{need}",
            flush=True,
        )
    return added


def parse_lines(xml_bytes: bytes):
    root = ET.fromstring(xml_bytes)
    for element in root.iter():
        if element.tag.rsplit("}", 1)[-1] != "TextLine":
            continue
        points, text = None, ""
        for child in element:
            tag = child.tag.rsplit("}", 1)[-1]
            if tag == "Coords" and child.get("points"):
                points = [tuple(map(float, p.split(","))) for p in child.get("points").split()]
            if tag == "TextEquiv":
                uni = next((c for c in child if c.tag.endswith("Unicode")), None)
                if uni is not None and uni.text:
                    text = uni.text
        if points is None and element.get("HPOS"):
            x, y = float(element.get("HPOS")), float(element.get("VPOS"))
            w, h = float(element.get("WIDTH")), float(element.get("HEIGHT"))
            points = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
            text = " ".join(
                s.get("CONTENT", "") for s in element.iter() if s.tag.endswith("String")
            )
        if points:
            yield points, text


def crop_png(image, points) -> bytes:
    """Mesmo recorte do EXP-043 (caixa do polígono, PNG), para o hash coincidir."""
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    box = (max(0, int(min(xs))), max(0, int(min(ys))), int(max(xs)) + 1, int(max(ys)) + 1)
    out = io.BytesIO()
    image.crop(box).save(out, "PNG")
    return out.getvalue()


def collect_htru(cat, source, need, charset, rng, state) -> int:
    owner, repo = re.match(r"https?://github\.com/([^/]+)/([^/#?]+)", source["url"]).groups()
    repo = repo.removesuffix(".git")
    meta = net.fetch_json(f"https://api.github.com/repos/{owner}/{repo}")
    branch = meta["default_branch"]
    tree = net.fetch_json(
        f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    )
    files = [t["path"] for t in tree.get("tree", []) if t.get("type") == "blob"]
    stem = lambda p: p.rsplit(".", 1)[0].rsplit("/", 1)[-1]  # noqa: E731
    images = {stem(p): p for p in files if p.lower().endswith(IMAGE_EXT)}
    pairs = sorted(
        (x, images[stem(x)]) for x in files if x.lower().endswith(".xml") and stem(x) in images
    )
    rng.shuffle(pairs)
    done = set(state.setdefault(source["source_id"], []))
    raw = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/"
    added = 0
    for xml_path, image_path in pairs:
        if valid_count(cat, source["source_id"], charset) >= need:
            break
        if xml_path in done:
            continue
        xml_bytes = net.fetch(raw + xml_path)
        image_bytes = net.fetch(raw + image_path)
        done.add(xml_path)
        state[source["source_id"]] = sorted(done)
        STATE.write_text(json.dumps(state), "utf-8")
        if image_bytes.startswith(b"version https://git-lfs"):
            continue
        try:
            image = Image.open(io.BytesIO(image_bytes))
            image.load()
            lines = list(parse_lines(xml_bytes))
        except Exception:  # noqa: BLE001 — página ilegível: segue
            continue
        for points, text in lines:
            if not groups.valid_text(text, charset):
                continue
            try:
                data = crop_png(image, points)
            except Exception:  # noqa: BLE001
                continue
            import hashlib

            native = hashlib.sha256(data).hexdigest()
            result = cat.ingest_line(
                source["source_id"],
                native,
                image=data,
                text=text,
                url=f"{raw + image_path}#line-{native[:12]}",
                script="manuscript",
                acquired_via="exp-031p",
            )
            added += result.created
        cat.flush()
        print(
            f"  {source['source_id']}: {valid_count(cat, source['source_id'], charset)}/{need}",
            flush=True,
        )
    return added


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--groups", default="A,B")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    WORK.mkdir(parents=True, exist_ok=True)
    charset = groups.load_charset(WORK / "charset.json")
    state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.is_file() else {}
    rng = random.Random("exp-031p-coleta")
    cat = Catalog()
    report = {}
    try:
        for group in args.groups.split(","):
            sources = groups.GROUPS[group]
            quota = groups.allocate(
                groups.PER_GROUP, {s: groups.AVAILABLE[s] for s in sources}, groups.MAX_SHARE
            )
            for source_id in sources:
                need = min(groups.AVAILABLE[source_id], int(quota[source_id] * 1.05) + 1)
                source = cat.source(source_id)
                before = valid_count(cat, source_id, charset)
                if before < need:
                    print(f"{source_id}: {before} → {need}", flush=True)
                    try:
                        if source_id.startswith("teklia-"):
                            collect_teklia(cat, source, need, charset, rng)
                        else:
                            collect_htru(cat, source, need, charset, rng, state)
                    except net.BlockedError as error:
                        print(f"  bloqueado: {error}", flush=True)
                    except Exception as error:  # noqa: BLE001 — registra e segue; é retomável
                        print(f"  erro em {source_id}: {type(error).__name__}", flush=True)
                report[source_id] = {
                    "need": need,
                    "before": before,
                    "after": valid_count(cat, source_id, charset),
                }
    finally:
        cat.close()
    (WORK / "coleta.json").write_text(json.dumps(report, indent=2), "utf-8")
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
