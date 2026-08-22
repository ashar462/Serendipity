/* Hero — Phase 1 target. Geometry source: Figma nodes 247:1248 (bg), 255:1937,
   247:1250 (logo), 247:1251 (menu), 247:1252 (content), 247:1093 (image bg). */
export default function Hero() {
  return (
    <section id="hero" style={{ position: 'relative', height: 960, background: 'var(--forest-950)' }}>
      <div style={{ position: 'absolute', inset: 0, display: 'grid', placeItems: 'center' }}>
        <h1 className="t-hero-66" style={{ textAlign: 'center' }}>
          The Marsden Rhythm:<br />Nature, Refined.
        </h1>
      </div>
    </section>
  )
}
