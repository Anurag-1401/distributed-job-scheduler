export function AuthLayout({ title, children }) {
  return (
    <div className="auth-layout">
      <div className="card auth-card">
        <h1>{title}</h1>
        {children}
      </div>
    </div>
  );
}
