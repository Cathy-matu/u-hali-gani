import { useEffect, useRef, useState } from 'react'
import { Send, Paperclip, CheckCheck } from 'lucide-react'
import { messagingApi } from '../../services/api'
export default function Chat({ threads, replyAs = 'them', placeholder = 'Write a message…' }) {
  const [all, setAll] = useState(threads)
  const [cur, setCur] = useState(0)
  const [text, setText] = useState('')
  const [typing, setTyping] = useState(false)
  const end = useRef()
  useEffect(() => { end.current?.scrollIntoView({ block: 'nearest' }) }, [all, typing, cur])
  const t = all[cur]
  const send = async e => {
    e.preventDefault()
    if (!text.trim()) return
    const msg = { from: 'me', text: text.trim(), time: 'now', read: false }
    await messagingApi.send(msg)
    setAll(a => a.map((x, i) => i === cur ? { ...x, unread: 0, msgs: [...x.msgs, msg] } : x))
    setText(''); setTyping(true)
    setTimeout(() => { setTyping(false); setAll(a => a.map((x, i) => i === cur ? { ...x, msgs: [...x.msgs.map(m => ({ ...m, read: true })), { from: replyAs, text: 'Thanks for the message. I’ll follow up shortly.', time: 'now' }] } : x)) }, 1300)
  }
  return (
    <div className="row g-3">
      <div className="col-md-4"><div className="card-h p-2">
        {all.map((x, i) => (
          <button key={x.name} className={`ans mb-1 ${i === cur ? 'sel' : ''}`} onClick={() => setCur(i)}>
            <div className="d-flex justify-content-between"><b>{x.name}</b>{x.unread > 0 && <span className="badge bg-danger">{x.unread}</span>}</div>
            <small className="muted">{x.online ? '● Online' : '○ Offline'}{x.priority ? ' · Priority' : ''}</small>
          </button>))}
      </div></div>
      <div className="col-md-8"><div className="card-h d-flex flex-column" style={{ height: 460 }}>
        <div className="border-bottom pb-2 mb-2"><b>{t.name}</b> <small className="muted">{t.online ? 'online' : 'offline'}</small></div>
        <div className="flex-grow-1 overflow-auto" aria-live="polite">
          {t.msgs.map((m, i) => (
            <div key={i} className={`bubble ${m.from === 'me' ? 'me' : 'them'}`}>{m.text}
              <div className="small opacity-75">{m.time} {m.from === 'me' && <CheckCheck size={14} color={m.read ? '#9ff' : '#fff'} />}</div></div>))}
          {typing && <div className="bubble them muted">typing…</div>}
          <div ref={end} />
        </div>
        <form onSubmit={send} className="d-flex gap-2 mt-2">
          <button type="button" className="btn btn-soft" aria-label="Attach file (demo)" onClick={() => alert('Attachments are a UI demo only.')}><Paperclip size={18} /></button>
          <input className="form-control" aria-label="Message" value={text} onChange={e => setText(e.target.value)} placeholder={placeholder} />
          <button className="btn btn-teal" aria-label="Send"><Send size={18} /></button>
        </form>
        <small className="muted mt-1">Demo only: messages are simulated and not encrypted.</small>
      </div></div>
    </div>
  )
}
