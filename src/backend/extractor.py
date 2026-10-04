"""
Action Items & Decision Extractor Module
========================================
Owner: Vinay M Rampur (PES1UG24AM455)
Phase: 3 - Implementation Sprint 1

Uses NLP heuristics and regex patterns to identify:
1. Action items (task description, assignee, deadline)
2. Key decisions made during the meeting
3. Meeting attendees and discussion topics
"""

import re
from typing import Dict, List, Any


def extract_attendees(transcript_text: str) -> List[str]:
    """Identifies unique speaker names from dialogue prefixes."""
    speakers = set()
    # Matches patterns like '[00:01:23] Alice:' or 'Alice:'
    matches = re.findall(r"(?:\[\d{2}:\d{2}:\d{2}\]\s+)?([A-Za-z0-9_\s]{2,20}):", transcript_text)
    for speaker in matches:
        clean_name = speaker.strip()
        if clean_name and len(clean_name) < 25:
            speakers.add(clean_name)
    return sorted(list(speakers))


def extract_decisions(transcript_text: str) -> List[str]:
    """Extracts agreed decisions based on consensus keywords."""
    decisions = []
    decision_patterns = [
        r"(?:decision|agreed|concluded|approved):\s*([^.\n]+)",
        r"(?:we decided|agreed to|consensus is)\s+([^.\n]+)"
    ]

    for line in transcript_text.splitlines():
        for pat in decision_patterns:
            match = re.search(pat, line, flags=re.IGNORECASE)
            if match:
                decision_text = match.group(1).strip()
                if decision_text and decision_text not in decisions:
                    decisions.append(decision_text.capitalize())

    return decisions


def extract_action_items(transcript_text: str) -> List[Dict[str, str]]:
    """
    Extracts action items using regex heuristics for tasks, assignees, and deadlines.
    Returns: List of dicts with keys {'task', 'assignee', 'deadline', 'status'}
    """
    action_items = []

    # Pattern 1: Explicit Action Item / TODO labels
    # e.g., "Action item: Bob will finalize the database models by Friday"
    explicit_pattern = re.compile(
        r"(?:action item|todo|task):\s*(?:(?P<assignee>[A-Za-z0-9]+)\s+(?:will|to|should|needs to)\s+)?(?P<task>[^.\n]+?)(?:\s+by\s+(?P<deadline>[A-Za-z0-9\s]+?))?[.]*$",
        re.IGNORECASE
    )

    # Pattern 2: Assignee commitment
    # e.g., "Charlie to implement drag-and-drop audio upload UI by Monday"
    commitment_pattern = re.compile(
        r"(?P<assignee>[A-Za-z0-9]+)\s+(?:will|to|is assigned to)\s+(?P<task>[^.\n]+?)(?:\s+by\s+(?P<deadline>[A-Za-z0-9\s]+?))?[.]*$",
        re.IGNORECASE
    )

    for line in transcript_text.splitlines():
        # Remove timestamp and speaker prefix if present
        clean_line = re.sub(r"^(?:\[\d{2}:\d{2}:\d{2}\]\s+)?[A-Za-z0-9_\s]{2,20}:\s*", "", line).strip().rstrip(".")
        
        match = explicit_pattern.search(clean_line)
        if match:
            assignee = match.group("assignee") or "Team"
            task = match.group("task").strip()
            deadline = match.group("deadline") or "TBD"
            action_items.append({
                "task": task,
                "assignee": assignee.strip(),
                "deadline": deadline.strip(),
                "status": "Pending"
            })
            continue

        match2 = commitment_pattern.search(clean_line)
        if match2 and any(k in clean_line.lower() for k in ["implement", "finalize", "create", "test", "handle", "write", "deploy"]):
            assignee = match2.group("assignee")
            task = match2.group("task").strip()
            deadline = match2.group("deadline") or "TBD"
            action_items.append({
                "task": task,
                "assignee": assignee.strip(),
                "deadline": deadline.strip(),
                "status": "Pending"
            })

    # Deduplicate items by task
    unique_items = []
    seen_tasks = set()
    for item in action_items:
        t_key = item["task"].lower()
        if t_key not in seen_tasks:
            seen_tasks.add(t_key)
            unique_items.append(item)

    return unique_items


def generate_executive_summary(transcript_text: str, decisions: List[str], action_items: List[Dict[str, str]]) -> str:
    """Creates a high-level summary of the meeting topics and outcomes."""
    attendees = extract_attendees(transcript_text)
    attendee_str = ", ".join(attendees) if attendees else "Project Team"
    
    summary = (
        f"Meeting held with {len(attendees)} participants ({attendee_str}). "
        f"The team reviewed project architecture, progress, and agreed on key next steps. "
        f"A total of {len(decisions)} key decisions were recorded, and {len(action_items)} action items were assigned."
    )
    return summary
