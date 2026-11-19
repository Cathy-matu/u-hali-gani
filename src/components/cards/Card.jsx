export const Card = ({ title, action, children, className = '' }) => (
  <section className={`card-h ${className}`}>
    {(title || action) && <div className="d-flex justify-content-between align-items-center mb-3"><h2 className="h5 m-0">{title}</h2>{action}</div>}
    {children}
  </section>
)
export const Stat = ({ label, value, hint }) => <div className="card-h stat"><div className="muted small">{label}</div><b>{value}</b>{hint && <div className="small muted">{hint}</div>}</div>
