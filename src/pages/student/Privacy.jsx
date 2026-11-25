import { useState } from 'react'
import toast from 'react-hot-toast'
import { Card, Disclaimer } from '../../components/common/ui'
import { useApp } from '../../context/AuthContext'
export function Privacy() {
  const { consent, updateResearchConsent, user, researchData } = useApp()
  const [savingConsent, setSavingConsent] = useState(false)
  const tog = async k => {
    if (savingConsent) return
    setSavingConsent(true)
    try {
      await updateResearchConsent({ [k]: !consent[k] })
      toast.success('Prototype consent choice updated.')
    } catch (error) {
      console.error('Unable to update prototype consent.', error)
      toast.error('We could not update your choice. Please try again.')
    } finally {
      setSavingConsent(false)
    }
  }
  const history = researchData.consentHistory.filter(item => item.userId === user?.id)
  return (
    <div className="research-page">
      <h1 className="h3">Privacy choices</h1>
      <Disclaimer>Prototype only: C1/C3 choices and check-ins are stored in this browser; C2 is saved as an account preference. These controls are not connected to a live research data service. Do not enter real wellbeing data or use this as research consent.</Disclaimer>
      <div className="row g-3">
        <div className="col-md-6"><Card title="Your Hali identity"><p>Display identity: <b>{user?.pseudonym || 'Not assigned in this preview'}</b></p><p className="mb-0 muted">This interface demonstrates pseudonymous display; it does not provide production anonymity or an emergency break-glass workflow.</p></Card></div>
        <div className="col-md-6"><Card title="Three separate choices">
          {[
            ['participation', 'C1 · Check-in participation', 'Store your check-ins for your own progression view. Turning this off removes your local check-in rows.'],
            ['research', 'C2 · Research contribution', 'Allow eligible check-ins to contribute to thresholded research aggregates. Requires C1. Turning this off removes your rows from future aggregates.'],
            ['leaderboard', 'C3 · Leaderboard visibility', 'Allow your pseudonymous check-in count to appear on the optional community board. Requires C1. Wellbeing ratings are never ranked.'],
          ].map(([key, label, description]) => (
            <div className="consent-choice" key={key}>
              <div className="form-check form-switch mb-1">
                <input id={`consent-${key}`} className="form-check-input" type="checkbox" checked={Boolean(consent[key])} disabled={savingConsent || (key !== 'participation' && !consent.participation)} onChange={() => tog(key)} />
                <label className="form-check-label fw-semibold" htmlFor={`consent-${key}`}>{label}</label>
              </div>
              <p className="small muted mb-0">{description}</p>
            </div>
          ))}
          <small className="muted">Declining C2 or C3 does not restrict personal tools or access to support.</small>
        </Card></div>
        <div className="col-md-6"><Card title="Data handling in this build"><p className="mb-0">The research preview uses local browser storage and sample data. Server-side row-level security, consent history, a controlled research extract, institutional audit logs, retention/deletion automation, and verified support escalation are not implemented.</p></Card></div>
        <div className="col-md-6"><Card title="Choice history">
          {history.length ? history.map((entry, index) => <div className="small border-top py-2" key={`${entry.at}-${index}`}>{new Date(entry.at).toLocaleString()} · C1 {entry.choices.participation ? 'on' : 'off'}, C2 {entry.choices.research ? 'on' : 'off'}, C3 {entry.choices.leaderboard ? 'on' : 'off'}</div>) : <p className="mb-0 muted">No changes in this browser yet.</p>}
        </Card></div>
      </div>
    </div>
  )
}

export default Privacy
