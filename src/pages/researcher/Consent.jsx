import { useState } from 'react'
import toast from 'react-hot-toast'
import { Card, Disclaimer } from '../../components/common/ui'


export function ResearcherConsent() {
  const [req, setReq] = useState({ topic: '', purpose: '' })
  return (<><h1 className="h3">Consent and requests</h1><Disclaimer>Requests are presentation-only drafts. No request is submitted and no participant-level dataset can be exported from this prototype.</Disclaimer><div className="row g-3">
    <div className="col-md-6"><Card title="Separate consent tiers"><ul className="mb-0"><li>Check-in participation (C1): personal records and progression view</li><li>Research contribution (C2): inclusion in de-identified aggregate research outputs; requires C1</li><li>Leaderboard visibility (C3): optional pseudonymous visibility; requires C1</li><li>Declining research or leaderboard use does not remove access to personal tools or support</li></ul></Card></div>
    <div className="col-md-6"><Card title="Research access request (draft only)">
      <input aria-label="Topic" className="form-control mb-2" placeholder="Research topic" value={req.topic} onChange={e => setReq({ ...req, topic: e.target.value })} />
      <textarea aria-label="Purpose" className="form-control mb-2" rows={3} placeholder="Purpose and ethics approval reference" value={req.purpose} onChange={e => setReq({ ...req, purpose: e.target.value })} />
      <button className="btn btn-teal" disabled={!req.topic || !req.purpose} onClick={() => { toast.success('Request drafted (nothing is sent in this demo)'); setReq({ topic: '', purpose: '' }) }}>Save draft request</button></Card></div></div></>)
}

export default ResearcherConsent
