import { useEffect, useState } from 'react'
import { LineChart, Line, BarChart, Bar, PieChart, Pie, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from 'recharts'
import { Card, Stat, Loading, Disclaimer, Badge } from '../../components/common/ui'
import { analyticsApi } from '../../services/api'
import { monthly, utilisation, riskDist, moodDist, departments, auditLog } from '../../data/mock'
import ChartBox from '../../components/charts/ChartBox'


export function PrivacyRules() {
  return (<><h1 className="h3">Privacy protection</h1>
    <Card title="Rules enforced in this dashboard"><ul className="mb-0"><li>Aggregate statistics only</li><li>Minimum cohort size of 10; smaller groups are suppressed</li><li>No individual student profiles, assessment results or counselling notes</li></ul></Card>
    <Card title="Check-in participation by department" className="mt-3"><table className="table mb-0"><thead><tr><th>Department</th><th>Students in group</th><th>Wellbeing indicator</th></tr></thead>
      <tbody>{departments.map(x => <tr key={x.name} className={x.n < 10 ? 'supp' : ''}><td>{x.name}</td><td>{x.n < 10 ? '—' : x.n}</td><td>{x.n < 10 ? <Badge>Hidden: fewer than 10 students</Badge> : <Badge tone="green">Shown</Badge>}</td></tr>)}</tbody></table>
      <small className="muted">Small groups are hidden so no one can be identified.</small></Card></>)
}

export default PrivacyRules
