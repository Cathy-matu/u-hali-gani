import { useState } from 'react'
import { NavLink, Outlet, useNavigate, Link } from 'react-router-dom'
import { Menu, LifeBuoy, LogOut } from 'lucide-react'
import { Logo } from '../components/common/ui'
import useDocumentTitle from '../hooks/useDocumentTitle'
import { useApp } from '../context/AuthContext'
export default function Shell({ nav, label, help }) {
  const [open, setOpen] = useState(false)
  const { role, setRole, reset } = useApp()
  const go = useNavigate()
  useDocumentTitle(label)
  const switchTo = r => { setRole(r); go(`/${r}`) }
  return (
    <div className="shell">
      <aside className={`side ${open ? 'open' : ''}`} aria-label={`${label} navigation`}>
        <div className="p-3"><Logo /></div>
        <nav onClick={() => setOpen(false)}>
          {nav.map(([to, text, Icon]) => <NavLink key={to} end={to.split('/').length === 2} className="nl" to={to}><Icon size={18} />{text}</NavLink>)}
        </nav>
        <div className="p-3 mt-3 border-top">
          <label className="small muted" htmlFor="rs">Switch demo role</label>
          <select id="rs" className="form-select mb-2" value={role || ''} onChange={e => switchTo(e.target.value)}>
            <option value="student">Student</option><option value="counsellor">Counsellor</option><option value="admin">University admin</option><option value="researcher">Researcher</option>
          </select>
          <button className="btn btn-outline-teal w-100" onClick={() => { setRole(null); go('/login') }}><LogOut size={16} />Leave demo</button>
          <button className="btn btn-link small w-100" onClick={reset}>Reset demo data</button>
        </div>
      </aside>
      <div className="main">
        <button className="btn btn-soft d-lg-none mb-3" aria-label="Open menu" onClick={() => setOpen(o => !o)}><Menu size={18} />Menu</button>
        <Outlet />
      </div>
      {help && <Link to="/student/help" className="btn btn-danger helpfab"><LifeBuoy size={18} />Get help now</Link>}
    </div>
  )
}
