import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import toast from 'react-hot-toast'
import { Card, Stat, Risk as RiskBadge, Badge, Disclaimer, Modal, Loading } from '../../components/common/ui'
import { useApp } from '../../context/AuthContext'
import Chat from '../../components/common/Chat'
import { cases, brief, appointmentsC } from '../../data/mock'
import Calendar, { iso, fmt } from '../../components/forms/Calendar'

const arrow = t => ({ worsening: '↑ worsening', improving: '↓ improving', stable: '→ stable' }[t])

export function Overview() {
  const { user } = useApp()
  const alerts = cases.filter(c => c.risk !== 'green')
  return (<><h1 className="h3">Good morning, {user?.full_name || 'Counsellor'}</h1>
    <div className="row g-3 mb-3">{[['Assigned students', 24], ['Pending requests', 3], ['Sessions this week', 11], ['Unread messages', 5]].map(([l, v]) => <div className="col-6 col-lg-3" key={l}><Stat label={l} value={v} /></div>)}</div>
    <div className="row g-3 mb-3"><div className="col-lg-7"><Card title="Weekly workload (sessions)"><div style={{ height: 180 }}><ResponsiveContainer><BarChart data={['Mon', 'Tue', 'Wed', 'Thu', 'Fri'].map((d, i) => ({ d, n: [4, 3, 5, 2, 3][i] }))}><XAxis dataKey="d" /><YAxis /><Tooltip /><Bar dataKey="n" fill="#087E83" radius={6} /></BarChart></ResponsiveContainer></div></Card></div><div className="col-lg-5"><Card title="Recent check-ins">{cases.slice(0, 4).map(c => <div key={c.id} className="border-top py-1 small d-flex justify-content-between"><span>{c.id}</span><span className="muted">{c.last}</span></div>)}</Card></div></div>
    <Card title="Needs attention">{alerts.map(c => <Link key={c.id} to={`/counsellor/cases/${c.id}`} className="d-flex justify-content-between text-decoration-none border-top py-2"><span>{c.id}</span><span><RiskBadge r={c.risk} /> <small className="muted">{arrow(c.trend)}</small></span></Link>)}</Card></>)
}

export default Overview
