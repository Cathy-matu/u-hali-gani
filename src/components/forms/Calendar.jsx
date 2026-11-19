import { useState } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'
export const iso = d => `${d.getFullYear()}-${d.getMonth() + 1}-${d.getDate()}`
export const fmt = d => (d ? d.toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric', month: 'short' }) : '')
export const startOfToday = () => { const d = new Date(); d.setHours(0, 0, 0, 0); return d }
export default function Calendar({ selected, onSelect, events = {}, disabled = () => false }) {
  const [m, setM] = useState(() => { const d = new Date(selected || Date.now()); return new Date(d.getFullYear(), d.getMonth(), 1) })
  const lead = (m.getDay() + 6) % 7
  const days = Array.from({ length: 42 }, (_, i) => new Date(m.getFullYear(), m.getMonth(), i - lead + 1))
  return (
    <div className="card-h p-2">
      <div className="d-flex justify-content-between align-items-center mb-2">
        <button className="btn btn-soft" aria-label="Previous month" onClick={() => setM(new Date(m.getFullYear(), m.getMonth() - 1, 1))}><ChevronLeft size={16} /></button>
        <b>{m.toLocaleDateString('en-GB', { month: 'long', year: 'numeric' })}</b>
        <button className="btn btn-soft" aria-label="Next month" onClick={() => setM(new Date(m.getFullYear(), m.getMonth() + 1, 1))}><ChevronRight size={16} /></button>
      </div>
      <div className="d-grid text-center small muted" style={{ gridTemplateColumns: 'repeat(7,1fr)' }}>{['M', 'T', 'W', 'T', 'F', 'S', 'S'].map((d, i) => <div key={i}>{d}</div>)}</div>
      <div className="d-grid gap-1" style={{ gridTemplateColumns: 'repeat(7,1fr)' }}>
        {days.map(d => {
          const out = d.getMonth() !== m.getMonth(); const on = selected && iso(d) === iso(selected); const n = events[iso(d)]
          return <button key={d.toISOString()} disabled={disabled(d)} aria-label={d.toDateString()} aria-pressed={!!on} onClick={() => onSelect(d)}
            className={`btn p-0 ${on ? 'btn-teal' : 'btn-outline-light text-dark'}`} style={{ minHeight: 44, opacity: out ? .4 : 1 }}>{d.getDate()}{n ? <span style={{ display: 'block', width: 6, height: 6, borderRadius: 9, background: on ? '#fff' : 'var(--teal)', margin: '0 auto' }} /> : null}</button>
        })}
      </div>
    </div>)
}
