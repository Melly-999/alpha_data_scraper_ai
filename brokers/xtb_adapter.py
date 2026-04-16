from __future__ import annotations

from brokers.xtb_mirror_adapter import XTBMirrorAdapter


class XTBBrokerAdapter(XTBMirrorAdapter):
    """Compatibility adapter. XTB direct API is unavailable, so this routes to mirror/manual mode."""

    name = "xtb"
