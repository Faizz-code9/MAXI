"""
Integration Tests for Flask REST API Endpoints
==============================================
Owner: Anagha Kaushik (PES1UG24AM459) & Mohammed Faizan (PES1UG24AM472)
Phase: 3 - Implementation Sprint 1
"""

import sys
import os
import io
import pytest

# Add backend directory to sys.path
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
)

from app import app
from models import (
    init_db,
    get_db_connection,
    create_meeting,
    add_action_items,
    update_action_item_status,
)


@pytest.fixture
def client():
    """Provide a Flask test client with an initialized database."""
    app.config["TESTING"] = True
    init_db()

    with app.test_client() as test_client:
        yield test_client


def test_index_page(client):
    """Verifies that the dashboard HTML loads successfully."""
    response = client.get("/")

    assert response.status_code == 200
    assert b"MiniMax" in response.data


def test_get_meetings_list(client):
    """Verifies that GET /api/meetings returns a JSON list."""
    response = client.get("/api/meetings")

    assert response.status_code == 200

    data = response.get_json()
    assert data["success"] is True
    assert isinstance(data["meetings"], list)


def test_upload_invalid_file(client):
    """Verifies that non-audio files are rejected."""
    data = {
        "audio": (io.BytesIO(b"fake text content"), "test.txt"),
        "title": "Invalid Test",
        "date": "2026-10-01",
    }

    response = client.post(
        "/api/upload",
        data=data,
        content_type="multipart/form-data",
    )

    assert response.status_code == 400

    json_data = response.get_json()
    assert json_data["success"] is False
    assert "Invalid format" in json_data["error"]


def test_upload_valid_audio_stub(client):
    """Verifies the upload pipeline with a valid audio-file stub."""
    fake_audio_bytes = (
        b"ID3\x03\x00\x00\x00\x00\x00#TSSE\x00\x00\x00\x0f"
        b"\x00\x00\x01\xff\xfeLavf58.29.100"
    )

    data = {
        "audio": (
            io.BytesIO(fake_audio_bytes),
            "sample_sprint_meeting.mp3",
        ),
        "title": "Sprint 1 Integration Meeting",
        "date": "2026-10-01",
    }

    response = client.post(
        "/api/upload",
        data=data,
        content_type="multipart/form-data",
    )

    assert response.status_code == 201

    json_data = response.get_json()
    assert json_data["success"] is True
    assert "meeting_id" in json_data
    assert json_data["title"] == "Sprint 1 Integration Meeting"
    assert len(json_data["action_items"]) > 0


def test_update_action_item_status():
    """Verifies the model helper updates an action item's status."""
    init_db()

    meeting_id = create_meeting(
        "Status Test Meeting",
        "2026-10-05",
    )

    add_action_items(
        meeting_id,
        [
            {
                "task": "Test task",
                "assignee": "Alice",
                "deadline": "Friday",
                "status": "Pending",
            }
        ],
    )

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM action_items WHERE meeting_id = ?",
            (meeting_id,),
        )
        row = cursor.fetchone()
        assert row is not None
        action_item_id = row["id"]
    finally:
        conn.close()

    updated = update_action_item_status(
        action_item_id,
        "Completed",
    )

    assert updated is True

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT status FROM action_items WHERE id = ?",
            (action_item_id,),
        )
        row = cursor.fetchone()
        assert row is not None
        status = row["status"]
    finally:
        conn.close()

    assert status == "Completed"


# ---------------------------------------------------------------------
# US-16: Interactive Action Item Status Updating
# PUT /api/action-items/<id>
# ---------------------------------------------------------------------

def _create_action_item_for_status_api_test():
    """Create a meeting and Pending action item for API tests."""
    init_db()

    meeting_id = create_meeting(
        "US-16 Status API Test",
        "2026-10-21",
    )

    add_action_items(
        meeting_id,
        [
            {
                "task": "Verify status update",
                "assignee": "Alice",
                "deadline": "Friday",
                "status": "Pending",
            }
        ],
    )

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM action_items WHERE meeting_id = ?",
            (meeting_id,),
        )
        row = cursor.fetchone()
        assert row is not None
        return row["id"]
    finally:
        conn.close()


def test_status_api_marks_item_completed(client):
    """US-16: PUT endpoint marks an action item as Completed."""
    item_id = _create_action_item_for_status_api_test()

    response = client.put(
        f"/api/action-items/{item_id}",
        json={"status": "Completed"},
    )

    assert response.status_code == 200

    data = response.get_json()
    assert data["success"] is True
    assert data["status"] == "Completed"

    # Verify the persisted status in the database.
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT status FROM action_items WHERE id = ?",
            (item_id,),
        )
        row = cursor.fetchone()
        assert row is not None
        assert row["status"] == "Completed"
    finally:
        conn.close()


def test_status_api_marks_item_pending(client):
    """US-16: A Completed action item can be changed back to Pending."""
    item_id = _create_action_item_for_status_api_test()

    completed_response = client.put(
        f"/api/action-items/{item_id}",
        json={"status": "Completed"},
    )
    assert completed_response.status_code == 200

    response = client.put(
        f"/api/action-items/{item_id}",
        json={"status": "Pending"},
    )

    assert response.status_code == 200

    data = response.get_json()
    assert data["success"] is True
    assert data["status"] == "Pending"

    # Verify the persisted status in the database.
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT status FROM action_items WHERE id = ?",
            (item_id,),
        )
        row = cursor.fetchone()
        assert row is not None
        assert row["status"] == "Pending"
    finally:
        conn.close()


def test_status_api_rejects_invalid_status(client):
    """US-16: The API rejects statuses outside Pending and Completed."""
    item_id = _create_action_item_for_status_api_test()

    response = client.put(
        f"/api/action-items/{item_id}",
        json={"status": "In Progress"},
    )

    assert response.status_code == 400

    data = response.get_json()
    assert data["success"] is False
    assert "error" in data


def test_status_api_rejects_missing_json_body(client):
    """US-16: The API rejects a request without a JSON body."""
    item_id = _create_action_item_for_status_api_test()

    response = client.put(
        f"/api/action-items/{item_id}",
        data="",
        content_type="application/json",
    )

    assert response.status_code == 400

    data = response.get_json()
    assert data["success"] is False
    assert "error" in data


def test_status_api_returns_404_for_unknown_item(client):
    """US-16: The API returns 404 for a nonexistent action item."""
    response = client.put(
        "/api/action-items/99999999",
        json={"status": "Completed"},
    )

    assert response.status_code == 404

    data = response.get_json()
    assert data["success"] is False
    assert "error" in data


# ---------------------------------------------------------------------
# Existing PDF export tests
# ---------------------------------------------------------------------

def test_export_pdf_endpoint(client):
    """Verifies that PDF export endpoints return a printable document."""
    meeting_id = create_meeting(
        "PDF Export Test",
        "2026-10-06",
    )

    # Test SAD 4.3 route.
    resp1 = client.get(f"/api/minutes/{meeting_id}/pdf")
    assert resp1.status_code == 200
    assert b"Meeting Minutes" in resp1.data

    # Test alias route.
    resp2 = client.get(f"/api/meetings/{meeting_id}/export/pdf")
    assert resp2.status_code == 200
    assert b"Meeting Minutes" in resp2.data

    # Test format query parameter.
    resp3 = client.get(f"/api/meetings/{meeting_id}/export?format=pdf")
    assert resp3.status_code == 200
    assert b"Meeting Minutes" in resp3.data


def test_health_check_endpoint(client):
    """Verifies GET /api/health for US-10 (#14) and US-02 (#6)."""
    response = client.get("/api/health")

    assert response.status_code == 200

    data = response.get_json()
    assert data["success"] is True
    assert data["status"] == "healthy"
    assert "mp3" in data["supported_formats"]
    assert data["max_upload_mb"] == 100


def test_filename_sanitization_security(client):
    """Verifies path traversal and XSS sanitization for US-17 (#21)."""
    fake_audio_bytes = b"ID3\x03\x00\x00\x00\x00\x00#TSSE"

    data = {
        "audio": (
            io.BytesIO(fake_audio_bytes),
            "../../evil_path/audio.mp3",
        ),
        "title": "<script>alert(1)</script>Security Review",
        "date": "2026-10-10",
    }

    response = client.post(
        "/api/upload",
        data=data,
        content_type="multipart/form-data",
    )

    assert response.status_code == 201

    json_data = response.get_json()
    assert json_data["success"] is True
    assert "<script>" not in json_data["title"]
    assert "&lt;script&gt;" in json_data["title"]
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
