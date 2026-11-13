"""
Flask REST API & Server Entry Point
===================================
Owner: Mohammed Faizan (PES1UG24AM472)
Phase: 3 - Implementation Sprint 1

Exposes REST API endpoints defined in SAD Section 4.3:
- POST /api/upload       : Uploads audio and processes full pipeline
- GET  /api/meetings     : Retrieves meeting history list
- GET  /api/meetings/<id>: Retrieves details of a specific meeting
- GET  /api/meetings/<id>/export: Exports meeting minutes as Markdown
- PUT  /api/action-items/<id>: Updates action item status
"""

import os
import re
import html
import uuid
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template, send_file, Response, session
from werkzeug.utils import secure_filename

# Configure Audit Logger (US-17 / MM-SR-006)
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT
)
audit_logger = logging.getLogger("minimax.audit")

try:
    from flask_cors import CORS
    HAS_CORS = True
except ImportError:
    HAS_CORS = False

from models import (
    init_db,
    create_meeting,
    get_meeting,
    list_meetings,
    add_action_items,
    update_action_item_status,
    update_meeting_processed,
    get_db_connection,
    create_user,
    get_user_by_email,
    get_user_by_id,
    verify_user_password
)
from transcriber import allowed_file, transcribe_audio, validate_audio_file
from preprocessor import clean_transcript
from extractor import (
    extract_attendees,
    extract_decisions,
    extract_action_items,
    generate_executive_summary
)
from generator import (
    generate_markdown_minutes,
    generate_html_minutes,
    generate_pdf_minutes,
    generate_docx_minutes
)

# Base directory setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, "uploads")
FRONTEND_TEMPLATES = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend", "templates"))
FRONTEND_STATIC = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend", "static"))

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(
    __name__,
    template_folder=FRONTEND_TEMPLATES,
    static_folder=FRONTEND_STATIC,
    static_url_path="/static"
)

if HAS_CORS:
    CORS(app)

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response

app.secret_key = os.environ.get("FLASK_SECRET_KEY", "minimax-secret-key-se-2026-auth")
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)  # MM-SR-003: 30-min session timeout
app.config["SESSION_COOKIE_HTTPONLY"] = True  # MM-SR-003 / SAD STRIDE Spoofing mitigation
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # 100 MB

EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")


# ============================================================================
# User Authentication & Account Management (MM-F-016 / MM-NF-004 / MM-SR-002)
# ============================================================================

@app.route("/api/auth/register", methods=["POST"])
def auth_register():
    """
    User registration endpoint (MM-F-016 / MM-NF-004 / MM-SR-002).
    Hashes password with bcrypt (cost factor >= 10) and creates user record.
    """
    if not request.is_json:
        return jsonify({"success": False, "error": "Request body must be JSON."}), 400

    data = request.get_json() or {}
    email = data.get("email", "").strip()
    name = data.get("name", "").strip()
    password = data.get("password", "")

    if not email or not EMAIL_REGEX.match(email):
        return jsonify({"success": False, "error": "A valid email address is required."}), 400

    if not name:
        return jsonify({"success": False, "error": "Full name is required."}), 400

    if not password or len(password) < 8:
        return jsonify({
            "success": False,
            "error": "Password must be at least 8 characters long."
        }), 400

    existing_user = get_user_by_email(email)
    if existing_user:
        audit_logger.warning("Registration rejected: email '%s' already registered.", email)
        return jsonify({"success": False, "error": "Email is already registered."}), 409

    try:
        user_id = create_user(email=email, name=name, password=password)
        audit_logger.info("New user registered successfully: id=%s email='%s'.", user_id, email)

        # Automatically log the newly registered user in
        session.permanent = True
        session["user_id"] = user_id
        session["user_email"] = email.lower()
        session["user_name"] = name

        return jsonify({
            "success": True,
            "message": "User registered successfully.",
            "user": {
                "id": user_id,
                "email": email.lower(),
                "name": name
            }
        }), 201
    except Exception as e:
        audit_logger.exception("Failed to register user '%s'.", email)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    """
    User authentication endpoint (MM-F-016 / MM-SR-002 / MM-SR-003).
    Verifies bcrypt password and initiates 30-min HTTP-only session.
    """
    if not request.is_json:
        return jsonify({"success": False, "error": "Request body must be JSON."}), 400

    data = request.get_json() or {}
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"success": False, "error": "Email and password are required."}), 400

    user = get_user_by_email(email)
    if not user or not verify_user_password(user, password):
        audit_logger.warning("Failed login attempt for email '%s'.", email)
        return jsonify({"success": False, "error": "Invalid email or password."}), 401

    session.permanent = True
    session["user_id"] = user["id"]
    session["user_email"] = user["email"]
    session["user_name"] = user["name"]
    audit_logger.info("User login successful: id=%s email='%s'.", user["id"], user["email"])

    return jsonify({
        "success": True,
        "message": "Login successful.",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"]
        }
    }), 200


@app.route("/api/auth/logout", methods=["POST"])
def auth_logout():
    """
    Logs out the current user by clearing the session (SAD Table 15 / MM-F-016).
    """
    user_email = session.get("user_email", "guest")
    session.clear()
    audit_logger.info("User logged out: email='%s'.", user_email)
    return jsonify({"success": True, "message": "Logged out successfully."}), 200


@app.route("/api/auth/me", methods=["GET"])
def auth_me():
    """
    Returns current authentication session status and user metadata.
    """
    user_id = session.get("user_id")
    if user_id:
        user = get_user_by_id(user_id)
        if user:
            return jsonify({
                "success": True,
                "authenticated": True,
                "user": user
            }), 200
        # Session references a non-existent user
        session.clear()

    return jsonify({
        "success": True,
        "authenticated": False,
        "user": None
    }), 200


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handles files exceeding the 100 MB limit (US-02 / MM-F-003)."""
    audit_logger.warning("Rejected upload: payload exceeded 100 MB limit.")
    return jsonify({
        "success": False,
        "error": "File exceeds maximum allowed limit of 100 MB."
    }), 413


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint verifying API & supported formats (US-10)."""
    return jsonify({
        "success": True,
        "status": "healthy",
        "supported_formats": ["mp3", "wav", "m4a"],
        "max_upload_mb": 100
    }), 200


@app.route("/")
def index():
    """Serves the Single Page Application dashboard."""
    return render_template("index.html")


@app.route("/api/upload", methods=["POST"])
def upload_audio():
    """
    Handles audio file upload and triggers processing pipeline:
    Upload -> Transcribe -> Clean -> Extract -> Save -> Generate
    """
    if "audio" not in request.files:
        audit_logger.warning("Upload rejected: no audio file part in request.")
        return jsonify({"success": False, "error": "No audio file provided."}), 400

    file = request.files["audio"]
    if file.filename == "":
        audit_logger.warning("Upload rejected: empty filename.")
        return jsonify({"success": False, "error": "No file selected."}), 400

    if not allowed_file(file.filename):
        audit_logger.warning("Upload rejected: unsupported extension '%s'.", file.filename)
        return jsonify({
            "success": False,
            "error": "Invalid format. Only .mp3, .wav, and .m4a are accepted."
        }), 400

    raw_title = request.form.get("title", "").strip() or f"Meeting on {datetime.now().strftime('%Y-%m-%d')}"
    title = html.escape(raw_title)
    meeting_date = html.escape(request.form.get("date", "").strip() or datetime.now().strftime("%Y-%m-%d"))

    # Sanitize filename against path traversal (US-17 / MM-SR-004)
    safe_base = secure_filename(file.filename) or "recording.mp3"
    # Timestamp + short unique id so simultaneous uploads of the same filename
    # can never overwrite each other (MM-NF-003 / SAD UUID-based naming).
    saved_filename = (
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}_{safe_base}"
    )
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], saved_filename)
    file.save(file_path)
    audit_logger.info("Saved sanitized audio upload '%s' for meeting '%s'.", saved_filename, title)

    try:
        # Step 1: Transcribe audio
        transcription_result = transcribe_audio(file_path)
        raw_text = transcription_result["raw_transcript"]
        duration = transcription_result["duration"]
        processing_time_ms = transcription_result.get("processing_time_ms", 0.0)

        # Step 2: Clean and normalize text
        cleaned_text = clean_transcript(raw_text)

        # Step 3: Extract NLP entities
        attendees = extract_attendees(cleaned_text)
        decisions = extract_decisions(cleaned_text)
        action_items = extract_action_items(cleaned_text)
        summary = generate_executive_summary(cleaned_text, decisions, action_items)

        # Step 4: Persist to SQLite Database
        user_id = session.get("user_id")
        meeting_id = create_meeting(
            title=title,
            date=meeting_date,
            audio_filename=saved_filename,
            raw_transcript=raw_text,
            user_id=user_id
        )
        update_meeting_processed(meeting_id, summary, cleaned_text)
        add_action_items(meeting_id, action_items)

        # Step 5: Generate Markdown Minutes
        markdown_doc = generate_markdown_minutes(
            title=title,
            date=meeting_date,
            duration=duration,
            attendees=attendees,
            summary=summary,
            decisions=decisions,
            action_items=action_items,
            transcript=cleaned_text
        )
        audit_logger.info("Pipeline completed for meeting %s.", meeting_id)

        return jsonify({
            "success": True,
            "meeting_id": meeting_id,
            "title": title,
            "date": meeting_date,
            "duration": duration,
            "processing_time_ms": processing_time_ms,
            "attendees": attendees,
            "summary": summary,
            "decisions": decisions,
            "action_items": action_items,
            "markdown": markdown_doc
        }), 201

    except Exception as e:
        audit_logger.exception("Pipeline failed for upload '%s'.", saved_filename)
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/meetings", methods=["GET"])
def get_meetings():
    """Retrieves meeting summaries for history view (scoped to user if authenticated)."""
    try:
        user_id = session.get("user_id")
        meetings = list_meetings(user_id=user_id)
        return jsonify({"success": True, "meetings": meetings}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/meetings/<int:meeting_id>", methods=["GET"])
def get_meeting_details(meeting_id):
    """Retrieves full details and action items for a single meeting (enforcing ownership authorization)."""
    try:
        meeting = get_meeting(meeting_id)
        if not meeting:
            return jsonify({"success": False, "error": "Meeting not found."}), 404

        user_id = session.get("user_id")
        meeting_owner_id = meeting.get("user_id")
        if meeting_owner_id is not None and user_id is not None and meeting_owner_id != user_id:
            audit_logger.warning("Access denied: user %s tried to access meeting %s owned by user %s.", user_id, meeting_id, meeting_owner_id)
            return jsonify({"success": False, "error": "Access denied. You do not have permission to view this meeting."}), 403

        # Parse attendees and decisions dynamically if needed
        transcript = meeting.get("processed_transcript") or meeting.get("raw_transcript") or ""
        attendees = extract_attendees(transcript)
        decisions = extract_decisions(transcript)

        markdown_doc = generate_markdown_minutes(
            title=meeting["title"],
            date=meeting["date"],
            duration=meeting["duration"],
            attendees=attendees,
            summary=meeting.get("summary") or "No summary recorded.",
            decisions=decisions,
            action_items=meeting.get("action_items", []),
            transcript=transcript
        )

        meeting["attendees"] = attendees
        meeting["decisions"] = decisions
        meeting["markdown"] = markdown_doc

        return jsonify({"success": True, "meeting": meeting}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/meetings/<int:meeting_id>/export", methods=["GET"])
def export_meeting(meeting_id):
    """Exports structured minutes as downloadable Markdown file (enforcing ownership authorization)."""
    try:
        meeting = get_meeting(meeting_id)
        if not meeting:
            return jsonify({"success": False, "error": "Meeting not found."}), 404

        user_id = session.get("user_id")
        meeting_owner_id = meeting.get("user_id")
        if meeting_owner_id is not None and user_id is not None and meeting_owner_id != user_id:
            audit_logger.warning("Access denied: user %s tried to export meeting %s owned by user %s.", user_id, meeting_id, meeting_owner_id)
            return jsonify({"success": False, "error": "Access denied. You do not have permission to export this meeting."}), 403

        transcript = meeting.get("processed_transcript") or meeting.get("raw_transcript") or ""
        attendees = extract_attendees(transcript)
        decisions = extract_decisions(transcript)

        markdown_doc = generate_markdown_minutes(
            title=meeting["title"],
            date=meeting["date"],
            duration=meeting["duration"],
            attendees=attendees,
            summary=meeting.get("summary") or "",
            decisions=decisions,
            action_items=meeting.get("action_items", []),
            transcript=transcript
        )

        # Check format parameter
        fmt = request.args.get("format", "").lower()
        if fmt == "pdf":
            return export_meeting_pdf(meeting_id)
        if fmt == "docx":
            return export_meeting_docx(meeting_id)

        filename = f"Minutes_{meeting_id}_{datetime.now().strftime('%Y%m%d')}.md"
        return Response(
            markdown_doc,
            mimetype="text/markdown; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/minutes/<int:meeting_id>/pdf", methods=["GET"])
@app.route("/api/meetings/<int:meeting_id>/pdf", methods=["GET"])
@app.route("/api/meetings/<int:meeting_id>/export/pdf", methods=["GET"])
def export_meeting_pdf(meeting_id):
    """
    Exports structured meeting minutes formatted for PDF printing/downloading.
    Provides styled print layout adhering to SAD Section 4.3 (/api/minutes/{id}/pdf).
    """
    try:
        meeting = get_meeting(meeting_id)
        if not meeting:
            return jsonify({"success": False, "error": "Meeting not found."}), 404

        transcript = meeting.get("processed_transcript") or meeting.get("raw_transcript") or ""
        attendees = extract_attendees(transcript)
        decisions = extract_decisions(transcript)
        action_items = meeting.get("action_items", [])

        html_doc = generate_html_minutes(
            title=meeting["title"],
            date=meeting["date"],
            duration=meeting.get("duration"),
            attendees=attendees,
            summary=meeting.get("summary") or "No summary recorded.",
            decisions=decisions,
            action_items=action_items,
            auto_print=request.args.get("autoprint", "").lower() == "true",
        )

        pdf_bytes = generate_pdf_minutes(html_doc)
        if pdf_bytes is None:
            # WeasyPrint unavailable: fall back to the printable HTML view.
            audit_logger.warning(
                "PDF engine unavailable; served HTML fallback for meeting %s.",
                meeting_id,
            )
            return Response(html_doc, mimetype="text/html")

        filename = f"Minutes_{meeting_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
        audit_logger.info("Exported PDF minutes for meeting %s.", meeting_id)
        return Response(
            pdf_bytes,
            mimetype="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500





@app.route("/api/minutes/<int:meeting_id>/docx", methods=["GET"])
@app.route("/api/meetings/<int:meeting_id>/docx", methods=["GET"])
@app.route("/api/meetings/<int:meeting_id>/export/docx", methods=["GET"])
def export_meeting_docx(meeting_id):
    """Exports structured meeting minutes as a Word .docx document."""
    try:
        meeting = get_meeting(meeting_id)
        if not meeting:
            return jsonify({"success": False, "error": "Meeting not found."}), 404

        transcript = meeting.get("processed_transcript") or meeting.get("raw_transcript") or ""
        attendees = extract_attendees(transcript)
        decisions = extract_decisions(transcript)
        action_items = meeting.get("action_items", [])

        docx_bio = generate_docx_minutes(
            title=meeting["title"],
            date=meeting["date"],
            duration=meeting.get("duration"),
            attendees=attendees,
            summary=meeting.get("summary") or "No summary recorded.",
            decisions=decisions,
            action_items=action_items,
        )

        filename = f"Minutes_{meeting_id}_{datetime.now().strftime('%Y%m%d')}.docx"
        audit_logger.info("Exported DOCX minutes for meeting %s.", meeting_id)
        return send_file(
            docx_bio,
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            as_attachment=True,
            download_name=filename,
        )
    except Exception as e:
        audit_logger.exception("Failed to export DOCX for meeting %s.", meeting_id)
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/action-items/<int:item_id>", methods=["PUT"])
def update_action_item(item_id):
    """Updates an action item's status to Pending or Completed."""
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "error": "A JSON request body is required."
        }), 400

    new_status = data.get("status")

    if not isinstance(new_status, str) or new_status not in {
        "Pending",
        "Completed"
    }:
        return jsonify({
            "success": False,
            "error": "Status must be Pending or Completed."
        }), 400

    try:
        updated = update_action_item_status(item_id, new_status)
    except Exception:
        audit_logger.exception(
            "Failed to update action item %s", item_id
        )
        return jsonify({
            "success": False,
            "error": "Failed to update action item."
        }), 500

    if not updated:
        return jsonify({
            "success": False,
            "error": "Action item not found."
        }), 404

    return jsonify({
        "success": True,
        "status": new_status
    }), 200


if __name__ == "__main__":
    init_db()
    print("🚀 MiniMax Server running at http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)
