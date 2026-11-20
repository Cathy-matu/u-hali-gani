import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Phone, Search } from 'lucide-react'
import { Card, Badge, Empty, Loading, Disclaimer, Modal, Risk } from '../../components/common/ui'
import Chat from '../../components/common/Chat'
import { useApp } from '../../context/AuthContext'
import { moods, moodHistory, resources, counsellors, slots, helpContacts, assistantReplies } from '../../data/mock'
import { SHORT, FULL, FREQ, WHO_OPT } from '../../data/instruments'
import { scoreAll, routeRisk } from '../../utils/scoring'
import Calendar, { fmt, startOfToday } from '../../components/forms/Calendar'
import { checkinApi, assessmentApi, bookingApi, consentApi } from '../../services/api'


export function Help() {
  const [t, setT] = useState(1)
  const L = ['Always-available information', 'Talk to an on-duty counsellor', 'High-risk support', 'Imminent risk: emergency protocol']
  return (<><h1 className="h3">Get help now</h1><Disclaimer>Hali is not an emergency service. If someone is in immediate danger, contact campus security or local emergency services. Numbers below are unverified placeholders.</Disclaimer>
    <div className="d-flex gap-2 flex-wrap my-3">{L.map((l, i) => <button key={l} className={`btn ${t === i ? 'btn-teal' : 'btn-soft'}`} onClick={() => setT(i)}>Tier {i}</button>)}</div>
    <Card title={L[t]}>{t === 1 && <p>An on-duty counsellor can pick up with your pseudonym and recent check-in already shared. <button className="btn btn-teal ms-2" onClick={() => toast.success('Counsellor notified (demo)')}>Connect me now</button></p>}
      {t === 2 && <p>Take a moment to breathe. You deserve support from a person. Use the contacts below or connect with a counsellor.</p>}
      {t === 3 && <p>In a situation of imminent risk, the break-glass protocol lets a trained human team reveal your identity to protect your safety. Every use is logged and reviewed.</p>}
      {t === 0 && <p>Your campus counselling centre, clinic and security team are listed below.</p>}
      {helpContacts.filter(c => c.tier <= t || t === 0 && c.tier === 0).map(c => <div key={c.label} className="d-flex justify-content-between align-items-center border-top py-2"><div>{c.label}<br /><small className="muted">{c.tel}</small></div><a className="btn btn-outline-teal" href={`tel:${c.tel.replace(/ /g, '')}`}><Phone size={16} />Call</a></div>)}</Card></>)
}

export default Help
