import base64
import hashlib
import io
import json
import sys
import tarfile
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
DEST = FRONTEND / "public" / "fonts"
VERSION = "5.3.0"

FONTS = [
    ("inter", "Inter", "sans-serif"),
    ("merriweather", "Merriweather", "serif"),
    ("lora", "Lora", "serif"),
    ("roboto-serif", "Roboto Serif", "serif"),
    ("source-serif-4", "Source Serif 4", "serif"),
    ("literata", "Literata", "serif"),
    ("eb-garamond", "EB Garamond", "serif"),
    ("libre-baskerville", "Libre Baskerville", "serif"),
    ("crimson-pro", "Crimson Pro", "serif"),
    ("noto-serif", "Noto Serif", "serif"),
    ("bitter", "Bitter", "serif"),
    ("fira-sans", "Fira Sans", "sans-serif"),
    ("source-sans-3", "Source Sans 3", "sans-serif"),
    ("noto-sans", "Noto Sans", "sans-serif"),
    ("atkinson-hyperlegible", "Atkinson Hyperlegible", "sans-serif"),
    ("opendyslexic", "OpenDyslexic", "sans-serif"),
    ("nunito-sans", "Nunito Sans", "sans-serif"),
    ("ibm-plex-sans", "IBM Plex Sans", "sans-serif"),
    ("ibm-plex-serif", "IBM Plex Serif", "serif"),
    ("jetbrains-mono", "JetBrains Mono", "monospace"),
    ("victor-mono", "Victor Mono", "monospace"),
    ("ibm-plex-mono", "IBM Plex Mono", "monospace"),
    ("source-code-pro", "Source Code Pro", "monospace"),
    ("roboto-mono", "Roboto Mono", "monospace"),
]

VARIANTS = [
    (weight, style)
    for weight in (400, 700)
    for style in ("normal", "italic")
]


def download(url):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "CadernoFontInstaller/0.2"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def write_atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(data)
    temporary.replace(path)


def install(font):
    ident, name, _ = font
    directory = DEST / ident / VERSION
    filenames = [
        f"latin-{weight}-{style}.woff2"
        for weight, style in VARIANTS
    ]
    expected = set(filenames + ["LICENSE"])
    manifest = directory / "checksums.json"

    try:
        hashes = json.loads(manifest.read_text(encoding="utf-8"))
        if set(hashes) == expected and all(
            hashlib.sha256((directory / file).read_bytes()).hexdigest()
            == hashes[file]
            for file in expected
        ):
            print(f"OK: {name} (já instalada)", flush=True)
            return
    except (OSError, ValueError, TypeError):
        pass

    print(f"Baixando: {name}", flush=True)

    metadata = json.loads(download(
        f"https://registry.npmjs.org/@fontsource%2F{ident}/{VERSION}"
    ))
    archive = download(metadata["dist"]["tarball"])

    digest = "sha512-" + base64.b64encode(
        hashlib.sha512(archive).digest()
    ).decode("ascii")

    if digest != metadata["dist"]["integrity"]:
        raise RuntimeError(f"Pacote inválido: {name}")

    files = {}

    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as package:
        for file in filenames + ["LICENSE"]:
            member = (
                "package/LICENSE"
                if file == "LICENSE"
                else f"package/files/{ident}-{file}"
            )
            stream = package.extractfile(member)

            if stream is None:
                raise RuntimeError(f"Arquivo ausente: {member}")

            data = stream.read()

            if file.endswith(".woff2") and (
                len(data) < 48
                or data[:4] != b"wOF2"
                or int.from_bytes(data[8:12], "big") != len(data)
            ):
                raise RuntimeError(f"Fonte WOFF2 inválida: {member}")

            files[file] = data

    for file, data in files.items():
        write_atomic(directory / file, data)

    hashes = {
        file: hashlib.sha256(data).hexdigest()
        for file, data in files.items()
    }
    write_atomic(
        manifest,
        json.dumps(hashes, indent=2).encode("utf-8"),
    )
    print(f"OK: {name}", flush=True)


def main():
    if not (FRONTEND / "src" / "main.ts").is_file():
        raise RuntimeError(
            "Coloque o script em scripts/instalar-fontes.py "
            "na raiz do projeto."
        )

    with ThreadPoolExecutor(max_workers=3) as pool:
        list(pool.map(install, FONTS))

    css = ["/* Gerado por scripts/instalar-fontes.py. */"]

    for ident, name, fallback in FONTS:
        family = f"Caderno {name}"

        for weight, style in VARIANTS:
            url = (
                f"/fonts/{ident}/{VERSION}/"
                f"latin-{weight}-{style}.woff2"
            )
            css.append(
                f'@font-face {{ font-family: "{family}"; '
                f'font-weight: {weight}; font-style: {style}; '
                f'font-display: block; '
                f'src: url("{url}") format("woff2"); }}'
            )

        mono = (
            f' --font-mono: "{family}", monospace;'
            if fallback == "monospace"
            else ""
        )

        css.append(
            f':root[data-font="{ident}"] {{ '
            f'--font-reading: "{family}", {fallback};{mono} }}'
        )

    catalog = {
        "version": VERSION,
        "options": [[ident, name] for ident, name, _ in FONTS],
    }

    write_atomic(
        FRONTEND / "src" / "fonts.css",
        ("\n".join(css) + "\n").encode("utf-8"),
    )
    write_atomic(
        FRONTEND / "src" / "font-catalog.json",
        json.dumps(
            catalog, ensure_ascii=False, indent=2
        ).encode("utf-8"),
    )

    print(
        "Concluído: 24 famílias, 96 arquivos WOFF2, "
        "licenças, fonts.css e catálogo."
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(
            f"ERRO: {error}\nCorrija o problema e execute novamente.",
            file=sys.stderr,
        )
        sys.exit(1)