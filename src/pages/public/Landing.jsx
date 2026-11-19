import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Logo, Card, Disclaimer } from '../../components/common/ui'
import { useApp } from '../../context/AuthContext'
import { authApi } from '../../services/api'
import { PSEUDONYM } from '../../data/mock'

const faqs = [['Is Hali anonymous?', 'Yes by default. Your identity is only revealed under a defined emergency protocol for imminent risk.'], ['Is Hali a diagnosis?', 'No. Check-ins are screening tools that help route you to a human counsellor.'], ['Is Hali an emergency service?', 'No. If you or someone else is in immediate danger, contact campus security or local emergency services.']]

export function Landing() {
  return (
    <div className="container py-3">
      <header className="d-flex justify-content-between align-items-center mb-4"><Logo /><Link to="/login" className="btn btn-outline-teal">Try the demo</Link></header>
      <section className="hero mb-5">
        <h1>Your wellbeing matters. Your privacy comes first.</h1>
        <p className="fs-5 my-3" style={{ maxWidth: 560 }}>Hali helps you notice how you are doing, then connects you with a human counsellor at your university when you want support.</p>
        <Link to="/onboarding" className="btn btn-teal me-2">Start a check-in</Link>
        <a href="#how" className="btn btn-outline-teal">Explore how Hali works</a>
      </section>
      <section id="how" className="row g-3 mb-5">
        {[['Check in anonymously', 'A short weekly questionnaire under a pseudonym.'], ['Get routed to the right support', 'Self-help resources, a counsellor booking, or an immediate human handoff.'], ['Talk to a person', 'Counsellors see your pseudonym and your trends, never a chatbot’s verdict.']].map(([t, d]) => <div className="col-md-4" key={t}><Card title={t}>{d}</Card></div>)}
      </section>
      <section className="row g-3 mb-5">
        <div className="col-md-6"><Card title="Privacy and safety">Administrators only ever see aggregates, and groups under 10 students are hidden. Anonymity can be broken only under the emergency protocol.</Card></div>
        <div className="col-md-6"><Card title="Counselling services">In-person, audio and text sessions. Video is planned for a future release.</Card></div>
      </section>
      <section className="mb-5"><h2 className="h4">Frequently asked questions</h2>
        {faqs.map(([q, a]) => <details key={q} className="card-h mb-2"><summary>{q}</summary><p className="mb-0 mt-2">{a}</p></details>)}</section>
      <Disclaimer>Hali supports students but does not replace professional counselling or emergency services.</Disclaimer>
      <footer className="py-4 muted small">© Hali demo. Frontend prototype with synthetic data.</footer>
    </div>
  )
}

export default Landing
