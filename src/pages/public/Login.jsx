import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ArrowRight, Eye, EyeOff, ShieldCheck } from 'lucide-react'
import toast from 'react-hot-toast'
import { Logo } from '../../components/common/ui'
import { useApp } from '../../context/AuthContext'
import { authApi, getAuthErrorMessage } from '../../services/auth'
import { offerPasswordSave } from '../../services/passwordManager'

export function Login() {
  const { authReady, user, setUser } = useApp()
  const go = useNavigate()
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    if (authReady && user) go(`/${user.role}`, { replace: true })
  }, [authReady, user, go])

  const homeForRole = role => {
    if (role === 'student' || role === 'counsellor') return `/${role}`
    throw new Error(`Unsupported Hali account role: ${role}`)
  }

  const submit = async event => {
    event.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      const signedInUser = await authApi.login({ identifier: identifier.trim(), password })
      const destination = homeForRole(signedInUser.role)
      offerPasswordSave(identifier.trim(), password)
      setUser(signedInUser)
      toast.success('Welcome back.')
      go(destination, { replace: true })
    } catch (requestError) {
      setError(getAuthErrorMessage(requestError, 'We could not sign you in. Please check your connection and try again.'))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="auth-page">
      <header className="auth-topbar">
        <Link to="/" aria-label="Hali home"><Logo size={34} /></Link>
        <p>New to Hali? <Link to="/onboarding">Create an account <ArrowRight size={15} /></Link></p>
      </header>

      <div className="auth-shell">
        <section className="auth-form-panel" aria-labelledby="login-title">
          <div className="auth-form-content">
            <span className="auth-eyebrow">YOUR CAMPUS WELLBEING SPACE</span>
            <h1 id="login-title">Welcome back</h1>
            <p className="auth-intro">Sign in to your Hali account to continue. Students and counsellors use the same secure sign-in.</p>

            <form className="auth-form" name="login" autoComplete="on" onSubmit={submit}>
              <div className="auth-field">
                <label htmlFor="login-identifier">Username or university email</label>
                <input
                  id="login-identifier"
                  className="form-control auth-email"
                  type="text"
                  name="username"
                  autoComplete="username"
                  maxLength={254}
                  required
                  value={identifier}
                  onChange={event => setIdentifier(event.target.value)}
                  placeholder="Your username or university email"
                />
              </div>
              <div className="auth-field">
                <label htmlFor="login-password">Password</label>
                <div className="auth-password-wrap">
                  <input
                    id="login-password"
                    className="form-control auth-email"
                    type={showPassword ? 'text' : 'password'}
                    name="password"
                    autoComplete="current-password"
                    maxLength={128}
                    required
                    value={password}
                    onChange={event => setPassword(event.target.value)}
                    placeholder="Enter your password"
                  />
                  <button type="button" className="auth-password-toggle" onClick={() => setShowPassword(value => !value)} aria-label="Toggle password visibility" aria-pressed={showPassword}>
                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
              </div>
              {error && <div className="auth-error" role="alert">{error}</div>}
              <button className="btn btn-teal auth-submit-button" type="submit" disabled={!authReady || submitting}>
                {submitting ? 'Signing in…' : 'Sign in'} {!submitting && <ArrowRight size={17} />}
              </button>
            </form>

            <div className="auth-login-divider"><span>SECURE ACCESS</span></div>
            <p className="auth-privacy-note"><ShieldCheck size={17} /> Your account and wellbeing information stay private.</p>
            <p className="auth-field-help">After sign-in, your browser may ask to save your username and password. Hali does not save passwords in browser storage.</p>
            <p className="auth-create-prompt">Need a Hali account? <Link to="/onboarding">Create one <ArrowRight size={14} /></Link></p>
          </div>
        </section>

        <aside className="auth-visual-panel" aria-label="Hali wellbeing support">
          <div className="auth-art" aria-hidden="true">
            <div className="auth-art-orbit auth-art-orbit-one" />
            <div className="auth-art-orbit auth-art-orbit-two" />
            <div className="auth-art-sun"><span /></div>
            <div className="auth-art-card auth-art-card-top"><span className="auth-art-dot" /><span>Space to pause</span></div>
            <div className="auth-art-card auth-art-card-bottom"><span className="auth-art-heart">♡</span><span>Support, when you need it</span></div>
          </div>
          <div className="auth-visual-copy">
            <span className="auth-visual-kicker">A little care goes a long way</span>
            <h2>Feel better, one small step at a time.</h2>
            <p>Check in with yourself, find helpful resources, and connect with a real person when you’re ready.</p>
          </div>
          <div className="auth-visual-foot"><ShieldCheck size={17} /> Your wellbeing. Your pace. Your privacy.</div>
        </aside>
      </div>

      <footer className="auth-footer">
        <span>© Hali · University wellbeing</span>
        <div><Link to="/">About Hali</Link><Link to="/onboarding">Create an account</Link></div>
      </footer>
    </div>
  )
}

export default Login
