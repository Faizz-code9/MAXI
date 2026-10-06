"""
Minutes Document Generator Module
=================================
Owner: Anagha Kaushik (PES1UG24AM459)
Phase: 3 - Implementation Sprint 1

Generates structured Markdown and text formatted meeting minutes documents
conforming to the MiniMax standardized layout.
"""

from typing import Dict, List, Any
import os


def generate_markdown_minutes(
    title: str,
    date: str,
    duration: str,
    attendees: List[str],
    summary: str,
    decisions: List[str],
    action_items: List[Dict[str, str]],
    transcript: str = ""
) -> str:
    """
    Renders structured Markdown document matching MiniMax template:
    - Header & Metadata
    - Executive Summary
    - Attendees
    - Key Decisions
    - Action Items Table
    - Transcript Appendix
    """
    attendees_str = ", ".join(attendees) if attendees else "General Team"

    doc = []
    doc.append(f"# 📋 Meeting Minutes: {title}")
    doc.append("")
    doc.append("## 📌 Meeting Metadata")
    doc.append(f"- **Date:** {date}")
    doc.append(f"- **Duration:** {duration}")
    doc.append(f"- **Attendees:** {attendees_str}")
    doc.append(f"- **Status:** Finalized")
    doc.append("")
    doc.append("---")
    doc.append("")
    doc.append("## 📝 Executive Summary")
    doc.append(summary)
    doc.append("")
    doc.append("---")
    doc.append("")
    doc.append("## ⚖️ Key Decisions")
    if decisions:
        for idx, dec in enumerate(decisions, 1):
            doc.append(f"{idx}. {dec}")
    else:
        doc.append("*No formal decisions were recorded.*")
    doc.append("")
    doc.append("---")
    doc.append("")
    doc.append("## ✅ Action Items")
    if action_items:
        doc.append("| # | Task Description | Assignee | Deadline | Status |")
        doc.append("|---|---|---|---|---|")
        for idx, item in enumerate(action_items, 1):
            task = item.get("task", "N/A")
            assignee = item.get("assignee", "Unassigned")
            deadline = item.get("deadline", "TBD")
            status = item.get("status", "Pending")
            doc.append(f"| {idx} | {task} | **{assignee}** | `{deadline}` | {status} |")
    else:
        doc.append("*No action items identified.*")
    doc.append("")
    doc.append("---")
    doc.append("")
    doc.append("## 🎙️ Transcript Appendix")
    doc.append("```text")
    doc.append(transcript.strip())
    doc.append("```")
    doc.append("")

    return "\n".join(doc)

def save_markdown_minutes(markdown_content: str, filename: str, output_dir: str = "exports") -> str:
    """Saves generated meeting minutes as a Markdown file."""
    os.makedirs(output_dir, exist_ok=True)

    if not filename.endswith(".md"):
        filename += ".md"

    file_path = os.path.join(output_dir, filename)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(markdown_content)

    return file_path
