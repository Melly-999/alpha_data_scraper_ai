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

The analysis result itself is produced by the pluggable provider layer
(``app/services/mobile_ai_provider.py``, MOBILE-AI-008B), which defaults to a
deterministic mock and degrades to a safe stub.
"""

from __future__ import annotations

from app.schemas.mobile_ai import ScreenshotAnalysisPreview
from app.services.mobile_ai_provider import run_analysis

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


class ScreenshotAnalysisService:
    """Validate an uploaded screenshot and return an analysis-only preview."""

    def analyze(
        self, content_type: str | None, data: bytes
    ) -> ScreenshotAnalysisPreview:
        # Validate, then hand the bytes to the provider layer for analysis.
        # Nothing is stored or logged; the provider defaults to a deterministic
        # mock and degrades to a safe stub on any error.
        mime = validate_image(content_type, data)
        return run_analysis(data, mime)
