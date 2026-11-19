import { useEffect, useState } from 'react'
import { LineChart, Line, BarChart, Bar, PieChart, Pie, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from 'recharts'
import { Card, Stat, Loading, Disclaimer, Badge } from '../../components/common/ui'
import { analyticsApi } from '../../services/api'
import { monthly, utilisation, riskDist, moodDist, departments, auditLog } from '../../data/mock'
import ChartBox from '../../components/charts/ChartBox'


export function AdminHome() {
  return (<><h1 className="h3">Institutional overview</h1><Disclaimer>Aggregate statistics only. No individual records are available to administrators.</Disclaimer>
    <div className="row g-3 my-1">{[['Enrolled students', '4,820'], ['Registered users', '1,236'], ['Weekly check-in participation', '27%'], ['Bookings this month', '184'], ['Completed sessions', '151'], ['Counsellor utilisation', '78%']].map(([l, v]) => <div className="col-6 col-lg-4" key={l}><Stat label={l} value={v} /></div>)}</div></>)
}

export default AdminHome
