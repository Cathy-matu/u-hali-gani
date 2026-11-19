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

function Result({ r, sc, mode, go }) {
  const M = { green: ['Self-help resources', 'Your answers suggest things look manageable right now. These resources may help.', '/student/resources', 'Browse resources'], amber: ['We’d encourage you to talk to a counsellor', 'Your answers suggest some strain. Talking to a person can help, and booking takes a minute.', '/student/book', 'Book a counsellor'], red: ['Let’s get you to a person now', 'A human counsellor is being alerted. You do not need to explain everything again.', '/student/help', 'Connect with a counsellor now'] }[r]
  return (<Card title={M[0]}><Risk r={r} /><p className="mt-2">{M[1]}</p>
    {mode === 'full' && <p className="small">Scores: PHQ-9 {sc.phq}/27 · GAD-7 {sc.gad}/21 · WHO-5 wellbeing {sc.who * 4}/100. These help a counsellor see how you are doing. They are not a diagnosis.</p>}
    {r === 'red' && <div className="notice mb-3" style={{ background: 'var(--redbg)' }}><b>Warm handoff started (demo).</b> On-duty counsellor notified · estimated response: under 5 minutes. If you are in immediate danger, contact campus security or emergency services.</div>}
    <button className={`btn ${r === 'red' ? 'btn-danger' : 'btn-teal'}`} onClick={() => go(M[2])}>{M[3]}</button>
    <p className="small muted mt-3 mb-0">Screening, not diagnosis. Hali does not replace professional care.</p></Card>)
}

export function Assessment() {
  const { setRisk } = useApp(); const go = useNavigate()
  const [mode, setMode] = useState(null); const [i, setI] = useState(0); const [a, setA] = useState({}); const [res, setRes] = useState(null); const [busy, setBusy] = useState(false)
  const items = mode === 'full' ? FULL : SHORT
  const start = m => { setMode(m); setI(0); try { setA(JSON.parse(sessionStorage.getItem('hali-draft-' + m) || '{}')) } catch { setA({}) } }
  const pick = v => { const n = { ...a, [items[i].id]: v }; setA(n); sessionStorage.setItem('hali-draft-' + mode, JSON.stringify(n)) }
  const submit = async () => { setBusy(true); await assessmentApi.submit(a); const sc = scoreAll(a); const r = routeRisk(mode, sc); setRisk(r); setRes({ r, sc }); sessionStorage.removeItem('hali-draft-' + mode); setBusy(false) }
  if (res) return <Result {...res} mode={mode} go={go} />
  if (!mode) return (<><h1 className="h3">Weekly check-in</h1><div className="row g-3">
    <div className="col-md-6"><Card title="Quick check-in (5 questions)"><p>PHQ-2, GAD-2 and one safety question. About 1 minute.</p><button className="btn btn-teal" onClick={() => start('short')}>Start quick check-in</button></Card></div>
    <div className="col-md-6"><Card title="Full check-in (21 questions)"><p>PHQ-9, GAD-7 and WHO-5. About 5 minutes.</p><button className="btn btn-outline-teal" onClick={() => start('full')}>Start full check-in</button></Card></div></div>
    <div className="mt-3"><Disclaimer>This is a screening, not a diagnosis. You can stop at any time.</Disclaimer></div></>)
  const it = items[i]; const opts = it.scale === 'who' ? WHO_OPT : FREQ; const cur = a[it.id]
  return (<><h1 className="h3">Weekly check-in</h1><p className="muted">Over the last 2 weeks… ({it.inst})</p>
    <div className="progress mb-3" role="progressbar" aria-valuenow={i + 1} aria-valuemax={items.length}><div className="progress-bar" style={{ width: `${((i + 1) / items.length) * 100}%`, background: 'var(--teal)' }} /></div>
    <Card title={`Question ${i + 1} of ${items.length}`}><p className="fs-5">{it.text}</p>
      {opts.map((o, v) => <button key={o} className={`ans ${cur === v ? 'sel' : ''}`} aria-pressed={cur === v} onClick={() => pick(v)}>{o}</button>)}
      <div className="d-flex justify-content-between mt-3"><button className="btn btn-outline-teal" onClick={() => (i ? setI(i - 1) : setMode(null))}>Previous</button>
        {i < items.length - 1 ? <button className="btn btn-teal" disabled={cur === undefined} onClick={() => setI(i + 1)}>Next</button> : <button className="btn btn-teal" disabled={cur === undefined || busy} onClick={submit}>{busy ? 'Working…' : 'See my results'}</button>}</div>
      <small className="muted d-block mt-2">Progress is saved as you go.</small></Card>
    <div className="mt-3"><Disclaimer>This is a screening, not a diagnosis.</Disclaimer></div></>)
}

export default Assessment
