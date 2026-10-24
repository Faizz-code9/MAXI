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
import html
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_file, Response
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
    get_db_connection
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
    generate_pdf_minutes
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

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # 100 MB


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
    saved_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{safe_base}"
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
        meeting_id = create_meeting(
            title=title,
            date=meeting_date,
            audio_filename=saved_filename,
            raw_transcript=raw_text
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
    """Retrieves all meeting summaries for history view."""
    try:
        meetings = list_meetings()
        return jsonify({"success": True, "meetings": meetings}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/meetings/<int:meeting_id>", methods=["GET"])
def get_meeting_details(meeting_id):
    """Retrieves full details and action items for a single meeting."""
    try:
        meeting = get_meeting(meeting_id)
        if not meeting:
            return jsonify({"success": False, "error": "Meeting not found."}), 404

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
    """Exports structured minutes as downloadable Markdown file."""
    try:
        meeting = get_meeting(meeting_id)
        if not meeting:
            return jsonify({"success": False, "error": "Meeting not found."}), 404

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

        # Check if PDF format is requested
        if request.args.get("format", "").lower() == "pdf":
            return export_meeting_pdf(meeting_id)

        filename = f"Minutes_{meeting_id}_{datetime.now().strftime('%Y%m%d')}.md"
        return Response(
            markdown_doc,
            mimetype="text/markdown",
            headers={"Content-Disposition": f"attachment;filename={filename}"}
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
