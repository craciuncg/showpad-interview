// The page talks only to /api. It never opens the graph or Ollama itself.
// sale is the opportunity id of the chip the user last chose.
// busy stops a second click while a long model call is still running.
const state = {
  sale: "opportunity:deal-1",
  busy: false,
};

const statusNode = document.querySelector("#status");
const buttons = [...document.querySelectorAll("button")];

document.querySelector("#sync").addEventListener("click", () => run("Syncing the CRM…", sync, "#crm"));
document.querySelector("#acme").addEventListener("click", () => run("Reading the Acme call. The local model can take a minute…", () => processCall("acme"), "#pipeline"));
document.querySelector("#sam").addEventListener("click", () => run("Reading the Globex call. The local model can take a minute…", () => processCall("sam"), "#pipeline"));
document.querySelector("#ask").addEventListener("click", ask);
document.querySelector("#ask-form").addEventListener("submit", (event) => {
  event.preventDefault();
  ask();
});
document.querySelector("#reset").addEventListener("click", () => run("Resetting…", reset));
document.querySelectorAll(".chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    state.sale = chip.dataset.sale;
    document.querySelectorAll(".chip").forEach((item) => item.classList.toggle("on", item === chip));
    refreshBrief();
  });
});

boot();

// On load, check Ollama and draw whatever is already in memory.
async function boot() {
  const health = await api("/api/health");
  const healthNode = document.querySelector("#health");
  healthNode.textContent = health.model.ok
    ? `Local model ready: ${health.model.model}`
    : health.model.detail;
  healthNode.classList.toggle("bad", !health.model.ok);
  await refreshGraph();
  await refreshBrief();
}

async function sync() {
  const result = await api("/api/crm/sync", { method: "POST" });
  document.querySelector("#crm").innerHTML = `
    <div class="card"><strong>Copied into the graph.</strong>
      ${result.summary.accounts} companies, ${result.summary.contacts} people, ${result.summary.opportunities} open sales, ${result.summary.finished_sales} finished sales kept for the count.</div>`;
  renderGraph(result.graph);
  await refreshBrief();
}

// callId is "acme" or "sam". The body matches the Pydantic CallIn model.
async function processCall(callId) {
  const result = await api("/api/calls/process", {
    method: "POST",
    body: JSON.stringify({ call_id: callId }),
  });
  state.sale = result.opportunity_id;
  document.querySelectorAll(".chip").forEach((chip) => chip.classList.toggle("on", chip.dataset.sale === state.sale));
  renderPipeline(result);
  renderGraph(result.graph);
  await refreshBrief();
}

async function ask() {
  await run("Phrasing an answer from the brief…", async () => {
    const result = await api("/api/query/ask", {
      method: "POST",
      body: JSON.stringify({
        opportunity_id: state.sale,
        question: document.querySelector("#question").value,
      }),
    });
    renderAnswer(result);
  }, "#answer");
}

async function reset() {
  await api("/api/reset", { method: "POST" });
  document.querySelector("#crm").textContent = "Sync the CRM to load Acme, Anna, and the Globex sale.";
  document.querySelector("#pipeline").textContent = "Process a call to see each box run.";
  document.querySelector("#answer").textContent = "Ask after the Acme call has been processed.";
  document.querySelector("#decisions").textContent = "Names from the selected sale appear here.";
  await refreshGraph();
  await refreshBrief();
}

async function refreshBrief() {
  const brief = await api(`/api/query/brief?opportunity_id=${encodeURIComponent(state.sale)}`);
  renderBrief(brief);
  renderDecisions(brief);
}

async function refreshGraph() {
  renderGraph(await api("/api/graph"));
}

function renderPipeline(result) {
  const steps = result.steps.map((step) => `<div class="step"><strong>${escapeHtml(step.component)}</strong><div>${escapeHtml(step.detail)}</div></div>`).join("");
  const dropped = result.dropped.length
    ? result.dropped.map((item) => `<div class="quote dropped"><div>${escapeHtml(item.surface || item.type || "Claim")}</div><div>${escapeHtml(item.quote || "")}</div><div class="muted">${escapeHtml(item.reason)}</div></div>`).join("")
    : `<p class="muted">Nothing was dropped. A sentence that is not in the call would appear here and would not be stored.</p>`;
  const resolved = result.resolved.map((item) => `<div class="card"><strong>${escapeHtml(item.surface)}</strong> — ${escapeHtml(item.status)}<div class="muted">${escapeHtml(item.note || "")}</div></div>`).join("");
  document.querySelector("#pipeline").innerHTML = `
    ${steps}
    <h3>Dropped before resolve</h3>
    ${dropped}
    <h3>After resolve</h3>
    ${resolved}
    <details><summary>Model JSON</summary><pre>${escapeHtml(JSON.stringify(result.model_output, null, 2))}</pre></details>`;
}

function renderBrief(brief) {
  const node = document.querySelector("#brief");
  if (!brief.ready) {
    node.textContent = brief.detail || "Sync the CRM first.";
    return;
  }
  const missing = brief.missing_people.length
    ? brief.missing_people.map(personCard).join("")
    : `<p class="muted">No missing person on this sale.</p>`;
  const spoken = brief.spoken.length
    ? brief.spoken.map((item) => `<div class="quote kept"><strong>${escapeHtml(item.label)}</strong><div>${escapeHtml(item.quote)}</div><div class="muted">CRM vendor field: ${escapeHtml(item.crm_competitor_field || "empty")}</div></div>`).join("")
    : `<p class="muted">No vendor or worry was kept from the call.</p>`;
  const similar = brief.similar.length
    ? brief.similar.map((item) => item.shown
      ? `<div class="card">${item.wins} signed after ${escapeHtml(item.win_action)}, ${item.losses} lost after ${escapeHtml(item.loss_action)}. Sample: ${item.sample_size}. No other buyer's sentences are included.</div>`
      : `<div class="card">${escapeHtml(item.detail)}</div>`).join("")
    : `<p class="muted">Process the call before the similar-sale count can be chosen.</p>`;
  const people = brief.people.map((person) => `<div class="card">${escapeHtml(person.name)} — ${escapeHtml(person.role || "no role")} <span class="muted">(${escapeHtml(person.where)})</span></div>`).join("");
  node.innerHTML = `
    <div class="card"><strong>${escapeHtml(brief.account)} — ${escapeHtml(brief.name)}</strong><div>${escapeHtml(brief.stage)}, ${money(brief.amount)}, vendor field ${escapeHtml(brief.competitor_field || "empty")}</div></div>
    <h3>People on this sale</h3>${people || `<p class="muted">None yet.</p>`}
    <h3>Named, not a confirmed CRM contact</h3>${missing}
    <h3>Said on the call</h3>${spoken}
    <h3>Similar finished sales</h3>${similar}`;
}

function personCard(person) {
  return `<div class="quote"><strong>${escapeHtml(person.name)}</strong> — ${escapeHtml(statusLabel(person.status))}<div>${escapeHtml(person.quote)}</div><div class="muted">${escapeHtml(person.note || "")}</div></div>`;
}

function renderDecisions(brief) {
  const node = document.querySelector("#decisions");
  if (!brief.ready || !brief.missing_people) {
    node.textContent = "Names from the selected sale appear here.";
    return;
  }
  const names = brief.missing_people.filter((person) => person.status !== "rejected");
  if (!names.length) {
    node.innerHTML = `<p class="muted">No open name on this sale. Confirmed CRM matches are already linked.</p>`;
    return;
  }
  node.innerHTML = names.map((person) => `
    <div class="card">
      <strong>${escapeHtml(person.name)}</strong>
      <div class="muted">${escapeHtml(statusLabel(person.status))}</div>
      <div class="actions">
        <button type="button" data-act="confirm" data-name="${escapeHtml(person.name)}">Confirm, still not in the CRM</button>
        <button type="button" class="quiet" data-act="reject" data-name="${escapeHtml(person.name)}">Reject</button>
      </div>
    </div>`).join("");
  node.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => decide(button.dataset.act, button.dataset.name));
  });
}

// decision is "confirm" or "reject". The body matches DecisionIn.
async function decide(decision, surface) {
  const accountId = state.sale === "opportunity:deal-2" ? "account-2" : "account-1";
  await run("Saving the decision…", async () => {
    const result = await api("/api/seller/decisions", {
      method: "POST",
      body: JSON.stringify({ account_id: accountId, surface, decision }),
    });
    renderGraph(result.graph);
    await refreshBrief();
  });
}

// The paragraph comes first. Under it, facts are grouped by where they came from.
// Left out appears only when the model added a sentence none of those groups contain.
function renderAnswer(result) {
  const node = document.querySelector("#answer");
  if (!result.ready) {
    node.textContent = result.detail || "The brief is not ready.";
    return;
  }
  const customer = (result.customer_file || []).map((item) => `<div class="quote kept"><strong>${escapeHtml(item.label)}</strong><div>${escapeHtml(item.value)}</div></div>`).join("");
  const call = (result.call || []).map((item) => `<div class="quote kept"><strong>${escapeHtml(item.label)}</strong> <span class="muted">${escapeHtml(item.id)}</span><div>${escapeHtml(item.quote)}</div></div>`).join("");
  const similar = (result.similar || []).map((item) => `<div class="quote kept"><strong>${escapeHtml(item.label)}</strong><div>${escapeHtml(item.quote)}</div></div>`).join("");
  const leftOut = (result.left_out || []).map((sentence) => `<div class="quote dropped">${escapeHtml(sentence.text)}<div class="muted">${escapeHtml(sentence.reason)}</div></div>`).join("");
  node.innerHTML = `
    ${result.used_brief_instead ? `<p class="muted">The reply is taken from the brief.</p>` : ""}
    <p class="prose">${escapeHtml(result.prose || "")}</p>
    <h3>From the customer file</h3>
    ${customer || `<p class="muted">No customer-file fields for this sale.</p>`}
    <h3>From this call</h3>
    ${call || `<p class="muted">Nothing from this call yet.</p>`}
    <h3>Similar finished sales</h3>
    ${similar || `<p class="muted">No similar-sale count for this sale.</p>`}
    ${leftOut ? `<h3>Left out</h3>${leftOut}` : ""}`;
}

function renderGraph(graph) {
  const node = document.querySelector("#graph");
  if (!graph.nodes.length) {
    node.textContent = "Empty until the CRM is synced.";
    return;
  }
  const labels = Object.fromEntries(graph.nodes.map((item) => [item.id, labelOf(item)]));
  const nodes = graph.nodes.map((item) => `<div class="card"><strong>${escapeHtml(item.type)}</strong> — ${escapeHtml(labelOf(item))}</div>`).join("");
  const edges = graph.edges.map((edge) => `<div class="edge">${escapeHtml(labels[edge.source] || edge.source)} — ${escapeHtml(edge.type)} — ${escapeHtml(labels[edge.target] || edge.target)}</div>`).join("");
  node.innerHTML = `<p class="muted">${graph.history_records} past-sale records are hidden. The brief reads their count.</p>${nodes}<h3>Links</h3>${edges}`;
}

function labelOf(node) {
  return node.name || node.surface || node.label || node.id;
}

function statusLabel(status) {
  const labels = {
    unresolved: "mentioned, not in the CRM",
    ambiguous: "two possible people, none chosen",
    confirmed_by_seller: "confirmed by you, still not in the CRM",
    rejected: "rejected",
    resolved: "matched to a CRM contact",
  };
  return labels[status] || status;
}

function money(amount) {
  if (!amount) return "no amount";
  return `$${Number(amount).toLocaleString("en-US")}`;
}

// Disable the buttons and show the spinner until the request returns.
async function run(message, action, waitTarget) {
  if (state.busy) return;
  state.busy = true;
  buttons.forEach((button) => { button.disabled = true; });
  statusNode.textContent = message;
  statusNode.classList.remove("error");
  if (waitTarget) showWait(waitTarget, message);
  try {
    await action();
    statusNode.textContent = "Done.";
  } catch (error) {
    statusNode.textContent = error.message;
    statusNode.classList.add("error");
    if (waitTarget) {
      document.querySelector(waitTarget).innerHTML = `<p class="error">${escapeHtml(error.message)}</p>`;
    }
  } finally {
    state.busy = false;
    buttons.forEach((button) => { button.disabled = false; });
  }
}

function showWait(selector, message) {
  document.querySelector(selector).innerHTML = `
    <div class="wait" role="status">
      <span class="spinner" aria-hidden="true"></span>
      <p>${escapeHtml(message)}</p>
      <div class="skeleton"></div>
      <div class="skeleton short"></div>
    </div>`;
}

// Every panel uses this. A failed response becomes the red status line.
async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(body.detail || `Request failed (${response.status})`);
  }
  return body;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}
