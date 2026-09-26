# Software Architecture and Design Specification (SAD)

## Automated Meeting Minutes Generator

| Field | Details |
|---|---|
| **Project** | Automated Meeting Minutes Generator (MiniMax) |
| **Version** | 1.0 |
| **Date** | September 2026 |
| **Authors** | Mohammed Faizan, Kamal Kanth N, Vinay M Rampur, Anagha Kaushik |
| **Status** | Draft |

---

### Team Members & SRN

| Name | SRN | Role |
|---|---|---|
| **Mohammed Faizan** | PES1UG24AM472 | Team Lead / Backend |
| **Kamal Kanth N** | PES1UG24AM434 | Backend Developer |
| **Vinay M Rampur** | PES1UG24AM455 | Frontend Developer |
| **Anagha Kaushik** | PES1UG24AM459 | Testing & Documentation |

### Revision History

| Version | Date | Author | Change Summary |
|---|---|---|---|
| 0.1 | DD-MM-2026 | Mohammed Faizan | Architecture and component design |
| 0.2 | DD-MM-2026 | Kamal Kanth N | API design and sequence diagrams |
| 0.3 | DD-MM-2026 | Vinay M Rampur | UX design and wireframes |
| 0.4 | DD-MM-2026 | Anagha Kaushik | Security architecture, DB design, error handling |
| 1.0 | DD-MM-2026 | All | Final reviewed version |

### Approvals

| Role | Name | Signature / Email | Date |
|---|---|---|---|
| Course Coordinator | | | |

---

## Table of Contents

1. Introduction
2. Document Overview
3. Architecture
4. Design
5. Appendices

---

## 1. Introduction

### 1.1 Purpose

This document specifies the software architecture and detailed design of the Automated Meeting Minutes Generator system. It translates the requirements defined in the SRS (v1.0) into a concrete technical blueprint that developers can follow to implement the system.

### 1.2 Scope

This document covers the architecture and design of the complete Meeting Minutes Generator system, including:

- The web-based frontend for audio upload, minutes viewing, and history browsing
- The backend REST API server
- The processing pipeline (Transcription stub, Text Extraction, Document Generation)
- The data persistence layer (SQLite database)
- Security architecture and threat modeling

### 1.3 Audience

- **Developers** — to understand the system architecture and implement modules
- **QA Engineers** — to understand component boundaries for test planning
- **Security Auditors** — to review the threat model and security controls
- **Course Instructors** — to evaluate design quality and SE process adherence
- **Maintenance Teams** — to understand the system for future modifications

### 1.4 Definitions

| Term | Definition |
|---|---|
| SAD | Software Architecture and Design Document |
| SRS | Software Requirements Specification |
| STP | Software Test Plan |
| RTM | Requirements Traceability Matrix |
| REST | Representational State Transfer |
| API | Application Programming Interface |
| ORM | Object-Relational Mapping |
| STRIDE | Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege |
| ADR | Architecture Decision Record |
| CRUD | Create, Read, Update, Delete |
| JWT | JSON Web Token |
| CORS | Cross-Origin Resource Sharing |

---

## 2. Document Overview

### 2.1 How to Use This Document

This document provides architectural deliverables including:

- **Section 3 (Architecture):** High-level system architecture, component diagrams, technology choices, security threat model, and traceability to SRS requirements.
- **Section 4 (Design):** Detailed module design with UML sequence diagrams, REST API specifications, database schema, error handling strategy, and UX wireframes.

Read Section 3 first for the big picture, then Section 4 for implementation details.

### 2.2 Related Documents

| Document | Version | Description |
|---|---|---|
| SRS | v1.0 | Software Requirements Specification — defines what the system must do |
| STP | v1.0 (pending) | Software Test Plan — defines how the system will be tested |
| RTM | v1.0 | Requirements Traceability Matrix — maps requirements to modules and tests |

---

## 3. Architecture

### 3.1 Goals & Constraints

**Goals:**

- **Modularity** — Each processing stage (transcription, extraction, generation) is an independent module that can be developed, tested, and replaced independently
- **Extensibility** — The stub transcription module can be swapped for a real ASR engine (e.g., Whisper API) without changing the rest of the pipeline
- **Simplicity** — Use straightforward, well-documented technologies suitable for a team of 4 developers
- **Security** — Protect user credentials and ensure data isolation between users

**Constraints:**

- Transcription is a **stub** — no real speech recognition
- Must use **open-source** libraries only
- Single-tenant deployment (one team/organization)
- Audio file size limited to **100 MB**
- Must run on standard hardware (no GPU required)

### 3.2 Stakeholders & Concerns

| Stakeholder | Concerns |
|---|---|
| **Users (Meeting Organizer)** | Fast processing, intuitive UI, accurate extraction, reliable PDF export |
| **Developers** | Clean module boundaries, simple APIs, easy debugging |
| **Course Instructor** | Proper SE process, clear architecture documentation, adherence to design patterns |
| **QA Team** | Testable components, clear interfaces, reproducible results |

### 3.3 Component (UML) Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                    │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │  Upload Page │  │Minutes Viewer│  │ History Page   │  │
│  └──────┬──────┘  └──────┬───────┘  └───────┬───────┘  │
│         │                │                   │          │
└─────────┼────────────────┼───────────────────┼──────────┘
          │      HTTP/JSON │                   │
┌─────────┼────────────────┼───────────────────┼──────────┐
│         ▼                ▼                   ▼          │
│                    API LAYER                             │
│  ┌──────────────────────────────────────────────────┐   │
│  │              Flask/FastAPI Server                  │   │
│  │  ┌──────────┐  ┌──────────┐  ┌────────────────┐  │   │
│  │  │ /upload  │  │ /minutes │  │ /auth          │  │   │
│  │  │ /process │  │ /history │  │ /register      │  │   │
│  │  │          │  │ /search  │  │ /login         │  │   │
│  │  └────┬─────┘  └────┬─────┘  └────────────────┘  │   │
│  └───────┼──────────────┼────────────────────────────┘   │
└──────────┼──────────────┼────────────────────────────────┘
           │              │
┌──────────┼──────────────┼────────────────────────────────┐
│          ▼              │      PROCESSING LAYER          │
│  ┌───────────────┐      │                                │
│  │ Transcription │      │                                │
│  │ Module (Stub) │      │                                │
│  └───────┬───────┘      │                                │
│          ▼              │                                │
│  ┌───────────────┐      │                                │
│  │ Text          │      │                                │
│  │ Preprocessor  │      │                                │
│  └───────┬───────┘      │                                │
│          ▼              │                                │
│  ┌───────────────┐      │                                │
│  │ Extractor     │      │                                │
│  │ Module        │      │                                │
│  └───────┬───────┘      │                                │
│          ▼              │                                │
│  ┌───────────────┐      │                                │
│  │ Document      │◄─────┘                                │
│  │ Generator     │                                       │
│  └───────┬───────┘                                       │
└──────────┼───────────────────────────────────────────────┘
           │
┌──────────┼───────────────────────────────────────────────┐
│          ▼           DATA LAYER                          │
│  ┌───────────────┐  ┌───────────────┐                    │
│  │ SQLite DB     │  │ File System   │                    │
│  │ (Users,       │  │ (Audio files, │                    │
│  │  Meetings,    │  │  Generated    │                    │
│  │  Minutes)     │  │  PDFs)        │                    │
│  └───────────────┘  └───────────────┘                    │
└──────────────────────────────────────────────────────────┘
```

> **Note:** This text diagram should be replaced with a proper UML component diagram created in draw.io or similar tool.

### 3.4 Component Descriptions

| Component | Responsibility | Key Classes/Modules |
|---|---|---|
| **Upload Page** | Audio file selection, meeting metadata input, upload trigger | `UploadForm`, `FileValidator` (frontend) |
| **Minutes Viewer** | Display generated minutes, allow action item editing, trigger PDF export | `MinutesDisplay`, `ActionItemEditor` (frontend) |
| **History Page** | List past meetings, provide search/filter, navigate to minutes | `MeetingList`, `SearchBar` (frontend) |
| **Flask/FastAPI Server** | Route HTTP requests, orchestrate pipeline, return responses | `app.py`, route handlers |
| **Auth Module** | User registration, login, session management, password hashing | `auth.py`, `User` model |
| **Transcription Module (Stub)** | Accept audio file reference, return simulated transcript text | `transcriber.py`, `StubTranscriber` class |
| **Text Preprocessor** | Normalize transcript (whitespace, case, line breaks) for extraction | `preprocessor.py`, `TextNormalizer` class |
| **Extractor Module** | Parse transcript using keyword patterns/regex to extract action items, deadlines, assignees, decisions, discussion points | `extractor.py`, `ActionItemExtractor`, `DeadlineParser`, `AssigneeExtractor`, `DecisionExtractor` |
| **Document Generator** | Assemble extracted data into Markdown using Jinja2 templates, convert to PDF | `generator.py`, `MinutesTemplate`, `PDFExporter` |
| **SQLite Database** | Store users, meetings, minutes, action items | `models.py`, SQLAlchemy ORM |
| **File System** | Store uploaded audio files and generated PDF outputs | `storage.py`, UUID-based file naming |

### 3.5 Chosen Architecture Pattern and Rationale

**Pattern: Layered Architecture (4 layers)**

| Layer | Components | Responsibility |
|---|---|---|
| **Presentation** | React / HTML+CSS+JS frontend | User interaction, display |
| **API** | Flask/FastAPI REST server | Request routing, validation, response formatting |
| **Processing** | Transcription, Preprocessor, Extractor, Generator | Business logic, data transformation |
| **Data** | SQLite + File System | Persistence, storage |

**Why Layered Architecture?**

- **Separation of concerns** — Each layer has a clear responsibility; changes in one layer don't ripple through others
- **Testability** — Each layer can be unit tested independently
- **Simplicity** — Easy to understand and implement for a team of 4
- **Matches the pipeline nature** — The processing flow (transcribe → preprocess → extract → generate) maps naturally to sequential layers

**Alternatives Considered and Rejected:**

| Pattern | Reason for Rejection |
|---|---|
| Microservices | Overly complex for a 4-person team project; adds deployment overhead |
| Event-driven | Unnecessary for synchronous request-response processing |
| Monolithic (no layers) | Would create tightly coupled code that's hard to test and maintain |

### 3.6 Technology Stack & Data Stores

| Layer | Technology | Justification |
|---|---|---|
| **Frontend** | HTML + CSS + JavaScript (or React) | Simple, widely known, sufficient for the UI needs |
| **Backend Framework** | Python Flask / FastAPI | Lightweight, excellent for REST APIs, large ecosystem |
| **Transcription** | Custom stub module | Returns pre-defined text; swappable for Whisper API later |
| **Text Processing** | Python `re` (regex) + spaCy (optional) | Powerful pattern matching for keyword extraction |
| **Template Engine** | Jinja2 | Industry-standard Python templating for generating Markdown |
| **PDF Generation** | WeasyPrint | Converts HTML/CSS to PDF; open-source and reliable |
| **ORM** | SQLAlchemy | Pythonic database abstraction; supports SQLite and PostgreSQL |
| **Database** | SQLite | Zero-configuration, file-based; perfect for development and demo |
| **Password Hashing** | bcrypt | Industry-standard secure hashing algorithm |
| **Authentication** | Flask-Login / JWT | Session management with secure token-based auth |

### 3.7 Risks & Mitigations

| # | Risk | Impact | Probability | Mitigation |
|---|---|---|---|---|
| R1 | Stub transcription produces unrealistic text | Low quality demo | Medium | Prepare realistic pre-written transcripts from actual meeting scenarios |
| R2 | Keyword extraction misses action items or produces false positives | Inaccurate minutes | High | Allow users to edit extracted items (MM-F-012); refine keyword patterns iteratively |
| R3 | PDF generation fails for complex Markdown content | Feature unavailable | Low | Use simple, well-tested HTML templates; add fallback Markdown download |
| R4 | Team member unavailable during critical phase | Schedule delay | Medium | Cross-train on modules; document all code with docstrings |
| R5 | Merge conflicts due to all members editing same files | Lost work | Medium | Clear module ownership; frequent small commits; branch-per-feature workflow |
| R6 | Large audio file uploads cause server timeout | Poor user experience | Low | Enforce 100 MB limit (MM-F-003); chunked upload if needed |

### 3.8 Traceability to Requirements

| SRS Requirement | Design Component | SAD Section |
|---|---|---|
| MM-F-001, MM-F-002, MM-F-003 (Upload & Validation) | Upload Page + `/upload` API + `FileValidator` | 3.4, 4.3 |
| MM-F-004, MM-F-005 (Transcription) | Transcription Module (Stub) | 3.4, 4.2 |
| MM-F-018 (Text Preprocessing) | Text Preprocessor | 3.4 |
| MM-F-006 to MM-F-009, MM-F-019, MM-F-020 (Extraction) | Extractor Module | 3.4, 4.2 |
| MM-F-010, MM-F-011 (Document Generation & PDF) | Document Generator | 3.4, 4.2 |
| MM-F-012 (Edit Action Items) | Minutes Viewer + `/minutes` API | 3.4, 4.3 |
| MM-F-013, MM-F-014, MM-F-015 (History & Search) | History Page + `/history`, `/search` API + SQLite | 3.4, 4.3 |
| MM-F-016, MM-F-017 (Auth & Meeting Setup) | Auth Module + `/auth` API | 3.4, 4.3 |
| MM-SR-001 to MM-SR-006 (Security) | Security Architecture (STRIDE) | 3.9 |
| MM-NF-001 to MM-NF-006 (Non-Functional) | Architecture decisions, tech stack | 3.5, 3.6 |

### 3.9 Security Architecture

#### Threat Modeling (STRIDE)

| Threat Category | Threat Description | Affected Component | Mitigation | SRS Req |
|---|---|---|---|---|
| **Spoofing** | Attacker impersonates a legitimate user by stealing session token | Auth Module | Use secure HTTP-only cookies; implement session timeout (30 min); use bcrypt for password hashing | MM-SR-002, MM-SR-003 |
| **Tampering** | Attacker modifies uploaded audio file or meeting data in transit | API Layer, File System | Enforce HTTPS/TLS 1.2+ for all communication; validate file integrity on server | MM-SR-001 |
| **Repudiation** | User denies uploading a file or modifying minutes | API Layer | Maintain timestamped audit logs for all uploads, edits, and deletions | MM-NF-006 |
| **Information Disclosure** | Unauthorized user accesses another user's meeting minutes or audio files | Data Layer, API Layer | Enforce user-based access control on all API endpoints; store files with UUID names (no guessable paths) | MM-SR-006 |
| **Denial of Service** | Attacker uploads extremely large files to exhaust server resources | Upload API | Enforce 100 MB file size limit; restrict allowed MIME types; rate limiting on upload endpoint | MM-F-003, MM-SR-005 |
| **Elevation of Privilege** | Attacker exploits input fields to execute SQL injection or XSS | API Layer, Database | Validate and sanitize all inputs server-side; use parameterized queries via ORM; escape output in templates | MM-SR-004 |

#### Security Controls Summary

| Control | Implementation |
|---|---|
| **Authentication** | bcrypt password hashing (cost factor ≥10), secure session management |
| **Authorization** | User-based access control — users can only access their own meetings |
| **Transport Security** | HTTPS with TLS 1.2+ in production |
| **Input Validation** | Server-side validation of all inputs; MIME type checking for uploads |
| **File Security** | UUID-based filenames; files stored outside web root |
| **Session Security** | HTTP-only cookies; 30-minute inactivity timeout |
| **Logging** | Timestamped logs for all critical operations; no sensitive data in logs |

---

## 4. Design

### 4.1 Design Overview

The system follows a sequential processing pipeline triggered by user action:

1. User uploads audio file + meeting metadata via the web UI
2. Backend validates and stores the file
3. Transcription module (stub) generates text from audio
4. Preprocessor normalizes the text
5. Extractor module identifies action items, deadlines, assignees, decisions, and discussion points
6. Document generator assembles a structured Markdown minutes document
7. User can view, edit action items, and export as PDF

### 4.2 UML Sequence Diagrams

#### Sequence Diagram 1 — Upload, Process, and Generate Minutes

```
User          Frontend       Backend API    Transcriber    Preprocessor    Extractor    Generator    Database    FileSystem
 │                │               │              │              │              │            │            │            │
 │─── Select ────►│               │              │              │              │            │            │            │
 │    Audio File  │               │              │              │              │            │            │            │
 │─── Enter ─────►│               │              │              │              │            │            │            │
 │    Metadata    │               │              │              │              │            │            │            │
 │─── Click ─────►│               │              │              │              │            │            │            │
 │    Upload      │               │              │              │              │            │            │            │
 │                │── POST ──────►│              │              │              │            │            │            │
 │                │   /upload     │              │              │              │            │            │            │
 │                │               │── Validate ─►│              │              │            │            │            │
 │                │               │   File       │              │              │            │            │            │
 │                │               │──────────────────────────────────────────────────────────────────────►│            │
 │                │               │              │              │              │            │   Save     │            │
 │                │               │              │              │              │            │   Audio    │            │
 │                │               │── Transcribe─►│              │              │            │            │            │
 │                │               │              │── Return ───►│              │            │            │            │
 │                │               │              │   Transcript │              │            │            │            │
 │                │               │              │              │── Normalize─►│            │            │            │
 │                │               │              │              │   Text       │            │            │            │
 │                │               │              │              │              │── Extract─►│            │            │
 │                │               │              │              │              │  Items     │            │            │
 │                │               │              │              │              │            │── Generate │            │
 │                │               │              │              │              │            │   Markdown │            │
 │                │               │──────────────────────────────────────────────────────────►│            │            │
 │                │               │              │              │              │            │  Save      │            │
 │                │               │              │              │              │            │  Meeting   │            │
 │                │◄── 200 OK ────│              │              │              │            │            │            │
 │                │   {minutes}   │              │              │              │            │            │            │
 │◄── Display ────│               │              │              │              │            │            │            │
 │    Minutes     │               │              │              │              │            │            │            │
```

> **Note:** Replace this text diagram with a proper UML sequence diagram created in draw.io, PlantUML, or similar tool.

#### Sequence Diagram 2 — View History and Export PDF

```
User          Frontend       Backend API    Database    Generator    FileSystem
 │                │               │              │            │            │
 │─── Click ─────►│               │              │            │            │
 │    History     │               │              │            │            │
 │                │── GET ───────►│              │            │            │
 │                │   /history    │              │            │            │
 │                │               │── Query ────►│            │            │
 │                │               │   Meetings   │            │            │
 │                │               │◄── Results ──│            │            │
 │                │◄── 200 OK ────│              │            │            │
 │                │   [meetings]  │              │            │            │
 │◄── Display ────│               │              │            │            │
 │    Meeting List│               │              │            │            │
 │                │               │              │            │            │
 │─── Select ────►│               │              │            │            │
 │    Meeting     │               │              │            │            │
 │                │── GET ───────►│              │            │            │
 │                │  /minutes/:id │              │            │            │
 │                │               │── Query ────►│            │            │
 │                │               │◄── Minutes ──│            │            │
 │                │◄── 200 OK ────│              │            │            │
 │◄── Display ────│               │              │            │            │
 │    Minutes     │               │              │            │            │
 │                │               │              │            │            │
 │─── Click ─────►│               │              │            │            │
 │    Export PDF  │               │              │            │            │
 │                │── GET ───────►│              │            │            │
 │                │  /minutes/    │              │            │            │
 │                │   :id/pdf     │              │            │            │
 │                │               │──────────────────────────►│            │
 │                │               │              │  Generate  │            │
 │                │               │              │  PDF       │            │
 │                │               │              │            │── Save ───►│
 │                │               │              │            │   PDF      │
 │                │◄── 200 OK ────│              │            │            │
 │                │   {pdf_url}   │              │            │            │
 │◄── Download ───│               │              │            │            │
 │    PDF         │               │              │            │            │
```

> **Note:** Replace this text diagram with a proper UML sequence diagram.

### 4.3 API Design

#### Authentication Endpoints

| Endpoint | Method | Request Body | Response | Description |
|---|---|---|---|---|
| `/api/auth/register` | POST | `{ "email": "...", "password": "..." }` | `201 { "message": "User created", "user_id": "..." }` | Register new user |
| `/api/auth/login` | POST | `{ "email": "...", "password": "..." }` | `200 { "token": "...", "user_id": "..." }` | Login and receive session token |
| `/api/auth/logout` | POST | (none — token in header) | `200 { "message": "Logged out" }` | End session |

#### Upload & Processing Endpoints

| Endpoint | Method | Request | Response | Description |
|---|---|---|---|---|
| `/api/upload` | POST | `multipart/form-data: file, title, date, participants` | `202 { "meeting_id": "...", "status": "processing" }` | Upload audio and start processing |
| `/api/meetings/{id}/status` | GET | — | `200 { "status": "processing" / "complete" / "error" }` | Check processing status |

#### Minutes Endpoints

| Endpoint | Method | Request | Response | Description |
|---|---|---|---|---|
| `/api/minutes/{id}` | GET | — | `200 { "meeting": {...}, "minutes": {...}, "action_items": [...] }` | Get generated minutes |
| `/api/minutes/{id}/actions` | PUT | `{ "action_items": [...] }` | `200 { "message": "Updated" }` | Edit action items |
| `/api/minutes/{id}/pdf` | GET | — | `200 (binary PDF)` | Download PDF export |

#### History & Search Endpoints

| Endpoint | Method | Request | Response | Description |
|---|---|---|---|---|
| `/api/history` | GET | Query: `?page=1&limit=10` | `200 { "meetings": [...], "total": N }` | List past meetings (paginated) |
| `/api/search` | GET | Query: `?q=keyword&from=date&to=date` | `200 { "results": [...] }` | Search past minutes |

#### Error Response Format

All error responses follow a standard format:

```json
{
  "error": {
    "code": 400,
    "type": "VALIDATION_ERROR",
    "message": "File size exceeds 100 MB limit",
    "field": "file"
  }
}
```

| HTTP Code | Type | When Used |
|---|---|---|
| 400 | VALIDATION_ERROR | Invalid input, unsupported file format, file too large |
| 401 | AUTHENTICATION_ERROR | Missing or invalid credentials / session expired |
| 403 | AUTHORIZATION_ERROR | User trying to access another user's data |
| 404 | NOT_FOUND | Meeting or minutes not found |
| 500 | INTERNAL_ERROR | Unexpected server error |

### 4.4 Error Handling, Logging & Monitoring

#### Error Handling Strategy

| Layer | Strategy |
|---|---|
| **Frontend** | Display user-friendly error messages; show form validation errors inline; show toast notifications for server errors |
| **API Layer** | Return standardized JSON error responses (see above); catch all exceptions with a global error handler; never expose stack traces to clients |
| **Processing Layer** | Each pipeline module catches its own exceptions and returns a structured error result; pipeline coordinator handles partial failures gracefully |
| **Data Layer** | ORM handles connection errors with retry logic; database constraint violations return meaningful errors |

#### Logging Strategy

| Log Level | Usage | Example |
|---|---|---|
| **INFO** | Successful operations | `[INFO] 2026-09-25T10:30:00Z - User user@email.com uploaded meeting "Sprint Review" (meeting_id: abc-123)` |
| **WARNING** | Recoverable issues | `[WARN] 2026-09-25T10:30:05Z - No action items extracted for meeting abc-123` |
| **ERROR** | Failures | `[ERROR] 2026-09-25T10:30:10Z - PDF generation failed for meeting abc-123: WeasyPrint timeout` |

**Logging Rules:**
- All logs include ISO 8601 timestamps (MM-NF-006)
- No sensitive data (passwords, tokens) in logs
- Log file rotation: daily, retain 30 days
- Structured format: `[LEVEL] TIMESTAMP - MESSAGE (context)`

#### Monitoring

| Metric | Measurement |
|---|---|
| Processing time per meeting | Tracked in logs; alert if >60s (MM-NF-001) |
| Upload failure rate | Count of 4xx responses on `/upload` |
| Active user sessions | Count of valid sessions |

### 4.5 UX Design

#### Page Wireframes

**Home Page (Upload)**

```
┌──────────────────────────────────────────────────┐
│  [Logo] Meeting Minutes Generator    [History] [Logout] │
├──────────────────────────────────────────────────┤
│                                                  │
│         ┌──────────────────────────┐             │
│         │                          │             │
│         │   📁 Drag & Drop Audio   │             │
│         │      or Click to Browse  │             │
│         │                          │             │
│         │   Supported: MP3, WAV,   │             │
│         │   M4A (max 100 MB)       │             │
│         └──────────────────────────┘             │
│                                                  │
│  Meeting Title:  [________________________]      │
│  Date:           [____/____/________]            │
│  Participants:   [________________________]      │
│                                                  │
│              [ Upload & Process ]                │
│                                                  │
└──────────────────────────────────────────────────┘
```

**Minutes Viewer**

```
┌──────────────────────────────────────────────────┐
│  [Logo] Meeting Minutes Generator    [History] [Logout] │
├──────────────────────────────────────────────────┤
│                                                  │
│  📄 Sprint Review Meeting                        │
│  Date: 25-Sep-2026  |  Participants: A, B, C     │
│                                                  │
│  ── Summary ─────────────────────────────────    │
│  Discussion about project status and next steps. │
│                                                  │
│  ── Discussion Points ───────────────────────    │
│  • Backend API progress update                   │
│  • Frontend UI review                            │
│                                                  │
│  ── Decisions ───────────────────────────────    │
│  ✓ Agreed to use Flask for backend               │
│                                                  │
│  ── Action Items ────────────────────────────    │
│  ┌────────────────────────────────────────────┐  │
│  │ Task          │ Assignee │ Deadline │ [Edit]│  │
│  │ Fix login bug │ Faizan   │ 30-Sep   │ [Edit]│  │
│  │ Add search    │ Vinay    │ 02-Oct   │ [Edit]│  │
│  └────────────────────────────────────────────┘  │
│                                                  │
│        [ Export as PDF ]   [ Back to History ]    │
│                                                  │
└──────────────────────────────────────────────────┘
```

**History Page**

```
┌──────────────────────────────────────────────────┐
│  [Logo] Meeting Minutes Generator    [History] [Logout] │
├──────────────────────────────────────────────────┤
│                                                  │
│  🔍 Search: [_______________] [From: ___] [To: ___] [Search] │
│                                                  │
│  ── Past Meetings ───────────────────────────    │
│  ┌────────────────────────────────────────────┐  │
│  │ Title              │ Date       │ Actions  │  │
│  │ Sprint Review      │ 25-Sep-2026│ [View]   │  │
│  │ Planning Meeting   │ 20-Sep-2026│ [View]   │  │
│  │ Design Discussion  │ 15-Sep-2026│ [View]   │  │
│  └────────────────────────────────────────────┘  │
│                                                  │
│           [ ← Previous ]  [ Next → ]             │
│                                                  │
└──────────────────────────────────────────────────┘
```

> **Note:** Replace these ASCII wireframes with proper UI mockups created in Figma, draw.io, or similar tool.

### 4.6 Database Design

#### Entity-Relationship Diagram

```
┌───────────────┐       1:N       ┌───────────────────┐
│     User      │────────────────►│     Meeting       │
├───────────────┤                 ├───────────────────┤
│ id (PK)       │                 │ id (PK)           │
│ email         │                 │ user_id (FK)      │
│ password_hash │                 │ title             │
│ created_at    │                 │ meeting_date      │
└───────────────┘                 │ participants      │
                                  │ audio_filename    │
                                  │ transcript        │
                                  │ minutes_markdown  │
                                  │ status            │
                                  │ created_at        │
                                  │ updated_at        │
                                  └────────┬──────────┘
                                           │
                                           │ 1:N
                                           ▼
                                  ┌───────────────────┐
                                  │   ActionItem      │
                                  ├───────────────────┤
                                  │ id (PK)           │
                                  │ meeting_id (FK)   │
                                  │ description       │
                                  │ assignee          │
                                  │ deadline          │
                                  │ status            │
                                  │ created_at        │
                                  └───────────────────┘
```

#### Table Schemas

**users**

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique user ID |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User email address |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt hashed password |
| created_at | DATETIME | NOT NULL, DEFAULT NOW | Account creation timestamp |

**meetings**

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique meeting ID |
| user_id | INTEGER | FOREIGN KEY → users.id, NOT NULL | Owner of the meeting |
| title | VARCHAR(255) | NOT NULL | Meeting title |
| meeting_date | DATE | NOT NULL | Date of the meeting |
| participants | TEXT | NULLABLE | Comma-separated participant names |
| audio_filename | VARCHAR(255) | NOT NULL | UUID-based stored filename |
| transcript | TEXT | NULLABLE | Full transcribed text |
| minutes_markdown | TEXT | NULLABLE | Generated Markdown minutes |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'uploaded' | processing / complete / error |
| created_at | DATETIME | NOT NULL, DEFAULT NOW | Record creation timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT NOW | Last modification timestamp |

**action_items**

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique action item ID |
| meeting_id | INTEGER | FOREIGN KEY → meetings.id, NOT NULL | Parent meeting |
| description | TEXT | NOT NULL | Action item text |
| assignee | VARCHAR(100) | NULLABLE, DEFAULT 'Unassigned' | Person responsible |
| deadline | DATE | NULLABLE | Due date |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | pending / done |
| created_at | DATETIME | NOT NULL, DEFAULT NOW | Record creation timestamp |

### 4.7 Open Issues & Next Steps

| # | Issue | Status | Owner |
|---|---|---|---|
| 1 | Finalize frontend technology choice (React vs plain HTML/CSS/JS) | Open | Vinay M Rampur |
| 2 | Define realistic stub transcription sample texts for demo | Open | Mohammed Faizan |
| 3 | Determine if spaCy is needed or regex alone is sufficient for extraction | Open | Kamal Kanth N |
| 4 | Create proper UML diagrams (component, sequence) to replace text diagrams | Open | Anagha Kaushik |

---

## 5. Appendices

### 5.1 Glossary

See Section 1.4 (Definitions).

### 5.2 References

| Reference | Description |
|---|---|
| IEEE 42010:2011 | Systems and software engineering — Architecture description |
| OWASP Top 10 | Web application security risks |
| STRIDE | Microsoft threat modeling methodology |
| Flask Documentation | https://flask.palletsprojects.com/ |
| SQLAlchemy Documentation | https://docs.sqlalchemy.org/ |
| WeasyPrint Documentation | https://weasyprint.org/ |

### 5.3 Tools

| Tool | Usage |
|---|---|
| draw.io / diagrams.net | UML component, sequence, and ER diagrams |
| Figma / draw.io | UI wireframes and mockups |
| PlantUML | Alternative UML diagram generation |
| Swagger / OpenAPI | API documentation (optional) |
| Git & GitHub | Version control and collaboration |

---

*End of SAD Document — Version 1.0*
