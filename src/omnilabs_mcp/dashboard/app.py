"""Dashboard placeholder — SEC-12 will implement the live web dashboard.

Exports DASHBOARD_PORT and start_dashboard() so server.py can import
them without error.
"""

from __future__ import annotations

import sys

DASHBOARD_PORT = 3141


def start_dashboard(port: int = DASHBOARD_PORT) -> None:
    """No-op placeholder. SEC-12 will start an HTTP server here."""
    print(f"Dashboard: pending (SEC-12) — will run on port {port}", file=sys.stderr)
