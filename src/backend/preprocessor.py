"""
Text Preprocessor Module
========================
Owner: Vinay M Rampur (PES1UG24AM455)
Phase: 3 - Implementation Sprint 1

Cleans raw transcript text by:
- Removing conversational filler words
- Normalizing timestamps
- Standardizing speaker labels
- Removing redundant whitespace and formatting artifacts
"""

import re
from typing import List


# Common conversational fillers.
FILLER_PATTERNS = [
    r"\bum+\b",
    r"\buh+\b",
    r"\bah+\b",
    r"\berr+\b",
    r"\byou know\b",
    r"\bactually\b",
    r"\bbasically\b",
]


def remove_filler_words(text: str) -> str:
    """
    Remove common conversational filler words while preserving
    meaningful uses of words such as 'like'.

    Examples:
        "Um, hello everyone." -> "hello everyone."
        "I, like, think we should proceed."
            -> "I think we should proceed."
        "I like the design." -> "I like the design."
    """
    cleaned = text

    for pattern in FILLER_PATTERNS:
        cleaned = re.sub(
            pattern,
            "",
            cleaned,
            flags=re.IGNORECASE,
        )

    # Remove "like" when enclosed by commas as a conversational filler.
    cleaned = re.sub(
        r",\s*like\s*,",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    # Remove "like" before common intensifiers when used as a filler.
    cleaned = re.sub(
        r"\blike\s+(really|very|basically|just)\b",
        r"\1",
        cleaned,
        flags=re.IGNORECASE,
    )

    # Remove a comma left at the beginning of a sentence or
    # immediately after a speaker label when a filler is removed.
    cleaned = re.sub(
        r"(^|:\s*),\s*",
        r"\1",
        cleaned,
    )

    # Remove spaces before punctuation.
    cleaned = re.sub(r"\s+([,.;!?])", r"\1", cleaned)

    # Collapse repeated spaces and tabs.
    cleaned = re.sub(r"[ \t]+", " ", cleaned)

    # Remove duplicate commas caused by filler removal.
    cleaned = re.sub(r",\s*,+", ",", cleaned)

    # Avoid stray punctuation at the beginning or end.
    return cleaned.strip(" ,")


def normalize_timestamp(timestamp: str) -> str:
    """
    Normalize timestamps into [HH:MM:SS] format.

    Supported inputs:
        0:1:5    -> [00:01:05]
        00:1:5   -> [00:01:05]
        1:05:10  -> [01:05:10]
        1:05     -> [00:01:05]

    Invalid formats are returned unchanged.
    """
    parts = timestamp.split(":")

    try:
        parts = [int(part) for part in parts]

        if len(parts) == 3:
            hours, minutes, seconds = parts
        elif len(parts) == 2:
            hours = 0
            minutes, seconds = parts
        else:
            return timestamp

        if hours < 0 or minutes < 0 or seconds < 0:
            return timestamp

        if minutes > 59 or seconds > 59:
            return timestamp

        return f"[{hours:02d}:{minutes:02d}:{seconds:02d}]"

    except ValueError:
        return timestamp


def normalize_timestamps(text: str) -> str:
    """Normalize supported timestamps enclosed in square brackets."""
    return re.sub(
        r"\[(\d{1,3}:\d{1,2}:\d{1,2}|\d{1,2}:\d{1,2})\]",
        lambda match: normalize_timestamp(match.group(1)),
        text,
    )


def normalize_speaker_turn(line: str) -> str:
    """
    Standardize speaker labels and spacing.

    Examples:
        'alice : Hello' -> 'Alice: Hello'
        'BOB: Hi'       -> 'Bob: Hi'
        'Alice   : Hi'  -> 'Alice: Hi'
    """
    pattern = (
        r"^(\s*(?:\[\d{2,3}:\d{2}:\d{2}\]\s*)?)"
        r"([A-Za-z][A-Za-z0-9 _-]{0,30})\s*:\s*(.*)$"
    )

    match = re.match(pattern, line)

    if not match:
        return line.strip()

    prefix = match.group(1)
    speaker = match.group(2).strip()
    message = match.group(3).strip()

    # Normalize all-lowercase or all-uppercase labels.
    # Preserve mixed-case labels such as "McDonald".
    if speaker.islower() or speaker.isupper():
        speaker = speaker.title()

    # Normalize whitespace inside speaker labels.
    speaker = re.sub(r"\s+", " ", speaker)

    return f"{prefix}{speaker}: {message}"


def normalize_lines(text: str) -> List[str]:
    """Split transcript text into cleaned, non-empty dialogue lines."""
    lines = []

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        # Normalize timestamps before processing speaker labels.
        line = normalize_timestamps(line)

        # Remove conversational filler words.
        line = remove_filler_words(line)

        # Standardize speaker labels and surrounding whitespace.
        line = normalize_speaker_turn(line)

        if line:
            lines.append(line)

    return lines


def clean_transcript(raw_text: str) -> str:
    """
    Normalize transcript text before information extraction.

    Processing steps:
        1. Split the transcript into lines.
        2. Remove blank lines and unnecessary whitespace.
        3. Normalize timestamps.
        4. Remove conversational filler words.
        5. Standardize speaker labels.
        6. Join the cleaned lines.
    """
    if not raw_text:
        return ""

    cleaned_lines = normalize_lines(raw_text)

    return "\n".join(cleaned_lines)
