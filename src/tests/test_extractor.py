"""
Unit Tests for Text Preprocessor & Extractor Modules
===================================================
Owner: Anagha Kaushik (PES1UG24AM459) & Vinay M Rampur (PES1UG24AM455)
Phase: 3 - Implementation Sprint 1
"""

import sys
import os
import pytest

# Add backend directory to sys.path
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "backend")
    )
)

from preprocessor import clean_transcript, remove_filler_words
from extractor import (
    extract_attendees,
    extract_decisions,
    extract_action_items,
    generate_executive_summary
)
from generator import generate_markdown_minutes, save_markdown_minutes


# ============================================================
# PREPROCESSOR TESTS
# ============================================================

def test_remove_filler_words():
    raw = "Um, Alice will, like, basically complete the report, you know."

    cleaned = remove_filler_words(raw)

    assert "um" not in cleaned.lower()
    assert "like" not in cleaned.lower()
    assert "basically" not in cleaned.lower()
    assert "Alice" in cleaned


# ============================================================
# ATTENDEE TESTS
# ============================================================

def test_extract_attendees():
    dialogue = (
        "[00:01:00] Alice: Hello everyone.\n"
        "[00:01:10] Bob: Hi Alice.\n"
        "[00:01:20] Charlie: Good morning.\n"
    )

    attendees = extract_attendees(dialogue)

    assert "Alice" in attendees
    assert "Bob" in attendees
    assert "Charlie" in attendees


def test_extract_attendees_normalizes_names():
    transcript = """
    [00:01:00] alice: Hello.
    [00:02:00] BOB: Hi.
    [00:03:00] Kamal: Good morning.
    """

    attendees = extract_attendees(transcript)

    assert "Alice" in attendees
    assert "Bob" in attendees
    assert "Kamal" in attendees


# ============================================================
# DECISION TESTS
# ============================================================

def test_extract_decisions():
    dialogue = (
        "Alice: Decision: SQLite will be used for Sprint 1.\n"
        "Bob: We decided to deploy locally on port 5000.\n"
    )

    decisions = extract_decisions(dialogue)

    assert len(decisions) >= 2
    assert any("sqlite" in d.lower() for d in decisions)


def test_extract_multiple_decisions():
    transcript = """
    [00:01:00] Alice: Decision: We will use Flask.
    [00:02:00] Bob: We decided to use SQLite.
    [00:03:00] Kamal: Consensus is to use REST APIs.
    """

    decisions = extract_decisions(transcript)

    assert len(decisions) == 3
    assert any("Flask" in decision for decision in decisions)
    assert any("SQLite" in decision for decision in decisions)
    assert any("REST APIs" in decision for decision in decisions)


# ============================================================
# ACTION ITEM TESTS
# ============================================================

def test_extract_action_items():
    dialogue = (
        "Action item: Bob will finalize the database models by Friday\n"
        "Charlie to implement drag-and-drop audio upload UI by Monday\n"
    )

    items = extract_action_items(dialogue)

    assert len(items) >= 2

    bob_item = next(
        (i for i in items if i["assignee"].lower() == "bob"),
        None
    )

    assert bob_item is not None
    assert "database" in bob_item["task"].lower()
    assert "friday" in bob_item["deadline"].lower()


def test_extract_action_item_with_deadline():
    transcript = """
    [00:01:00] Alice: Bob will finalize the database models by Friday.
    """

    items = extract_action_items(transcript)

    assert len(items) == 1
    assert items[0]["assignee"] == "Bob"
    assert items[0]["task"] == "finalize the database models"
    assert items[0]["deadline"] == "Friday"
    assert items[0]["status"] == "Pending"


def test_extract_action_item_without_deadline():
    transcript = """
    [00:01:00] Alice: Bob will update the API documentation.
    """

    items = extract_action_items(transcript)

    assert len(items) == 1
    assert items[0]["assignee"] == "Bob"
    assert items[0]["task"] == "update the API documentation"
    assert items[0]["deadline"] == "TBD"
    assert items[0]["status"] == "Pending"


def test_extract_todo_action_item():
    transcript = """
    [00:02:00] Alice: TODO: Kamal will update the dashboard by Monday.
    """

    items = extract_action_items(transcript)

    assert len(items) == 1
    assert items[0]["assignee"] == "Kamal"
    assert items[0]["task"] == "update the dashboard"
    assert items[0]["deadline"] == "Monday"


def test_extract_to_pattern_action_item():
    transcript = """
    [00:03:00] Alice: Charlie to implement the upload UI by Monday.
    """

    items = extract_action_items(transcript)

    assert len(items) == 1
    assert items[0]["assignee"] == "Charlie"
    assert items[0]["task"] == "implement the upload UI"
    assert items[0]["deadline"] == "Monday"


def test_extract_multiple_action_items():
    transcript = """
    [00:01:00] Alice: Bob will update the API by Friday.
    [00:02:00] Bob: Kamal will test the dashboard by Monday.
    [00:03:00] Kamal: Charlie will deploy the application tomorrow.
    """

    items = extract_action_items(transcript)

    assert len(items) == 3

    assert items[0]["assignee"] == "Bob"
    assert items[0]["deadline"] == "Friday"

    assert items[1]["assignee"] == "Kamal"
    assert items[1]["deadline"] == "Monday"

    assert items[2]["assignee"] == "Charlie"
    assert items[2]["deadline"] == "tomorrow"


def test_action_items_are_deduplicated():
    transcript = """
    [00:01:00] Alice: Bob will update the API by Friday.
    [00:02:00] Bob: Bob will update the API by Friday.
    """

    items = extract_action_items(transcript)

    assert len(items) == 1


# ============================================================
# MARKDOWN GENERATOR TEST
# ============================================================

def test_generate_markdown_minutes():
    doc = generate_markdown_minutes(
        title="Weekly Sprint Sync",
        date="2026-10-01",
        duration="00:05:00",
        attendees=["Alice", "Bob"],
        summary="Brief summary of meeting.",
        decisions=["Use SQLite"],
        action_items=[
            {
                "task": "Build UI",
                "assignee": "Charlie",
                "deadline": "Monday",
                "status": "Pending"
            }
        ],
        transcript="Alice: Test"
    )

    assert "# 📋 Meeting Minutes: Weekly Sprint Sync" in doc
    assert "Alice, Bob" in doc
    assert "Charlie" in doc


def test_save_markdown_minutes(tmp_path):
    content = "# Meeting Minutes\n\nTest meeting."
    file_path = save_markdown_minutes(
        content,
        "test_meeting",
        str(tmp_path)
    )

    assert file_path.endswith("test_meeting.md")

    with open(file_path, "r", encoding="utf-8") as file:
        saved_content = file.read()

    assert saved_content == content

