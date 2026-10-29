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

function renderNav() {
  const nav = document.createElement("nav");
  nav.setAttribute("aria-label", "Main");
  const links = [["/resume.html", "Resume"], ["/jobs.html", "Jobs"], ["/match.html", "Match"],
    ["/recommend.html", "Recommendations"], ["/bookmarks.html", "Bookmarks"], ["/applications.html", "Applications"]];
  nav.innerHTML = links.map(([h, t]) => `<a href="${h}">${t}</a>`).join("") + '<a href="#" id="logout">Log out</a>';
  document.body.prepend(nav);
  document.getElementById("logout").onclick = (e) => {
    e.preventDefault(); sessionStorage.removeItem("token"); location.href = "/index.html";
  };
}
