import { createContext, useContext, useEffect, useState } from 'react'
import { authApi } from '../services/auth'
const Ctx = createContext(null)
export const useApp = () => useContext(Ctx)
const KEY = 'hali-demo-v1' // demo state only: no real health data or credentials
const load = () => { try { return JSON.parse(localStorage.getItem(KEY)) || {} } catch { return {} } }
export function AuthProvider({ children }) {
  const s = load()
  const [user, setUser] = useState(null)
  const [authReady, setAuthReady] = useState(false)
  const [risk, setRisk] = useState(s.risk || null)
  const [bookings, setBookings] = useState(s.bookings || [])
  const [consent, setConsent] = useState({ research: false, recontact: false })
  const [lang, setLang] = useState(s.lang || 'en')
  const role = user?.role || null
  const setAuthenticatedUser = currentUser => {
    setUser(currentUser)
    setConsent({
      research: currentUser?.research_consent || false,
      recontact: currentUser?.recontact_consent || false,
    })
  }
  useEffect(() => {
    localStorage.setItem(KEY, JSON.stringify({ risk, bookings, lang }))
  }, [risk, bookings, lang])
  useEffect(() => {
    let active = true
    authApi.me().then(currentUser => {
      if (active) setAuthenticatedUser(currentUser)
    }).catch(error => {
      if (error?.response?.status !== 401 && active) {
        console.error('Unable to restore the Hali session.', error)
      }
    }).finally(() => {
      if (active) setAuthReady(true)
    })
    return () => { active = false }
  }, [])
  const logout = async () => {
    await authApi.logout()
    setAuthenticatedUser(null)
  }
  return <Ctx.Provider value={{ role, user, setUser: setAuthenticatedUser, authReady, logout, risk, setRisk, bookings, setBookings, consent, setConsent, lang, setLang }}>{children}</Ctx.Provider>
}
