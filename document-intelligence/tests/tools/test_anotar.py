"""F-DI-13.01 — ferramenta de caixas e linhas: integridade do arquivo (schema, ``$``, ``line_id``,
hashes, versão) e API local. Só páginas fictícias."""

from __future__ import annotations

import copy
import functools
import json
import os
import subprocess
import threading
import urllib.error
import urllib.request

import pytest

from tests.tools.synthetic import make_dataset
from tools.anotar import store
from tools.anotar.paths import DI_ROOT, MOTOR_PYTHON, Paths
from tools.anotar.server import make_server


@pytest.fixture
def paths(tmp_path):
    return make_dataset(tmp_path)


def confirmed(doc, field="pass1", mode=None):
    out = copy.deepcopy(doc)
    for line in out["lines"]:
        value = {"text": f"texto fictício {line['line_id']}", "at": "2026-11-20T12:00:00Z"}
        if mode:
            value["mode"] = mode
        line[field] = value
    return out


# ---------------------------------------------------------------- store


def test_initial_doc_from_motor(paths):
    doc = store.load_page(paths, "p01")
    assert doc["version"] == 0
    assert doc["split"] == "test"
    assert [line["line_id"] for line in doc["lines"]] == ["L001", "L002", "L003"]
    assert doc["next_line_id"] == 4
    first = doc["lines"][0]
    assert first["polygon"] == [[50, 100], [900, 100], [900, 180], [50, 180]]
    assert first["box_origin"] == "motor" and first["draft"] == first["motor_text"]
    assert store.load_page(paths, "p02")["split"] == "sem-split"


def test_save_validates_and_hashes(paths):
    doc = store.load_page(paths, "p01")
    saved = store.save_page(paths, "p01", doc, expected_version=0)
    assert saved["version"] == 1
    assert saved["content_sha256"] == store.content_hash(saved)
    on_disk = json.loads((paths.annotations / "p01.json").read_text(encoding="utf-8"))
    assert on_disk == saved
    assert store.validate(on_disk) == []


def test_content_hash_ignores_key_order_and_own_field(paths):
    doc = store.save_page(paths, "p01", store.load_page(paths, "p01"), expected_version=0)
    reordered = dict(reversed(list(doc.items())))
    reordered["content_sha256"] = "0" * 64
    assert store.content_hash(reordered) == doc["content_sha256"]


def test_invalid_doc_is_refused_and_nothing_written(paths):
    doc = store.load_page(paths, "p01")
    doc["lines"][0]["box_origin"] = "inventada"
    with pytest.raises(store.InvalidError) as error:
        store.save_page(paths, "p01", doc, expected_version=0)
    assert any("box_origin" in message for message in error.value.errors)
    assert not (paths.annotations / "p01.json").exists()


@pytest.mark.parametrize(
    ("text", "ok"),
    [("sem fórmula", True), ("$x$ e $y$", True), ("preço \\$ 5", True), ("$x^2", False)],
)
def test_dollar_balance(text, ok):
    assert store.dollar_balanced(text) is ok


def test_unbalanced_dollar_refused(paths):
    doc = confirmed(store.load_page(paths, "p01"))
    doc["lines"][1]["pass1"]["text"] = "fórmula $a+b"
    with pytest.raises(store.InvalidError) as error:
        store.save_page(paths, "p01", doc, expected_version=0)
    assert any("L002" in message and "$" in message for message in error.value.errors)


def test_line_id_never_reused(paths):
    doc = store.save_page(paths, "p01", store.load_page(paths, "p01"), expected_version=0)
    doc["lines"] = [line for line in doc["lines"] if line["line_id"] != "L003"]
    doc = store.save_page(paths, "p01", doc, expected_version=1)
    reborn = copy.deepcopy(doc["lines"][0])
    reborn.update(line_id="L003", order=3, box_origin="criada")
    doc["lines"].append(reborn)
    with pytest.raises(store.InvalidError) as error:
        store.save_page(paths, "p01", doc, expected_version=2)
    assert any("L003" in message for message in error.value.errors)
    doc["lines"][-1]["line_id"] = "L004"
    doc["next_line_id"] = 5
    assert store.save_page(paths, "p01", doc, expected_version=2)["version"] == 3


def test_next_line_id_cannot_go_back(paths):
    doc = store.save_page(paths, "p01", store.load_page(paths, "p01"), expected_version=0)
    doc["next_line_id"] = 2
    with pytest.raises(store.InvalidError):
        store.save_page(paths, "p01", doc, expected_version=1)


def test_duplicate_ids_and_orders_refused(paths):
    doc = store.load_page(paths, "p01")
    doc["lines"][1]["line_id"] = "L001"
    doc["lines"][2]["order"] = 1
    with pytest.raises(store.InvalidError) as error:
        store.save_page(paths, "p01", doc, expected_version=0)
    joined = " ".join(error.value.errors)
    assert "L001" in joined and "order" in joined


def test_polygon_outside_image_refused(paths):
    doc = store.load_page(paths, "p01")
    doc["lines"][0]["polygon"][1] = [5000, 100]
    with pytest.raises(store.InvalidError):
        store.save_page(paths, "p01", doc, expected_version=0)


def test_status_is_computed_by_server(paths):
    doc = store.load_page(paths, "p01")
    doc["status"] = {"boxes_done": True, "pass1_done": True, "pass2_done": True}
    saved = store.save_page(paths, "p01", doc, expected_version=0)
    assert saved["status"] == {"boxes_done": True, "pass1_done": False, "pass2_done": False}
    saved = store.save_page(paths, "p01", confirmed(saved), expected_version=1)
    assert saved["status"]["pass1_done"] is True
    saved = store.save_page(paths, "p01", confirmed(saved, "pass2", "cego"), expected_version=2)
    assert saved["status"]["pass2_done"] is True


def test_second_pass_keeps_first(paths):
    doc = confirmed(store.load_page(paths, "p01"))
    doc = store.save_page(paths, "p01", doc, expected_version=0)
    first = [line["pass1"]["text"] for line in doc["lines"]]
    second = confirmed(doc, "pass2", "revisao")
    second["lines"][0]["pass2"]["text"] = "outra leitura fictícia"
    saved = store.save_page(paths, "p01", second, expected_version=1)
    assert [line["pass1"]["text"] for line in saved["lines"]] == first
    assert saved["lines"][0]["pass2"] == {
        "text": "outra leitura fictícia",
        "at": "2026-11-20T12:00:00Z",
        "mode": "revisao",
    }


def test_empty_pass_text_refused(paths):
    doc = confirmed(store.load_page(paths, "p01"))
    doc["lines"][0]["pass1"]["text"] = "   "
    with pytest.raises(store.InvalidError):
        store.save_page(paths, "p01", doc, expected_version=0)


def test_version_conflict(paths):
    doc = store.load_page(paths, "p01")
    store.save_page(paths, "p01", doc, expected_version=0)
    with pytest.raises(store.ConflictError) as error:
        store.save_page(paths, "p01", doc, expected_version=0)
    assert error.value.current_version == 1


def test_seconds_accumulate_and_previous_kept(paths):
    doc = store.load_page(paths, "p01")
    first = store.save_page(paths, "p01", doc, expected_version=0, seconds_delta={"boxes": 30})
    second = store.save_page(
        paths, "p01", first, expected_version=1, seconds_delta={"boxes": 12.5, "pass1": 40}
    )
    assert second["seconds"] == {"boxes": 42.5, "pass1": 40, "pass2": 0}
    previous = json.loads((paths.annotations / "p01.prev.json").read_text(encoding="utf-8"))
    assert previous["version"] == 1
    with pytest.raises(store.InvalidError):
        store.save_page(paths, "p01", second, expected_version=2, seconds_delta={"pass1": -5})


def test_client_cannot_change_image_identity(paths):
    doc = store.load_page(paths, "p01")
    doc["image"]["sha256"] = "f" * 64
    doc["image"]["width"] = 7
    saved = store.save_page(paths, "p01", doc, expected_version=0)
    assert saved["image"]["width"] == 1000
    registered = json.loads(paths.registered.read_text(encoding="utf-8"))["pages"]["p01"]
    assert saved["image"]["sha256"] == registered["sha256"]


def test_low_resolution_flag_in_page_list(paths):
    data = json.loads(paths.registered.read_text(encoding="utf-8"))
    data["pages"]["p02"]["low_resolution"] = True
    paths.registered.write_text(json.dumps(data), encoding="utf-8")
    flags = {page["id"]: page["low_resolution"] for page in store.list_pages(paths)}
    assert flags == {"p01": False, "p02": True}


def test_page_with_wrong_hash_is_blocked(paths):
    (paths.images / "p02.jpg").write_bytes(b"outra imagem")
    pages = {page["id"]: page for page in store.list_pages(paths)}
    assert pages["p01"]["hash_ok"] is True
    assert pages["p02"]["hash_ok"] is False
    with pytest.raises(store.BlockedError):
        store.load_page(paths, "p02")


def test_unregistered_original_is_blocked(paths):
    index = json.loads(paths.index.read_text(encoding="utf-8"))
    index["pages"]["p02"]["sha256"] = "a" * 64
    paths.index.write_text(json.dumps(index), encoding="utf-8")
    with pytest.raises(store.BlockedError):
        store.load_page(paths, "p02")


@pytest.mark.parametrize("bad", ["../p01", "p1", "p01.json", "P01", "p01/../../x"])
def test_bad_page_ids(paths, bad):
    with pytest.raises(store.NotFoundError):
        store.load_page(paths, bad)


def test_import_draft_distributes_in_order(paths):
    doc = store.load_page(paths, "p01")
    text = "primeira fictícia\n\nsegunda fictícia\nterceira\nquarta sobra\nquinta sobra\n"
    out = store.import_draft(doc, text, "professor-teste")
    assert [line["draft"] for line in out["lines"]] == [
        "primeira fictícia",
        "segunda fictícia",
        "terceira",
    ]
    assert out["draft_leftover"] == ["quarta sobra", "quinta sobra"]
    assert out["draft_source"] == "importado:professor-teste"
    assert [line["motor_text"] for line in out["lines"]] == [
        line["motor_text"] for line in doc["lines"]
    ]
    assert store.validate({**out, "version": 1, "content_sha256": "0" * 64,
                           "updated_at": "2026-11-20T12:00:00Z"}) == []


def test_order_follows_list_when_lines_sorted(paths):
    doc = store.load_page(paths, "p01")
    doc["lines"][0]["order"], doc["lines"][2]["order"] = 3, 1
    saved = store.save_page(paths, "p01", doc, expected_version=0)
    assert [line["order"] for line in saved["lines"]] == [1, 2, 3]
    assert [line["line_id"] for line in saved["lines"]] == ["L003", "L002", "L001"]


# ---------------------------------------------------------------- servidor


@pytest.fixture
def server(paths):
    httpd = make_server(paths, port=0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()
    httpd.server_close()


def call(url, method="GET", body=None):
    data = None if body is None else json.dumps(body).encode()
    request = urllib.request.Request(url, data=data, method=method)
    request.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as error:
        return error.code, error.read()


def test_server_binds_only_localhost(paths):
    with pytest.raises(ValueError):
        make_server(paths, host="0.0.0.0", port=0)


def test_api_round_trip(server):
    status, body = call(f"{server}/api/pages")
    assert status == 200
    pages = json.loads(body)["pages"]
    assert [page["id"] for page in pages] == ["p01", "p02"]
    status, body = call(f"{server}/api/pages/p01")
    doc = json.loads(body)
    status, body = call(
        f"{server}/api/pages/p01",
        "PUT",
        {"version": 0, "doc": doc, "seconds_delta": {"boxes": 3}},
    )
    assert status == 200, body
    assert json.loads(body)["doc"]["version"] == 1
    status, body = call(f"{server}/api/pages/p01", "PUT", {"version": 0, "doc": doc})
    assert status == 409 and json.loads(body)["current_version"] == 1
    doc["lines"][0]["box_origin"] = "x"
    status, body = call(f"{server}/api/pages/p01", "PUT", {"version": 1, "doc": doc})
    assert status == 422 and json.loads(body)["errors"]


def test_api_image_and_static(server):
    status, body = call(f"{server}/img/p01.jpg")
    assert status == 200 and body == "imagem de trabalho fictícia p01".encode()
    status, _ = call(f"{server}/")
    assert status == 200
    for bad in ["/img/..%2Fpages.json", "/img/p99.jpg", "/../tools/anotar/paths.py",
                "/static/..%2F..%2Fpaths.py", "/api/pages/..%2Fp01"]:
        status, _ = call(f"{server}{bad}")
        assert status in {403, 404}, bad


def test_api_draft_import(server):
    status, body = call(
        f"{server}/api/pages/p01/draft", "POST", {"text": "a\nb\nc\nd", "label": "teste"}
    )
    assert status == 200
    doc = json.loads(body)["doc"]
    assert doc["draft_leftover"] == ["d"] and doc["lines"][0]["draft"] == "a"


def test_api_rejects_large_body(server):
    status, _ = call(f"{server}/api/pages/p01", "PUT", {"version": 0, "doc": "x" * 6_000_000})
    assert status == 413


# ---------------------------------------------------------------- preparação (ambiente do motor)


@pytest.mark.skipif(not MOTOR_PYTHON.is_file(), reason="ambiente do motor ausente")
def test_prepare_maps_by_hash_orients_and_resumes(tmp_path):
    root = tmp_path / "dataset"
    photos = root / "raw" / "exp-027" / "fotos"
    splits = tmp_path / "splits"
    splits.mkdir()
    env = {**os.environ, "ANOTAR_DATA_ROOT": str(root), "ANOTAR_SPLITS_DIR": str(splits)}
    run = functools.partial(
        subprocess.run, cwd=DI_ROOT, env=env, capture_output=True, text=True, timeout=300
    )
    made = run([str(MOTOR_PYTHON), "-m", "tests.tools.make_photos", str(photos), "3"])
    assert made.returncode == 0, made.stderr
    files = sorted(photos.iterdir())
    registered = {
        "p01": {"sha256": store.file_sha256(files[0]), "width": 1500, "height": 2000},
        "p02": {"sha256": store.file_sha256(files[1]), "width": 1500, "height": 2000},
    }
    (splits / "pages-sha256.json").write_text(json.dumps({"pages": registered}), encoding="utf-8")
    (splits / "test-manifest.json").write_text(json.dumps({"pages": {"p02": {}}}), "utf-8")

    first = run([str(MOTOR_PYTHON), "-m", "tools.anotar.prepare", "--no-motor"])
    assert first.returncode == 0, first.stderr
    report = json.loads(first.stdout.strip().splitlines()[-1])
    assert report["registered"] == 2 and report["unregistered"] == 1 and report["prepared"] == 2
    assert report["missing"] == []
    paths = Paths(data_root=root, splits=splits)
    index = json.loads(paths.index.read_text(encoding="utf-8"))["pages"]
    assert (index["p02"]["width"], index["p02"]["height"]) == (1500, 2000)  # EXIF 6 desfeito
    assert all(store.hash_ok(paths, pid) for pid in ("p01", "p02"))
    assert store.load_page(paths, "p02")["split"] == "test"

    again = run([str(MOTOR_PYTHON), "-m", "tools.anotar.prepare", "--no-motor"])
    assert json.loads(again.stdout.strip().splitlines()[-1])["prepared"] == 0


@pytest.mark.skipif(not MOTOR_PYTHON.is_file(), reason="ambiente do motor ausente")
def test_register_by_mtime_and_remove(tmp_path):
    root = tmp_path / "dataset"
    photos = root / "raw" / "exp-027" / "fotos"
    splits = tmp_path / "splits"
    splits.mkdir()
    (splits / "pages-sha256.json").write_text(
        json.dumps({"pages": {"p01": {"sha256": "a" * 64, "width": 1, "height": 1}}}), "utf-8"
    )
    env = {**os.environ, "ANOTAR_DATA_ROOT": str(root), "ANOTAR_SPLITS_DIR": str(splits)}
    run = functools.partial(
        subprocess.run, cwd=DI_ROOT, env=env, capture_output=True, text=True, timeout=300
    )
    made = run([str(MOTOR_PYTHON), "-m", "tests.tools.make_photos", str(photos), "3"])
    assert made.returncode == 0
    files = sorted(photos.iterdir())
    for offset, path in enumerate(reversed(files)):  # horário inverso ao nome
        os.utime(path, (1_700_000_000 + offset, 1_700_000_000 + offset))
    args = [str(MOTOR_PYTHON), "-m", "tools.anotar.register", "--order", "p10,p11,p14",
            "--source", "teste", "--low-resolution"]
    done = run([*args, "--remove", "p01"])
    assert done.returncode == 0, done.stderr
    data = json.loads((splits / "pages-sha256.json").read_text(encoding="utf-8"))
    assert sorted(data["pages"]) == ["p10", "p11", "p14"]
    assert data["pages"]["p10"]["sha256"] == store.file_sha256(files[-1])  # o mais antigo
    assert data["pages"]["p10"]["low_resolution"] is True
    assert data["amendments"][-1]["removed"] == ["p01"]
    wrong = run([str(MOTOR_PYTHON), "-m", "tools.anotar.register", "--order", "p10,p11",
                 "--source", "teste"])
    assert wrong.returncode != 0 and "3 fotos" in wrong.stderr + wrong.stdout



def test_second_pass_flag_and_last_pass1(paths):
    (paths.splits / "second-pass.json").write_text(json.dumps({"pages": {"p02": {}}}), "utf-8")
    doc = store.load_page(paths, "p02")
    doc["lines"][0]["pass1"] = {"text": "texto fictício", "at": "2026-11-20T12:00:00Z"}
    store.save_page(paths, "p02", doc, expected_version=0)
    pages = {page["id"]: page for page in store.list_pages(paths)}
    assert pages["p02"]["second_pass"] == "cego" and pages["p01"]["second_pass"] is None
    assert pages["p02"]["last_pass1_at"] == "2026-11-20T12:00:00Z"
    assert pages["p01"]["last_pass1_at"] is None
    assert (pages["p02"]["pass1_lines"], pages["p02"]["pass2_lines"]) == (1, 0)
    assert pages["p01"]["pass1_lines"] == 0
