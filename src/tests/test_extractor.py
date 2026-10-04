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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from preprocessor import clean_transcript, remove_filler_words
from extractor import (
    extract_attendees,
    extract_decisions,
    extract_action_items,
    generate_executive_summary
)
from generator import generate_markdown_minutes


def test_remove_filler_words():
    raw = "Um, Alice will, like, basically complete the report, you know."
    cleaned = remove_filler_words(raw)
    assert "um" not in cleaned.lower()
    assert "like" not in cleaned.lower()
    assert "basically" not in cleaned.lower()
    assert "Alice" in cleaned


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


def test_extract_decisions():
    dialogue = (
        "Alice: Decision: SQLite will be used for Sprint 1.\n"
        "Bob: We decided to deploy locally on port 5000.\n"
    )
    decisions = extract_decisions(dialogue)
    assert len(decisions) >= 2
    assert any("sqlite" in d.lower() for d in decisions)


def test_extract_action_items():
    dialogue = (
        "Action item: Bob will finalize the database models by Friday\n"
        "Charlie to implement drag-and-drop audio upload UI by Monday\n"
    )
    items = extract_action_items(dialogue)
    assert len(items) >= 2

    bob_item = next((i for i in items if i["assignee"].lower() == "bob"), None)
    assert bob_item is not None
    assert "database" in bob_item["task"].lower()
    assert "friday" in bob_item["deadline"].lower()


def test_generate_markdown_minutes():
    doc = generate_markdown_minutes(
        title="Weekly Sprint Sync",
        date="2026-10-01",
        duration="00:05:00",
        attendees=["Alice", "Bob"],
        summary="Brief summary of meeting.",
        decisions=["Use SQLite"],
        action_items=[{"task": "Build UI", "assignee": "Charlie", "deadline": "Monday", "status": "Pending"}],
        transcript="Alice: Test"
    )
    assert "# 📋 Meeting Minutes: Weekly Sprint Sync" in doc
    assert "Alice, Bob" in doc
    assert "Use SQLite" in doc
    assert "Charlie" in doc
