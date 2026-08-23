export function LoadingState({ message = "Loading…" }) {
  return <div className="state-panel" role="status"><span className="spinner" /> <span>{message}</span></div>;
}
export function EmptyState({ title, children, action }) {
  return <div className="state-panel card"><div className="empty-icon">—</div><h2>{title}</h2><p className="muted">{children}</p>{action}</div>;
}
export function ErrorState({ title = "Unable to load data", children, onRetry }) {
  return <div className="card form-error" role="alert"><strong>{title}</strong><div>{children}</div>{onRetry ? <button type="button" className="btn btn-secondary retry-btn" onClick={onRetry}>Retry</button> : null}</div>;
}
