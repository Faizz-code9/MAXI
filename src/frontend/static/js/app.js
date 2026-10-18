/**
 * MiniMax — Automated Meeting Minutes Generator Frontend Logic
 * Owner: Kamal Kanth N (PES1UG24AM434)
 * Phase: 3 - Implementation Sprint 1
 */

document.addEventListener("DOMContentLoaded", () => {
  // Navigation elements
  const navButtons = document.querySelectorAll(".nav-btn");
  const tabContents = document.querySelectorAll(".tab-content");
  const navViewer = document.getElementById("nav-viewer");
  const navHistory = document.getElementById("nav-history");

  // Form & Dropzone elements
  const uploadForm = document.getElementById("upload-form");
  const dropzone = document.getElementById("dropzone");
  const audioInput = document.getElementById("audio-input");
  const fileInfo = document.getElementById("file-info");
  const fileName = document.getElementById("file-name");
  const removeFileBtn = document.getElementById("remove-file");
  const meetingTitleInput = document.getElementById("meeting-title");
  const meetingDeptInput = document.getElementById("meeting-dept");
  const meetingDateInput = document.getElementById("meeting-date");
  const progressContainer = document.getElementById("upload-progress-container");
  const progressFill = document.getElementById("progress-fill");
  const progressPercent = document.getElementById("progress-percent");
  const submitBtn = document.getElementById("submit-btn");

  // Viewer elements
  const viewTitle = document.getElementById("view-title");
  const viewDate = document.getElementById("view-date");
  const viewDuration = document.getElementById("view-duration");
  const viewAttendees = document.getElementById("view-attendees");
  const viewSummary = document.getElementById("view-summary");
  const viewDecisions = document.getElementById("view-decisions");
  const viewActionItems = document.getElementById("view-action-items");
  const viewTranscript = document.getElementById("view-transcript");
  const btnExportMd = document.getElementById("btn-export-md");
  const btnExportPdf = document.getElementById("btn-export-pdf");
  const btnCopyClip = document.getElementById("btn-copy-clip");

  // History elements
  const historyList = document.getElementById("history-list");
  const historySearch = document.getElementById("history-search");
  const historyNoResults = document.getElementById("history-no-results");

  let currentMeetingId = null;
  let currentMarkdownContent = "";
  let meetings = [];

  // Set today's date as default
  meetingDateInput.value = new Date().toISOString().split("T")[0];

  // ================= TAB SWITCHING =================
  navButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetTab = btn.getAttribute("data-tab");
      switchTab(targetTab);
    });
  });

  function switchTab(tabId) {
    navButtons.forEach(b => b.classList.toggle("active", b.getAttribute("data-tab") === tabId));
    tabContents.forEach(tc => tc.classList.toggle("active", tc.id === tabId));

    if (tabId === "history-tab") {
      loadMeetingHistory();
    }
  }

  // ================= DRAG & DROP HANDLING =================
  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  });

  dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("dragover");
  });

  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
    if (e.dataTransfer.files.length > 0) {
      audioInput.files = e.dataTransfer.files;
      handleFileSelected();
    }
  });

  audioInput.addEventListener("change", handleFileSelected);

  function handleFileSelected() {
    if (audioInput.files.length > 0) {
      const file = audioInput.files[0];
      fileName.textContent = `Selected: ${file.name} (${(file.size / (1024 * 1024)).toFixed(1)} MB)`;
      fileInfo.classList.remove("hidden");
      if (!meetingTitleInput.value) {
        meetingTitleInput.value = file.name.replace(/\.[^/.]+$/, "");
      }
    }
  }

  removeFileBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    audioInput.value = "";
    fileInfo.classList.add("hidden");
  });

  // ================= FORM SUBMISSION & API UPLOAD =================
  uploadForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!audioInput.files.length) {
      alert("Please select or drop an audio file.");
      return;
    }

const file = audioInput.files[0];

// Check supported audio file types
const allowedExtensions = [".mp3", ".wav", ".m4a"];
const fileNameLower = file.name.toLowerCase();
const isAllowedType = allowedExtensions.some(ext => fileNameLower.endsWith(ext));

if (!isAllowedType) {
  alert("Unsupported file type. Please select an MP3, WAV, or M4A file.");
  audioInput.value = "";
  fileInfo.classList.add("hidden");
  return;
}

// Check maximum file size: 100 MB
const maxFileSize = 100 * 1024 * 1024;
if (file.size > maxFileSize) {
  alert("File is too large. Maximum allowed size is 100 MB.");
  audioInput.value = "";
  fileInfo.classList.add("hidden");
  return;
}

const formData = new FormData();
    formData.append("audio", file);
    formData.append("title", meetingTitleInput.value);
    formData.append("date", meetingDateInput.value);
    formData.append("department", meetingDeptInput.value);

    // Show Progress
    progressContainer.classList.remove("hidden");
    submitBtn.disabled = true;
    submitBtn.textContent = "Processing Pipeline...";
    simulateProgress();

    try {
      const res = await fetch("/api/upload", {
        method: "POST",
        body: formData
      });

      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.error || "Upload failed");
      }

      progressFill.style.width = "100%";
      progressPercent.textContent = "100%";

      setTimeout(() => {
        progressContainer.classList.add("hidden");
        submitBtn.disabled = false;
        submitBtn.textContent = "Generate Meeting Minutes";
        window.viewHistoricalMeeting(data.meeting_id);
      }, 500);

    } catch (err) {
      alert("Error: " + err.message);
      progressContainer.classList.add("hidden");
      submitBtn.disabled = false;
      submitBtn.textContent = "Generate Meeting Minutes";
    }
  });

  function simulateProgress() {
    let p = 15;
    progressFill.style.width = p + "%";
    progressPercent.textContent = p + "%";
    const interval = setInterval(() => {
      if (p < 85) {
        p += Math.floor(Math.random() * 15) + 5;
        if (p > 85) p = 85;
        progressFill.style.width = p + "%";
        progressPercent.textContent = p + "%";
      } else {
        clearInterval(interval);
      }
    }, 300);
  }

  // ================= DISPLAY MINUTES IN VIEWER =================
  function displayMinutes(data) {
    currentMeetingId = data.meeting_id;
    currentMarkdownContent = data.markdown || "";

    viewTitle.textContent = data.title;
    viewDate.textContent = "📅 " + data.date;
    viewDuration.textContent = "⏱️ " + (data.duration || "00:02:25");

    // Attendees
    viewAttendees.innerHTML = "";
    (data.attendees || []).forEach(att => {
      const pill = document.createElement("span");
      pill.className = "attendee-pill";
      pill.textContent = att;
      viewAttendees.appendChild(pill);
    });

    // Summary
    viewSummary.textContent = data.summary || "No summary provided.";

    // Decisions
    viewDecisions.innerHTML = "";
    if (data.decisions && data.decisions.length) {
      data.decisions.forEach(dec => {
        const li = document.createElement("li");
        li.textContent = dec;
        viewDecisions.appendChild(li);
      });
    } else {
      viewDecisions.innerHTML = "<li>No formal decisions recorded.</li>";
    }

    // Action Items
    viewActionItems.replaceChildren();
    if (data.action_items && data.action_items.length) {
      data.action_items.forEach((item, idx) => {
        const tr = document.createElement("tr");
        const numberCell = document.createElement("td");
        numberCell.textContent = String(idx + 1);
        const taskCell = document.createElement("td");
        taskCell.textContent = item.task || "";
        const assigneeCell = document.createElement("td");
        const assignee = document.createElement("strong");
        assignee.textContent = item.assignee || "Unassigned";
        assigneeCell.appendChild(assignee);
        const deadlineCell = document.createElement("td");
        const deadline = document.createElement("code");
        deadline.textContent = item.deadline || "TBD";
        deadlineCell.appendChild(deadline);
        const statusCell = document.createElement("td");
        const status = item.status === "Completed" ? "Completed" : "Pending";
        const statusButton = document.createElement("button");
        statusButton.type = "button";
        statusButton.className = `status-tag ${status === "Completed" ? "status-completed" : "status-pending"}`;
        statusButton.dataset.id = item.id || "";
        statusButton.dataset.status = status;
        statusButton.textContent = status;
        statusCell.appendChild(statusButton);
        tr.append(numberCell, taskCell, assigneeCell, deadlineCell, statusCell);
        viewActionItems.appendChild(tr);
      });
    } else {
      const row = document.createElement("tr");
      const cell = document.createElement("td");
      cell.colSpan = 5;
      cell.className = "empty-state-cell";
      cell.textContent = "No action items detected.";
      row.appendChild(cell);
      viewActionItems.appendChild(row);
    }

    // Transcript
    const transcript = data.raw_transcript || data.processed_transcript || "";
viewTranscript.textContent = transcript.trim()
  ? transcript
  : "No transcript is available for this meeting.";
  }
// ================= TOGGLE ACTION ITEM STATUS =================
viewActionItems.addEventListener("click", async (e) => {
  const btn = e.target.closest("button[data-id]");
  if (!btn || !btn.dataset.id) return;
  const newStatus = btn.dataset.status === "Completed" ? "Pending" : "Completed";
  try {
    const res = await fetch(`/api/action-items/${btn.dataset.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: newStatus })
    });
    const data = await res.json();
    if (data.success) {
      btn.dataset.status = newStatus;
      btn.textContent = newStatus;
      btn.className = "status-tag " + (newStatus === "Completed" ? "status-completed" : "status-pending");
    }
  } catch (err) {
    alert("Could not update status: " + err.message);
  }
});
  // ================= EXPORT ACTIONS =================
  btnExportMd.addEventListener("click", () => {
    if (!currentMeetingId) return;
    window.location.href = `/api/meetings/${currentMeetingId}/export`;
  });

  if (btnExportPdf) {
    btnExportPdf.addEventListener("click", () => {
      if (!currentMeetingId) return;
      console.log("Export PDF clicked. Meeting ID:", currentMeetingId);
      window.open(`/api/minutes/${currentMeetingId}/pdf?autoprint=true`, "_blank");
    });
  }

  btnCopyClip.addEventListener("click", () => {
    if (!currentMarkdownContent) return;
    navigator.clipboard.writeText(currentMarkdownContent).then(() => {
      alert("Meeting minutes copied to clipboard!");
    });
  });

  // ================= MEETING HISTORY =================
  async function loadMeetingHistory() {
    historyNoResults.classList.add("hidden");
    showHistoryMessage("Loading meeting history…");
    try {
      const res = await fetch("/api/meetings");
      const data = await res.json().catch(() => ({}));
      if (!res.ok || !data.success || !Array.isArray(data.meetings)) {
        throw new Error(data.error || "Could not load meeting history.");
      }

      meetings = data.meetings.slice().sort((a, b) =>
        String(b.date || "").localeCompare(String(a.date || "")) || Number(b.id) - Number(a.id)
      );
      if (!meetings.length) {
        showHistoryMessage("No past meetings recorded yet.");
        return;
      }

      renderMeetingHistory();
    } catch (err) {
      meetings = [];
      showHistoryMessage(err.message || "Could not load meeting history.", true);
    }
  }

  function showHistoryMessage(message, retry = false) {
    historyList.replaceChildren();
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 6;
    cell.className = "empty-state-cell";
    cell.setAttribute("role", "status");
    cell.textContent = message;
    if (retry) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "btn btn-secondary btn-sm history-retry";
      button.textContent = "Retry";
      button.addEventListener("click", loadMeetingHistory);
      cell.append(" ", button);
    }
    row.appendChild(cell);
    historyList.appendChild(row);
  }

  function renderMeetingHistory() {
    historyList.replaceChildren();
    const term = historySearch.value.trim().toLocaleLowerCase();
    const filteredMeetings = meetings.filter((meeting) =>
      `${meeting.title || ""} ${meeting.date || ""}`.toLocaleLowerCase().includes(term)
    );
    historyNoResults.classList.toggle("hidden", filteredMeetings.length > 0);

    filteredMeetings.forEach((m) => {
      const tr = document.createElement("tr");
      const idCell = document.createElement("td");
      idCell.textContent = `#${m.id}`;
      const titleCell = document.createElement("td");
      const title = document.createElement("strong");
      title.textContent = m.title || "Untitled meeting";
      titleCell.appendChild(title);
      const dateCell = document.createElement("td");
      dateCell.textContent = m.date || "—";
      const durationCell = document.createElement("td");
      durationCell.textContent = m.duration || "—";
      const statusCell = document.createElement("td");
      const status = document.createElement("span");
      status.className = "status-tag status-completed";
      status.textContent = m.status || "Processed";
      statusCell.appendChild(status);
      const actionCell = document.createElement("td");
      const viewButton = document.createElement("button");
      viewButton.type = "button";
      viewButton.className = "btn btn-secondary btn-sm";
      viewButton.textContent = "View";
      viewButton.addEventListener("click", () => window.viewHistoricalMeeting(m.id));
      const exportLink = document.createElement("a");
      exportLink.className = "btn btn-secondary btn-sm";
      exportLink.href = `/api/meetings/${encodeURIComponent(m.id)}/export`;
      exportLink.textContent = "Download";
      actionCell.append(viewButton, exportLink);
      tr.append(idCell, titleCell, dateCell, durationCell, statusCell, actionCell);
      historyList.appendChild(tr);
    });
  }

  window.viewHistoricalMeeting = async (id) => {
    try {
      const res = await fetch(`/api/meetings/${encodeURIComponent(id)}`);
      const data = await res.json().catch(() => ({}));
      if (!res.ok || !data.success || !data.meeting) {
        throw new Error(data.error || "Could not load this meeting.");
      }
      displayMinutes(data.meeting);
      switchTab("viewer-tab");
    } catch (err) {
      alert("Error loading meeting: " + err.message);
    }
  };

  // Search by meeting title or date, including when history loads after typing.
  historySearch.addEventListener("input", renderMeetingHistory);

});
