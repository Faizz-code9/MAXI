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
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_file, Response
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
from generator import generate_markdown_minutes

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
    return response

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # 100 MB


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
        return jsonify({"success": False, "error": "No audio file provided."}), 400

    file = request.files["audio"]
    if file.filename == "":
        return jsonify({"success": False, "error": "No file selected."}), 400

    if not allowed_file(file.filename):
        return jsonify({
            "success": False,
            "error": "Invalid format. Only .mp3, .wav, and .m4a are accepted."
        }), 400

    title = request.form.get("title", "").strip() or f"Meeting on {datetime.now().strftime('%Y-%m-%d')}"
    meeting_date = request.form.get("date", "").strip() or datetime.now().strftime("%Y-%m-%d")

    # Save audio file to uploads/
    saved_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], saved_filename)
    file.save(file_path)

    try:
        # Step 1: Transcribe audio
        transcription_result = transcribe_audio(file_path)
        raw_text = transcription_result["raw_transcript"]
        duration = transcription_result["duration"]

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

        return jsonify({
            "success": True,
            "meeting_id": meeting_id,
            "title": title,
            "date": meeting_date,
            "duration": duration,
            "attendees": attendees,
            "summary": summary,
            "decisions": decisions,
            "action_items": action_items,
            "markdown": markdown_doc
        }), 201

    except Exception as e:
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

        decisions_html = "".join(f"<li>{d}</li>" for d in decisions) if decisions else "<li>No formal decisions recorded.</li>"
        action_rows = "".join(
            f"<tr><td>{i}</td><td>{item.get('task','')}</td><td><strong>{item.get('assignee','Unassigned')}</strong></td><td><code>{item.get('deadline','TBD')}</code></td><td>{item.get('status','Pending')}</td></tr>"
            for i, item in enumerate(action_items, 1)
        ) if action_items else '<tr><td colspan="5" style="text-align:center;">No action items recorded.</td></tr>'

        html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Meeting Minutes - {meeting['title']}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 40px; color: #0f172a; line-height: 1.6; max-width: 850px; margin: auto; }}
    h1 {{ color: #4338ca; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-bottom: 12px; }}
    h2 {{ color: #1e1b4b; margin-top: 24px; border-bottom: 1px solid #f1f5f9; padding-bottom: 4px; }}
    .meta-box {{ background: #f8fafc; border-left: 4px solid #4338ca; padding: 12px 16px; border-radius: 4px; margin: 16px 0; }}
    .meta-box p {{ margin: 4px 0; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 12px; }}
    th, td {{ border: 1px solid #cbd5e1; padding: 8px 12px; text-align: left; font-size: 14px; }}
    th {{ background: #f1f5f9; font-weight: 600; text-transform: uppercase; font-size: 12px; }}
    ul {{ padding-left: 20px; }}
    li {{ margin-bottom: 6px; }}
    .summary-text {{ background: #f8fafc; padding: 12px 16px; border-radius: 6px; border: 1px solid #e2e8f0; }}
    @media print {{
      body {{ padding: 0; }}
      @page {{ margin: 1.5cm; }}
    }}
  </style>
  <script>
    window.onload = function() {{
      if (window.location.search.includes('print=true') || window.location.search.includes('autoprint=true')) {{
        window.print();
      }}
    }};
  </script>
</head>
<body>
  <h1>📋 Meeting Minutes: {meeting['title']}</h1>
  <div class="meta-box">
    <p><strong>Date:</strong> {meeting['date']} &nbsp;|&nbsp; <strong>Duration:</strong> {meeting.get('duration', '00:02:25')} &nbsp;|&nbsp; <strong>Status:</strong> Approved</p>
    <p><strong>Attendees:</strong> {', '.join(attendees) if attendees else 'General Project Team'}</p>
  </div>

  <h2>📝 Executive Summary</h2>
  <div class="summary-text">{meeting.get('summary', 'No summary recorded.')}</div>

  <h2>⚖️ Key Decisions</h2>
  <ul>{decisions_html}</ul>

  <h2>✅ Action Items</h2>
  <table>
    <thead>
      <tr>
        <th>#</th>
        <th>Task Description</th>
        <th>Assignee</th>
        <th>Deadline</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>{action_rows}</tbody>
  </table>
</body>
</html>"""

        return Response(html_doc, mimetype="text/html")
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/action-items/<int:item_id>", methods=["PUT"])
def update_action_item(item_id):
    """Toggles action item status (Pending <-> Completed)."""
    data = request.get_json() or {}
    new_status = data.get("status", "Completed")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE action_items SET status = ? WHERE id = ?", (new_status, item_id))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "status": new_status}), 200


if __name__ == "__main__":
    init_db()
    print("🚀 MiniMax Server running at http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)
