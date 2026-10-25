"""
Minutes Document Generator Module
=================================
Owner: Anagha Kaushik (PES1UG24AM459)
Phase: 3 - Implementation Sprint 1

Generates structured Markdown and text formatted meeting minutes documents
conforming to the MiniMax standardized layout.
"""

from typing import Dict, List, Any, Optional
import html
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


# ---------------------------------------------------------------------------
# PDF export (US-15 / MM-F-011 / TC-GEN-02)
# ---------------------------------------------------------------------------

_PDF_CSS = """
@page {
  size: A4;
  margin: 18mm 16mm 20mm 16mm;
  @bottom-center {
    content: "Page " counter(page) " of " counter(pages);
    font-size: 9pt;
    color: #64748b;
  }
}
body { font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; color: #0f172a;
       font-size: 11pt; line-height: 1.5; }
h1 { color: #4338ca; font-size: 20pt; border-bottom: 2px solid #e2e8f0;
     padding-bottom: 6px; margin: 0 0 12px 0; }
h2 { color: #1e1b4b; font-size: 14pt; margin: 20px 0 6px 0;
     border-bottom: 1px solid #e2e8f0; padding-bottom: 3px; }
.meta { background: #f8fafc; border-left: 4px solid #4338ca;
        padding: 8px 14px; margin: 12px 0; }
.meta p { margin: 3px 0; }
.summary { background: #f8fafc; border: 1px solid #e2e8f0; padding: 8px 14px; }
ol, ul { padding-left: 20px; }
li { margin-bottom: 4px; }
table { width: 100%; border-collapse: collapse; margin-top: 6px; }
th, td { border: 1px solid #cbd5e1; padding: 6px 9px; text-align: left;
         font-size: 10pt; vertical-align: top; }
th { background: #f1f5f9; font-size: 9pt; text-transform: uppercase; }
tr { page-break-inside: avoid; }
.empty { color: #64748b; font-style: italic; }
"""


def _esc(value: Any) -> str:
    """
    Escape any value for safe HTML output.

    Values may already be HTML-escaped by the upload route, so they are
    unescaped first to avoid double-escaping (e.g. "&amp;amp;").
    """
    return html.escape(html.unescape(str(value if value is not None else "")))


def generate_html_minutes(
    title: str,
    date: str,
    duration: str,
    attendees: List[str],
    summary: str,
    decisions: List[str],
    action_items: List[Dict[str, str]],
    auto_print: bool = False,
) -> str:
    """
    Renders meeting minutes as a styled, print-ready HTML document.

    All meeting data is HTML-escaped. This HTML is the source for the PDF and
    is also the fallback view when PDF rendering is unavailable.
    """
    attendees_str = ", ".join(_esc(a) for a in attendees) if attendees else "General Team"

    if decisions:
        decisions_html = "<ol>" + "".join(f"<li>{_esc(d)}</li>" for d in decisions) + "</ol>"
    else:
        decisions_html = '<p class="empty">No formal decisions were recorded.</p>'

    if action_items:
        rows = "".join(
            "<tr>"
            f"<td>{idx}</td>"
            f"<td>{_esc(item.get('task', 'N/A'))}</td>"
            f"<td><strong>{_esc(item.get('assignee') or 'Unassigned')}</strong></td>"
            f"<td>{_esc(item.get('deadline') or 'TBD')}</td>"
            f"<td>{_esc(item.get('status') or 'Pending')}</td>"
            "</tr>"
            for idx, item in enumerate(action_items, 1)
        )
        actions_html = (
            "<table><thead><tr><th>#</th><th>Task</th><th>Assignee</th>"
            "<th>Deadline</th><th>Status</th></tr></thead>"
            f"<tbody>{rows}</tbody></table>"
        )
    else:
        actions_html = '<p class="empty">No action items recorded.</p>'

    print_script = (
        "<script>window.onload = function() { window.print(); };</script>"
        if auto_print else ""
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Meeting Minutes - {_esc(title)}</title>
  <style>{_PDF_CSS}</style>
  {print_script}
</head>
<body>
  <h1>Meeting Minutes: {_esc(title)}</h1>
  <div class="meta">
    <p><strong>Date:</strong> {_esc(date)} &nbsp;|&nbsp; <strong>Duration:</strong> {_esc(duration or "N/A")}</p>
    <p><strong>Attendees:</strong> {attendees_str}</p>
  </div>
  <h2>Executive Summary</h2>
  <div class="summary">{_esc(summary) or "No summary recorded."}</div>
  <h2>Key Decisions</h2>
  {decisions_html}
  <h2>Action Items</h2>
  {actions_html}
</body>
</html>"""


def generate_pdf_minutes(html_document: str) -> Optional[bytes]:
    """
    Converts the minutes HTML into PDF bytes using WeasyPrint (SAD 3.4).

    Returns None if WeasyPrint or its system libraries (Pango) are not
    available, so callers can fall back to the HTML print view (SAD risk R3).
    """
    try:
        from weasyprint import HTML
    except (ImportError, OSError):
        return None

    try:
        return HTML(string=html_document).write_pdf()
    except Exception:
        return None
