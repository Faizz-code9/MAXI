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
  const btnCopyClip = document.getElementById("btn-copy-clip");

  // History elements
  const historyList = document.getElementById("history-list");
  const historySearch = document.getElementById("history-search");

  let currentMeetingId = null;
  let currentMarkdownContent = "";

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
    const formData = new FormData();
    formData.append("audio", file);
    formData.append("title", meetingTitleInput.value);
    formData.append("date", meetingDateInput.value);

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
        displayMinutes(data);
        switchTab("viewer-tab");
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
    viewActionItems.innerHTML = "";
    if (data.action_items && data.action_items.length) {
      data.action_items.forEach((item, idx) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${idx + 1}</td>
          <td>${item.task}</td>
          <td><strong>${item.assignee}</strong></td>
          <td><code>${item.deadline}</code></td>
          <td>
            <button class="status-tag ${item.status === 'Completed' ? 'status-completed' : 'status-pending'}" 
                    data-id="${item.id || ''}" data-status="${item.status}">
              ${item.status}
            </button>
          </td>
        `;
        viewActionItems.appendChild(tr);
      });
    } else {
      viewActionItems.innerHTML = `<tr><td colspan="5" style="text-align:center; color:#94A3B8;">No action items detected.</td></tr>`;
    }

    // Transcript
    viewTranscript.textContent = data.raw_transcript || data.processed_transcript || "";
  }

  // ================= EXPORT ACTIONS =================
  btnExportMd.addEventListener("click", () => {
    if (!currentMeetingId) return;
    window.location.href = `/api/meetings/${currentMeetingId}/export`;
  });

  btnCopyClip.addEventListener("click", () => {
    if (!currentMarkdownContent) return;
    navigator.clipboard.writeText(currentMarkdownContent).then(() => {
      alert("Meeting minutes copied to clipboard!");
    });
  });

  // ================= MEETING HISTORY =================
  async function loadMeetingHistory() {
    try {
      const res = await fetch("/api/meetings");
      const data = await res.json();
      if (!data.success) return;

      historyList.innerHTML = "";
      if (!data.meetings.length) {
        historyList.innerHTML = `<tr><td colspan="6" style="text-align:center; color:#94A3B8;">No past meetings recorded yet.</td></tr>`;
        return;
      }

      data.meetings.forEach(m => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>#${m.id}</td>
          <td><strong>${m.title}</strong></td>
          <td>${m.date}</td>
          <td>${m.duration}</td>
          <td><span class="status-tag status-completed">${m.status}</span></td>
          <td>
            <button class="btn btn-secondary btn-sm" onclick="viewHistoricalMeeting(${m.id})">View</button>
          </td>
        `;
        historyList.appendChild(tr);
      });
    } catch (err) {
      console.error("Failed to load meetings:", err);
    }
  }

  window.viewHistoricalMeeting = async (id) => {
    try {
      const res = await fetch(`/api/meetings/${id}`);
      const data = await res.json();
      if (data.success && data.meeting) {
        displayMinutes(data.meeting);
        switchTab("viewer-tab");
      }
    } catch (err) {
      alert("Error loading meeting: " + err.message);
    }
  };

  // Search filter
  historySearch.addEventListener("input", (e) => {
    const term = e.target.value.toLowerCase();
    const rows = historyList.querySelectorAll("tr");
    rows.forEach(r => {
      r.style.display = r.textContent.toLowerCase().includes(term) ? "" : "none";
    });
  });
});
