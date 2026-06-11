# MellyTrade Brand Asset Pack (v1, draft-review)

First production-ready vector asset pack implementing the approved MellyTrade
visual identity. Source of truth:

- [mellytrade_visual_identity_board_summary.md](../../mellytrade_visual_identity_board_summary.md)
- [mellytrade_visual_identity_prompt_pack.md](../../mellytrade_visual_identity_prompt_pack.md)

## Approved hierarchy

| Role | Identity | Asset |
| --- | --- | --- |
| Primary official | MT pixel monogram + MellyTrade wordmark | `mellytrade_logo_horizontal_dark.svg`, `mellytrade_logo_stacked_dark.svg`, `mellytrade_mt_monogram.svg` |
| Secondary | Terminal badge / subtle mascot reference | `mellytrade_terminal_badge.svg` |
| Community | Melly Pet head / upper-body mascot | `melly_pet_community_badge.svg` |

**Mascot rule:** Melly Pet is secondary/community only. It is never the
primary official logo. The official MellyTrade mark is always MT monogram +
wordmark.

## Files

| File | Type | Intended use |
| --- | --- | --- |
| `mellytrade_logo_horizontal_dark.svg` | Official logo (horizontal, dark) | GitHub, README header, website header, app header |
| `mellytrade_logo_stacked_dark.svg` | Official logo (stacked, dark) | Splash screen, README intro, app intro |
| `mellytrade_mt_monogram.svg` | Monogram tile | Favicon/app icon base, small official marks |
| `mellytrade_terminal_badge.svg` | Secondary terminal badge | README banners, product-safe brand moments |
| `melly_pet_community_badge.svg` | Community mascot badge | Discord avatar, community/social surfaces only |
| `preview_contact_sheet.svg` | Generated preview | Review convenience only — not a brand mark |
| `asset_manifest.json` | Metadata | Structured asset inventory |

## Recommended usage

- **GitHub / README / website / app header:** horizontal official logo.
- **Splash / intro:** stacked official logo.
- **Favicon / app icon:** export from `mellytrade_mt_monogram.svg`
  (16/32/64/128/256/512/1024 px).
- **Discord / community avatars:** `melly_pet_community_badge.svg` only.
- **Wallpapers:** not in this pack (deferred to a later approved export task).

## Do / Don't

**Do**

- Keep black/charcoal (`#070A0D`, `#10151B`, `#161C23`) as the dominant field.
- Lead official surfaces with the MT monogram + wordmark.
- Reserve orange (`#F27A4D`) for the monogram accent, mascot system, and one
  focal highlight; amber/gold (`#D6A84F`/`#E1B45A`) for premium safety accents.
- Show safety posture with calm terminal badges
  (READ ONLY / PAPER SANDBOX / AI WORKSPACE).

**Don't**

- Don't use Melly Pet as the official logo or in official headers/product chrome.
- Don't use a large full-body mascot as the brand mark.
- Don't place tiny wordmarks inside social icons or favicons.
- Don't add casino/gambling, crypto-hype, or hype-finance visual language.
- Don't depict buy/sell/order/execute controls, broker execution, live-trading
  UX, or profit promises in any brand visual.
- Don't include secrets, credentials, or account IDs in any asset.

## Typography note

SVGs use editable `<text>` elements with fallback stacks
(`Space Grotesk, Sora, Geist, Inter, Arial, sans-serif` for the wordmark;
`JetBrains Mono, IBM Plex Mono, Space Mono, Consolas, monospace` for terminal
labels). **No font files are bundled.** For final production export, outline
text to paths in Figma/Illustrator so rendering does not depend on installed
fonts.

## Export guidance (later task)

PNG/ICO favicon sets, social-size PNGs, and wallpapers are intentionally not
committed yet. After visual approval, generate them in a dedicated asset
export task (small, reviewed binaries only). The Open Design evidence board
remains stored locally outside the repository.

## Palette reference

`#070A0D` deep background · `#10151B` terminal charcoal · `#161C23` panel
charcoal · `#0D1117` suit black · `#2A313A` suit highlight · `#F27A4D` mascot
orange · `#FF9A6A` soft orange · `#D6A84F` premium amber · `#E1B45A` warm gold
· `#F4F6F8` primary white · `#7B8491` muted cool gray · `#4B5563` secondary
slate
