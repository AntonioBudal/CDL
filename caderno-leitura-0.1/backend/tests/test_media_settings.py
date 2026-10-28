"""Feature 090-C (C031): configurações de cota e retenção; valor inválido impede a partida."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.core import config
from app.main import create_app

NAMES = (
    "LEITORUM_USER_STORAGE_QUOTA_BYTES", "LEITORUM_GLOBAL_STORAGE_QUOTA_BYTES", "LEITORUM_STORAGE_FREE_MARGIN_BYTES",
    "LEITORUM_MEDIA_RETENTION_DAYS", "LEITORUM_MEDIA_COMPLETED_GRACE_DAYS", "LEITORUM_MEDIA_JOB_INTERVAL_HOURS",
    "LEITORUM_MEDIA_DELETE_ON_COMPLETED",
)


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for name in NAMES:
        monkeypatch.delenv(name, raising=False)


def test_defaults():
    assert config.get_user_storage_quota_bytes() == 1_073_741_824
    assert config.get_global_storage_quota_bytes() == 966_367_641_600
    assert config.get_storage_free_margin_bytes() == 2_147_483_648
    assert config.get_media_retention_days() == 30
    assert config.get_media_completed_grace_days() == 7
    assert config.get_media_job_interval_hours() == 6
    assert config.get_media_delete_on_completed() is True
    config.validate_media_settings()


def test_values_from_environment(monkeypatch):
    monkeypatch.setenv("LEITORUM_USER_STORAGE_QUOTA_BYTES", "2_147_483_648")
    monkeypatch.setenv("LEITORUM_MEDIA_RETENTION_DAYS", "45")
    monkeypatch.setenv("LEITORUM_MEDIA_DELETE_ON_COMPLETED", "false")
    assert config.get_user_storage_quota_bytes() == 2 * 1024**3
    assert config.get_media_retention_days() == 45
    assert config.get_media_delete_on_completed() is False


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("LEITORUM_USER_STORAGE_QUOTA_BYTES", "um giga"),
        ("LEITORUM_USER_STORAGE_QUOTA_BYTES", "0"),
        ("LEITORUM_GLOBAL_STORAGE_QUOTA_BYTES", "-5"),
        ("LEITORUM_MEDIA_RETENTION_DAYS", "0"),
        ("LEITORUM_MEDIA_RETENTION_DAYS", "3651"),
        ("LEITORUM_MEDIA_JOB_INTERVAL_HOURS", "0"),
        ("LEITORUM_MEDIA_DELETE_ON_COMPLETED", "talvez"),
    ],
)
def test_invalid_value_names_the_variable(monkeypatch, name, value):
    monkeypatch.setenv(name, value)
    with pytest.raises(ValueError, match=name):
        config.validate_media_settings()


def test_invalid_value_prevents_startup(monkeypatch):
    monkeypatch.setenv("LEITORUM_MEDIA_RETENTION_DAYS", "trinta")
    with pytest.raises(ValueError, match="LEITORUM_MEDIA_RETENTION_DAYS"):
        with TestClient(create_app()):
            pass
