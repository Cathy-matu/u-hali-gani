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


export function Assistant() {
  const { lang, setLang } = useApp(); const R = assistantReplies[lang]; const go = useNavigate()
  const [msgs, setMsgs] = useState([{ b: true, t: R.default }]); const [t, setT] = useState(''); const [typing, setTyping] = useState(false)
  const ask = txt => {
    if (!txt.trim()) return; setMsgs(m => [...m, { t: txt }]); setT(''); setTyping(true)
    const l = txt.toLowerCase(); const key = /(hopeless|die|hurt|kill|suicid|kujiua)/.test(l) ? 'human' : /(sleep|lala|usingizi)/.test(l) ? 'sleep' : /(stress|exam|mtihani)/.test(l) ? 'stress' : 'default'
    setTimeout(() => { setTyping(false); setMsgs(m => [...m, { b: true, t: R[key], human: key === 'human' }]) }, 1000)
  }
  const prompts = lang === 'en' ? ['I’m stressed about exams', 'I can’t sleep', 'I feel hopeless'] : ['Nina mfadhaiko wa mtihani', 'Siwezi kulala', 'Nahisi hakuna matumaini']
  return (<><div className="d-flex justify-content-between align-items-center"><h1 className="h3">{lang === 'en' ? 'Wellbeing assistant' : 'Msaidizi wa ustawi'}</h1><button className="btn btn-soft" onClick={() => setLang(lang === 'en' ? 'sw' : 'en')}>{lang === 'en' ? 'Kiswahili' : 'English'}</button></div>
    <Disclaimer>{lang === 'en' ? 'I’m an AI, not a counsellor. Demo replies are pre-written.' : 'Mimi ni AI, si mshauri. Majibu ya onyesho yameandikwa mapema.'}</Disclaimer>
    <div className="card-h mt-3" style={{ minHeight: 300 }} aria-live="polite">{msgs.map((m, i) => <div key={i} className={`bubble ${m.b ? 'them' : 'me'}`}>{m.t}{m.human && <div className="mt-2"><button className="btn btn-danger btn-sm" onClick={() => go('/student/help')}>Talk to a human</button></div>}</div>)}{typing && <div className="bubble them muted">…</div>}</div>
    <div className="my-2">{prompts.map(p => <button key={p} className="btn btn-soft me-1 mb-1" onClick={() => ask(p)}>{p}</button>)}</div>
    <form className="d-flex gap-2" onSubmit={e => { e.preventDefault(); ask(t) }}><input aria-label="Message" className="form-control" value={t} onChange={e => setT(e.target.value)} /><button className="btn btn-teal">Send</button><Link to="/student/help" className="btn btn-danger">Talk to a human</Link></form></>)
}

export default Assistant
