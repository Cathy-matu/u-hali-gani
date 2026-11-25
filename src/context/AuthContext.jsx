import { createContext, useContext, useEffect, useState } from 'react'
import { authApi } from '../services/auth'
import { DOMAINS } from '../utils/longitudinal'
const Ctx = createContext(null)
export const useApp = () => useContext(Ctx)
const KEY = 'hali-demo-v1' // demo state only: no real health data or credentials
const PREVIEW_KEY = 'hali-preview-role'
const RESEARCH_KEY = 'hali-research-prototype-v1'
const emptyResearchState = () => ({ sessions: [], responses: [], consents: {}, consentHistory: [] })
const load = () => { try { return JSON.parse(localStorage.getItem(KEY)) || {} } catch { return {} } }
const loadResearchState = () => {
  try {
    const saved = JSON.parse(localStorage.getItem(RESEARCH_KEY))
    return {
      ...emptyResearchState(),
      ...saved,
      sessions: Array.isArray(saved?.sessions) ? saved.sessions : [],
      responses: Array.isArray(saved?.responses) ? saved.responses : [],
      consents: saved?.consents && typeof saved.consents === 'object' ? saved.consents : {},
      consentHistory: Array.isArray(saved?.consentHistory) ? saved.consentHistory : [],
    }
  } catch {
    return emptyResearchState()
  }
}
const getPreviewRole = () => {
  const role = sessionStorage.getItem(PREVIEW_KEY)
  return ['student', 'counsellor', 'lecturer', 'researcher'].includes(role) ? role : null
}
export function AuthProvider({ children }) {
  const s = load()
  const [user, setUser] = useState(null)
  const [authReady, setAuthReady] = useState(false)
  const [isDemo, setIsDemo] = useState(() => Boolean(getPreviewRole()))
  const [researchData, setResearchData] = useState(loadResearchState)
  const [bookings, setBookings] = useState(s.bookings || [])
  const [consent, setConsent] = useState({ participation: false, research: false, leaderboard: false, recontact: false })
  const [lang, setLang] = useState(s.lang || 'en')
  const role = user?.role || null
  const setAuthenticatedUser = (currentUser, initialConsent) => {
    setUser(currentUser)
    if (!currentUser) {
      setConsent({ participation: false, research: false, leaderboard: false, recontact: false })
      return
    }
    if (initialConsent) {
      const event = { userId: currentUser.id, at: new Date().toISOString(), choices: { ...initialConsent } }
      setResearchData(current => ({
        ...current,
        consents: { ...current.consents, [currentUser.id]: initialConsent },
        consentHistory: [event, ...current.consentHistory],
      }))
      setConsent(initialConsent)
      return
    }
    const stored = researchData.consents[currentUser.id]
    setConsent(stored || {
      participation: false,
      research: currentUser.research_consent || false,
      leaderboard: false,
      recontact: currentUser.recontact_consent || false,
    })
  }
  const startDemo = role => {
    if (!['student', 'counsellor', 'lecturer', 'researcher'].includes(role)) {
      throw new Error(`Unsupported Hali preview role: ${role}`)
    }
    sessionStorage.setItem(PREVIEW_KEY, role)
    setIsDemo(true)
    setAuthenticatedUser({
      id: `demo-${role}`,
      username: `demo.${role}`,
      email: `${role}@demo.hali`,
      full_name: `Demo ${role[0].toUpperCase()}${role.slice(1)}`,
      role,
      pseudonym: `Hali-demo-${role}`,
      research_consent: false,
      recontact_consent: false,
    })
    setAuthReady(true)
  }
  const updateResearchConsent = async changes => {
    if (!user) throw new Error('Sign in before updating consent choices.')
    const previous = researchData.consents[user.id] || consent
    const next = { ...previous, ...changes }
    if (!next.participation) {
      next.research = false
      next.leaderboard = false
    }
    if (!isDemo && next.research !== previous.research) {
      await authApi.updateConsent({ research: next.research, recontact: next.recontact || false })
    }
    const event = {
      userId: user.id,
      at: new Date().toISOString(),
      choices: { ...next },
    }
    setResearchData(current => ({
      ...current,
      responses: current.responses
        .filter(row => next.participation || row.userId !== user.id)
        .map(row => row.userId === user.id && !next.research ? { ...row, researchEligible: false } : row),
      consents: { ...current.consents, [user.id]: next },
      consentHistory: [event, ...current.consentHistory],
    }))
    setConsent(next)
  }
  const createClassSession = title => {
    if (!title.trim()) throw new Error('Enter a class or session label.')
    const code = String(Math.floor(100000 + Math.random() * 900000))
    const session = {
      id: `session-${Date.now()}`,
      title: title.trim(),
      code,
      createdAt: new Date().toISOString(),
      weekIndex: researchData.sessions.length + 1,
      active: true,
    }
    setResearchData(current => ({
      ...current,
      sessions: [session, ...current.sessions.map(item => ({ ...item, active: false }))],
    }))
    return session
  }
  const closeClassSession = sessionId => {
    setResearchData(current => ({
      ...current,
      sessions: current.sessions.map(item => item.id === sessionId ? { ...item, active: false } : item),
    }))
  }
  const submitDomainCheckin = (sessionId, ratings) => {
    if (!user || !consent.participation) throw new Error('Enable check-in participation in Privacy choices before submitting.')
    if (DOMAINS.some(({ id }) => !Number.isInteger(ratings[id]) || ratings[id] < 1 || ratings[id] > 5)) {
      throw new Error('Complete each wellbeing domain before submitting.')
    }
    const session = researchData.sessions.find(item => item.id === sessionId && item.active)
    if (!session) throw new Error('This class session is no longer open.')
    const response = {
      id: `response-${Date.now()}`,
      sessionId,
      userId: user.id,
      pseudonym: user.pseudonym || `Hali-${user.id.slice(-6)}`,
      createdAt: new Date().toISOString(),
      weekIndex: session.weekIndex,
      ratings,
      researchEligible: Boolean(consent.research),
    }
    setResearchData(current => ({
      ...current,
      responses: [...current.responses.filter(row => !(row.sessionId === sessionId && row.userId === user.id)), response],
    }))
    return response
  }
  const addSampleCohort = sessionId => {
    const session = researchData.sessions.find(item => item.id === sessionId)
    if (!session) throw new Error('Choose a class session before adding sample data.')
    const syntheticRows = Array.from({ length: 12 }, (_, index) => ({
      id: `sample-${sessionId}-${index + 1}`,
      sessionId,
      userId: `synthetic-${sessionId}-${index + 1}`,
      pseudonym: null,
      createdAt: new Date(Date.now() - (index % 4) * 7 * 86400000).toISOString(),
      ratings: {
        academic: 1 + ((index * 2) % 5),
        spiritual: 1 + ((index + 2) % 5),
        social: 1 + ((index * 3) % 5),
        physical: 1 + ((index + 1) % 5),
        psychological: 1 + ((index * 4) % 5),
      },
      researchEligible: true,
      synthetic: true,
    }))
    setResearchData(current => ({
      ...current,
      responses: [
        ...current.responses.filter(row => !row.synthetic || row.sessionId !== sessionId),
        ...syntheticRows,
      ],
    }))
  }
  useEffect(() => {
    localStorage.setItem(KEY, JSON.stringify({ bookings, lang }))
  }, [bookings, lang])
  useEffect(() => {
    localStorage.setItem(RESEARCH_KEY, JSON.stringify(researchData))
  }, [researchData])
  useEffect(() => {
    const syncResearchState = event => {
      if (event.key === RESEARCH_KEY) setResearchData(loadResearchState())
    }
    window.addEventListener('storage', syncResearchState)
    return () => window.removeEventListener('storage', syncResearchState)
  }, [])
  useEffect(() => {
    let active = true
    const previewRole = getPreviewRole()
    if (previewRole) {
      startDemo(previewRole)
      return () => { active = false }
    }
    authApi.me().then(currentUser => {
      if (active && !getPreviewRole()) {
        setIsDemo(false)
        setAuthenticatedUser(currentUser)
      }
    }).catch(error => {
      if (error?.response?.status !== 401 && active && !getPreviewRole()) {
        console.error('Unable to restore the Hali session.', error)
      }
    }).finally(() => {
      if (active) setAuthReady(true)
    })
    return () => { active = false }
  }, [])
  const logout = async () => {
    if (isDemo || getPreviewRole()) {
      sessionStorage.removeItem(PREVIEW_KEY)
      setIsDemo(false)
      setAuthenticatedUser(null)
      return
    }
    await authApi.logout()
    setAuthenticatedUser(null)
  }
  return <Ctx.Provider value={{ role, user, setUser: setAuthenticatedUser, authReady, isDemo, startDemo, logout, bookings, setBookings, consent, setConsent, updateResearchConsent, researchData, createClassSession, closeClassSession, submitDomainCheckin, addSampleCohort, lang, setLang }}>{children}</Ctx.Provider>
}
