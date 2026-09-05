# 🧑‍🤝‍🧑 Team Guide — SRS Review & Git Workflow

## For: All 4 Team Members

This guide tells each member **exactly what to do** to review, edit, and push their SRS sections.

---

## 🔧 One-Time Setup (Everyone)

```bash
# 1. Clone the repo (if not already done)
git clone <your-repo-url>
cd Maxi

# 2. If already cloned, pull latest changes
git pull origin main
```

---

## 📂 File You Are Editing

```
docs/SRS.md    ← This is the ONLY file you edit
```

Open it in **VS Code**, **Notepad++**, or any text editor.

---

## ⚠️ Git Workflow (IMPORTANT — Avoid Conflicts)

Since all 4 members edit the **same file**, follow this workflow **every time**:

```bash
# Step 1: Pull latest changes BEFORE you start editing
git pull origin main

# Step 2: Make your edits in docs/SRS.md (your assigned sections ONLY)

# Step 3: Save the file

# Step 4: Stage and commit
git add docs/SRS.md
git commit -m "docs(SRS): <your-name> - <what you changed>"

# Step 5: Pull again (in case someone pushed while you were editing)
git pull origin main

# Step 6: If there's a merge conflict, resolve it, then:
git add docs/SRS.md
git commit -m "resolve merge conflict in SRS"

# Step 7: Push
git push origin main
```

### Example Commit Messages
```
git commit -m "docs(SRS): Ali - filled Introduction and Overall Description"
git commit -m "docs(SRS): Sara - reviewed functional requirements FR-006 to FR-009"
git commit -m "docs(SRS): Raza - added UML use case diagram images"
git commit -m "docs(SRS): Hina - refined security requirements and NFRs"
```

---

## 👥 Who Does What — Section Assignments

### 📌 Member 1 (Team Lead)

**Your Sections:** 1 (Introduction) + 2 (Overall Description) + Revision History + Final Review

**What to do:**

1. Open `docs/SRS.md`
2. Go to **line 7-11** → Replace `Team MiniMax` with your actual team name
3. Go to **line 17-23** (Revision History) → Fill in:
   - Replace `Member 1`, `Member 2`, etc. with **actual names**
   - Replace `DD-MM-2026` with **actual dates**
4. Review **Section 1 (Introduction)**:
   - 1.1 Purpose → Does it accurately describe your project? Edit if needed
   - 1.2 Scope → Check "In Scope" and "Out of Scope" lists — add/remove items
   - 1.3 Audience → Correct? Add your instructor's name if needed
   - 1.4 Definitions → Add any terms your team uses that are missing
5. Review **Section 2 (Overall Description)**:
   - 2.3 User Roles → Are these the right roles for your project? Edit names/descriptions
   - 2.4 Operating Environment → Confirm tech stack (Python version, browsers, etc.)
   - 2.5 Constraints → Add any constraints from your course (deadline, tools required, etc.)
   - 2.6 Assumptions → Add any assumptions specific to your team
6. **After all 4 members push** → Do a final read-through of the entire SRS for consistency

---

### 📌 Member 2

**Your Sections:** 4 (All Functional Requirements) + 8 (RTM — functional part)

**What to do:**

1. Open `docs/SRS.md`
2. Go to **Section 4** (starts around line 150)
3. Review each Functional Requirement (MM-F-001 to MM-F-017):
   - **Read each requirement** — Does it make sense for your project?
   - **Edit the wording** if something is unclear or too generic
   - **Add new FRs** if you think something is missing (use ID MM-F-018, MM-F-019, etc.)
   - **Remove any FR** that doesn't apply (but keep at least 15!)
   - **Check Acceptance Criteria** — Is each one testable? Can you write a test for it?
   - **Check Priority** — Is High/Medium correct for each?
4. Key FRs to pay special attention to:
   - MM-F-006 to MM-F-009 (extraction) → Are the keyword patterns realistic? Add more examples
   - MM-F-011 (PDF export) → Is this a must-have or nice-to-have for your team?
   - MM-F-012 (edit action items) → Is this achievable in your timeline?
5. Go to **Section 8 (RTM)** → Update the table if you added/removed any FRs
6. Commit and push

---

### 📌 Member 3

**Your Sections:** 3 (External Interfaces) + 7 (UML Use Case Diagrams)

**What to do:**

1. Open `docs/SRS.md`
2. Review **Section 3 (External Interface Requirements)**:
   - 3.1 User Interfaces → Check the page list — add/remove pages based on what your team will actually build
   - 3.2 Hardware Interfaces → Confirm "no specialized hardware" is correct
   - 3.3 Software Interfaces → Verify the tech stack matches what your team agreed on
   - 3.4 Communication Interfaces → Review and confirm
3. **Section 7 (UML Use Case Diagrams)** — This is your **main task**:
   - The current diagrams are **text-based placeholders**
   - You need to create **proper UML diagrams** using one of these tools:
     - [draw.io](https://app.diagrams.net/) (free, recommended)
     - StarUML
     - PlantUML
     - Lucidchart
   - Create **at least 2 Use Case Diagrams**:
     - **Diagram 1:** Core workflow (Upload → Transcribe → Extract → Generate → Export)
     - **Diagram 2:** User management (Register, Login, View History, Search)
   - Export diagrams as **PNG images**
   - Save them in `docs/diagrams/` folder:
     ```bash
     mkdir docs/diagrams
     # Save your diagrams there as:
     # docs/diagrams/usecase_core_workflow.png
     # docs/diagrams/usecase_user_management.png
     ```
   - Update Section 7 in the SRS to reference the images:
     ```markdown
     ![Use Case Diagram 1 - Core Workflow](diagrams/usecase_core_workflow.png)
     ```
4. Review the **Use Case Descriptions table** — edit actors, flows, pre/postconditions
5. Commit and push (including the image files!)

---

### 📌 Member 4

**Your Sections:** 5 (Non-Functional + Security) + 6 (Quality & Acceptance)

**What to do:**

1. Open `docs/SRS.md`
2. Review **Section 5 (Non-Functional Requirements)**:
   - MM-NF-001 → Is "60 seconds for 30-min audio" realistic for your stub? Adjust if needed
   - MM-NF-002 → Confirm browser support list
   - MM-NF-003 → "10 concurrent users" — is this realistic for a course project? Maybe reduce to 5
   - MM-NF-004 → Password hashing — confirm your team will use bcrypt
   - MM-NF-005 → "99% uptime" — realistic for a demo? Maybe change to "available during demo"
   - MM-NF-006 → Logging — confirm this is needed
   - **Add more NFRs** if needed (use MM-NF-007, MM-NF-008, etc.)
3. Review **Section 5.1.1 (Security Objectives)**:
   - Are both objectives clear and relevant?
   - Add a third objective if your instructor expects more
4. Review **Section 5.1.2 (Security Requirements)**:
   - MM-SR-001 to MM-SR-006 → Read each one, verify it's achievable
   - **You need at least 5** — we have 6, so you're safe
   - Edit wording to be more specific if needed
5. Review **Section 6 (Quality & Acceptance)**:
   - 6.1 Exit Criteria → Add any criteria your instructor expects
   - 6.2 Acceptance Test Suites → Verify all test suites make sense
6. Go to **Section 8 (RTM)** → Verify your NFR and SR rows are correct
7. Commit and push

---

## 📅 Timeline

| Day | Action |
|---|---|
| **Day 1** | Everyone pulls repo, reads full SRS, understands their sections |
| **Day 2-3** | Each member edits their assigned sections |
| **Day 3** | Member 3 creates UML diagrams |
| **Day 4** | Everyone pushes their changes |
| **Day 5** | **Member 1 (Lead)** does final review, fixes inconsistencies, commits final version |
| **Day 5** | Team meeting to approve SRS → Move to Phase 2 (SAD) |

---

## ✅ Checklist Before Pushing

Every member should verify before pushing:

- [ ] I only edited MY assigned sections
- [ ] I did `git pull` before starting
- [ ] My commit message clearly says what I changed
- [ ] I did `git pull` again before pushing
- [ ] I resolved any merge conflicts (if any)
- [ ] The file still renders correctly in a Markdown viewer

---

## 🆘 If Something Goes Wrong

```bash
# See what you changed
git diff docs/SRS.md

# Undo ALL your changes (before committing)
git checkout docs/SRS.md

# See commit history
git log --oneline -10

# If you accidentally broke something, reset to last commit
git reset --hard HEAD
```
