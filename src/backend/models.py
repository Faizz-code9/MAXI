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
import bcrypt

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

    # Users Table (SAD Table 22 / MM-F-016 / MM-NF-004 / MM-SR-002)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Meetings Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT NOT NULL,
            date TEXT NOT NULL,
            duration TEXT DEFAULT '00:00:00',
            audio_filename TEXT,
            raw_transcript TEXT,
            processed_transcript TEXT,
            summary TEXT,
            status TEXT DEFAULT 'Uploaded',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
        )
    """)

    # Migration: Ensure user_id column exists on meetings table if upgrading
    cursor.execute("PRAGMA table_info(meetings)")
    columns = [row["name"] for row in cursor.fetchall()]
    if "user_id" not in columns:
        try:
            cursor.execute("ALTER TABLE meetings ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE SET NULL")
        except Exception:
            pass

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


def create_user(email: str, name: str, password: str) -> int:
    """
    Creates a new user account with bcrypt-hashed password.
    Enforces MM-NF-004 & MM-SR-002: Minimum cost factor 12 (>= 10), salted.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    salt = bcrypt.gensalt(rounds=12)
    pwd_bytes = password.encode("utf-8")
    password_hash = bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")

    cursor.execute(
        "INSERT INTO users (email, name, password_hash) VALUES (?, ?, ?)",
        (email.strip().lower(), name.strip(), password_hash)
    )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Retrieves a user by email."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE LOWER(email) = ?", (email.strip().lower(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves safe user information by ID (excluding password hash)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, name, created_at FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def verify_user_password(user: Dict[str, Any], password: str) -> bool:
    """Verifies a plaintext password against the stored bcrypt hash (MM-SR-002)."""
    stored_hash = user.get("password_hash", "")
    if not stored_hash:
        return False
    try:
        return bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))
    except Exception:
        return False


def create_meeting(
    title: str,
    date: str,
    audio_filename: Optional[str] = None,
    raw_transcript: str = "",
    user_id: Optional[int] = None
) -> int:
    """Inserts a new meeting record and returns its ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO meetings (title, date, audio_filename, raw_transcript, user_id) VALUES (?, ?, ?, ?, ?)",
        (title, date, audio_filename, raw_transcript, user_id)
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


def list_meetings(user_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """Returns list of meetings ordered by creation date desc, strictly filtered by user_id if authenticated."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if user_id is not None:
        cursor.execute(
            "SELECT id, user_id, title, date, duration, status, created_at FROM meetings WHERE user_id = ? ORDER BY id DESC",
            (user_id,)
        )
    else:
        cursor.execute("SELECT id, user_id, title, date, duration, status, created_at FROM meetings ORDER BY id DESC")
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
