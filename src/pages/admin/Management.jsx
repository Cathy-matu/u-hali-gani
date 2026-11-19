import { useEffect, useState } from 'react'
import { LineChart, Line, BarChart, Bar, PieChart, Pie, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from 'recharts'
import { Card, Stat, Loading, Disclaimer, Badge } from '../../components/common/ui'
import { analyticsApi } from '../../services/api'
import { monthly, utilisation, riskDist, moodDist, departments, auditLog } from '../../data/mock'
import ChartBox from '../../components/charts/ChartBox'


export function Management() {
  return (<><h1 className="h3">University management</h1><div className="row g-3">
    <div className="col-md-6"><Card title="University profile"><p className="mb-0">Demo University · Nairobi<br />6 departments · 4,820 students</p></Card></div>
    <div className="col-md-6"><Card title="Counsellors"><p className="mb-0">Dr. A. Wekesa · Mr. B. Otieno · Ms. G. Mutua<br /><small className="muted">Utilisation 78% (aggregate)</small></p></Card></div>
    <div className="col-md-6"><Card title="Platform configuration"><div className="form-check form-switch"><input id="c1" className="form-check-input" type="checkbox" defaultChecked disabled /><label htmlFor="c1" className="form-check-label">Minimum cohort size 10 (locked)</label></div></Card></div>
    <div className="col-md-6"><Card title="Aggregate reports"><button className="btn btn-soft" onClick={() => alert('Report export is not implemented in this demo.')}>Request monthly report</button></Card></div>
    <div className="col-12"><Card title="Audit log"><table className="table mb-0"><tbody>{auditLog.map(([t, a, d]) => <tr key={t + a}><td>{t}</td><td>{a}</td><td>{d}</td></tr>)}</tbody></table></Card></div></div></>)
}

export default Management
