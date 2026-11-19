import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Logo, Card, Disclaimer } from '../../components/common/ui'
import { useApp } from '../../context/AuthContext'
import { authApi } from '../../services/api'
import { PSEUDONYM } from '../../data/mock'


export function Login() {
  const { setRole } = useApp(); const go = useNavigate()
  const enter = async r => { await authApi.login(r); setRole(r); toast.success(`Demo started as ${r}`); go(`/${r}`) }
  return (
    <div className="container py-5" style={{ maxWidth: 640 }}>
      <div className="mb-4"><Logo size={36} /></div>
      <h1 className="h3">Explore the Hali demo</h1>
      <p className="muted">No account needed. Each role opens a sample workspace filled with synthetic data.</p>
      <div className="d-grid gap-2 mb-3">
        {[['student', 'Demo as Student'], ['counsellor', 'Demo as Counsellor'], ['admin', 'Demo as University Admin'], ['researcher', 'Demo as Researcher']].map(([r, t]) => <button key={r} className="btn btn-teal py-3" onClick={() => enter(r)}>{t}</button>)}
      </div>
      <Link to="/onboarding">See the student onboarding first</Link>
      <p className="mt-4 small muted">Suggested walkthrough: Student → Weekly check-in (answer “Several days” or higher) → Book a counsellor → Counsellor → open the case and generate a brief → University Admin.</p>
    </div>
  )
}

export default Login
