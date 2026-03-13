"""OmniLabs Dashboard — lightweight local web server.

Runs on a background thread alongside the MCP stdio server.
Serves a single-page dashboard at http://localhost:3141 that
reads from ~/.omnilabs/state.json and auto-refreshes.
"""

from __future__ import annotations

import json
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

STATE_FILE = Path.home() / ".omnilabs" / "state.json"
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
  @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.4; } }
  .session-info { color: var(--muted); font-size: 13px; margin-bottom: 20px; }
  .session-info code { color: var(--purple); background: rgba(188,140,255,.1);
                       padding: 2px 6px; border-radius: 4px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
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
</div>

<div id="app">
  <div class="empty">
    <h2>Waiting for analysis...</h2>
    <p>Start an analysis in Claude Code:<br>
    <code>Analyze ~/projects/my-app with OmniLabs</code></p>
  </div>
</div>

<script>
const AGENT_META = {
  business:    { icon: '\\ud83d\\udcca', focus: 'Product-market fit, competitive landscape, GTM readiness' },
  financial:   { icon: '\\ud83d\\udcb0', focus: 'TCO modeling, unit economics, cost at 1K\\u21921M users' },
  technical:   { icon: '\\u2699\\ufe0f', focus: '6-dimension scoring: scalability, reliability, security...' },
  adversarial: { icon: '\\ud83d\\udd25', focus: 'Pre-mortem, assumption attack, competitor simulation' },
};

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
  if (!state.current_session_id || !state.sessions) {
    return;
  }
  const session = state.sessions[state.current_session_id];
  if (!session) return;

  let html = `
    <div class="session-info">
      Session <code>${session.session_id}</code> &mdash;
      ${session.target_repo}
    </div>
    <div class="grid">`;

  for (const [name, info] of Object.entries(session.agents)) {
    const meta = AGENT_META[name] || { icon: '\\ud83e\\udd16', focus: '' };
    const duration = info.duration_seconds ? `${info.duration_seconds}s` : '\\u2014';
    const error = info.error ? `<div class="meta" style="color:var(--red)">${info.error}</div>` : '';

    html += `
      <div class="card">
        <div class="card-header">
          <span class="card-title">${meta.icon} ${name.charAt(0).toUpperCase() + name.slice(1)}</span>
          <span class="badge badge-${info.status}">${info.status}</span>
        </div>
        <div class="meta">
          <span>Duration: ${duration}</span>
          <span>${info.has_output ? '\\u2713 Has output' : ''}</span>
        </div>
        ${error}
        <div class="focus">${meta.focus}</div>
      </div>`;
  }

  html += '</div>';
  app.innerHTML = html;
}

setInterval(refresh, 1500);
refresh();
</script>
</body>
</html>"""


class DashboardHandler(SimpleHTTPRequestHandler):
    """Serves the dashboard HTML and the state API."""

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self._serve_html()
        elif self.path == "/api/state":
            self._serve_state()
        else:
            self.send_error(404)

    def _serve_html(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(DASHBOARD_HTML.encode())

    def _serve_state(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        try:
            data = STATE_FILE.read_text() if STATE_FILE.exists() else "{}"
        except Exception:
            data = "{}"
        self.wfile.write(data.encode())

    def log_message(self, format, *args):
        pass  # Suppress request logs to keep CLI clean


def start_dashboard(port: int = DASHBOARD_PORT) -> threading.Thread:
    """Start the dashboard HTTP server in a daemon thread.

    Returns the thread (already started). The thread is a daemon,
    so it will be killed when the main MCP process exits.
    """
    server = HTTPServer(("127.0.0.1", port), DashboardHandler)

    thread = threading.Thread(
        target=server.serve_forever,
        name="omnilabs-dashboard",
        daemon=True,
    )
    thread.start()
    return thread
