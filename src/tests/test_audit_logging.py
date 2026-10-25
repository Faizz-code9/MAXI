"""
Audit Logging Tests (US-12 / MM-NF-006 / TC-OPS-01)
===================================================
Verifies that audit log entries are emitted for uploads and rejections, and
that their timestamps use the ISO 8601 format required by the SAD.
"""

import io
import logging
import os
import re
import sys

import pytest

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
)

from app import app, audit_logger, LOG_FORMAT, LOG_DATE_FORMAT
from models import init_db
import app as app_module

AUDIT_LOGGER = "minimax.audit"


@pytest.fixture
def client():
    """Provide a Flask test client with an initialized database."""
    app.config["TESTING"] = True
    init_db()
    with app.test_client() as test_client:
        yield test_client


def _records(caplog, level):
    return [
        r for r in caplog.records
        if r.name == AUDIT_LOGGER and r.levelno == level
    ]


def test_audit_log_timestamp_is_iso8601(caplog):
    """Verify the timestamp format of an emitted audit log."""
    with caplog.at_level(logging.INFO, logger=AUDIT_LOGGER):
        audit_logger.info("US-12 timestamp verification")

    assert caplog.records, "No audit log record was captured"

    record = caplog.records[-1]
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    actual_log_line = formatter.format(record)
    timestamp = actual_log_line.split(" [", 1)[0]

    assert re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:[+-]\d{4})?",
        timestamp,
    ), f"Timestamp is not ISO 8601: {timestamp}"


def test_rejected_extension_is_logged_as_warning(client, caplog):
    """An unsupported upload must leave a WARNING audit entry."""
    with caplog.at_level(logging.INFO, logger=AUDIT_LOGGER):
        response = client.post(
            "/api/upload",
            data={"audio": (io.BytesIO(b"text"), "notes.txt")},
            content_type="multipart/form-data",
        )

    assert response.status_code == 400
    warnings = _records(caplog, logging.WARNING)
    assert warnings, "Expected a WARNING audit record for rejected upload"
    assert "unsupported extension" in warnings[0].getMessage()


def test_missing_audio_part_is_logged_as_warning(client, caplog):
    """A request with no audio part must leave a WARNING audit entry."""
    with caplog.at_level(logging.INFO, logger=AUDIT_LOGGER):
        response = client.post(
            "/api/upload",
            data={"title": "No audio"},
            content_type="multipart/form-data",
        )

    assert response.status_code == 400
    assert any(
        "no audio file" in r.getMessage()
        for r in _records(caplog, logging.WARNING)
    )


def test_successful_upload_is_logged_as_info(client, caplog):
    """A successful upload must leave an INFO audit entry."""
    fake_mp3 = (
        b"ID3\x03\x00\x00\x00\x00\x00#TSSE\x00\x00\x00\x0f"
        b"\x00\x00\x01\xff\xfe"
    )

    with caplog.at_level(logging.INFO, logger=AUDIT_LOGGER):
        response = client.post(
            "/api/upload",
            data={
                "audio": (io.BytesIO(fake_mp3), "audit_check.mp3"),
                "title": "Audit Check",
                "date": "2026-10-01",
            },
            content_type="multipart/form-data",
        )

    assert response.status_code == 201
    infos = _records(caplog, logging.INFO)
    assert any("audit_check.mp3" in r.getMessage() for r in infos)


def test_pipeline_failure_is_logged_as_error(client, caplog, monkeypatch):
    """A processing failure must be logged at ERROR level."""
    def boom(_path):
        raise RuntimeError("simulated transcription failure")

    monkeypatch.setattr(app_module, "transcribe_audio", boom)
    fake_mp3 = b"ID3\x03\x00\x00\x00\x00\x00"

    with caplog.at_level(logging.INFO, logger=AUDIT_LOGGER):
        response = client.post(
            "/api/upload",
            data={"audio": (io.BytesIO(fake_mp3), "pipeline_fail.mp3")},
            content_type="multipart/form-data",
        )

    assert response.status_code == 500
    errors = _records(caplog, logging.ERROR)
    assert errors, "Expected an ERROR audit record for pipeline failure"
    assert "Pipeline failed" in errors[0].getMessage()

def test_pipeline_completion_is_logged(client, caplog):
    """A fully processed upload must log that the pipeline completed."""
    fake_mp3 = (
        b"ID3\x03\x00\x00\x00\x00\x00#TSSE\x00\x00\x00\x0f"
        b"\x00\x00\x01\xff\xfe"
    )

    with caplog.at_level(logging.INFO, logger=AUDIT_LOGGER):
        response = client.post(
            "/api/upload",
            data={
                "audio": (io.BytesIO(fake_mp3), "pipeline_ok.mp3"),
                "title": "Pipeline OK",
                "date": "2026-10-01",
            },
            content_type="multipart/form-data",
        )

    assert response.status_code == 201
    assert any(
        "Pipeline completed" in r.getMessage()
        for r in _records(caplog, logging.INFO)
    )
