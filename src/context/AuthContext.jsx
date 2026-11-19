import { createContext, useContext, useEffect, useState } from 'react'
const Ctx = createContext(null)
export const useApp = () => useContext(Ctx)
const KEY = 'hali-demo-v1' // demo state only: no real health data or credentials
const load = () => { try { return JSON.parse(localStorage.getItem(KEY)) || {} } catch { return {} } }
export function AuthProvider({ children }) {
  const s = load()
  const [role, setRole] = useState(s.role || null)
  const [risk, setRisk] = useState(s.risk || null)
  const [bookings, setBookings] = useState(s.bookings || [{ id: 1, who: 'Dr. Amina Wekesa', when: 'Fri 10:30', type: 'Audio', status: 'Upcoming' }])
  const [consent, setConsent] = useState(s.consent || { research: false, recontact: false })
  const [lang, setLang] = useState(s.lang || 'en')
  useEffect(() => { localStorage.setItem(KEY, JSON.stringify({ role, risk, bookings, consent, lang })) }, [role, risk, bookings, consent, lang])
  const reset = () => { localStorage.removeItem(KEY); location.hash = '#/'; location.reload() }
  return <Ctx.Provider value={{ role, setRole, risk, setRisk, bookings, setBookings, consent, setConsent, lang, setLang, reset }}>{children}</Ctx.Provider>
}
