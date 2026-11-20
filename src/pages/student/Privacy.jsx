import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Phone, Search } from 'lucide-react'
import { Card, Badge, Empty, Loading, Disclaimer, Modal, Risk } from '../../components/common/ui'
import Chat from '../../components/common/Chat'
import { useApp } from '../../context/AuthContext'
import { authApi, getAuthErrorMessage } from '../../services/auth'
import { moods, moodHistory, resources, counsellors, slots, helpContacts, assistantReplies } from '../../data/mock'
import { SHORT, FULL, FREQ, WHO_OPT } from '../../data/instruments'
import { scoreAll, routeRisk } from '../../utils/scoring'
import Calendar, { fmt, startOfToday } from '../../components/forms/Calendar'
import { checkinApi, assessmentApi, bookingApi } from '../../services/api'


export function Privacy() {
  const { consent, setConsent, setUser, user } = useApp()
  const [hist, setHist] = useState([['Today', 'Opened privacy centre']])
  const [savingConsent, setSavingConsent] = useState(false)
  const tog = async k => {
    if (savingConsent) return
    const n = { ...consent, [k]: !consent[k] }
    setSavingConsent(true)
    try {
      const updatedUser = await authApi.updateConsent(n)
      setUser(updatedUser)
      setConsent(n)
      setHist(h => [[new Date().toLocaleTimeString(), `${k} consent ${n[k] ? 'given' : 'withdrawn'}`], ...h])
      toast.success('Consent updated')
    } catch (error) {
      toast.error(getAuthErrorMessage(error, 'We could not update your consent. Please try again.'))
    } finally {
      setSavingConsent(false)
    }
  }
  return (<><h1 className="h3">Privacy centre</h1><div className="row g-3">
    <div className="col-md-6"><Card title="Your identity"><p>Pseudonym: <b>{user?.pseudonym}</b></p><p className="mb-0 muted">Anonymity is the default. It can be broken only under the emergency protocol for imminent risk.</p></Card></div>
    <div className="col-md-6"><Card title="Research consent (optional)">{[['research', 'Share de-identified data for research'], ['recontact', 'Allow re-contact about studies']].map(([k, l]) => <div className="form-check form-switch mb-2" key={k}><input id={k} className="form-check-input" type="checkbox" checked={consent[k]} disabled={savingConsent} onChange={() => tog(k)} /><label htmlFor={k} className="form-check-label">{l}</label></div>)}<small className="muted">Separate from counselling. Saying no never affects your access.</small></Card></div>
    <div className="col-md-6"><Card title="How data is used"><p className="mb-0">Counsellors see your pseudonym and check-ins. Administrators see aggregates of 10 or more students. Your account and consent choices are stored securely; other care activity in this preview uses sample data.</p></Card></div>
    <div className="col-md-6"><Card title="Consent history">{hist.map((h, i) => <div key={i} className="small">{h[0]}: {h[1]}</div>)}</Card></div></div></>)
}

export default Privacy
