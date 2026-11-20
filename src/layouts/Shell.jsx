import { useState } from 'react'
import { NavLink, Outlet, useNavigate, Link } from 'react-router-dom'
import { Menu, LifeBuoy, LogOut, ShieldCheck } from 'lucide-react'
import toast from 'react-hot-toast'
import { Logo } from '../components/common/ui'
import useDocumentTitle from '../hooks/useDocumentTitle'
import { useApp } from '../context/AuthContext'
export default function Shell({ nav, label, help }) {
  const [open, setOpen] = useState(false)
  const { user, logout } = useApp()
  const go = useNavigate()
  useDocumentTitle(label)
  const signOut = async () => {
    try {
      await logout()
      go('/login', { replace: true })
      toast.success('You are signed out.')
    } catch (error) {
      console.error('Unable to sign out of Hali.', error)
      toast.error('We could not sign you out. Please try again.')
    }
  }
  return (
    <div className="shell">
      <aside className={`side ${open ? 'open' : ''}`} aria-label={`${label} navigation`}>
        <div className="side-brand"><Logo /></div>
        <p className="side-kicker">{label === 'Student' ? 'YOUR CAMPUS' : 'WORKSPACE'}</p>
        <nav onClick={() => setOpen(false)}>
          {nav.map(([to, text, Icon]) => <NavLink key={to} end={to.split('/').length === 2} className="nl" to={to}><Icon size={18} />{text}</NavLink>)}
        </nav>
        <div className="side-account">
          <div className="side-account-detail">
            <span className="side-account-avatar" aria-hidden="true">{user?.full_name?.trim().charAt(0).toUpperCase() || 'H'}</span>
            <span className="side-account-copy"><small>Signed in as</small><strong title={user?.full_name}>{user?.full_name || 'Hali member'}</strong></span>
          </div>
          <button className="btn btn-outline-teal w-100" onClick={signOut}><LogOut size={16} />Sign out</button>
        </div>
      </aside>
      <div className="main">
        <header className="app-topbar">
          <button className="btn btn-soft app-menu-button" aria-label={open ? 'Close menu' : 'Open menu'} onClick={() => setOpen(o => !o)}><Menu size={18} /><span>Menu</span></button>
          <p>{label === 'Student' ? 'A little more well, together.' : `${label} workspace`}</p>
          {label === 'Student' && <Link to="/student/privacy" className="app-privacy-link"><ShieldCheck size={17} /> <span>Privacy first</span></Link>}
        </header>
        <div className="app-content"><Outlet /></div>
      </div>
      {help && <Link to="/student/help" className="btn btn-danger helpfab"><LifeBuoy size={18} />Get help now</Link>}
    </div>
  )
}
