import sys
from pathlib import Path

import pytest

# Add src/backend to the Python import path.
BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from preprocessor import (
    remove_filler_words,
    normalize_timestamp,
    normalize_timestamps,
    normalize_speaker_turn,
    normalize_lines,
    clean_transcript,
)


def test_remove_common_filler_words():
    text = "Um, I think, uh, we should start."
    result = remove_filler_words(text)

    assert "um" not in result.lower()
    assert "uh" not in result.lower()
    assert "we should start" in result


def test_preserve_meaningful_like():
    text = "I like the design."
    result = remove_filler_words(text)

    assert "like" in result.lower()
    assert "design" in result.lower()


def test_remove_conversational_like():
    text = "I, like, think we should proceed."
    result = remove_filler_words(text)

    assert "like" not in result.lower()
    assert "think we should proceed" in result


def test_remove_redundant_whitespace():
    text = "  Hello    world   "
    result = clean_transcript(text)

    assert result == "Hello world"


def test_remove_blank_lines():
    text = "Alice: Hello\n\n\nBob: Hi"
    result = clean_transcript(text)

    assert result == "Alice: Hello\nBob: Hi"


def test_normalize_three_part_timestamp():
    assert normalize_timestamp("0:1:5") == "[00:01:05]"


def test_normalize_two_part_timestamp():
    assert normalize_timestamp("1:5") == "[00:01:05]"


def test_normalize_timestamps_in_transcript():
    text = "[0:1:5] Alice: Hello"
    result = normalize_timestamps(text)

    assert result == "[00:01:05] Alice: Hello"


def test_normalize_speaker_capitalization():
    assert normalize_speaker_turn("alice : Hello") == "Alice: Hello"
    assert normalize_speaker_turn("BOB: Hi") == "Bob: Hi"


def test_normalize_speaker_spacing():
    assert normalize_speaker_turn("Alice   :   Hello  ") == "Alice: Hello"


def test_clean_transcript_combines_normalization():
    text = (
        "[0:1:5] alice : Um, hello   everyone.\n"
        "\n"
        "BOB: Uh, welcome."
    )
    result = clean_transcript(text)

    assert result == (
        "[00:01:05] Alice: hello everyone.\n"
        "Bob: welcome."
    )


def test_empty_transcript():
    assert clean_transcript("") == ""


def test_transcript_with_only_blank_lines():
    assert clean_transcript("\n  \n\t\n") == ""


def test_currently_removes_actually():
    # Records the existing behavior; review semantic preservation
    # against the SRS before deciding whether to change it.
    result = remove_filler_words("The system actually works.")

    assert result == "The system works."