const apiInput = document.getElementById("apiBase");
const btnSaveApi = document.getElementById("btnSaveApi");
const healthEl = document.getElementById("health");

const API_BASE = {
  get: () => localStorage.getItem("api_base") || "http://127.0.0.1:8000",
  set: (v) => localStorage.setItem("api_base", v)
};
apiInput.value = API_BASE.get();

btnSaveApi.addEventListener("click", () => {
  API_BASE.set(apiInput.value.trim());
  pingHealth();
});


async function api(path, { method = "GET", body } = {}) {
  const res = await fetch(API_BASE.get() + path, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  const text = await res.text();
  let data = null;
  try { data = text ? JSON.parse(text) : null; } catch { data = text; }
  if (!res.ok) {
    const msg = (data && (data.detail || data.message)) || text || "Error";
    throw new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
  }
  return data;
}

function setStatus(el, msg, type) {
  el.textContent = msg || "";
  el.className = "status" + (type ? " " + type : "");
}

const tabs = document.querySelectorAll(".tabs button");
const panels = document.querySelectorAll("[data-panel]");
document.querySelector(".tabs").addEventListener("click", (e) => {
  const btn = e.target.closest("button[data-tab]");
  if (!btn) return;
  tabs.forEach(b => b.classList.toggle("active", b === btn));
  const tab = btn.getAttribute("data-tab");
  panels.forEach(p => p.hidden = (p.getAttribute("data-panel") !== tab));
});


async function pingHealth() {
  setStatus(healthEl, "Comprobando…");
  try {
    const h = await api("/");
    setStatus(healthEl, "API activo", "ok");
  } catch {
    setStatus(healthEl, "No disponible", "err");
  }
}
pingHealth();


const formPatient = document.getElementById("formPatient");
const pStatus = document.getElementById("pStatus");
formPatient.addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(formPatient);
  const name = fd.get("name").toString().trim();
  const email = fd.get("email").toString().trim() || null;
  if (!name) return setStatus(pStatus, "El nombre es obligatorio", "err");
  try {
    const data = await api("/patients", { method: "POST", body: { name, email } });
    setStatus(pStatus, `Paciente creado (#${data.id})`, "ok");
    formPatient.reset();
  } catch (err) {
    setStatus(pStatus, err.message, "err");
  }
});


const formDoctor = document.getElementById("formDoctor");
const dStatus = document.getElementById("dStatus");
formDoctor.addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(formDoctor);
  const name = fd.get("name").toString().trim();
  const specialty = fd.get("specialty").toString().trim() || null;
  if (!name) return setStatus(dStatus, "El nombre es obligatorio", "err");
  try {
    const data = await api("/doctors", { method: "POST", body: { name, specialty } });
    setStatus(dStatus, `Doctor creado (#${data.id})`, "ok");
    formDoctor.reset();
  } catch (err) {
    setStatus(dStatus, err.message, "err");
  }
});


const formAppt = document.getElementById("formAppt");
const aStatus = document.getElementById("aStatus");
formAppt.addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(formAppt);
  const patient_id = parseInt(fd.get("patient_id"), 10);
  const doctor_id = parseInt(fd.get("doctor_id"), 10);
  const start_at = fd.get("start_at").toString().trim();
  const duration_min = parseInt(fd.get("duration_min"), 10) || 30;
  const reason = fd.get("reason").toString().trim() || null;

  if (!Number.isInteger(patient_id) || !Number.isInteger(doctor_id) || !start_at) {
    return setStatus(aStatus, "Campos requeridos: patient_id, doctor_id, start_at", "err");
  }
  try {
    const data = await api("/appointments", {
      method: "POST",
      body: { patient_id, doctor_id, start_at, duration_min, reason }
    });
    setStatus(aStatus, `Cita creada (#${data.id})`, "ok");

  } catch (err) {
    setStatus(aStatus, err.message, "err");
  }
});


const btnLoad = document.getElementById("btnLoad");
const btnClear = document.getElementById("btnClear");
const fDoctor = document.getElementById("fDoctor");
const fPatient = document.getElementById("fPatient");
const list = document.getElementById("list");
const lStatus = document.getElementById("lStatus");

async function loadList() {
  setStatus(lStatus, "Cargando…");
  try {
    const qs = new URLSearchParams();
    if (fDoctor.value.trim()) qs.set("doctor_id", fDoctor.value.trim());
    if (fPatient.value.trim()) qs.set("patient_id", fPatient.value.trim());
    const rows = await api("/appointments" + (qs.toString() ? `?${qs}` : ""));
    renderList(Array.isArray(rows) ? rows : []);
    setStatus(lStatus, `Total: ${rows.length}`, "ok");
  } catch (err) {
    setStatus(lStatus, err.message, "err");
    list.innerHTML = "";
  }
}

function renderList(rows) {
  list.innerHTML = "";
  if (!rows.length) {
    const li = document.createElement("li");
    li.textContent = "No hay citas.";
    li.className = "muted";
    list.appendChild(li);
    return;
  }
  rows
    .slice()
    .sort((a,b)=>new Date(a.start_at)-new Date(b.start_at))
    .forEach(r => {
      const li = document.createElement("li");
      const left = document.createElement("div");
      left.innerHTML = `<div class="ttl">#${r.id} — ${r.reason || "Sin motivo"}</div>
                        <div class="muted">P${r.patient_id} · D${r.doctor_id} · ${r.duration_min} min</div>`;
      const right = document.createElement("span");
      right.className = "badge";
      right.textContent = new Date(r.start_at).toLocaleString();
      li.appendChild(left); li.appendChild(right);
      list.appendChild(li);
    });
}

btnLoad.addEventListener("click", loadList);
btnClear.addEventListener("click", () => { fDoctor.value = ""; fPatient.value = ""; loadList(); });


loadList();
