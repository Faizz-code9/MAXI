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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app import app
from models import init_db


@pytest.fixture
def client():
    app.config["TESTING"] = True
    init_db()
    with app.test_client() as client:
        yield client


def test_index_page(client):
    """Verifies that the dashboard HTML loads successfully."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"MiniMax" in response.data


def test_get_meetings_list(client):
    """Verifies that GET /api/meetings returns JSON list."""
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
        "date": "2026-10-01"
    }
    response = client.post("/api/upload", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["success"] is False
    assert "Invalid format" in json_data["error"]


def test_upload_valid_audio_stub(client):
    """Verifies complete upload pipeline with a valid audio file."""
    fake_audio_bytes = b"ID3\x03\x00\x00\x00\x00\x00#TSSE\x00\x00\x00\x0f\x00\x00\x01\xff\xfeLavf58.29.100"
    data = {
        "audio": (io.BytesIO(fake_audio_bytes), "sample_sprint_meeting.mp3"),
        "title": "Sprint 1 Integration Meeting",
        "date": "2026-10-01"
    }
    response = client.post("/api/upload", data=data, content_type="multipart/form-data")
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data["success"] is True
    assert "meeting_id" in json_data
    assert json_data["title"] == "Sprint 1 Integration Meeting"
    assert len(json_data["action_items"]) > 0
