from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_AUDIT_SOURCE = REPO_ROOT / "mellytrade_v3/mellytrade-api/app/audit.py"
FRONTEND_AUDIT_FILTER_SOURCE = REPO_ROOT / "frontend/src/pages/AuditTrailPage.tsx"
FRONTEND_AUDIT_TYPE_SOURCE = REPO_ROOT / "frontend/src/types/melly.ts"

GENERIC_FILTER_VALUES = {"", "all", "ALL", "All"}
EVENT_LITERAL_RE = re.compile(r'\b(?:event_type|type)\s*=\s*"([a-z][a-z0-9_]*)"')


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _backend_emitted_event_types(source: str) -> set[str]:
    """Extract audit event literals emitted by the backend audit module."""
    return set(EVENT_LITERAL_RE.findall(source))


def _frontend_filter_event_types(source: str) -> set[str]:
    """Extract only EVENT_TYPES option values from the audit filter control."""
    match = re.search(
        r"const\s+EVENT_TYPES\b.*?=\s*\[(?P<body>.*?)\];",
        source,
        flags=re.DOTALL,
    )
    assert match, "Could not find AuditTrailPage EVENT_TYPES filter options."

    values = set(re.findall(r'\bvalue:\s*"([^"]*)"', match.group("body")))
    return {value for value in values if value not in GENERIC_FILTER_VALUES}


def _frontend_audit_type_union(source: str) -> set[str]:
    """Extract only AuditEventType union members from the frontend type file."""
    match = re.search(
        r"export\s+type\s+AuditEventType\s*=(?P<body>.*?);",
        source,
        flags=re.DOTALL,
    )
    assert match, "Could not find frontend AuditEventType union."

    return set(re.findall(r'\|\s*"([^"]+)"', match.group("body")))


def test_backend_audit_event_types_are_frontend_filterable() -> None:
    backend_event_types = _backend_emitted_event_types(_read(BACKEND_AUDIT_SOURCE))
    frontend_filter_types = _frontend_filter_event_types(
        _read(FRONTEND_AUDIT_FILTER_SOURCE)
    )
    frontend_type_union = _frontend_audit_type_union(_read(FRONTEND_AUDIT_TYPE_SOURCE))

    assert backend_event_types, "No backend audit event type literals were extracted."

    missing_filters = sorted(backend_event_types - frontend_filter_types)
    assert not missing_filters, (
        "Backend audit event types are missing from frontend audit filter options: "
        f"{missing_filters}. Update AuditTrailPage EVENT_TYPES when adding emitted "
        "backend audit event types."
    )

    missing_type_union = sorted(backend_event_types - frontend_type_union)
    assert not missing_type_union, (
        "Backend audit event types are missing from frontend AuditEventType: "
        f"{missing_type_union}. Update frontend/src/types/melly.ts when adding "
        "emitted backend audit event types."
    )
