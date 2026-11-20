import { ArrowRight, BookOpen, CalendarDays, ClipboardCheck, Compass, Heart, HeartPulse, MessageCircle, Sparkles } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useApp } from '../../context/AuthContext'
import { resources } from '../../data/mock'
import { Risk } from '../../components/common/ui'

const shortcuts = [
  { to: '/student/mood', icon: HeartPulse, title: 'Check in with yourself', text: 'A quick mood check-in' },
  { to: '/student/assessment', icon: ClipboardCheck, title: 'Weekly check-in', text: 'Notice how you’re doing' },
  { to: '/student/book', icon: CalendarDays, title: 'Talk to a counsellor', text: 'Find the right support' },
]

export function Dashboard() {
  const { risk, bookings } = useApp()
  const next = bookings.find(booking => booking.status === 'Upcoming')
  const firstResource = resources[0]
  const hour = new Date().getHours()
  const greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening'

  return (
    <div className="student-dashboard">
      <header className="student-welcome">
        <div>
          <span className="dashboard-kicker">YOUR WELLBEING SPACE</span>
          <h1>{greeting}.</h1>
          <p>Take what you need today. There’s no right way to use Hali.</p>
        </div>
        <Link className="dashboard-privacy-link" to="/student/privacy"><Heart size={16} /> Your privacy matters</Link>
      </header>

      <section className="student-community-hero">
        <img src="/images/campus-friends-study.jpg" alt="Black and other students smiling and talking together" />
        <div className="student-community-hero-overlay" />
        <div className="student-community-hero-content">
          <span>GOOD THINGS GROW TOGETHER</span>
          <h2>Find your people.<br />Feel more at home.</h2>
          <p>From sports to societies, your next community could be one hello away.</p>
          <Link to="/student/communities" className="student-hero-button">Explore communities <ArrowRight size={17} /></Link>
        </div>
      </section>

      <section className="student-care-section" aria-labelledby="student-care-title">
        <div className="student-section-heading">
          <div><span className="dashboard-kicker">A LITTLE SUPPORT, YOUR WAY</span><h2 id="student-care-title">Where would you like to start?</h2></div>
        </div>
        <div className="student-shortcuts">
          {shortcuts.map(({ to, icon: Icon, title, text }) => (
            <Link to={to} className="student-shortcut" key={to}>
              <span className="student-shortcut-icon"><Icon size={20} /></span>
              <span className="student-shortcut-copy"><strong>{title}</strong><small>{text}</small></span>
              <ArrowRight className="student-shortcut-arrow" size={17} />
            </Link>
          ))}
        </div>
      </section>

      <div className="student-dashboard-lower">
        <section className="student-checkin-panel">
          <div className="student-lower-icon"><Sparkles size={20} /></div>
          <div>
            <span className="dashboard-kicker">YOUR CHECK-IN</span>
            <h2>A moment for you</h2>
            {risk ? <p>Your latest weekly check-in: <Risk r={risk} /></p> : <p>A private, two-minute check-in can help you notice how things are going.</p>}
            <Link to="/student/assessment">{risk ? 'View your check-in' : 'Start a check-in'} <ArrowRight size={16} /></Link>
          </div>
        </section>

        <section className="student-next-step-panel">
          <div className="student-lower-icon"><CalendarDays size={20} /></div>
          <div>
            <span className="dashboard-kicker">{next ? 'COMING UP' : 'WHEN YOU’RE READY'}</span>
            <h2>{next ? 'Your appointment' : 'Talk to someone'}</h2>
            {next ? <p>{next.who} · {next.when} · {next.type}</p> : <p>Choose a counsellor and a way to connect that works for you.</p>}
            <Link to="/student/book">{next ? 'View appointments' : 'Find a counsellor'} <ArrowRight size={16} /></Link>
          </div>
        </section>
      </div>

      <section className="student-resource-strip">
        <div className="student-resource-icon"><BookOpen size={19} /></div>
        <div className="student-resource-copy">
          <span className="dashboard-kicker">A GENTLE PLACE TO BEGIN</span>
          <h2>{firstResource?.title || 'Explore wellbeing resources'}</h2>
          <p>{firstResource?.body || 'Explore practical, supportive resources at your own pace.'}</p>
        </div>
        <Link to="/student/resources" aria-label="Explore all resources"><span>Explore resources</span><ArrowRight size={17} /></Link>
      </section>

      <div className="student-dashboard-footnote">
        <MessageCircle size={16} />
        <p>Hali can help you find support, but it isn’t an emergency service. <Link to="/student/help">Get urgent help</Link></p>
      </div>
    </div>
  )
}

export default Dashboard
