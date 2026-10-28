"""
DOCX Export Tests
=================
Verifies that meeting minutes can be exported as a valid Word .docx document,
that table and bullet sections are formatted correctly, and that the API serves
the file for download across all expected routes and query params.
"""

import io
import os
import sys
import pytest

docx = pytest.importorskip("docx", reason="python-docx package is required for DOCX export tests")

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
)

from app import app
from generator import generate_docx_minutes
from models import init_db, create_meeting, add_action_items, update_meeting_processed

SAMPLE_ACTIONS = [
    {"task": "Prepare the Q4 budget", "assignee": "Priya", "deadline": "Friday", "status": "Pending"},
    {"task": "Review the architecture", "assignee": "Rahul", "deadline": "2026-10-30", "status": "Completed"},
]


def _generate_docx(**overrides):
    kwargs = dict(
        title="Sprint Architecture Review",
        date="2026-10-25",
        duration="00:03:15",
        attendees=["Faizan", "Kamal", "Vinay", "Anagha"],
        summary="Architecture review concluded successfully.",
        decisions=["Adopt SQLite WAL mode.", "Export in MD, PDF, and DOCX."],
        action_items=SAMPLE_ACTIONS,
    )
    kwargs.update(overrides)
    return generate_docx_minutes(**kwargs)


@pytest.fixture
def client():
    app.config["TESTING"] = True
    init_db()
    with app.test_client() as test_client:
        yield test_client


def test_generate_docx_returns_valid_docx():
    bio = _generate_docx()
    assert isinstance(bio, io.BytesIO)
    bytes_data = bio.getvalue()
    # A .docx file is a ZIP package starting with the PK zip header
    assert bytes_data.startswith(b"PK\x03\x04")

    # Load back with python-docx to verify document structure
    doc = docx.Document(bio)
    full_text = "\n".join(p.text for p in doc.paragraphs)
    assert "Sprint Architecture Review" in full_text
    assert "Faizan, Kamal, Vinay, Anagha" in full_text
    assert "Architecture review concluded successfully." in full_text
    assert "Adopt SQLite WAL mode." in full_text

    # Verify table structure
    assert len(doc.tables) == 1
    table = doc.tables[0]
    headers = [cell.text for cell in table.rows[0].cells]
    assert headers == ["#", "Task Description", "Assignee", "Deadline", "Status"]
    assert len(table.rows) == 3  # Header + 2 sample items
    assert table.rows[1].cells[1].text == "Prepare the Q4 budget"
    assert table.rows[1].cells[2].text == "Priya"


def test_generate_docx_handles_empty_fields():
    bio = _generate_docx(decisions=[], action_items=[], attendees=[])
    doc = docx.Document(bio)
    full_text = "\n".join(p.text for p in doc.paragraphs)
    assert "General Team" in full_text
    assert "No formal decisions recorded." in full_text
    assert "No action items recorded." in full_text
    assert len(doc.tables) == 0


def _make_meeting():
    meeting_id = create_meeting("DOCX API Test", "2026-10-25")
    update_meeting_processed(
        meeting_id,
        "Discussion summary for DOCX export test.",
        "Faizan: Hello team. Let's export to DOCX."
    )
    add_action_items(meeting_id, SAMPLE_ACTIONS)
    return meeting_id


@pytest.mark.parametrize("route", [
    "/api/minutes/{id}/docx",
    "/api/meetings/{id}/docx",
    "/api/meetings/{id}/export/docx",
    "/api/meetings/{id}/export?format=docx",
])
def test_docx_routes_return_downloadable_docx(client, route):
    meeting_id = _make_meeting()
    response = client.get(route.format(id=meeting_id))

    assert response.status_code == 200
    assert "wordprocessingml.document" in response.mimetype
    assert response.data.startswith(b"PK\x03\x04")
    disposition = response.headers.get("Content-Disposition", "")
    assert "attachment" in disposition
    assert f"Minutes_{meeting_id}_" in disposition
    assert disposition.endswith(".docx") or '.docx"' in disposition


def test_docx_export_unknown_meeting_returns_404(client):
    response = client.get("/api/minutes/99999999/docx")
    assert response.status_code == 404
    assert response.get_json()["success"] is False
