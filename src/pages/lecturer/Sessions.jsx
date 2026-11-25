import { useState } from 'react'
import toast from 'react-hot-toast'
import { Card, Disclaimer } from '../../components/common/ui'
import { useApp } from '../../context/AuthContext'
import { AGGREGATION_THRESHOLD, DOMAINS, summarizeSession } from '../../utils/longitudinal'

export function LecturerSessions() {
  const { isDemo, researchData, createClassSession, closeClassSession, addSampleCohort } = useApp()
  const [title, setTitle] = useState('')
  const sessions = researchData.sessions

  const openSession = event => {
    event.preventDefault()
    try {
      const session = createClassSession(title)
      setTitle('')
      toast.success(`Class PIN: ${session.code}`)
    } catch (error) {
      toast.error(error.message || 'Could not open class session.')
    }
  }

  const seedSession = sessionId => {
    try {
      addSampleCohort(sessionId)
      toast.success('Added 12 clearly labelled synthetic contributions for the presentation.')
    } catch (error) {
      toast.error(error.message || 'Could not add sample contributions.')
    }
  }

  return (
    <div className="research-page">
      <header className="student-welcome">
        <div><span className="dashboard-kicker">LECTURER WORKSPACE</span><h1>Class sessions</h1><p>Open a PIN-based check-in and see only thresholded aggregates.</p></div>
      </header>
      <Disclaimer>
        Preview data only. This local prototype is not an authenticated lecturer system and must not be used to collect student wellbeing data.
      </Disclaimer>
      <Card title="Open a check-in session">
        <form className="d-flex flex-wrap gap-2" onSubmit={openSession}>
          <label className="visually-hidden" htmlFor="session-title">Class or session label</label>
          <input id="session-title" className="form-control" value={title} onChange={event => setTitle(event.target.value)} placeholder="e.g. Week 1 · Lecture 3" maxLength={100} required />
          <button type="submit" className="btn btn-teal">Open session</button>
        </form>
        <p className="small muted mt-2 mb-0">A six-digit PIN is generated for students to enter. Only one session remains open at a time.</p>
      </Card>

      <div className="row g-3">
        {sessions.map(session => {
          const summary = summarizeSession(researchData.responses, session.id)
          return (
            <div className="col-12" key={session.id}>
              <Card title={session.title}>
                <div className="d-flex justify-content-between align-items-center flex-wrap gap-2">
                  <p className="mb-0"><strong>Student PIN:</strong> <span className="session-pin">{session.code}</span> · {session.active ? 'Open' : 'Closed'}</p>
                  {session.active && <button className="btn btn-outline-teal" type="button" onClick={() => closeClassSession(session.id)}>Close session</button>}
                </div>
                <div className="aggregate-status mt-3">
                  {summary.released ? (
                    <>
                      <p><strong>Aggregate released</strong> · {summary.count} distinct rows (threshold {AGGREGATION_THRESHOLD}). No individual responses are shown here.</p>
                      {summary.syntheticCount > 0 && <p className="small text-warning-emphasis">{summary.syntheticCount} rows are generated sample data, not real participants or consent records.</p>}
                      <div className="row g-2">
                        {DOMAINS.map(domain => <div key={domain.id} className="col-6 col-lg"><div className="aggregate-cell"><small>{domain.label}</small><strong>{summary.means[domain.id]} / 5</strong></div></div>)}
                      </div>
                    </>
                  ) : <p className="mb-0">Suppressed: {summary.count} eligible rows; {AGGREGATION_THRESHOLD} are required. Individual responses are not visible.</p>}
                </div>
                {isDemo && <button type="button" className="btn btn-soft mt-3" onClick={() => seedSession(session.id)}>Add 12 synthetic sample responses</button>}
              </Card>
            </div>
          )
        })}
      </div>
      {!sessions.length && <Card title="No sessions yet"><p className="mb-0">Open a session to create a PIN for the student check-in preview.</p></Card>}
      <p className="small muted">Suppression counts distinct C2-eligible rows, not submissions. Synthetic examples are clearly identified. This browser-only prototype is not a security boundary.</p>
    </div>
  )
}

export default LecturerSessions
