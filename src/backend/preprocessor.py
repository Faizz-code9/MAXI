"""
Text Preprocessor Module
========================
Owner: Vinay M Rampur (PES1UG24AM455)
Phase: 3 - Implementation Sprint 1

Cleans raw transcript text by removing conversational filler words,
standardizing whitespace, and normalizing speaker tags and timestamps.
"""

import re
from typing import List

FILLER_WORDS = [
    r"\bum+\b",
    r"\buh+\b",
    r"\bah+\b",
    r"\berr*\b",
    r"\blike\b",
    r"\byou know\b",
    r"\bactually\b",
    r"\bbasically\b"
]


def remove_filler_words(text: str) -> str:
    """Removes common conversational filler words while preserving grammatical punctuation."""
    cleaned = text
    for pattern in FILLER_WORDS:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
    # Collapse multiple consecutive spaces
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    return cleaned.strip()


def normalize_lines(text: str) -> List[str]:
    """Splits text into cleaned, non-empty dialogue lines."""
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            cleaned = remove_filler_words(line)
            lines.append(cleaned)
    return lines


def clean_transcript(raw_text: str) -> str:
    """Performs full end-to-end normalization on transcript string."""
    cleaned_lines = normalize_lines(raw_text)
    return "\n".join(cleaned_lines)
