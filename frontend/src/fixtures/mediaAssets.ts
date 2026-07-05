/**
 * mediaAssets — MELLYTRADE-MEDIA-INTEGRATION-001
 *
 * Real, live paths to the accepted Higgsfield-generated hero/media assets
 * under `frontend/public/media/mellytrade/` (served by Vite at
 * `/media/mellytrade/*`). See `frontend/public/media/mellytrade/manifest.json`
 * for per-asset source prompt, model/settings, and safety-sweep notes, and
 * `docs/showcase/media_integration_001.md` for the integration QA writeup.
 *
 * Only the assets actually wired into a page below are imported by any
 * component today — `riskLayerActivation` and `productShowcaseFinale` are
 * documented here as available media for a future non-hero preview
 * section, per the design pack, but are not currently rendered anywhere.
 */
const MELLYTRADE_MEDIA_BASE = "/media/mellytrade";

export const MELLYTRADE_PUBLIC_MEDIA = {
  /** H0 — accepted hero image; also serves as Clip 1's poster frame. */
  heroImage: `${MELLYTRADE_MEDIA_BASE}/hero-command-core.png`,
  heroPoster: `${MELLYTRADE_MEDIA_BASE}/hero-command-core-poster.png`,
  /** C1 — "AIOS Assembly" (hero clip, desktop/non-reduced-motion only). */
  aiosAssembly: `${MELLYTRADE_MEDIA_BASE}/aios-assembly.mp4`,
  /** C2 — "Risk Layer Activation". Available; not wired into a page yet. */
  riskLayerActivation: `${MELLYTRADE_MEDIA_BASE}/risk-layer-activation.mp4`,
  /** C3 — "Product Showcase Finale". Available; not wired into a page yet. */
  productShowcaseFinale: `${MELLYTRADE_MEDIA_BASE}/product-showcase-finale.mp4`,
  /** File/section/poster mapping manifest, per the design pack's post-generation steps. */
  manifest: `${MELLYTRADE_MEDIA_BASE}/manifest.json`,
} as const;
