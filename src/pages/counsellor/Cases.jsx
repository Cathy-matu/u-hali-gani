import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import toast from 'react-hot-toast'
import { Card, Stat, Risk as RiskBadge, Badge, Disclaimer, Modal, Loading } from '../../components/common/ui'
import Chat from '../../components/common/Chat'
import { cases, brief, appointmentsC } from '../../data/mock'
import Calendar, { iso, fmt } from '../../components/forms/Calendar'

const arrow = t => ({ worsening: '↑ worsening', improving: '↓ improving', stable: '→ stable' }[t])

export function Cases() {
  const [f, setF] = useState('all'); const list = cases.filter(c => f === 'all' || c.risk === f)
  return (<><h1 className="h3">Student cases</h1><p className="muted">Pseudonymous IDs only.</p>
    <div className="mb-3">{['all', 'red', 'amber', 'green'].map(x => <button key={x} className={`btn me-1 ${f === x ? 'btn-teal' : 'btn-soft'}`} onClick={() => setF(x)}>{x}</button>)}</div>
    <div className="card-h table-responsive"><table className="table align-middle mb-0"><thead><tr><th>Student</th><th>Risk</th><th>Latest check-in</th><th>Trend</th><th>Next</th><th>Status</th></tr></thead>
      <tbody>{list.map(c => <tr key={c.id}><td><Link to={`/counsellor/cases/${c.id}`}>{c.id}</Link></td><td><RiskBadge r={c.risk} /></td><td>{c.last}</td><td>{arrow(c.trend)}</td><td>{c.next}</td><td>{c.status}</td></tr>)}</tbody></table></div></>)
}

export default Cases
