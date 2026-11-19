import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import toast from 'react-hot-toast'
import { Card, Stat, Risk as RiskBadge, Badge, Disclaimer, Modal, Loading } from '../../components/common/ui'
import Chat from '../../components/common/Chat'
import { cases, brief, appointmentsC } from '../../data/mock'
import Calendar, { iso, fmt } from '../../components/forms/Calendar'

const arrow = t => ({ worsening: '↑ worsening', improving: '↓ improving', stable: '→ stable' }[t])

export function Risk() {
  const g = r => cases.filter(c => c.risk === r).length
  return (<><h1 className="h3">Risk monitoring</h1>
    <div className="row g-3 mb-3">{['red', 'amber', 'green'].map(r => <div className="col-4" key={r}><Stat label={r + ' cases'} value={g(r)} /></div>)}</div>
    <Card title="Recent alerts">{cases.filter(c => c.risk !== 'green').map(c => <div key={c.id} className="d-flex justify-content-between align-items-center border-top py-2"><div>{c.id}<br /><small className="muted">{c.last} · {arrow(c.trend)} · {c.status}</small></div><Link className="btn btn-soft" to={`/counsellor/cases/${c.id}`}>Review case</Link></div>)}</Card></>)
}

export default Risk
