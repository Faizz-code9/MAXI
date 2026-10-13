"""
Action Items & Decision Extractor Module
========================================

Owner: Vinay M Rampur (PES1UG24AM455)

Phase: 3 - Implementation Sprint 1

Uses NLP heuristics and regular expressions to identify:

1. Action items
2. Assignees
3. Deadlines
4. Key decisions
5. Meeting attendees
"""

import re
from typing import Dict, List


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

def _remove_speaker_prefix(line: str) -> str:
    """
    Remove an optional timestamp and speaker prefix.

    Examples:
        [00:01:05] Alice: Hello
        Alice: Hello

    Result:
        Hello
    """

    pattern = (
        r"^\s*"
        r"(?:\[\d{1,3}:\d{1,2}:\d{1,2}\]\s*)?"
        r"[A-Za-z][A-Za-z0-9 _-]{0,30}"
        r"\s*:\s*"
    )

    return re.sub(pattern, "", line).strip()


def _normalize_deadline(deadline: str) -> str:
    """Clean extracted deadline text; return an empty string if absent."""

    if not deadline:
        return ""

    deadline = re.sub(r"\s+", " ", deadline.strip())
    return deadline.rstrip(".,;:")


def _normalize_task(task: str) -> str:
    """Clean extracted task text."""

    task = task.strip()
    task = re.sub(r"\s+", " ", task)
    task = task.strip(" ,;:-")

    return task


def _normalize_assignee(assignee: str) -> str:
    """Normalize an assignee name."""

    if not assignee:
        return "Unassigned"

    assignee = assignee.strip()
    assignee = re.sub(r"\s+", " ", assignee)

    return assignee


# ---------------------------------------------------------------------------
# Attendee Extraction
# ---------------------------------------------------------------------------

def extract_attendees(transcript_text: str) -> List[str]:
    """
    Identify unique speaker names from transcript dialogue prefixes.

    Supported formats:

        Alice: Hello
        [00:01:23] Alice: Hello
        alice: Hello
        BOB: Hello

    Returns:
        Sorted list of unique speaker names.
    """

    speakers = set()

    speaker_pattern = re.compile(
        r"^\s*"
        r"(?:\[\d{1,3}:\d{1,2}:\d{1,2}\]\s*)?"
        r"(?P<speaker>[A-Za-z][A-Za-z0-9 _-]{0,30})"
        r"\s*:\s*"
    )

    for line in transcript_text.splitlines():

        match = speaker_pattern.match(line)

        if not match:
            continue

        speaker = match.group("speaker").strip()

        if not speaker:
            continue

        # Do not treat these labels as attendee names.
        if speaker.lower() in {
            "action item",
            "todo",
            "task",
            "decision",
            "summary",
            "note",
        }:
            continue

        # Normalize simple uppercase/lowercase names.
        if speaker.isupper() or speaker.islower():
            speaker = speaker.title()

        speakers.add(speaker)

    return sorted(speakers)


# ---------------------------------------------------------------------------
# Decision Extraction
# ---------------------------------------------------------------------------

def extract_decisions(transcript_text: str) -> List[str]:
    """
    Extract decisions using common consensus phrases.

    Examples:

        Decision: SQLite will be used.
        We decided to use SQLite.
        Agreed to deploy locally.
        Consensus is to use Flask.
        The team decided to use PostgreSQL.

    Returns:
        List of unique decision strings.
    """

    decisions = []

    decision_patterns = [
        # Explicit labels
        r"\bdecision\s*:\s*(?P<decision>[^.\n]+)",
        r"\bagreed\s*:\s*(?P<decision>[^.\n]+)",
        r"\bconcluded\s*:\s*(?P<decision>[^.\n]+)",
        r"\bapproved\s*:\s*(?P<decision>[^.\n]+)",

        # Natural language decisions
        r"\bwe\s+decided\s+(?:to\s+)?(?P<decision>[^.\n]+)",
        r"\bagreed\s+to\s+(?P<decision>[^.\n]+)",
        r"\bconsensus\s+is\s+(?:to\s+)?(?P<decision>[^.\n]+)",
        r"\bthe\s+team\s+decided\s+(?:to\s+)?(?P<decision>[^.\n]+)",
    ]

    for line in transcript_text.splitlines():

        for pattern in decision_patterns:

            match = re.search(
                pattern,
                line,
                flags=re.IGNORECASE,
            )

            if not match:
                continue

            decision = match.group("decision").strip()
            decision = re.sub(r"\s+", " ", decision)
            decision = decision.rstrip(".,;:")

            if not decision:
                continue

            decision = decision[0].upper() + decision[1:]

            # Prevent duplicate decisions.
            if not any(
                existing.lower() == decision.lower()
                for existing in decisions
            ):
                decisions.append(decision)

            break

    return decisions


# ---------------------------------------------------------------------------
# Action Item Extraction
# ---------------------------------------------------------------------------

def extract_action_items(
    transcript_text: str,
) -> List[Dict[str, str]]:
    """Extract actionable commitments, assignees, and deadlines.

    The parser uses deterministic regex heuristics. It supports explicit labels,
    named commitments, assignment phrases, and common relative/absolute dates.
    """
    action_items: List[Dict[str, str]] = []

    month = (
        r"jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|"
        r"jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|sept(?:ember)?|"
        r"oct(?:ober)?|nov(?:ember)?|dec(?:ember)?"
    )
    weekday = r"monday|tuesday|wednesday|thursday|friday|saturday|sunday"
    date = rf"(?:{month})\s+\d{{1,2}}|\d{{1,2}}\s+(?:{month})"
    # Keep multiword phrases together so the deadline is not reduced to just
    # the final weekday/month expression.
    deadline_pattern = rf"(?:today|tomorrow|tonight|eod|end\s+of\s+day|this\s+week|next\s+week|next\s+month|(?:{weekday})(?:\s+(?:morning|afternoon|evening))?|(?:before|by|due\s+on)\s+(?:next\s+)?(?:{weekday}|{date})|within\s+\w+(?:\s+\w+)?)"

    # Assignee names may contain up to three words, e.g. Kamal Kanth.
    name = r"[A-Za-z][A-Za-z0-9_-]*(?:\s+[A-Za-z][A-Za-z0-9_-]*){0,2}"
    deadline_suffix = rf"(?:\s+(?:by\s+)?(?P<deadline>{deadline_pattern}))?(?:\s*,?\s*(?:please|thanks))?[\s.,;!]*$"

    explicit_pattern = re.compile(
        rf"^\s*(?:action\s+item|todo|task)\s*:\s*"
        rf"(?:(?P<assignee>{name})\s+)?"
        rf"(?:will|should|needs?\s+to|is\s+assigned\s+to|"
        rf"is\s+responsible\s+for|to)\s+"
        rf"(?P<task>.+?){deadline_suffix}",
        re.IGNORECASE,
    )
    commitment_pattern = re.compile(
        rf"^\s*(?P<assignee>{name})\s+"
        rf"(?:will|should|needs?\s+to)\s+"
        rf"(?P<task>.+?){deadline_suffix}",
        re.IGNORECASE,
    )
    responsible_pattern = re.compile(
        rf"^\s*(?P<assignee>{name})\s+is\s+responsible\s+for\s+"
        rf"(?P<task>.+?){deadline_suffix}",
        re.IGNORECASE,
    )
    assigned_pattern = re.compile(
        rf"^\s*(?P<task>.+?)\s+is\s+assigned\s+to\s+"
        rf"(?P<assignee>{name}){deadline_suffix}",
        re.IGNORECASE,
    )
    to_pattern = re.compile(
        rf"^\s*(?P<assignee>{name})\s+to\s+"
        rf"(?P<task>.+?){deadline_suffix}",
        re.IGNORECASE,
    )

    non_actionable_tasks = {
        "be available", "be there", "be present", "attend the meeting",
        "join the meeting", "be available tomorrow",
    }

    labels = {"action item", "todo", "task", "decision", "summary", "note"}

    for line in transcript_text.splitlines():
        clean_line = line.strip()
        if not clean_line:
            continue

        clean_line = re.sub(
            r"^\[\d{1,3}:\d{1,2}:\d{1,2}\]\s*", "", clean_line
        ).strip()

        # Remove a speaker prefix, while preserving extraction labels.
        speaker_match = re.match(
            r"^(?P<speaker>[A-Za-z][A-Za-z0-9 _-]{0,30})\s*:\s*(?P<message>.*)$",
            clean_line,
        )
        if speaker_match and speaker_match.group("speaker").strip().lower() not in labels:
            clean_line = speaker_match.group("message").strip()

        clean_line = clean_line.rstrip(". ")

        match = None
        for pattern in (
            explicit_pattern,
            responsible_pattern,
            assigned_pattern,
            commitment_pattern,
            to_pattern,
        ):
            match = pattern.match(clean_line)
            if match:
                break
        if not match:
            continue

        assignee = _normalize_assignee(match.groupdict().get("assignee"))
        task = _normalize_task(match.groupdict().get("task") or "")
        deadline = _normalize_deadline(match.groupdict().get("deadline"))
        deadline = re.sub(r"^(?:due\s+on)\s+", "", deadline, flags=re.IGNORECASE)

        # Remove polite trailing language if the deadline wasn't recognized.
        task = re.sub(r"\s*,?\s*(?:please|thanks)[.!]*$", "", task, flags=re.IGNORECASE).strip()
        if not task or task.lower().rstrip(".!?") in non_actionable_tasks:
            continue
        # Avoid treating first-person availability statements as assigned work.
        if assignee.lower() in {"i", "we", "you"} and task.lower().startswith(("be available", "be there", "be present")):
            continue

        action_items.append({
            "task": task,
            "assignee": assignee,
            "deadline": deadline,
            "status": "Pending",
        })

    unique_items: List[Dict[str, str]] = []
    seen = set()
    for item in action_items:
        key = (item["task"].lower(), item["assignee"].lower())
        if key not in seen:
            seen.add(key)
            unique_items.append(item)

    return unique_items


# ---------------------------------------------------------------------------
# Executive Summary
# ---------------------------------------------------------------------------

def generate_executive_summary(
    transcript_text: str,
    decisions: List[str],
    action_items: List[Dict[str, str]],
) -> str:
    """
    Create a high-level summary of meeting participants,
    decisions and action items.
    """

    attendees = extract_attendees(transcript_text)

    attendee_str = (
        ", ".join(attendees)
        if attendees
        else "Project Team"
    )

    summary = (
        f"Meeting held with {len(attendees)} participants "
        f"({attendee_str}). "
        f"The team reviewed project architecture, progress, "
        f"and agreed on key next steps. "
        f"A total of {len(decisions)} key decisions were recorded, "
        f"and {len(action_items)} action items were assigned."
    )

    return summary