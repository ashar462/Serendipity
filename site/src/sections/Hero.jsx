/* Hero — geometry from Figma (frame 247:1092, zone y 0–960):
   · video bg 'Comp 2 1' 1920×960 @ (0,0)          → /assets/hero-video.mp4
   · 'Rectangle 872' gradient 1920×741 @ y=219      → fade to forest #001A18
   · headline 'The Marsden Rhythm: / Nature, Refined.'
     Rethink Sans Medium 66px · lh 79.2 · ls 6.6 · uppercase · center · #000
   · content block 'Frame 36' 1936×752 @ y=113 (internals pending JSON restore) */
export default function Hero() {
  return (
    <section id="hero" style={{ position: 'relative', width: '100%', height: 960, background: 'var(--forest-950)' }}>
      {/* video background */}
      <video
        autoPlay
        muted
        loop
        playsInline
        style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover' }}
        src="/assets/hero-video.mp4"
      />

      {/* bottom gradient fade (Rectangle 872) */}
      <div
        style={{
          position: 'absolute', left: 0, top: 219,
          width: '100%', height: 741,
          background: 'linear-gradient(180deg, rgba(0,26,24,0) 0%, #001A18 96%)',
        }}
      />

      {/* headline block (Frame 36 — centered zone y 113–865) */}
      <div
        style={{
          position: 'absolute', left: 0, top: 0, width: '100%', height: '100%',
          display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
        }}
      >
        <h1 className="t-hero-66" style={{ color: '#000', textAlign: 'center' }}>
          The Marsden Rhythm:<br />
          Nature, Refined.
        </h1>
      </div>
    </section>
  )
}
