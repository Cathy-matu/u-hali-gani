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


export function Resources() {
  const [q, setQ] = useState(''); const [cat, setCat] = useState('All'); const [open, setOpen] = useState(null)
  const cats = ['All', ...new Set(resources.map(r => r.cat))]
  const list = resources.filter(r => (cat === 'All' || r.cat === cat) && (r.title + r.body).toLowerCase().includes(q.toLowerCase()))
  return (<><h1 className="h3">Wellbeing resources</h1>
    <div className="d-flex gap-2 flex-wrap mb-3"><div className="position-relative"><Search size={16} className="position-absolute" style={{ top: 14, left: 12 }} /><input aria-label="Search resources" className="form-control ps-5" value={q} onChange={e => setQ(e.target.value)} placeholder="Search" /></div>
      {cats.map(c => <button key={c} className={`btn ${cat === c ? 'btn-teal' : 'btn-soft'}`} onClick={() => setCat(c)}>{c}</button>)}</div>
    {list.length ? <div className="row g-3">{list.map(r => <div className="col-md-4" key={r.id}><Card><Badge tone="green">{r.cat}</Badge><h3 className="h6 mt-2">{r.title}</h3><button className="btn btn-link p-0" onClick={() => setOpen(r)}>Read more</button></Card></div>)}</div> : <Empty title="No matches" text="Try a different word or category." />}
    <Modal open={!!open} onClose={() => setOpen(null)} title={open?.title}><p>{open?.body}</p><Disclaimer>Supportive information, not a substitute for professional care.</Disclaimer></Modal></>)
}

export default Resources
