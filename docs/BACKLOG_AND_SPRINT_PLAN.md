# 📊 MiniMax — Product Backlog & Two-Sprint Implementation Plan

## Software Engineering Mini-Project Deliverables: Part-2

* **Project Title:** Automated Meeting Minutes Generator (MiniMax)
* **Repository:** [https://github.com/Faizz-code9/MAXI](https://github.com/Faizz-code9/MAXI)
* **Team Members:**
  * **Mohammed Faizan** (`PES1UG24AM472`) — Team Lead / Backend Core & Integration (Repo Owner)
  * **Vinay M Rampur** (`PES1UG24AM455`) — Backend Developer (NLP Extraction & Preprocessing)
  * **Kamal Kanth N** (`PES1UG24AM434`) — Frontend Developer (UI/UX & Client Logic)
  * **Anagha Kaushik** (`PES1UG24AM459`) — QA & Testing / Database & Minutes Generator

---

## 📅 Schedule & Key Milestones Overview

| Milestone | Window / ETA | Key Objectives | Status |
|---|---|---|---|
| **Backlog & Project Setup** | **12th Oct 2026** | Create GitHub Project board, link repo, convert FR/NFR to User Stories, assign Story Points (SP) and assignees. | ✅ Documented |
| **Sprint Dry Run (Practice)** | **12th Oct – 16th Oct 2026** | Team dry-run of git feature branches, test PR raising, test CI execution, local environment sanity check. | ⏳ Scheduled |
| **Backlog Final Refinement** | **19th Oct 2026** | Review and finalize story estimates, adjust any acceptance criteria before Sprint 1 kickoff. | ⏳ Scheduled |
| **Sprint 1 Execution** | **19th Oct – 23rd Oct 2026** | Implement Core Working MVP, automated GitHub Actions CI, raise and review PRs, record **1-minute video demo**. | ⏳ Active |
| **Sprint 2 Execution** | **26th Oct – 30th Oct 2026** | Implement PDF export, history & search, action item editing, record **2-minute video demo**, complete docs, **Freeze**. | ⏳ Scheduled |

---

## 🛠️ 1. GitHub Project Setup & Linking Instructions

### A. How to Create the GitHub Project
1. Open the repository on GitHub: [`https://github.com/Faizz-code9/MAXI`](https://github.com/Faizz-code9/MAXI).
2. Click on the **Projects** tab at the top.
3. Click **"New project"** $\rightarrow$ select **"Board"** template.
4. Name the project: **`MiniMax - SE Sprint Board`**.
5. Link repository: Under project settings, click **"Manage access"** or **"Linked repositories"** and link `Faizz-code9/MAXI`.

### B. Board Columns & Custom Fields Setup
Configure the board with the following columns:
* **📋 Product Backlog** (all unstarted user stories)
* **🏃 Sprint 1 (In Progress)** (items active in Sprint 1)
* **👀 In Review / PR Open** (PR raised by assigned team member, awaiting review)
* **🏃 Sprint 2 (Planned)** (items scheduled for Sprint 2)
* **✅ Done** (PR reviewed, merged by Repo Owner, tests passing)

**Custom Project Fields:**
* **Story Points (SP):** Number field (Fibonacci: 1, 2, 3, 5, 8)
* **Sprint:** Single select (`Sprint 1`, `Sprint 2`)
* **SRS Requirement:** Text field (e.g. `MM-F-001`, `MM-NF-001`)

---

## 🔢 2. Story Point Estimation Methodology

Story Points are estimated using the **Planning Poker / Fibonacci Scale** ($1, 2, 3, 5, 8$), representing effort, technical complexity, and uncertainty:

* **1 SP:** Trivial change, configuration update, or minor UI tweak (e.g., label changes, status badges).
* **2 SP:** Well-defined small component or helper function (e.g., regex filler-word cleaner, input validation).
* **3 SP:** Standard feature module with clear scope and tests (e.g., SQLite model setup, Markdown generator, history table).
* **5 SP:** Complex core component requiring algorithmic logic or multi-tier integration (e.g., NLP extraction engine, REST upload pipeline, PDF rendering engine).
* **8 SP:** Large architectural subsystem (none allowed; decomposed into smaller 3/5 SP stories).

**Velocity Planning:**
* **Total Product Backlog:** **59 Story Points** across 20 User Stories.
* **Sprint 1 Target:** **37 Story Points** (Focus: Core Working MVP Pipeline).
* **Sprint 2 Target:** **22 Story Points** (Focus: Feature Polish, PDF Export, History Search, Code Freeze).

---

## 📋 3. Complete Product Backlog (Mapped to SRS FRs & NFRs)

| Story ID | User Story Title & Description | SRS Mapping | SP | Assignee | Sprint | Priority |
|---|---|---|---|---|---|---|
| **US-01** | **Audio Upload Drag-and-Drop Form**<br>*As a user, I want to drag and drop audio recordings (.mp3, .wav, .m4a) on the dashboard, so that I can easily submit meeting recordings.* | MM-F-001, MM-F-017, MM-NF-002 | **3** | Kamal Kanth N | Sprint 1 | High |
| **US-02** | **Audio Format & Size Validation**<br>*As a backend system, I want to validate file extensions, MIME types, and enforce the 100MB limit with friendly error alerts, so that invalid files are rejected safely.* | MM-F-002, MM-F-003, MM-SR-005 | **2** | Mohammed Faizan | Sprint 1 | High |
| **US-03** | **Transcription Engine & Progress Visualizer**<br>*As a user, I want the audio transcribed into structured speaker dialogue with a real-time progress bar, so that I know the pipeline is processing.* | MM-F-004, MM-F-005, MM-NF-001 | **5** | Mohammed Faizan | Sprint 1 | High |
| **US-04** | **Transcript Cleaning & Filler Word Removal**<br>*As an NLP engine, I want conversational fillers ("um", "uh", "like") stripped and timestamps standardized, so that text extraction accuracy is maximized.* | MM-F-018 | **2** | Vinay M Rampur | Sprint 1 | High |
| **US-05** | **Action Item & Task Detection**<br>*As a participant, I want tasks extracted using action triggers ("action item:", "TODO", "will", "needs to"), so that commitments are recorded.* | MM-F-006, MM-F-020 | **5** | Vinay M Rampur | Sprint 1 | High |
| **US-06** | **Assignee & Deadline Extraction**<br>*As a project lead, I want assignees and date expressions ("by Friday", "by Monday") linked to each action item, so that task ownership is clear.* | MM-F-007, MM-F-008 | **3** | Vinay M Rampur | Sprint 1 | High |
| **US-07** | **Key Decisions & Discussion Points Extraction**<br>*As a team member, I want explicit consensus decisions ("we decided", "agreed") extracted separately from general discussion, so that agreements are obvious.* | MM-F-009, MM-F-019 | **3** | Vinay M Rampur | Sprint 1 | Medium |
| **US-08** | **SQLite Schema & Data Persistence**<br>*As a backend service, I want meeting metadata, transcripts, and action items stored persistently in an SQLite database, so that data survives server restarts.* | MM-F-013, MM-NF-006 | **3** | Anagha Kaushik | Sprint 1 | High |
| **US-09** | **Structured Markdown Minutes Generator**<br>*As a user, I want a standardized Markdown document generated with meeting metadata, summary, decisions, and action items table, so that it can be reviewed and exported.* | MM-F-010 | **3** | Anagha Kaushik | Sprint 1 | High |
| **US-10** | **Backend REST API Route Integration**<br>*As a frontend client, I want `/api/upload`, `/api/meetings`, and CORS-enabled endpoints, so that the UI can interactively trigger the pipeline.* | MM-F-001, MM-F-004, MM-F-010 | **5** | Mohammed Faizan | Sprint 1 | High |
| **US-11** | **Minutes Viewer Dashboard UI**<br>*As a user, I want an interactive Minutes Viewer displaying summary, decision lists, and an action items table with status tags, so that I can inspect meeting output.* | MM-F-010, MM-NF-002 | **3** | Kamal Kanth N | Sprint 1 | High |
| **US-12** | **Automated CI/CD Pipeline & Test Suite**<br>*As a QA engineer, I want GitHub Actions to run pytest automatically on every push and PR, so that broken builds are caught immediately.* | MM-NF-005, MM-NF-006 | **3** | Anagha Kaushik | Sprint 1 | High |
| **US-13** | **Meeting History Listing & Navigation**<br>*As a user, I want a History page listing past meetings sorted by date with "View" and "Export" buttons, so that I can revisit earlier discussions.* | MM-F-014, MM-NF-002 | **3** | Kamal Kanth N | Sprint 2 | Medium |
| **US-14** | **Meeting History Search by Title and Date**<br>*As a user, I want an interactive search bar in History to filter meetings instantly by keyword or date, so that I can locate specific discussions in seconds.* | MM-F-015 | **3** | Kamal Kanth N | Sprint 2 | Medium |
| **US-15** | **PDF Minutes Export Engine**<br>*As a user, I want to export generated minutes as a downloadable, beautifully formatted PDF document, so that I can print or distribute it to stakeholders.* | MM-F-011 | **5** | Anagha Kaushik | Sprint 2 | High |
| **US-16** | **Interactive Action Item Status Updating**<br>*As a meeting organizer, I want to toggle action item statuses between "Pending" and "Completed" via `PUT /api/action-items/<id>`, so that I can keep task tracking updated.* | MM-F-012 | **3** | Vinay M Rampur | Sprint 2 | Medium |
| **US-17** | **API Security, Sanitization & Audit Logging**<br>*As a system auditor, I want input sanitization, file path traversal protection, and timestamped error logging, so that user data and server storage remain secure.* | MM-SR-004, MM-SR-006, MM-NF-006 | **3** | Mohammed Faizan | Sprint 2 | High |
| **US-18** | **System Performance & Concurrency Testing**<br>*As a QA engineer, I want to execute load tests validating sub-60-second processing and multi-user concurrency, so that NFR benchmarks are verified.* | MM-NF-001, MM-NF-003 | **3** | Anagha Kaushik | Sprint 2 | Medium |
| **US-19** | **Traceability Matrix & Documentation Freeze**<br>*As a team lead, I want all SE documents (SRS, SAD, RTM, Test Plan) synchronized with final code and deviations logged, so that deliverables are frozen for evaluation.* | All Deliverables | **2** | Mohammed Faizan | Sprint 2 | High |
| **US-20** | **Video Demonstration Recordings**<br>*As a project evaluator, I want 1-minute Sprint 1 and 2-minute Sprint 2 product demonstration videos showing working software, so that progress is verifiable.* | Deliverable Part-2 | **3** | Kamal Kanth N | Sprint 2 | High |

---

## 🏃 4. Sprint 1 Plan [19th Oct to 23rd Oct 2026]

### Sprint Goal:
Deliver a **fully functioning Minimum Viable Product (MVP)** capable of ingesting an audio file, transcribing it, extracting action items and decisions, saving to SQLite, displaying in a responsive dashboard, and generating Markdown minutes.

### Sprint 1 Stories & Work Allocation:
* **Mohammed Faizan (12 SP):**
  * `US-02`: Audio validation & size guard (`transcriber.py`)
  * `US-03`: Audio transcriber engine & progress feedback (`transcriber.py`)
  * `US-10`: Flask REST API routes & orchestration (`app.py`)
* **Vinay M Rampur (13 SP):**
  * `US-04`: Text preprocessor & filler word cleaner (`preprocessor.py`)
  * `US-05`: Action item regex extractor (`extractor.py`)
  * `US-06`: Assignee & deadline extraction (`extractor.py`)
  * `US-07`: Key decisions & discussion points extractor (`extractor.py`)
* **Kamal Kanth N (6 SP):**
  * `US-01`: Drag-and-drop audio upload form (`index.html`, `style.css`)
  * `US-11`: Minutes Viewer UI & copy-to-clipboard handler (`index.html`, `app.js`)
* **Anagha Kaushik (6 SP):**
  * `US-08`: SQLite models & database persistence layer (`models.py`)
  * `US-09`: Structured Markdown minutes document generator (`generator.py`)
  * `US-12`: GitHub Actions CI pipeline & pytest test suite (`ci.yml`, `test_extractor.py`, `test_api.py`)

### Sprint 1 Required Deliverables:
1. All 12 stories implemented and merged to `main`.
2. Automated GitHub Actions CI workflow passing on all PRs.
3. **1-Minute Demo Video:** Uploaded to repo under `demos/sprint1_demo.mp4` (or unlisted video link in README).

---

## 🚀 5. Sprint 2 Plan [26th Oct to 30th Oct 2026]

### Sprint Goal:
Deliver the **feature-complete product**, including PDF export, meeting history navigation & search, interactive action item status toggling, security hardening, final documentation synchronization, and code freeze.

### Sprint 2 Stories & Work Allocation:
* **Kamal Kanth N (9 SP):**
  * `US-13`: Meeting history page & table navigation (`index.html`, `app.js`)
  * `US-14`: Search filter for historical meetings (`app.js`)
  * `US-20`: Recording, editing, and uploading the 2-minute Sprint 2 demo video
* **Anagha Kaushik (8 SP):**
  * `US-15`: PDF export service with WeasyPrint / HTML print styling
  * `US-18`: Concurrency and latency performance verification
* **Mohammed Faizan (5 SP):**
  * `US-17`: Security checks, path traversal guards, structured audit logging
  * `US-19`: Synchronizing SRS/SAD/RTM documentation and enforcing code freeze
* **Vinay M Rampur (3 SP):**
  * `US-16`: In-place action item status toggle API & database update

### Sprint 2 Required Deliverables:
1. Feature development frozen on **30th Oct 2026**.
2. **2-Minute Demo Video:** Uploaded under `demos/sprint2_demo.mp4`.
3. Complete documentation package ready for evaluation.

---

## 🤖 6. GitHub Actions Automation & PR Protocol

### A. CI Workflow (`.github/workflows/ci.yml`)
The repository is equipped with an automated GitHub Actions workflow that triggers on every `push` and `pull_request` to `main`:
1. Checks out repository code.
2. Configures Python 3.11 with pip caching.
3. Installs dependencies from `requirements.txt`.
4. Executes the automated test suite with `pytest src/tests/ -v`.
5. Verifies package import integrity across all backend modules.
6. **PR Rule:** A PR cannot be merged if the CI build fails (red cross).

### B. Pull Request (PR) Raising & Review Protocol
Per course requirements:
1. **Feature Branching:** Each team member develops on their own feature branch:
   ```bash
   git checkout -b feature/vinay-action-extractor
   # or
   git checkout -b feature/kamal-upload-ui
   ```
2. **Raising the PR:**
   - The assigned member pushes their branch to GitHub and opens a Pull Request targeting `main`.
   - The PR title must reference the story: e.g. `feat(extractor): [US-05] Implement action item regex extractor`.
   - The PR description must use the template at `.github/pull_request_template.md`.
3. **Review & Merge (Repo Owner):**
   - **Mohammed Faizan** (Repo Owner) reviews the diff, checks code quality and verifies that the GitHub Actions CI check has passed.
   - Upon review, Faizan approves and commits/merges the PR into `main`.

---

## 🎬 7. Video Demonstration Guidelines & Scripts

### A. Sprint 1 Video (Length: Exactly 1 Minute)
* **Goal:** Prove you have a working core product (audio in $\rightarrow$ minutes out).
* **Location:** `demos/sprint1_demo.mp4`

| Timestamp | Screen Display | Voiceover / Action |
|---|---|---|
| **0:00 – 0:15** | MiniMax Dashboard Home Page | Introduce MiniMax, show the drag-and-drop audio upload zone, and enter meeting title: *"Sprint 1 Architecture Sync"*. |
| **0:15 – 0:35** | Upload & Processing | Drag in sample audio (`.mp3`), click *"Generate Meeting Minutes"*, show the dynamic progress bar moving through transcription. |
| **0:35 – 0:50** | Minutes Viewer Outcome | Show the automatically generated output: Attendees list badges, Executive Summary, Key Decisions list, and Action Items table with assignees and deadlines. |
| **0:50 – 1:00** | Export & Automated CI | Click *"Export Markdown"*, show the generated file, and show GitHub Actions green checkmark passing the test suite. |

---

### B. Sprint 2 Video (Length: Exactly 2 Minutes)
* **Goal:** Showcase the full end-to-end product with history, search, PDF export, and action item editing.
* **Location:** `demos/sprint2_demo.mp4`

| Timestamp | Screen Display | Voiceover / Action |
|---|---|---|
| **0:00 – 0:25** | System Architecture & Overview | Brief introduction to MiniMax 4-tier architecture and team roles. |
| **0:25 – 0:55** | Complete Audio Processing Pipeline | Upload a new recording, observe transcription, NLP extraction, and database persistence. |
| **0:55 – 1:20** | Interactive Minutes Viewer & PDF Export | Demonstrate toggling an action item from "Pending" to "Completed", and download the finalized PDF export. |
| **1:20 – 1:45** | Meeting History & Instant Search | Switch to History tab, demonstrate instant search filtering by keyword and date, open past meeting. |
| **1:45 – 2:00** | CI/CD, Test Coverage & Code Freeze | Show passing GitHub Actions pipeline, test coverage report, and announce final development freeze. |

---

## 📝 8. Deviations Tracking Log

Course requirement: *“Deviations from the submitted document should be documented and explained during the final demo.”*

| Deviation ID | Planned Specification (SRS / SAD) | Implemented Specification | Reason & Justification | Impact on Project |
|---|---|---|---|---|
| **DEV-01** | User authentication with login/register (MM-F-016) required for single-tenant local demo. | Simplified single-tenant session model without authentication barrier for local desktop evaluation. | Faster user workflow during live instructor evaluation; avoids login friction during short demo. | No loss of core functionality; database and privacy models remain intact. |
| **DEV-02** | External speech-to-text API (e.g. OpenAI Whisper API). | Intelligent offline transcription engine stub with realistic speaker turns and timestamps. | Guarantees 100% offline determinism, eliminates API rate limits/costs, and adheres to course project constraints. | Zero dependency on external network or paid API keys. |
| **DEV-03** | Server-side WeasyPrint PDF renderer. | Dual export: Direct Markdown (`.md`) export and browser print-to-PDF engine. | Eliminates complex OS-level GTK/Cairo library installation dependencies on student Windows machines. | Identical visual PDF output with greater cross-platform portability. |

---

## ✅ Deliverable Part-2 Checklist for Evaluation

- [x] GitHub Actions CI workflow implemented and automated (`.github/workflows/ci.yml`).
- [x] Standard Pull Request template enabled (`.github/pull_request_template.md`).
- [x] Standard User Story Issue template enabled (`.github/ISSUE_TEMPLATE/user_story.md`).
- [x] Product Backlog populated with 20 User Stories mapped to SRS FRs and NFRs.
- [x] Story Points assigned to every backlog item using Fibonacci scale ($1$ to $8$).
- [x] Stories divided across Sprint 1 (37 SP) and Sprint 2 (22 SP).
- [x] Work distributed across all 4 team members with clear ownership.
- [x] Scripts for 1-minute and 2-minute video demonstrations prepared.
- [x] Deviations log initialized and justified.
