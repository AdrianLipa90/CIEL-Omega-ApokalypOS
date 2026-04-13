/* CIEL Quiet Orbital Control — minimal interactive layer
   Principle: no fake telemetry, no decorative animation.
   Only purposeful, state-driven behaviour. */

"use strict";

const POLL_INTERVAL_MS = 15000;   // 15 s status poll (energy-aware)

/* -------------------------------------------------------
   Status bar refresh
   ------------------------------------------------------- */
async function refreshStatus() {
  try {
    const res = await fetch("/api/status");
    if (!res.ok) return;
    const data = await res.json();

    setTextIfExists("sb-mode",    data.system_mode   ?? "—");
    setTextIfExists("sb-backend", data.backend_status ?? "—");
    setTextIfExists("sb-coherence", fmt2(data.coherence_index));
    setTextIfExists("sb-health",    fmt2(data.system_health));
    setTextIfExists("sb-energy",    data.energy_budget ?? "—");

    const backendEl = document.getElementById("sb-backend");
    if (backendEl) {
      backendEl.className = "value " + (data.backend_status === "online" ? "online" : "offline");
    }

    const dotEl = document.getElementById("sb-dot");
    if (dotEl) {
      dotEl.className = "dot " + (data.backend_status === "online" ? "online" : "offline");
    }
  } catch (_) { /* silent — don't alarm operator on transient failure */ }
}

/* -------------------------------------------------------
   Panel data
   ------------------------------------------------------- */
async function refreshPanel() {
  try {
    const res = await fetch("/api/panel");
    if (!res.ok) return;
    const data = await res.json();

    const ci = data.control?.coherence_index ?? 0;
    const sh = data.control?.system_health   ?? 0;

    setTextIfExists("metric-coherence", fmt2(ci));
    setTextIfExists("metric-health",    fmt2(sh));
    setTextIfExists("metric-mode",      data.control?.mode ?? "—");

    updateBar("bar-coherence", ci, ci < 0.5 ? "warn" : "");
    updateBar("bar-health",    sh, sh < 0.5 ? "warn" : "");
  } catch (_) { /* silent */ }
}

/* -------------------------------------------------------
   Model manager
   ------------------------------------------------------- */
async function refreshModels() {
  const container = document.getElementById("model-list");
  if (!container) return;
  try {
    const res = await fetch("/api/models");
    if (!res.ok) { container.textContent = "unavailable"; return; }
    const data = await res.json();

    if (data.models.length === 0) {
      container.innerHTML =
        `<div class="model-row">
           <div class="model-icon">
             <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" fill="none" stroke-width="1.5">
               <circle cx="12" cy="12" r="9"/><line x1="12" y1="8" x2="12" y2="12"/>
               <line x1="12" y1="16" x2="12.01" y2="16"/>
             </svg>
           </div>
           <div>
             <div class="model-name">No models installed</div>
             <div class="model-meta">Click <em>Ensure Default Model</em> to download TinyLlama-1.1B</div>
           </div>
         </div>`;
      return;
    }

    const selected = data.selected_model || '';
    container.innerHTML = data.models.map(m =>
      `<div class="model-row">
         <div class="model-icon">
           <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" fill="none" stroke-width="1.5">
             <path d="M12 2L2 7l10 5 10-5-10-5z"/>
             <path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/>
           </svg>
         </div>
         <div>
           <div class="model-name">${escHtml(m.name)}</div>
           <div class="model-meta">${escHtml(m.path)}</div>
         </div>
         <div class="model-size">${fmtBytes(m.size_bytes)}</div>
       </div>`
    ).join("");

    const modelSelect = document.getElementById('model-select');
    if (modelSelect) {
      modelSelect.innerHTML = data.models.map(m => `<option value="${escHtml(m.name)}">${escHtml(m.name)}</option>`).join('');
      if (selected) modelSelect.value = selected;
    }
  } catch (_) {
    container.textContent = "error loading models";
  }
}

async function ensureDefaultModel() {
  const btn = document.getElementById("btn-ensure-model");
  const status = document.getElementById("model-ensure-status");
  if (!btn || !status) return;

  btn.disabled = true;
  status.innerHTML = `<span class="spinner"></span> Downloading default model…`;

  try {
    const res = await fetch("/api/models/ensure", { method: "POST" });
    const data = await res.json();
    if (data.status === "installed" || data.status === "already_installed") {
      status.innerHTML = `<span class="badge badge-cyan">${data.status}</span> ${escHtml(data.path ?? "")}`;
      refreshModels();
    } else {
      status.innerHTML = `<span class="badge badge-red">error</span> ${escHtml(data.error ?? "unknown error")}`;
    }
  } catch (err) {
    status.innerHTML = `<span class="badge badge-red">error</span> ${escHtml(String(err))}`;
  } finally {
    btn.disabled = false;
  }
}



/* -------------------------------------------------------
   Settings / preferences / control options
   ------------------------------------------------------- */
async function refreshSettings() {
  try {
    const [sRes, cRes] = await Promise.all([fetch('/api/settings'), fetch('/api/control/options')]);
    if (!sRes.ok || !cRes.ok) return;
    const settings = await sRes.json();
    const control = await cRes.json();

    const mode = document.getElementById('ctl-mode');
    const energy = document.getElementById('ctl-energy');
    if (mode) {
      mode.innerHTML = (control.available_modes || []).map(m => `<option value="${escHtml(m)}">${escHtml(m)}</option>`).join('');
      mode.value = settings.control?.mode || control.recommended_mode || 'guided';
    }
    if (energy) {
      energy.innerHTML = (control.energy_budgets || []).map(e => `<option value="${escHtml(e)}">${escHtml(e)}</option>`).join('');
      energy.value = settings.control?.energy_budget || 'warm';
    }

    const lang = document.getElementById('pref-language');
    const theme = document.getElementById('pref-theme');
    const temp = document.getElementById('model-temp');
    if (lang) lang.value = settings.preferences?.language || 'pl-PL';
    if (theme) theme.value = settings.preferences?.theme || 'quiet-dark';
    if (temp) temp.value = settings.model?.temperature ?? 0.2;
  } catch (_) {
    // silent
  }
}

async function saveSettings() {
  const status = document.getElementById('settings-save-status');
  const payload = {
    preferences: {
      language: document.getElementById('pref-language')?.value || 'pl-PL',
      theme: document.getElementById('pref-theme')?.value || 'quiet-dark',
    },
    control: {
      mode: document.getElementById('ctl-mode')?.value || 'guided',
      energy_budget: document.getElementById('ctl-energy')?.value || 'warm',
    },
    model: {
      temperature: Number(document.getElementById('model-temp')?.value || 0.2),
    },
  };

  const modelName = document.getElementById('model-select')?.value;
  if (modelName) {
    try {
      await fetch('/api/models/select', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name: modelName}),
      });
    } catch (_) {}
  }

  try {
    const res = await fetch('/api/settings', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (status) status.innerHTML = `<span class="badge badge-cyan">saved</span> ${escHtml(data.path || '')}`;
    refreshStatus();
  } catch (err) {
    if (status) status.innerHTML = `<span class="badge badge-red">error</span> ${escHtml(String(err))}`;
  }
}

/* -------------------------------------------------------
   Navigation
   ------------------------------------------------------- */
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

/* -------------------------------------------------------
   Helpers
   ------------------------------------------------------- */
function setTextIfExists(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

function updateBar(id, value, cls) {
  const fill = document.getElementById(id);
  if (!fill) return;
  fill.style.width = (Math.min(1, Math.max(0, value)) * 100).toFixed(1) + "%";
  fill.className = "orbital-bar-fill" + (cls ? " " + cls : "");
}

function fmt2(v) { return (typeof v === "number") ? v.toFixed(2) : "—"; }

function fmtBytes(n) {
  if (!n) return "—";
  if (n >= 1e9) return (n / 1e9).toFixed(1) + " GB";
  if (n >= 1e6) return (n / 1e6).toFixed(1) + " MB";
  return (n / 1e3).toFixed(0) + " KB";
}

function escHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

/* -------------------------------------------------------
   Initialise
   ------------------------------------------------------- */
document.addEventListener("DOMContentLoaded", () => {
  initNav();
  showSection("control");

  // Bind model button
  const btnEnsure = document.getElementById("btn-ensure-model");
  if (btnEnsure) btnEnsure.addEventListener("click", ensureDefaultModel);
  const btnSave = document.getElementById('btn-save-settings');
  if (btnSave) btnSave.addEventListener('click', saveSettings);

  // Initial data load
  refreshStatus();
  refreshPanel();
  refreshModels();
  refreshSettings();

  // Periodic refresh
  setInterval(refreshStatus, POLL_INTERVAL_MS);
  setInterval(refreshPanel,  POLL_INTERVAL_MS);
});
