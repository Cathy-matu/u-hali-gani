import { Card, Disclaimer } from '../../components/common/ui'
import { useApp } from '../../context/AuthContext'
import { AGGREGATION_THRESHOLD, DOMAINS, summarizeSession } from '../../utils/longitudinal'
export function ResearcherHome() {
  const { researchData } = useApp()
  return (
    <div className="research-page">
      <h1 className="h3">Research overview</h1>
      <Disclaimer>Prototype only. This page displays browser-local aggregate previews, not a secured research extract. Synthetic sample records are labelled; no ethics approval or live data processing is implied.</Disclaimer>
      <Card title={`Aggregate release rule · k = ${AGGREGATION_THRESHOLD}`}>
        <p>Only session-level means with at least {AGGREGATION_THRESHOLD} distinct C2-eligible rows are displayed. Smaller groups are suppressed.</p>
        {!researchData.sessions.length && <p className="muted mb-0">No class sessions have been created in this browser.</p>}
        {researchData.sessions.map(session => {
          const summary = summarizeSession(researchData.responses, session.id)
          return <div key={session.id} className="research-session">
            <h2 className="h6">{session.title}</h2>
            {summary.released ? (
              <>
                <p className="small muted">{summary.count} distinct rows · threshold passed</p>
                {summary.syntheticCount > 0 && <p className="small text-warning-emphasis">{summary.syntheticCount} generated sample rows are synthetic and are not participant data.</p>}
                <div className="row g-2">{DOMAINS.map(domain => <div className="col-6 col-lg" key={domain.id}><div className="aggregate-cell"><small>{domain.label}</small><strong>{summary.means[domain.id]} / 5</strong></div></div>)}</div>
              </>
            ) : <p className="small mb-0">Suppressed · {summary.count} distinct consenting participants; {AGGREGATION_THRESHOLD} required.</p>}
          </div>
        })}
      </Card>
      <Card title="Access and data status">
        <ul className="mb-0">
          <li>Participant-level export is not implemented.</li>
          <li>Consent state and response rows are stored in browser local storage for this prototype.</li>
          <li>Production controls—server-side role enforcement, append-only consent audit, retention/deletion jobs, and a protected research extract—are not implemented.</li>
        </ul>
      </Card>
    </div>
  )
}

export default ResearcherHome
