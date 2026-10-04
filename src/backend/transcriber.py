"""
Audio Transcriber Module
========================
Owner: Mohammed Faizan (PES1UG24AM472)
Phase: 3 - Implementation Sprint 1

Handles audio file ingestion, validation, and speech-to-text transcription.
Supports: MP3, WAV, M4A format verification and size checks (<= 100 MB).
"""

import os
from typing import Tuple, Dict, Any

ALLOWED_EXTENSIONS = {"mp3", "wav", "m4a"}
MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024  # 100 MB


def allowed_file(filename: str) -> bool:
    """Checks if the uploaded file has a supported audio extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_audio_file(file_path: str) -> Tuple[bool, str]:
    """
    Validates audio file existence, format, and size limit.
    Returns (is_valid, error_message).
    """
    if not os.path.exists(file_path):
        return False, "File does not exist."

    filename = os.path.basename(file_path)
    if not allowed_file(filename):
        return False, f"Unsupported file format. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"

    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE_BYTES:
        return False, f"File exceeds maximum limit of 100 MB (current size: {file_size / (1024 * 1024):.1f} MB)."

    return True, ""


def transcribe_audio(file_path: str) -> Dict[str, Any]:
    """
    Transcribes audio into structured dialogue text with speaker tags and timestamps.
    In Sprint 1, implements an intelligent transcription stub that yields realistic
    dialogue turns, speakers, and action items.
    """
    is_valid, error = validate_audio_file(file_path)
    if not is_valid:
        raise ValueError(error)

    # Base realistic transcription stub for Sprint 1 demo
    filename = os.path.basename(file_path)
    stub_transcript = (
        f"[00:00:05] Lead: Welcome team to the meeting regarding {filename}.\n"
        "[00:00:15] Backend: We have set up the database and REST API endpoints.\n"
        "[00:00:30] Frontend: The dashboard wireframes and drag-and-drop uploader are designed.\n"
        "[00:00:50] QA: Test cases and verification suites are outlined for the pipeline.\n"
        "[00:01:10] Lead: Agreed. Decision: We are approving Sprint 1 architecture.\n"
        "[00:01:25] Lead: Action item: Vinay to refine regex extractor for task detection by Friday.\n"
        "[00:01:45] Lead: Action item: Kamal will connect the audio upload form to the API by Monday.\n"
        "[00:02:00] Lead: Action item: Anagha to run pytest test suites and generate markdown minutes by Wednesday.\n"
        "[00:02:20] Lead: Meeting adjourned. Great work everyone!"
    )

    return {
        "audio_filename": filename,
        "duration": "00:02:25",
        "raw_transcript": stub_transcript,
        "status": "Transcribed"
    }
