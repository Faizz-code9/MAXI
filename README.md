# 📝 Automated Meeting Minutes Generator (MiniMax)

> An end-to-end software pipeline that ingests meeting audio, transcribes dialogue (stub/engine), extracts action items, assignees, deadlines, and decisions using NLP heuristics, and formats them into structured minutes documents (Markdown/PDF).

[![CI Pipeline](https://github.com/Faizz-code9/MAXI/actions/workflows/ci.yml/badge.svg)](https://github.com/Faizz-code9/MAXI/actions/workflows/ci.yml)
[![Status](https://img.shields.io/badge/Status-Part--2%20Active-brightgreen)]()
[![Team](https://img.shields.io/badge/Team-4%20Members-blue)]()
[![Tests](https://img.shields.io/badge/Pytest-100%25%20Passing-success)]()
[![License](https://img.shields.io/badge/License-MIT-green)]()

---

## 🎯 SE Deliverables Part-2 Quick Links

* 📊 **Product Backlog & Sprint Plan (Markdown):** [`docs/BACKLOG_AND_SPRINT_PLAN.md`](docs/BACKLOG_AND_SPRINT_PLAN.md)
* 📄 **Product Backlog & Sprint Plan (Word .docx):** [`docs/BACKLOG_AND_SPRINT_PLAN.docx`](docs/BACKLOG_AND_SPRINT_PLAN.docx)
* 🤖 **GitHub Actions CI Workflow:** [`.github/workflows/ci.yml`](.github/workflows/ci.yml)
* 📋 **Pull Request Template:** [`.github/pull_request_template.md`](.github/pull_request_template.md)
* 📌 **User Story Issue Template:** [`.github/ISSUE_TEMPLATE/user_story.md`](.github/ISSUE_TEMPLATE/user_story.md)
* 📁 **JSON Backlog Export:** [`docs/github_issues.json`](docs/github_issues.json)

---

## ✨ System Architecture & Pipeline

```text
Audio File (.mp3, .wav, .m4a)
       │
       ▼
[transcriber.py] ──▶ Formatted Dialogue with Timestamps
       │
       ▼
[preprocessor.py] ──▶ Normalization & Filler Word Stripping ("um", "uh")
       │
       ▼
[extractor.py] ──▶ NLP Heuristics (Action Items, Assignees, Deadlines, Decisions)
       │
       ▼
[generator.py] ──▶ Structured Markdown & PDF Minutes Document
       │
       ▼
[models.py] ──▶ Persistent SQLite Storage (Meetings & Action Items)
       │
       ▼
[Frontend Dashboard] ──▶ Web UI (Upload Form, Minutes Viewer, History & Search)
```

---

## 🚀 Quick Start & Local Execution

### 1. Prerequisites
* Python 3.10+ (tested on Python 3.11, 3.12, 3.13)
* Git

### 2. Setup Virtual Environment
```bash
# Clone repository
git clone https://github.com/Faizz-code9/MAXI.git
cd MAXI

# Create virtual environment (Windows)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run Automated Tests
```bash
pytest src/tests/ -v
```

### 4. Launch Development Server
```bash
python src/backend/app.py
```
Open your browser at: **`http://127.0.0.1:5000`**

---

## 👥 Team Members & Responsibilities

| Member | SRN | Role | Part-2 Responsibilities |
|---|---|---|---|
| **Mohammed Faizan** | `PES1UG24AM472` | **Team Lead / Backend Core (Repo Owner)** | Project orchestration, audio transcriber engine (`transcriber.py`), Flask REST API (`app.py`), PR review and merge authority. |
| **Vinay M Rampur** | `PES1UG24AM455` | **Backend Developer (NLP Extractor)** | Text preprocessor (`preprocessor.py`), regex action items/decisions extractor (`extractor.py`), action item status toggle API. |
| **Kamal Kanth N** | `PES1UG24AM434` | **Frontend Developer (UI/UX)** | Dashboard HTML/CSS (`index.html`, `style.css`), AJAX client logic (`app.js`), History page search, recording video demos. |
| **Anagha Kaushik** | `PES1UG24AM459` | **QA & Testing / Generator** | SQLite schema & models (`models.py`), Markdown/PDF minutes generator (`generator.py`), test suite (`src/tests/`), GitHub Actions CI. |

---

## 📅 Part-2 Sprint Timelines

| Sprint / Milestone | Dates | Focus & Deliverables |
|---|---|---|
| **Backlog Creation in GitHub** | **ETA: 12th Oct 2026** | GitHub Project board, 20 User Stories, Story Points (Fibonacci scale), assignees mapped. |
| **Sprint Dry Run (Practice)** | **12th Oct – 16th Oct 2026** | Practice feature branching, PR raising, CI checks, and team reviews. |
| **Backlog Final Refinement** | **19th Oct 2026** | Final scope adjustments and story point verification. |
| **Sprint 1 Execution** | **19th Oct – 23rd Oct 2026** | Core Working MVP (Upload $\rightarrow$ Transcribe $\rightarrow$ Extract $\rightarrow$ View), GitHub Actions CI, **1-minute demo video**. |
| **Sprint 2 Execution** | **26th Oct – 30th Oct 2026** | PDF export, History & Search, action item editing, **2-minute demo video**, **Code Freeze**. |

---

## 🧪 CI/CD & Automated Quality Assurance

All pull requests and commits to `main` are automatically verified by **GitHub Actions** ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)):
* Automatic environment setup (Python 3.11 on Ubuntu)
* Dependency caching and installation
* Full `pytest` execution across unit and integration test suites
* Architectural import verification
* Strict merge policy: PRs must pass CI before repo owner merge.
