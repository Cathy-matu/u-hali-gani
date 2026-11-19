import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Logo, Card, Disclaimer } from '../../components/common/ui'
import { useApp } from '../../context/AuthContext'
import { authApi } from '../../services/api'
import { PSEUDONYM } from '../../data/mock'

const steps = ['Welcome', 'Anonymous by default', 'Check eligibility', 'Your pseudonym', 'Privacy', 'Consent']

export function Onboarding() {
  const [i, setI] = useState(0); const [email, setEmail] = useState(''); const { setRole, setConsent } = useApp(); const go = useNavigate()
  const [c, setC] = useState(false)
  const finish = () => { setConsent({ research: c, recontact: false }); setRole('student'); toast.success('Welcome to Hali'); go('/student') }
  const body = [
    <p>Hali is a calm place to check in with yourself and reach a human counsellor.</p>,
    <p>You take part under a pseudonym. Anonymity is the default. It can be broken only under a defined emergency protocol involving imminent risk.</p>,
    <><label htmlFor="em" className="form-label">University email</label><input id="em" className="form-control" type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="name@university.ac.ke" /><div className="notice mt-2">Demo only: this screen does not verify anything. A real build verifies eligibility on a server.</div></>,
    <p>Your pseudonym: <b className="fs-4">{PSEUDONYM}</b><br /><span className="muted">Counsellors see this, not your name.</span></p>,
    <p>Administrators see aggregate numbers only. Small groups are hidden. Your reflections are not shared with the university.</p>,
    <label className="d-flex gap-2"><input type="checkbox" className="form-check-input" checked={c} onChange={e => setC(e.target.checked)} />Optionally share de-identified data for research. This is separate from counselling and you can withdraw any time.</label>,
  ]
  return (
    <div className="container py-5" style={{ maxWidth: 600 }}>
      <Logo /><div className="progress my-3" role="progressbar" aria-valuenow={i + 1} aria-valuemax={steps.length}><div className="progress-bar" style={{ width: `${((i + 1) / steps.length) * 100}%`, background: 'var(--teal)' }} /></div>
      <Card title={`${i + 1}. ${steps[i]}`}>{body[i]}
        <div className="d-flex justify-content-between mt-4">
          <button className="btn btn-outline-teal" disabled={!i} onClick={() => setI(i - 1)}>Back</button>
          {i < steps.length - 1 ? <button className="btn btn-teal" onClick={() => setI(i + 1)}>Continue</button> : <button className="btn btn-teal" onClick={finish}>Go to my dashboard</button>}
        </div></Card>
    </div>
  )
}

export default Onboarding
