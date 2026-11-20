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


export function Mood() {
  const [sel, setSel] = useState(null); const [note, setNote] = useState(''); const [done, setDone] = useState(false); const [hist, setHist] = useState(moodHistory)
  const save = async () => { await checkinApi.saveMood({ sel, note }); setHist(h => [...h, ['Today', moods[sel][0]]]); setDone(true); toast.success('Mood saved') }
  if (done) return <Card title="Thanks for checking in"><p>Saved at {new Date().toLocaleString()}. Missing a day is completely fine.</p><button className="btn btn-soft" onClick={() => { setDone(false); setSel(null); setNote('') }}>Check in again</button></Card>
  return (<><h1 className="h3">How are you feeling?</h1>
    <Card><div className="d-flex gap-2 flex-wrap mb-3">{moods.map(([n, e], i) => <button key={n} className={`mood ${sel === i ? 'sel' : ''}`} aria-pressed={sel === i} onClick={() => setSel(i)}><div className="fs-2">{e}</div>{n}</button>)}</div>
      <label htmlFor="n" className="form-label">Anything to add? (optional)</label><textarea id="n" className="form-control mb-3" rows={2} value={note} onChange={e => setNote(e.target.value)} />
      <button className="btn btn-teal" disabled={sel === null} onClick={save}>Save mood</button></Card>
    <h2 className="h5 mt-4">Mood history</h2><div className="d-flex gap-2 flex-wrap">{hist.map(([d, m], i) => <Badge key={i}>{d}: {m}</Badge>)}</div></>)
}

export default Mood
