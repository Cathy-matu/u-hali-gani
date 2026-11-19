import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import toast from 'react-hot-toast'
import { Card, Stat, Risk as RiskBadge, Badge, Disclaimer, Modal, Loading } from '../../components/common/ui'
import Chat from '../../components/common/Chat'
import { cases, brief, appointmentsC } from '../../data/mock'
import Calendar, { iso, fmt } from '../../components/forms/Calendar'


export function Appointments() {
  const [list, setList] = useState(appointmentsC); const [view, setView] = useState('List'); const [tab, setTab] = useState('Confirmed'); const [sel, setSel] = useState(new Date())
  const dateOf = a => { const d = new Date(); d.setHours(0, 0, 0, 0); d.setDate(d.getDate() + a.off); return d }
  const on = d => list.filter(a => iso(dateOf(a)) === iso(d)).sort((x, y) => x.time.localeCompare(y.time))
  const ev = {}; list.forEach(a => { const k = iso(dateOf(a)); ev[k] = (ev[k] || 0) + 1 })
  const act = (a, status) => { setList(list.map(x => x.id === a.id ? { ...x, status } : x)); toast.success(status) }
  const Row = ({ a }) => <div className="card-h d-flex justify-content-between align-items-center mb-2 flex-wrap gap-2"><div><b>{a.student}</b><br /><small>{fmt(dateOf(a))} {a.time} · {a.type} · <Badge tone={a.status === 'Confirmed' ? 'green' : a.status === 'Requested' ? 'amber' : 'grey'}>{a.status}</Badge></small></div>
    <div>{a.status === 'Requested' && <button className="btn btn-teal me-1" onClick={() => act(a, 'Confirmed')}>Accept</button>}{['Requested', 'Confirmed'].includes(a.status) && <button className="btn btn-outline-teal" onClick={() => act(a, 'Cancelled')}>Cancel</button>}</div></div>
  const shift = n => { const d = new Date(sel); d.setDate(d.getDate() + n); setSel(d) }
  const mon = new Date(sel); mon.setDate(sel.getDate() - ((sel.getDay() + 6) % 7))
  return (<><h1 className="h3">Appointments</h1><div className="mb-3">{['List', 'Day', 'Week', 'Month'].map(v => <button key={v} className={`btn me-1 ${view === v ? 'btn-teal' : 'btn-soft'}`} onClick={() => setView(v)}>{v}</button>)}</div>
    {view === 'List' && <><div className="mb-3">{['Requested', 'Confirmed', 'Completed', 'Cancelled'].map(t => <button key={t} className={`btn me-1 ${tab === t ? 'btn-teal' : 'btn-outline-teal'}`} onClick={() => setTab(t)}>{t}</button>)}</div>
      {list.filter(a => a.status === tab).map(a => <Row key={a.id} a={a} />)}{!list.some(a => a.status === tab) && <p className="muted">Nothing here.</p>}</>}
    {view === 'Day' && <><div className="d-flex align-items-center gap-2 mb-3"><button className="btn btn-soft" onClick={() => shift(-1)}>Previous</button><b>{fmt(sel)}</b><button className="btn btn-soft" onClick={() => shift(1)}>Next</button></div>{on(sel).map(a => <Row key={a.id} a={a} />)}{!on(sel).length && <p className="muted">No sessions this day.</p>}</>}
    {view === 'Week' && <><div className="d-flex align-items-center gap-2 mb-3"><button className="btn btn-soft" onClick={() => shift(-7)}>Previous week</button><b>Week of {fmt(mon)}</b><button className="btn btn-soft" onClick={() => shift(7)}>Next week</button></div>
      <div className="row row-cols-1 row-cols-md-7 g-2">{Array.from({ length: 7 }, (_, i) => { const d = new Date(mon); d.setDate(mon.getDate() + i); return <div className="col" key={i}><div className="card-h p-2 h-100"><b className="small">{fmt(d)}</b>{on(d).map(a => <div key={a.id} className="small border-top mt-1 pt-1">{a.time}<br />{a.student}</div>)}</div></div> })}</div></>}
    {view === 'Month' && <div className="row g-3"><div className="col-md-6"><Calendar selected={sel} onSelect={d => { setSel(d); setView('Day') }} events={ev} /></div><div className="col-md-6 muted">Dots mark days with sessions. Select a day to open its schedule.</div></div>}</>)
}

export default Appointments
