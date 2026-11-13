"""
Authentication & User Account Security Tests
=============================================
Verifies:
- MM-F-016 : User registration and login (email + password)
- MM-NF-004: Passwords hashed with bcrypt and never stored in plaintext
- MM-SR-002: bcrypt password hashing with minimum cost factor >= 10
- MM-SR-003: 30-minute session timeout & HTTP-only session cookies
- TC-AUTH-01 / TC-SEC-01 / TC-SEC-03 / TC-SEC-04
"""

import os
import sys
from datetime import timedelta
import pytest
import bcrypt

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
)

from app import app
import models


@pytest.fixture
def isolated_db(monkeypatch, tmp_path):
    """Provides a fresh isolated database for authentication testing."""
    test_db = str(tmp_path / "test_auth.db")
    monkeypatch.setattr(models, "DB_PATH", test_db)
    models.init_db()
    return test_db


@pytest.fixture
def client(isolated_db):
    """Configures a Flask test client with clean session and isolated DB."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ============================================================================
# 1. Password Hashing & Encryption Security (MM-NF-004 / MM-SR-002)
# ============================================================================

def test_password_hashing_bcrypt_properties(isolated_db):
    """
    Verifies MM-NF-004 and MM-SR-002:
    - Password is never stored in plaintext.
    - Password is hashed with bcrypt.
    - Cost factor (work factor) is at least 10 (configured to 12).
    - Salting produces unique hashes even for identical passwords.
    """
    raw_password = "SecurePassword123!"
    user_id_1 = models.create_user("user1@example.com", "Alice Smith", raw_password)
    user_id_2 = models.create_user("user2@example.com", "Bob Jones", raw_password)

    conn = models.get_db_connection()
    c = conn.cursor()
    c.execute("SELECT email, password_hash FROM users WHERE id IN (?, ?)", (user_id_1, user_id_2))
    rows = c.fetchall()
    conn.close()

    assert len(rows) == 2
    for row in rows:
        stored_hash = row["password_hash"]
        # Must not contain plaintext
        assert raw_password not in stored_hash
        # Must be a valid bcrypt hash signature ($2a$, $2b$, or $2y$)
        assert stored_hash.startswith(("$2a$", "$2b$", "$2y$"))
        # Parse cost factor: format is $2b$<rounds>$...
        parts = stored_hash.split("$")
        cost_factor = int(parts[2])
        assert cost_factor >= 10, f"Cost factor {cost_factor} must be >= 10 per MM-SR-002"

    # Salting verification: two identical passwords must yield distinct hashes
    assert rows[0]["password_hash"] != rows[1]["password_hash"]


def test_verify_user_password_helper(isolated_db):
    """Verifies password comparison against bcrypt hash."""
    user_id = models.create_user("verifier@example.com", "Verifier", "CorrectHorseBatteryStaple")
    user = models.get_user_by_email("verifier@example.com")

    assert user is not None
    assert models.verify_user_password(user, "CorrectHorseBatteryStaple") is True
    assert models.verify_user_password(user, "WrongPassword") is False
    assert models.verify_user_password(user, "") is False


# ============================================================================
# 2. Registration Endpoint Tests (MM-F-016 / TC-AUTH-01)
# ============================================================================

def test_register_new_user_success(client):
    """Tests successful registration via POST /api/auth/register."""
    payload = {
        "email": "student@pes.edu",
        "name": "Mohammed Faizan",
        "password": "SuperSecretPassword123"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201

    data = response.get_json()
    assert data["success"] is True
    assert "user" in data
    assert data["user"]["email"] == "student@pes.edu"
    assert data["user"]["name"] == "Mohammed Faizan"
    assert "id" in data["user"]
    # Passwords should never be leaked in response
    assert "password" not in data["user"]
    assert "password_hash" not in data["user"]


def test_register_duplicate_email_rejected(client):
    """Tests that registering an already existing email returns 409 Conflict."""
    payload = {
        "email": "duplicate@pes.edu",
        "name": "First User",
        "password": "Password1234"
    }
    first_res = client.post("/api/auth/register", json=payload)
    assert first_res.status_code == 201

    # Second attempt with same email
    second_res = client.post("/api/auth/register", json=payload)
    assert second_res.status_code == 409
    data = second_res.get_json()
    assert data["success"] is False
    assert "already registered" in data["error"].lower()


def test_register_invalid_email_format(client):
    """Tests that registering with invalid email formats returns 400 Bad Request."""
    invalid_emails = ["not-an-email", "missing-at.com", "@missing-username.com", "spaces in@email.com"]
    for bad_email in invalid_emails:
        payload = {
            "email": bad_email,
            "name": "Bad Email Tester",
            "password": "ValidPassword123"
        }
        res = client.post("/api/auth/register", json=payload)
        assert res.status_code == 400
        data = res.get_json()
        assert data["success"] is False
        assert "valid email" in data["error"].lower()


def test_register_short_password_rejected(client):
    """Tests that password length under 8 characters is rejected with 400 Bad Request."""
    payload = {
        "email": "short@pes.edu",
        "name": "Short Pwd",
        "password": "short"
    }
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 400
    data = res.get_json()
    assert data["success"] is False
    assert "8 characters" in data["error"]


def test_register_missing_name_rejected(client):
    """Tests that registration without name returns 400 Bad Request."""
    payload = {
        "email": "noname@pes.edu",
        "name": "   ",
        "password": "ValidPassword123"
    }
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 400


# ============================================================================
# 3. Login Endpoint Tests (MM-F-016 / TC-AUTH-01)
# ============================================================================

def test_login_success(client):
    """Tests that valid credentials return 200 OK and establish an authenticated session."""
    # Register first
    client.post("/api/auth/register", json={
        "email": "loginuser@pes.edu",
        "name": "Login User",
        "password": "ValidPassword123!"
    })

    # Perform Login
    res = client.post("/api/auth/login", json={
        "email": "loginuser@pes.edu",
        "password": "ValidPassword123!"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["user"]["email"] == "loginuser@pes.edu"
    assert data["user"]["name"] == "Login User"

    # Verify session persists across subsequent calls
    me_res = client.get("/api/auth/me")
    assert me_res.status_code == 200
    me_data = me_res.get_json()
    assert me_data["authenticated"] is True
    assert me_data["user"]["email"] == "loginuser@pes.edu"


def test_login_wrong_password_rejected(client):
    """Tests that an incorrect password returns 401 Unauthorized."""
    client.post("/api/auth/register", json={
        "email": "secureuser@pes.edu",
        "name": "Secure User",
        "password": "CorrectPassword123"
    })

    res = client.post("/api/auth/login", json={
        "email": "secureuser@pes.edu",
        "password": "WrongPassword999"
    })
    assert res.status_code == 401
    data = res.get_json()
    assert data["success"] is False
    assert "invalid email or password" in data["error"].lower()


def test_login_nonexistent_email_rejected(client):
    """Tests that non-registered email returns 401 Unauthorized."""
    res = client.post("/api/auth/login", json={
        "email": "nonexistent@pes.edu",
        "password": "SomePassword123"
    })
    assert res.status_code == 401
    data = res.get_json()
    assert data["success"] is False


def test_login_missing_fields_rejected(client):
    """Tests that missing credentials return 400 Bad Request."""
    res = client.post("/api/auth/login", json={"email": "onlyemail@pes.edu"})
    assert res.status_code == 400


# ============================================================================
# 4. Session Management & Logout Tests (MM-SR-003 / TC-SEC-04)
# ============================================================================

def test_auth_me_unauthenticated(client):
    """Tests that /api/auth/me returns authenticated: False for guests."""
    res = client.get("/api/auth/me")
    assert res.status_code == 200
    data = res.get_json()
    assert data["authenticated"] is False
    assert data["user"] is None


def test_logout_clears_session(client):
    """Tests that calling /api/auth/logout ends the authenticated session."""
    client.post("/api/auth/register", json={
        "email": "logoutuser@pes.edu",
        "name": "Logout Tester",
        "password": "Password123"
    })

    # Confirm authenticated
    res_before = client.get("/api/auth/me")
    assert res_before.get_json()["authenticated"] is True

    # Call logout
    res_logout = client.post("/api/auth/logout")
    assert res_logout.status_code == 200
    assert res_logout.get_json()["success"] is True

    # Confirm now unauthenticated
    res_after = client.get("/api/auth/me")
    assert res_after.get_json()["authenticated"] is False


def test_session_cookie_security_and_timeout():
    """
    Verifies MM-SR-003 and SAD Security Architecture:
    - Session cookie has HTTP-only flag enabled (prevents XSS cookie theft / spoofing).
    - Permanent session lifetime is exactly 30 minutes (1800 seconds).
    """
    assert app.config.get("SESSION_COOKIE_HTTPONLY") is True
    timeout = app.config.get("PERMANENT_SESSION_LIFETIME")
    assert timeout == timedelta(minutes=30)


# ============================================================================
# 5. Multi-Tenant Meeting History Isolation & Authorization (SAD Table 14 / MM-SR-004)
# ============================================================================

def test_meeting_history_scoped_to_user_account(isolated_db):
    """
    Verifies that meeting history is strictly scoped to the logged-in user account.
    User A can only see User A's meetings. User B can only see User B's meetings.
    """
    user_a_id = models.create_user("user_a@pes.edu", "User A", "Password123")
    user_b_id = models.create_user("user_b@pes.edu", "User B", "Password123")

    # Create meeting for User A
    meeting_a = models.create_meeting("User A Private Sync", "2026-11-13", user_id=user_a_id)
    # Create meeting for User B
    meeting_b = models.create_meeting("User B Strategy Session", "2026-11-13", user_id=user_b_id)

    # User A's history
    user_a_meetings = models.list_meetings(user_id=user_a_id)
    user_a_ids = [m["id"] for m in user_a_meetings]
    assert meeting_a in user_a_ids
    assert meeting_b not in user_a_ids

    # User B's history
    user_b_meetings = models.list_meetings(user_id=user_b_id)
    user_b_ids = [m["id"] for m in user_b_meetings]
    assert meeting_b in user_b_ids
    assert meeting_a not in user_b_ids


def test_unauthorized_user_cannot_access_other_users_meeting(client, isolated_db):
    """
    Verifies that User B cannot access or export User A's private meeting (HTTP 403 Forbidden).
    """
    user_a_id = models.create_user("owner@pes.edu", "Owner", "Password123")
    meeting_id = models.create_meeting("Confidential Financial Review", "2026-11-13", user_id=user_a_id)

    # Register and log in as an unauthorized user
    client.post("/api/auth/register", json={
        "email": "attacker@pes.edu",
        "name": "Attacker",
        "password": "Password123"
    })

    # Try to access Owner's meeting details
    res_details = client.get(f"/api/meetings/{meeting_id}")
    assert res_details.status_code == 403
    assert "access denied" in res_details.get_json()["error"].lower()

    # Try to export Owner's meeting
    res_export = client.get(f"/api/meetings/{meeting_id}/export")
    assert res_export.status_code == 403
    assert "access denied" in res_export.get_json()["error"].lower()
