import { useState } from 'react'
import toast from 'react-hot-toast'
import { Card, Stat, Disclaimer } from '../../components/common/ui'
import { researchLog } from '../../data/mock'


export function ResearcherHome() {
  return (<><h1 className="h3">Research overview</h1><Disclaimer>Prototype with synthetic data. No real exports and no ethical approval is implied.</Disclaimer>
    <div className="row g-3 my-1">{[['Consenting participants', '214'], ['Re-contact consent', '96'], ['Withdrawals (30 days)', '3']].map(([l, v]) => <div className="col-md-4" key={l}><Stat label={l} value={v} /></div>)}</div>
    <div className="row g-3 mb-3"><div className="col-md-6"><Card title="Aggregate statistics (groups of 10 or more)"><div className="small">Check-in completion: 27%<br />Median weekly mood: Okay<br />Booking rate after amber outcome: 41%</div></Card></div><div className="col-md-6"><Card title="Consent withdrawal history"><div className="small">Nov 03: 3 withdrawals<br />Oct 21: 1 withdrawal<br />Oct 05: 2 withdrawals</div></Card></div></div>
    <Card title="Activity log">{researchLog.map(([d, t]) => <div key={d + t} className="border-top py-1 small">{d}: {t}</div>)}</Card></>)
}

export default ResearcherHome
