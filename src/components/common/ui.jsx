import { Link } from 'react-router-dom'
export const Logo = ({ size = 28 }) => (
  <span className="brand d-inline-flex align-items-center gap-2 fs-4" style={{ color: 'var(--teal)' }}>
    <img src="/icon.svg" width={size} height={size} alt="" />Hali
  </span>
)
export const Badge = ({ tone = 'grey', children }) => <span className={`pill b-${tone}`}>{children}</span>
export const riskTone = r => ({ green: 'green', amber: 'amber', red: 'red' }[r] || 'grey')
export const Risk = ({ r }) => <Badge tone={riskTone(r)}>{r[0].toUpperCase() + r.slice(1)}</Badge>
export { Card, Stat } from '../cards/Card'
export { Modal } from '../modals/Modal'
export const Empty = ({ title, text, to, cta }) => (
  <div className="text-center p-4 muted"><h3 className="h6">{title}</h3><p className="mb-2">{text}</p>{to && <Link className="btn btn-soft" to={to}>{cta}</Link>}</div>
)
export const Loading = ({ text = 'Loading…' }) => <div className="p-4 text-center muted" role="status"><span className="spinner-border spinner-border-sm me-2" />{text}</div>
export const Disclaimer = ({ children }) => <div className="notice">{children}</div>
