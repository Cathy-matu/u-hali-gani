import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ArrowLeft, ArrowRight, Check, Eye, EyeOff, ShieldCheck } from 'lucide-react'
import toast from 'react-hot-toast'
import { Logo } from '../../components/common/ui'
import { useApp } from '../../context/AuthContext'
import { authApi, getAuthErrorMessage } from '../../services/auth'

const steps = ['Welcome', 'Private by default', 'Create your account', 'Your Hali identity', 'Your privacy', 'Your choice']

export function Onboarding() {
  const [i, setI] = useState(0)
  const [form, setForm] = useState({ fullName: '', username: '', email: '', role: 'student', password: '', confirmPassword: '', inviteCode: '' })
  const [fieldErrors, setFieldErrors] = useState({})
  const [requestError, setRequestError] = useState('')
  const [researchConsent, setResearchConsent] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const { authReady, user, setUser, setConsent } = useApp()
  const go = useNavigate()

  useEffect(() => {
    if (authReady && user) go(`/${user.role}`, { replace: true })
  }, [authReady, user, go])

  const update = event => {
    const { name, value } = event.target
    setForm(current => ({ ...current, [name]: value }))
    setFieldErrors(current => ({ ...current, [name]: '' }))
    setRequestError('')
  }

  const validateAccount = () => {
    const errors = {}
    if (form.fullName.trim().length < 2) errors.fullName = 'Enter your full name.'
    if (!/^[a-z0-9](?:[a-z0-9._-]{1,30}[a-z0-9])$/i.test(form.username.trim())) errors.username = 'Use 3–32 letters or numbers; dots, underscores and hyphens are allowed between characters.'
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim())) errors.email = 'Enter a valid email address.'
    if (form.password.length < 12) errors.password = 'Use at least 12 characters.'
    if (form.password !== form.confirmPassword) errors.confirmPassword = 'Your passwords do not match.'
    if (form.role === 'counsellor' && !form.inviteCode.trim()) errors.inviteCode = 'Enter the invitation code provided by your university.'
    setFieldErrors(errors)
    return Object.keys(errors).length === 0
  }

  const submitStep = async event => {
    event.preventDefault()
    setRequestError('')
    if (i === 2 && !validateAccount()) return
    if (i < steps.length - 1) {
      setI(step => step + 1)
      return
    }

    setSubmitting(true)
    try {
      const newUser = await authApi.register({
        full_name: form.fullName.trim(),
        username: form.username.trim(),
        email: form.email.trim(),
        password: form.password,
        role: form.role,
        counsellor_invite_code: form.role === 'counsellor' ? form.inviteCode : undefined,
        research_consent: researchConsent,
        recontact_consent: false,
      })
      setConsent({ research: researchConsent, recontact: false })
      setUser(newUser)
      toast.success('Your Hali account is ready.')
      go(`/${newUser.role}`, { replace: true })
    } catch (error) {
      setRequestError(getAuthErrorMessage(error, 'We could not create your account. Please try again.'))
    } finally {
      setSubmitting(false)
    }
  }

  const body = [
    <p>Hali is a calm place to check in with yourself and reach a human counsellor.</p>,
    <p>You take part under a pseudonym. Anonymity is the default. It can be broken only under a defined emergency protocol involving imminent risk.</p>,
    <div className="auth-account-fields">
      <div className="auth-field">
        <label htmlFor="account-name">Full name</label>
        <input id="account-name" className="form-control auth-email" name="fullName" autoComplete="name" maxLength={160} value={form.fullName} onChange={update} aria-invalid={Boolean(fieldErrors.fullName)} aria-describedby={fieldErrors.fullName ? 'name-error' : undefined} />
        {fieldErrors.fullName && <span id="name-error" className="auth-field-error">{fieldErrors.fullName}</span>}
      </div>
      <div className="auth-field">
        <label htmlFor="account-username">Username</label>
        <input id="account-username" className="form-control auth-email" name="username" autoComplete="username" maxLength={32} value={form.username} onChange={update} aria-invalid={Boolean(fieldErrors.username)} aria-describedby={fieldErrors.username ? 'username-error' : 'username-hint'} />
        <span id={fieldErrors.username ? 'username-error' : 'username-hint'} className={fieldErrors.username ? 'auth-field-error' : 'auth-field-help'}>{fieldErrors.username || 'Use 3–32 letters or numbers; dots, underscores and hyphens are allowed.'}</span>
      </div>
      <div className="auth-field">
        <label htmlFor="account-email">University email</label>
        <input id="account-email" className="form-control auth-email" name="email" type="email" inputMode="email" autoComplete="email" maxLength={254} placeholder="name@university.ac.ke" value={form.email} onChange={update} aria-invalid={Boolean(fieldErrors.email)} aria-describedby={fieldErrors.email ? 'email-error' : undefined} />
        {fieldErrors.email && <span id="email-error" className="auth-field-error">{fieldErrors.email}</span>}
      </div>
      <fieldset className="auth-role-field">
        <legend>Account type</legend>
        <div className="auth-role-choices">
          {[['student', 'Student'], ['counsellor', 'Counsellor']].map(([value, label]) => (
            <label key={value} className={`auth-role-choice${form.role === value ? ' selected' : ''}`}>
              <input type="radio" name="role" value={value} checked={form.role === value} onChange={update} />
              <span>{label}</span>
            </label>
          ))}
        </div>
      </fieldset>
      {form.role === 'counsellor' && (
        <div className="auth-field">
          <label htmlFor="account-invite">Counsellor invitation code</label>
          <input id="account-invite" className="form-control auth-email" name="inviteCode" autoComplete="off" maxLength={256} value={form.inviteCode} onChange={update} aria-invalid={Boolean(fieldErrors.inviteCode)} aria-describedby={fieldErrors.inviteCode ? 'invite-error' : 'invite-hint'} />
          <span id={fieldErrors.inviteCode ? 'invite-error' : 'invite-hint'} className={fieldErrors.inviteCode ? 'auth-field-error' : 'auth-field-help'}>{fieldErrors.inviteCode || 'Ask your university administrator for an invitation.'}</span>
        </div>
      )}
      <div className="auth-field">
        <label htmlFor="account-password">Create password</label>
        <div className="auth-password-wrap">
          <input id="account-password" className="form-control auth-email" name="password" type={showPassword ? 'text' : 'password'} autoComplete="new-password" maxLength={128} value={form.password} onChange={update} aria-invalid={Boolean(fieldErrors.password)} aria-describedby={fieldErrors.password ? 'password-error' : 'password-hint'} />
          <button type="button" className="auth-password-toggle" onClick={() => setShowPassword(value => !value)} aria-label="Toggle password visibility" aria-pressed={showPassword}>{showPassword ? <EyeOff size={18} /> : <Eye size={18} />}</button>
        </div>
        <span id={fieldErrors.password ? 'password-error' : 'password-hint'} className={fieldErrors.password ? 'auth-field-error' : 'auth-field-help'}>{fieldErrors.password || 'Use at least 12 characters.'}</span>
      </div>
      <div className="auth-field">
        <label htmlFor="account-confirm-password">Confirm password</label>
        <div className="auth-password-wrap">
          <input id="account-confirm-password" className="form-control auth-email" name="confirmPassword" type={showConfirmPassword ? 'text' : 'password'} autoComplete="new-password" maxLength={128} value={form.confirmPassword} onChange={update} aria-invalid={Boolean(fieldErrors.confirmPassword)} aria-describedby={fieldErrors.confirmPassword ? 'confirm-password-error' : undefined} />
          <button type="button" className="auth-password-toggle" onClick={() => setShowConfirmPassword(value => !value)} aria-label="Toggle password visibility" aria-pressed={showConfirmPassword}>{showConfirmPassword ? <EyeOff size={18} /> : <Eye size={18} />}</button>
        </div>
        {fieldErrors.confirmPassword && <span id="confirm-password-error" className="auth-field-error">{fieldErrors.confirmPassword}</span>}
      </div>
    </div>,
    <p>Your unique Hali identity is generated when your account is created.<br /><span className="muted">Counsellors see your pseudonym, not your name.</span></p>,
    <p>Administrators see aggregate numbers only. Small groups are hidden. Your reflections are not shared with the university.</p>,
    <label className="auth-consent-option"><input type="checkbox" className="form-check-input" checked={researchConsent} onChange={event => setResearchConsent(event.target.checked)} /> <span>Optionally share de-identified data for research. This is separate from counselling and you can withdraw any time.</span></label>,
  ]

  return (
    <div className="auth-page auth-registration">
      <header className="auth-topbar">
        <Link to="/" aria-label="Hali home"><Logo size={34} /></Link>
        <p>Already have an account? <Link to="/login">Sign in <ArrowRight size={15} /></Link></p>
      </header>

      <div className="auth-shell">
        <section className="auth-form-panel" aria-labelledby="registration-title">
          <div className="auth-form-content auth-registration-content">
            <div className="auth-step-meta">
              <span className="auth-eyebrow">YOUR HALI ACCOUNT</span>
              <span className="auth-step-count">STEP {i + 1} OF {steps.length}</span>
            </div>
            <div className="progress auth-progress" role="progressbar" aria-label="Registration progress" aria-valuenow={i + 1} aria-valuemin={1} aria-valuemax={steps.length}>
              <div className="progress-bar" style={{ width: `${((i + 1) / steps.length) * 100}%` }} />
            </div>
            <h1 id="registration-title">{steps[i]}</h1>
            <form onSubmit={submitStep} noValidate>
              <div className="auth-step-body">{body[i]}</div>
              {requestError && <div className="auth-error mt-3" role="alert">{requestError}</div>}
              <div className="auth-step-actions">
                <button type="button" className="auth-back-button" disabled={!i || submitting} onClick={() => { setI(step => step - 1); setRequestError('') }}><ArrowLeft size={17} /> Back</button>
                <button type="submit" className="btn btn-teal auth-continue-button" disabled={!authReady || submitting}>
                  {submitting ? 'Creating account…' : i < steps.length - 1 ? <>Continue <ArrowRight size={17} /></> : <>Create account <ArrowRight size={17} /></>}
                </button>
              </div>
            </form>
            <p className="auth-registration-footnote"><ShieldCheck size={16} /> You’re in control of what you share.</p>
          </div>
        </section>

        <aside className="auth-visual-panel auth-registration-visual" aria-label="Hali privacy commitments">
          <div className="auth-art auth-art-registration" aria-hidden="true">
            <div className="auth-art-orbit auth-art-orbit-one" />
            <div className="auth-art-orbit auth-art-orbit-two" />
            <div className="auth-art-sun"><span /></div>
            <div className="auth-art-card auth-art-card-top"><ShieldCheck size={18} /><span>Private by default</span></div>
            <div className="auth-art-card auth-art-card-bottom"><span className="auth-art-check"><Check size={17} /></span><span>Support at your pace</span></div>
          </div>
          <div className="auth-visual-copy">
            <span className="auth-visual-kicker">A safe place to start</span>
            <h2>Your story stays yours.</h2>
            <p>Hali is designed around your privacy. Your reflections belong to you, and research participation is always your choice.</p>
          </div>
          <div className="auth-visual-foot"><ShieldCheck size={17} /> A human is always part of your care.</div>
        </aside>
      </div>

      <footer className="auth-footer">
        <span>© Hali · University wellbeing</span>
        <div><Link to="/login">Sign in</Link><Link to="/">About Hali</Link></div>
      </footer>
    </div>
  )
}

export default Onboarding
