const qs = (selector) => document.querySelector(selector);

const els = {
  body: document.body,
  modeDot: qs("#modeDot"),
  sideMode: qs("#sideMode"),
  twilioBadge: qs("#twilioBadge"),
  demoBadge: qs("#demoBadge"),
  systemStatus: qs("#systemStatus"),
  alarmState: qs("#alarmState"),
  dispatchState: qs("#dispatchState"),
  activeTimer: qs("#activeTimer"),
  banner: qs("#banner"),
  eventTime: qs("#eventTime"),
  vehicleNumber: qs("#vehicleNumber"),
  locationText: qs("#locationText"),
  currentStage: qs("#currentStage"),
  driverResponse: qs("#driverResponse"),
  recipientsSummary: qs("#recipientsSummary"),
  contactsBody: qs("#contactsBody"),
  logList: qs("#logList"),
  settingsForm: qs("#settingsForm"),
  vehicleInput: qs("#vehicleInput"),
  locationInput: qs("#locationInput"),
  demoModeInput: qs("#demoModeInput"),
  contactDialog: qs("#contactDialog"),
  contactForm: qs("#contactForm"),
  contactIndex: qs("#contactIndex"),
  contactName: qs("#contactName"),
  contactNumber: qs("#contactNumber"),
  closeDialog: qs("#closeDialog"),
  railAlertMode: qs("#railAlertMode"),
  railLastEvent: qs("#railLastEvent"),
  dispatchHeadline: qs("#dispatchHeadline"),
  dispatchSubline: qs("#dispatchSubline")
};

let lastContactsKey = "";
let lastSystemGauge = null;
let lastAlertGauge = null;

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options
  });
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

async function postAction(action) {
  await api("/api/action", {
    method: "POST",
    body: JSON.stringify({ action })
  });
  await refresh();
}

function setText(element, value) {
  if (!element) {
    return;
  }
  element.textContent = value || "";
}

function setInputValue(input, value) {
  if (input && document.activeElement !== input) {
    input.value = value || "";
  }
}

function bind(element, eventName, handler) {
  if (element) {
    element.addEventListener(eventName, handler);
  }
}

function modeLabel(mode) {
  const labels = {
    normal: "Monitoring",
    driver_wait: "Driver timer",
    message_dispatch: "Sending SMS",
    contact_wait: "Awaiting ack",
    auto_calling: "Calling",
    completed: "Completed",
    resolved: "Resolved"
  };
  return labels[mode] || mode;
}

function applyTheme(mode) {
  els.body.classList.remove("is-danger", "is-warning", "is-success");
  if (["driver_wait", "message_dispatch", "auto_calling", "completed"].includes(mode)) {
    els.body.classList.add("is-danger");
    return;
  }
  if (mode === "contact_wait") {
    els.body.classList.add("is-warning");
    return;
  }
  els.body.classList.add("is-success");
}

function updateTimeline(mode) {
  const order = ["normal", "driver_wait", "message_dispatch", "contact_wait", "auto_calling", "completed"];
  const activeIndex = Math.max(0, order.indexOf(mode === "resolved" ? "normal" : mode));
  document.querySelectorAll("#timeline [data-step]").forEach((step) => {
    const stepIndex = order.indexOf(step.dataset.step);
    step.classList.toggle("completed", stepIndex < activeIndex);
    step.classList.toggle("active", stepIndex === activeIndex);
    step.classList.toggle("pending", stepIndex > activeIndex);
  });
}

function updateDispatchPanel(state) {
  const copy = {
    normal: ["Monitoring clear", "Emergency alerts are on standby."],
    driver_wait: ["Driver response timer active", "Waiting before emergency alert dispatch."],
    message_dispatch: ["Emergency alerts sent", "Calling emergency services is queued if nobody acknowledges."],
    contact_wait: ["SMS sent, awaiting acknowledgement", "Automatic calls will start if no response is received."],
    auto_calling: ["Calling emergency services", "Voice escalation is active for saved responders."],
    completed: ["Escalation cycle completed", "Messages and calls were dispatched."],
    resolved: ["Emergency flow resolved", "No active dispatch is running."]
  };
  const [headline, subline] = copy[state.mode] || copy.normal;
  setText(els.dispatchHeadline, headline);
  setText(els.dispatchSubline, subline);
}

function secondsFromTimer(value) {
  const match = String(value || "").match(/^(\d{2}):(\d{2})$/);
  if (!match) {
    return null;
  }
  return Number(match[1]) * 60 + Number(match[2]);
}

function gaugeTargets(state) {
  const seconds = secondsFromTimer(state.active_timer);
  if (state.mode === "driver_wait" && seconds !== null) {
    const elapsed = Math.max(0, Math.min(30, 30 - seconds));
    const percent = Math.round((elapsed / 30) * 100);
    return { system: Math.max(18, percent), alert: Math.max(40, percent) };
  }
  if (state.mode === "contact_wait" && seconds !== null) {
    const elapsed = Math.max(0, Math.min(15, 15 - seconds));
    const percent = Math.round((elapsed / 15) * 100);
    return { system: 100, alert: Math.max(55, percent) };
  }
  const targets = {
    normal: { system: 72, alert: 24 },
    message_dispatch: { system: 100, alert: 78 },
    auto_calling: { system: 100, alert: 92 },
    completed: { system: 100, alert: 100 },
    resolved: { system: 64, alert: 32 }
  };
  return targets[state.mode] || targets.normal;
}

function setAnimatedGauge(name, percent) {
  const value = Math.max(0, Math.min(100, Number(percent) || 0));
  const property = name === "system" ? "--system-angle" : "--alert-angle";
  const lastKey = name === "system" ? lastSystemGauge : lastAlertGauge;
  if (lastKey === value) {
    return;
  }
  if (name === "system") {
    lastSystemGauge = value;
  } else {
    lastAlertGauge = value;
  }
  document.documentElement.style.setProperty(property, "0deg");
  window.requestAnimationFrame(() => {
    window.requestAnimationFrame(() => {
      document.documentElement.style.setProperty(property, `${Math.round(value * 2.72)}deg`);
    });
  });
}

function updateGauges(state) {
  const targets = gaugeTargets(state);
  setAnimatedGauge("system", targets.system);
  setAnimatedGauge("alert", targets.alert);
}

function chip(status) {
  const normalized = String(status || "Standby").toLowerCase();
  return `<span class="status-chip ${normalized}">${status}</span>`;
}

function renderContacts(contacts) {
  if (!els.contactsBody) {
    return;
  }
  const key = JSON.stringify(contacts);
  if (key === lastContactsKey) {
    return;
  }
  lastContactsKey = key;
  els.contactsBody.innerHTML = contacts.map((contact, index) => `
    <tr>
      <td>${escapeHtml(contact.name)}</td>
      <td>${escapeHtml(contact.role)}</td>
      <td>${escapeHtml(contact.number)}</td>
      <td>${chip(contact.sms_status)}</td>
      <td>${chip(contact.call_status)}</td>
      <td><button type="button" data-edit="${index}">Edit</button></td>
    </tr>
  `).join("");
}

function renderLogs(logs) {
  if (!els.logList) {
    return;
  }
  els.logList.innerHTML = logs.slice(-80).map((entry) => `
    <div class="log-row ${escapeHtml(entry.level)}">
      <time>${escapeHtml(entry.time)}</time>
      <span>${escapeHtml(entry.message)}</span>
    </div>
  `).join("");
  els.logList.scrollTop = els.logList.scrollHeight;
}

function escapeHtml(value) {
  return String(value || "").replace(/[&<>"']/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;"
  })[character]);
}

function renderState(state) {
  setText(els.sideMode, modeLabel(state.mode));
  setText(els.systemStatus, state.system_status);
  setText(els.alarmState, state.alarm_state);
  setText(els.dispatchState, state.dispatch_state);
  setText(els.activeTimer, state.active_timer);
  setText(els.banner, state.banner);
  setText(els.eventTime, state.event_time);
  setText(els.vehicleNumber, state.vehicle_number);
  setText(els.locationText, state.location_text);
  setText(els.currentStage, state.current_stage);
  setText(els.driverResponse, state.driver_response);
  setText(els.recipientsSummary, state.recipients_summary);

  setText(els.twilioBadge, state.twilio_ready ? "Twilio ready" : "Twilio not configured");
  setText(els.demoBadge, state.demo_mode ? "Demo mode" : "Real Twilio mode");
  setText(els.railAlertMode, state.demo_mode ? "Demo Mode" : "Real Twilio");
  setText(els.railLastEvent, state.event_time === "--:--" ? "No event" : state.event_time);
  if (els.demoModeInput) {
    els.demoModeInput.checked = state.demo_mode;
  }
  setInputValue(els.vehicleInput, state.vehicle_number);
  setInputValue(els.locationInput, state.location_text);

  applyTheme(state.mode);
  updateGauges(state);
  updateTimeline(state.mode);
  updateDispatchPanel(state);
  renderContacts(state.contacts);
  renderLogs(state.logs);
}

async function refresh() {
  try {
    const state = await api("/api/state");
    renderState(state);
  } catch (error) {
    console.error(error);
  }
}

document.querySelectorAll("[data-action]").forEach((button) => {
  button.addEventListener("click", () => postAction(button.dataset.action));
});

bind(els.settingsForm, "submit", async (event) => {
  event.preventDefault();
  await api("/api/settings", {
    method: "POST",
    body: JSON.stringify({
      vehicle_number: els.vehicleInput.value,
      location_text: els.locationInput.value,
      demo_mode: els.demoModeInput.checked
    })
  });
  await refresh();
});

bind(els.contactsBody, "click", async (event) => {
  const button = event.target.closest("[data-edit]");
  if (!button || !els.contactDialog) {
    return;
  }
  const state = await api("/api/state");
  const index = Number(button.dataset.edit);
  const contact = state.contacts[index];
  if (!contact) {
    return;
  }
  els.contactIndex.value = String(index);
  els.contactName.value = contact.name;
  els.contactNumber.value = contact.number;
  els.contactDialog.showModal();
});

bind(els.closeDialog, "click", () => els.contactDialog.close());

bind(els.contactForm, "submit", async (event) => {
  event.preventDefault();
  await api("/api/contact", {
    method: "POST",
    body: JSON.stringify({
      index: Number(els.contactIndex.value),
      name: els.contactName.value,
      number: els.contactNumber.value
    })
  });
  els.contactDialog.close();
  await refresh();
});

refresh();
setInterval(refresh, 1000);
