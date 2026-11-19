import { useEffect, useState } from 'react'
import { LineChart, Line, BarChart, Bar, PieChart, Pie, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from 'recharts'
import { Card, Stat, Loading, Disclaimer, Badge } from '../../components/common/ui'
import { analyticsApi } from '../../services/api'
import { monthly, utilisation, riskDist, moodDist, departments, auditLog } from '../../data/mock'
import ChartBox from '../../components/charts/ChartBox'


export function Analytics() {
  const [d, setD] = useState(null); const [range, setRange] = useState(8)
  useEffect(() => { analyticsApi.overview().then(setD) }, [])
  if (!d) return <Loading />
  const s = d.slice(-range)
  return (<><h1 className="h3">Analytics</h1><div className="mb-3">{[4, 8].map(r => <button key={r} className={`btn me-1 ${range === r ? 'btn-teal' : 'btn-soft'}`} onClick={() => setRange(r)}>Last {r} weeks</button>)}</div>
    <div className="row g-3">
      <div className="col-lg-6"><Card title="Weekly check-in participation"><ChartBox><BarChart data={s}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="w" /><YAxis /><Tooltip /><Bar dataKey="checkins" fill="#087E83" radius={6} /></BarChart></ChartBox></Card></div>
      <div className="col-lg-6"><Card title="Aggregate PHQ / GAD averages"><ChartBox><LineChart data={s}><XAxis dataKey="w" /><YAxis /><Tooltip /><Legend /><Line dataKey="phq" stroke="#087E83" strokeWidth={2} /><Line dataKey="gad" stroke="#B7791F" strokeWidth={2} /></LineChart></ChartBox></Card></div>
      <div className="col-lg-6"><Card title="Booking trends"><ChartBox><LineChart data={s}><XAxis dataKey="w" /><YAxis /><Tooltip /><Line dataKey="bookings" stroke="#2F855A" strokeWidth={2} /></LineChart></ChartBox></Card></div>
      <div className="col-lg-3"><Card title="Risk distribution (%)"><ChartBox><PieChart><Pie data={riskDist} dataKey="value" nameKey="name" innerRadius={40} /><Tooltip /><Legend /></PieChart></ChartBox></Card></div>
      <div className="col-lg-3"><Card title="Mood distribution (%)"><ChartBox><BarChart data={moodDist} layout="vertical"><XAxis type="number" /><YAxis type="category" dataKey="name" width={70} /><Tooltip /><Bar dataKey="value" fill="#6BB8B3" /></BarChart></ChartBox></Card></div>
    <div className="col-lg-6"><Card title="Monthly engagement"><ChartBox><LineChart data={monthly}><XAxis dataKey="m" /><YAxis /><Tooltip /><Legend /><Line dataKey="active" name="Active users" stroke="#087E83" strokeWidth={2} /><Line dataKey="sessions" name="Sessions" stroke="#2F855A" strokeWidth={2} /></LineChart></ChartBox></Card></div>
      <div className="col-lg-6"><Card title="Service utilisation by session type (%)"><ChartBox><BarChart data={utilisation}><XAxis dataKey="name" /><YAxis /><Tooltip /><Bar dataKey="value" fill="#6BB8B3" radius={6} /></BarChart></ChartBox></Card></div>
    </div><p className="small muted mt-2">Synthetic data.</p></>)
}

export default Analytics
