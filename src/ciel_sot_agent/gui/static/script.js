"use strict";

const POLL_INTERVAL_MS = 15000;
let cachedModels = [];

async function refreshStatus() {
  try {
    const res = await fetch("/api/status");
    if (!res.ok) return;
    const data = await res.json();
    setTextIfExists("sb-mode", data.system_mode ?? "—");
    setTextIfExists("sb-backend", data.backend_status ?? "—");
    setTextIfExists("sb-coherence", fmt2(data.coherence_index));
    setTextIfExists("sb-health", fmt2(data.system_health));
    setTextIfExists("sb-energy", data.energy_budget ?? "—");

    const backendEl = document.getElementById("sb-backend");
    if (backendEl) backendEl.className = "value " + (data.backend_status === "online" ? "online" : "offline");

    const dotEl = document.getElementById("sb-dot");
    if (dotEl) dotEl.className = "dot " + (data.backend_status === "online" ? "online" : "offline");
  } catch (_) {}
}

async function refreshPanel() {
  try {
    const res = await fetch("/api/panel");
    if (!res.ok) return;
    const data = await res.json();

    const ci = data.control?.coherence_index ?? 0;
    const sh = data.control?.system_health ?? 0;

    setTextIfExists("metric-coherence", fmt2(ci));
    setTextIfExists("metric-health", fmt2(sh));
    setTextIfExists("metric-mode", data.control?.mode ?? "—");
    updateBar("bar-coherence", ci, ci < 0.5 ? "warn" : "");
    updateBar("bar-health", sh, sh < 0.5 ? "warn" : "");

    const transcript = data.communication?.transcript_preview ?? "No active session.";
    setTextIfExists("chat-transcript", transcript || "No active session.");

    renderEEG(data.control?.eeg_state ?? {});
    renderVitals(data.control?.live_vitals ?? {}, data.preferences?.live_vitals_enabled ?? true);
    hydratePreferences(data.preferences ?? {}, data);
  } catch (_) {}
}

function renderEEG(eeg) {
  const block = document.getElementById("eeg-state-block");
  if (!block) return;
  block.textContent = Object.keys(eeg).length ? JSON.stringify(eeg, null, 2) : "No EEG state available.";
}

function renderVitals(vitals, enabled) {
  const summary = document.getElementById("live-vitals-summary");
  const chart = document.getElementById("live-vitals-chart");
  if (!summary || !chart) return;
  if (!enabled) {
    summary.textContent = "Live vitals disabled in preferences.";
    chart.textContent = "";
    return;
  }
  const signals = Array.isArray(vitals.signals) ? vitals.signals : [];
  if (signals.length === 0) {
    summary.textContent = "No vital telemetry yet.";
    chart.textContent = "";
    return;
  }
  const last = signals[signals.length - 1];
  summary.textContent = `HR ${last.heart_rate_bpm} bpm | SpO2 ${last.spo2_pct}% | RR ${last.respiration_rpm} rpm`;
  chart.textContent = signals.slice(-12).map(s => `t=${s.t} | HR=${s.heart_rate_bpm} | SpO2=${s.spo2_pct} | RR=${s.respiration_rpm}`).join("\n");
}

async function refreshModels() {
  const container = document.getElementById("model-list");
  const select = document.getElementById("model-select");
  if (!container) return;
  try {
    const res = await fetch("/api/models");
    if (!res.ok) { container.textContent = "unavailable"; return; }
    const data = await res.json();
    cachedModels = data.models || [];

    if (cachedModels.length === 0) {
      container.innerHTML = `<div class="model-row"><div><div class="model-name">No models installed</div><div class="model-meta">Use Ensure Default Model.</div></div></div>`;
      if (select) select.innerHTML = `<option value="">(none)</option>`;
      return;
    }

    container.innerHTML = cachedModels.map(m => `<div class="model-row"><div><div class="model-name">${escHtml(m.name)}</div><div class="model-meta">${escHtml(m.path)}</div></div><div class="model-size">${fmtBytes(m.size_bytes)}</div></div>`).join("");
    if (select) {
      select.innerHTML = cachedModels.map(m => `<option value="${escHtml(m.name)}">${escHtml(m.name)}</option>`).join("");
    }
  } catch (_) {
    container.textContent = "error loading models";
  }
}

async function refreshControlOptions() {
  try {
    const res = await fetch('/api/control/options');
    if (!res.ok) return;
    const data = await res.json();
    fillSelect('pref-mode', data.modes || []);
    fillSelect('pref-orchestration', data.orchestration_levels || []);
    fillSelect('pref-memory', data.memory_policies || []);
  } catch (_) {}
}

function fillSelect(id, values) {
  const el = document.getElementById(id);
  if (!el) return;
  el.innerHTML = values.map(v => `<option value="${escHtml(v)}">${escHtml(v)}</option>`).join('');
}

function hydratePreferences(pref, panelData) {
  const setValue = (id, v) => { const el = document.getElementById(id); if (el && v != null) el.value = v; };
  setValue('pref-mode', pref.preferred_mode);
  setValue('pref-orchestration', pref.orchestration_level);
  setValue('pref-memory', pref.memory_retention);
  const live = document.getElementById('pref-live-vitals');
  if (live) live.checked = !!pref.live_vitals_enabled;

  const modelSelect = document.getElementById('model-select');
  if (modelSelect && pref.selected_model) modelSelect.value = pref.selected_model;
}

async function savePreferences() {
  const status = document.getElementById('pref-save-status');
  const payload = {
    selected_model: document.getElementById('model-select')?.value || null,
    preferred_mode: document.getElementById('pref-mode')?.value || 'guided',
    orchestration_level: document.getElementById('pref-orchestration')?.value || 'balanced',
    live_vitals_enabled: !!document.getElementById('pref-live-vitals')?.checked,
    memory_retention: document.getElementById('pref-memory')?.value || 'session-first',
  };

  try {
    const res = await fetch('/api/preferences', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (status) status.textContent = res.ok ? `Saved (${data.preferences?.preferred_mode ?? 'ok'})` : 'Save failed';
  } catch (_) {
    if (status) status.textContent = 'Save error';
  }
}

async function ensureDefaultModel() {
  const btn = document.getElementById("btn-ensure-model");
  const status = document.getElementById("model-ensure-status");
  if (!btn || !status) return;
  btn.disabled = true;
  status.textContent = "Downloading default model…";
  try {
    const res = await fetch("/api/models/ensure", { method: "POST" });
    const data = await res.json();
    status.textContent = (data.status || 'error') + (data.path ? `: ${data.path}` : '');
    refreshModels();
  } catch (err) {
    status.textContent = `error: ${String(err)}`;
  } finally {
    btn.disabled = false;
  }
}

function initNav() {
  document.querySelectorAll(".nav-item[data-section]").forEach(el => {
    el.addEventListener("click", () => {
      const target = el.dataset.section;
      showSection(target);
      document.querySelectorAll(".nav-item").forEach(n => n.classList.remove("active"));
      el.classList.add("active");
    });
  });
}

function showSection(id) {
  document.querySelectorAll(".ws-section").forEach(el => {
    el.style.display = el.id === "section-" + id ? "" : "none";
  });
}

function setTextIfExists(id, text) { const el = document.getElementById(id); if (el) el.textContent = text; }
function updateBar(id, value, cls) {
  const fill = document.getElementById(id);
  if (!fill) return;
  fill.style.width = (Math.min(1, Math.max(0, value)) * 100).toFixed(1) + "%";
  fill.className = "orbital-bar-fill" + (cls ? " " + cls : "");
}
function fmt2(v) { return (typeof v === "number") ? v.toFixed(2) : "—"; }
function fmtBytes(n) { if (!n) return "—"; if (n >= 1e9) return (n / 1e9).toFixed(1) + " GB"; if (n >= 1e6) return (n / 1e6).toFixed(1) + " MB"; return (n / 1e3).toFixed(0) + " KB"; }
function escHtml(s) { return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/\"/g, "&quot;"); }

document.addEventListener("DOMContentLoaded", () => {
  initNav();
  showSection("control");
  document.getElementById("btn-ensure-model")?.addEventListener("click", ensureDefaultModel);
  document.getElementById("btn-save-preferences")?.addEventListener("click", savePreferences);

  refreshControlOptions();
  refreshStatus();
  refreshPanel();
  refreshModels();

  setInterval(refreshStatus, POLL_INTERVAL_MS);
  setInterval(refreshPanel, POLL_INTERVAL_MS);
});
