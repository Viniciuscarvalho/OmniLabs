"""OmniLabs Dashboard — live at http://localhost:3141.

Reads from ~/.omnilabs/state.json (sessions) and
~/.omnilabs/agents.json (agent metadata, written at startup).
"""

from __future__ import annotations

import json
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

STATE_FILE = Path.home() / ".omnilabs" / "state.json"
AGENTS_META_FILE = Path.home() / ".omnilabs" / "agents.json"
DASHBOARD_PORT = 3141

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>OmniLabs Dashboard</title>
<style>
  :root {
    --bg: #0d1117; --surface: #161b22; --border: #30363d;
    --text: #e6edf3; --muted: #8b949e;
    --green: #3fb950; --yellow: #d29922; --red: #f85149; --blue: #58a6ff;
    --purple: #bc8cff;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: var(--bg); color: var(--text); padding: 24px; }
  .header { display: flex; align-items: center; gap: 12px; margin-bottom: 24px; }
  .header h1 { font-size: 20px; font-weight: 600; }
  .header .dot { width: 8px; height: 8px; border-radius: 50%; background: var(--green);
                 animation: pulse 2s infinite; }
  .header .count { font-size: 13px; color: var(--muted); margin-left: auto; }
  @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.4; } }
  .session-info { color: var(--muted); font-size: 13px; margin-bottom: 20px; }
  .session-info code { color: var(--purple); background: rgba(188,140,255,.1);
                       padding: 2px 6px; border-radius: 4px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
          gap: 16px; }
  .card { background: var(--surface); border: 1px solid var(--border);
          border-radius: 12px; padding: 20px; transition: border-color .2s; }
  .card:hover { border-color: var(--purple); }
  .card-header { display: flex; justify-content: space-between; align-items: center;
                 margin-bottom: 12px; }
  .card-title { font-size: 15px; font-weight: 600; }
  .badge { font-size: 11px; padding: 3px 10px; border-radius: 12px; font-weight: 500;
           text-transform: uppercase; letter-spacing: .5px; }
  .badge-idle { background: rgba(139,148,158,.15); color: var(--muted); }
  .badge-running { background: rgba(210,153,34,.15); color: var(--yellow);
                   animation: pulse 1.5s infinite; }
  .badge-completed { background: rgba(63,185,80,.15); color: var(--green); }
  .badge-failed { background: rgba(248,81,73,.15); color: var(--red); }
  .meta { font-size: 12px; color: var(--muted); margin-top: 8px; }
  .meta span { display: inline-block; margin-right: 14px; }
  .focus { font-size: 13px; color: var(--muted); margin-top: 10px;
           line-height: 1.5; border-top: 1px solid var(--border); padding-top: 10px; }
  .tags { margin-top: 8px; }
  .tag { font-size: 10px; padding: 2px 6px; border-radius: 4px;
         background: rgba(88,166,255,.1); color: var(--blue); margin-right: 4px; }
  .empty { text-align: center; color: var(--muted); padding: 60px 20px; }
  .empty h2 { font-size: 18px; margin-bottom: 8px; color: var(--text); }
  .empty p { font-size: 14px; line-height: 1.6; }
  .empty code { color: var(--blue); background: rgba(88,166,255,.1);
                padding: 2px 6px; border-radius: 4px; }
</style>
</head>
<body>

<div class="header">
  <div class="dot"></div>
  <h1>OmniLabs</h1>
  <span class="count" id="agent-count"></span>
</div>

<div id="app">
  <div class="empty">
    <h2>Waiting for analysis...</h2>
    <p>Start an analysis in Claude Code:<br>
    <code>Analyze ~/projects/my-app with OmniLabs</code></p>
  </div>
</div>

<script>
let AGENT_META = {};

async function loadMeta() {
  try {
    const res = await fetch('/api/agents');
    if (res.ok) {
      AGENT_META = await res.json();
      const n = Object.keys(AGENT_META).length;
      document.getElementById('agent-count').textContent = n + ' agents registered';
    }
  } catch {}
}

async function refresh() {
  try {
    const res = await fetch('/api/state');
    if (!res.ok) return;
    const state = await res.json();
    render(state);
  } catch {}
}

function render(state) {
  const app = document.getElementById('app');
  if (!state.current_session_id || !state.sessions) return;
  const session = state.sessions[state.current_session_id];
  if (!session) return;

  let html = `
    <div class="session-info">
      Session <code>${session.session_id}</code> &mdash; ${session.target_repo}
    </div>
    <div class="grid">`;

  for (const [name, info] of Object.entries(session.agents)) {
    const meta = AGENT_META[name] || { icon: '\\ud83e\\udd16', focus: '', tags: [] };
    const duration = info.duration_seconds ? `${info.duration_seconds}s` : '\\u2014';
    const error = info.error
      ? `<div class="meta" style="color:var(--red)">${info.error}</div>` : '';
    const tags = (meta.tags || [])
      .map(t => `<span class="tag">${t}</span>`).join('');

    html += `
      <div class="card">
        <div class="card-header">
          <span class="card-title">${meta.icon || '\\ud83e\\udd16'} ${name.charAt(0).toUpperCase() + name.slice(1)}</span>
          <span class="badge badge-${info.status}">${info.status}</span>
        </div>
        <div class="meta">
          <span>Duration: ${duration}</span>
          <span>${info.has_output ? '\\u2713 Output' : ''}</span>
        </div>
        ${error}
        <div class="focus">${meta.focus || ''}</div>
        ${tags ? '<div class="tags">' + tags + '</div>' : ''}
      </div>`;
  }

  html += '</div>';
  app.innerHTML = html;
}

loadMeta();
setInterval(refresh, 1500);
refresh();
</script>
</body>
</html>"""


class DashboardHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self._respond(200, "text/html", DASHBOARD_HTML)
        elif self.path == "/api/state":
            self._respond_json(STATE_FILE)
        elif self.path == "/api/agents":
            self._respond_json(AGENTS_META_FILE)
        else:
            self.send_error(404)

    def _respond(self, code: int, ctype: str, body: str):
        self.send_response(code)
        self.send_header("Content-Type", f"{ctype}; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body.encode())

    def _respond_json(self, path: Path):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        try:
            data = path.read_text() if path.exists() else "{}"
        except Exception:
            data = "{}"
        self.wfile.write(data.encode())

    def log_message(self, fmt, *args):
        pass


def write_agents_meta(agents_data: dict) -> None:
    """Write agent metadata for the dashboard to read."""
    AGENTS_META_FILE.parent.mkdir(parents=True, exist_ok=True)
    AGENTS_META_FILE.write_text(json.dumps(agents_data, indent=2))


def start_dashboard(port: int = DASHBOARD_PORT) -> threading.Thread:
    server = HTTPServer(("127.0.0.1", port), DashboardHandler)
    thread = threading.Thread(target=server.serve_forever, name="omnilabs-dashboard", daemon=True)
    thread.start()
    return thread
