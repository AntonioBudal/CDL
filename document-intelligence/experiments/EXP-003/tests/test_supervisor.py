"""Testes do supervisor de layout: referência, deslocamento, limites e portão de licença."""

import hashlib

from evaluate import evaluate_pages
from supervisor import Limits, license_gate, run_candidate

MIB = 1024 * 1024
NO_FREE_CHECK = {"min_free_system_bytes": 0}
RELAXED = Limits(**NO_FREE_CHECK)
REFERENCE = {
    "id": "reference",
    "kind": "reference",
    "adapter": "adapters.reference:ReferenceDetector",
}


def _fake(name, **options):
    adapter = f"adapters.fakes:{name}"
    return {"id": name, "kind": "reference", "adapter": adapter, "options": options}


def _metrics(manifest, result):
    return evaluate_pages(manifest, {p["id"]: p["result"] for p in result.predictions})


def test_reference_detector_scores_perfectly(tiny_manifest):
    path, root, manifest = tiny_manifest
    result = run_candidate(REFERENCE, path, root, limits=RELAXED)
    assert result.status == "OK", result.stderr_tail
    metrics = _metrics(manifest, result)
    assert metrics["lines"]["bbox"]["0.5"]["f1"] == 1.0
    assert metrics["blocks"]["map50"] == 1.0
    assert all(p["elapsed_ms"] >= 0 for p in result.predictions)


def test_shifted_detector_gives_known_iou(tiny_manifest):
    path, root, manifest = tiny_manifest
    result = run_candidate(_fake("ShiftedDetector", dx=40), path, root, limits=RELAXED)
    assert result.status == "OK", result.stderr_tail
    lines = _metrics(manifest, result)["lines"]["bbox"]
    assert lines["0.5"]["mean_iou"] == 160 / 240
    assert lines["0.75"]["tp"] == 0


def test_corrupted_page_fails_the_run(tiny_manifest):
    path, root, manifest = tiny_manifest
    (root / manifest["pages"][4]["image"]).write_bytes(b"adulterado")
    result = run_candidate(REFERENCE, path, root, limits=RELAXED)
    assert result.status == "FAILED"
    assert any("SHA-256" in line for line in result.stderr_tail)


def test_memory_limit(tiny_manifest):
    path, root, _ = tiny_manifest
    limits = Limits(memory_bytes=150 * MIB, poll_interval_s=0.01, **NO_FREE_CHECK)
    result = run_candidate(_fake("MemoryHogDetector", total_mib=400), path, root, limits=limits)
    assert result.status == "ABORTED" and result.reason.startswith("memory")


def test_load_timeout(tiny_manifest):
    path, root, _ = tiny_manifest
    limits = Limits(load_timeout_s=1.0, **NO_FREE_CHECK)
    result = run_candidate(_fake("SlowLoadDetector", load_seconds=30), path, root, limits=limits)
    assert result.status == "ABORTED" and result.reason.startswith("load timeout")


def test_latency_limit_keeps_partial_predictions(tiny_manifest):
    path, root, manifest = tiny_manifest
    limits = Limits(latency_probe_lines=3, latency_abort_ms=50.0, **NO_FREE_CHECK)
    result = run_candidate(
        _fake("SlowPageDetector", page_seconds=0.12), path, root, limits=limits, warmup=0
    )
    assert result.status == "ABORTED" and result.reason.startswith("latency")
    assert 3 <= len(result.predictions) < len(manifest["pages"])


def test_crash_is_failed(tiny_manifest):
    path, root, _ = tiny_manifest
    result = run_candidate(_fake("CrashingDetector"), path, root, limits=RELAXED)
    assert result.status == "FAILED"
    assert any("falha simulada" in line for line in result.stderr_tail)


def test_license_gate_and_refusal(tiny_manifest, tmp_path):
    path, root, _ = tiny_manifest
    assert license_gate({"kind": "reference"})[0]
    assert not license_gate({"license_status": "NEEDS VALIDATION", "benchmark_allowed": True})[0]
    assert license_gate(
        {"license_status": "NEEDS VALIDATION", "benchmark_allowed": True, "user_exception": "ok"}
    )[0]
    candidate = {
        "id": "sem-licenca",
        "adapter": "adapters.reference:ReferenceDetector",
        "license_status": "NEEDS VALIDATION",
        "benchmark_allowed": True,
    }
    refused = run_candidate(candidate, path, root, limits=RELAXED)
    assert refused.status == "REFUSED" and refused.exit_code is None

    weights = tmp_path / "w"
    weights.mkdir()
    (weights / "model.pth").write_bytes(b"pesos")
    candidate.update(
        license_status="VERIFIED", weights={"files": {"model.pth": {"sha256": "0" * 64}}}
    )
    assert (
        run_candidate(candidate, path, root, limits=RELAXED, weights_dir=weights).status
        == "REFUSED"
    )
    candidate["weights"]["files"]["model.pth"]["sha256"] = hashlib.sha256(b"pesos").hexdigest()
    assert run_candidate(candidate, path, root, limits=RELAXED, weights_dir=weights).status == "OK"
