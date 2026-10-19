(() => {
  "use strict";
  const $ = (selector) => document.querySelector(selector);
  const state = { snapshot: null, timeline: null, activeView: "explorer", explorerMode: "tree", familyHighlight: false, familyPids: new Set(), selectedPid: null, expanded: new Set(), query: "", lastUpdated: 0, requestInFlight: false, toastTimer: null, initializedExpansion: false, labExperiments: [], labRuns: [], previousSnapshot: null, eventStatus: null };
  const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const humanBytes = (bytes) => {
    if (bytes === null || bytes === undefined || !Number.isFinite(Number(bytes))) return "Unavailable";
    const units = ["B", "KiB", "MiB", "GiB", "TiB"]; let value = Number(bytes), i = 0;
    while (value >= 1024 && i < units.length - 1) { value /= 1024; i++; }
    return `${value.toFixed(i === 0 ? 0 : 1)} ${units[i]}`;
  };
  const humanState = (record) => record.state_description || "State unavailable";
  const stateClass = (record) => `state-${/^[A-Za-z]$/.test(record.state || "") ? record.state : "unknown"}`;
  const processMatches = (record) => {
    if (!state.query) return true;
    const q = state.query.toLowerCase();
    return [record.name, String(record.pid), String(record.ppid), record.executable || "", ...(record.command_line || [])].join(" ").toLowerCase().includes(q);
  };
  function matchingSubtree(pid, processes, children, memo = new Map()) {
    if (memo.has(pid)) return memo.get(pid);
    const record = processes[String(pid)]; if (!record) return false;
    // Set before recursion so malformed/cyclic data cannot recurse indefinitely.
    memo.set(pid, false);
    let match = processMatches(record);
    for (const child of (children[String(pid)] || [])) match = matchingSubtree(child, processes, children, memo) || match;
    memo.set(pid, match); return match;
  }
  function showToast(message) {
    const toast = $("#toast"); toast.textContent = message; toast.classList.add("show");
    clearTimeout(state.toastTimer); state.toastTimer = setTimeout(() => toast.classList.remove("show"), 3000);
  }
  function processRow(record, hasChildren, isExpanded) {
    const selected = Number(state.selectedPid) === record.pid;
    const glyph = record.state === "Z" ? "Z" : record.state === "R" ? "▶" : record.state === "T" || record.state === "t" ? "Ⅱ" : "•";
    const family = state.familyHighlight && state.familyPids.has(record.pid);
    return `<div class="tree-row${selected ? " selected" : ""}${family ? " family-related" : ""}" role="treeitem" tabindex="0" aria-selected="${selected}" aria-expanded="${hasChildren ? isExpanded : "false"}" data-pid="${record.pid}">
      <button class="tree-toggle${hasChildren ? "" : " placeholder"}" data-toggle="${record.pid}" aria-label="${isExpanded ? "Collapse" : "Expand"} ${escapeHtml(record.name)}" tabindex="-1">${hasChildren ? (isExpanded ? "▾" : "▸") : "·"}</button>
      <span class="process-glyph ${stateClass(record)}" aria-hidden="true">${glyph}</span>
      <span class="process-name" title="${escapeHtml(record.name)}"><strong>${escapeHtml(record.name || "Unknown process")}</strong></span>
      <span class="process-pid">${record.pid}</span><span class="state-pill ${stateClass(record)}">${escapeHtml(record.state || "?")}</span>
    </div>`;
  }
  function renderNode(pid, depth, processes, children, matching, seen) {
    const key = String(pid), record = processes[key];
    if (!record || seen.has(pid) || !matching.has(pid)) return "";
    seen.add(pid);
    const childIds = (children[key] || []).filter((id) => matching.has(id));
    const hasChildren = childIds.length > 0;
    const expanded = state.query ? true : state.expanded.has(pid);
    let html = `<div class="tree-node" role="group">${processRow(record, hasChildren, expanded)}`;
    if (hasChildren && expanded) html += `<div class="tree-children">${childIds.map((child) => renderNode(child, depth + 1, processes, children, matching, seen)).join("")}</div>`;
    html += `</div>`;
    return html;
  }
  function calculateFamily(processes, children) {
    const family = new Set();
    const selected = Number(state.selectedPid);
    if (!selected || !processes[String(selected)]) return family;
    let cursor = processes[String(selected)], guard = new Set();
    while (cursor && !guard.has(cursor.pid)) {
      guard.add(cursor.pid); family.add(cursor.pid);
      cursor = processes[String(cursor.ppid)];
    }
    const visit = (pid) => {
      for (const child of children[String(pid)] || []) {
        if (family.has(child)) continue;
        family.add(child); visit(child);
      }
    };
    visit(selected);
    return family;
  }
  function renderGroupedView(mode, processes) {
    const records = Object.values(processes).filter(processMatches).sort((a,b) => a.pid - b.pid);
    const groups = new Map();
    const add = (key, record) => { if (!groups.has(key)) groups.set(key, []); groups.get(key).push(record); };
    if (mode === "threads") {
      for (const record of records) add(`Process ${record.pid} · ${record.name}`, record);
      return [...groups.entries()].map(([label, members]) => `<section class="organization-group"><h3>${escapeHtml(label)}</h3><p class="organization-caption">${members[0].thread_count ?? "?"} threads reported · thread IDs from /proc/PID/task</p><div class="organization-members">${(members[0].thread_ids || []).map(tid => `<button class="thread-chip" type="button" data-pid="${members[0].pid}" title="Select owning process">TID ${tid}</button>`).join("") || `<span class="organization-empty">Thread IDs unavailable</span>`}</div></section>`).join("") || `<div class="tree-empty">No processes match that search.</div>`;
    }
    for (const record of records) {
      let key;
      if (mode === "groups") key = record.process_group_id == null ? "Process group unavailable" : `Process group ${record.process_group_id}`;
      else if (mode === "sessions") key = record.session_id == null ? "Session unavailable" : `Session ${record.session_id}`;
      else key = record.cgroups?.length ? record.cgroups[0] : "Cgroup unavailable";
      add(key, record);
    }
    return [...groups.entries()].sort((a,b) => a[0].localeCompare(b[0], undefined, {numeric:true})).map(([label, members]) => `<section class="organization-group"><h3>${escapeHtml(label)}</h3><p class="organization-caption">${members.length} process${members.length === 1 ? "" : "es"}</p><div class="organization-members">${members.map(record => processRow(record, false, false)).join("")}</div></section>`).join("") || `<div class="tree-empty">No processes match that search.</div>`;
  }
  function renderTree() {
    const container = $("#tree-container"), snapshot = state.snapshot;
    if (!snapshot) return;
    const processes = snapshot.processes || {}, children = snapshot.children_by_pid || {};
    state.familyPids = calculateFamily(processes, children);
    const matching = new Set();
    for (const pid of Object.keys(processes)) if (matchingSubtree(Number(pid), processes, children)) matching.add(Number(pid));
    let html = "";
    if (state.explorerMode !== "tree") {
      html = renderGroupedView(state.explorerMode, processes);
    } else {
      const seen = new Set();
      const roots = (snapshot.roots || []).filter((pid) => matching.has(pid));
      html = roots.map((pid) => renderNode(pid, 0, processes, children, matching, seen)).join("");
      // Defensive fallback for unusual proc snapshots with no resolvable roots.
      for (const pid of Object.keys(processes).map(Number)) if (!seen.has(pid) && matching.has(pid)) html += renderNode(pid, 0, processes, children, matching, seen);
      if (!html) html = `<div class="tree-empty">${state.query ? "No processes match that search. Try a different name or ID." : "No process records were available in this snapshot."}</div>`;
    }
    container.innerHTML = html;
    const count = state.explorerMode === "tree" ? matching.size : Object.values(processes).filter(processMatches).length;
    $("#tree-result-count").textContent = state.query ? `${count} matching` : `${count} processes`;
    document.querySelectorAll("[data-explorer-mode]").forEach(button => {
      const active = button.dataset.explorerMode === state.explorerMode;
      button.classList.toggle("active", active); button.setAttribute("aria-pressed", String(active));
    });
    const familyButton = $("#family-toggle");
    familyButton.classList.toggle("active", state.familyHighlight);
    familyButton.setAttribute("aria-pressed", String(state.familyHighlight));
    familyButton.textContent = state.familyHighlight ? "Family highlighted" : "Follow family";
    familyButton.disabled = state.selectedPid == null;
  }
  function field(label, value, wide = false, extraClass = "") {
    return `<div class="detail-field${wide ? " wide" : ""}"><span>${escapeHtml(label)}</span><strong class="${extraClass}">${escapeHtml(value)}</strong></div>`;
  }
  function renderDetails() {
    const target = $("#detail-content"), snapshot = state.snapshot;
    const record = snapshot && snapshot.processes[String(state.selectedPid)];
    if (!record) {
      target.innerHTML = `<div class="empty-detail"><div class="empty-icon">⌖</div><strong>Select a process</strong><p>Choose any row in the tree to view its identity, state, and available resource information.</p></div>`;
      return;
    }
    const parent = snapshot.processes[String(record.ppid)];
    const command = record.command_line === null ? "Unavailable" : (record.command_line.length ? record.command_line.join(" ") : "No command-line arguments (or unavailable for this process)");
    const warnings = record.collection_warnings || [];
    target.innerHTML = `<div class="detail-process-title"><span class="process-glyph ${stateClass(record)}">${escapeHtml(record.state || "?")}</span><div><h3>${escapeHtml(record.name || "Unknown process")}</h3><p>Process ID ${record.pid}</p></div></div>
      <div class="detail-section-title">PROCESS IDENTITY</div><div class="detail-grid">
      ${field("Process ID (PID)", record.pid)}${field("Parent process ID", record.ppid)}
      ${field("Parent process", parent ? `${parent.name} · ${parent.pid}` : (record.ppid === 0 ? "System root" : "Not in this snapshot"), true)}
      ${field("Current state", `${record.state || "?"} · ${humanState(record)}`, true)}
      </div><div class="detail-section-title">RESOURCE INFORMATION</div><div class="detail-grid">
      ${field("Resident memory", humanBytes(record.rss_bytes))}${field("Thread count", record.thread_count ?? "Unavailable")}
      ${field("User CPU ticks", record.user_ticks ?? "Unavailable")}${field("System CPU ticks", record.system_ticks ?? "Unavailable")}
      </div><div class="detail-section-title">PROCESS ORGANIZATION</div><div class="detail-grid">
      ${field("Process group ID (PGID)", record.process_group_id ?? "Unavailable")}${field("Session ID (SID)", record.session_id ?? "Unavailable")}
      ${field("Controlling terminal", record.terminal_id === 0 ? "None" : (record.terminal_id ?? "Unavailable"), true)}
      ${field("Thread IDs (TIDs)", (record.thread_ids || []).join(", ") || "Unavailable", true)}
      ${field("Cgroup paths", (record.cgroups || []).join("; ") || "Unavailable", true)}
      </div><div class="detail-section-title">EXECUTION DETAILS</div><div class="detail-grid">
      ${field("Executable path", record.executable ?? "Unavailable", true)}${field("Command line", command, true, "command-line")}
      </div><div class="detail-section-title">PROCESS IDENTITY KEY</div><p class="detail-description">This process is tracked using the current boot ID, PID, and start time. This helps distinguish a new process if Linux reuses the same PID.</p>
      <div class="detail-grid" style="margin-top:10px">${field("Start time (clock ticks)", record.identity?.start_time_ticks ?? "Unavailable", true)}${field("Boot ID", record.identity?.boot_id ?? "Unavailable", true)}</div>
      ${warnings.length ? `<div class="detail-section-title">COLLECTION NOTES</div><ul class="warning-list">${warnings.map((w) => `<li>${escapeHtml(w)}</li>`).join("")}</ul>` : ""}`;
  }
  function updateSummary(snapshot) {
    const processes = snapshot.processes || {};
    $("#process-count").textContent = Object.keys(processes).length.toLocaleString();
    $("#root-count").textContent = (snapshot.roots || []).length.toLocaleString();
    $("#snapshot-time").textContent = new Date(snapshot.captured_at_unix * 1000).toLocaleTimeString([], {hour:"2-digit",minute:"2-digit",second:"2-digit"});
    $("#snapshot-duration").textContent = `Collected in ${(snapshot.duration_seconds * 1000).toFixed(1)} ms`;
    const warningCount = (snapshot.warnings || []).length + (snapshot.skipped_processes || 0);
    $("#warning-count").textContent = warningCount.toLocaleString();
    $("#skipped-count").textContent = `Skipped records: ${snapshot.skipped_processes || 0}`;
    $("#boot-label").textContent = `Boot identity: ${snapshot.boot_id ? snapshot.boot_id.slice(0, 8) + "…" : "unavailable"}`;
  }
  const timelineIcons = { baseline: "◎", appeared: "+", disappeared: "−", state: "↻", parent: "⌁", "pid-reuse": "!", fork: "↗", exec: "▶", exit: "×" };
  function renderTimeline() {
    const payload = state.timeline;
    const target = $("#timeline-events");
    if (!payload) return;
    const filter = $("#timeline-filter").value;
    const events = (payload.events || []).filter((event) => filter === "all" || event.kind === filter);
    $("#timeline-count").textContent = `${events.length} observation${events.length === 1 ? "" : "s"} shown · ${payload.event_count} retained in memory`;
    target.innerHTML = events.length ? events.map((event) => {
      const time = new Date(event.timestamp * 1000);
      const formatted = Number.isNaN(time.getTime()) ? "Time unavailable" : time.toLocaleString([], {month:"short",day:"numeric",hour:"2-digit",minute:"2-digit",second:"2-digit"});
      const pid = event.pid === null || event.pid === undefined ? "System-wide" : `PID ${event.pid}`;
      const sourceLabel = event.source === "kernel event" ? "Kernel event · observed" : event.source === "snapshot" ? "Baseline snapshot" : "Inferred from snapshots";
      const confidenceClass = event.confidence === "observed" ? "observed" : "inferred";
      return `<article class="timeline-event" data-kind="${escapeHtml(event.kind)}"><div class="timeline-event-icon" aria-hidden="true">${timelineIcons[event.kind] || "·"}</div><div><h3>${escapeHtml(event.title)}</h3><p>${escapeHtml(event.detail)}</p><div class="timeline-event-meta"><span class="timeline-tag">${escapeHtml(pid)}</span><span class="timeline-tag ${confidenceClass}">${escapeHtml(sourceLabel)}</span></div></div><time class="timeline-time" datetime="${escapeHtml(time.toISOString ? time.toISOString() : "")}">${escapeHtml(formatted)}</time></article>`;
    }).join("") : `<div class="timeline-empty">${filter === "all" ? "No observations have been recorded yet. Wait for the next process snapshot." : "No observations match this filter yet."}</div>`;
    $("#timeline-limitations").innerHTML = (payload.limitations || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("");
  }
  async function fetchTimeline() {
    try {
      const response = await fetch("/api/timeline", {cache:"no-store", headers:{"Accept":"application/json"}});
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || `Timeline returned HTTP ${response.status}`);
      state.timeline = payload;
      renderTimeline();
    } catch (error) {
      $("#timeline-events").innerHTML = `<div class="timeline-empty">Timeline temporarily unavailable: ${escapeHtml(error.message)}</div>`;
    }
  }
  function setView(view) {
    state.activeView = ["timeline", "lab", "reports"].includes(view) ? view : "explorer";
    $("#explorer-view").classList.toggle("view-hidden", state.activeView !== "explorer");
    $("#timeline-view").classList.toggle("view-hidden", state.activeView !== "timeline");
    $("#lab-view").classList.toggle("view-hidden", state.activeView !== "lab");
    $("#reports-view").classList.toggle("view-hidden", state.activeView !== "reports");
    document.querySelectorAll(".nav-item[data-view]").forEach((link) => {
      const active = link.dataset.view === state.activeView;
      link.classList.toggle("active", active);
      if (active) link.setAttribute("aria-current", "page"); else link.removeAttribute("aria-current");
    });
    const crumb = $(".crumb strong");
    if (crumb) crumb.textContent = ({explorer:"Process Explorer", timeline:"Activity Timeline", lab:"Process Lab", reports:"Reports"})[state.activeView];
    if (state.activeView === "timeline") fetchTimeline();
    if (state.activeView === "lab") { fetchLabExperiments(); fetchLabStatus(); }
    if (state.activeView === "reports") { renderReportDiagnostics(); fetchEventStatus(); }
  }


  const labIcons = { zombie: "☠", orphan: "↗", pipeline: "⇢", threads: "≋", "fork-exec": "⑂" };
  async function labRequest(url, options = {}) {
    const response = await fetch(url, {cache:"no-store", ...options, headers:{"Accept":"application/json", ...(options.headers || {})}});
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || `Request failed (${response.status})`);
    return payload;
  }
  function renderLabExperiments() {
    const target = $("#lab-experiments");
    target.innerHTML = state.labExperiments.map((exp) => `<article class="lab-experiment-card"><div class="lab-card-top"><span class="lab-card-icon">${labIcons[exp.id] || "⚗"}</span><span class="timeline-tag">${exp.duration}s maximum</span></div><h3>${escapeHtml(exp.title)}</h3><p>${escapeHtml(exp.summary)}</p><div class="lab-expected"><strong>What to look for</strong><p>${escapeHtml(exp.expected)}</p></div><button class="button button-primary lab-run-button" type="button" data-lab-run="${escapeHtml(exp.id)}">Run experiment</button></article>`).join("") || `<div class="timeline-empty">No experiments are available.</div>`;
    $("#lab-compiler-status").textContent = state.labCompilerAvailable ? "C compiler available" : "C compiler required";
    $("#lab-compiler-status").classList.toggle("observed", state.labCompilerAvailable);
  }
  function renderLabRuns() {
    const target = $("#lab-runs");
    const active = state.labRuns.filter((run) => run.status === "running");
    target.innerHTML = state.labRuns.length ? state.labRuns.map((run) => `<article class="lab-run-card"><div class="lab-run-heading"><div><h3>${escapeHtml(run.title)}</h3><p>Run ${escapeHtml(run.id)} · Launcher PID ${run.pid}</p></div><span class="timeline-tag ${run.status === "running" ? "inferred" : "observed"}">${escapeHtml(run.status)}</span></div><p class="lab-run-explanation">${escapeHtml(run.summary)}</p><div class="lab-expected"><strong>Expected observation</strong><p>${escapeHtml(run.expected)}</p></div>${run.output ? `<details class="lab-output"><summary>Experiment output</summary><pre>${escapeHtml(run.output)}</pre></details>` : ""}<div class="lab-run-actions"><button class="button button-secondary" type="button" data-lab-observe="${escapeHtml(run.pid)}">Find in Explorer</button>${run.status === "running" ? `<button class="button button-danger" type="button" data-lab-stop="${escapeHtml(run.id)}">Stop & clean up</button>` : ""}</div></article>`).join("") : `<div class="timeline-empty">No experiments started yet. Choose an experiment above to begin.</div>`;
    $("#lab-cleanup-all").disabled = active.length === 0;
  }
  async function fetchLabExperiments() {
    try { const payload = await labRequest("/api/lab/experiments"); state.labExperiments = payload.experiments || []; state.labCompilerAvailable = payload.compiler_available; renderLabExperiments(); }
    catch (error) { $("#lab-experiments").innerHTML = `<div class="timeline-empty">Could not load experiments: ${escapeHtml(error.message)}</div>`; }
  }
  async function fetchLabStatus() {
    try { const payload = await labRequest("/api/lab/status"); state.labRuns = payload.runs || []; renderLabRuns(); }
    catch (error) { $("#lab-runs").innerHTML = `<div class="timeline-empty">Could not load experiment status: ${escapeHtml(error.message)}</div>`; }
  }
  async function startLabExperiment(id) {
    const button = document.querySelector(`[data-lab-run="${CSS.escape(id)}"]`);
    if (button) { button.disabled = true; button.textContent = "Starting…"; }
    try { await labRequest("/api/lab/run", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({experiment:id})}); await fetchLabStatus(); showToast("Experiment started. Open Explorer to observe its processes."); }
    catch (error) { showToast(`Could not start experiment: ${error.message}`); }
    finally { if (button) { button.disabled = false; button.textContent = "Run experiment"; } }
  }
  async function stopLabRun(id) {
    try { await labRequest(`/api/lab/stop/${encodeURIComponent(id)}`, {method:"POST"}); await fetchLabStatus(); await fetchSnapshot(); showToast("Lab experiment stopped and cleanup requested."); }
    catch (error) { showToast(`Cleanup issue: ${error.message}`); }
  }
  async function cleanupAllLabRuns() {
    const active = state.labRuns.filter((run) => run.status === "running");
    for (const run of active) { try { await labRequest(`/api/lab/stop/${encodeURIComponent(run.id)}`, {method:"POST"}); } catch (_) {} }
    await fetchLabStatus(); await fetchSnapshot(); showToast("Cleanup requested for all active Lab experiments.");
  }

  async function fetchSnapshot(manual = false) {
    if (state.requestInFlight) return;
    state.requestInFlight = true;
    try {
      const response = await fetch("/api/snapshot", {cache:"no-store", headers:{"Accept":"application/json"}});
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || `Collector returned HTTP ${response.status}`);
      if (state.snapshot) state.previousSnapshot = state.snapshot;
      state.snapshot = payload; state.lastUpdated = Date.now();
      if (state.activeView === "reports") renderSnapshotDiff();
      if (!state.initializedExpansion) { (payload.roots || []).forEach((pid) => state.expanded.add(pid)); state.initializedExpansion = true; }
      $("#status-dot").style.background = "var(--green)"; $("#footer-status").style.background = "var(--green)";
      $("#connection-label").textContent = "Collector connected";
      $("#footer-message").textContent = `Updated ${new Date().toLocaleTimeString([], {hour:"2-digit",minute:"2-digit",second:"2-digit"})}`;
      updateSummary(payload); renderTree(); renderDetails(); await fetchTimeline();
      if (manual) showToast("Process snapshot refreshed.");
    } catch (error) {
      $("#status-dot").style.background = "var(--amber)"; $("#footer-status").style.background = "var(--amber)";
      $("#connection-label").textContent = "Collector unavailable";
      $("#footer-message").textContent = "Could not refresh process data";
      if (!state.snapshot) $("#tree-container").innerHTML = `<div class="tree-empty">Unable to read process information.<br><br>${escapeHtml(error.message)}<br><br>Start ProcScope on Ubuntu using the provided launcher.</div>`;
      if (manual) showToast(`Refresh failed: ${error.message}`);
    } finally { state.requestInFlight = false; }
  }

  function reportSnapshot(redact) {
    if (!state.snapshot) throw new Error("No process snapshot is available yet.");
    const payload = JSON.parse(JSON.stringify(state.snapshot));
    payload.report = { product: "ProcScope", version: "1.0", exported_at: new Date().toISOString(), command_line_redacted: Boolean(redact), note: "Best-effort /proc snapshot; not an atomic system-wide view." };
    if (redact) {
      for (const record of Object.values(payload.processes || {})) {
        record.command_line = record.command_line === null ? null : (record.command_line && record.command_line.length ? ["[REDACTED]"] : []);
        record.executable = record.executable ? "[REDACTED]" : record.executable;
      }
    }
    return payload;
  }
  function downloadFile(filename, content, type) {
    const url = URL.createObjectURL(new Blob([content], {type}));
    const anchor = document.createElement("a"); anchor.href = url; anchor.download = filename; document.body.appendChild(anchor); anchor.click(); anchor.remove(); URL.revokeObjectURL(url);
  }
  function renderSnapshotDiff() {
    const target = $("#snapshot-diff");
    if (!state.snapshot || !state.previousSnapshot) { target.innerHTML = "<strong>Waiting for two snapshots</strong><p>Once a second snapshot is collected, ProcScope can compare process identities and parent relationships.</p>"; return; }
    const before = state.previousSnapshot.processes || {}, after = state.snapshot.processes || {};
    const oldKeys = new Set(Object.values(before).map(p => `${p.identity?.boot_id}:${p.pid}:${p.identity?.start_time_ticks}`));
    const newKeys = new Set(Object.values(after).map(p => `${p.identity?.boot_id}:${p.pid}:${p.identity?.start_time_ticks}`));
    const oldPids = new Set(Object.values(before).map(p => p.pid));
    const newPids = new Set(Object.values(after).map(p => p.pid));
    const appeared = [...newKeys].filter(k => !oldKeys.has(k)).length;
    const disappeared = [...oldKeys].filter(k => !newKeys.has(k)).length;
    const reused = [...oldPids].filter(pid => newPids.has(pid) && [...Object.values(before)].some(p => p.pid === pid && !newKeys.has(`${p.identity?.boot_id}:${p.pid}:${p.identity?.start_time_ticks}`))).length;
    target.innerHTML = `<strong>Comparison ready</strong><p>Latest snapshot compared with the immediately previous browser-session snapshot. Timing differences can affect results.</p><div class="report-diff-stats"><div class="report-diff-stat"><strong>${appeared}</strong><span>New identities</span></div><div class="report-diff-stat"><strong>${disappeared}</strong><span>Missing identities</span></div><div class="report-diff-stat"><strong>${reused}</strong><span>Possible PID reuse</span></div></div>`;
  }
  function renderReportDiagnostics(summary = null) {
    const snap = state.snapshot;
    const target = $("#diagnostics-content");
    if (!snap) { target.textContent = "Waiting for a process snapshot."; return; }
    const values = [
      ["Baseline collector", "Linux /proc snapshots"], ["Processes visible", Object.keys(snap.processes || {}).length],
      ["Visible tree roots", (snap.roots || []).length], ["Records skipped", snap.skipped_processes ?? "Unavailable"],
      ["Collection warnings", (snap.warnings || []).length], ["Snapshot duration", `${(snap.duration_seconds * 1000).toFixed(1)} ms`],
      ["Kernel event mode", state.eventStatus?.status || "Not checked"], ["Event history", `${state.eventStatus?.event_count ?? 0} retained`]
    ];
    target.innerHTML = values.map(([label, value]) => `<div class="diagnostic-item"><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong></div>`).join("");
    const badge = $("#event-mode-badge");
    badge.textContent = state.eventStatus?.status === "listening" ? "Events listening" : "Snapshot baseline";
    badge.classList.toggle("observed", state.eventStatus?.status === "listening");
    if (state.eventStatus?.message) $("#event-message").textContent = state.eventStatus.message;
  }
  async function fetchEventStatus() {
    try { const response = await fetch("/api/events/status", {cache:"no-store"}); state.eventStatus = await response.json(); renderReportDiagnostics(); }
    catch (error) { $("#event-message").textContent = `Event status unavailable: ${error.message}. Snapshot collection continues independently.`; }
  }
  async function controlEventMode(action) {
    const button = action === "start" ? $("#event-start") : $("#event-stop");
    button.disabled = true;
    try {
      const response = await fetch(`/api/events/${action}`, {method:"POST", cache:"no-store", headers:{"Accept":"application/json"}});
      const payload = await response.json(); state.eventStatus = payload; $("#event-message").textContent = payload.message || `Event mode ${payload.status}.`; renderReportDiagnostics();
      showToast(payload.status === "listening" ? "Optional event collection is listening." : `Event mode: ${payload.status}. Snapshot mode remains available.`);
    } catch (error) { $("#event-message").textContent = `Could not change event mode: ${error.message}`; }
    finally { button.disabled = false; }
  }
  $("#reports-refresh").addEventListener("click", async () => { await fetchSnapshot(true); await fetchEventStatus(); renderSnapshotDiff(); });
  $("#compare-snapshots").addEventListener("click", renderSnapshotDiff);
  $("#export-json").addEventListener("click", () => { try { const data = reportSnapshot($("#report-redact").checked); downloadFile(`procscope-snapshot-${new Date().toISOString().replace(/[:.]/g,"-")}.json`, JSON.stringify(data, null, 2), "application/json"); showToast("Snapshot JSON exported."); } catch (error) { showToast(error.message); } });
  $("#export-csv").addEventListener("click", () => { try { const data = reportSnapshot($("#report-redact").checked); const columns = ["pid","ppid","name","state","rss_bytes","thread_count","user_ticks","system_ticks","executable","command_line"]; const quote = value => `"${String(value ?? "").replace(/"/g, '""')}"`; const rows = [columns.join(","), ...Object.values(data.processes).map(p => columns.map(c => quote(Array.isArray(p[c]) ? p[c].join(" ") : p[c])).join(","))]; downloadFile(`procscope-processes-${new Date().toISOString().replace(/[:.]/g,"-")}.csv`, rows.join("\r\n"), "text/csv;charset=utf-8"); showToast("Process table CSV exported."); } catch (error) { showToast(error.message); } });
  $("#event-start").addEventListener("click", () => controlEventMode("start"));
  $("#event-stop").addEventListener("click", () => controlEventMode("stop"));

  document.querySelectorAll(".nav-item[data-view]").forEach((link) => link.addEventListener("click", (event) => { event.preventDefault(); setView(link.dataset.view); history.replaceState(null, "", link.getAttribute("href")); }));
  $("#timeline-filter").addEventListener("change", renderTimeline);
  $("#lab-experiments").addEventListener("click", (event) => { const button = event.target.closest("[data-lab-run]"); if (button) startLabExperiment(button.dataset.labRun); });
  $("#lab-runs").addEventListener("click", (event) => {
    const stop = event.target.closest("[data-lab-stop]"); if (stop) { stopLabRun(stop.dataset.labStop); return; }
    const observe = event.target.closest("[data-lab-observe]"); if (observe) { setView("explorer"); state.query = String(observe.dataset.labObserve); $("#search-input").value = state.query; renderTree(); showToast(`Searching the process tree for PID ${state.query}.`); }
  });
  $("#lab-refresh").addEventListener("click", async () => { await fetchLabExperiments(); await fetchLabStatus(); showToast("Process Lab status refreshed."); });
  $("#lab-cleanup-all").addEventListener("click", cleanupAllLabRuns);
  $("#timeline-refresh").addEventListener("click", async () => { await fetchSnapshot(true); await fetchTimeline(); showToast("Timeline refreshed from the latest snapshot."); });
  document.querySelectorAll("[data-explorer-mode]").forEach(button => button.addEventListener("click", () => { state.explorerMode = button.dataset.explorerMode; renderTree(); }));
  $("#family-toggle").addEventListener("click", () => { state.familyHighlight = !state.familyHighlight; renderTree(); showToast(state.familyHighlight ? "Selected process family highlighted." : "Process-family highlighting cleared."); });
  $("#tree-container").addEventListener("click", (event) => {
    const toggle = event.target.closest("[data-toggle]");
    if (toggle) {
      event.stopPropagation(); const pid = Number(toggle.dataset.toggle);
      if (state.expanded.has(pid)) state.expanded.delete(pid); else state.expanded.add(pid);
      renderTree(); return;
    }
    const row = event.target.closest("[data-pid]"); if (row) { state.selectedPid = Number(row.dataset.pid); renderTree(); renderDetails(); }
  });
  $("#tree-container").addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      const row = event.target.closest("[data-pid]"); if (row && event.target === row) { event.preventDefault(); state.selectedPid = Number(row.dataset.pid); renderTree(); renderDetails(); }
    }
  });
  $("#search-input").addEventListener("input", (event) => { state.query = event.target.value.trim(); renderTree(); });
  $("#refresh-now").addEventListener("click", () => fetchSnapshot(true));
  $("#collapse-all").addEventListener("click", () => { state.expanded.clear(); renderTree(); showToast("Process tree collapsed."); });
  document.addEventListener("keydown", (event) => {
    if (event.key === "/" && !["INPUT","TEXTAREA"].includes(document.activeElement.tagName)) { event.preventDefault(); $("#search-input").focus(); }
    if (event.key === "Escape" && document.activeElement === $("#search-input")) { $("#search-input").value = ""; state.query = ""; renderTree(); $("#search-input").blur(); }
  });
  if (["#timeline", "#lab", "#reports"].includes(location.hash)) setView(location.hash.slice(1));
  fetchSnapshot(); setInterval(() => fetchSnapshot(), 2000);
})();
