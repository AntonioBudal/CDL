"""Feature 091-C (C018): reconstrução do estado do adaptador a partir dos registros. Banco descartável, dados fictícios."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from app.core.config import BACKEND_DIR
from app.models.organizer_feedback import OrganizerUserState
from app.services.organizer import adapter_service
from feedback_harness import OWNER, harness  # noqa: F401
from test_adapter_service import STEPS, feed, state_of

SCRIPT = BACKEND_DIR / "scripts" / "rebuild_organizer_state.py"


def load_script():
    spec = importlib.util.spec_from_file_location("rebuild_organizer_state", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def user_a_steps(n: int) -> list[dict]:
    return [s for s in STEPS if s["user"] == "u-a"][:n]


def test_rebuild_gives_the_incremental_state(harness):
    feed(harness, user_a_steps(6))
    incremental = state_of(harness).state
    with harness.factory() as session:
        session.get(OrganizerUserState, OWNER).state = '{"schema": "corrompido"}'
        session.commit()
        report = adapter_service.rebuild(session, OWNER, execute=True)
    assert report["records"] == 6 and report["written"] is True
    assert state_of(harness).state == incremental


def test_dry_run_writes_nothing(harness):
    feed(harness, user_a_steps(3))
    before = state_of(harness).state
    with harness.factory() as session:
        session.get(OrganizerUserState, OWNER).state = "marcador"
        session.commit()
        report = adapter_service.rebuild(session, OWNER, execute=False)
    assert report["written"] is False and report["records"] == 3
    assert state_of(harness).state == "marcador" != before


def test_script_refuses_with_the_server_listening(monkeypatch, capsys):
    module = load_script()
    monkeypatch.setattr(module, "port_in_use", lambda port=8000: True)
    called = []
    monkeypatch.setattr(module, "run", lambda *a, **k: called.append(1))
    assert module.main(["--all"]) == 2
    assert called == []
    assert "porta 8000" in capsys.readouterr().err


def test_script_dry_run_reports_only_counts(harness, monkeypatch, capsys, tmp_path):
    feed(harness, user_a_steps(2))
    module = load_script()
    monkeypatch.setattr(module, "port_in_use", lambda port=8000: False)
    database = Path(harness.factory.kw["bind"].url.database)
    monkeypatch.setattr(module, "get_database_path", lambda: database)
    snapshots = []
    monkeypatch.setattr(module, "ensure_pre_upgrade_snapshot", lambda path: snapshots.append(path))
    assert module.main(["--all"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["records"] == 2 and out["written"] is False and snapshots == []
    assert set(out) == {"users", "records", "codes", "bytes", "pruned_books", "written"}
