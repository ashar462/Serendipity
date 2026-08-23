/* Header — geometry from Figma (frame 247:1092):
   · logo 'Vector' 128×32 @ (896, 34) — horizontally centered
   · menu 'Component 2' 188×49 @ (140, 21)
   (refine pass once bridge JSON returns exact internals) */
export default function Header() {
  return (
    <header
      style={{
        position: 'absolute',
        top: 0, left: 0,
        width: '100%', height: 100,
        zIndex: 50,
      }}
    >
      {/* menu pill — 188×49 @ x=140 */}
      <button
        type="button"
        style={{
          position: 'absolute',
          left: 140, top: 21,
          width: 188, height: 49,
          display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: 10,
          border: '1px solid rgba(255,255,255,.45)',
          borderRadius: 999,
        }}
        className="menu-btn"
        aria-label="Menu"
      >
        <span style={{ display: 'inline-block', width: 18, height: 2, background: 'currentColor', boxShadow: '0 5px 0 currentColor, 0 -5px 0 currentColor' }} />
        <span className="t-label-19" style={{ fontSize: 14, letterSpacing: 2 }}>MENU</span>
      </button>

      {/* logo — 128×32 @ (896,34), horizontally centered */}
      <a
        href="/"
        style={{ position: 'absolute', left: 896, top: 34, width: 128, height: 32, display: 'block' }}
        aria-label="Serendipity home"
      >
        <img src="/assets/logo.png" alt="Serendipity" style={{ width: 128, height: 32, objectFit: 'contain' }} />
      </a>
    </header>
  )
}
