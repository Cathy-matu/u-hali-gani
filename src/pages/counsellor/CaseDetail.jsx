import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import toast from 'react-hot-toast'
import { Card, Stat, Risk as RiskBadge, Badge, Disclaimer, Modal, Loading } from '../../components/common/ui'
import Chat from '../../components/common/Chat'
import { cases, brief, appointmentsC } from '../../data/mock'
import Calendar, { iso, fmt } from '../../components/forms/Calendar'


export function CaseDetail() {
  const { id } = useParams(); const c = cases.find(x => x.id === id) || cases[0]
  const [b, setB] = useState(null); const [busy, setBusy] = useState(false); const [reveal, setReveal] = useState(false); const [note, setNote] = useState('')
  const data = c.phq.map((v, i) => ({ w: `W${i + 1}`, PHQ: v, GAD: c.gad[i] }))
  const gen = () => { setBusy(true); setTimeout(() => { setB(brief); setBusy(false); toast.success('Draft brief generated') }, 1500) }
  return (<><div className="d-flex justify-content-between align-items-center flex-wrap gap-2"><h1 className="h3">{c.id} <RiskBadge r={c.risk} /></h1>
      <div><button className="btn btn-teal me-2" onClick={gen} disabled={busy}>{busy ? 'Generating…' : 'Generate Case Brief'}</button><button className="btn btn-outline-teal" onClick={() => setReveal(true)}>Request identity disclosure</button></div></div>
    {busy && <Loading text="Preparing draft brief…" />}
    {b && <Card title="Pre-session brief (draft)" className="my-3"><Disclaimer>AI-generated draft for counsellor review. It does not diagnose and is not a clinical decision.</Disclaimer>
      <p className="mt-3">{b.summary}</p><b>Observations</b><ul>{b.observations.map(o => <li key={o}>{o}</li>)}</ul><b>Suggested topics</b><ul className="mb-0">{b.topics.map(o => <li key={o}>{o}</li>)}</ul></Card>}
    <div className="row g-3 mt-1"><div className="col-lg-7"><Card title="Score trends (screening)"><div style={{ height: 240 }}><ResponsiveContainer><LineChart data={data}><XAxis dataKey="w" /><YAxis /><Tooltip /><Legend /><Line dataKey="PHQ" stroke="#087E83" strokeWidth={2} /><Line dataKey="GAD" stroke="#B7791F" strokeWidth={2} /></LineChart></ResponsiveContainer></div></Card></div>
      <div className="col-lg-5"><Card title="Timeline">{['Weekly check-in: scores rose', 'Booked session (audio)', 'Message sent to student', 'Mood logged: Low'].map(t => <div className="border-top py-1 small" key={t}>{t}</div>)}</Card></div>
      <div className="col-md-6"><Card title="Sessions and bookings">{['Previous: 3 sessions, last 9 days ago', `Next: ${c.next}`, 'Check-in plan agreed'].map(t => <div className="border-top py-1 small" key={t}>{t}</div>)}</Card></div>
      <div className="col-md-6"><Card title="Mood and communication">{['Mood: Okay, Low, Low, Okay', 'Last message from student: today 08:12', 'Last reply sent: yesterday'].map(t => <div className="border-top py-1 small" key={t}>{t}</div>)}</Card></div>
      <div className="col-12"><Card title="Counsellor notes"><textarea aria-label="Notes" className="form-control mb-2" rows={3} value={note} onChange={e => setNote(e.target.value)} placeholder="Private session notes (demo, not saved to a server)" /><button className="btn btn-soft" onClick={() => toast.success('Note saved locally')}>Save note</button></Card></div></div>
    <Modal open={reveal} onClose={() => setReveal(false)} title="Identity disclosure"><p>Identity can only be revealed under the formal emergency protocol for imminent risk. Requests need a second authoriser and are audit-logged.</p><button className="btn btn-danger" onClick={() => { setReveal(false); toast('Request sent for authorisation (demo)') }}>Submit protocol request</button></Modal></>)
}

export default CaseDetail
