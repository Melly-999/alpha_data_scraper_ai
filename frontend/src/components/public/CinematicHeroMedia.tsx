import { useEffect, useState } from "react";

/**
 * CinematicHeroMedia — PUBLIC-SITE-001 / MEDIA-WIRING-PREP-001
 *
 * Video-with-poster-fallback media primitive for hero bands. No Higgsfield
 * media was generated in this run — this renders a CSS-driven placeholder
 * shell by default and accepts optional `posterSrc`/`videoSrc` props so a
 * later media-generation run can drop in real assets without touching this
 * component's call sites. Decorative only (`aria-hidden`); all hero content
 * is duplicated as real text by the caller (see `HeroAIOSShowcase`,
 * `CaseStudyPage`).
 *
 * Per the design pack's mobile rule ("static image on small viewports, no
 * autoplay video") and standard reduced-motion practice, an autoplaying
 * video is only ever rendered when a `videoSrc` is provided AND the visitor
 * is neither on a small viewport nor has `prefers-reduced-motion: reduce`
 * set — otherwise this falls back to the poster image (or the static
 * placeholder if no poster is provided either).
 */
type CinematicHeroMediaProps = {
  posterSrc?: string;
  videoSrc?: string;
};

const MOBILE_VIEWPORT_QUERY = "(max-width: 768px)";
const REDUCED_MOTION_QUERY = "(prefers-reduced-motion: reduce)";

function useMatchMedia(query: string): boolean {
  const [matches, setMatches] = useState(
    () => typeof window !== "undefined" && window.matchMedia(query).matches,
  );

  useEffect(() => {
    const mql = window.matchMedia(query);
    const onChange = (event: MediaQueryListEvent) => setMatches(event.matches);
    setMatches(mql.matches);
    mql.addEventListener("change", onChange);
    return () => mql.removeEventListener("change", onChange);
  }, [query]);

  return matches;
}

export function CinematicHeroMedia({ posterSrc, videoSrc }: CinematicHeroMediaProps) {
  const prefersReducedMotion = useMatchMedia(REDUCED_MOTION_QUERY);
  const isMobileViewport = useMatchMedia(MOBILE_VIEWPORT_QUERY);
  const canAutoplayVideo = Boolean(videoSrc) && !prefersReducedMotion && !isMobileViewport;

  if (canAutoplayVideo) {
    return (
      <video
        className="public-hero__media"
        aria-hidden="true"
        muted
        loop
        playsInline
        autoPlay
        poster={posterSrc}
        preload="none"
      >
        <source src={videoSrc} type="video/mp4" />
      </video>
    );
  }

  if (posterSrc) {
    return (
      <img
        className="public-hero__media"
        src={posterSrc}
        alt=""
        aria-hidden="true"
      />
    );
  }

  // Static CSS-driven placeholder shell — no external assets required.
  return (
    <div
      className="public-hero__media"
      aria-hidden="true"
      style={{
        background:
          "radial-gradient(circle at 50% 35%, rgba(245,165,36,0.14), transparent 42%)," +
          "radial-gradient(circle at 30% 70%, rgba(79,209,197,0.08), transparent 38%)," +
          "linear-gradient(180deg, #0b0f14 0%, #070a0f 100%)",
      }}
    />
  );
}
