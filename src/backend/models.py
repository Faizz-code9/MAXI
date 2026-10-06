"""
Database Models & Access Layer
==============================
Owner: Anagha Kaushik (PES1UG24AM459)
Phase: 3 - Implementation Sprint 1

Implements SQLite schema defined in SAD Section 4.6 (ER Diagram):
- Meeting (id, title, date, duration, audio_filename, raw_transcript, summary, created_at)
- ActionItem (id, meeting_id, task, assignee, deadline, status, created_at)
"""

import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "minimax.db")


def get_db_connection() -> sqlite3.Connection:
    """Creates a database connection with dict-like row access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initializes tables matching ER Diagram."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Meetings Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            date TEXT NOT NULL,
            duration TEXT DEFAULT '00:00:00',
            audio_filename TEXT,
            raw_transcript TEXT,
            processed_transcript TEXT,
            summary TEXT,
            status TEXT DEFAULT 'Uploaded',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Action Items Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS action_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_id INTEGER NOT NULL,
            task TEXT NOT NULL,
            assignee TEXT DEFAULT 'Unassigned',
            deadline TEXT DEFAULT 'TBD',
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (meeting_id) REFERENCES meetings (id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


def create_meeting(title: str, date: str, audio_filename: Optional[str] = None, raw_transcript: str = "") -> int:
    """Inserts a new meeting record and returns its ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO meetings (title, date, audio_filename, raw_transcript) VALUES (?, ?, ?, ?)",
        (title, date, audio_filename, raw_transcript)
    )
    meeting_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return meeting_id


def get_meeting(meeting_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves a meeting along with its associated action items."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM meetings WHERE id = ?", (meeting_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    meeting = dict(row)
    cursor.execute("SELECT * FROM action_items WHERE meeting_id = ?", (meeting_id,))
    meeting["action_items"] = [dict(item) for item in cursor.fetchall()]
    conn.close()
    return meeting


def list_meetings() -> List[Dict[str, Any]]:
    """Returns list of all meetings ordered by creation date desc."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, date, duration, status, created_at FROM meetings ORDER BY id DESC")
    meetings = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return meetings


def add_action_items(meeting_id: int, items: List[Dict[str, str]]) -> None:
    """Bulk inserts extracted action items for a given meeting."""
    conn = get_db_connection()
    cursor = conn.cursor()
    for item in items:
        cursor.execute(
            """INSERT INTO action_items (meeting_id, task, assignee, deadline, status)
               VALUES (?, ?, ?, ?, ?)""",
            (
                meeting_id,
                item.get("task", ""),
                item.get("assignee", "Unassigned"),
                item.get("deadline", "TBD"),
                item.get("status", "Pending")
            )
        )
    conn.commit()
    conn.close()

def update_action_item_status(action_item_id: int, status: str) -> bool:
    """Updates the status of an action item."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE action_items SET status = ? WHERE id = ?",
        (status, action_item_id)
    )

    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()

    return updated


def update_meeting_processed(meeting_id: int, summary: str, processed_transcript: str) -> None:
    """Updates meeting with generated summary and clean transcript."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE meetings SET summary = ?, processed_transcript = ?, status = 'Processed' WHERE id = ?",
        (summary, processed_transcript, meeting_id)
    )
    conn.commit()
    conn.close()


# Auto-initialize database tables on first import
init_db()
