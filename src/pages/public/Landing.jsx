import { ArrowDown, ArrowRight, HeartHandshake, ShieldCheck, Sparkles, UsersRound } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import { Logo, Disclaimer } from '../../components/common/ui'
import { useApp } from '../../context/AuthContext'

const faqs = [
  ['Is Hali anonymous?', 'The design uses pseudonymous student-facing identifiers. This prototype does not implement production anonymity controls or an emergency identity-release workflow.'],
  ['Is Hali a diagnosis?', 'No. Check-ins are screening tools that can help connect you with a human counsellor.'],
  ['Is Hali an emergency service?', 'No. Support contacts in this prototype are placeholders and must be replaced with verified campus and local services before real-world use. If someone is in immediate danger, contact verified emergency services.'],
]

const waysToConnect = [
  { icon: Sparkles, title: 'Check in, at your pace', text: 'Short wellbeing check-ins help you pause and notice what’s going on.' },
  { icon: HeartHandshake, title: 'Reach a real person', text: 'Explore university counselling and decide what kind of support feels right.' },
  { icon: UsersRound, title: 'Find your community', text: 'Discover clubs, societies and sports where new people are welcome.' },
]

const scrollToSection = (event, sectionId) => {
  event.preventDefault()
  document.getElementById(sectionId)?.scrollIntoView({ behavior: 'instant', block: 'start' })
}

export function Landing() {
  const { startDemo } = useApp()
  const go = useNavigate()
  const preview = role => {
    startDemo(role)
    go(`/${role}`)
  }

  return (
    <div className="landing-page">
      <header className="landing-header">
        <Link to="/" aria-label="Hali home"><Logo /></Link>
        <nav className="landing-nav" aria-label="Main navigation">
          <a href="#about" onClick={event => scrollToSection(event, 'about')}>About Hali</a>
          <a href="#communities" onClick={event => scrollToSection(event, 'communities')}>Campus life</a>
          <Link to="/login">Sign in</Link>
          <Link to="/onboarding" className="landing-nav-cta">Create your account <ArrowRight size={16} /></Link>
        </nav>
      </header>

      <main>
        <section className="landing-hero">
          <div className="landing-hero-copy">
            <span className="landing-eyebrow"><span /> A LITTLE MORE WELL, TOGETHER</span>
            <h1>Your wellbeing belongs here.</h1>
            <p>University life can be a lot. Hali helps you check in with yourself, find human support, and feel a little more at home on campus.</p>
            <div className="landing-hero-actions">
              <button type="button" className="landing-primary-button" onClick={() => preview('student')}>Preview student space <ArrowRight size={18} /></button>
              <button type="button" className="landing-secondary-button" onClick={() => preview('counsellor')}>Preview counsellor workspace</button>
            </div>
            <div className="landing-hero-actions">
              <button type="button" className="landing-secondary-button" onClick={() => preview('lecturer')}>Preview lecturer sessions</button>
              <button type="button" className="landing-secondary-button" onClick={() => preview('researcher')}>Preview research dashboard</button>
            </div>
            <p className="landing-trust-note">No sign-in required · Uses sample data for presentations.</p>
            <div className="landing-trust-note"><ShieldCheck size={17} /> Your care journey is yours to shape.</div>
          </div>
          <div className="landing-photo-collage" aria-label="Students spending time together on campus">
            <img className="landing-photo-main" src="/images/campus-friends-talking.jpg" alt="Black and other university students sharing a laugh together" />
            <img className="landing-photo-small" src="/images/campus-friends-high-five.jpg" alt="Friends greeting each other with a high five on campus" />
            <div className="landing-photo-caption"><span className="landing-caption-icon"><HeartHandshake size={18} /></span><span><strong>Good things grow together</strong><small>There’s room for you here.</small></span></div>
            <span className="landing-photo-star" aria-hidden="true">✳</span>
          </div>
        </section>

        <section className="landing-community-invite" id="communities">
          <div className="landing-community-image">
            <img src="/images/campus-friends-study.jpg" alt="Students sitting together and connecting on campus" loading="lazy" />
            <span className="landing-image-label">YOUR CAMPUS, YOUR PEOPLE</span>
          </div>
          <div className="landing-community-copy">
            <span className="landing-eyebrow">BELONGING LOOKS DIFFERENT FOR EVERYONE</span>
            <h2>Find a place to plug in.</h2>
            <p>Maybe it’s a team, a cultural society, a creative space, or just a few familiar faces. Start with what you enjoy and see where it takes you.</p>
            <Link to="/onboarding" className="landing-text-link">Explore Hali <ArrowRight size={17} /></Link>
          </div>
        </section>

        <section className="landing-about" id="about">
          <div className="landing-about-copy">
            <span className="landing-eyebrow">A HUMAN-CENTRED WAY TO FEEL BETTER</span>
            <h2>Support for the whole you.</h2>
            <p>Hali brings wellbeing check-ins, practical resources, counselling connections and community discovery into one welcoming place. You choose where to begin, and you can take things one step at a time.</p>
            <a className="landing-about-link" href="#how" onClick={event => scrollToSection(event, 'how')}><span>See how Hali works</span><ArrowDown size={16} /></a>
          </div>
          <div className="landing-about-photo">
            <img src="/images/campus-friends-high-five.jpg" alt="Black university students interacting warmly outdoors" loading="lazy" />
            <span className="landing-about-note">You deserve to feel seen,<br />supported and at home.</span>
          </div>
        </section>

        <section className="landing-how" id="how">
          <div className="landing-section-heading">
            <span className="landing-eyebrow">YOUR NEXT STEP CAN BE A SMALL ONE</span>
            <h2>Care that meets you where you are.</h2>
            <p>Use the parts of Hali that feel helpful. Skip the rest until you’re ready.</p>
          </div>
          <div className="landing-way-grid">
            {waysToConnect.map(({ icon: Icon, title, text }, index) => (
              <article className="landing-way" key={title}>
                <span className="landing-way-icon"><Icon size={22} /></span>
                <span className="landing-way-number">0{index + 1}</span>
                <h3>{title}</h3>
                <p>{text}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="landing-assurance">
          <div className="landing-assurance-heading"><ShieldCheck size={23} /><h2>Your privacy and safety come first.</h2></div>
          <p>The prototype demonstrates intended student-centred privacy and support flows using sample data. Server-enforced access controls, live aggregate governance, verified support contacts and emergency escalation must be completed before it can handle real wellbeing data.</p>
          <div className="landing-faqs">
            <h3>Good to know</h3>
            {faqs.map(([question, answer]) => <details key={question}><summary>{question}</summary><p>{answer}</p></details>)}
          </div>
          <Disclaimer>Hali supports students but does not replace professional counselling or emergency services.</Disclaimer>
        </section>

        <section className="landing-final-cta">
          <span className="landing-eyebrow">YOU BELONG IN THE CONVERSATION</span>
          <h2>Start wherever you are.</h2>
          <p>Make an account when you’re ready. There’s no pressure to have it all figured out.</p>
          <Link to="/onboarding" className="landing-primary-button">Create your account <ArrowRight size={18} /></Link>
        </section>
      </main>

      <footer className="landing-footer">
        <Link to="/" aria-label="Hali home"><Logo size={23} /></Link>
        <p>© Hali · University wellbeing</p>
        <a href="https://www.pexels.com/" target="_blank" rel="noopener noreferrer">Student photos via Pexels</a>
      </footer>
    </div>
  )
}

export default Landing
