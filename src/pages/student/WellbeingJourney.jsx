import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import toast from 'react-hot-toast'
import { Card, Disclaimer } from '../../components/common/ui'
import { useApp } from '../../context/AuthContext'
import { AGGREGATION_THRESHOLD, DOMAIN_SCALE, DOMAINS } from '../../utils/longitudinal'

export function WellbeingJourney() {
  const { user, consent, researchData, submitDomainCheckin } = useApp()
  const [code, setCode] = useState('')
  const [session, setSession] = useState(null)
  const [ratings, setRatings] = useState({})
  const [saving, setSaving] = useState(false)
  const myResponses = researchData.responses
    .filter(row => row.userId === user?.id)
    .sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt))
  const chartData = myResponses.map((row, index) => ({
    checkin: `Check-in ${index + 1}`,
    ...row.ratings,
  }))
  const savedForSession = session && myResponses.some(row => row.sessionId === session.id)
  const leaderboardRows = [...new Map(researchData.responses
    .filter(row => !row.synthetic && row.pseudonym && researchData.consents[row.userId]?.leaderboard)
    .map(row => [row.userId, {
      userId: row.userId,
      pseudonym: row.pseudonym,
      checkins: researchData.responses.filter(item => !item.synthetic && item.userId === row.userId).length,
    }])).values()]
    .sort((a, b) => b.checkins - a.checkins)

  const joinSession = event => {
    event.preventDefault()
    const found = researchData.sessions.find(item => item.active && item.code === code.trim())
    if (!found) {
      toast.error('That PIN does not match an open class session.')
      return
    }
    setSession(found)
    setRatings({})
  }

  const submit = () => {
    setSaving(true)
    try {
      submitDomainCheckin(session.id, ratings)
      toast.success('Your check-in was saved.')
      setRatings({})
    } catch (error) {
      toast.error(error.message || 'We could not save your check-in.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="research-page">
      <header className="student-welcome">
        <div><span className="dashboard-kicker">YOUR OWN DATA</span><h1>Wellbeing journey</h1><p>Brief check-ins, on your terms.</p></div>
        <Link className="dashboard-privacy-link" to="/student/privacy">Review privacy choices</Link>
      </header>
      <Disclaimer>
        Prototype only: data are stored in this browser, not a protected research system. Do not enter real or sensitive wellbeing data.
      </Disclaimer>

      {!consent.participation ? (
        <Card title="Choose before you check in">
          <p>Check-in participation is off until you choose it. You can review the separate participation, research-use, and leaderboard choices in Privacy.</p>
          <Link className="btn btn-teal" to="/student/privacy">Review privacy choices</Link>
        </Card>
      ) : (
        <>
          {!session && <Card title="Join a class check-in">
            <p className="muted">Enter the six-digit PIN shown by your lecturer. A class check-in takes about a minute.</p>
            <form className="d-flex flex-wrap gap-2" onSubmit={joinSession}>
              <label className="visually-hidden" htmlFor="class-pin">Class session PIN</label>
              <input id="class-pin" className="form-control" inputMode="numeric" pattern="[0-9]{6}" maxLength={6} value={code} onChange={event => setCode(event.target.value.replace(/\D/g, ''))} placeholder="6-digit PIN" required />
              <button className="btn btn-teal" type="submit">Join session</button>
            </form>
          </Card>}

          {session && !savedForSession && <Card title={session.title}>
            <p className="muted">Think about the past 7 days and choose how much you agree with each statement. There are no right answers. This is a self-reflection, not a test, diagnosis, or class report; you can leave without submitting.</p>
            <div className="domain-checkin-list">
              {DOMAINS.map(domain => (
                <fieldset className="domain-question" key={domain.id}>
                  <legend>{domain.question}</legend>
                  <div className="domain-options">
                    {DOMAIN_SCALE.map((label, index) => (
                      <button key={label} type="button" className={`btn ${ratings[domain.id] === index + 1 ? 'btn-teal' : 'btn-soft'}`} aria-pressed={ratings[domain.id] === index + 1} onClick={() => setRatings(current => ({ ...current, [domain.id]: index + 1 }))}>
                        {label}
                      </button>
                    ))}
                  </div>
                </fieldset>
              ))}
            </div>
            <div className="d-flex justify-content-between align-items-center flex-wrap gap-2 mt-3">
              <button className="btn btn-outline-teal" type="button" onClick={() => setSession(null)}>Leave check-in</button>
              <button className="btn btn-teal" type="button" disabled={saving || DOMAINS.some(({ id }) => !ratings[id])} onClick={submit}>{saving ? 'Saving…' : 'Save my reflection'}</button>
            </div>
          </Card>}

          {session && savedForSession && <Card title="Check-in complete">
            <p>Your responses are saved for your personal view. You can return to this page to see your progress.</p>
            <button type="button" className="btn btn-soft" onClick={() => setSession(null)}>Done</button>
          </Card>}

          <Card title="Your progression">
            {chartData.length ? (
              <>
                <p className="muted">Your private ratings over time. These descriptive ratings are not a validated scale or diagnosis.</p>
                <div className="wellbeing-chart">
                  <ResponsiveContainer>
                    <LineChart data={chartData}>
                      <XAxis dataKey="checkin" />
                      <YAxis domain={[1, 5]} ticks={[1, 2, 3, 4, 5]} />
                      <Tooltip />
                      {DOMAINS.map((domain, index) => <Line key={domain.id} type="monotone" dataKey={domain.id} name={domain.label} stroke={['#087E83', '#B7791F', '#477A51', '#7C65A5', '#C0504D'][index]} strokeWidth={2} dot />)}
                    </LineChart>
                  </ResponsiveContainer>
                </div>
                <div className="d-flex flex-wrap gap-2 mt-2">{DOMAINS.map((domain, index) => <span className="small" key={domain.id}><span className="domain-legend-dot" style={{ background: ['#087E83', '#B7791F', '#477A51', '#7C65A5', '#C0504D'][index] }} />{domain.label}</span>)}</div>
              </>
            ) : <p className="muted mb-0">Your personal trend will appear after your first check-in.</p>}
          </Card>
          <Card title="Community check-in board">
            {consent.leaderboard ? (
              leaderboardRows.length ? (
                <>
                  <p className="small muted">Optional pseudonymous participation counts only; wellbeing ratings are never ranked.</p>
                  {leaderboardRows.map((row, index) => <div className="d-flex justify-content-between border-top py-2" key={row.userId}><span>{index + 1}. {row.pseudonym}{row.userId === user?.id ? ' · You' : ''}</span><span>{row.checkins} check-ins</span></div>)}
                </>
              ) : <p className="mb-0 muted">Your pseudonym will appear after your first check-in. No wellbeing scores are shown.</p>
            ) : <p className="mb-0">Visibility is off. You can opt in separately from Privacy choices. Your check-ins and research contribution do not depend on leaderboard participation. <Link to="/student/privacy">Review choices</Link>.</p>}
          </Card>
        </>
      )}
      <p className="small muted">Aggregate results are only considered for release at {AGGREGATION_THRESHOLD} or more distinct C2-eligible rows. The prototype does not enforce production access controls.</p>
    </div>
  )
}

export default WellbeingJourney
