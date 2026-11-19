export const Modal = ({ open, onClose, title, children }) => !open ? null : (
  <div className="modal d-block" role="dialog" aria-modal="true" style={{ background: 'rgba(24,53,54,.45)' }} onClick={onClose}>
    <div className="modal-dialog modal-dialog-centered" onClick={e => e.stopPropagation()}>
      <div className="modal-content" style={{ borderRadius: 18 }}>
        <div className="modal-header"><h2 className="h5 m-0">{title}</h2><button className="btn-close" aria-label="Close" onClick={onClose} /></div>
        <div className="modal-body">{children}</div>
      </div>
    </div>
  </div>
)
