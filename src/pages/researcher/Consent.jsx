import { useState } from 'react'
import toast from 'react-hot-toast'
import { Card, Stat, Disclaimer } from '../../components/common/ui'
import { researchLog } from '../../data/mock'


export function ResearcherConsent() {
  const [req, setReq] = useState({ topic: '', purpose: '' })
  return (<><h1 className="h3">Consent and requests</h1><div className="row g-3">
    <div className="col-md-6"><Card title="Consent categories"><ul className="mb-0"><li>De-identified aggregate analysis</li><li>Re-contact about studies</li><li>Optional: withdrawn any time, separate from counselling</li></ul></Card></div>
    <div className="col-md-6"><Card title="De-identified dataset request (demo)">
      <input aria-label="Topic" className="form-control mb-2" placeholder="Research topic" value={req.topic} onChange={e => setReq({ ...req, topic: e.target.value })} />
      <textarea aria-label="Purpose" className="form-control mb-2" rows={3} placeholder="Purpose and ethics approval reference" value={req.purpose} onChange={e => setReq({ ...req, purpose: e.target.value })} />
      <button className="btn btn-teal" disabled={!req.topic || !req.purpose} onClick={() => { toast.success('Request drafted (nothing is sent in this demo)'); setReq({ topic: '', purpose: '' }) }}>Save draft request</button></Card></div></div></>)
}

export default ResearcherConsent
