# 📝 Automated Meeting Minutes Generator (MiniMax)

> A tool that transcribes uploaded meeting audio, extracts action items via keyword patterns, and formats them into a structured minutes document.

[![Status](https://img.shields.io/badge/Status-In%20Development-yellow)]()
[![Team](https://img.shields.io/badge/Team-4%20Members-blue)]()
[![License](https://img.shields.io/badge/License-MIT-green)]()

---

## 🎯 Project Overview

**Automated Meeting Minutes Generator** is a Software Engineering course project that integrates:

- **Audio-to-Text Conversion** — Upload meeting audio and convert it to text (stub/API-based transcription).
- **Text-Processing Pipelines** — Extract action items, decisions, and key discussion points using keyword pattern matching and NLP techniques.
- **Templated Document Generation** — Format extracted information into a clean, structured meeting minutes document (PDF/Markdown).

## ✨ Key Features (Planned)

| Feature | Description |
|---|---|
| 🎙️ Audio Upload | Support for common audio formats (MP3, WAV, M4A) |
| 📄 Transcription | Audio-to-text conversion (stub with option for API integration) |
| 🔍 Action Item Extraction | Keyword and pattern-based extraction of action items, deadlines, and owners |
| 📊 Summary Generation | Auto-generated meeting summary with key discussion points |
| 📑 Document Export | Structured minutes in Markdown and PDF formats |
| 🗂️ Meeting History | Store and browse past meeting minutes |

## 🏗️ Tech Stack (Proposed)

| Layer | Technology |
|---|---|
| **Frontend** | React.js / HTML-CSS-JS |
| **Backend** | Python (Flask / FastAPI) |
| **Transcription** | SpeechRecognition / Whisper API (stub) |
| **NLP / Text Processing** | spaCy / regex patterns |
| **Document Generation** | Jinja2 templates + WeasyPrint (PDF) |
| **Database** | SQLite / PostgreSQL |
| **Version Control** | Git & GitHub |

## 📁 Project Structure (Planned)

```
Maxi/
├── docs/                    # All SE documents (SRS, SDD, Test Plan, etc.)
│   ├── SRS.md
│   ├── SDD.md
│   └── ...
├── src/                     # Source code
│   ├── frontend/            # UI components
│   ├── backend/             # API & business logic
│   │   ├── transcription/   # Audio-to-text module
│   │   ├── extractor/       # Action item extraction
│   │   └── generator/       # Document generation
│   └── tests/               # Unit & integration tests
├── templates/               # Meeting minutes templates
├── uploads/                 # Uploaded audio files (gitignored)
├── output/                  # Generated minutes (gitignored)
├── requirements.txt
├── README.md
└── .gitignore
```

## 🚀 Getting Started

> _Setup instructions will be added as development progresses._

```bash
# Clone the repository
git clone <repo-url>
cd Maxi

# Install dependencies (coming soon)
pip install -r requirements.txt

# Run the application (coming soon)
python src/backend/app.py
```

## 👥 Team

| Member | Role | Responsibilities |
|---|---|---|
| Member 1 | Team Lead / Backend | Project coordination, Transcription module |
| Member 2 | Backend Developer | Text processing & action item extraction |
| Member 3 | Frontend Developer | UI/UX, upload interface, minutes display |
| Member 4 | Testing & Docs | SRS, SDD, test cases, document generation |

## 📅 Development Phases

| Phase | Deliverable | Timeline |
|---|---|---|
| Phase 1 | Requirements & SRS Document | Week 1-2 |
| Phase 2 | System Design (SDD) | Week 3-4 |
| Phase 3 | Implementation (Sprint 1 - Core) | Week 5-7 |
| Phase 4 | Implementation (Sprint 2 - Features) | Week 8-9 |
| Phase 5 | Testing & QA | Week 10-11 |
| Phase 6 | Deployment & Final Report | Week 12 |

## 📜 License

This project is licensed under the MIT License.

---

*Built with ❤️ as a Software Engineering course project.*
