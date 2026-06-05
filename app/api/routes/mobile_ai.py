"""MOBILE-AI-007B — Mobile AI screenshot upload analysis route.

Exposes a single analysis-only endpoint that accepts raw image bytes (PNG /
JPEG / WebP), validates them, and returns a deterministic paper-only preview.

Safety posture (MOBILE-AI-007A contract):
  * read-only / analysis-only — no order, no broker call, no execution,
  * no image storage / persistence, no image logging,
  * no AI provider call, no network call, no database write.

Raw bytes are read from the request body (no multipart / python-multipart
dependency). The body is size-capped while streaming so an oversized upload is
rejected without being fully buffered.
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.schemas.mobile_ai import ScreenshotAnalysisPreview
from app.services.screenshot_analysis import (
    MAX_UPLOAD_BYTES,
    ScreenshotAnalysisService,
    ScreenshotValidationError,
)

router = APIRouter(tags=["mobile-ai"])

_service = ScreenshotAnalysisService()


async def _read_capped_body(request: Request) -> bytes:
    """Read the request body, aborting if it exceeds ``MAX_UPLOAD_BYTES``.

    Streams chunks so an oversized payload is never fully buffered.
    """
    # Fast reject using Content-Length when the client provides it.
    declared = request.headers.get("content-length")
    if declared is not None:
        try:
            if int(declared) > MAX_UPLOAD_BYTES:
                raise ScreenshotValidationError(
                    413, "Image exceeds the 5 MB upload limit."
                )
        except ValueError:
            raise ScreenshotValidationError(400, "Invalid Content-Length.")

    chunks: list[bytes] = []
    total = 0
    async for chunk in request.stream():
        total += len(chunk)
        if total > MAX_UPLOAD_BYTES:
            raise ScreenshotValidationError(413, "Image exceeds the 5 MB upload limit.")
        chunks.append(chunk)
    return b"".join(chunks)


@router.post(
    "/mobile/ai/screenshot/preview",
    response_model=ScreenshotAnalysisPreview,
)
async def screenshot_preview(request: Request):
    """Analyze an uploaded chart screenshot (analysis only, paper only).

    Accepts raw image bytes with an ``image/png``, ``image/jpeg``, or
    ``image/webp`` content type (max 5 MB). Validates MIME + magic signature,
    then returns a deterministic analysis-only preview. The image is never
    stored, never logged, and never sent to an AI provider. This endpoint
    performs no order placement, no broker call, and no trade execution.
    """
    try:
        body = await _read_capped_body(request)
        return _service.analyze(request.headers.get("content-type"), body)
    except ScreenshotValidationError as exc:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
