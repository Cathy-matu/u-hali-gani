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


export function Book() {
  const { bookings, setBookings } = useApp()
  const [cs, setCs] = useState(null); const [c, setC] = useState(null); const [slot, setSlot] = useState(null); const [day, setDay] = useState(null); const [type, setType] = useState('Audio'); const [ok, setOk] = useState(false)
  useEffect(() => { bookingApi.counsellors().then(setCs) }, [])
  const confirm = async () => { const b = { id: Date.now(), who: c.name, when: `${fmt(day)} ${slot}`, type, status: 'Upcoming' }; await bookingApi.book(b); setBookings([b, ...bookings]); setOk(true); toast.success('Appointment booked') }
  if (!cs) return <Loading />
  return (<><h1 className="h3">Counsellors</h1>
    <div className="row g-3 mb-4">{cs.map(x => <div className="col-md-4" key={x.id}><Card className={c?.id === x.id ? 'border-success' : ''}><h3 className="h6">{x.name}</h3><button className="btn btn-soft" onClick={() => { setC(x); setSlot(null); setOk(false) }}>Choose</button></Card></div>)}</div>
    {c && !ok && <Card title={`Book with ${c.name}`}>
      <div className="mb-3" style={{ maxWidth: 380 }}><Calendar selected={day} onSelect={setDay} disabled={d => d < startOfToday() || [0, 6].includes(d.getDay())} /></div>
      <div className="mb-2">{slots.map(s => <button key={s} className={`btn me-1 mb-1 ${slot === s ? 'btn-teal' : 'btn-outline-teal'}`} onClick={() => setSlot(s)}>{s}</button>)}</div>
      <select aria-label="Appointment type" className="form-select mb-2" style={{ maxWidth: 240 }} value={type} onChange={e => setType(e.target.value)}>{[...c.modes, 'Video (coming later)'].map(m => <option key={m} disabled={m.startsWith('Video')}>{m}</option>)}</select>
      <button className="btn btn-teal" disabled={!slot || !day} onClick={confirm}>Confirm booking</button></Card>}
    {ok && <Card title="You’re booked"><p className="mb-0">{c.name}, {fmt(day)} {slot}, {type}. Your counsellor sees your pseudonym only.</p></Card>}
    <h2 className="h5 mt-4">Your appointments</h2>
    {bookings.length ? bookings.map(b => <div key={b.id} className="card-h d-flex justify-content-between align-items-center mb-2"><div><b>{b.who}</b><br /><small>{b.when} · {b.type}</small></div><div><Badge tone={b.status === 'Upcoming' ? 'green' : 'grey'}>{b.status}</Badge>{b.status === 'Upcoming' && <button className="btn btn-link" onClick={() => { setBookings(bookings.map(x => x.id === b.id ? { ...x, status: 'Cancelled' } : x)); toast('Appointment cancelled') }}>Cancel</button>}</div></div>) : <Empty title="No appointments" text="Booked sessions appear here." />}</>)
}

export default Book
