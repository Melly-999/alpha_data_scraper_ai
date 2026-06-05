"""MOBILE-AI-007B — Screenshot upload analysis service.

Validates an uploaded chart screenshot (raw image bytes) and returns a
deterministic, analysis-only preview. Honors the MOBILE-AI-007A safety
contract and image privacy/retention policy:

  * no image storage / persistence (bytes are validated then discarded),
  * no AI provider calls, no network calls,
  * no database writes, no image logging,
  * analysis-only / paper-only response, never an order.

Validation is pure standard library: MIME allowlist + magic-signature
checks. No Pillow / python-magic / python-multipart dependency is used.
"""

from __future__ import annotations

from app.schemas.mobile_ai import (
    ChartAnalysisResult,
    MarketBias,
    PaperGamePlan,
    RiskAssessment,
    RiskLevel,
    ScreenshotAnalysisPreview,
)

# Conservative upload limit (5 MB) per the MOBILE-AI-007A safety contract.
MAX_UPLOAD_BYTES = 5 * 1024 * 1024

# Allowed image MIME types (allowlist).
ALLOWED_MIME_TYPES: frozenset[str] = frozenset(
    {"image/png", "image/jpeg", "image/webp"}
)


class ScreenshotValidationError(Exception):
    """Raised when an upload fails a validation rule.

    ``status_code`` mirrors the HTTP status the route should return.
    """

    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


def _normalize_mime(content_type: str | None) -> str:
    """Return the bare MIME type (drop charset/params), lowercased."""
    if not content_type:
        return ""
    return content_type.split(";", 1)[0].strip().lower()


def _detect_signature(data: bytes) -> str | None:
    """Return a MIME type detected from magic bytes, or ``None``.

    Recognizes only the allowed image formats. Explicitly does not accept
    SVG, PDF, or archive signatures.
    """
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if len(data) >= 12 and data[0:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return None


def validate_image(content_type: str | None, data: bytes) -> str:
    """Validate raw image bytes; return the confirmed MIME type.

    Raises :class:`ScreenshotValidationError` (with an HTTP status code) on
    any failure. Performs no storage and no provider call.
    """
    if not data:
        raise ScreenshotValidationError(400, "Empty upload body.")

    if len(data) > MAX_UPLOAD_BYTES:
        raise ScreenshotValidationError(413, "Image exceeds the 5 MB upload limit.")

    mime = _normalize_mime(content_type)
    if mime not in ALLOWED_MIME_TYPES:
        raise ScreenshotValidationError(
            415,
            "Unsupported media type. Allowed: image/png, image/jpeg, " "image/webp.",
        )

    detected = _detect_signature(data)
    if detected is None:
        raise ScreenshotValidationError(
            415, "Upload is not a valid PNG, JPEG, or WebP image."
        )
    if detected != mime:
        raise ScreenshotValidationError(
            415,
            "Declared content type does not match the image signature.",
        )

    return detected


def build_preview() -> ScreenshotAnalysisPreview:
    """Return a deterministic analysis-only preview.

    Content is static and advisory only — no AI provider, no OCR, and no
    dependence on image contents beyond successful validation. Mirrors the
    safe `/mobile` mock copy.
    """
    chart = ChartAnalysisResult(
        instrument="XAUUSD",
        timeframe="M15",
        trading_style="Intraday / paper only",
        market_bias=MarketBias.NEUTRAL_BULLISH,
        trend="Bullish short-term",
        key_levels=["Support 2,318-2,322", "Resistance 2,341-2,346"],
        momentum="Improving",
        volatility=RiskLevel.HIGH,
        pattern="Retest continuation candidate",
        confirmation_checklist=[
            "M15 close confirms",
            "Retest holds",
            "Momentum confirms",
            "Risk <= 1%",
        ],
    )
    plan = PaperGamePlan(
        scenario="Long only if confirmed",
        entry_zone="2,322 - 2,326 (example)",
        invalidation="M15 candle close below 2,316 (example)",
        take_profit_1="2,341 (example)",
        take_profit_2="2,352 (example)",
        max_risk_per_trade_pct=1.0,
    )
    risk = RiskAssessment(
        safety_score=82,
        risk_per_trade_pct=1.0,
        stop_loss_present=True,
        take_profit_present=True,
        overtrading_risk=RiskLevel.MEDIUM,
        news_risk=RiskLevel.HIGH,
    )
    return ScreenshotAnalysisPreview(
        chart_analysis=chart,
        paper_game_plan=plan,
        risk_assessment=risk,
    )


class ScreenshotAnalysisService:
    """Validate an uploaded screenshot and return an analysis-only preview."""

    def analyze(
        self, content_type: str | None, data: bytes
    ) -> ScreenshotAnalysisPreview:
        # Validate then discard the bytes — nothing is stored or logged.
        validate_image(content_type, data)
        return build_preview()
