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


# Filler words that can safely be removed when they are used
# as conversational fillers.
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
    Remove common conversational filler words.

    The word 'like' is handled separately so that meaningful
    sentences such as 'I like the design' are preserved.
    """

    cleaned = text

    for pattern in FILLER_PATTERNS:
        cleaned = re.sub(
            pattern,
            "",
            cleaned,
            flags=re.IGNORECASE,
        )

    # Remove 'like' only when it is clearly being used
    # as a conversational filler.
    #
    # Examples removed:
    #   "I, like, think we should..."
    #   "It was, like, really good."
    #
    # Examples preserved:
    #   "I like the design."
    #   "We like this approach."
    cleaned = re.sub(
        r",\s*like\s*,",
        ",",
        cleaned,
        flags=re.IGNORECASE,
    )

    cleaned = re.sub(
        r"\b(like)\s+(really|very|basically|just)\b",
        r"\2",
        cleaned,
        flags=re.IGNORECASE,
    )

    # Remove spaces before punctuation.
    cleaned = re.sub(r"\s+([,.;!?])", r"\1", cleaned)

    # Collapse repeated spaces.
    cleaned = re.sub(r"[ \t]+", " ", cleaned)

    # Remove duplicated commas created by filler removal.
    cleaned = re.sub(r",\s*,+", ",", cleaned)

    return cleaned.strip(" ,")


def normalize_timestamp(timestamp: str) -> str:
    """
    Normalize timestamps into [HH:MM:SS] format.

    Examples:
        [0:1:5]     -> [00:01:05]
        [00:1:5]    -> [00:01:05]
        [1:05:10]   -> [01:05:10]
        [00:01:05]  -> [00:01:05]
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

        return f"[{hours:02d}:{minutes:02d}:{seconds:02d}]"

    except ValueError:
        return timestamp


def normalize_timestamps(text: str) -> str:
    """Normalize all timestamps in a transcript."""

    return re.sub(
        r"\[(\d{1,3}:\d{1,2}:\d{1,2})\]",
        lambda match: normalize_timestamp(match.group(0)[1:-1]),
        text,
    )


def normalize_speaker_turn(line: str) -> str:
    """
    Standardize speaker labels.

    Examples:
        'alice : Hello' -> 'Alice: Hello'
        'BOB: Hi'       -> 'Bob: Hi'
        'Alice   : Hi'  -> 'Alice: Hi'
    """

    pattern = r"^(\s*(?:\[\d{2}:\d{2}:\d{2}\]\s*)?)([A-Za-z][A-Za-z0-9 _-]{0,30})\s*:\s*(.*)$"

    match = re.match(pattern, line)

    if not match:
        return line.strip()

    prefix = match.group(1)
    speaker = match.group(2).strip()
    message = match.group(3).strip()

    # Normalize speaker capitalization without destroying
    # already correctly formatted names/acronyms.
    if speaker.islower() or speaker.isupper():
        speaker = speaker.title()

    return f"{prefix}{speaker}: {message}"


def normalize_lines(text: str) -> List[str]:
    """
    Split transcript into cleaned, non-empty dialogue lines.
    """

    lines = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        # Normalize timestamp before speaker processing.
        line = normalize_timestamps(line)

        # Remove filler words.
        line = remove_filler_words(line)

        # Normalize speaker formatting.
        line = normalize_speaker_turn(line)

        if line:
            lines.append(line)

    return lines


def clean_transcript(raw_text: str) -> str:
    """
    Perform complete transcript normalization.

    Pipeline:
        Raw transcript
            ↓
        Remove filler words
            ↓
        Normalize timestamps
            ↓
        Normalize speaker labels
            ↓
        Normalize whitespace
            ↓
        Clean transcript
    """

    if not raw_text:
        return ""

    cleaned_lines = normalize_lines(raw_text)

    return "\n".join(cleaned_lines)