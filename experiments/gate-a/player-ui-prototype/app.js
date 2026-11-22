const state = {
  bootstrap: null,
  projection: null,
  attemptId: null,
  page: "home",
  viewer: null,
  viewerOrigin: "investigations",
  viewerInvokerId: null,
  viewerScrollY: 0,
  viewerCompare: null,
  selectedOrders: new Set(["A", "T", "C"]),
  orderReview: false,
  differential: ["DX-A", "DX-B"],
  reasoning: "",
  questionDraft: "How many episodes do you remember?",
  dialogueBlocked: false,
  debrief: null,
  debriefState: "idle",
  selectedRating: 0,
  bannerDismissed: false,
  lastCommandError: null,
  draftVersion: 0,
  draftHasLocalChanges: false,
  draftConflict: null,
  draftSaveStatus: "",
  pendingOrder: null,
  recoveryMessage: "",
};

const CASE_ITEMS = [
  { id: "A", kind: "point", title: "Point observation A", description: "Scalar fixture observation" },
  { id: "B", kind: "point", title: "Point observation B", description: "Compatible point item for same-time comparison" },
  { id: "T", kind: "trace", title: "Trace study T", description: "Three-sample synthetic waveform" },
  { id: "C", kind: "point", title: "Point observation C", description: "Additional scalar fixture observation" },
];

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const byId = (id) => document.getElementById(id);

class ApiError extends Error {
  constructor(status, body) {
    super(body?.error || `Request failed (${status})`);
    this.status = status;
    this.body = body;
  }
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
  });
  let body = {};
  try { body = await response.json(); } catch { body = {}; }
  if (!response.ok) throw new ApiError(response.status, body);
  return body;
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[character]);
}

function formatClock(milliseconds) {
  const ms = Math.max(0, Number(milliseconds) || 0);
  const minutes = Math.floor(ms / 60000);
  const seconds = Math.floor((ms % 60000) / 1000);
  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
}

function formatPrecise(milliseconds) {
  const ms = Math.max(0, Number(milliseconds) || 0);
  const minutes = Math.floor(ms / 60000);
  const seconds = Math.floor((ms % 60000) / 1000);
  const fraction = ms % 1000;
  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}.${String(fraction).padStart(3, "0")}`;
}

function announce(message) {
  const announcer = byId("announcer");
  if (announcer) announcer.textContent = message;
}

let toastTimer = 0;
function toast(message, kind = "info") {
  const node = byId("toast");
  node.textContent = message;
  node.className = `toast toast-${kind}`;
  node.hidden = false;
  window.clearTimeout(toastTimer);
  toastTimer = window.setTimeout(() => { node.hidden = true; }, 5500);
  announce(message);
}

function activeData() {
  return state.projection?.data || {};
}

function activeOrders() {
  return activeData().orders || {};
}

function releasedResults() {
  return activeData().released_results || {};
}

function activeAttemptNumber() {
  return state.projection?.attempt_number || 1;
}

function attemptName() {
  return `Patient 04 · Attempt ${activeAttemptNumber()}`;
}

function hasActiveAttempt() {
  return Boolean(state.attemptId && state.projection);
}

function isComplete() {
  return state.projection?.status === "encounter_complete";
}

function draftKey(attemptId = state.attemptId) {
  return `meddx-fixture-draft:${attemptId}`;
}

function pendingOrderKey(attemptId = state.attemptId) {
  return `meddx-fixture-pending-order:${attemptId}`;
}

function readDraft(attemptId) {
  if (!attemptId) return null;
  try { return JSON.parse(localStorage.getItem(draftKey(attemptId)) || "null"); }
  catch { return null; }
}

function readPendingOrder(attemptId) {
  if (!attemptId) return null;
  try {
    const value = JSON.parse(localStorage.getItem(pendingOrderKey(attemptId)) || "null");
    if (value?.attempt_id !== attemptId || value.kind !== "order_tests" || typeof value.command_id !== "string" || !Number.isInteger(value.expected_revision)) return null;
    const items = Array.isArray(value.payload?.items) ? value.payload.items.filter((item) => {
      const definition = CASE_ITEMS.find((candidate) => candidate.id === item?.item_id);
      return definition && definition.kind === item?.kind;
    }) : [];
    if (!items.length) return null;
    return { ...value, payload: { items } };
  } catch { return null; }
}

function persistPendingOrder(value) {
  try {
    localStorage.setItem(pendingOrderKey(value.attempt_id), JSON.stringify(value));
    state.pendingOrder = value;
    state.recoveryMessage = "Sending the saved order request. If the response is lost, the same request can be checked or retried.";
    renderDraftStatus();
    return true;
  } catch {
    state.draftSaveStatus = "Recovery record not saved · the order was not sent.";
    renderDraftStatus();
    return false;
  }
}

function clearPendingOrder() {
  try { if (state.attemptId) localStorage.removeItem(pendingOrderKey()); } catch { /* A committed order remains discoverable from the authority. */ }
  state.pendingOrder = null;
  state.recoveryMessage = "";
  renderDraftStatus();
}

function saveDraft() {
  if (!state.attemptId || isComplete()) return;
  if (state.draftConflict) {
    state.draftSaveStatus = "Draft conflict · choose which saved copy to keep.";
    renderDraftStatus();
    return false;
  }
  const stored = readDraft(state.attemptId);
  const storedVersion = Number(stored?._draft_revision) || 0;
  if (storedVersion > state.draftVersion) {
    state.draftConflict = stored;
    state.draftSaveStatus = "A newer draft was saved in another tab.";
    renderDraftStatus();
    return false;
  }
  const draft = {
    reasoning: state.reasoning,
    differential: state.differential,
    questionDraft: state.questionDraft,
    selectedOrders: [...state.selectedOrders],
    _draft_revision: Math.max(state.draftVersion, storedVersion) + 1,
  };
  try {
    localStorage.setItem(draftKey(), JSON.stringify(draft));
    state.draftVersion = draft._draft_revision;
    state.draftHasLocalChanges = true;
    state.draftSaveStatus = `Draft saved · ${attemptName()}`;
    renderDraftStatus();
    return true;
  } catch {
    state.draftSaveStatus = "Draft not saved · your edits remain in this tab.";
    renderDraftStatus();
    return false;
  }
}

function applyDraft(draft) {
  state.reasoning = typeof draft?.reasoning === "string" ? draft.reasoning : "";
  state.differential = Array.isArray(draft?.differential) && draft.differential.length
    ? draft.differential.filter((item) => ["DX-A", "DX-B"].includes(item))
    : ["DX-A", "DX-B"];
  if (state.differential.length === 0) state.differential = ["DX-A", "DX-B"];
  state.questionDraft = typeof draft?.questionDraft === "string" ? draft.questionDraft : "How many episodes do you remember?";
  state.selectedOrders = new Set(Array.isArray(draft?.selectedOrders) ? draft.selectedOrders.filter((item) => CASE_ITEMS.some((entry) => entry.id === item)) : ["A", "T", "C"]);
}

function renderDraftStatus() {
  const status = byId("draft-status");
  if (status) {
    status.hidden = !state.attemptId || !state.draftSaveStatus;
    status.textContent = state.draftSaveStatus;
  }
  const conflict = byId("draft-conflict");
  if (conflict) conflict.hidden = !state.draftConflict;
  renderCommandRecovery();
}

function renderCommandRecovery() {
  const panel = byId("command-recovery");
  if (!panel) return;
  panel.hidden = !state.pendingOrder;
  if (!state.pendingOrder) return;
  const title = byId("command-recovery-title");
  const detail = byId("command-recovery-detail");
  title.textContent = state.recoveryMessage.startsWith("Checking") ? "Checking whether the order was saved" : "Order outcome needs confirmation";
  detail.textContent = state.recoveryMessage || "The response is unresolved. Check the saved projection or retry this exact request.";
}

function restoreDraft(attemptId) {
  const draft = readDraft(attemptId);
  applyDraft(draft);
  state.draftVersion = Number(draft?._draft_revision) || 0;
  state.draftHasLocalChanges = false;
  state.draftConflict = null;
  state.draftSaveStatus = draft ? `Draft restored · ${attemptName()}` : "";
  state.pendingOrder = readPendingOrder(attemptId);
  state.recoveryMessage = state.pendingOrder ? "Checking whether this order request was saved." : "";
  renderDraftStatus();
}

function setScreen(page, { focus = false } = {}) {
  if (["encounter", "investigations", "diagnosis", "submission", "debrief", "viewer"].includes(page) && !hasActiveAttempt()) {
    toast("Start a Fixture-A attempt to open this workspace.", "warning");
    page = "home";
  }
  if (page === "submission" && isComplete()) page = "debrief";
  if (page === "debrief" && !isComplete()) page = "encounter";
  state.page = page;
  render();
  if (focus) byId("main-content").focus({ preventScroll: true });
}

function statusLabel(status) {
  const labels = {
    ordered: "Ordered",
    collecting: "Collecting",
    processing: "Processing",
    released: "Released",
    closed_at_submission: "Closed at submission",
    cancelled: "Cancelled",
    unsupported: "Unsupported",
    unavailable: "Unavailable",
    failed: "Failed",
  };
  return labels[status] || status || "Not started";
}

function statusClass(status) {
  if (status === "released") return "status-released";
  if (status === "failed" || status === "unavailable" || status === "unsupported") return "status-alert";
  if (status === "closed_at_submission") return "status-closed";
  if (status === "ordered" || status === "collecting" || status === "processing") return "status-pending";
  return "status-idle";
}

async function refreshBootstrap({ keepPage = true } = {}) {
  state.bootstrap = await api("/api/bootstrap");
  const next = state.bootstrap.current_attempt_id;
  if (next && next !== state.attemptId) {
    state.attemptId = next;
    state.projection = await api(`/api/projection?attempt_id=${encodeURIComponent(next)}`);
    restoreDraft(next);
    state.page = keepPage && state.page !== "home" ? state.page : "encounter";
  } else if (state.attemptId) {
    try { state.projection = await api(`/api/projection?attempt_id=${encodeURIComponent(state.attemptId)}`); }
    catch { state.attemptId = null; state.projection = null; }
  }
  if (!state.attemptId) {
    const latest = [...state.bootstrap.attempts].reverse().find((item) => item.status === "encounter_complete");
    if (latest && new URLSearchParams(location.search).get("attempt") === latest.playthrough_id) {
      await selectAttempt(latest.playthrough_id, false);
    }
  }
  if (state.projection?.status === "encounter_complete" && state.page !== "home" && state.page !== "help") {
    state.page = "debrief";
    state.debriefState = "idle";
    state.debrief = null;
  }
  render();
  if (state.pendingOrder) void checkOrderRecovery({ automatic: true });
}

async function selectAttempt(attemptId, route = true) {
  try {
    const projection = await api(`/api/projection?attempt_id=${encodeURIComponent(attemptId)}`);
    state.attemptId = attemptId;
    state.projection = projection;
    state.viewer = null;
    state.debrief = null;
    state.debriefState = "idle";
    restoreDraft(attemptId);
    if (route) state.page = projection.status === "encounter_complete" ? "debrief" : "encounter";
    history.replaceState(null, "", `?attempt=${encodeURIComponent(attemptId)}`);
    render();
    if (state.page === "debrief") void loadDebrief();
    if (state.pendingOrder) void checkOrderRecovery({ automatic: true });
  } catch (error) {
    toast(error.message || "This attempt is not available.", "error");
  }
}

async function runCommand(kind, payload, { commandId, expectedRevision, quiet = false } = {}) {
  if (!state.projection || !state.attemptId) throw new Error("No active attempt");
  if (state.draftConflict && ["ask_patient", "order_tests", "wait", "submit_diagnosis"].includes(kind)) {
    throw new Error("Resolve the draft conflict before making another clinical change.");
  }
  if (state.pendingOrder && ["ask_patient", "order_tests", "wait", "submit_diagnosis"].includes(kind) && commandId !== state.pendingOrder.command_id) {
    throw new Error("Resolve the saved order request before making another clinical change.");
  }
  const result = await api("/api/command", {
    method: "POST",
    body: JSON.stringify({
      attempt_id: state.attemptId,
      command_id: commandId || `ui-${kind}-${crypto.randomUUID()}`,
      expected_revision: expectedRevision ?? state.projection.revision,
      kind,
      payload,
    }),
  });
  state.projection = result.projection;
  if (result.receipt.status === "revision_conflict") {
    state.lastCommandError = "revision_conflict";
    if (!quiet) toast("The attempt changed in another view. Review the latest status before continuing.", "warning");
  } else if (result.receipt.status === "restore_blocked") {
    state.lastCommandError = "restore_blocked";
    if (!quiet) toast("Resume is blocked because a required fixture version is unavailable. History remains available.", "error");
  } else if (!quiet && result.receipt.status !== "committed" && result.receipt.status !== "encounter_complete") {
    toast(`Action not committed: ${result.receipt.status.replaceAll("_", " ")}.`, "warning");
  }
  render();
  return result;
}

function render() {
  renderHeader();
  renderDraftStatus();
  renderHome();
  renderEncounter();
  renderInvestigations();
  renderViewer();
  renderDiagnosis();
  renderSubmission();
  renderDebrief();
  renderHelp();
  renderQaDrawer();
  $$(".screen").forEach((section) => {
    const visible = section.dataset.page === state.page;
    section.hidden = !visible;
    section.classList.toggle("screen-active", visible);
  });
  $$(".nav-link").forEach((button) => button.classList.toggle("active", button.dataset.screen === state.page || (state.page === "viewer" && button.dataset.screen === "investigations")));
  const bar = byId("encounter-bar");
  bar.hidden = !hasActiveAttempt() || state.page === "home" || state.page === "help";
  byId("prototype-banner");
  const banner = $(".prototype-banner");
  banner.hidden = state.bannerDismissed;
}

function renderHeader() {
  if (!state.bootstrap) return;
  const projection = state.projection;
  byId("patient-label").textContent = "Patient 04";
  byId("attempt-label").textContent = projection ? `Attempt ${activeAttemptNumber()} · ${projection.data.case_version_id || "Fixture-A v1"}` : "No active attempt";
  byId("attempt-status").textContent = projection ? (projection.status === "active" ? "In progress" : "Completed") : "Ready";
  byId("clinical-clock").textContent = formatClock(projection?.elapsed_ms || 0);
  byId("mini-clock").textContent = formatClock(projection?.elapsed_ms || 0);
  byId("investigations-clock").textContent = formatClock(projection?.elapsed_ms || 0);
  byId("viewer-attempt").textContent = projection ? attemptName() : "";
  byId("dialogue-readiness").textContent = state.bootstrap.dialogue_outcome === "success" ? "Available" : "Blocked";
  byId("dialogue-readiness").className = `state-label ${state.bootstrap.dialogue_outcome === "success" ? "ready-label" : "blocked-label"}`;
}

function renderHome() {
  if (!state.bootstrap) return;
  const cases = state.bootstrap.catalog?.data?.playable_case_ids || [];
  const attempts = state.bootstrap.attempts || [];
  const active = attempts.find((item) => item.status === "active");
  const latest = [...attempts].reverse()[0];
  byId("case-count").textContent = `${cases.length} CASE${cases.length === 1 ? "" : "S"}`;
  if (active) {
    byId("home-continue").innerHTML = `<div class="continue-card"><div class="continue-avatar">P</div><div class="continue-details"><strong>Patient 04 · Attempt ${active.number}</strong><span>Fixture-A · ${formatClock(active.elapsed_ms)} clinical time</span><span class="status-inline"><i></i> In progress</span></div><button class="primary-button" data-action="continue-active">Continue <span aria-hidden="true">→</span></button></div>`;
  } else if (latest?.status === "encounter_complete") {
    byId("home-continue").innerHTML = `<div class="continue-card"><div class="continue-avatar complete-avatar">✓</div><div class="continue-details"><strong>Patient 04 · Attempt ${latest.number}</strong><span>Fixture-A · Completed at ${formatClock(latest.elapsed_ms)}</span><span class="status-inline complete-inline"><i></i> Saved to local history</span></div><button class="secondary-button" data-action="open-latest">View debrief <span aria-hidden="true">→</span></button></div>`;
  } else {
    byId("home-continue").innerHTML = `<div class="empty-continue"><div class="empty-illustration" aria-hidden="true"><span>⌕</span><i></i><b></b></div><div><strong>No active encounter</strong><p>Publish the local synthetic case to begin a walkthrough.</p></div></div>`;
  }
  if (cases.includes("Fixture-A")) {
    byId("library-card").innerHTML = `<article class="library-card"><div class="case-icon" aria-hidden="true">◈</div><div class="library-copy"><div class="case-title-row"><h3>Fixture-A</h3><span class="case-version">V1</span></div><p>Local synthetic case · software exercise</p><div class="case-meta"><span><i class="dot-accent"></i> Ready to play</span><span>${attempts.length} attempt${attempts.length === 1 ? "" : "s"}</span></div></div><button class="secondary-button" data-action="start-attempt">${active ? "Start separate attempt" : "Start encounter"} <span aria-hidden="true">→</span></button></article>`;
  } else {
    byId("library-card").innerHTML = `<article class="library-empty"><div><strong>No cases published yet</strong><p>The local test build publishes a deterministic Fixture-A case.</p></div><button class="primary-button" data-action="generate-case">Publish fixture <span aria-hidden="true">↗</span></button></article>`;
  }
  byId("recent-attempts").innerHTML = attempts.length ? [...attempts].reverse().slice(0, 4).map((attempt) => `<button class="recent-item" data-attempt-id="${escapeHtml(attempt.playthrough_id)}"><span class="recent-avatar">P</span><span class="recent-copy"><strong>Patient 04 · Attempt ${attempt.number}</strong><small>${attempt.status === "active" ? "In progress" : "Completed"} · ${formatClock(attempt.elapsed_ms)}</small></span><span class="recent-arrow" aria-hidden="true">→</span></button>`).join("") : `<div class="empty-history"><span aria-hidden="true">◷</span><p>Completed attempts will appear here.</p></div>`;
}

function renderEncounter() {
  if (!state.projection) return;
  const data = activeData();
  const dialogue = data.dialogue_history || [];
  byId("transcript").innerHTML = dialogue.length
    ? dialogue.map((utterance) => `<div class="transcript-turn"><div class="turn-question"><span class="turn-role">YOU</span><p>${escapeHtml(utterance.question)}</p><time>${formatClock(utterance.at_ms)}</time></div><div class="turn-answer"><span class="turn-role patient-role">PATIENT</span><p>${escapeHtml(utterance.answer)}</p><span class="source-tag patient-tag">PATIENT REPORTED</span></div></div>`).join("")
    : `<div class="transcript-empty"><span class="conversation-mark" aria-hidden="true">···</span><div><strong>Start with a question</strong><p>Committed replies are added to this transcript with their source and clinical time.</p></div></div>`;
  const historyCount = data.history?.verified_prior_episodes ?? 0;
  byId("chart-history").textContent = `${historyCount} verified prior episode${historyCount === 1 ? "" : "s"} recorded`;
  const releasedCount = Object.keys(releasedResults()).length;
  byId("patient-measurements").textContent = releasedCount ? `${releasedCount} released fixture observation${releasedCount === 1 ? "" : "s"}` : "None released yet";
  byId("dialogue-blocker").hidden = !state.dialogueBlocked;
  const question = byId("question-input");
  if (document.activeElement !== question) question.value = state.questionDraft;
  const send = byId("send-question");
  send.disabled = isComplete() || Boolean(state.pendingOrder || state.draftConflict);
  byId("worklist-summary").innerHTML = renderStatusSummary();
}

function renderStatusSummary() {
  const rows = Object.values(activeOrders());
  if (!rows.length) return `<div class="empty-worklist"><span aria-hidden="true">⌁</span><strong>No investigations yet</strong><small>Open the catalog to choose an action.</small></div>`;
  const statuses = rows.map((row) => `<div class="worklist-row"><span class="test-id">${escapeHtml(row.item_id)}</span><span class="worklist-name">${escapeHtml(itemTitle(row.item_id))}</span><span class="status-pill ${statusClass(row.status)}">${escapeHtml(statusLabel(row.status))}</span></div>`).join("");
  const released = Object.keys(releasedResults()).length;
  return `<div class="worklist-rows">${statuses}</div><div class="worklist-totals"><span>${rows.length} committed</span><span>${released} released</span></div>`;
}

function itemTitle(id) {
  return CASE_ITEMS.find((item) => item.id === id)?.title || `Fixture item ${id}`;
}

function renderInvestigations() {
  if (!state.projection) return;
  const orders = activeOrders();
  byId("catalog-list").innerHTML = CASE_ITEMS.map((item) => {
    const existing = orders[item.id];
    const selected = state.selectedOrders.has(item.id);
    return `<label class="catalog-item ${existing ? "catalog-committed" : ""}"><input type="checkbox" name="order-item" value="${item.id}" ${selected ? "checked" : ""} ${existing || isComplete() ? "disabled" : ""}><span class="catalog-check" aria-hidden="true"></span><span class="catalog-glyph ${item.kind === "trace" ? "trace-glyph" : "point-glyph"}" aria-hidden="true">${item.kind === "trace" ? "∿" : "●"}</span><span class="catalog-item-copy"><strong>${escapeHtml(item.title)}</strong><small>${escapeHtml(item.description)}</small></span><span class="catalog-kind">${item.kind === "trace" ? "TRACE" : "POINT"}</span>${existing ? `<span class="already-ordered">${escapeHtml(statusLabel(existing.status))}</span>` : ""}</label>`;
  }).join("");
  byId("order-draft-count").textContent = `${state.selectedOrders.size} selected · no clock change on placement`;
  const mutationBlocked = isComplete() || Boolean(state.pendingOrder || state.draftConflict);
  byId("review-orders").disabled = !state.selectedOrders.size || mutationBlocked;
  const placeButton = $('[data-action="place-orders"]');
  if (placeButton) placeButton.disabled = mutationBlocked;
  byId("order-review-panel").hidden = !state.orderReview;
  byId("order-review-items").innerHTML = [...state.selectedOrders].map((id) => {
    const item = CASE_ITEMS.find((entry) => entry.id === id);
    return `<div class="order-review-row"><span class="review-order-icon">${item?.kind === "trace" ? "∿" : "●"}</span><div><strong>${escapeHtml(item?.title || id)}</strong><small>Queued at ${formatClock(state.projection.elapsed_ms)}</small></div><span class="step-chip">Selected</span></div>`;
  }).join("") || `<p class="helper-copy">No new items selected.</p>`;
  byId("order-list").innerHTML = Object.keys(orders).length
    ? Object.values(orders).map((order) => renderOrderRow(order)).join("")
    : `<div class="empty-orders"><span class="empty-order-icon" aria-hidden="true">⌁</span><div><strong>No orders placed</strong><p>Choose a fixture action above. Your current time remains ${formatClock(state.projection.elapsed_ms)}.</p></div></div>`;
  byId("orders-count").textContent = `${Object.keys(orders).length} ITEM${Object.keys(orders).length === 1 ? "" : "S"}`;
  byId("tray-summary").innerHTML = renderStatusSummary();
  const timeControl = byId("time-control");
  timeControl.hidden = !Object.keys(orders).length || isComplete();
  const waitButton = $('[data-action="wait"]');
  if (waitButton) waitButton.disabled = isComplete() || Boolean(state.pendingOrder || state.draftConflict);
}

function renderOrderRow(order) {
  const result = releasedResults()[order.item_id];
  const resultText = result
    ? order.kind === "trace"
      ? `${(result.samples || []).join(" · ")} ${result.units || ""}`
      : `${result.value} ${result.units || ""}`
    : "No released result";
  const canOpen = Boolean(result) && !isComplete();
  return `<article class="order-row"><div class="test-id large-id">${escapeHtml(order.item_id)}</div><div class="order-row-copy"><div class="order-title-line"><strong>${escapeHtml(itemTitle(order.item_id))}</strong><span class="status-pill ${statusClass(order.status)}">${escapeHtml(statusLabel(order.status))}</span></div><small>Ordered ${formatClock(order.ordered_at_ms)} · ${escapeHtml(order.kind.toUpperCase())}</small>${result ? `<span class="released-preview">${escapeHtml(resultText)}</span>` : `<span class="pending-preview">${escapeHtml(order.status === "processing" ? "Result not released yet" : "Waiting for a later clinical event")}</span>`}</div>${canOpen ? `<button id="view-order-${escapeHtml(order.item_id)}" class="secondary-button view-result-button" data-view-item="${escapeHtml(order.item_id)}">View study <span aria-hidden="true">↗</span></button>` : ""}</article>`;
}

function renderViewer() {
  if (!state.viewer || !state.projection) return;
  const { itemId, artifact } = state.viewer;
  const title = itemTitle(itemId);
  byId("viewer-title").textContent = title;
  byId("viewer-subtitle").textContent = `Fixture-A · ${artifact?.kind === "trace" ? "waveform" : "point observation"} · synthetic values`;
  if (!artifact || !artifact.result) {
    byId("viewer-content").innerHTML = `<section class="panel viewer-error"><h2>Study unavailable</h2><p>The authority did not return a released artifact for this attempt.</p><button class="secondary-button" data-action="return-viewer">Back to investigations</button></section>`;
    return;
  }
  const result = artifact.result;
  const capturedAt = result.collected_at_ms;
  const releasedAt = result.released_at_ms;
  const trace = result.samples ? result.samples : null;
  const mainResult = trace
    ? `<div class="trace-viewer"><div class="trace-plot">${traceSvg(trace, result.units || "fixture-unit")}</div><div class="trace-text"><span class="eyebrow">TEXT EQUIVALENT</span><p>Samples: <strong>${trace.map((value) => escapeHtml(value)).join(", ")}</strong> ${escapeHtml(result.units || "fixture-unit")}</p><p>Sample offsets: <strong>${(result.sample_offsets || [0, 1, 2].slice(0, trace.length)).join(", ")}</strong> ms</p></div></div>`
    : `<div class="scalar-result"><span class="scalar-mark" aria-hidden="true">●</span><span class="scalar-value">${escapeHtml(result.value)}</span><span class="scalar-unit">${escapeHtml(result.units || "fixture-unit")}</span></div>`;
  const pointCompare = artifact.kind === "point" ? renderCompareControls(itemId) : `<div class="compare-note"><span aria-hidden="true">↗</span><p>No compatible earlier point measurement is available for this trace. Compare only studies with matching type and units.</p></div>`;
  const targetOptions = ["general", ...state.differential].map((target) => `<option value="${escapeHtml(target)}">${target === "general" ? "General reasoning" : `Hypothesis ${escapeHtml(target)}`}</option>`).join("");
  const backLabel = state.viewerOrigin === "diagnosis" ? "Back to diagnosis" : "Back to investigations";
  byId("viewer-back-label").textContent = backLabel;
  byId("viewer-content").innerHTML = `<div class="viewer-main"><section class="panel artifact-panel"><div class="artifact-panel-head"><div><p class="eyebrow">FIXTURE RESULT · ${escapeHtml(itemId)}</p><h2>${escapeHtml(title)}</h2></div><span class="quality-pill">${escapeHtml(result.quality || "valid")} quality</span></div><div class="artifact-plot">${mainResult}</div><div class="provenance-strip"><div><span>ACQUIRED</span><strong>${formatPrecise(capturedAt)}</strong></div><div><span>RELEASED</span><strong>${formatPrecise(releasedAt)}</strong></div><div><span>UNITS</span><strong>${escapeHtml(result.units || "fixture-unit")}</strong></div><div><span>METHOD</span><strong>${escapeHtml(result.provenance?.investigation_version || "Fixture-A v1")}</strong></div></div><div class="fixture-disclaimer"><span aria-hidden="true">i</span><p>All values are synthetic fixture output. They are not clinical measurements or recommendations.</p></div></section>${pointCompare}<section class="panel cite-panel"><div><p class="eyebrow">EVIDENCE-TO-REASONING</p><h2>Cite in reasoning</h2><p>Choose a destination. The citation is inserted as editable text in the diagnosis draft.</p></div><div class="cite-controls"><label for="citation-target">Associate with</label><select id="citation-target">${targetOptions}</select><button class="primary-button" data-action="cite-result">Cite in reasoning <span aria-hidden="true">↗</span></button></div><div class="cite-confirmation" id="cite-confirmation" aria-live="polite"></div></section></div><aside class="viewer-side"><section class="panel study-info"><p class="eyebrow">STUDY DETAILS</p><h2>Attempt-scoped evidence</h2><div class="detail-row"><span>Attempt</span><strong>${escapeHtml(attemptName())}</strong></div><div class="detail-row"><span>Clinical time now</span><strong>${formatPrecise(state.projection.elapsed_ms)}</strong></div><div class="detail-row"><span>Opened at</span><strong>${formatPrecise(state.projection.elapsed_ms)}</strong></div><div class="detail-row"><span>Source</span><strong>Fixture authority</strong></div><div class="panel-divider"></div><p class="helper-copy">Opening and reading this study do not advance clinical time.</p></section><section class="panel viewer-next"><p class="eyebrow">NEXT STEP</p><h2>Use this finding</h2><p>Add the released result to a diagnosis hypothesis or to general reasoning.</p><button class="secondary-button full-width" data-screen="diagnosis">Open diagnosis draft <span aria-hidden="true">→</span></button></section></aside>`;
  if (state.viewerCompare) renderCompareResult();
}

function traceSvg(values, units) {
  const width = 600;
  const height = 240;
  const left = 58;
  const right = 20;
  const top = 24;
  const bottom = 45;
  const min = Math.min(...values) - 0.35;
  const max = Math.max(...values) + 0.35;
  const x = (index) => left + (values.length === 1 ? 0 : index * (width - left - right) / (values.length - 1));
  const y = (value) => top + (max - value) * (height - top - bottom) / (max - min || 1);
  const points = values.map((value, index) => `${x(index)},${y(value)}`).join(" ");
  const circles = values.map((value, index) => `<circle cx="${x(index)}" cy="${y(value)}" r="6" fill="#66d2c1" stroke="#071522" stroke-width="3"><title>Sample ${index + 1}: ${escapeHtml(value)} ${escapeHtml(units)} at ${index} milliseconds</title></circle>`).join("");
  const yLabels = [min + 0.35, max - 0.35].map((value) => `<text x="${left - 12}" y="${y(value) + 4}" text-anchor="end">${escapeHtml(value)}</text>`).join("");
  const xLabels = values.map((_, index) => `<text x="${x(index)}" y="${height - 15}" text-anchor="middle">${index} ms</text>`).join("");
  return `<svg viewBox="0 0 ${width} ${height}" role="img" aria-labelledby="trace-svg-title trace-svg-desc"><title id="trace-svg-title">Synthetic trace study</title><desc id="trace-svg-desc">${values.map((value, index) => `At ${index} milliseconds: ${value} ${units}`).join(". ")}</desc><g class="grid-line"><line x1="${left}" y1="${top}" x2="${left}" y2="${height - bottom}"/><line x1="${left}" y1="${height - bottom}" x2="${width - right}" y2="${height - bottom}"/><line x1="${left}" y1="${top}" x2="${width - right}" y2="${top}"/></g><g class="axis-label">${yLabels}${xLabels}<text x="18" y="${top}" transform="rotate(-90 18 ${top})">${escapeHtml(units)}</text></g><polyline points="${points}" fill="none" stroke="#66d2c1" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>${circles}</svg>`;
}

function renderCompareControls(currentId) {
  const candidates = Object.keys(releasedResults()).filter((id) => id !== currentId && ["A", "B", "C"].includes(id));
  if (!candidates.length) return `<div class="compare-note"><span aria-hidden="true">↗</span><p>No other released point reading in this attempt. The fixture has no earlier compatible observation yet.</p></div>`;
  return `<section class="panel compare-panel"><div class="panel-head"><div><p class="eyebrow">COMPATIBLE POINT STUDIES</p><h2>Compare measurements</h2></div><span class="step-chip">Same attempt</span></div><p class="panel-intro">Select another released point result. Matching type and units permit comparison; timestamps determine whether it is a prior trend.</p><div class="compare-controls"><label for="compare-study">Compare with</label><select id="compare-study">${candidates.map((id) => `<option value="${escapeHtml(id)}">${escapeHtml(itemTitle(id))}</option>`).join("")}</select><button class="secondary-button" data-action="compare-study">Compare</button></div><div id="compare-result" class="compare-result" aria-live="polite"></div></section>`;
}

async function renderCompareResult() {
  const target = byId("compare-result");
  if (!target || !state.viewerCompare || !state.viewer) return;
  const { itemId, otherId, otherAsset } = state.viewerCompare;
  const current = state.viewer.artifact.result;
  const other = otherAsset?.result;
  if (!other || current.units !== other.units) {
    target.innerHTML = `<p class="compare-warning">These readings do not have matching units and cannot be compared.</p>`;
    return;
  }
  const sameTime = current.collected_at_ms === other.collected_at_ms;
  target.innerHTML = `<div class="compare-values"><div><span>${escapeHtml(itemId)} · ${formatPrecise(current.collected_at_ms)}</span><strong>${escapeHtml(current.value)} ${escapeHtml(current.units)}</strong></div><span class="compare-mark" aria-hidden="true">↔</span><div><span>${escapeHtml(otherId)} · ${formatPrecise(other.collected_at_ms)}</span><strong>${escapeHtml(other.value)} ${escapeHtml(other.units)}</strong></div></div><p class="compare-warning">${sameTime ? "Same-time observations. This comparison does not show a trend." : `Earlier point measurement: ${escapeHtml(otherId)} was acquired at ${formatPrecise(other.collected_at_ms)}.`}</p>`;
}

function renderDiagnosis() {
  if (!state.projection) return;
  const list = state.differential.filter((item) => ["DX-A", "DX-B"].includes(item));
  byId("differential-list").innerHTML = list.map((hypothesis, index) => `<li class="differential-item"><span class="rank-number">${index + 1}</span><span class="hypothesis-label">${escapeHtml(hypothesis)}</span><div class="rank-controls"><button class="rank-button" data-action="rank-up" data-hypothesis="${escapeHtml(hypothesis)}" aria-label="Move ${escapeHtml(hypothesis)} up" ${index === 0 || isComplete() ? "disabled" : ""}>↑</button><button class="rank-button" data-action="rank-down" data-hypothesis="${escapeHtml(hypothesis)}" aria-label="Move ${escapeHtml(hypothesis)} down" ${index === list.length - 1 || isComplete() ? "disabled" : ""}>↓</button></div></li>`).join("");
  const reasoning = byId("reasoning-input");
  if (document.activeElement !== reasoning) reasoning.value = state.reasoning;
  reasoning.disabled = isComplete();
  byId("reasoning-count").textContent = `${state.reasoning.length} / 2,000`;
  const evidence = Object.entries(releasedResults());
  byId("evidence-list").innerHTML = evidence.length ? evidence.map(([id, result]) => `<button id="view-evidence-${escapeHtml(id)}" class="evidence-item" data-view-item="${escapeHtml(id)}"><span class="evidence-code">${escapeHtml(id)}</span><span class="evidence-copy"><strong>${escapeHtml(itemTitle(id))}</strong><small>${result.samples ? `${result.samples.join(" · ")} ${escapeHtml(result.units || "")}` : `${escapeHtml(result.value)} ${escapeHtml(result.units || "")}`} · released ${formatClock(result.released_at_ms)}</small></span><span aria-hidden="true">↗</span></button>`).join("") : `<div class="evidence-empty"><span aria-hidden="true">⌁</span><p>No released evidence is available to cite.</p><button class="quiet-button" data-screen="investigations">Open investigations</button></div>`;
  byId("review-submission").disabled = isComplete();
}

function renderSubmission() {
  if (!state.projection) return;
  const leading = state.differential[0] || "Not selected";
  byId("review-leading").textContent = leading;
  byId("review-differential").innerHTML = state.differential.map((item, index) => `<div class="review-rank-row"><span class="rank-number">${index + 1}</span><strong>${escapeHtml(item)}</strong>${index === 0 ? `<span class="leader-tag">LEADING</span>` : ""}</div>`).join("");
  byId("review-reasoning").textContent = state.reasoning.trim() || "No reasoning text supplied.";
  byId("review-evidence").innerHTML = Object.entries(releasedResults()).map(([id, result]) => `<span class="citation-chip">${escapeHtml(id)} · ${result.samples ? `${result.samples.join("–")}` : result.value} ${escapeHtml(result.units || "")}</span>`).join("");
  const clock = formatClock(state.projection.elapsed_ms);
  byId("review-clock").textContent = clock;
  byId("confirm-time").textContent = clock;
  const rows = Object.values(activeOrders());
  byId("closeout-list").innerHTML = rows.length ? rows.map((order) => {
    const disposition = order.status === "released" ? "Retained in frozen history" : `Will close from ${statusLabel(order.status).toLowerCase()}`;
    return `<div class="closeout-row"><span class="closeout-symbol ${order.status === "released" ? "keep-symbol" : "close-symbol"}" aria-hidden="true">${order.status === "released" ? "✓" : "×"}</span><div><strong>${escapeHtml(itemTitle(order.item_id))}</strong><small>${escapeHtml(disposition)}</small></div><span class="status-pill ${statusClass(order.status)}">${escapeHtml(statusLabel(order.status))}</span></div>`;
  }).join("") : `<p class="helper-copy">No committed orders to close.</p>`;
  byId("submit-final").disabled = isComplete() || Boolean(state.pendingOrder || state.draftConflict);
}

function renderDebrief() {
  if (!state.projection || !isComplete()) return;
  const submission = activeData().submission;
  if (!submission) return;
  byId("frozen-leading").textContent = submission.leading_diagnosis;
  byId("frozen-differential").innerHTML = (submission.differential || []).map((item, index) => `<div class="review-rank-row"><span class="rank-number">${index + 1}</span><strong>${escapeHtml(item)}</strong>${index === 0 ? `<span class="leader-tag">LEADING</span>` : ""}</div>`).join("");
  byId("frozen-reasoning").textContent = submission.reasoning || "No reasoning text was submitted.";
  byId("frozen-meta").innerHTML = `<span>Submitted ${formatPrecise(submission.submitted_at_ms)}</span><span>Evidence cutoff ${formatPrecise(submission.evidence_cutoff_ms)}</span><span>Clock unchanged after closeout</span>`;
  byId("debrief-panel").hidden = state.debriefState === "unavailable";
  byId("debrief-unavailable").hidden = state.debriefState !== "unavailable";
  byId("closeout-summary").innerHTML = Object.values(activeOrders()).map((order) => `<div class="closeout-summary-row"><span>${escapeHtml(order.item_id)}</span><span class="status-pill ${statusClass(order.status)}">${escapeHtml(statusLabel(order.status))}</span>${order.pre_close_state ? `<small>Before closeout: ${escapeHtml(statusLabel(order.pre_close_state))}</small>` : ""}</div>`).join("") || `<p class="helper-copy">No investigations were ordered.</p>`;
  const review = activeData().review;
  const feedbackDone = review && ["submitted", "skipped"].includes(review.status);
  byId("feedback-panel").classList.toggle("feedback-complete", Boolean(feedbackDone));
  if (feedbackDone) {
    byId("feedback-status").textContent = review.status === "submitted" ? `Feedback saved · ${review.rating}/5${review.comment ? ` · “${review.comment}”` : ""}` : "Feedback skipped. This prompt will not return for this attempt.";
    $$("#feedback-panel input, #feedback-panel textarea, #feedback-panel button[data-rating], #feedback-panel button[data-action]").forEach((element) => { element.disabled = true; });
  } else {
    byId("feedback-status").textContent = "";
    $$("#feedback-panel input, #feedback-panel textarea, #feedback-panel button[data-rating], #feedback-panel button[data-action]").forEach((element) => { element.disabled = false; });
    byId("submit-feedback").disabled = state.selectedRating < 1;
  }
  if (state.debrief) renderDebriefContent(state.debrief);
  else if (state.debriefState === "loading") byId("debrief-content").innerHTML = `<div class="loading-row"><span class="spinner"></span><span>Loading the authorized synthetic assessment…</span></div>`;
  else byId("debrief-content").innerHTML = `<p class="helper-copy">The submitted snapshot is saved separately from this assessment.</p>`;
}

function renderDebriefContent(debrief) {
  const dimensions = Object.entries(debrief.dimensions || {});
  const evidence = debrief.key_evidence || [];
  byId("debrief-content").innerHTML = `<div class="dimension-grid">${dimensions.map(([name, value]) => `<div class="dimension-card"><span class="eyebrow">${escapeHtml(name.replaceAll("_", " "))}</span><strong>${escapeHtml(value.status || value.evidence_link || "Recorded")}</strong>${value.uncertainty ? `<small>Uncertainty: ${escapeHtml(value.uncertainty)}</small>` : ""}</div>`).join("")}</div><div class="debrief-evidence"><p class="eyebrow">CUTOFF-AUTHORIZED FIXTURE EVIDENCE</p>${evidence.length ? evidence.map((item) => `<div class="debrief-evidence-row"><span class="evidence-code">${escapeHtml(item.item_id)}</span><span>${escapeHtml(item.observation)}</span><span class="quality-pill">${escapeHtml(item.quality || "valid")}</span></div>`).join("") : `<p>No released evidence was available at submission.</p>`}</div>${(debrief.valid_alternative_reasoning || []).map((item) => `<p class="alternative-note">${escapeHtml(item)}</p>`).join("")}<p class="fixture-note">This is a software fixture rubric, not clinical grading.</p>`;
}

function renderHelp() {
  if (!state.bootstrap) return;
  const dialogue = byId("dialogue-scenario");
  const orderResponse = byId("order-response-scenario");
  const debrief = byId("debrief-scenario");
  if (dialogue && document.activeElement !== dialogue) dialogue.value = state.bootstrap.dialogue_outcome;
  if (orderResponse && document.activeElement !== orderResponse) orderResponse.value = state.bootstrap.order_response_failure || "none";
  if (debrief && document.activeElement !== debrief) debrief.checked = state.bootstrap.debrief_unavailable;
}

function renderQaDrawer() {
  if (!state.bootstrap) return;
  const orders = activeOrders();
  const tPending = orders.T && !releasedResults().T && !isComplete();
  const canProbeClosed = isComplete();
  const parts = [];
  parts.push(`<div class="qa-status">Mode: <strong>local synthetic</strong> · actor scopes enforced by Gate A · clinical time ${formatPrecise(state.projection?.elapsed_ms || 0)}</div>`);
  if (state.attemptId && tPending) {
    parts.push(`<div class="qa-control"><div><strong>Manual release for T</strong><small>Authority action in the fixture harness; not a player command.</small></div><button class="secondary-button qa-button" data-action="release-fixture">Release prepared study T</button></div>`);
  }
  if (canProbeClosed) {
    parts.push(`<div class="qa-control"><div><strong>Post-submission clock check</strong><small>Send a synthetic wait after closeout and confirm the frozen clock.</small></div><button class="secondary-button qa-button" data-action="probe-post-submit">Attempt 1-second wait</button></div>`);
  }
  parts.push(`<div class="qa-control qa-note"><div><strong>Provider and case boundaries</strong><small>No external model, credentials, real patient context, or clinical assets are used.</small></div><a href="WALKTHROUGH.md" target="_blank" rel="noreferrer">Walkthrough notes ↗</a></div>`);
  byId("qa-content").innerHTML = parts.join("");
}

async function loadDebrief() {
  if (!state.attemptId || !isComplete()) return;
  state.debriefState = "loading";
  render();
  try {
    const response = await api(`/api/debrief?attempt_id=${encodeURIComponent(state.attemptId)}`);
    state.debrief = response.debrief;
    state.debriefState = "ready";
  } catch (error) {
    state.debrief = null;
    state.debriefState = error.status === 503 ? "unavailable" : "error";
    if (state.debriefState === "error") toast("The debrief could not be loaded. Your frozen submission remains saved.", "warning");
  }
  render();
}

async function generateCase() {
  try {
    const result = await api("/api/generate", { method: "POST", body: "{}" });
    await refreshBootstrap({ keepPage: true });
    toast(result.status === "already_published" ? "Fixture-A is already in the local library." : "Fixture-A was published to the local library.", "success");
  } catch (error) { toast(error.message || "Could not publish the fixture.", "error"); }
}

async function startAttempt() {
  try {
    const result = await api("/api/attempts", { method: "POST", body: "{}" });
    if (result.receipt.status !== "committed") {
      toast(`Could not start attempt: ${result.receipt.status.replaceAll("_", " ")}.`, "error");
      return;
    }
    state.bootstrap = await api("/api/bootstrap");
    state.attemptId = result.projection.target_id;
    state.projection = result.projection;
    state.viewer = null;
    state.debrief = null;
    state.debriefState = "idle";
    state.selectedOrders = new Set(["A", "T", "C"]);
    state.orderReview = false;
    state.differential = ["DX-A", "DX-B"];
    state.reasoning = "";
    state.questionDraft = "How many episodes do you remember?";
    state.dialogueBlocked = false;
    state.page = "encounter";
    restoreDraft(state.attemptId);
    history.replaceState(null, "", `?attempt=${encodeURIComponent(state.attemptId)}`);
    render();
    toast(`Started Patient 04 · Attempt ${activeAttemptNumber()} at 00:00.`, "success");
    byId("main-content").focus({ preventScroll: true });
  } catch (error) { toast(error.message || "Could not start the encounter.", "error"); }
}

async function placeOrders() {
  if (state.pendingOrder) {
    toast("Resolve the saved order request before placing another order.", "warning");
    return;
  }
  const current = activeOrders();
  const items = [...state.selectedOrders].filter((id) => !current[id]).map((id) => ({ item_id: id, kind: CASE_ITEMS.find((item) => item.id === id).kind }));
  if (!items.length) {
    state.orderReview = false;
    render();
    toast("No new orders to place.", "warning");
    return;
  }
  const pending = {
    attempt_id: state.attemptId,
    command_id: `ui-order-${crypto.randomUUID()}`,
    expected_revision: state.projection.revision,
    kind: "order_tests",
    payload: { items },
  };
  if (!persistPendingOrder(pending)) {
    toast("The recovery record could not be saved, so the order was not sent.", "error");
    return;
  }
  state.orderReview = false;
  state.recoveryMessage = "Sending the saved order request.";
  render();
  try {
    const result = await runCommand("order_tests", pending.payload, { commandId: pending.command_id, expectedRevision: pending.expected_revision });
    if (result.receipt.status === "idempotency_conflict") {
      state.recoveryMessage = "The authority found a different payload for this request identity. Keep it unresolved and check with the local authority.";
      render();
      toast("Order identity conflict. The saved request remains available for recovery.", "error");
      return;
    }
    clearPendingOrder();
    render();
    if (result.receipt.status === "committed") toast("Orders committed at the current clinical time. The clock did not move.", "success");
    else toast(`Order not committed: ${result.receipt.status.replaceAll("_", " ")}.`, "warning");
  } catch (error) {
    if (error instanceof ApiError && error.status > 0 && error.status < 500) {
      clearPendingOrder();
      state.orderReview = true;
      render();
      toast(`Order was rejected before commit: ${error.message}. The selected queue is still available.`, "warning");
      return;
    }
    state.recoveryMessage = "Order outcome unknown. Check the current authority projection or retry this exact saved request.";
    render();
    toast("Order outcome unknown. Your request is saved for recovery.", "warning");
  }
}

async function checkOrderRecovery({ automatic = false } = {}) {
  const pending = state.pendingOrder;
  if (!pending || state.recoveryCheckInProgress) return;
  state.recoveryCheckInProgress = true;
  state.recoveryMessage = "Checking whether this order request was saved.";
  renderDraftStatus();
  try {
    const projection = await api(`/api/projection?attempt_id=${encodeURIComponent(pending.attempt_id)}`);
    if (pending.attempt_id !== state.attemptId) return;
    state.projection = projection;
    const orders = projection.data?.orders || {};
    const committed = pending.payload.items.every((item) => Boolean(orders[item.item_id]));
    if (committed) {
      clearPendingOrder();
      render();
      toast("Recovered the committed order from the authority. It was applied once.", "success");
      return;
    }
    state.recoveryMessage = "Outcome unknown. No matching order is visible yet; use Retry same order to resolve the saved request safely.";
    render();
    if (!automatic) toast("The order is still unresolved. The request was not resent.", "warning");
  } catch {
    state.recoveryMessage = "Recovery check unavailable. The request remains unresolved and has not been resent.";
    renderDraftStatus();
    if (!automatic) toast("Could not check the authority. The saved request remains unresolved.", "warning");
  } finally {
    state.recoveryCheckInProgress = false;
  }
}

async function retryOrderRecovery() {
  const pending = state.pendingOrder;
  if (!pending) return;
  state.recoveryMessage = "Retrying the same saved request identity and payload.";
  renderDraftStatus();
  try {
    const result = await runCommand(pending.kind, pending.payload, {
      commandId: pending.command_id,
      expectedRevision: pending.expected_revision,
    });
    if (result.receipt.status === "idempotency_conflict") {
      state.recoveryMessage = "The authority found a different payload for this request identity. The request remains unresolved.";
      render();
      toast("Retry was blocked by an identity conflict.", "error");
      return;
    }
    clearPendingOrder();
    render();
    toast(result.receipt.status === "committed"
      ? "Same-intent retry resolved the order. The authority applied it once."
      : `The authority confirmed ${result.receipt.status.replaceAll("_", " ")}; review the current order tray before creating a new request.`,
    result.receipt.status === "committed" ? "success" : "warning");
  } catch {
    state.recoveryMessage = "Retry response unavailable. The original request identity remains saved; check status or retry again.";
    render();
    toast("Same-intent retry did not resolve the outcome. Your request remains saved.", "warning");
  }
}

async function waitClinicalTime() {
  const duration = Number(byId("wait-duration").value);
  try {
    const result = await runCommand("wait", { duration_ms: duration });
    if (result.receipt.status === "committed") toast(`Clinical time advanced to ${formatClock(state.projection.elapsed_ms)}.`, "success");
  } catch (error) { toast(error.message || "Could not advance the clock.", "error"); }
}

async function releaseFixture() {
  try {
    const result = await api("/api/fixture/release", {
      method: "POST",
      body: JSON.stringify({ attempt_id: state.attemptId, item_id: "T", expected_revision: state.projection.revision }),
    });
    state.projection = result.projection;
    render();
    toast(result.receipt.status === "committed" ? "Fixture authority released study T." : `Release not committed: ${result.receipt.status.replaceAll("_", " ")}.`, result.receipt.status === "committed" ? "success" : "warning");
  } catch (error) { toast(error.message || "Fixture release failed.", "error"); }
}

async function openViewer(itemId) {
  if (!releasedResults()[itemId]) {
    toast("This result has not been released to the active attempt.", "warning");
    return;
  }
  state.viewerOrigin = state.page === "viewer" ? state.viewerOrigin : state.page;
  const invoker = document.activeElement?.closest?.("[data-view-item]");
  state.viewerInvokerId = invoker?.id || `view-order-${itemId}`;
  state.viewerScrollY = window.scrollY;
  try {
    const opened = await runCommand("open_artifact", { item_id: itemId }, { quiet: true });
    if (opened.receipt.status !== "committed") {
      toast(`Study could not be opened: ${opened.receipt.status.replaceAll("_", " ")}.`, "warning");
      return;
    }
    const response = await api(`/api/asset?attempt_id=${encodeURIComponent(state.attemptId)}&item_id=${encodeURIComponent(itemId)}&asset_id=primary`);
    if (response.status !== "available") {
      toast(`Study artifact is ${response.status.replaceAll("_", " ")}.`, "warning");
      return;
    }
    const item = CASE_ITEMS.find((entry) => entry.id === itemId);
    state.viewer = { itemId, kind: item?.kind, artifact: { kind: item?.kind, result: releasedResults()[itemId], representation: response.artifact } };
    state.viewerCompare = null;
    setScreen("viewer", { focus: true });
  } catch (error) { toast(error.message || "Could not open this study.", "error"); }
}

async function compareStudy() {
  const otherId = byId("compare-study")?.value;
  if (!otherId || !state.viewer) return;
  try {
    const result = await api(`/api/asset?attempt_id=${encodeURIComponent(state.attemptId)}&item_id=${encodeURIComponent(otherId)}&asset_id=primary`);
    if (result.status !== "available") {
      toast(`Comparison is ${result.status}.`, "warning");
      return;
    }
    state.viewerCompare = { itemId: state.viewer.itemId, otherId, otherAsset: { result: releasedResults()[otherId], representation: result.artifact } };
    renderViewer();
  } catch (error) { toast(error.message || "Could not compare these studies.", "error"); }
}

function makeCitation(itemId, result, target) {
  const prefix = target === "general" ? "" : `For hypothesis ${target}, `;
  const stamp = `acquired ${formatPrecise(result.collected_at_ms)}, released ${formatPrecise(result.released_at_ms)}`;
  if (Array.isArray(result.samples) && result.samples.length >= 2) {
    const offsets = result.sample_offsets || [0, 1, 2].slice(0, result.samples.length);
    return `${prefix}the trace rose from ${result.samples[0]} to ${result.samples[1]} ${result.units || "fixture-unit"} across ${offsets[1] ?? 1} ms in study ${itemId} (${stamp}).`;
  }
  return `${prefix}point sample was ${result.value} ${result.units || "fixture-unit"} in ${itemId} (${stamp}).`;
}

function citeResult() {
  if (!state.viewer?.artifact?.result) return;
  const target = byId("citation-target").value;
  const citation = makeCitation(state.viewer.itemId, state.viewer.artifact.result, target);
  const separator = state.reasoning.trim() ? "\n" : "";
  state.reasoning = `${state.reasoning}${separator}${citation}`;
  saveDraft();
  const confirmation = byId("cite-confirmation");
  if (confirmation) confirmation.textContent = `Citation inserted into the editable reasoning draft${target === "general" ? "." : ` for ${target}.`}`;
  toast("Citation inserted. Review or edit it in the diagnosis draft.", "success");
  renderDiagnosis();
}

async function showSubmissionReview() {
  if (!state.differential.length) {
    toast("Add at least one hypothesis before reviewing submission.", "warning");
    return;
  }
  saveDraft();
  setScreen("submission", { focus: true });
}

async function submitFinal() {
  if (!state.projection || isComplete()) return;
  const snapshot = {
    leading_diagnosis: state.differential[0],
    differential: [...state.differential],
    reasoning: state.reasoning.trim() || null,
  };
  const commandId = `prototype-submit-${state.attemptId}`;
  byId("submit-final").disabled = true;
  try {
    const result = await runCommand("submit_diagnosis", snapshot, { commandId, quiet: true });
    if (result.receipt.status !== "committed" && !result.receipt.replayed) {
      byId("submit-final").disabled = false;
      toast(`Submission not committed: ${result.receipt.status.replaceAll("_", " ")}. Review the latest attempt before trying again.`, "warning");
      if (result.receipt.status === "revision_conflict") setScreen("diagnosis");
      return;
    }
    state.bootstrap = await api("/api/bootstrap");
    state.page = "debrief";
    state.debrief = null;
    state.debriefState = "idle";
    render();
    toast("Submission saved. The encounter is closed at the reviewed clock time.", "success");
    void loadDebrief();
  } catch (error) {
    byId("submit-final").disabled = false;
    toast(error.message || "The submission response is unavailable. The reviewed snapshot remains on screen.", "error");
  }
}

async function applyScenario() {
  try {
    const result = await api("/api/prototype/scenario", {
      method: "POST",
      body: JSON.stringify({
        dialogue_outcome: byId("dialogue-scenario").value,
        order_response_failure: byId("order-response-scenario").value,
        debrief_unavailable: byId("debrief-scenario").checked,
      }),
    });
    state.bootstrap.dialogue_outcome = result.dialogue_outcome;
    state.bootstrap.order_response_failure = result.order_response_failure;
    state.bootstrap.debrief_unavailable = result.debrief_unavailable;
    render();
    toast("Synthetic walkthrough scenario updated.", "success");
  } catch (error) { toast(error.message || "Could not update the local scenario.", "error"); }
}

async function saveFeedback() {
  if (state.selectedRating < 1) return;
  try {
    const result = await runCommand("review_case", {
      rating: state.selectedRating,
      comment: byId("feedback-input").value.trim(),
    }, { quiet: true });
    if (result.receipt.status === "committed") toast("Feedback saved separately from the frozen submission.", "success");
  } catch (error) { toast(error.message || "Feedback could not be saved.", "error"); }
}

async function skipFeedback() {
  try {
    const result = await runCommand("skip_review", {}, { quiet: true });
    if (result.receipt.status === "committed") toast("Feedback skipped for this attempt.", "success");
  } catch (error) { toast(error.message || "Could not record Skip.", "error"); }
}

async function probePostSubmit() {
  const before = state.projection.elapsed_ms;
  try {
    const result = await runCommand("wait", { duration_ms: 1000 }, { quiet: true });
    const after = result.projection.elapsed_ms;
    toast(result.receipt.status === "encounter_complete" && before === after
      ? `Confirmed: post-submission wait was rejected; clinical time stayed at ${formatClock(after)}.`
      : `Unexpected closeout probe result: ${result.receipt.status}. Time ${formatClock(before)} → ${formatClock(after)}.`,
    result.receipt.status === "encounter_complete" && before === after ? "success" : "error");
  } catch (error) { toast(error.message || "Closeout probe could not run.", "error"); }
}

document.addEventListener("click", async (event) => {
  const screenButton = event.target.closest("[data-screen]");
  if (screenButton) {
    event.preventDefault();
    setScreen(screenButton.dataset.screen, { focus: true });
    return;
  }
  const attemptButton = event.target.closest("[data-attempt-id]");
  if (attemptButton) { await selectAttempt(attemptButton.dataset.attemptId); return; }
  const viewButton = event.target.closest("[data-view-item]");
  if (viewButton) { await openViewer(viewButton.dataset.viewItem); return; }
  const ratingButton = event.target.closest("[data-rating]");
  if (ratingButton) {
    state.selectedRating = Number(ratingButton.dataset.rating);
    $$("[data-rating]").forEach((button) => button.classList.toggle("selected", Number(button.dataset.rating) <= state.selectedRating));
    byId("rating-label").textContent = `${state.selectedRating} out of 5 selected`;
    byId("submit-feedback").disabled = false;
    return;
  }
  const action = event.target.closest("[data-action]")?.dataset.action;
  if (!action) return;
  switch (action) {
    case "dismiss-banner": state.bannerDismissed = true; render(); break;
    case "generate-case": await generateCase(); break;
    case "start-attempt":
    case "start-replay": await startAttempt(); break;
    case "continue-active": {
      const currentId = state.bootstrap.current_attempt_id;
      if (currentId) await selectAttempt(currentId);
      break;
    }
    case "open-latest": {
      const latest = [...(state.bootstrap.attempts || [])].reverse()[0];
      if (latest) await selectAttempt(latest.playthrough_id);
      break;
    }
    case "continue-encounter": setScreen(isComplete() ? "debrief" : "encounter", { focus: true }); break;
    case "toggle-help": setScreen("help", { focus: true }); break;
    case "close-help": setScreen(state.projection ? (isComplete() ? "debrief" : "encounter") : "home", { focus: true }); break;
    case "refresh": await refreshBootstrap(); toast("Attempt projection refreshed.", "success"); break;
    case "review-orders": state.orderReview = true; render(); byId("order-review-panel").scrollIntoView({ behavior: "smooth", block: "center" }); break;
    case "cancel-order-review": state.orderReview = false; render(); break;
    case "place-orders": await placeOrders(); break;
    case "wait": await waitClinicalTime(); break;
    case "return-viewer": {
      const returnPage = state.viewerOrigin || "investigations";
      const invokerId = state.viewerInvokerId;
      const scrollY = state.viewerScrollY;
      state.viewer = null;
      state.viewerCompare = null;
      setScreen(returnPage, { focus: false });
      requestAnimationFrame(() => {
        window.scrollTo(0, scrollY);
        const invoker = invokerId ? byId(invokerId) : null;
        invoker?.focus({ preventScroll: true });
      });
      break;
    }
    case "compare-study": await compareStudy(); break;
    case "cite-result": citeResult(); break;
    case "rank-up": {
      const index = state.differential.indexOf(event.target.closest("[data-hypothesis]")?.dataset.hypothesis);
      if (index > 0) [state.differential[index - 1], state.differential[index]] = [state.differential[index], state.differential[index - 1]];
      saveDraft(); renderDiagnosis(); break;
    }
    case "rank-down": {
      const index = state.differential.indexOf(event.target.closest("[data-hypothesis]")?.dataset.hypothesis);
      if (index >= 0 && index < state.differential.length - 1) [state.differential[index + 1], state.differential[index]] = [state.differential[index], state.differential[index + 1]];
      saveDraft(); renderDiagnosis(); break;
    }
    case "restore-newer-draft": {
      if (!state.draftConflict) break;
      const newer = state.draftConflict;
      applyDraft(newer);
      state.draftVersion = Number(newer._draft_revision) || state.draftVersion;
      state.draftHasLocalChanges = false;
      state.draftConflict = null;
      state.draftSaveStatus = "Newer saved draft restored.";
      render();
      toast("The newer draft was restored from the other tab.", "success");
      break;
    }
    case "save-my-draft": {
      if (!state.draftConflict) break;
      const latest = readDraft(state.attemptId);
      const latestVersion = Number(latest?._draft_revision) || Number(state.draftConflict._draft_revision) || state.draftVersion;
      const own = {
        reasoning: state.reasoning,
        differential: state.differential,
        questionDraft: state.questionDraft,
        selectedOrders: [...state.selectedOrders],
        _draft_revision: latestVersion + 1,
      };
      try {
        localStorage.setItem(draftKey(), JSON.stringify(own));
        state.draftVersion = own._draft_revision;
        state.draftHasLocalChanges = true;
        state.draftConflict = null;
        state.draftSaveStatus = "Your draft was saved as the newest copy.";
        render();
        toast("Your draft was saved as the newest copy.", "success");
      } catch {
        state.draftSaveStatus = "Draft not saved · your edits remain in this tab.";
        renderDraftStatus();
      }
      break;
    }
    case "check-order-recovery": await checkOrderRecovery(); break;
    case "retry-order-recovery": await retryOrderRecovery(); break;
    case "review-submission": await showSubmissionReview(); break;
    case "submit-final": await submitFinal(); break;
    case "retry-debrief": await loadDebrief(); break;
    case "save-scenario": await applyScenario(); break;
    case "submit-feedback": await saveFeedback(); break;
    case "skip-feedback": await skipFeedback(); break;
    case "release-fixture": await releaseFixture(); break;
    case "probe-post-submit": await probePostSubmit(); break;
  }
});

document.addEventListener("input", (event) => {
  if (event.target.id === "question-input") { state.questionDraft = event.target.value; saveDraft(); }
  if (event.target.id === "reasoning-input") {
    state.reasoning = event.target.value;
    saveDraft();
    byId("reasoning-count").textContent = `${state.reasoning.length} / 2,000`;
  }
});

document.addEventListener("change", (event) => {
  if (event.target.matches('input[name="order-item"]')) {
    if (event.target.checked) state.selectedOrders.add(event.target.value);
    else state.selectedOrders.delete(event.target.value);
    saveDraft();
    byId("order-draft-count").textContent = `${state.selectedOrders.size} selected · no clock change on placement`;
  }
});

window.addEventListener("storage", (event) => {
  if (!state.attemptId) return;
  if (event.key === pendingOrderKey()) {
    if (event.newValue) {
      const pending = readPendingOrder(state.attemptId);
      if (pending) {
        state.pendingOrder = pending;
        state.recoveryMessage = "Another tab has an unresolved order request for this attempt.";
        render();
        announce("Another tab has an unresolved order request. Clinical changes are paused until it is resolved.");
      }
    } else if (state.pendingOrder) {
      state.pendingOrder = null;
      state.recoveryMessage = "The other tab resolved the saved request. Refreshing the latest projection.";
      void refreshBootstrap({ keepPage: true });
    }
    return;
  }
  if (event.key !== draftKey() || !event.newValue) return;
  let incoming;
  try { incoming = JSON.parse(event.newValue); } catch { return; }
  const incomingVersion = Number(incoming?._draft_revision) || 0;
  if (incomingVersion <= state.draftVersion) return;
  if (state.draftHasLocalChanges) {
    state.draftConflict = incoming;
    state.draftSaveStatus = "A newer draft was saved in another tab.";
    renderDraftStatus();
    announce("A newer draft is available in another tab. Choose which saved copy to keep.");
    return;
  }
  applyDraft(incoming);
  state.draftVersion = incomingVersion;
  state.draftHasLocalChanges = false;
  state.draftConflict = null;
  state.draftSaveStatus = "Draft updated from another tab.";
  render();
  announce("Draft updated from another tab.");
});

document.addEventListener("submit", async (event) => {
  if (event.target.id !== "talk-form") return;
  event.preventDefault();
  const question = state.questionDraft.trim();
  if (!question) { toast("Enter a question before sending.", "warning"); return; }
  const button = byId("send-question");
  button.disabled = true;
  try {
    const result = await runCommand("ask_patient", { question }, { quiet: true });
    if (result.receipt.status === "committed") {
      state.dialogueBlocked = false;
      state.questionDraft = "";
      saveDraft();
      render();
      toast("Patient reply added. Clinical time did not change.", "success");
    } else if (result.receipt.status === "dialogue_blocked") {
      state.dialogueBlocked = true;
      render();
      toast("New dialogue unavailable. Your question remains in the composer.", "warning");
    } else {
      toast(`Question not committed: ${result.receipt.status.replaceAll("_", " ")}.`, "warning");
    }
  } catch (error) {
    state.dialogueBlocked = true;
    render();
    toast(error.message || "New dialogue unavailable. Your question remains in the composer.", "warning");
  } finally {
    button.disabled = isComplete();
  }
});

async function start() {
  try {
    state.bootstrap = await api("/api/bootstrap");
    if (state.bootstrap.current_attempt_id) {
      state.attemptId = state.bootstrap.current_attempt_id;
      state.projection = await api(`/api/projection?attempt_id=${encodeURIComponent(state.attemptId)}`);
      restoreDraft(state.attemptId);
      state.page = "encounter";
    } else {
      const requested = new URLSearchParams(location.search).get("attempt");
      const prior = requested || [...state.bootstrap.attempts].reverse()[0]?.playthrough_id;
      if (prior) await selectAttempt(prior, false);
      state.page = prior ? "debrief" : "home";
    }
    render();
    if (state.page === "debrief") void loadDebrief();
    if (state.pendingOrder) void checkOrderRecovery({ automatic: true });
  } catch (error) {
    toast(`Local authority unavailable: ${error.message || "Could not connect."}`, "error");
  }
}

void start();
