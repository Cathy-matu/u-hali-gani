import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Phone, Search } from 'lucide-react'
import { Card, Badge, Empty, Loading, Disclaimer, Modal, Risk } from '../../components/common/ui'
import Chat from '../../components/common/Chat'
import { useApp } from '../../context/AuthContext'
import { PSEUDONYM, moods, moodHistory, resources, counsellors, slots, helpContacts, assistantReplies } from '../../data/mock'
import { SHORT, FULL, FREQ, WHO_OPT } from '../../data/instruments'
import { scoreAll, routeRisk } from '../../utils/scoring'
import Calendar, { fmt, startOfToday } from '../../components/forms/Calendar'
import { checkinApi, assessmentApi, bookingApi, consentApi } from '../../services/api'


export function Dashboard() {
  const { risk, bookings } = useApp(); const next = bookings.find(b => b.status === 'Upcoming')
  return (<>
    <h1 className="h3">Hello, {PSEUDONYM}</h1><p className="muted">Your privacy status: anonymous. Nobody at the university can see your name.</p>
    <div className="row g-3">
      <div className="col-lg-6"><Card title="Wellbeing overview">{risk ? <p>Latest weekly check-in: <Risk r={risk} /></p> : <Empty title="No weekly check-in yet" text="It takes about two minutes. Skip any week you need to." to="/student/assessment" cta="Start check-in" />}</Card></div>
      <div className="col-lg-6"><Card title="Upcoming appointment">{next ? <p className="mb-0"><b>{next.who}</b><br />{next.when} · {next.type}</p> : <Empty title="Nothing booked" text="Choose a counsellor when you feel ready." to="/student/book" cta="Find a counsellor" />}</Card></div>
      <div className="col-lg-6"><Card title="Quick mood" action={<Link to="/student/mood">Open</Link>}><div className="d-flex gap-2 flex-wrap">{moods.map(([n, e]) => <Link key={n} to="/student/mood" className="mood text-decoration-none" aria-label={n}>{e}</Link>)}</div></Card></div>
      <div className="col-lg-6"><Card title="Message from your counsellor"><p className="mb-1">“Looking forward to Friday. Bring anything you want to talk about.”</p><small className="muted">Dr. Amina Wekesa · yesterday</small></Card></div>
      <div className="col-12"><Card title="Recent activity">{['Mood logged: Okay (Thu)', 'Weekly check-in completed (Mon)', 'Booked: Dr. Amina Wekesa'].map(t => <div key={t} className="border-top py-1 small">{t}</div>)}</Card></div>
      <div className="col-12"><Card title="Suggested for you" action={<Link to="/student/resources">All resources</Link>}><div className="row g-2">{resources.slice(0, 3).map(r => <div className="col-md-4" key={r.id}><Link to="/student/resources" className="text-decoration-none"><Badge tone="green">{r.cat}</Badge><div className="mt-1">{r.title}</div></Link></div>)}</div></Card></div>
    </div></>)
}

export default Dashboard
