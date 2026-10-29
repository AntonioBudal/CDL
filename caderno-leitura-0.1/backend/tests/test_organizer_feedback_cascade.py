"""Feature 091-B (B011): o registro do organizador sai em todo caminho de exclusão definitiva e fica fora da exportação."""

from __future__ import annotations

import io
import zipfile

from app.models.organizer_feedback import OrganizerFeedback, OrganizerUserState
from app.models.study import Study
from app.models.user import User
from app.services import account_service, trash_service
from app.services.export_service import generate_account_export_zip
from feedback_harness import OTHER, OWNER, harness, suggestion  # noqa: F401


def recorded_study(harness, uid: str = OWNER) -> int:
    study = harness.study(uid)
    assert harness.send(study, {"origin": "digitize", "organizer": suggestion()}, uid).status_code == 204
    return study


def count(harness) -> int:
    with harness.factory() as session:
        return session.query(OrganizerFeedback).count()


def test_permanent_study_delete_removes_record(harness):
    study = recorded_study(harness)
    with harness.factory() as session:
        trash_service.trash_study(session, study, OWNER)
        trash_service.permanent_delete_study(session, study, OWNER)
        session.commit()
    assert count(harness) == 0


def test_emptying_trash_removes_record(harness):
    study = recorded_study(harness)
    kept = recorded_study(harness)
    with harness.factory() as session:
        trash_service.trash_study(session, study, OWNER)
        session.commit()
        trash_service.empty_trash(session, OWNER)
        session.commit()
    assert [r.study_id for r in harness.records()] == [kept]


def test_permanent_book_delete_removes_record(harness):
    study = recorded_study(harness)
    with harness.factory() as session:
        book_id = session.get(Study, study).chapter.book_id
        trash_service.trash_book(session, book_id, OWNER)
        trash_service.permanent_delete_book(session, book_id, OWNER)
        session.commit()
    assert count(harness) == 0


def test_account_delete_removes_records_and_state(harness):
    recorded_study(harness, OTHER)
    kept = recorded_study(harness, OWNER)
    with harness.factory() as session:
        assert session.get(OrganizerUserState, OTHER) is not None  # criado pelo adaptador (091-C)
        account_service.delete_account_permanently(session, session.get(User, OTHER), "outro_teste")
        session.commit()
        assert [s.user_id for s in session.query(OrganizerUserState)] == [OWNER]
    assert [r.study_id for r in harness.records()] == [kept]


def test_account_export_does_not_carry_the_record(harness):
    recorded_study(harness)
    with harness.factory() as session:
        data, _name = generate_account_export_zip(session, session.get(User, OWNER))
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        content = b"".join(archive.read(name) for name in archive.namelist())
    for marker in (b"leitorum-feedback", b"human_corrections", b"saved_sections", b"organizer_feedback"):
        assert marker not in content
