# 🧑‍🤝‍🧑 Team Guide — Phase 3: Implementation (Sprint 1)

## For: All 4 Team Members
* **Mohammed Faizan** (`PES1UG24AM472`) — Team Lead / Core Backend API
* **Vinay M Rampur** (`PES1UG24AM455`) — Backend Developer (Processing & Extractor)
* **Kamal Kanth N** (`PES1UG24AM434`) — Frontend Developer (UI / UX & Client Logic)
* **Anagha Kaushik** (`PES1UG24AM459`) — QA, Database & Minutes Generator

---

## 🎯 Phase 3 Goal: Minimum Viable Product (MVP)
In Phase 2 (SAD), we finalized the architecture, diagrams, schemas, and wireframes. 
In **Phase 3 (Sprint 1)**, our goal is to build the **working end-to-end software pipeline**:
$$\text{User uploads Audio} \longrightarrow \text{Transcriber} \longrightarrow \text{Extractor} \longrightarrow \text{Generator} \longrightarrow \text{Dashboard Display}$$

---

## 📂 Target Project Directory Structure

```text
Maxi/
├── docs/                         # Phase 1 (SRS) & Phase 2 (SAD) deliverables
│   ├── SRS.md / SRS.docx
│   ├── SAD.md / SAD.docx
│   ├── TEAM_GUIDE.md
│   ├── TEAM_GUIDE_PHASE2.md
│   └── TEAM_GUIDE_PHASE3.md     # This guide
├── src/
│   ├── backend/
│   │   ├── app.py                # [Faizan] Flask REST API & routing
│   │   ├── models.py             # [Anagha] SQLite DB schema & storage
│   │   ├── transcriber.py        # [Faizan] Audio intake & transcript engine
│   │   ├── preprocessor.py       # [Vinay] Text cleaner & normalizer
│   │   ├── extractor.py          # [Vinay] Regex & NLP action item extractor
│   │   └── generator.py          # [Anagha] Markdown & minutes document builder
│   ├── frontend/
│   │   ├── templates/
│   │   │   └── index.html        # [Kamal] Dashboard (Home, Viewer, History)
│   │   └── static/
│   │       ├── css/
│   │       │   └── style.css     # [Kamal] Styles matching wireframes
│   │       └── js/
│   │           └── app.js        # [Kamal] Audio upload & AJAX fetch calls
│   └── tests/
│       ├── test_extractor.py     # [Anagha & Vinay] Unit tests for extraction
│       └── test_api.py           # [Anagha & Faizan] API integration tests
├── uploads/                      # Uploaded audio files storage (gitignored)
├── sample_audio/                 # Sample test audio/transcript files
├── requirements.txt              # Project dependencies
└── README.md
```

---

## ⚡ Quick Setup for All Members

### 1. Pull Latest Repository
```bash
git pull origin main
```

### 2. Setup Python Virtual Environment (Windows)
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

*(On macOS/Linux: `source venv/bin/activate`)*

---

## 👥 Member-by-Member Detailed Task Breakdown

---

### 📌 1. Mohammed Faizan (Team Lead / Core Backend API)

**Assigned Files:**
* `requirements.txt`
* `src/backend/app.py`
* `src/backend/transcriber.py`

**Key Responsibilities:**
1. **Initialize Project Scaffolding:**
   - Define all required packages in `requirements.txt` (`flask`, `flask-cors`, `sqlalchemy`, `pytest`).
   - Create directories: `src/backend`, `src/frontend`, `uploads/`.

2. **Implement `src/backend/transcriber.py`:**
   - Validate audio file uploads:
     - Check file extensions (`.mp3`, `.wav`, `.m4a`).
     - Check file size limit ($\le 100\text{ MB}$).
   - Build a realistic transcription engine:
     - Ingests audio files and converts speech to formatted transcript text with speaker labels and timestamps (e.g., `[00:01:15] Speaker 1: Let's finalize the sprint goals...`).
     - Includes sample fallback audio processing for immediate demo testing.

3. **Implement `src/backend/app.py` (Flask REST API):**
   - Setup Flask server with CORS enabled.
   - Implement the primary endpoints defined in SAD Section 4.3:
     - `POST /api/upload`: Receives multipart audio file, saves to `uploads/`, invokes `transcriber.py`, stores meeting record in DB, and returns `meeting_id`.
     - `POST /api/process`: Triggers `preprocessor.py`, `extractor.py`, and `generator.py` for the given meeting ID.
     - `GET /api/meetings`: Returns list of all past meetings (for History view).
     - `GET /api/meetings/<id>`: Returns full meeting minutes details (summary, decisions, action items).
     - `GET /api/meetings/<id>/export`: Downloads minutes as `.md` or formatted text file.

**Git Commit & Push:**
```bash
git add requirements.txt src/backend/app.py src/backend/transcriber.py
git commit -m "feat(backend): Faizan - implemented Flask API endpoints and audio transcriber engine"
git push origin main
```

---

### 📌 2. Vinay M Rampur (Backend Developer — Data Processing & Extractor)

**Assigned Files:**
* `src/backend/preprocessor.py`
* `src/backend/extractor.py`

**Key Responsibilities:**
1. **Implement `src/backend/preprocessor.py`:**
   - Clean raw transcription text:
     - Strip conversational filler words (`um`, `uh`, `like`, `you know`, `err`).
     - Normalize timestamps (e.g., `[00:12:30]`).
     - Standardize speaker turns (e.g., `Alice:`, `Bob:`).
     - Remove redundant whitespace and artifacts.

2. **Implement `src/backend/extractor.py` (Core NLP Engine):**
   - **Action Item Extraction:**
     - Use pattern matching and regex heuristics to detect task commitments:
       - Triggers: `action item`, `todo`, `assigned to`, `will handle`, `agreed to`, `responsible for`, `needs to`.
     - Extract three key properties for each item:
       1. `task`: Description of work to be done.
       2. `assignee`: Person responsible (e.g., John, Alice, Dev Team).
       3. `deadline`: Extracted dates/days (e.g., `Friday`, `by Oct 15`, `next week`, `EOD`).
   - **Key Decision Extraction:**
     - Detect agreed decisions using trigger phrases:
       - Triggers: `we decided`, `agreed upon`, `consensus is`, `conclusion:`, `approved`.
   - **Key Topics & Attendees Extraction:**
     - Identify attendee names from speaker tags.
     - Extract main meeting topics/keywords.

**Function Signatures Expected:**
```python
def clean_transcript(raw_text: str) -> str:
    """Removes filler words and normalizes whitespace."""
    ...

def extract_action_items(cleaned_text: str) -> list[dict]:
    """Returns list of dicts: [{'task': ..., 'assignee': ..., 'deadline': ..., 'status': 'Pending'}]"""
    ...

def extract_decisions(cleaned_text: str) -> list[str]:
    """Returns list of string decisions."""
    ...
```

**Git Commit & Push:**
```bash
git add src/backend/preprocessor.py src/backend/extractor.py
git commit -m "feat(extractor): Vinay - implemented text preprocessor and regex action item extractor"
git push origin main
```

---

### 📌 3. Kamal Kanth N (Frontend Developer — UI / UX & Client Logic)

**Assigned Files:**
* `src/frontend/templates/index.html`
* `src/frontend/static/css/style.css`
* `src/frontend/static/js/app.js`

**Key Responsibilities:**
1. **Implement `index.html` (Single-Page Application Dashboard):**
   - Build layout strictly following the 3 wireframes designed in Phase 2:
     - **Section 1: Header & Navigation** (App brand "MiniMax Automated Minutes", Nav tabs: *Upload*, *Minutes Viewer*, *History*).
     - **Section 2: Upload Zone (`wireframe_home.png`)**:
       - Drag & Drop audio upload box with browse file button.
       - Inputs: Meeting Title, Meeting Date, Department / Project tag.
       - "Generate Minutes" action button with upload progress indicator.
     - **Section 3: Minutes Viewer (`wireframe_minutes_viewer.png`)**:
       - Meeting Header (Title, Date, Duration, Attendees badges).
       - Summary card.
       - Key Decisions list.
       - Action Items table (`Task`, `Assignee`, `Deadline`, `Status Badge`).
       - Action buttons: "Export Markdown", "Export PDF", "Copy to Clipboard".
     - **Section 4: Meeting History (`wireframe_history.png`)**:
       - Search filter input (by keyword or date).
       - Table / Grid of past meetings with "View" and "Download" buttons.

2. **Implement `style.css`:**
   - Modern, professional UI design:
     - Primary theme: Indigo/Blue (`#4F46E5`), Slate gray backgrounds (`#F8FAFC`), crisp typography (`Inter` / system-ui).
     - Responsive grid and card system.
     - Styling for drag & drop zone with hover/active states.
     - Badges for status (`Pending`, `In Progress`, `Completed`).

3. **Implement `app.js` (Client-Side Logic & API Integration):**
   - Intercept file selection and handle drag & drop events.
   - Make asynchronous `fetch()` requests to Flask backend:
     - Send audio file to `POST /api/upload`.
     - Show loading spinner/progress bar while processing.
     - Render extracted minutes dynamically into the Minutes Viewer on response.
     - Fetch `GET /api/meetings` to populate the History tab.
     - Handle export downloads via `GET /api/meetings/<id>/export`.

**Git Commit & Push:**
```bash
git add src/frontend/
git commit -m "feat(frontend): Kamal - created dashboard UI, styling, and AJAX client handlers"
git push origin main
```

---

### 📌 4. Anagha Kaushik (QA, Database & Minutes Generator)

**Assigned Files:**
* `src/backend/models.py`
* `src/backend/generator.py`
* `src/tests/test_extractor.py`
* `src/tests/test_api.py`

**Key Responsibilities:**
1. **Implement `src/backend/models.py` (Database Layer):**
   - Implement the SQLite schema defined in ER Diagram (SAD Section 4.6):
     - `Meeting` model: `id`, `title`, `date`, `audio_filename`, `raw_transcript`, `summary`, `created_at`.
     - `ActionItem` model: `id`, `meeting_id` (FK), `task`, `assignee`, `deadline`, `status`.
   - Provide helper database functions:
     - `save_meeting()`, `get_meeting(id)`, `list_meetings()`, `update_action_item_status()`.

2. **Implement `src/backend/generator.py` (Document Generator):**
   - Format extracted data into a standard structured Markdown minutes document:
     - Title & Metadata Header.
     - Attendees list.
     - Executive Summary.
     - Discussion Topics & Key Decisions.
     - Action Items Table (Markdown formatted table with `Task`, `Assignee`, `Deadline`).
   - Provide file output handler (saves `.md` file to disk for export).

3. **Implement Unit & Integration Tests (`src/tests/`):**
   - `test_extractor.py`: Test `clean_transcript()` and `extract_action_items()` with sample meeting dialogues.
   - `test_api.py`: Test Flask `/api/upload` and `/api/meetings` endpoints using `pytest`.
   - Ensure all tests pass with exit code `0`.

**Git Commit & Push:**
```bash
git add src/backend/models.py src/backend/generator.py src/tests/
git commit -m "feat(storage-qa): Anagha - implemented database models, minutes generator, and test suite"
git push origin main
```

---

## 🔄 Integration & Execution (How to Run Everything)

Once each member commits their files, run the integrated app:

```bash
# 1. Activate venv
venv\Scripts\activate

# 2. Run test suite
pytest src/tests/

# 3. Start local development server
python src/backend/app.py
```

Open your browser at:
👉 **`http://127.0.0.1:5000`**

---

## 📅 Sprint 1 Timeline & Checkpoints

| Checkpoint | Target | Deliverable |
|---|---|---|
| **Day 1** | Scaffolding & Setup | `requirements.txt` ready, virtual env active for all 4 members |
| **Day 2** | Core Backend & Data Logic | `models.py` (Anagha), `preprocessor.py` + `extractor.py` (Vinay) |
| **Day 3** | Transcriber & API Routes | `transcriber.py` + `app.py` (Faizan), `generator.py` (Anagha) |
| **Day 4** | Frontend Dashboard | `index.html` + `style.css` + `app.js` (Kamal) |
| **Day 5** | Integration & Testing | Full test suite passes (`pytest`), end-to-end audio upload working |

---

## 🏆 Sprint 1 "Definition of Done" (DoD)

- [ ] Audio upload accepts `.mp3`, `.wav`, `.m4a`.
- [ ] Transcriber produces formatted speaker transcript.
- [ ] Extractor successfully identifies action items, assignees, and deadlines.
- [ ] Generator outputs clean, structured Markdown minutes document.
- [ ] Frontend displays upload interface, minutes viewer, and meeting history.
- [ ] `pytest src/tests/` passes without errors.
- [ ] Code committed and cleanly merged to `origin/main`.
