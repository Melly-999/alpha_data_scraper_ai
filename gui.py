from __future__ import annotations

import json
from typing import Any


def render_console(payload: dict[str, Any]) -> None:
    print("=== Alpha AI Live Snapshot ===")
    print(json.dumps(payload, indent=2))
