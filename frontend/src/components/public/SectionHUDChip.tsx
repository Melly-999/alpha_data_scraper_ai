import { useEffect, useState } from "react";

/**
 * SectionHUDChip — PUBLIC-SITE-001
 *
 * Small fixed chip showing the current landing-page section name plus the
 * static safety badges. Hidden on mobile per the design pack's mobile
 * rules (badges instead render inline at the top of each section there).
 * Purely presentational — observes section elements already in the DOM,
 * no network calls.
 */
const SECTION_IDS = [
  "hero",
  "snapshot",
  "aios-preview",
  "safety-contract",
  "product-previews",
  "github-evidence",
  "mobile-pwa",
  "cta",
] as const;

const SECTION_LABELS: Record<string, string> = {
  hero: "Hero",
  snapshot: "Product Snapshot",
  "aios-preview": "AIOS Preview",
  "safety-contract": "Safety Contract",
  "product-previews": "Product Previews",
  "github-evidence": "GitHub Evidence",
  "mobile-pwa": "Mobile / PWA",
  cta: "Get In Touch",
};

export function SectionHUDChip() {
  const [activeSection, setActiveSection] = useState<string>("hero");

  useEffect(() => {
    const elements = SECTION_IDS.map((id) => document.getElementById(id)).filter(
      (el): el is HTMLElement => Boolean(el),
    );
    if (elements.length === 0) {
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
        if (visible?.target.id) {
          setActiveSection(visible.target.id);
        }
      },
      { rootMargin: "-40% 0px -50% 0px", threshold: [0, 0.25, 0.5, 0.75, 1] },
    );

    elements.forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, []);

  return (
    <div className="public-hud-chip" aria-hidden="true">
      <span className="public-hud-chip__section">
        {SECTION_LABELS[activeSection] ?? "MellyTrade"}
      </span>
      <span className="public-hud-chip__badges">
        <span>READ ONLY</span>
        <span>PAPER</span>
        <span>ORDERS BLOCKED</span>
      </span>
    </div>
  );
}
