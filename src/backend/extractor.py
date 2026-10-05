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
    """Clean extracted deadline text."""

    if not deadline:
        return "TBD"

    deadline = deadline.strip()
    deadline = re.sub(r"\s+", " ", deadline)
    deadline = deadline.rstrip(".,;:")

    return deadline


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
    """
    Extract action items from a meeting transcript.

    Supported patterns:

        Action item: Bob will finalize the database models by Friday.

        TODO: Alice will update the API by Monday.

        Charlie to implement the upload UI by Monday.

        Dave will test the application.

        Kamal is responsible for updating the dashboard by Monday.

    Returns:

        [
            {
                "task": "...",
                "assignee": "...",
                "deadline": "...",
                "status": "Pending"
            }
        ]
    """

    action_items: List[Dict[str, str]] = []

    # ------------------------------------------------------------------
    # Deadline pattern
    # ------------------------------------------------------------------

    deadline_pattern = (
        r"(?:"
        r"today"
        r"|tomorrow"
        r"|tonight"
        r"|eod"
        r"|end\s+of\s+day"
        r"|this\s+week"
        r"|next\s+week"
        r"|next\s+month"
        r"|monday"
        r"|tuesday"
        r"|wednesday"
        r"|thursday"
        r"|friday"
        r"|saturday"
        r"|sunday"
        r"|(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)"
        r"\s+(?:morning|afternoon|evening)"
        r"|(?:"
        r"jan(?:uary)?"
        r"|feb(?:ruary)?"
        r"|mar(?:ch)?"
        r"|apr(?:il)?"
        r"|may"
        r"|jun(?:e)?"
        r"|jul(?:y)?"
        r"|aug(?:ust)?"
        r"|sep(?:tember)?"
        r"|sept(?:ember)?"
        r"|oct(?:ober)?"
        r"|nov(?:ember)?"
        r"|dec(?:ember)?"
        r")\s+\d{1,2}"
        r"|(?:\d{1,2}\s+"
        r"(?:"
        r"jan(?:uary)?"
        r"|feb(?:ruary)?"
        r"|mar(?:ch)?"
        r"|apr(?:il)?"
        r"|may"
        r"|jun(?:e)?"
        r"|jul(?:y)?"
        r"|aug(?:ust)?"
        r"|sep(?:tember)?"
        r"|sept(?:ember)?"
        r"|oct(?:ober)?"
        r"|nov(?:ember)?"
        r"|dec(?:ember)?"
        r"))"
        r")"
    )

    # ------------------------------------------------------------------
    # Pattern 1:
    #
    # Action item: Bob will finalize the database models by Friday
    # TODO: Alice should update the API by Monday
    # Task: Charlie needs to test the application
    # ------------------------------------------------------------------

    explicit_pattern = re.compile(
        rf"""
        ^\s*

        (?:action\s+item|todo|task)
        \s*:\s*

        (?:
            (?P<assignee>
                [A-Za-z][A-Za-z0-9_-]*
            )
            \s+
        )?

        (?:
            will
            |should
            |needs?\s+to
            |is\s+assigned\s+to
            |is\s+responsible\s+for
            |to
        )
        \s+

        (?P<task>.*?)

        (?:
            \s+
            (?:by\s+)?
            (?P<deadline>{deadline_pattern})
        )?

        \s*$
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    # ------------------------------------------------------------------
    # Pattern 2:
    #
    # Charlie will implement the upload UI by Monday
    # Alice should update the API
    # Bob needs to test the backend
    # ------------------------------------------------------------------

    commitment_pattern = re.compile(
        rf"""
        ^\s*

        (?P<assignee>
            [A-Za-z][A-Za-z0-9_-]*
        )

        \s+

        (?:
            will
            |should
            |needs?\s+to
            |is\s+assigned\s+to
            |is\s+responsible\s+for
        )

        \s+

        (?P<task>.*?)

        (?:
            \s+
            (?:by\s+)?
            (?P<deadline>{deadline_pattern})
        )?

        \s*$
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    # ------------------------------------------------------------------
    # Pattern 3:
    #
    # Charlie to implement the upload UI by Monday
    # Alice to test the backend
    # ------------------------------------------------------------------

    to_pattern = re.compile(
        rf"""
        ^\s*

        (?P<assignee>
            [A-Za-z][A-Za-z0-9_-]*
        )

        \s+
        to
        \s+

        (?P<task>.*?)

        (?:
            \s+
            (?:by\s+)?
            (?P<deadline>{deadline_pattern})
        )?

        \s*$
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    # ------------------------------------------------------------------
    # Process each transcript line
    # ------------------------------------------------------------------

    for line in transcript_text.splitlines():

        line = line.strip()

        if not line:
            continue

        # Remove timestamp.
        clean_line = re.sub(
            r"^\s*\[\d{1,3}:\d{1,2}:\d{1,2}\]\s*",
            "",
            line,
        ).strip()

        # Remove normal speaker prefix.
        #
        # Do NOT remove prefixes such as:
        # Action item:
        # TODO:
        # Task:
        # Decision:
        # Summary:
        # Note:
        speaker_match = re.match(
            r"^(?P<speaker>[A-Za-z][A-Za-z0-9 _-]{0,30})"
            r"\s*:\s*"
            r"(?P<message>.*)$",
            clean_line,
        )

        if speaker_match:

            possible_speaker = (
                speaker_match.group("speaker").strip()
            )

            if possible_speaker.lower() not in {
                "action item",
                "todo",
                "task",
                "decision",
                "summary",
                "note",
            }:
                clean_line = (
                    speaker_match.group("message").strip()
                )

        # Remove trailing punctuation.
        clean_line = clean_line.rstrip(".")

        # --------------------------------------------------------------
        # Explicit action item
        # --------------------------------------------------------------

        match = explicit_pattern.match(clean_line)

        if match:

            assignee = _normalize_assignee(
                match.group("assignee")
            )

            task = _normalize_task(
                match.group("task")
            )

            deadline = _normalize_deadline(
                match.group("deadline")
            )

            if task:
                action_items.append(
                    {
                        "task": task,
                        "assignee": assignee,
                        "deadline": deadline,
                        "status": "Pending",
                    }
                )

            continue

        # --------------------------------------------------------------
        # Commitment pattern
        # --------------------------------------------------------------

        match = commitment_pattern.match(clean_line)

        if match:

            assignee = _normalize_assignee(
                match.group("assignee")
            )

            task = _normalize_task(
                match.group("task")
            )

            deadline = _normalize_deadline(
                match.group("deadline")
            )

            if task:
                action_items.append(
                    {
                        "task": task,
                        "assignee": assignee,
                        "deadline": deadline,
                        "status": "Pending",
                    }
                )

            continue

        # --------------------------------------------------------------
        # "Name to task" pattern
        # --------------------------------------------------------------

        match = to_pattern.match(clean_line)

        if match:

            assignee = _normalize_assignee(
                match.group("assignee")
            )

            task = _normalize_task(
                match.group("task")
            )

            deadline = _normalize_deadline(
                match.group("deadline")
            )

            if task:
                action_items.append(
                    {
                        "task": task,
                        "assignee": assignee,
                        "deadline": deadline,
                        "status": "Pending",
                    }
                )

    # ------------------------------------------------------------------
    # Deduplicate action items
    # ------------------------------------------------------------------

    unique_items: List[Dict[str, str]] = []
    seen = set()

    for item in action_items:

        key = (
            item["task"].lower(),
            item["assignee"].lower(),
        )

        if key in seen:
            continue

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