const API = "/api/v1";
function token() { return sessionStorage.getItem("token"); }

async function api(path, opts = {}) {
  const headers = opts.headers || {};
  if (token()) headers["Authorization"] = "Bearer " + token();
  const init = { method: opts.method || "GET", headers };
  if (opts.json !== undefined) { headers["Content-Type"] = "application/json"; init.body = JSON.stringify(opts.json); }
  if (opts.body !== undefined) init.body = opts.body;   // FormData for file upload
  const res = await fetch(API + path, init);
  if (res.status === 401 && !path.startsWith("/auth")) { sessionStorage.removeItem("token"); location.href = "/index.html"; }
  if (res.status === 204) return null;
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error((data.error && data.error.message) || "Request failed");
  return data;
}

function requireLogin() { if (!token()) location.href = "/index.html"; }

function showMessage(el, text, isError) {
  el.textContent = text;
  el.className = isError ? "msg error" : "msg";
  el.setAttribute("role", isError ? "alert" : "status");
}

/* ---------- shared rendering helpers (all output is escaped) ---------- */
function escHtml(s) { const d = document.createElement("div"); d.textContent = s == null ? "" : String(s); return d.innerHTML; }

const TAG_COLORS = ["blue", "purple", "pink", "orange", "yellow", "brown", "green", "gray"];
function tagColor(name) {
  let h = 0;
  for (const ch of String(name)) h = (h * 31 + ch.charCodeAt(0)) >>> 0;
  return TAG_COLORS[h % TAG_COLORS.length];
}
function tagList(items, color, empty) {
  if (!items || !items.length) return `<span class="empty-val">${escHtml(empty || "Empty")}</span>`;
  return '<ul class="tags">' + items.map((t) => `<li class="tag ${color || tagColor(t)}">${escHtml(t)}</li>`).join("") + "</ul>";
}
function bulletList(items, empty) {
  return items && items.length
    ? "<ul>" + items.map((i) => `<li>${escHtml(i)}</li>`).join("") + "</ul>"
    : `<p class="empty-val">${escHtml(empty)}</p>`;
}
function scoreClass(s) { return s >= 70 ? "high" : s >= 40 ? "mid" : "low"; }
const STATUS_COLORS = { saved: "gray", applied: "blue", interviewing: "yellow", offer: "green", rejected: "red", withdrawn: "brown" };
const TYPE_COLORS = { "full-time": "blue", "part-time": "purple", internship: "green", contract: "orange" };

/* ---------- sidebar navigation ---------- */
const PAGES = [
  ["/resume.html", "📄", "My resume"],
  ["/jobs.html", "🔎", "Find jobs"],
  ["/match.html", "🎯", "Match"],
  ["/recommend.html", "✨", "Recommendations"],
  ["/bookmarks.html", "🔖", "Bookmarks"],
  ["/applications.html", "🗂️", "Applications"],
];

function renderNav() {
  document.body.classList.add("app");
  const here = location.pathname === "/" ? "/index.html" : location.pathname;
  const nav = document.createElement("nav");
  nav.className = "sidebar";
  nav.setAttribute("aria-label", "Main");
  nav.innerHTML =
    '<div class="workspace"><span class="workspace-mark" aria-hidden="true">R</span>Resume Matcher</div>' +
    '<p class="side-group">Pages</p>' +
    PAGES.map(([h, icon, t]) =>
      `<a class="side-link" href="${h}"${h === here ? ' aria-current="page"' : ""}>` +
      `<span class="side-icon" aria-hidden="true">${icon}</span><span class="side-text">${t}</span></a>`).join("") +
    '<div class="side-foot"><div class="side-user" id="side-user"></div>' +
    '<a href="#" class="side-link" id="logout"><span class="side-icon" aria-hidden="true">↩</span><span class="side-text">Log out</span></a></div>';
  document.body.prepend(nav);
  document.getElementById("logout").onclick = (e) => {
    e.preventDefault(); sessionStorage.removeItem("token"); location.href = "/index.html";
  };
  api("/me").then((me) => { document.getElementById("side-user").textContent = me.email; }).catch(() => {});
}
