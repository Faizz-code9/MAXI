"""Unit tests for the SQLite database access layer."""

import sys
from pathlib import Path

import pytest

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "backend")
)

import models


@pytest.fixture
def isolated_db(monkeypatch, tmp_path):
    """Use a fresh temporary database for each test."""
    monkeypatch.setattr(
        models, "DB_PATH", str(tmp_path / "test_minimax.db")
    )
    models.init_db()
    return models


def test_create_and_get_meeting(isolated_db):
    meeting_id = isolated_db.create_meeting(
        "Database Test Meeting",
        "2026-10-19",
        "test_audio.wav",
        "This is a test transcript.",
    )

    meeting = isolated_db.get_meeting(meeting_id)

    assert meeting is not None
    assert meeting["title"] == "Database Test Meeting"
    assert meeting["date"] == "2026-10-19"
    assert meeting["audio_filename"] == "test_audio.wav"
    assert meeting["raw_transcript"] == "This is a test transcript."
    assert meeting["action_items"] == []


def test_get_meeting_returns_none_for_missing_id(isolated_db):
    assert isolated_db.get_meeting(-1) is None


def test_add_action_items_to_meeting(isolated_db):
    meeting_id = isolated_db.create_meeting(
        "Action Item Test", "2026-10-19"
    )

    isolated_db.add_action_items(meeting_id, [{
        "task": "Prepare sprint demo",
        "assignee": "Anagha",
        "deadline": "Friday",
        "status": "Pending",
    }])

    meeting = isolated_db.get_meeting(meeting_id)

    assert len(meeting["action_items"]) == 1
    assert meeting["action_items"][0]["task"] == "Prepare sprint demo"
    assert meeting["action_items"][0]["assignee"] == "Anagha"
    assert meeting["action_items"][0]["status"] == "Pending"


def test_update_meeting_processed(isolated_db):
    meeting_id = isolated_db.create_meeting(
        "Processing Test", "2026-10-19"
    )

    isolated_db.update_meeting_processed(
        meeting_id,
        "A summary of the meeting.",
        "The cleaned transcript.",
    )

    meeting = isolated_db.get_meeting(meeting_id)

    assert meeting["summary"] == "A summary of the meeting."
    assert meeting["processed_transcript"] == "The cleaned transcript."
    assert meeting["status"] == "Processed"


def test_list_meetings_includes_created_meeting(isolated_db):
    meeting_id = isolated_db.create_meeting(
        "Meeting List Test", "2026-10-19"
    )

    meetings = isolated_db.list_meetings()

    assert any(meeting["id"] == meeting_id for meeting in meetings)
