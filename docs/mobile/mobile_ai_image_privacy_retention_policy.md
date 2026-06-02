# Mobile AI Image Privacy & Retention Policy (MOBILE-AI-007A)

**Type:** docs-only privacy/retention policy (no runtime code, no storage)

This policy governs how uploaded chart screenshots would be handled by a future
screenshot upload analysis endpoint (MOBILE-AI-007B). It is documentation only.
No storage, persistence, logging, or provider integration is added here.

Companion document: `docs/mobile/mobile_ai_screenshot_upload_safety_contract.md`.

---

## A. Default policy

- **Do not persist** uploaded screenshots by default.
- Process **in memory only** where possible.
- **No training use** of uploaded images.
- **No sharing** with third parties unless explicitly documented and approved.
- **No public links** to uploaded images.
- **No image logs** (do not write image bytes to logs or audit trails).

---

## B. If storage is later approved

Storage must not be added until these are defined and approved:

- explicit **opt-in** from the user,
- a defined **retention period**,
- a **deletion workflow**,
- **encryption at rest** if applicable,
- **access controls** (least privilege),
- **audit logs** for access (metadata only, never image bytes),
- **safe file IDs** generated server-side,
- **no original filename trust**,
- a **user deletion request path**.

---

## C. Provider policy

If AI provider integration is later approved (MOBILE-AI-008):

- provider calls must be **backend-only**,
- **no provider keys in the frontend**,
- the provider **data-use policy must be reviewed** before sending any image,
- **redact sensitive metadata** before sending where possible,
- **do not send** screenshots that contain secrets or account IDs,
- **document** explicitly if images are sent to a provider.

---

## D. Local / dev policy

- Local testing should use **synthetic / demo screenshots only**.
- **No real broker account screenshots.**
- **No private CV / personal screenshots.**
- **No secrets.**
- **No account IDs.**
- **No live trading screenshots with account identifiers.**

---

## E. User-facing privacy copy (draft for future UI)

- “We don’t store your screenshots by default. Images are analyzed and then
  discarded.”
- “Do not upload screenshots with account numbers, API keys, passwords, or
  broker credentials.”
- “Analysis only. Not financial advice. Paper plan only — no live orders.”
- “You can request deletion of any stored data if storage is ever enabled.”
- “MellyTrade never places orders from uploaded screenshots.”
