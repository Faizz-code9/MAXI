"""
Performance & Concurrency Tests (US-18)
=======================================
Owner: Anagha Kaushik (PES1UG24AM459)

TC-PERF-01 / MM-NF-001:
    A 30-minute audio stub must be processed and its minutes generated within
    60 seconds (90th percentile of repeated runs).

TC-PERF-02 / MM-NF-003:
    At least 5 users must be able to upload and process simultaneously with no
    errors.

These tests start the real Flask app on a local port (threaded, like a live
server) and send genuine multipart HTTP uploads, so timings include request
parsing, file save, the whole processing pipeline, SQLite writes and
Markdown generation.

Measured values are printed (run with `pytest -s`) and attached to the JUnit
XML as test properties, so CI keeps the evidence.
"""

import http.client
import json
import math
import os
import statistics
import sys
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

import pytest
from werkzeug.serving import make_server

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
)

from app import app
from models import init_db, get_meeting
from preprocessor import clean_transcript
from extractor import (
    extract_attendees,
    extract_decisions,
    extract_action_items,
    generate_executive_summary,
)
from generator import generate_markdown_minutes

# ---------------------------------------------------------------------------
# Targets taken from the SRS
# ---------------------------------------------------------------------------
MAX_PROCESSING_SECONDS = 60          # MM-NF-001
RUNS_FOR_PERCENTILE = 10             # sample size for the 90th percentile
REQUIRED_CONCURRENT_USERS = 5        # MM-NF-003
EXTRA_HEADROOM_USERS = 10            # twice the requirement, for margin

# A 30-minute MP3 at 128 kbps is about 28.8 MB.
THIRTY_MIN_AUDIO_BYTES = 30 * 60 * 16_000
PERF_FILE_TAG = "perfqa"             # used to find and clean up test uploads


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def percentile(values, pct):
    """Nearest-rank percentile (e.g. pct=90 -> 90th percentile)."""
    ordered = sorted(values)
    rank = max(1, math.ceil(pct / 100 * len(ordered)))
    return ordered[rank - 1]


def build_multipart(filename, payload, fields):
    """Builds a multipart/form-data body using only the standard library."""
    boundary = uuid.uuid4().hex
    chunks = []
    for name, value in fields.items():
        chunks.append(
            f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"'
            f"\r\n\r\n{value}\r\n".encode()
        )
    chunks.append(
        f'--{boundary}\r\nContent-Disposition: form-data; name="audio"; '
        f'filename="{filename}"\r\nContent-Type: audio/mpeg\r\n\r\n'.encode()
    )
    chunks.append(payload)
    chunks.append(f"\r\n--{boundary}--\r\n".encode())
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"


def upload(host, port, payload, label):
    """
    Uploads one audio file and returns (status, seconds, parsed_json).
    Each call uses its own connection, like an independent user.
    """
    filename = f"{PERF_FILE_TAG}_{label}_{uuid.uuid4().hex[:8]}.mp3"
    body, content_type = build_multipart(
        filename, payload, {"title": f"Perf {label}", "date": "2026-10-25"}
    )
    started = time.perf_counter()
    conn = http.client.HTTPConnection(host, port, timeout=120)
    try:
        conn.request("POST", "/api/upload", body=body,
                     headers={"Content-Type": content_type})
        response = conn.getresponse()
        data = json.loads(response.read().decode("utf-8"))
        return response.status, time.perf_counter() - started, data
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def server():
    """Runs the Flask app on a free local port, threaded like production."""
    app.config["TESTING"] = True
    init_db()
    httpd = make_server("127.0.0.1", 0, app, threaded=True)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield "127.0.0.1", httpd.server_port
    httpd.shutdown()
    thread.join(timeout=5)


@pytest.fixture(scope="module")
def audio_30_min():
    """A 30-minute-sized audio payload (the transcriber is a stub)."""
    return b"ID3\x03\x00\x00\x00\x00\x00\x00" + bytes(THIRTY_MIN_AUDIO_BYTES)


@pytest.fixture(scope="module", autouse=True)
def cleanup_uploaded_files():
    """Deletes the large audio files these tests leave in the uploads folder."""
    yield
    folder = app.config["UPLOAD_FOLDER"]
    for name in os.listdir(folder):
        if PERF_FILE_TAG in name:
            try:
                os.remove(os.path.join(folder, name))
            except OSError:
                pass


# ---------------------------------------------------------------------------
# TC-PERF-01 / MM-NF-001 : processing time
# ---------------------------------------------------------------------------

def test_30_minute_upload_p90_under_60_seconds(server, audio_30_min, record_property):
    """90th percentile end-to-end time for a 30-minute upload is <= 60 s."""
    host, port = server
    timings = []

    for run in range(RUNS_FOR_PERCENTILE):
        status, seconds, data = upload(host, port, audio_30_min, f"p{run}")
        assert status == 201, f"Run {run} failed: {data}"
        assert data["success"] is True
        assert data["markdown"], "Minutes were not generated"
        timings.append(seconds)

    p90 = percentile(timings, 90)
    summary = (
        f"\n[TC-PERF-01] {RUNS_FOR_PERCENTILE} uploads of "
        f"{len(audio_30_min) / 1_000_000:.1f} MB: "
        f"min={min(timings):.3f}s mean={statistics.mean(timings):.3f}s "
        f"p90={p90:.3f}s max={max(timings):.3f}s (limit {MAX_PROCESSING_SECONDS}s)"
    )
    print(summary)
    record_property("tc_perf_01_p90_seconds", round(p90, 3))
    record_property("tc_perf_01_max_seconds", round(max(timings), 3))

    assert p90 <= MAX_PROCESSING_SECONDS, summary


def test_pipeline_stages_on_30_minute_transcript_under_60_seconds(record_property):
    """
    The NLP/generation stages stay fast on a transcript as long as a real
    30-minute meeting (~4,500 words), guarding against slow regexes.
    """
    lines = []
    for minute in range(30):
        for turn in range(8):
            seconds = turn * 7
            ts = f"[00:{minute:02d}:{seconds:02d}]"
            lines.append(f"{ts} Speaker{turn % 4}: Um, so we were discussing the "
                         "release plan and the dependencies between the teams.")
        lines.append(f"[00:{minute:02d}:58] Lead: Decision: we are approving "
                     f"milestone {minute}.")
        lines.append(f"[00:{minute:02d}:59] Lead: Action item: Priya to finish "
                     f"task {minute} by Friday.")
    transcript = "\n".join(lines)
    word_count = len(transcript.split())
    assert word_count > 3_500

    started = time.perf_counter()
    cleaned = clean_transcript(transcript)
    attendees = extract_attendees(cleaned)
    decisions = extract_decisions(cleaned)
    actions = extract_action_items(cleaned)
    summary = generate_executive_summary(cleaned, decisions, actions)
    markdown = generate_markdown_minutes(
        "30-min meeting", "2026-10-25", "00:30:00",
        attendees, summary, decisions, actions, cleaned,
    )
    elapsed = time.perf_counter() - started

    print(f"\n[TC-PERF-01] pipeline stages on {word_count} words: {elapsed:.3f}s")
    record_property("pipeline_stage_seconds", round(elapsed, 3))

    assert markdown
    assert elapsed <= MAX_PROCESSING_SECONDS


# ---------------------------------------------------------------------------
# TC-PERF-02 / MM-NF-003 : concurrency
# ---------------------------------------------------------------------------

def _run_concurrent_uploads(server, payload, users):
    host, port = server
    barrier = threading.Barrier(users)

    def one_user(index):
        barrier.wait()  # all users start at the same moment
        return upload(host, port, payload, f"u{index}")

    with ThreadPoolExecutor(max_workers=users) as pool:
        futures = [pool.submit(one_user, i) for i in range(users)]
        return [f.result(timeout=300) for f in futures]


def test_5_concurrent_uploads_complete_without_errors(server, audio_30_min, record_property):
    """TC-PERF-02: 5 simultaneous uploads all succeed within the time limit."""
    started = time.perf_counter()
    results = _run_concurrent_uploads(server, audio_30_min, REQUIRED_CONCURRENT_USERS)
    wall = time.perf_counter() - started

    failures = [(s, d) for s, _, d in results if s != 201 or not d.get("success")]
    seconds = [t for _, t, _ in results]
    print(
        f"\n[TC-PERF-02] {REQUIRED_CONCURRENT_USERS} concurrent users: "
        f"failures={len(failures)} slowest={max(seconds):.3f}s wall={wall:.3f}s"
    )
    record_property("tc_perf_02_failures", len(failures))
    record_property("tc_perf_02_slowest_seconds", round(max(seconds), 3))

    assert not failures, f"Concurrent uploads failed: {failures}"
    assert max(seconds) <= MAX_PROCESSING_SECONDS


def test_concurrent_uploads_get_unique_meetings_and_persist(server, audio_30_min):
    """No two users share a meeting id and every meeting is saved."""
    results = _run_concurrent_uploads(server, audio_30_min, REQUIRED_CONCURRENT_USERS)

    ids = [data["meeting_id"] for _, _, data in results]
    assert len(set(ids)) == REQUIRED_CONCURRENT_USERS, f"Duplicate meeting ids: {ids}"

    for meeting_id in ids:
        stored = get_meeting(meeting_id)
        assert stored is not None, f"Meeting {meeting_id} was not persisted"
        assert stored["action_items"], f"Meeting {meeting_id} lost its action items"


def test_10_concurrent_uploads_headroom(server, audio_30_min, record_property):
    """Headroom check: double the required load still completes cleanly."""
    results = _run_concurrent_uploads(server, audio_30_min, EXTRA_HEADROOM_USERS)

    failures = [(s, d) for s, _, d in results if s != 201 or not d.get("success")]
    slowest = max(t for _, t, _ in results)
    print(
        f"\n[TC-PERF-02] {EXTRA_HEADROOM_USERS} concurrent users (headroom): "
        f"failures={len(failures)} slowest={slowest:.3f}s"
    )
    record_property("headroom_10_users_failures", len(failures))

    assert not failures, f"Failures under 10 concurrent users: {failures}"
    assert slowest <= MAX_PROCESSING_SECONDS


def test_mixed_read_write_load_stays_healthy(server, audio_30_min):
    """Uploads running alongside reads (history, health) must not error."""
    host, port = server

    def read_traffic(_):
        conn = http.client.HTTPConnection(host, port, timeout=60)
        try:
            codes = []
            for path in ("/api/health", "/api/meetings") * 5:
                conn.request("GET", path)
                response = conn.getresponse()
                response.read()
                codes.append(response.status)
            return codes
        finally:
            conn.close()

    with ThreadPoolExecutor(max_workers=8) as pool:
        uploads = [pool.submit(upload, host, port, audio_30_min, f"m{i}") for i in range(3)]
        reads = [pool.submit(read_traffic, i) for i in range(5)]
        upload_results = [f.result(timeout=300) for f in uploads]
        read_results = [f.result(timeout=300) for f in reads]

    assert all(status == 201 for status, _, _ in upload_results)
    assert all(code == 200 for codes in read_results for code in codes)


def test_simultaneous_uploads_with_same_filename_do_not_collide(server):
    """
    Two users uploading a file with the same name at the same moment must each
    keep their own audio file (regression test for a timestamp-only filename).
    """
    host, port = server
    payload = b"ID3\x03\x00\x00\x00\x00\x00\x00" + bytes(2000)
    users = REQUIRED_CONCURRENT_USERS
    barrier = threading.Barrier(users)

    def same_name_upload(index):
        body, content_type = build_multipart(
            f"{PERF_FILE_TAG}_same.mp3", payload, {"title": f"Same {index}"}
        )
        barrier.wait()
        conn = http.client.HTTPConnection(host, port, timeout=60)
        try:
            conn.request("POST", "/api/upload", body=body,
                         headers={"Content-Type": content_type})
            return json.loads(conn.getresponse().read().decode("utf-8"))
        finally:
            conn.close()

    with ThreadPoolExecutor(max_workers=users) as pool:
        results = list(pool.map(same_name_upload, range(users)))

    stored_names = [get_meeting(r["meeting_id"])["audio_filename"] for r in results]
    assert len(set(stored_names)) == users, f"Audio files collided: {stored_names}"
