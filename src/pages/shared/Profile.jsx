import { useApp } from '../../context/AuthContext'
import { Card } from '../../components/common/ui'
import useDocumentTitle from '../../hooks/useDocumentTitle'

const valueOrFallback = value => value || 'Not set'

export default function Profile() {
  const { user, consent } = useApp()
  useDocumentTitle('My profile')

  const details = [
    ['Full name', user?.full_name],
    ['Username', user?.username],
    ['Email', user?.email],
    ['Account type', user?.role],
    ...(user?.role === 'student' ? [['Hali identity', user?.pseudonym]] : []),
  ]

  return (
    <>
      <h1 className="h3">My profile</h1>
      <p className="muted mb-4">Review the account details connected to your Hali sign-in.</p>
      <div className="row g-3">
        <div className="col-lg-7">
          <Card title="Account details">
            <dl className="row mb-0">
              {details.map(([label, value]) => (
                <div className="col-sm-6 mb-3" key={label}>
                  <dt className="small muted">{label}</dt>
                  <dd className="mb-0 text-break">{valueOrFallback(value)}</dd>
                </div>
              ))}
            </dl>
          </Card>
        </div>
        <div className="col-lg-5">
          <Card title="Privacy choices">
            <dl className="row mb-0">
              <div className="col-12 mb-3">
                <dt className="small muted">Research participation</dt>
                <dd className="mb-0">{consent.research ? 'Opted in' : 'Not opted in'}</dd>
              </div>
              <div className="col-12">
                <dt className="small muted">Re-contact permission</dt>
                <dd className="mb-0">{consent.recontact ? 'Allowed' : 'Not allowed'}</dd>
              </div>
            </dl>
          </Card>
        </div>
      </div>
    </>
  )
}
