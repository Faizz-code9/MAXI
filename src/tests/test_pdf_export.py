"""
PDF Export Tests (US-15 / MM-F-011 / TC-GEN-02)
===============================================
Verifies that meeting minutes can be exported as a valid PDF, that the HTML
used to build it is escaped, and that the API serves the file for download.
"""

import os
import sys

import pytest

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
)

from app import app
from generator import generate_html_minutes, generate_pdf_minutes
from models import init_db, create_meeting, add_action_items, update_meeting_processed

SAMPLE_ACTIONS = [
    {"task": "Prepare the Q4 budget", "assignee": "Priya", "deadline": "Friday", "status": "Pending"},
    {"task": "Review the design", "assignee": "Rahul", "deadline": "", "status": "Completed"},
]


def _render(**overrides):
    kwargs = dict(
        title="Sprint Planning",
        date="2026-10-20",
        duration="00:45:00",
        attendees=["Priya", "Rahul"],
        summary="We planned the sprint.",
        decisions=["Use SQLite for the demo."],
        action_items=SAMPLE_ACTIONS,
    )
    kwargs.update(overrides)
    return generate_html_minutes(**kwargs)


@pytest.fixture
def client():
    app.config["TESTING"] = True
    init_db()
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture(scope="module")
def pdf_engine_available():
    if generate_pdf_minutes("<p>probe</p>") is None:
        pytest.skip("WeasyPrint/Pango not available on this machine")


# ---------------------------------------------------------------------
# HTML source of the PDF
# ---------------------------------------------------------------------

def test_html_contains_all_sections():
    doc = _render()
    for text in ["Sprint Planning", "2026-10-20", "Priya, Rahul",
                 "We planned the sprint.", "Use SQLite for the demo.",
                 "Prepare the Q4 budget", "Rahul", "Completed"]:
        assert text in doc


def test_html_handles_empty_decisions_and_actions():
    doc = _render(decisions=[], action_items=[], attendees=[])
    assert "No formal decisions were recorded." in doc
    assert "No action items recorded." in doc
    assert "General Team" in doc


def test_html_escapes_untrusted_content():
    """Transcript-derived text must never inject markup into the export."""
    doc = _render(
        title="<script>alert(1)</script>",
        summary="<img src=x onerror=alert(1)>",
        decisions=["<b>bold</b>"],
        action_items=[{"task": "<script>x</script>", "assignee": "<i>me</i>",
                       "deadline": "now", "status": "Pending"}],
    )
    assert "<script>alert(1)</script>" not in doc
    assert "<img src=x" not in doc
    assert "<b>bold</b>" not in doc
    assert "&lt;script&gt;" in doc


def test_html_does_not_double_escape_stored_titles():
    """The upload route stores titles HTML-escaped; PDF must not escape twice."""
    doc = _render(title="Q&amp;A Session")
    assert "Q&amp;A Session" in doc
    assert "&amp;amp;" not in doc


# ---------------------------------------------------------------------
# PDF bytes
# ---------------------------------------------------------------------

def test_generate_pdf_returns_valid_pdf(pdf_engine_available):
    pdf = generate_pdf_minutes(_render())
    assert pdf is not None
    assert pdf.startswith(b"%PDF-")
    assert pdf.rstrip().endswith(b"%%EOF")
    assert len(pdf) > 1000


# ---------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------

def _make_meeting():
    meeting_id = create_meeting("PDF API Test", "2026-10-21")
    update_meeting_processed(meeting_id, "Short summary.", "Priya: Hello team.")
    add_action_items(meeting_id, SAMPLE_ACTIONS)
    return meeting_id


@pytest.mark.parametrize("route", [
    "/api/minutes/{id}/pdf",
    "/api/meetings/{id}/pdf",
    "/api/meetings/{id}/export/pdf",
    "/api/meetings/{id}/export?format=pdf",
])
def test_pdf_routes_return_downloadable_pdf(client, pdf_engine_available, route):
    meeting_id = _make_meeting()
    response = client.get(route.format(id=meeting_id))

    assert response.status_code == 200
    assert response.mimetype == "application/pdf"
    assert response.data.startswith(b"%PDF-")
    disposition = response.headers["Content-Disposition"]
    assert "attachment" in disposition
    assert f"Minutes_{meeting_id}_" in disposition
    assert disposition.endswith(".pdf")


def test_pdf_export_unknown_meeting_returns_404(client):
    response = client.get("/api/minutes/99999999/pdf")
    assert response.status_code == 404
    assert response.get_json()["success"] is False


def test_pdf_export_falls_back_to_html_when_engine_missing(client, monkeypatch):
    """SAD risk R3: a PDF failure must not break the export feature."""
    import app as app_module
    monkeypatch.setattr(app_module, "generate_pdf_minutes", lambda _html: None)

    meeting_id = _make_meeting()
    response = client.get(f"/api/minutes/{meeting_id}/pdf")

    assert response.status_code == 200
    assert response.mimetype == "text/html"
    assert b"Meeting Minutes" in response.data
