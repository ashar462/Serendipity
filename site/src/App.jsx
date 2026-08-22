import Header from './components/Header.jsx'
import Hero from './sections/Hero.jsx'

/* Homepage section map — order & heights exactly from Figma frame 247:1092 (1920×9421).
   Each section gets built out in its own phase; heights/positions recorded from JSON. */
const SECTIONS = [
  { id: 'intro',      name: 'Intro — “Your Home Away from Home.”' },
  { id: 'location',   name: '“Hidden Away, Yet Close to Everything.”' },
  { id: 'rhythm',     name: '“Nature, Refined. Simple Living, Perfected.”' },
  { id: 'gallery',    name: '“Postcards from the Valley.”' },
  { id: 'amenities',  name: '“Off-Grid Peace. On-Grid Capability.”' },
  { id: 'guests',     name: '“Moments at Serendipity.” / “What Our Guests Say.”' },
  { id: 'cta',        name: '“The Escape is Calling”' },
  { id: 'brochure',   name: '“Download Your Guest Brochure”' },
  { id: 'footer',     name: 'Footer' },
]

export default function App() {
  return (
    <div className="page">
      <Header />
      <Hero />
      {SECTIONS.map((s) => (
        <section key={s.id} id={s.id} style={{ minHeight: 240, borderBottom: '1px solid #ffffff12', display: 'grid', placeItems: 'center' }}>
          <p className="t-body-19" style={{ opacity: 0.5 }}>{s.name} — <small>Phase: pending</small></p>
        </section>
      ))}
    </div>
  )
}
